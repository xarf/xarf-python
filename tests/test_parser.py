"""Tests for XARF Parser."""

import json

import pytest

from xarf import XARFParseError, XARFParser, XARFValidationError
from xarf.models import ConnectionReport, ContentReport, MessagingReport


class TestXARFParser:
    """Test XARF Parser functionality."""

    def test_parse_valid_messaging_report(self):
        """Test parsing valid messaging report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test Org",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Test Org",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.100",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
            "protocol": "smtp",
            "smtp_from": "spammer@example.com",
            "subject": "Test Spam",
        }

        parser = XARFParser()
        report = parser.parse(report_data)

        assert isinstance(report, MessagingReport)
        assert report.category == "messaging"
        assert report.type == "spam"
        assert report.smtp_from == "spammer@example.com"

    def test_parse_valid_connection_report(self):
        """Test parsing valid connection report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "b2c3d4e5-f6g7-8901-bcde-f1234567890a",
            "timestamp": "2024-01-15T11:00:00Z",
            "reporter": {
                "org": "Security Monitor",
                "contact": "security@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Security Monitor",
                "contact": "security@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.200",
            "category": "connection",
            "type": "ddos",
            "evidence_source": "honeypot",
            "destination_ip": "203.0.113.10",
            "protocol": "tcp",
            "destination_port": 80,
            "attack_type": "syn_flood",
        }

        parser = XARFParser()
        report = parser.parse(report_data)

        assert isinstance(report, ConnectionReport)
        assert report.category == "connection"
        assert report.type == "ddos"
        assert report.destination_ip == "203.0.113.10"

    def test_parse_valid_content_report(self):
        """Test parsing valid content report."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "c3d4e5f6-g7h8-9012-cdef-234567890abc",
            "timestamp": "2024-01-15T12:00:00Z",
            "reporter": {
                "org": "Web Security",
                "contact": "web@example.com",
                "domain": "example.com",
            },
            "sender": {
                "org": "Web Security",
                "contact": "web@example.com",
                "domain": "example.com",
            },
            "source_identifier": "192.0.2.300",
            "category": "content",
            "type": "phishing_site",
            "evidence_source": "user_report",
            "url": "http://phishing.example.com",
        }

        parser = XARFParser()
        report = parser.parse(report_data)

        assert isinstance(report, ContentReport)
        assert report.category == "content"
        assert report.type == "phishing_site"
        assert report.url == "http://phishing.example.com"

    def test_parse_json_string(self):
        """Test parsing from JSON string."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
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
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

        parser = XARFParser()
        report = parser.parse(json.dumps(report_data))

        assert report.category == "messaging"
        assert report.type == "spam"

    def test_validation_errors(self):
        """Test validation error collection."""
        invalid_data = {
            "xarf_version": "3.0.0",  # Wrong version
            "report_id": "test-id",
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
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

        parser = XARFParser(strict=False)
        result = parser.validate(invalid_data)

        assert result is False
        errors = parser.get_errors()
        assert len(errors) > 0
        assert "Unsupported XARF version" in errors[0]

    def test_strict_mode_validation_error(self):
        """Test strict mode raises validation errors."""
        invalid_data = {
            "xarf_version": "4.0.0",
            # Missing required fields
        }

        parser = XARFParser(strict=True)

        with pytest.raises(XARFValidationError):
            parser.parse(invalid_data)

    def test_invalid_json_error(self):
        """Test invalid JSON handling."""
        parser = XARFParser()

        with pytest.raises(XARFParseError):
            parser.parse("{invalid json}")

    def test_unsupported_category_alpha(self):
        """Test unsupported category in alpha version."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
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
            "category": "vulnerability",  # Not supported in alpha
            "type": "cve",
            "evidence_source": "vulnerability_scan",
        }

        parser = XARFParser(strict=False)
        report = parser.parse(report_data)

        # Should fall back to base model
        assert report.category == "vulnerability"
        errors = parser.get_errors()
        assert len(errors) == 1
        assert "Unsupported category" in errors[0]

    def test_missing_required_fields(self):
        """Test missing required field validation."""
        invalid_data = {
            "xarf_version": "4.0.0",
            # Missing most required fields
        }

        parser = XARFParser(strict=False)
        result = parser.validate(invalid_data)

        assert result is False
        errors = parser.get_errors()
        assert any("Missing required fields" in error for error in errors)

    def test_missing_sender(self):
        """Test validation fails without sender field."""
        invalid_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Test",
                "contact": "test@example.com",
                "domain": "example.com",
            },
            # Missing sender
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

        parser = XARFParser(strict=False)
        result = parser.validate(invalid_data)

        assert result is False
        errors = parser.get_errors()
        assert any("sender" in error.lower() for error in errors)

    def test_reporter_sender_same_org(self):
        """Test report where reporter and sender are the same."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-same-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Same Org",
                "contact": "abuse@same.com",
                "domain": "same.com",
            },
            "sender": {
                "org": "Same Org",
                "contact": "abuse@same.com",
                "domain": "same.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.reporter.org == "Same Org"
        assert report.sender.org == "Same Org"
        assert report.reporter.org == report.sender.org

    def test_reporter_sender_different_orgs(self):
        """Test report where reporter and sender are different organizations."""
        report_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-diff-org",
            "timestamp": "2024-01-15T10:30:00Z",
            "reporter": {
                "org": "Reporter Org",
                "contact": "abuse@reporter.com",
                "domain": "reporter.com",
            },
            "sender": {
                "org": "Sender Org",
                "contact": "abuse@sender.com",
                "domain": "sender.com",
            },
            "source_identifier": "192.0.2.1",
            "category": "messaging",
            "type": "spam",
            "evidence_source": "spamtrap",
        }

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.reporter.org == "Reporter Org"
        assert report.sender.org == "Sender Org"
        assert report.reporter.org != report.sender.org
