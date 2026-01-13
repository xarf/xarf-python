"""Comprehensive validation tests for all XARF categories.

All test data follows XARF v4 spec from xarf-core.json.
"""

from xarf import XARFParser

from .conftest import (
    create_v4_base_report,
    create_v4_connection_report,
    create_v4_content_report,
    create_v4_copyright_report,
    create_v4_infrastructure_report,
    create_v4_messaging_report,
    create_v4_reputation_report,
    create_v4_vulnerability_report,
)


class TestCategoryValidation:
    """Test validation for all 7 XARF v4 categories."""

    def test_messaging_category_valid(self) -> None:
        """Test valid messaging category report."""
        report_data = create_v4_messaging_report(
            report_id="test-messaging-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "messaging"
        assert report.type == "spam"

    def test_connection_category_valid(self) -> None:
        """Test valid connection category report."""
        report_data = create_v4_connection_report(
            report_id="test-connection-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "connection"
        assert report.type == "ddos"

    def test_content_category_valid(self) -> None:
        """Test valid content category report."""
        report_data = create_v4_content_report(
            report_id="test-content-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "content"
        assert report.type == "phishing"  # v4 uses 'phishing' not 'phishing_site'

    def test_infrastructure_category_valid(self) -> None:
        """Test valid infrastructure category report."""
        report_data = create_v4_infrastructure_report(
            report_id="test-infrastructure-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "infrastructure"
        assert report.type == "open_resolver"

    def test_copyright_category_valid(self) -> None:
        """Test valid copyright category report."""
        report_data = create_v4_copyright_report(
            report_id="test-copyright-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "copyright"
        assert report.type == "dmca"

    def test_vulnerability_category_valid(self) -> None:
        """Test valid vulnerability category report."""
        report_data = create_v4_vulnerability_report(
            report_id="test-vulnerability-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "vulnerability"
        assert report.type == "exposed_service"

    def test_reputation_category_valid(self) -> None:
        """Test valid reputation category report."""
        report_data = create_v4_reputation_report(
            report_id="test-reputation-001",
        )

        parser = XARFParser()
        report = parser.parse(report_data)
        assert report.category == "reputation"
        assert report.type == "blocklist"


class TestMandatoryFields:
    """Test validation of all mandatory fields per v4 spec.

    Per xarf-core.json, required fields are:
    - xarf_version, report_id, timestamp
    - reporter, sender (both contact_info with org, contact, domain)
    - source_identifier, category, type

    Note: evidence_source is RECOMMENDED but not required in v4.
    """

    def test_missing_xarf_version(self) -> None:
        """Test validation fails without xarf_version."""
        report_data = create_v4_messaging_report()
        del report_data["xarf_version"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("xarf_version" in e.field for e in result.errors)

    def test_missing_report_id(self) -> None:
        """Test validation fails without report_id."""
        report_data = create_v4_messaging_report()
        del report_data["report_id"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("report_id" in e.field for e in result.errors)

    def test_missing_timestamp(self) -> None:
        """Test validation fails without timestamp."""
        report_data = create_v4_messaging_report()
        del report_data["timestamp"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("timestamp" in e.field for e in result.errors)

    def test_missing_reporter(self) -> None:
        """Test validation fails without reporter."""
        report_data = create_v4_messaging_report()
        del report_data["reporter"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("reporter" in e.field for e in result.errors)

    def test_missing_sender(self) -> None:
        """Test validation fails without sender (required in v4)."""
        report_data = create_v4_messaging_report()
        del report_data["sender"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("sender" in e.field for e in result.errors)

    def test_missing_source_identifier(self) -> None:
        """Test validation fails without source_identifier."""
        report_data = create_v4_messaging_report()
        del report_data["source_identifier"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("source_identifier" in e.field for e in result.errors)

    def test_missing_category(self) -> None:
        """Test validation fails without category."""
        report_data = create_v4_messaging_report()
        del report_data["category"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("category" in e.field for e in result.errors)

    def test_missing_type(self) -> None:
        """Test validation fails without type."""
        report_data = create_v4_messaging_report()
        del report_data["type"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("type" in e.field for e in result.errors)

    def test_evidence_source_optional(self) -> None:
        """Test that evidence_source is optional in v4.

        Per v4 spec, evidence_source is RECOMMENDED but not required.
        """
        report_data = create_v4_messaging_report()
        # evidence_source is not in base report - should still be valid

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.category == "messaging"

    def test_invalid_xarf_version(self) -> None:
        """Test validation fails with wrong xarf_version."""
        report_data = create_v4_messaging_report()
        report_data["xarf_version"] = "3.0.0"

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("pattern" in e.message.lower() for e in result.errors)

    def test_invalid_timestamp_format(self) -> None:
        """Test validation fails with invalid timestamp."""
        report_data = create_v4_messaging_report()
        report_data["timestamp"] = "not-a-timestamp"

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("timestamp" in e.field.lower() for e in result.errors)

    def test_missing_reporter_org(self) -> None:
        """Test validation fails without reporter.org."""
        report_data = create_v4_messaging_report()
        del report_data["reporter"]["org"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("reporter" in e.field and "org" in e.field for e in result.errors)

    def test_missing_reporter_contact(self) -> None:
        """Test validation fails without reporter.contact."""
        report_data = create_v4_messaging_report()
        del report_data["reporter"]["contact"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any(
            "reporter" in e.field and "contact" in e.field for e in result.errors
        )

    def test_missing_reporter_domain(self) -> None:
        """Test validation fails without reporter.domain (required in v4).

        Note: v4 uses 'domain' not 'type' for contact_info.
        """
        report_data = create_v4_messaging_report()
        del report_data["reporter"]["domain"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("domain" in e.field for e in result.errors)

    def test_missing_sender_domain(self) -> None:
        """Test validation fails without sender.domain."""
        report_data = create_v4_messaging_report()
        del report_data["sender"]["domain"]

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("sender" in e.field and "domain" in e.field for e in result.errors)


class TestCategorySpecificValidation:
    """Test category-specific field validation."""

    def test_messaging_with_protocol(self) -> None:
        """Test messaging report with protocol field."""
        report_data = create_v4_messaging_report(
            protocol="smtp",
            smtp_from="spammer@example.com",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.protocol == "smtp"
        assert report.smtp_from == "spammer@example.com"

    def test_connection_with_destination(self) -> None:
        """Test connection report with destination fields."""
        report_data = create_v4_connection_report(
            destination_ip="203.0.113.10",
            destination_port=443,
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.destination_ip == "203.0.113.10"
        assert report.destination_port == 443

    def test_content_with_url(self) -> None:
        """Test content report with url field."""
        report_data = create_v4_content_report(
            url="https://malicious.example.com/phishing",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.url == "https://malicious.example.com/phishing"

    def test_invalid_category(self) -> None:
        """Test validation fails with invalid category."""
        report_data = create_v4_base_report(
            category="invalid_category",
            report_type="spam",
        )

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("category" in e.field.lower() for e in result.errors)

    def test_invalid_type_for_category(self) -> None:
        """Test validation fails with invalid type for category."""
        report_data = create_v4_base_report(
            category="messaging",
            report_type="invalid_type",
        )

        parser = XARFParser(strict=False)
        result = parser.validate(report_data)

        assert not result.valid
        assert any("type" in e.field.lower() for e in result.errors)


class TestOptionalFields:
    """Test optional field handling."""

    def test_with_evidence(self) -> None:
        """Test report with evidence array."""
        report_data = create_v4_messaging_report(
            evidence=[
                {
                    "content_type": "message/rfc822",
                    "payload": "SGVsbG8gV29ybGQ=",  # Base64 "Hello World"
                    "description": "Original spam email",
                }
            ],
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.evidence is not None
        assert len(report.evidence) == 1
        assert report.evidence[0].content_type == "message/rfc822"

    def test_with_tags(self) -> None:
        """Test report with tags array."""
        report_data = create_v4_messaging_report(
            tags=["malware:emotet", "campaign:winter-2024"],
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.tags is not None
        assert len(report.tags) == 2
        assert "malware:emotet" in report.tags

    def test_with_confidence(self) -> None:
        """Test report with confidence score."""
        report_data = create_v4_messaging_report(
            confidence=0.95,
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.confidence == 0.95

    def test_with_description(self) -> None:
        """Test report with description."""
        report_data = create_v4_messaging_report(
            description="Spam campaign targeting financial institutions",
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.description is not None
        assert "financial" in report.description

    def test_with_on_behalf_of(self) -> None:
        """Test report with on_behalf_of field."""
        report_data = create_v4_messaging_report(
            on_behalf_of={
                "org": "Original Reporter",
                "contact": "original@reporter.org",
                "domain": "reporter.org",
            },
        )

        parser = XARFParser()
        report = parser.parse(report_data)

        assert report.on_behalf_of is not None
        assert report.on_behalf_of.org == "Original Reporter"
