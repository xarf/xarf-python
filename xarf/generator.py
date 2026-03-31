"""XARF Report Generator.

Provides the module-level :func:`create_report` and :func:`create_evidence`
functions for programmatic creation of XARF v4 reports with automatic
metadata, validation, and type safety.

Mirrors ``generator.ts`` from the JavaScript reference implementation.
``xarf_version``, ``report_id``, and ``timestamp`` are auto-generated;
callers supply all other required fields plus any category-specific kwargs.

Example:
    >>> from xarf import create_report, create_evidence
    >>> evidence = create_evidence("text/plain", b"log line", description="Log")
    >>> result = create_report(
    ...     category="messaging",
    ...     type="spam",
    ...     source_identifier="192.0.2.1",
    ...     reporter={"org": "ACME", "contact": "abuse@acme.example",
    ...               "domain": "acme.example"},
    ...     sender={"org": "Bad Actor", "contact": "noreply@bad.example",
    ...             "domain": "bad.example"},
    ...     evidence=[evidence],
    ... )
    >>> result.errors
    []
"""

from __future__ import annotations

import base64
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from xarf._version import SPEC_VERSION as _SPEC_VERSION
from xarf.models import AnyXARFReport, ContactInfo, CreateReportResult, XARFEvidence
from xarf.validator import _validator

# ---------------------------------------------------------------------------
# Module-level TypeAdapter (built once; reused for every create_report() call)
# ---------------------------------------------------------------------------

_REPORT_ADAPTER: TypeAdapter[AnyXARFReport] = TypeAdapter(AnyXARFReport)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _to_jsonable(value: Any) -> Any:  # noqa: ANN401
    """Recursively convert Pydantic models to plain dicts for JSON serialisation.

    Used to ensure that caller-supplied :class:`~xarf.models.XARFEvidence`
    objects (or other Pydantic models) in ``**kwargs`` are serialised to plain
    dicts before the report dict is handed to the schema validator.

    Args:
        value: Any Python value — plain scalars, lists, dicts, or
            :class:`pydantic.BaseModel` instances.

    Returns:
        The value with all :class:`pydantic.BaseModel` instances converted to
        ``dict`` (recursively).  Non-model values are returned unchanged.
    """
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, exclude_none=True)
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_report(
    *,
    category: str,
    type: str,  # noqa: A002
    source_identifier: str,
    reporter: dict[str, Any] | ContactInfo,
    sender: dict[str, Any] | ContactInfo,
    strict: bool = False,
    show_missing_optional: bool = False,
    **kwargs: Any,
) -> CreateReportResult:
    """Create a validated XARF report with auto-generated metadata.

    ``xarf_version``, ``report_id``, and ``timestamp`` are filled in
    automatically.  Category-specific fields are passed via ``**kwargs`` and
    merged into the report alongside the named parameters.

    Mirrors ``createReport()`` in ``xarf-javascript/src/generator.ts``.

    Args:
        category: XARF abuse category (e.g. ``"messaging"``, ``"connection"``).
        type: Report type within the category (e.g. ``"spam"``, ``"ddos"``).
        source_identifier: IP address, domain, or other identifier of the
            abusive source.
        reporter: Contact information for the reporting party — either a
            :class:`~xarf.models.ContactInfo` instance or a plain dict with
            ``org``, ``contact``, and ``domain`` keys.
        sender: Contact information for the originating/sending party — same
            format as *reporter*.
        strict: When ``True``, recommended fields are treated as required,
            unknown fields become errors, and validation failures cause
            ``report=None`` to be returned.
        show_missing_optional: When ``True``,
            :attr:`~xarf.models.CreateReportResult.info` is populated with
            details about absent optional and recommended fields.
        **kwargs: Category-specific fields and any other valid XARF report
            fields (e.g. ``destination_ip``, ``protocol``, ``evidence``).
            :class:`~xarf.models.XARFEvidence` instances in list values are
            automatically serialised to dicts.

    Returns:
        :class:`~xarf.models.CreateReportResult` containing:

        - ``report``: The typed report model, or ``None`` on failure.
        - ``errors``: Validation errors (empty list means valid).
        - ``warnings``: Non-fatal warnings.
        - ``info``: Missing-field metadata when ``show_missing_optional=True``,
          otherwise ``None``.

    Example:
        >>> result = create_report(
        ...     category="connection",
        ...     type="ddos",
        ...     source_identifier="192.0.2.1",
        ...     reporter={"org": "Acme", "contact": "abuse@acme.example",
        ...               "domain": "acme.example"},
        ...     sender={"org": "Bad", "contact": "x@bad.example",
        ...             "domain": "bad.example"},
        ... )
        >>> result.errors
        []
    """
    # ------------------------------------------------------------------
    # Step 1 — Serialise ContactInfo objects; build report dict
    # ------------------------------------------------------------------
    reporter_dict: dict[str, Any] = (
        reporter.model_dump(by_alias=True, exclude_none=True)
        if isinstance(reporter, ContactInfo)
        else reporter
    )
    sender_dict: dict[str, Any] = (
        sender.model_dump(by_alias=True, exclude_none=True)
        if isinstance(sender, ContactInfo)
        else sender
    )

    # Serialise any Pydantic models nested in kwargs (e.g. XARFEvidence lists)
    serialised_kwargs: dict[str, Any] = {k: _to_jsonable(v) for k, v in kwargs.items()}

    report_dict: dict[str, Any] = {
        **serialised_kwargs,
        "category": category,
        "type": type,
        "source_identifier": source_identifier,
        "reporter": reporter_dict,
        "sender": sender_dict,
        # Auto-generated metadata
        "xarf_version": _SPEC_VERSION,
        "report_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # ------------------------------------------------------------------
    # Step 2 — Validate (schema + unknown fields + missing optional)
    # ------------------------------------------------------------------
    result = _validator.validate(
        report_dict, strict=strict, show_missing_optional=show_missing_optional
    )

    # ------------------------------------------------------------------
    # Step 3 — Strict mode early return
    # ------------------------------------------------------------------
    if result.errors and strict:
        return CreateReportResult(
            report=None,
            errors=result.errors,
            warnings=result.warnings,
            info=result.info,
        )

    # ------------------------------------------------------------------
    # Step 4 — Pydantic deserialization via discriminated union
    # ------------------------------------------------------------------
    try:
        report = _REPORT_ADAPTER.validate_python(report_dict)
    except PydanticValidationError:
        return CreateReportResult(
            report=None,
            errors=result.errors,
            warnings=result.warnings,
            info=result.info,
        )

    return CreateReportResult(
        report=report,
        errors=result.errors,
        warnings=result.warnings,
        info=result.info,
    )


def create_evidence(
    content_type: str,
    payload: bytes | str,
    *,
    description: str | None = None,
    hash_algorithm: Literal["sha256", "sha512", "sha1", "md5"] = "sha256",
) -> XARFEvidence:
    """Create an evidence item with automatic hashing, encoding, and size.

    Converts *payload* to bytes if needed, computes a hex digest with the
    chosen algorithm, base64-encodes the payload, and returns a fully-formed
    :class:`~xarf.models.XARFEvidence` object.

    Mirrors ``createEvidence()`` in ``xarf-javascript/src/generator.ts``.

    Args:
        content_type: MIME type of the evidence (e.g. ``"message/rfc822"``).
        payload: Raw evidence data as bytes or a UTF-8 string.
        description: Human-readable description of the evidence item.
        hash_algorithm: Cryptographic algorithm for the integrity hash
            (default ``"sha256"``).  Supported values: ``"sha256"``,
            ``"sha512"``, ``"sha1"``, ``"md5"``.

    Returns:
        :class:`~xarf.models.XARFEvidence` with ``content_type``, base64
        ``payload``, ``hash`` in ``"algorithm:hexvalue"`` format, ``size``
        (byte count of the original payload), and optional ``description``.

    Example:
        >>> ev = create_evidence("text/plain", b"Hello, XARF!", description="Test")
        >>> ev.hash.startswith("sha256:")
        True
        >>> ev.size
        12
    """
    payload_bytes: bytes = (
        payload.encode("utf-8") if isinstance(payload, str) else payload
    )

    # Compute hash — sha1/md5 are legacy but valid per the XARF spec
    hasher = hashlib.new(hash_algorithm)
    hasher.update(payload_bytes)
    hex_digest = hasher.hexdigest()

    encoded_payload: str = base64.b64encode(payload_bytes).decode("ascii")

    return XARFEvidence(
        content_type=content_type,
        payload=encoded_payload,
        hash=f"{hash_algorithm}:{hex_digest}",
        size=len(payload_bytes),
        description=description,
    )
