"""Tests for XARF Parser.

All test data follows XARF v4 spec from xarf-core.json.
"""

import json

import pytest

from xarf import XARFParseError, XARFParser, XARFValidationError
from xarf.models import ConnectionReport, ContentReport, MessagingReport

from .conftest import (
    create_v4_base_report,
    create_v4_connection_report,
    create_v4_content_report,
    create_v4_messaging_report,
)


class TestXARFParser:
    """Test XARF Parser functionality."""

    def test_parse_valid_messaging_report(self) -> None:
        """Test parsing valid messaging report."""
        report_data = create_v4_messaging_report(
            report_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            source_identifier="192.0.2.100",
            subject="Test Spam",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert isinstance(report, MessagingReport)
        assert report.category == "messaging"
        assert report.type == "spam"
        assert report.smtp_from == "spammer@example.com"

    def test_parse_valid_connection_report(self) -> None:
        """Test parsing valid connection report."""
        report_data = create_v4_connection_report(
            report_id="b2c3d4e5-f6g7-8901-bcde-f1234567890a",
            timestamp="2024-01-15T11:00:00Z",
            source_identifier="192.0.2.200",
            destination_ip="203.0.113.10",
            attack_type="syn_flood",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert isinstance(report, ConnectionReport)
        assert report.category == "connection"
        assert report.type == "ddos"
        assert report.destination_ip == "203.0.113.10"

    def test_parse_valid_content_report(self) -> None:
        """Test parsing valid content report."""
        report_data = create_v4_content_report(
            report_id="c3d4e5f6-g7h8-9012-cdef-234567890abc",
            timestamp="2024-01-15T12:00:00Z",
            source_identifier="192.0.2.300",
            url="http://phishing.example.com",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert isinstance(report, ContentReport)
        assert report.category == "content"
        assert report.type == "phishing"  # v4 uses 'phishing' not 'phishing_site'
        assert report.url == "http://phishing.example.com"

    def test_parse_json_string(self) -> None:
        """Test parsing from JSON string."""
        report_data = create_v4_messaging_report()

        parser = XARFParser()
        report = parser.parse(json.dumps(report_data))

        assert report.category == "messaging"
        assert report.type == "spam"

    def test_validation_errors(self) -> None:
        """Test validation error collection."""
        # Create valid report then break the version
        invalid_data = create_v4_messaging_report()
        invalid_data["xarf_version"] = "3.0.0"  # Wrong version

        parser = XARFParser(strict=False)
        result = parser.validate(invalid_data)

        assert not result.valid
        assert len(result.errors) > 0
        # Check for version-related error
        assert any("pattern" in e.message.lower() for e in result.errors)

    def test_strict_mode_validation_error(self) -> None:
        """Test strict mode raises validation errors."""
        invalid_data = {
            "xarf_version": "4.0.0",
            # Missing required fields
        }

        parser = XARFParser(strict=True)

        with pytest.raises(XARFValidationError):
            parser.parse(invalid_data)

    def test_invalid_json_error(self) -> None:
        """Test invalid JSON handling."""
        parser = XARFParser()

        with pytest.raises(XARFParseError):
            parser.parse("{invalid json}")

    def test_unsupported_category(self) -> None:
        """Test unsupported category handling."""
        report_data = create_v4_base_report(
            category="unknown_category",
            report_type="unknown_type",
        )

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("category" in e.message.lower() for e in result.errors)

    def test_missing_required_fields(self) -> None:
        """Test missing required field validation."""
        invalid_data = {
            "xarf_version": "4.0.0",
            # Missing most required fields
        }

        parser = XARFParser(strict=False)
        result = parser.validate(invalid_data)

        assert not result.valid
        assert len(result.errors) > 0

    def test_invalid_reporter_missing_domain(self) -> None:
        """Test invalid reporter (missing domain) validation.

        Per v4 spec, reporter requires: org, contact, domain.
        """
        report_data = create_v4_messaging_report()
        # Remove domain from reporter (required in v4)
        del report_data["reporter"]["domain"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("domain" in e.field.lower() for e in result.errors)

    def test_missing_sender(self) -> None:
        """Test missing sender field validation.

        Per v4 spec, sender is required.
        """
        report_data = create_v4_messaging_report()
        del report_data["sender"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("sender" in e.field.lower() for e in result.errors)

    def test_evidence_source_optional(self) -> None:
        """Test that evidence_source is optional in v4.

        Per v4 spec, evidence_source is recommended but not required.
        """
        report_data = create_v4_messaging_report()
        # evidence_source is not in the base report, which is fine

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.category == "messaging"
        # Should parse successfully without evidence_source

    def test_parse_with_evidence_source(self) -> None:
        """Test parsing report with evidence_source."""
        report_data = create_v4_messaging_report(
            evidence_source="spamtrap",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.evidence_source == "spamtrap"

    def test_infrastructure_category(self) -> None:
        """Test infrastructure category parsing."""
        report_data = create_v4_base_report(
            category="infrastructure",
            report_type="open_resolver",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.category == "infrastructure"
        assert report.type == "open_resolver"

    def test_vulnerability_category(self) -> None:
        """Test vulnerability category parsing."""
        report_data = create_v4_base_report(
            category="vulnerability",
            report_type="exposed_service",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.category == "vulnerability"
        assert report.type == "exposed_service"

    def test_reputation_category(self) -> None:
        """Test reputation category parsing."""
        report_data = create_v4_base_report(
            category="reputation",
            report_type="blocklist",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.category == "reputation"
        assert report.type == "blocklist"

    def test_copyright_category(self) -> None:
        """Test copyright category parsing."""
        report_data = create_v4_base_report(
            category="copyright",
            report_type="dmca",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.category == "copyright"
        assert report.type == "dmca"
