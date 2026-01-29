"""Tests for SchemaValidator - JSON Schema validation."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from xarf.exceptions import XARFValidationError
from xarf.schema_validator import (
    SchemaValidationError,
    SchemaValidationResult,
    SchemaValidator,
    validate_report,
    validate_report_strict,
)


def create_valid_report(
    category: str = "messaging",
    report_type: str = "spam",
    include_type_fields: bool = True,
) -> dict:
    """Create a minimal valid XARF v4 report.

    Args:
        category: Report category.
        report_type: Report type.
        include_type_fields: Whether to include type-specific required fields.

    Returns:
        Valid XARF v4 report dict.
    """
    report: dict = {
        "xarf_version": "4.0.0",
        "report_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reporter": {
            "org": "Test Organization",
            "contact": "abuse@test.org",
            "domain": "test.org",
        },
        "sender": {
            "org": "Sender Organization",
            "contact": "abuse@sender.org",
            "domain": "sender.org",
        },
        "source_identifier": "192.0.2.1",
        "category": category,
        "type": report_type,
    }

    # Add type-specific required fields based on actual schema requirements
    if include_type_fields:
        if category == "messaging" and report_type == "spam":
            report["protocol"] = "smtp"
            report["smtp_from"] = "spammer@example.com"
            report["source_port"] = 25
        elif category == "connection" and report_type == "ddos":
            report["destination_ip"] = "192.0.2.100"
            report["protocol"] = "tcp"
            report["first_seen"] = datetime.now(timezone.utc).isoformat()
            report["source_port"] = 12345
        elif category == "content" and report_type == "phishing":
            report["url"] = "https://phishing.example.com/login"
        elif category == "infrastructure" and report_type == "botnet":
            report["compromise_evidence"] = "C2 communication detected"
        elif category == "vulnerability" and report_type == "cve":
            report["cve_id"] = "CVE-2024-12345"
            report["service"] = "http"
            report["service_port"] = 80

    return report


class TestSchemaValidator:
    """Tests for SchemaValidator class."""

    def test_validator_loads_schemas(self) -> None:
        """Verify SchemaValidator loads schemas on init."""
        validator = SchemaValidator()
        assert validator.is_loaded()

    def test_validate_returns_result(self) -> None:
        """validate() should return SchemaValidationResult."""
        validator = SchemaValidator()
        report = create_valid_report()
        result = validator.validate(report)
        assert isinstance(result, SchemaValidationResult)

    def test_validate_valid_report(self) -> None:
        """validate() should return valid=True for valid report."""
        validator = SchemaValidator()
        report = create_valid_report()
        result = validator.validate(report)
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_missing_required_field(self) -> None:
        """validate() should detect missing required fields."""
        validator = SchemaValidator()
        report = create_valid_report()
        del report["category"]

        result = validator.validate(report)
        assert not result.valid
        assert len(result.errors) > 0

        # Check error mentions the missing field
        error_messages = [e.message for e in result.errors]
        assert any("category" in msg for msg in error_messages)

    def test_validate_invalid_category(self) -> None:
        """validate() should detect invalid category values."""
        validator = SchemaValidator()
        report = create_valid_report()
        report["category"] = "invalid_category"

        result = validator.validate(report)
        assert not result.valid
        assert any("category" in e.field for e in result.errors)

    def test_validate_invalid_xarf_version(self) -> None:
        """validate() should detect invalid xarf_version."""
        validator = SchemaValidator()
        report = create_valid_report()
        report["xarf_version"] = "3.0.0"

        result = validator.validate(report)
        assert not result.valid

    def test_validate_missing_reporter(self) -> None:
        """validate() should detect missing reporter."""
        validator = SchemaValidator()
        report = create_valid_report()
        del report["reporter"]

        result = validator.validate(report)
        assert not result.valid

    def test_validate_missing_sender(self) -> None:
        """validate() should detect missing sender (required in v4)."""
        validator = SchemaValidator()
        report = create_valid_report()
        del report["sender"]

        result = validator.validate(report)
        assert not result.valid

    def test_validate_invalid_reporter_structure(self) -> None:
        """validate() should detect invalid reporter structure."""
        validator = SchemaValidator()
        report = create_valid_report()
        report["reporter"] = {"org": "Test"}  # Missing contact and domain

        result = validator.validate(report)
        assert not result.valid


class TestSchemaValidationError:
    """Tests for SchemaValidationError dataclass."""

    def test_error_has_required_fields(self) -> None:
        """Verify SchemaValidationError has field and message."""
        error = SchemaValidationError(
            field="category",
            message="Invalid value",
            value="invalid",
        )
        assert error.field == "category"
        assert error.message == "Invalid value"
        assert error.value == "invalid"

    def test_error_default_values(self) -> None:
        """Verify SchemaValidationError has sensible defaults."""
        error = SchemaValidationError(field="test", message="error")
        assert error.value is None
        assert error.schema_path == ""


class TestSchemaValidationResult:
    """Tests for SchemaValidationResult dataclass."""

    def test_result_valid_true(self) -> None:
        """Verify SchemaValidationResult represents valid state."""
        result = SchemaValidationResult(valid=True)
        assert result.valid
        assert result.errors == []

    def test_result_valid_false_with_errors(self) -> None:
        """Verify SchemaValidationResult contains errors when invalid."""
        errors = [SchemaValidationError(field="test", message="error")]
        result = SchemaValidationResult(valid=False, errors=errors)
        assert not result.valid
        assert len(result.errors) == 1


class TestValidateReportFunction:
    """Tests for validate_report convenience function."""

    def test_validate_report_valid(self) -> None:
        """validate_report() should return valid result for valid report."""
        report = create_valid_report()
        result = validate_report(report)
        assert result.valid

    def test_validate_report_invalid(self) -> None:
        """validate_report() should return invalid result for invalid report."""
        report = {"invalid": "report"}
        result = validate_report(report)
        assert not result.valid


class TestValidateReportStrictFunction:
    """Tests for validate_report_strict convenience function."""

    def test_validate_report_strict_valid(self) -> None:
        """validate_report_strict() should not raise for valid report."""
        report = create_valid_report()
        # Should not raise
        validate_report_strict(report)

    def test_validate_report_strict_invalid(self) -> None:
        """validate_report_strict() should raise XARFValidationError for invalid."""
        report = {"invalid": "report"}
        with pytest.raises(XARFValidationError) as exc_info:
            validate_report_strict(report)
        assert "Schema validation failed" in str(exc_info.value)


class TestSchemaValidatorCategories:
    """Tests for validating different report categories."""

    def test_validate_messaging_spam(self) -> None:
        """validate() should accept valid messaging/spam report."""
        validator = SchemaValidator()
        report = create_valid_report(category="messaging", report_type="spam")

        result = validator.validate(report)
        assert result.valid

    def test_validate_connection_ddos(self) -> None:
        """validate() should accept valid connection/ddos report."""
        validator = SchemaValidator()
        report = create_valid_report(category="connection", report_type="ddos")

        result = validator.validate(report)
        assert result.valid

    def test_validate_content_phishing(self) -> None:
        """validate() should accept valid content/phishing report."""
        validator = SchemaValidator()
        report = create_valid_report(category="content", report_type="phishing")

        result = validator.validate(report)
        assert result.valid

    def test_validate_infrastructure_botnet(self) -> None:
        """validate() should accept valid infrastructure/botnet report."""
        validator = SchemaValidator()
        report = create_valid_report(category="infrastructure", report_type="botnet")

        result = validator.validate(report)
        assert result.valid

    def test_validate_vulnerability_cve(self) -> None:
        """validate() should accept valid vulnerability/cve report."""
        validator = SchemaValidator()
        report = create_valid_report(category="vulnerability", report_type="cve")

        result = validator.validate(report)
        assert result.valid


class TestSchemaValidatorOptionalFields:
    """Tests for optional field handling."""

    def test_validate_with_evidence(self) -> None:
        """validate() should accept report with evidence."""
        validator = SchemaValidator()
        report = create_valid_report()
        report["evidence"] = [
            {
                "content_type": "text/plain",
                "description": "Spam email headers",
                "payload": "From: spammer@example.com",
            }
        ]

        result = validator.validate(report)
        assert result.valid

    def test_validate_with_tags(self) -> None:
        """validate() should accept report with tags."""
        validator = SchemaValidator()
        report = create_valid_report()
        # Tags must follow pattern: namespace:value
        report["tags"] = ["category:spam", "priority:high", "source:spamtrap"]

        result = validator.validate(report)
        assert result.valid

    def test_validate_with_internal_metadata(self) -> None:
        """validate() should accept report with _internal metadata."""
        validator = SchemaValidator()
        report = create_valid_report()
        report["_internal"] = {
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "source_system": "test",
        }

        result = validator.validate(report)
        assert result.valid


class TestSchemaValidatorErrorMessages:
    """Tests for error message formatting."""

    def test_error_message_for_missing_required(self) -> None:
        """Error message should clearly indicate missing required field."""
        validator = SchemaValidator()
        report = create_valid_report()
        del report["category"]

        result = validator.validate(report)
        assert not result.valid

        # Should have a clear error message
        messages = [e.message for e in result.errors]
        assert any(
            "required" in msg.lower() or "category" in msg.lower() for msg in messages
        )

    def test_error_message_for_invalid_enum(self) -> None:
        """Error message should indicate valid enum values."""
        validator = SchemaValidator()
        report = create_valid_report()
        report["category"] = "not_a_valid_category"

        result = validator.validate(report)
        assert not result.valid

        # Should mention valid values
        messages = [e.message for e in result.errors]
        assert any(
            "must be one of" in msg.lower() or "enum" in msg.lower() for msg in messages
        )
