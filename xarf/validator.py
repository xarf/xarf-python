"""XARF Report Validator.

Higher-level validator that wraps schema validation and adds unknown-field
detection and optional missing-field discovery.  Mirrors ``validator.ts``
from the JavaScript reference implementation.

The public surface of this module is :class:`ValidationResult` (exported
from :mod:`xarf`) and the private :data:`_validator` singleton consumed by
:func:`xarf.parser.parse`.  :class:`XARFValidator` itself is an internal
implementation detail, matching the JS convention where the class is not
re-exported from ``index.ts``.

Example:
    >>> from xarf.validator import _validator
    >>> result = _validator.validate(report_dict, strict=False)
    >>> result.valid
    True
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from xarf.models import ValidationError, ValidationWarning, XARFReport
from xarf.schema_registry import schema_registry
from xarf.schema_validator import schema_validator

# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------


@dataclass
class ValidationResult:
    """Result returned by :meth:`XARFValidator.validate`.

    Mirrors the ``ValidationResult`` interface in
    ``xarf-javascript/src/validator.ts``.

    Attributes:
        valid: ``True`` when :attr:`errors` is empty.
        errors: Schema-validation errors and (in strict mode) unknown-field
            errors.
        warnings: Unknown-field warnings (non-strict mode only).
        info: Missing optional/recommended field details when
            ``show_missing_optional=True``, otherwise ``None``.
    """

    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    info: list[dict[str, str]] | None = None


# ---------------------------------------------------------------------------
# XARFValidator
# ---------------------------------------------------------------------------


class XARFValidator:
    """Higher-level XARF report validator.

    Wraps :class:`~xarf.schema_validator.SchemaValidator` and adds
    unknown-field detection and missing optional-field discovery, mirroring
    ``XARFValidator`` in ``xarf-javascript/src/validator.ts``.

    All state is local to each :meth:`validate` call — the class carries no
    instance state and the module-level :data:`_validator` singleton is safe
    for concurrent use.
    """

    def validate(
        self,
        report: XARFReport | dict[str, Any],
        strict: bool = False,
        show_missing_optional: bool = False,
    ) -> ValidationResult:
        """Validate *report* and collect errors, warnings, and optional info.

        Mirrors ``XARFValidator.validate()`` in
        ``xarf-javascript/src/validator.ts``.

        Steps:

        1. **Schema validation** via :data:`~xarf.schema_validator.schema_validator`.
        2. **Unknown-field detection** — fields not defined in the core or
           type-specific schema produce :class:`~xarf.models.ValidationWarning`
           entries.
        3. **Strict-mode promotion** — in strict mode, unknown-field warnings
           are converted to :class:`~xarf.models.ValidationError` entries and
           the warnings list is cleared.
        4. **Missing optional fields** — populated only when
           *show_missing_optional* is ``True``.

        Args:
            report: A :class:`~xarf.models.XARFReport` (or subclass) instance,
                or a plain :class:`dict` containing raw report data.
            strict: When ``True``, schema recommended fields are treated as
                required and unknown-field warnings become errors.
            show_missing_optional: When ``True``, :attr:`ValidationResult.info`
                is populated with details about absent optional and recommended
                fields.

        Returns:
            :class:`ValidationResult` with ``valid``, ``errors``, ``warnings``,
            and optional ``info``.

        Example:
            >>> result = _validator.validate({"category": "messaging", ...})
            >>> result.valid
            False
        """
        data: dict[str, Any] = (
            report
            if isinstance(report, dict)
            else report.model_dump(by_alias=True, exclude_none=True)
        )

        # ------------------------------------------------------------------
        # Step 1 — Schema validation
        # ------------------------------------------------------------------
        errors: list[ValidationError] = list(
            schema_validator.validate(data, strict=strict)
        )

        # ------------------------------------------------------------------
        # Step 2 — Unknown-field detection
        # ------------------------------------------------------------------
        category: str = str(data.get("category", ""))
        type_: str = str(data.get("type", ""))
        warnings: list[ValidationWarning] = []
        if category and type_:
            warnings = _collect_unknown_fields(data, category, type_)

        # ------------------------------------------------------------------
        # Step 3 — Strict mode: promote unknown-field warnings to errors
        # ------------------------------------------------------------------
        if strict and warnings:
            errors.extend(
                ValidationError(field=w.field, message=w.message) for w in warnings
            )
            warnings = []

        # ------------------------------------------------------------------
        # Step 4 — Missing optional / recommended fields
        # ------------------------------------------------------------------
        info: list[dict[str, str]] | None = None
        if show_missing_optional and category and type_:
            info = _collect_missing_optional(data, category, type_)

        return ValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            info=info,
        )


# ---------------------------------------------------------------------------
# Private helpers (mirrors private methods of XARFValidator in validator.ts)
# ---------------------------------------------------------------------------


def _collect_unknown_fields(
    data: dict[str, Any],
    category: str,
    type_: str,
) -> list[ValidationWarning]:
    """Return warnings for fields in *data* not defined in the XARF schema.

    Mirrors ``collectUnknownFields()`` in ``xarf-javascript/src/validator.ts``.
    Known fields are the union of core property names and type-specific fields
    for the given ``category``/``type_`` pair.

    Args:
        data: Raw report dict (post-v3-conversion if applicable).
        category: XARF category string (e.g. ``"messaging"``).
        type_: XARF type string within the category (e.g. ``"spam"``).

    Returns:
        List of :class:`~xarf.models.ValidationWarning`, one per unknown field.
    """
    known_fields: set[str] = set(schema_registry.get_core_property_names())
    known_fields.update(schema_registry.get_category_fields(category, type_))

    return [
        ValidationWarning(
            field=field_name,
            message=f"Unknown field '{field_name}' is not defined in the XARF schema",
        )
        for field_name in data
        if field_name not in known_fields
    ]


def _collect_missing_optional(
    data: dict[str, Any],
    category: str,
    type_: str,
) -> list[dict[str, str]]:
    """Collect missing optional and recommended fields for the report.

    Mirrors ``collectMissingOptionalFields()`` in
    ``xarf-javascript/src/validator.ts``.  Checks both the core schema and
    the type-specific schema, following ``allOf`` / base-schema references.

    Each returned dict has two keys:

    - ``"field"``: the field name.
    - ``"message"``: ``"RECOMMENDED: <description>"`` or
      ``"OPTIONAL: <description>"``.

    Args:
        data: Raw report dict.
        category: XARF category string.
        type_: XARF type string.

    Returns:
        List of info dicts for each field that is absent from *data*.
    """
    info: list[dict[str, str]] = []
    required_fields = schema_registry.get_required_fields()

    # Core optional fields
    for field_name in sorted(schema_registry.get_core_property_names()):
        if field_name in required_fields or field_name == "_internal":
            continue
        if field_name in data:
            continue
        metadata = schema_registry.get_field_metadata(field_name)
        if metadata is None:
            continue
        prefix = "RECOMMENDED" if metadata.recommended else "OPTIONAL"
        description = metadata.description or f"Optional field: {field_name}"
        info.append({"field": field_name, "message": f"{prefix}: {description}"})

    # Type-specific optional fields
    type_schema = schema_registry.get_type_schema(category, type_)
    if type_schema:
        for field_name, description, recommended in _extract_type_optional_fields(
            type_schema
        ):
            if field_name in data:
                continue
            prefix = "RECOMMENDED" if recommended else "OPTIONAL"
            info.append({"field": field_name, "message": f"{prefix}: {description}"})

    return info


def _extract_type_optional_fields(
    schema: dict[str, Any],
    _accumulated_required: frozenset[str] | None = None,
) -> list[tuple[str, str, bool]]:
    """Extract optional field metadata from a type schema.

    Mirrors ``extractOptionalFields()`` in ``xarf-javascript/src/validator.ts``.
    Handles ``properties`` defined directly on the schema as well as fields
    inherited via ``allOf`` (resolving ``-base.json`` references).

    Core fields are excluded; ``category``, ``type``, and ``_internal`` are
    always skipped.

    Args:
        schema: The type-specific (or base) schema dict to inspect.
        _accumulated_required: Required field names accumulated from parent
            schemas during recursive calls.  Pass ``None`` on the initial call.

    Returns:
        List of ``(field_name, description, recommended)`` triples for each
        optional field found.
    """
    core_fields = schema_registry.get_core_property_names()
    _skip = {"category", "type", "_internal"}

    schema_required: frozenset[str] = frozenset(schema.get("required", []))
    effective_required = (
        schema_required | _accumulated_required
        if _accumulated_required is not None
        else schema_required
    )

    result: list[tuple[str, str, bool]] = []
    seen: set[str] = set()

    def _add(field_name: str, description: str, recommended: bool) -> None:
        if field_name not in seen:
            seen.add(field_name)
            result.append((field_name, description, recommended))

    for field_name, prop_def in schema.get("properties", {}).items():
        if field_name in core_fields or field_name in _skip:
            continue
        if field_name in effective_required:
            continue
        description = prop_def.get("description") or f"Optional field: {field_name}"
        recommended = prop_def.get("x-recommended") is True
        _add(field_name, description, recommended)

    for sub in schema.get("allOf", []):
        ref: str = sub.get("$ref", "")
        if ref:
            if "-base.json" not in ref:
                continue
            base_schema = _load_base_schema(ref)
            if base_schema is None:
                continue
            for item in _extract_type_optional_fields(base_schema, effective_required):
                _add(*item)
        else:
            for item in _extract_type_optional_fields(sub, effective_required):
                _add(*item)

    return result


def _load_base_schema(ref: str) -> dict[str, Any] | None:
    """Load a base schema file referenced by a ``$ref`` string.

    Only handles ``-base.json`` references (e.g. ``"./content-base.json"``).
    Uses the same schemas directory as
    :data:`~xarf.schema_registry.schema_registry`.

    Args:
        ref: The ``$ref`` value from the schema (e.g. ``"./content-base.json"``).

    Returns:
        Parsed schema dict, or ``None`` if the file cannot be loaded.
    """
    filename = ref.removeprefix("./").removeprefix("../")
    schema_path = schema_registry._schemas_dir / "types" / filename
    try:
        with schema_path.open(encoding="utf-8") as fh:
            return json.load(fh)  # type: ignore[no-any-return]
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Module-level singleton (private — used by parser.parse(), not public API)
# ---------------------------------------------------------------------------

#: Private singleton consumed by :func:`xarf.parser.parse`.
#: Not exported from :mod:`xarf`
_validator: XARFValidator = XARFValidator()
