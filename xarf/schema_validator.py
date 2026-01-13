"""JSON Schema validation for XARF reports.

This module provides JSON Schema validation using the jsonschema library,
validating reports against the XARF v4 core schema and type-specific schemas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import jsonschema
from jsonschema import Draft202012Validator
from jsonschema import ValidationError as JsonSchemaError

from .exceptions import XARFSchemaError, XARFValidationError
from .schema_utils import get_v4_schemas_directory, load_json_schema


@dataclass
class SchemaValidationError:
    """Represents a single schema validation error."""

    field: str
    message: str
    value: Any = None
    schema_path: str = ""


@dataclass
class SchemaValidationResult:
    """Result of schema validation."""

    valid: bool
    errors: list[SchemaValidationError] = field(default_factory=list)


class SchemaValidator:
    """Validates XARF reports against JSON schemas.

    Uses jsonschema library to validate reports against:
    - xarf-core.json (base schema with required fields)
    - Type-specific schemas (e.g., messaging-spam.json)
    """

    def __init__(self) -> None:
        """Initialize the schema validator."""
        self._schemas_dir: Optional[Path] = None
        self._core_schema: Optional[dict[str, Any]] = None
        self._type_schemas: dict[str, dict[str, Any]] = {}
        self._resolver: Optional[jsonschema.RefResolver] = None

        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all schemas from the schemas directory."""
        try:
            self._schemas_dir = get_v4_schemas_directory()
            self._load_core_schema()
            self._setup_resolver()
        except XARFSchemaError:
            # Schemas not found - validator will operate in degraded mode
            pass

    def _load_core_schema(self) -> None:
        """Load the core schema."""
        if self._schemas_dir is None:
            return
        core_path = self._schemas_dir / "xarf-core.json"
        self._core_schema = load_json_schema(core_path)

    def _setup_resolver(self) -> None:
        """Set up the JSON Schema resolver for $ref resolution."""
        if self._schemas_dir is None or self._core_schema is None:
            return

        # Create a resolver that can resolve local file references
        schema_uri = self._schemas_dir.as_uri() + "/"
        self._resolver = jsonschema.RefResolver(
            base_uri=schema_uri,
            referrer=self._core_schema,
        )

    def _get_type_schema(
        self, category: str, type_name: str
    ) -> Optional[dict[str, Any]]:
        """Get the type-specific schema for a category/type combination.

        Args:
            category: The report category.
            type_name: The report type.

        Returns:
            The type schema or None if not found.
        """
        if self._schemas_dir is None:
            return None

        # Check cache first
        cache_key = f"{category}/{type_name}"
        if cache_key in self._type_schemas:
            return self._type_schemas[cache_key]

        # Try to load the schema
        # Convert underscores to hyphens for filename
        hyphenated_type = type_name.replace("_", "-")
        schema_path = self._schemas_dir / "types" / f"{category}-{hyphenated_type}.json"

        if not schema_path.exists():
            return None

        try:
            schema = load_json_schema(schema_path)
            self._type_schemas[cache_key] = schema
            return schema
        except XARFSchemaError:
            return None

    def validate(self, report: dict[str, Any]) -> SchemaValidationResult:
        """Validate a report against JSON schemas.

        Validates against:
        1. Core schema (required fields, basic structure)
        2. Type-specific schema if available

        Args:
            report: The XARF report to validate.

        Returns:
            SchemaValidationResult with valid flag and any errors.
        """
        errors: list[SchemaValidationError] = []

        # Validate against core schema
        core_errors = self._validate_against_core(report)
        errors.extend(core_errors)

        # Validate against type-specific schema if we have category/type
        category = report.get("category")
        type_name = report.get("type")
        if category and type_name:
            type_errors = self._validate_against_type(report, category, type_name)
            errors.extend(type_errors)

        return SchemaValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

    def _validate_against_core(
        self, report: dict[str, Any]
    ) -> list[SchemaValidationError]:
        """Validate report against core schema.

        Args:
            report: The report to validate.

        Returns:
            List of validation errors.
        """
        if self._core_schema is None:
            return []

        return self._run_validation(report, self._core_schema)

    def _validate_against_type(
        self, report: dict[str, Any], category: str, type_name: str
    ) -> list[SchemaValidationError]:
        """Validate report against type-specific schema.

        Args:
            report: The report to validate.
            category: The report category.
            type_name: The report type.

        Returns:
            List of validation errors.
        """
        type_schema = self._get_type_schema(category, type_name)
        if type_schema is None:
            return []

        return self._run_validation(report, type_schema)

    def _run_validation(
        self, report: dict[str, Any], schema: dict[str, Any]
    ) -> list[SchemaValidationError]:
        """Run JSON Schema validation.

        Args:
            report: The report to validate.
            schema: The schema to validate against.

        Returns:
            List of validation errors.
        """
        errors: list[SchemaValidationError] = []

        try:
            # Use Draft 2020-12 validator
            validator_cls = Draft202012Validator
            validator = validator_cls(schema, resolver=self._resolver)

            for error in validator.iter_errors(report):
                errors.append(self._convert_error(error))

        except jsonschema.SchemaError as e:
            # Schema itself is invalid
            errors.append(
                SchemaValidationError(
                    field="$schema",
                    message=f"Invalid schema: {e.message}",
                    schema_path=str(e.schema_path),
                )
            )

        return errors

    def _convert_error(self, error: JsonSchemaError) -> SchemaValidationError:
        """Convert a jsonschema error to our error format.

        Args:
            error: The jsonschema ValidationError.

        Returns:
            SchemaValidationError with user-friendly message.
        """
        # Build field path from error path
        field_path = ".".join(str(p) for p in error.absolute_path) or "$root"

        # Get the value that caused the error
        value = error.instance

        # Create user-friendly message
        message = self._format_error_message(error)

        return SchemaValidationError(
            field=field_path,
            message=message,
            value=value,
            schema_path=".".join(str(p) for p in error.schema_path),
        )

    def _format_error_message(self, error: JsonSchemaError) -> str:
        """Format a user-friendly error message.

        Args:
            error: The jsonschema ValidationError.

        Returns:
            User-friendly error message.
        """
        # Handle common error types with better messages
        validator = error.validator

        if validator == "required":
            missing = error.validator_value
            if isinstance(missing, list):
                return f"Missing required field(s): {', '.join(missing)}"
            return f"Missing required field: {missing}"

        if validator == "type":
            expected = error.validator_value
            actual = type(error.instance).__name__
            return f"Expected type '{expected}', got '{actual}'"

        if validator == "enum":
            allowed = error.validator_value
            return f"Value must be one of: {', '.join(str(v) for v in allowed)}"

        if validator == "pattern":
            pattern = error.validator_value
            return f"Value does not match pattern: {pattern}"

        if validator == "format":
            fmt = error.validator_value
            return f"Invalid format, expected: {fmt}"

        if validator == "minLength":
            min_len = error.validator_value
            return f"Value must be at least {min_len} characters"

        if validator == "maxLength":
            max_len = error.validator_value
            return f"Value must be at most {max_len} characters"

        if validator == "minimum":
            min_val = error.validator_value
            return f"Value must be >= {min_val}"

        if validator == "maximum":
            max_val = error.validator_value
            return f"Value must be <= {max_val}"

        if validator == "additionalProperties":
            return f"Unknown property: {error.message}"

        # Default to the original message
        return str(error.message)

    def is_loaded(self) -> bool:
        """Check if schemas are loaded.

        Returns:
            True if core schema is loaded.
        """
        return self._core_schema is not None


def validate_report(report: dict[str, Any]) -> SchemaValidationResult:
    """Validate a report against JSON schemas.

    Args:
        report: The XARF report to validate.

    Returns:
        SchemaValidationResult with valid flag and any errors.
    """
    validator = SchemaValidator()
    return validator.validate(report)


def validate_report_strict(report: dict[str, Any]) -> None:
    """Validate a report and raise exception on failure.

    Args:
        report: The XARF report to validate.

    Raises:
        XARFValidationError: If validation fails.
    """
    result = validate_report(report)
    if not result.valid:
        error_messages = [f"{e.field}: {e.message}" for e in result.errors]
        raise XARFValidationError(
            f"Schema validation failed: {'; '.join(error_messages)}",
            errors=error_messages,
        )
