"""Tests for :class:`xarf.validator.XARFValidator` and the :data:`_validator` singleton.

Port of the JavaScript ``validator.test.ts`` test suite.

Covers:

- Missing required fields.
- Invalid category and type values.
- Strict-mode promotion of recommended fields and unknown fields.
- Format validation (UUID, timestamp, semver).
- Required nested sub-fields (reporter.contact, reporter.domain).
- Evidence-source enum validation.
- Category-specific business rules.
- Port range validation.
- ``on_behalf_of`` handling.
- ``show_missing_optional`` info population.
- Unknown-field detection in both modes.
- ``valid`` flag accuracy.
"""

from __future__ import annotations

import copy
from typing import Any

from xarf.validator import _validator

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_CONTACT: dict[str, str] = {
    "org": "Test Org",
    "contact": "test@example.com",
    "domain": "example.com",
}


def _valid_ddos_report() -> dict[str, Any]:
    """Return a fresh minimal valid ``connection/ddos`` report dict.

    Returns:
        A new dict on every call to prevent cross-test mutation.
    """
    return {
        "xarf_version": "4.2.0",
        "report_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2024-01-15T10:30:00Z",
        "reporter": copy.deepcopy(_CONTACT),
        "sender": copy.deepcopy(_CONTACT),
        "source_identifier": "192.0.2.1",
        "category": "connection",
        "type": "ddos",
        "evidence_source": "honeypot",
        "source_port": 12345,
        "destination_ip": "203.0.113.10",
        "protocol": "tcp",
        "first_seen": "2024-01-15T09:00:00Z",
    }


# ---------------------------------------------------------------------------
# TestMissingRequiredFields
# ---------------------------------------------------------------------------


class TestMissingRequiredFields:
    """Tests that missing required fields produce validation errors."""

    def test_empty_report_is_invalid(self) -> None:
        """An empty dict must fail validation with at least one error."""
        result = _validator.validate({})
        assert result.valid is False
        assert len(result.errors) > 0

    def test_missing_source_identifier_is_invalid(self) -> None:
        """A report without ``source_identifier`` must fail validation."""
        data = _valid_ddos_report()
        del data["source_identifier"]
        result = _validator.validate(data)
        assert result.valid is False


# ---------------------------------------------------------------------------
# TestInvalidCategory
# ---------------------------------------------------------------------------


class TestInvalidCategory:
    """Tests that an unrecognised category value produces an appropriate error."""

    def test_invalid_category_produces_category_error(self) -> None:
        """An unknown category value must produce an error with ``field="category"``."""
        data = _valid_ddos_report()
        data["category"] = "totally_invalid_category"
        result = _validator.validate(data)
        assert result.valid is False
        error_fields = [e.field for e in result.errors]
        assert "category" in error_fields


# ---------------------------------------------------------------------------
# TestStrictMode
# ---------------------------------------------------------------------------


class TestStrictMode:
    """Tests for strict-mode behaviour."""

    def test_invalid_xarf_version_fails_in_strict(self) -> None:
        """``xarf_version="3.0.0"`` must fail validation in strict mode."""
        data = _valid_ddos_report()
        data["xarf_version"] = "3.0.0"
        result = _validator.validate(data, strict=True)
        assert result.valid is False

    def test_unknown_field_is_warning_in_non_strict(self) -> None:
        """An unknown field produces a warning (not an error) in non-strict mode."""
        data = _valid_ddos_report()
        data["unknown_exotic_field_xyz"] = "value"
        result = _validator.validate(data, strict=False)
        assert result.valid is True
        warning_fields = [w.field for w in result.warnings]
        assert "unknown_exotic_field_xyz" in warning_fields

    def test_unknown_field_is_error_in_strict(self) -> None:
        """An unknown field becomes an error in strict mode."""
        data = _valid_ddos_report()
        data["unknown_exotic_field_xyz"] = "value"
        result = _validator.validate(data, strict=True)
        assert result.valid is False
        error_fields = [e.field for e in result.errors]
        assert "unknown_exotic_field_xyz" in error_fields

    def test_strict_mode_clears_warnings_on_promotion(self) -> None:
        """In strict mode, unknown-field entries appear as errors and not warnings."""
        data = _valid_ddos_report()
        data["unknown_exotic_field_xyz"] = "value"
        result = _validator.validate(data, strict=True)
        warning_fields = [w.field for w in result.warnings]
        assert "unknown_exotic_field_xyz" not in warning_fields


# ---------------------------------------------------------------------------
# TestFormatValidation
# ---------------------------------------------------------------------------


class TestFormatValidation:
    """Tests for field-level format validation (UUID, timestamp, semver)."""

    def test_invalid_uuid_report_id_fails(self) -> None:
        """A non-UUID ``report_id`` must produce an error referencing ``report_id``."""
        data = _valid_ddos_report()
        data["report_id"] = "not-a-uuid"
        result = _validator.validate(data)
        assert result.valid is False
        error_fields_and_messages = " ".join(
            f"{e.field} {e.message}" for e in result.errors
        )
        assert "report_id" in error_fields_and_messages

    def test_wrong_type_timestamp_fails(self) -> None:
        """A non-string ``timestamp`` (wrong JSON type) must produce an error.

        Note:
            ``date-time`` *format* validation (e.g. rejecting ``"foo"``) requires
            the optional ``rfc3339-validator`` package, which is not a runtime
            dependency.  This test covers the weaker guarantee: a timestamp that is
            not a string at all (e.g. an integer) is caught by jsonschema's type
            checker, which is always active.
        """
        data = _valid_ddos_report()
        data["timestamp"] = 42  # wrong type — caught without optional format deps
        result = _validator.validate(data)
        assert result.valid is False
        assert any(e.field == "timestamp" for e in result.errors)

    def test_invalid_version_format_fails(self) -> None:
        """A non-semver ``xarf_version`` such as ``"4.0"`` must fail validation."""
        data = _valid_ddos_report()
        data["xarf_version"] = "4.0"
        result = _validator.validate(data)
        assert result.valid is False

    def test_valid_report_passes(self) -> None:
        """A fully valid report must pass validation with no errors."""
        result = _validator.validate(_valid_ddos_report())
        assert result.valid is True
        assert result.errors == []


# ---------------------------------------------------------------------------
# TestRequiredFieldEdgeCases
# ---------------------------------------------------------------------------


class TestRequiredFieldEdgeCases:
    """Tests for required sub-fields within nested objects."""

    def test_missing_reporter_contact_fails(self) -> None:
        """A report without ``reporter.contact`` must fail with an error
        referencing both.

        Args: (none beyond self)
        """
        data = _valid_ddos_report()
        del data["reporter"]["contact"]
        result = _validator.validate(data)
        assert result.valid is False
        combined = " ".join(f"{e.field} {e.message}" for e in result.errors)
        assert "reporter" in combined.lower()
        assert "contact" in combined.lower()

    def test_missing_reporter_domain_fails(self) -> None:
        """A report without ``reporter.domain`` must fail with an error
        referencing both.

        Args: (none beyond self)
        """
        data = _valid_ddos_report()
        del data["reporter"]["domain"]
        result = _validator.validate(data)
        assert result.valid is False
        combined = " ".join(f"{e.field} {e.message}" for e in result.errors)
        assert "reporter" in combined.lower()
        assert "domain" in combined.lower()


# ---------------------------------------------------------------------------
# TestValueValidation
# ---------------------------------------------------------------------------


class TestValueValidation:
    """Tests for field value constraints (enums, ranges)."""

    def test_invalid_evidence_source_enum_fails(self) -> None:
        """An invalid ``evidence_source`` value must fail with
        ``field="evidence_source"``."""
        data = _valid_ddos_report()
        data["evidence_source"] = "made_up_source_value"
        result = _validator.validate(data)
        assert result.valid is False
        error_fields = [e.field for e in result.errors]
        assert "evidence_source" in error_fields


# ---------------------------------------------------------------------------
# TestCategorySpecific
# ---------------------------------------------------------------------------


class TestCategorySpecific:
    """Category-specific validation rule tests."""

    def test_valid_messaging_spam_report_passes(self) -> None:
        """A minimal valid ``messaging/spam`` report (protocol=sms) must pass."""
        data: dict[str, Any] = {
            "xarf_version": "4.2.0",
            "report_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": copy.deepcopy(_CONTACT),
            "sender": copy.deepcopy(_CONTACT),
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "honeypot",
            "protocol": "sms",
        }
        result = _validator.validate(data)
        assert result.valid is True

    def test_unknown_type_fails(self) -> None:
        """An unknown report type within a valid category must fail validation."""
        data = _valid_ddos_report()
        data["type"] = "no_such_type_ever"
        result = _validator.validate(data)
        assert result.valid is False

    def test_smtp_spam_without_smtp_from_fails(self) -> None:
        """``messaging/spam`` with ``protocol=smtp`` but no ``smtp_from`` must fail."""
        data: dict[str, Any] = {
            "xarf_version": "4.2.0",
            "report_id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": copy.deepcopy(_CONTACT),
            "sender": copy.deepcopy(_CONTACT),
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "honeypot",
            "protocol": "smtp",
            # smtp_from intentionally omitted
        }
        result = _validator.validate(data)
        assert result.valid is False
        combined = " ".join(f"{e.field} {e.message}" for e in result.errors)
        assert "smtp_from" in combined

    def test_ddos_without_destination_ip_is_valid(self) -> None:
        """``connection/ddos`` without ``destination_ip`` (recommended) is valid in
        non-strict mode."""
        data = _valid_ddos_report()
        del data["destination_ip"]
        result = _validator.validate(data, strict=False)
        assert result.valid is True

    def test_phishing_without_url_fails(self) -> None:
        """``content/phishing`` without ``url`` (required) must fail validation."""
        data: dict[str, Any] = {
            "xarf_version": "4.2.0",
            "report_id": "6ba7b812-9dad-11d1-80b4-00c04fd430c8",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": copy.deepcopy(_CONTACT),
            "sender": copy.deepcopy(_CONTACT),
            "source_identifier": "192.0.2.1",
            "category": "content",
            "type": "phishing",
            "evidence_source": "honeypot",
            # url intentionally omitted
        }
        result = _validator.validate(data)
        assert result.valid is False

    def test_phishing_with_wrong_type_url_fails(self) -> None:
        """``content/phishing`` with a non-string ``url`` must produce an error.

        Note:
            ``uri`` *format* validation (e.g. rejecting ``"not a url"`` strings)
            requires the optional ``rfc3986-validator`` package, which is not a
            runtime dependency.  This test covers the weaker guarantee: a ``url``
            field with the wrong JSON type (e.g. an integer) is rejected by
            jsonschema's type checker, which is always active.
        """
        data: dict[str, Any] = {
            "xarf_version": "4.2.0",
            "report_id": "6ba7b813-9dad-11d1-80b4-00c04fd430c8",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": copy.deepcopy(_CONTACT),
            "sender": copy.deepcopy(_CONTACT),
            "source_identifier": "192.0.2.1",
            "category": "content",
            "type": "phishing",
            "evidence_source": "honeypot",
            "url": 12345,  # wrong type — caught without optional format deps
        }
        result = _validator.validate(data)
        assert result.valid is False
        assert any(e.field == "url" for e in result.errors)
        error_fields = [e.field for e in result.errors]
        assert "url" in error_fields

    def test_valid_botnet_report_passes(self) -> None:
        """A minimal valid ``infrastructure/botnet`` report must pass validation."""
        data: dict[str, Any] = {
            "xarf_version": "4.2.0",
            "report_id": "6ba7b814-9dad-11d1-80b4-00c04fd430c8",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": copy.deepcopy(_CONTACT),
            "sender": copy.deepcopy(_CONTACT),
            "source_identifier": "192.0.2.1",
            "category": "infrastructure",
            "type": "botnet",
            "evidence_source": "honeypot",
            "compromise_evidence": "C2 communication observed",
        }
        result = _validator.validate(data)
        assert result.valid is True


# ---------------------------------------------------------------------------
# TestPortValidation
# ---------------------------------------------------------------------------


class TestPortValidation:
    """Tests for ``destination_port`` range and type validation."""

    def test_destination_port_as_string_fails(self) -> None:
        """``destination_port`` must be an integer; a string value must fail."""
        data = _valid_ddos_report()
        data["destination_port"] = "80"  # type: ignore[assignment]
        result = _validator.validate(data)
        assert result.valid is False
        error_fields = [e.field for e in result.errors]
        assert "destination_port" in error_fields

    def test_destination_port_too_high_fails(self) -> None:
        """``destination_port=70000`` exceeds 65535 and must fail validation."""
        data = _valid_ddos_report()
        data["destination_port"] = 70000
        result = _validator.validate(data)
        assert result.valid is False

    def test_destination_port_negative_fails(self) -> None:
        """``destination_port=-1`` is below the minimum and must fail validation."""
        data = _valid_ddos_report()
        data["destination_port"] = -1
        result = _validator.validate(data)
        assert result.valid is False


# ---------------------------------------------------------------------------
# TestOnBehalfOf
# ---------------------------------------------------------------------------


class TestOnBehalfOf:
    """Tests for the optional ``on_behalf_of`` field."""

    def test_valid_on_behalf_of_passes(self) -> None:
        """A report with a valid ``on_behalf_of`` contact dict must pass validation."""
        data = _valid_ddos_report()
        data["on_behalf_of"] = copy.deepcopy(_CONTACT)
        result = _validator.validate(data)
        assert result.valid is True


# ---------------------------------------------------------------------------
# TestShowMissingOptional
# ---------------------------------------------------------------------------


class TestShowMissingOptional:
    """Tests for ``show_missing_optional`` info population."""

    def test_show_missing_optional_false_returns_none_info(self) -> None:
        """``show_missing_optional=False`` must leave ``result.info`` as ``None``."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=False)
        assert result.info is None

    def test_show_missing_optional_true_returns_list(self) -> None:
        """``show_missing_optional=True`` must populate ``result.info`` with a list."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert isinstance(result.info, list)

    def test_info_contains_description(self) -> None:
        """``description`` (optional core field absent from test report) must
        appear in info."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        assert "description" in info_fields

    def test_info_contains_confidence(self) -> None:
        """``confidence`` (recommended core field absent from test report) must
        appear in info."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        assert "confidence" in info_fields

    def test_info_contains_tags(self) -> None:
        """``tags`` (optional core field absent from test report) must appear in
        info."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        assert "tags" in info_fields

    def test_info_contains_type_specific_optional_field(self) -> None:
        """Type-specific optional field ``destination_port`` must appear in info
        for ddos."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        assert "destination_port" in info_fields

    def test_present_fields_not_in_info(self) -> None:
        """Fields present in the report must not appear in info."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        for present in (
            "xarf_version",
            "report_id",
            "category",
            "type",
            "evidence_source",
        ):
            assert present not in info_fields

    def test_confidence_info_message_contains_recommended(self) -> None:
        """The ``confidence`` info entry message must start with ``RECOMMENDED:``."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        confidence_entries = [e for e in result.info if e["field"] == "confidence"]
        assert len(confidence_entries) == 1
        assert confidence_entries[0]["message"].startswith("RECOMMENDED:")

    def test_description_info_message_contains_optional(self) -> None:
        """The ``description`` info entry message must start with ``OPTIONAL:``."""
        result = _validator.validate(_valid_ddos_report(), show_missing_optional=True)
        assert result.info is not None
        desc_entries = [e for e in result.info if e["field"] == "description"]
        assert len(desc_entries) == 1
        assert desc_entries[0]["message"].startswith("OPTIONAL:")

    def test_content_phishing_info_contains_content_base_fields(self) -> None:
        """content/phishing info must include fields from the
        content-base.json ``$ref``.

        Verifies that ``_extract_type_optional_fields`` follows ``allOf`` ``$ref``
        chains to ``-base.json`` schemas.  ``registrar`` and ``hosting_provider``
        are optional fields defined in ``content-base.json``.
        """
        phishing_data: dict[str, Any] = {
            "xarf_version": "4.2.0",
            "report_id": "550e8400-e29b-41d4-a716-446655440000",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "content",
            "type": "phishing",
            "url": "https://phishing.example.com/login",
        }
        result = _validator.validate(phishing_data, show_missing_optional=True)
        assert result.info is not None
        info_fields = [e["field"] for e in result.info]
        assert "registrar" in info_fields
        assert "hosting_provider" in info_fields


# ---------------------------------------------------------------------------
# TestUnknownFieldDetection
# ---------------------------------------------------------------------------


class TestUnknownFieldDetection:
    """Tests for unknown-field detection logic."""

    def test_two_unknown_fields_produce_two_warnings(self) -> None:
        """Two unknown fields must each produce exactly one warning."""
        data = _valid_ddos_report()
        data["unknown_alpha"] = "a"
        data["unknown_beta"] = "b"
        result = _validator.validate(data, strict=False)
        warning_fields = [w.field for w in result.warnings]
        assert "unknown_alpha" in warning_fields
        assert "unknown_beta" in warning_fields

    def test_unknown_field_warnings_have_correct_field_values(self) -> None:
        """Each unknown-field warning must carry the field name in its ``field``
        attribute."""
        data = _valid_ddos_report()
        data["xarf_mystery_field"] = "mystery"
        result = _validator.validate(data, strict=False)
        matched = [w for w in result.warnings if w.field == "xarf_mystery_field"]
        assert len(matched) == 1

    def test_known_core_fields_do_not_produce_warnings(self) -> None:
        """Core optional fields (``description``, ``confidence``, ``tags``) must
        not trigger warnings."""
        data = _valid_ddos_report()
        data["description"] = "A legitimate optional field"
        data["confidence"] = 90
        data["tags"] = ["test"]
        result = _validator.validate(data, strict=False)
        warning_fields = [w.field for w in result.warnings]
        for core_field in ("description", "confidence", "tags"):
            assert core_field not in warning_fields

    def test_known_category_specific_fields_do_not_produce_warnings(self) -> None:
        """Category-specific defined fields (e.g. ``destination_port`` for ddos)
        must not warn."""
        data = _valid_ddos_report()
        data["destination_port"] = 80
        result = _validator.validate(data, strict=False)
        warning_fields = [w.field for w in result.warnings]
        assert "destination_port" not in warning_fields

    def test_unknown_fields_in_strict_mode_appear_as_errors(self) -> None:
        """In strict mode, unknown fields must appear in errors, not warnings."""
        data = _valid_ddos_report()
        data["unknown_strict_field"] = "strict"
        result = _validator.validate(data, strict=True)
        error_fields = [e.field for e in result.errors]
        warning_fields = [w.field for w in result.warnings]
        assert "unknown_strict_field" in error_fields
        assert "unknown_strict_field" not in warning_fields


# ---------------------------------------------------------------------------
# TestValidResult
# ---------------------------------------------------------------------------


class TestValidResult:
    """Tests for the ``valid`` flag on :class:`~xarf.validator.ValidationResult`."""

    def test_valid_flag_true_when_no_errors(self) -> None:
        """``result.valid`` must be ``True`` when ``result.errors`` is empty."""
        result = _validator.validate(_valid_ddos_report())
        assert result.valid is True
        assert result.errors == []

    def test_valid_flag_false_when_errors_present(self) -> None:
        """``result.valid`` must be ``False`` when there are validation errors."""
        data = _valid_ddos_report()
        del data["source_identifier"]
        result = _validator.validate(data)
        assert result.valid is False
        assert len(result.errors) > 0
