"""XARF v4 Parser Implementation.

Provides parsing and validation for XARF v4 abuse reports with:
- Schema-driven validation using SchemaRegistry
- Unknown field detection
- Missing optional field reporting (showMissingOptional)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .exceptions import XARFParseError, XARFValidationError
from .models import ConnectionReport, ContentReport, MessagingReport, XARFReport
from .schema_registry import schema_registry
from .schema_validator import SchemaValidator
from .v3_compat import convert_v3_to_v4, is_v3_report


@dataclass
class ValidationError:
    """Validation error details."""

    field: str
    message: str
    value: Any = None


@dataclass
class ValidationWarning:
    """Validation warning details."""

    field: str
    message: str
    value: Any = None


@dataclass
class ValidationInfo:
    """Validation info for missing optional fields."""

    field: str
    message: str


@dataclass
class ValidationResult:
    """Result of validation with errors, warnings, and optional info."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)
    info: list[ValidationInfo] | None = None


class XARFParser:
    """XARF v4 Report Parser.

    Parses and validates XARF v4 abuse reports from JSON.
    Uses SchemaRegistry for schema-driven validation.
    """

    def __init__(self, strict: bool = False, use_schema_validation: bool = True):
        """Initialize parser.

        Args:
            strict: If True, raise exceptions on validation errors.
                   If False, collect errors for later retrieval.
            use_schema_validation: If True, use JSON Schema validation.
        """
        self.strict = strict
        self.use_schema_validation = use_schema_validation
        self.errors: list[str] = []
        self._validation_errors: list[ValidationError] = []
        self._validation_warnings: list[ValidationWarning] = []
        self._validation_info: list[ValidationInfo] = []
        self._schema_validator = SchemaValidator() if use_schema_validation else None

    def parse(self, json_data: str | dict[str, Any]) -> XARFReport:
        """Parse XARF report from JSON.

        Supports both XARF v4 and v3 (with automatic conversion).

        Args:
            json_data: JSON string or dictionary containing XARF report

        Returns:
            XARFReport: Parsed report object

        Raises:
            XARFParseError: If parsing fails
            XARFValidationError: If validation fails (strict mode)
        """
        self._clear_state()

        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
        except json.JSONDecodeError as e:
            raise XARFParseError(f"Invalid JSON: {e}") from e

        # Auto-detect and convert v3 reports
        if is_v3_report(data):
            try:
                data = convert_v3_to_v4(data)
            except Exception as e:
                raise XARFParseError(f"Failed to convert XARF v3 report: {e}") from e

        # Validate basic structure
        if not self.validate_structure(data):
            if self.strict:
                raise XARFValidationError("Validation failed", self.errors)

        # Parse based on category
        report_category = data.get("category")

        # Use SchemaRegistry to check if category is valid
        if not schema_registry.is_valid_category(report_category or ""):
            valid_categories = schema_registry.get_categories()
            error_msg = (
                f"Invalid category '{report_category}'. "
                f"Valid categories: {sorted(valid_categories)}"
            )
            if self.strict:
                raise XARFValidationError(error_msg)
            else:
                self.errors.append(error_msg)
                return XARFReport(**data)

        try:
            # Return category-specific model if available
            if report_category == "messaging":
                return MessagingReport(**data)
            elif report_category == "connection":
                return ConnectionReport(**data)
            elif report_category == "content":
                return ContentReport(**data)
            else:
                # For other valid categories, use base model
                return XARFReport(**data)

        except Exception as e:
            raise XARFParseError(
                f"Failed to parse {report_category} report: {e}"
            ) from e

    def validate(
        self,
        json_data: str | dict[str, Any],
        strict: bool = False,
        show_missing_optional: bool = False,
    ) -> ValidationResult:
        """Validate XARF report comprehensively.

        Args:
            json_data: JSON string or dictionary containing XARF report
            strict: If True, warnings are treated as errors
            show_missing_optional: If True, includes info about missing optional fields

        Returns:
            ValidationResult with errors, warnings, and optionally info

        Raises:
            XARFValidationError: If strict mode and validation fails
        """
        self._clear_state()

        # Parse JSON
        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(field="$root", message=f"Invalid JSON: {e}")],
            )

        # 1. Run schema validation first (if enabled)
        if self.use_schema_validation and self._schema_validator:
            schema_result = self._schema_validator.validate(data)
            if not schema_result.valid:
                for err in schema_result.errors:
                    self._validation_errors.append(
                        ValidationError(
                            field=err.field,
                            message=err.message,
                            value=err.value,
                        )
                    )

        # 2. Run hand-coded validation for better error messages
        self._validate_required_fields(data)
        self._validate_formats(data)
        self._validate_values(data)
        self._validate_category_specific(data)

        # 3. Check for unknown fields
        self._collect_unknown_fields(data)

        # 4. Deduplicate errors
        self._deduplicate_errors()

        # 5. In strict mode, convert warnings to errors
        if strict and self._validation_warnings:
            for warning in self._validation_warnings:
                self._validation_errors.append(
                    ValidationError(
                        field=warning.field,
                        message=warning.message,
                        value=warning.value,
                    )
                )
            self._validation_warnings = []

        # 6. Collect missing optional fields if requested
        if show_missing_optional:
            self._collect_missing_optional_fields(data)

        result = ValidationResult(
            valid=len(self._validation_errors) == 0,
            errors=list(self._validation_errors),
            warnings=list(self._validation_warnings),
        )

        # Only include info if show_missing_optional is enabled
        if show_missing_optional:
            result.info = list(self._validation_info)

        # Note: We return the result even in strict mode so callers can inspect errors.
        # The strict parameter converts warnings to errors but doesn't raise.
        # Callers who want exceptions should check result.valid and raise themselves.
        return result

    def validate_structure(self, data: dict[str, Any]) -> bool:
        """Validate basic XARF structure.

        Args:
            data: Parsed JSON data

        Returns:
            bool: True if structure is valid
        """
        # Get required fields from SchemaRegistry
        required_fields = schema_registry.get_required_fields()

        # Check required fields
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            self.errors.append(f"Missing required fields: {missing_fields}")
            return False

        # Check XARF version
        if data.get("xarf_version") != "4.0.0":
            self.errors.append(f"Unsupported XARF version: {data.get('xarf_version')}")
            return False

        # Validate reporter structure
        reporter = data.get("reporter", {})
        if not isinstance(reporter, dict):
            self.errors.append("Reporter must be an object")
            return False

        # Get required contact fields from SchemaRegistry
        contact_required = schema_registry.get_contact_required_fields()
        missing_reporter = contact_required - set(reporter.keys())
        if missing_reporter:
            self.errors.append(f"Missing reporter fields: {missing_reporter}")
            return False

        # Validate sender structure (required in v4)
        sender = data.get("sender", {})
        if not isinstance(sender, dict):
            self.errors.append("Sender must be an object")
            return False

        missing_sender = contact_required - set(sender.keys())
        if missing_sender:
            self.errors.append(f"Missing sender fields: {missing_sender}")
            return False

        # Validate timestamp format
        try:
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            self.errors.append(f"Invalid timestamp format: {data.get('timestamp')}")
            return False

        # Category-specific validation
        return self._validate_category_type(data)

    def _clear_state(self) -> None:
        """Clear validation state."""
        self.errors.clear()
        self._validation_errors.clear()
        self._validation_warnings.clear()
        self._validation_info.clear()

    def _validate_required_fields(self, data: dict[str, Any]) -> None:
        """Validate required fields using SchemaRegistry."""
        required_fields = schema_registry.get_required_fields()

        for field_name in required_fields:
            if field_name not in data:
                self._validation_errors.append(
                    ValidationError(
                        field=field_name,
                        message=f"Missing required field: {field_name}",
                    )
                )

    def _validate_formats(self, data: dict[str, Any]) -> None:
        """Validate field formats."""
        # Validate timestamp
        timestamp = data.get("timestamp")
        if timestamp:
            try:
                datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                self._validation_errors.append(
                    ValidationError(
                        field="timestamp",
                        message=f"Invalid timestamp format: {timestamp}",
                        value=timestamp,
                    )
                )

        # Validate reporter contact info
        reporter = data.get("reporter", {})
        if isinstance(reporter, dict):
            self._validate_contact_info(reporter, "reporter")

        # Validate sender contact info
        sender = data.get("sender", {})
        if isinstance(sender, dict):
            self._validate_contact_info(sender, "sender")

    def _validate_contact_info(
        self, contact: dict[str, Any], field_prefix: str
    ) -> None:
        """Validate contact info structure."""
        # Check for required contact fields
        contact_required = schema_registry.get_contact_required_fields()
        for field_name in contact_required:
            if field_name not in contact:
                self._validation_errors.append(
                    ValidationError(
                        field=f"{field_prefix}.{field_name}",
                        message=f"Missing required field: {field_prefix}.{field_name}",
                    )
                )

    def _validate_values(self, data: dict[str, Any]) -> None:
        """Validate field values against schema enums."""
        # Validate category
        category = data.get("category")
        if category and not schema_registry.is_valid_category(category):
            valid = sorted(schema_registry.get_categories())
            self._validation_errors.append(
                ValidationError(
                    field="category",
                    message=f"Invalid category '{category}'. Valid: {valid}",
                    value=category,
                )
            )

        # Validate type for category
        report_type = data.get("type")
        if category and report_type:
            if not schema_registry.is_valid_type(category, report_type):
                valid = sorted(schema_registry.get_types_for_category(category))
                self._validation_errors.append(
                    ValidationError(
                        field="type",
                        message=(
                            f"Invalid type '{report_type}' for category "
                            f"'{category}'. Valid: {valid}"
                        ),
                        value=report_type,
                    )
                )

        # Validate evidence_source if present
        evidence_source = data.get("evidence_source")
        if evidence_source:
            sources = schema_registry.get_evidence_sources()
            if sources and evidence_source not in sources:
                self._validation_warnings.append(
                    ValidationWarning(
                        field="evidence_source",
                        message=(
                            f"Unknown evidence_source '{evidence_source}'. "
                            f"Known sources: {sorted(sources)}"
                        ),
                        value=evidence_source,
                    )
                )

    def _validate_category_specific(self, data: dict[str, Any]) -> None:
        """Validate category-specific requirements."""
        category = data.get("category")
        report_type = data.get("type")

        if not category or not report_type:
            return

        # Get category-specific required fields from type schema
        # This is handled by JSON Schema validation, so we just do
        # additional business logic checks here

        if category == "messaging":
            self._validate_messaging(data)
        elif category == "connection":
            self._validate_connection(data)
        elif category == "content":
            self._validate_content(data)

    def _validate_messaging(self, data: dict[str, Any]) -> None:
        """Validate messaging category reports."""
        # Email-specific validation
        if data.get("protocol") == "smtp":
            if not data.get("smtp_from"):
                self._validation_errors.append(
                    ValidationError(
                        field="smtp_from",
                        message="smtp_from required when protocol is smtp",
                    )
                )

    def _validate_connection(self, data: dict[str, Any]) -> None:
        """Validate connection category reports."""
        # Connection reports should have destination_ip
        if not data.get("destination_ip"):
            self._validation_warnings.append(
                ValidationWarning(
                    field="destination_ip",
                    message="destination_ip recommended for connection reports",
                )
            )

    def _validate_content(self, data: dict[str, Any]) -> None:
        """Validate content category reports."""
        # Content reports should have url
        if not data.get("url"):
            self._validation_warnings.append(
                ValidationWarning(
                    field="url",
                    message="url recommended for content reports",
                )
            )

    def _validate_category_type(self, data: dict[str, Any]) -> bool:
        """Validate category and type combination."""
        category = data.get("category")
        report_type = data.get("type")

        if not category:
            self.errors.append("Missing category field")
            return False

        if not schema_registry.is_valid_category(category):
            valid = sorted(schema_registry.get_categories())
            self.errors.append(f"Invalid category '{category}'. Valid: {valid}")
            return False

        if not report_type:
            self.errors.append("Missing type field")
            return False

        if not schema_registry.is_valid_type(category, report_type):
            valid = sorted(schema_registry.get_types_for_category(category))
            self.errors.append(
                f"Invalid type '{report_type}' for category '{category}'. "
                f"Valid: {valid}"
            )
            return False

        return True

    def _collect_unknown_fields(self, data: dict[str, Any]) -> None:
        """Collect unknown fields not defined in the schema."""
        # Get all known fields from core schema
        known_fields = set(schema_registry.get_core_property_names())

        # Add category-specific fields if category and type are present
        category = data.get("category")
        report_type = data.get("type")
        if category and report_type:
            category_fields = schema_registry.get_category_fields(category, report_type)
            known_fields.update(category_fields)

        # Check all fields in the report
        for field_name in data.keys():
            if field_name not in known_fields:
                self._validation_warnings.append(
                    ValidationWarning(
                        field=field_name,
                        message=(
                            f"Unknown field '{field_name}' is not defined "
                            "in the XARF schema"
                        ),
                        value=data[field_name],
                    )
                )

    def _collect_missing_optional_fields(self, data: dict[str, Any]) -> None:
        """Collect missing optional fields from the report."""
        # Get optional fields from core schema
        optional_info = schema_registry.get_optional_field_info(
            category=data.get("category"),
            type_name=data.get("type"),
        )

        for field_info in optional_info:
            field_name = field_info["field"]
            if field_name not in data or data[field_name] is None:
                prefix = "RECOMMENDED" if field_info["recommended"] else "OPTIONAL"
                description = (
                    field_info["description"] or f"Optional field: {field_name}"
                )
                self._validation_info.append(
                    ValidationInfo(
                        field=field_name,
                        message=f"{prefix}: {description}",
                    )
                )

    def _deduplicate_errors(self) -> None:
        """Remove duplicate errors."""
        seen: set[tuple[str, str]] = set()
        unique_errors: list[ValidationError] = []

        for error in self._validation_errors:
            key = (error.field, error.message)
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)

        self._validation_errors = unique_errors

    def get_errors(self) -> list[str]:
        """Get validation errors from last parse/validate call.

        Returns:
            List[str]: List of validation error messages
        """
        return self.errors.copy()

    def get_warnings(self) -> list[ValidationWarning]:
        """Get validation warnings from last validate call.

        Returns:
            List of validation warnings
        """
        return list(self._validation_warnings)
