"""Tests for XARFParser v2 - schema-driven validation features.

These tests use the correct XARF v4 spec format:
- reporter/sender require: org, contact, domain (not type)
- sender is required
- evidence_source is optional
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from xarf.parser import (
    ValidationError,
    ValidationInfo,
    ValidationResult,
    ValidationWarning,
    XARFParser,
)


def create_valid_report(
    category: str = "messaging",
    report_type: str = "spam",
) -> dict:
    """Create a valid XARF v4 report matching the spec."""
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

    # Add type-specific required fields
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

    return report


class TestXARFParserValidate:
    """Tests for XARFParser.validate() method."""

    def test_validate_returns_validation_result(self) -> None:
        """validate() should return ValidationResult."""
        parser = XARFParser()
        report = create_valid_report()
        result = parser.validate(report)
        assert isinstance(result, ValidationResult)

    def test_validate_valid_report(self) -> None:
        """validate() should return valid=True for valid report."""
        parser = XARFParser()
        report = create_valid_report()
        result = parser.validate(report)
        assert result.valid
        assert len(result.errors) == 0

    def test_validate_missing_required_field(self) -> None:
        """validate() should detect missing required fields."""
        parser = XARFParser()
        report = create_valid_report()
        del report["category"]

        result = parser.validate(report)
        assert not result.valid
        assert any("category" in e.message.lower() for e in result.errors)

    def test_validate_missing_sender(self) -> None:
        """validate() should detect missing sender (required in v4)."""
        parser = XARFParser()
        report = create_valid_report()
        del report["sender"]

        result = parser.validate(report)
        assert not result.valid
        assert any("sender" in e.field.lower() for e in result.errors)

    def test_validate_invalid_category(self) -> None:
        """validate() should detect invalid category."""
        parser = XARFParser()
        report = create_valid_report()
        report["category"] = "invalid_category"

        result = parser.validate(report)
        assert not result.valid
        assert any("category" in e.field for e in result.errors)

    def test_validate_invalid_type_for_category(self) -> None:
        """validate() should detect invalid type for category."""
        parser = XARFParser()
        report = create_valid_report()
        report["type"] = "invalid_type"

        result = parser.validate(report)
        assert not result.valid
        assert any("type" in e.field for e in result.errors)


class TestUnknownFieldDetection:
    """Tests for unknown field detection."""

    def test_unknown_field_generates_warning(self) -> None:
        """Unknown fields should generate warnings."""
        parser = XARFParser()
        report = create_valid_report()
        report["unknown_field"] = "some value"

        result = parser.validate(report)
        # Report is still valid (unknown fields are warnings, not errors)
        assert result.valid
        assert len(result.warnings) > 0
        assert any("unknown_field" in w.field for w in result.warnings)

    def test_unknown_field_in_strict_mode(self) -> None:
        """In strict mode, unknown fields become errors."""
        parser = XARFParser()
        report = create_valid_report()
        report["unknown_field"] = "some value"

        result = parser.validate(report, strict=True)
        # In strict mode, warnings become errors
        assert not result.valid
        assert any("unknown_field" in e.field for e in result.errors)

    def test_multiple_unknown_fields(self) -> None:
        """Multiple unknown fields should all be reported."""
        parser = XARFParser()
        report = create_valid_report()
        report["unknown1"] = "value1"
        report["unknown2"] = "value2"

        result = parser.validate(report)
        unknown_warnings = [
            w for w in result.warnings if "unknown" in w.message.lower()
        ]
        assert len(unknown_warnings) >= 2


class TestShowMissingOptional:
    """Tests for showMissingOptional feature."""

    def test_show_missing_optional_disabled_by_default(self) -> None:
        """Info should be None when showMissingOptional is False."""
        parser = XARFParser()
        report = create_valid_report()

        result = parser.validate(report, show_missing_optional=False)
        assert result.info is None

    def test_show_missing_optional_returns_info(self) -> None:
        """Info should contain missing optional fields when enabled."""
        parser = XARFParser()
        report = create_valid_report()

        result = parser.validate(report, show_missing_optional=True)
        assert result.info is not None
        assert isinstance(result.info, list)

    def test_show_missing_optional_includes_field_info(self) -> None:
        """Info entries should have field and message."""
        parser = XARFParser()
        report = create_valid_report()

        result = parser.validate(report, show_missing_optional=True)
        assert result.info is not None
        if result.info:
            info_item = result.info[0]
            assert isinstance(info_item, ValidationInfo)
            assert hasattr(info_item, "field")
            assert hasattr(info_item, "message")

    def test_show_missing_optional_marks_recommended(self) -> None:
        """Recommended fields should be marked as RECOMMENDED."""
        parser = XARFParser()
        report = create_valid_report()

        result = parser.validate(report, show_missing_optional=True)
        assert result.info is not None
        # Check that some fields are marked as RECOMMENDED or OPTIONAL
        messages = [i.message for i in result.info]
        assert any("RECOMMENDED" in m or "OPTIONAL" in m for m in messages)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_valid(self) -> None:
        """Test ValidationResult represents valid state."""
        result = ValidationResult(valid=True)
        assert result.valid
        assert result.errors == []
        assert result.warnings == []
        assert result.info is None

    def test_validation_result_with_errors(self) -> None:
        """Test ValidationResult contains errors."""
        errors = [ValidationError(field="test", message="error")]
        result = ValidationResult(valid=False, errors=errors)
        assert not result.valid
        assert len(result.errors) == 1

    def test_validation_result_with_warnings(self) -> None:
        """Test ValidationResult contains warnings."""
        warnings = [ValidationWarning(field="test", message="warning")]
        result = ValidationResult(valid=True, warnings=warnings)
        assert result.valid
        assert len(result.warnings) == 1

    def test_validation_result_with_info(self) -> None:
        """Test ValidationResult contains info."""
        info = [ValidationInfo(field="test", message="info")]
        result = ValidationResult(valid=True, info=info)
        assert result.info is not None
        assert len(result.info) == 1


class TestXARFParserParse:
    """Tests for XARFParser.parse() method."""

    def test_parse_valid_report(self) -> None:
        """parse() should return XARFReport for valid report."""
        parser = XARFParser()
        report = create_valid_report()
        result = parser.parse(report)
        assert result is not None
        assert result.category == "messaging"

    def test_parse_json_string(self) -> None:
        """parse() should accept JSON string."""
        import json

        parser = XARFParser()
        report = create_valid_report()
        json_str = json.dumps(report)
        result = parser.parse(json_str)
        assert result is not None

    def test_parse_invalid_json(self) -> None:
        """parse() should raise XARFParseError for invalid JSON."""
        from xarf.exceptions import XARFParseError

        parser = XARFParser()
        with pytest.raises(XARFParseError):
            parser.parse("not valid json")

    def test_parse_strict_mode_raises(self) -> None:
        """parse() in strict mode should raise on validation errors."""
        from xarf.exceptions import XARFValidationError

        parser = XARFParser(strict=True)
        report = create_valid_report()
        del report["category"]

        with pytest.raises(XARFValidationError):
            parser.parse(report)


class TestCategoryValidation:
    """Tests for category-specific validation."""

    def test_all_categories_valid(self) -> None:
        """All 7 categories should be valid."""
        from xarf.schema_registry import schema_registry

        categories = schema_registry.get_categories()
        assert len(categories) == 7
        expected = {
            "messaging",
            "connection",
            "content",
            "infrastructure",
            "copyright",
            "vulnerability",
            "reputation",
        }
        assert categories == expected

    def test_messaging_spam_valid(self) -> None:
        """messaging/spam should be valid."""
        parser = XARFParser()
        report = create_valid_report("messaging", "spam")
        result = parser.validate(report)
        assert result.valid

    def test_connection_ddos_valid(self) -> None:
        """connection/ddos should be valid."""
        parser = XARFParser()
        report = create_valid_report("connection", "ddos")
        result = parser.validate(report)
        assert result.valid

    def test_content_phishing_valid(self) -> None:
        """content/phishing should be valid."""
        parser = XARFParser()
        report = create_valid_report("content", "phishing")
        result = parser.validate(report)
        assert result.valid


class TestSchemaRegistryIntegration:
    """Tests for SchemaRegistry integration."""

    def test_parser_uses_schema_registry_categories(self) -> None:
        """Parser should use SchemaRegistry for category validation."""
        from xarf.schema_registry import schema_registry

        parser = XARFParser()
        report = create_valid_report()

        # Use a category from the registry
        categories = schema_registry.get_categories()
        report["category"] = next(iter(categories))

        # Should not fail on category validation
        result = parser.validate(report)
        # May fail on type-specific fields, but not on category
        category_errors = [e for e in result.errors if "category" in e.field.lower()]
        assert len(category_errors) == 0

    def test_parser_uses_schema_registry_types(self) -> None:
        """Parser should use SchemaRegistry for type validation."""
        from xarf.schema_registry import schema_registry

        parser = XARFParser()
        report = create_valid_report()

        # Use a type from the registry
        types = schema_registry.get_types_for_category("messaging")
        report["type"] = next(iter(types))

        result = parser.validate(report)
        # May fail on type-specific fields, but not on type itself
        type_errors = [
            e
            for e in result.errors
            if e.field == "type" and "invalid type" in e.message.lower()
        ]
        assert len(type_errors) == 0
