"""XARF v4 Parser.

Provides the module-level :func:`parse` function that converts raw JSON (a
string or a plain dict) into a fully-typed :data:`~xarf.models.AnyXARFReport`
Pydantic model, returning a :class:`~xarf.models.ParseResult` that carries the
report together with any validation errors, warnings, and optional
missing-field info.

Mirrors ``parse()`` in ``xarf-javascript/src/parser.ts``.  All validation
logic — schema validation, unknown-field detection, and missing-field
discovery — is delegated to :data:`xarf.validator._validator`, exactly as
``parser.ts`` delegates to its ``XARFValidator`` instance.

Example:
    >>> from xarf import parse
    >>> result = parse(json_string)
    >>> if not result.errors:
    ...     report = result.report  # fully typed AnyXARFReport subclass
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import TypeAdapter
from pydantic import ValidationError as PydanticValidationError

from xarf.exceptions import XARFParseError
from xarf.models import AnyXARFReport, ParseResult, ValidationWarning
from xarf.v3_compat import convert_v3_to_v4, get_v3_deprecation_warning, is_v3_report
from xarf.validator import _validator

# ---------------------------------------------------------------------------
# Module-level TypeAdapter (built once; reused for every parse() call)
# ---------------------------------------------------------------------------

_REPORT_ADAPTER: TypeAdapter[AnyXARFReport] = TypeAdapter(AnyXARFReport)

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse(
    json_data: str | dict[str, Any],
    strict: bool = False,
    show_missing_optional: bool = False,
) -> ParseResult:
    """Parse a XARF v4 report from JSON.

    Supports both XARF v4 and v3 (legacy) formats.  v3 reports are
    automatically converted to v4 and a deprecation warning is emitted via
    :mod:`warnings` as well as added to
    :attr:`~xarf.models.ParseResult.warnings`.

    In non-strict mode the parser attempts best-effort deserialization even
    when schema validation errors are present, returning ``report=None`` only
    when Pydantic is also unable to construct a typed model.

    Args:
        json_data: A JSON string or a pre-parsed dict containing XARF report
            data.
        strict: When ``True``, fields marked ``x-recommended: true`` in the
            schema are treated as required, unknown fields become errors, and
            any validation error causes ``report=None`` to be returned
            immediately without Pydantic deserialization.
        show_missing_optional: When ``True``,
            :attr:`~xarf.models.ParseResult.info` is populated with details
            about optional and recommended fields absent from the report.

    Returns:
        :class:`~xarf.models.ParseResult` containing:

        - ``report``: The typed report model, or ``None`` on failure.
        - ``errors``: Validation errors (empty list means valid).
        - ``warnings``: Non-fatal warnings (v3 conversion, unknown fields).
        - ``info``: Missing-field metadata when ``show_missing_optional=True``,
          otherwise ``None``.

    Raises:
        XARFParseError: If *json_data* is a string containing malformed JSON.

    Example:
        >>> result = parse('{"xarf_version": "4.2.0", ...}')
        >>> result.report
        SpamReport(...)
        >>> result.errors
        []
    """
    parse_warnings: list[ValidationWarning] = []

    # ------------------------------------------------------------------
    # Step 1 — JSON parsing
    # ------------------------------------------------------------------
    if isinstance(json_data, str):
        try:
            parsed = json.loads(json_data)
        except json.JSONDecodeError as exc:
            raise XARFParseError(f"Invalid JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise XARFParseError(f"Expected a JSON object, got {type(parsed).__name__}")
        data: dict[str, Any] = parsed
    else:
        data = json_data

    # ------------------------------------------------------------------
    # Step 2 — v3 detection and conversion
    # ------------------------------------------------------------------
    if is_v3_report(data):
        # convert_v3_to_v4 emits a Python warnings.warn() internally.
        # Collect non-fatal conversion messages (e.g. missing ReporterOrg).
        conversion_msgs: list[str] = []
        data = convert_v3_to_v4(data, conversion_warnings=conversion_msgs)
        parse_warnings.append(
            ValidationWarning(field="", message=get_v3_deprecation_warning())
        )
        for msg in conversion_msgs:
            parse_warnings.append(ValidationWarning(field="", message=msg))

    # ------------------------------------------------------------------
    # Step 3 — Validate (schema + unknown fields + missing optional)
    # Mirrors: validator.validate(data, strict, showMissingOptional)
    # ------------------------------------------------------------------
    result = _validator.validate(
        data, strict=strict, show_missing_optional=show_missing_optional
    )

    # ------------------------------------------------------------------
    # Step 4 — Strict mode early return (Python-specific: prevents a
    # Pydantic discriminator failure on malformed category/type)
    # ------------------------------------------------------------------
    if result.errors and strict:
        return ParseResult(report=None, errors=result.errors, warnings=parse_warnings)

    # ------------------------------------------------------------------
    # Step 5 — Pydantic deserialization via discriminated union
    # ------------------------------------------------------------------
    try:
        report = _REPORT_ADAPTER.validate_python(data)
    except PydanticValidationError:
        return ParseResult(report=None, errors=result.errors, warnings=parse_warnings)

    return ParseResult(
        report=report,
        errors=result.errors,
        warnings=parse_warnings + result.warnings,
        info=result.info,
    )
