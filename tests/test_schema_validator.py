"""Tests for xarf.schema_validator.SchemaValidator."""

from collections import deque

import jsonschema.exceptions

from xarf import ContactInfo, SpamReport
from xarf.models import ValidationError, XARFEvidence
from xarf.schema_validator import SchemaValidator, schema_validator

# ---------------------------------------------------------------------------
# Helper fixture
# ---------------------------------------------------------------------------


def _valid_spam_report() -> SpamReport:
    """Return a fully valid SpamReport for use in tests.

    Includes smtp_from and source_port because the schema conditionally
    requires them when protocol is "smtp".

    Returns:
        A SpamReport with all schema-required fields populated.
    """
    return SpamReport(
        xarf_version="4.2.0",
        report_id="02eb480f-8172-431a-9276-c28ba90f694a",
        timestamp="2025-01-11T10:59:45Z",
        reporter=ContactInfo(
            org="Test Org", contact="test@test.com", domain="test.com"
        ),
        sender=ContactInfo(org="Test Org", contact="test@test.com", domain="test.com"),
        source_identifier="192.168.1.1",
        category="messaging",
        type="spam",
        protocol="smtp",
        smtp_from="spammer@example.com",
        source_port=25,
    )


# ---------------------------------------------------------------------------
# TestValidReports
# ---------------------------------------------------------------------------


class TestValidReports:
    def test_valid_spam_report_has_no_errors(self) -> None:
        report = _valid_spam_report()
        errors = schema_validator.validate(report)
        assert errors == []


# ---------------------------------------------------------------------------
# TestInvalidReports
# ---------------------------------------------------------------------------


class TestInvalidReports:
    def test_invalid_report_id_format(self) -> None:
        report = _valid_spam_report()
        report.report_id = "not-a-uuid"
        errors = schema_validator.validate(report)
        assert len(errors) >= 1
        fields = [e.field for e in errors]
        assert any("report_id" in f for f in fields)

    def test_invalid_xarf_version_pattern(self) -> None:
        report = _valid_spam_report()
        report.xarf_version = "3.0.0"
        errors = schema_validator.validate(report)
        assert len(errors) >= 1
        assert any(e.field == "xarf_version" for e in errors)

    def test_errors_are_validation_error_instances(self) -> None:
        report = _valid_spam_report()
        report.report_id = "not-a-uuid"
        errors = schema_validator.validate(report)
        assert all(isinstance(e, ValidationError) for e in errors)
        assert all(len(e.message) > 0 for e in errors)


# ---------------------------------------------------------------------------
# TestStrictMode
# ---------------------------------------------------------------------------


class TestStrictMode:
    def test_recommended_field_missing_passes_normal_mode(self) -> None:
        report = _valid_spam_report()
        # evidence_source is x-recommended; omitting it is fine in normal mode
        assert report.evidence_source is None
        errors = schema_validator.validate(report, strict=False)
        assert errors == []

    def test_recommended_field_missing_fails_strict_mode(self) -> None:
        report = _valid_spam_report()
        assert report.evidence_source is None
        errors = schema_validator.validate(report, strict=True)
        assert len(errors) >= 1
        assert any("evidence_source" in e.message for e in errors)

    def test_strict_mode_valid_when_all_recommended_present(self) -> None:
        report = _valid_spam_report()
        # Core x-recommended: evidence_source, source_port (already set), evidence, confidence
        # evidence_item x-recommended: description, hash
        # Spam type x-recommended: evidence_source, smtp_to, subject, message_id
        # confidence is 0.0-1.0 per schema
        report.evidence_source = "spamtrap"
        report.evidence = [
            XARFEvidence(
                content_type="message/rfc822",
                payload="dGVzdA==",
                description="Spam email evidence",
                hash="sha256:abc123def456abc123def456abc123def456abc123def456abc123def456abc12345",
            )
        ]
        report.confidence = 1  # schema max is 1.0
        report.smtp_to = "victim@example.com"
        report.subject = "Buy now!"
        report.message_id = "<abc123@example.com>"
        errors = schema_validator.validate(report, strict=True)
        assert errors == []


# ---------------------------------------------------------------------------
# TestErrorDeduplication
# ---------------------------------------------------------------------------


class TestErrorDeduplication:
    def test_no_duplicate_errors(self) -> None:
        report = _valid_spam_report()
        report.report_id = "not-a-uuid"
        errors = schema_validator.validate(report)
        pairs = [(e.field, e.message) for e in errors]
        assert len(pairs) == len(set(pairs))


# ---------------------------------------------------------------------------
# TestFormatValidationErrorHelper
# ---------------------------------------------------------------------------


class TestFormatValidationErrorHelper:
    def _make_validator(self) -> SchemaValidator:
        """Return a SchemaValidator (loads schemas lazily on demand)."""
        return SchemaValidator()

    def test_field_from_absolute_path(self) -> None:
        sv = self._make_validator()
        err = jsonschema.exceptions.ValidationError(
            message="test error",
            path=deque(["reporter", "contact"]),
            instance="bad-value",
        )
        ve = sv._format_validation_error(err)
        assert ve.field == "reporter.contact"

    def test_empty_field_for_root_error(self) -> None:
        sv = self._make_validator()
        err = jsonschema.exceptions.ValidationError(
            message="root error",
            path=deque(),
            instance={"key": "value"},
        )
        ve = sv._format_validation_error(err)
        assert ve.field == ""

    def test_message_is_raw(self) -> None:
        sv = self._make_validator()
        raw_message = "some raw jsonschema message"
        err = jsonschema.exceptions.ValidationError(
            message=raw_message,
            path=deque(),
            instance=None,
        )
        ve = sv._format_validation_error(err)
        assert ve.message == raw_message

    def test_value_is_instance(self) -> None:
        sv = self._make_validator()
        instance_value = {"foo": "bar"}
        err = jsonschema.exceptions.ValidationError(
            message="test",
            path=deque(),
            instance=instance_value,
        )
        ve = sv._format_validation_error(err)
        assert ve.value == instance_value


# ---------------------------------------------------------------------------
# TestSupportedTypes
# ---------------------------------------------------------------------------


class TestSupportedTypes:
    def test_returns_list_of_strings(self) -> None:
        sv = SchemaValidator()
        result = sv.get_supported_types()
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_contains_known_types(self) -> None:
        sv = SchemaValidator()
        result = sv.get_supported_types()
        assert "messaging/spam" in result
        assert "connection/ddos" in result

    def test_format_is_category_slash_type(self) -> None:
        sv = SchemaValidator()
        result = sv.get_supported_types()
        assert len(result) > 0
        for item in result:
            assert item.count("/") == 1


# ---------------------------------------------------------------------------
# TestHasTypeSchema
# ---------------------------------------------------------------------------


class TestHasTypeSchema:
    def test_known_pair_returns_true(self) -> None:
        sv = SchemaValidator()
        assert sv.has_type_schema("messaging", "spam") is True

    def test_unknown_type_returns_false(self) -> None:
        sv = SchemaValidator()
        assert sv.has_type_schema("messaging", "unknown_type") is False

    def test_unknown_category_returns_false(self) -> None:
        sv = SchemaValidator()
        assert sv.has_type_schema("unknown_category", "spam") is False


# ---------------------------------------------------------------------------
# TestDictInput — validate() accepts raw dicts
# ---------------------------------------------------------------------------


def _valid_spam_dict() -> dict[str, object]:
    """Return the same report as _valid_spam_report() but as a plain dict."""
    _contact = {"org": "Test Org", "contact": "test@test.com", "domain": "test.com"}
    return {
        "xarf_version": "4.2.0",
        "report_id": "02eb480f-8172-431a-9276-c28ba90f694a",
        "timestamp": "2025-01-11T10:59:45Z",
        "reporter": _contact,
        "sender": _contact,
        "source_identifier": "192.168.1.1",
        "category": "messaging",
        "type": "spam",
        "protocol": "smtp",
        "smtp_from": "spammer@example.com",
        "source_port": 25,
    }


class TestDictInput:
    def test_valid_dict_produces_no_errors(self) -> None:
        """validate() accepts a raw dict and returns no errors for a valid report."""
        errors = schema_validator.validate(_valid_spam_dict())
        assert errors == []

    def test_invalid_dict_produces_errors(self) -> None:
        """validate() accepts a raw dict and returns errors for an invalid report."""
        data = _valid_spam_dict()
        data["report_id"] = "not-a-uuid"  # type: ignore[index]
        errors = schema_validator.validate(data)
        assert len(errors) >= 1
        assert any("report_id" in e.field for e in errors)

    def test_dict_and_model_produce_same_errors(self) -> None:
        """validate() returns identical errors for a dict and equivalent model."""
        data = _valid_spam_dict()
        data["report_id"] = "not-a-uuid"  # type: ignore[index]

        report = _valid_spam_report()
        report.report_id = "not-a-uuid"

        dict_errors = schema_validator.validate(data)
        model_errors = schema_validator.validate(report)
        assert [(e.field, e.message) for e in dict_errors] == [
            (e.field, e.message) for e in model_errors
        ]
