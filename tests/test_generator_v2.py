"""Tests for XARF Generator v4 alignment.

Tests for the updated generator that aligns with XARF v4 spec and JavaScript reference.
All test data follows XARF v4 spec from xarf-core.json.
"""

import re
import uuid

import pytest

from xarf.exceptions import XARFError
from xarf.generator import XARFGenerator
from xarf.schema_registry import schema_registry


class TestGeneratorV4Compliance:
    """Test generator produces v4-compliant reports."""

    def test_generate_report_has_required_fields(self) -> None:
        """Generated report must have all v4 required fields."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
        )

        # Per xarf-core.json required fields
        assert "xarf_version" in report
        assert "report_id" in report
        assert "timestamp" in report
        assert "reporter" in report
        assert "sender" in report
        assert "source_identifier" in report
        assert "category" in report
        assert "type" in report

    def test_generate_report_sender_required(self) -> None:
        """Sender is required in v4 - must raise error if None."""
        generator = XARFGenerator()

        # Passing None for sender should raise XARFError
        with pytest.raises(XARFError, match="sender is required"):
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender=None,  # type: ignore[arg-type]
            )

    def test_generate_report_reporter_uses_domain_not_type(self) -> None:
        """Reporter/sender use 'domain' field, not 'type' (v4 spec)."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
        )

        # v4 uses 'domain', not 'type'
        assert "domain" in report["reporter"]
        assert "type" not in report["reporter"]
        assert "domain" in report["sender"]
        assert "type" not in report["sender"]

    def test_generate_report_evidence_source_optional(self) -> None:
        """evidence_source is optional (x-recommended) in v4."""
        generator = XARFGenerator()

        # Should work without evidence_source
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
        )

        # evidence_source should not be in report if not provided
        assert "evidence_source" not in report

    def test_generate_report_with_evidence_source(self) -> None:
        """evidence_source is included when provided."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
            evidence_source="spamtrap",
        )

        assert report["evidence_source"] == "spamtrap"


class TestContactInfoValidation:
    """Test contact info validation (reporter/sender)."""

    def test_reporter_requires_org(self) -> None:
        """Reporter must have org field."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="org"):
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )

    def test_reporter_requires_contact(self) -> None:
        """Reporter must have contact field."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="contact"):
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )

    def test_reporter_requires_domain(self) -> None:
        """Reporter must have domain field."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="domain"):
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )

    def test_sender_requires_all_fields(self) -> None:
        """Sender must have org, contact, and domain fields."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="org"):
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )


class TestSchemaRegistryIntegration:
    """Test generator uses SchemaRegistry for validation."""

    def test_valid_categories_from_schema(self) -> None:
        """Generator should accept categories from schema."""
        generator = XARFGenerator()
        categories = schema_registry.get_categories()

        # Test at least one category from schema
        if "messaging" in categories:
            report = generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )
            assert report["category"] == "messaging"

    def test_invalid_category_rejected(self) -> None:
        """Generator should reject invalid categories."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="Invalid category"):
            generator.generate_report(
                category="invalid_category",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )

    def test_valid_types_from_schema(self) -> None:
        """Generator should accept types from schema for category."""
        generator = XARFGenerator()
        types = schema_registry.get_types_for_category("messaging")

        # Test at least one type from schema
        if "spam" in types:
            report = generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )
            assert report["type"] == "spam"

    def test_invalid_type_for_category_rejected(self) -> None:
        """Generator should reject invalid type for category."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="Invalid type"):
            generator.generate_report(
                category="messaging",
                report_type="ddos",  # ddos is not valid for messaging
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
            )


class TestReportIdAndTimestamp:
    """Test report_id and timestamp generation."""

    def test_report_id_is_valid_uuid(self) -> None:
        """report_id should be a valid UUID v4."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
        )

        # Should be parseable as UUID
        parsed = uuid.UUID(report["report_id"])
        assert parsed.version == 4

    def test_timestamp_is_iso8601(self) -> None:
        """timestamp should be ISO 8601 format."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
        )

        # Should match ISO 8601 pattern
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        assert re.match(iso_pattern, report["timestamp"])


class TestOptionalFields:
    """Test optional field handling."""

    def test_description_included_when_provided(self) -> None:
        """description should be included when provided."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
            description="Test spam report",
        )

        assert report["description"] == "Test spam report"

    def test_confidence_included_when_provided(self) -> None:
        """confidence should be included when provided."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
            confidence=0.95,
        )

        assert report["confidence"] == 0.95

    def test_confidence_validation(self) -> None:
        """confidence must be between 0.0 and 1.0."""
        generator = XARFGenerator()

        with pytest.raises(XARFError, match="confidence"):
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter={
                    "org": "Test Org",
                    "contact": "abuse@test.com",
                    "domain": "test.com",
                },
                sender={
                    "org": "Sender Org",
                    "contact": "sender@sender.com",
                    "domain": "sender.com",
                },
                confidence=1.5,  # Invalid
            )

    def test_tags_included_when_provided(self) -> None:
        """tags should be included when provided."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
            tags=["category:messaging", "type:spam"],
        )

        assert report["tags"] == ["category:messaging", "type:spam"]

    def test_additional_fields_merged(self) -> None:
        """additional_fields should be merged into report."""
        generator = XARFGenerator()
        report = generator.generate_report(
            category="messaging",
            report_type="spam",
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
            additional_fields={
                "smtp_from": "spammer@evil.com",
                "subject": "Buy now!",
            },
        )

        assert report["smtp_from"] == "spammer@evil.com"
        assert report["subject"] == "Buy now!"


class TestEvidenceGeneration:
    """Test evidence item generation."""

    def test_add_evidence_creates_hash(self) -> None:
        """add_evidence should create hash in correct format."""
        generator = XARFGenerator()
        evidence = generator.add_evidence(
            content_type="text/plain",
            description="Test evidence",
            payload="test data",
        )

        assert "hash" in evidence
        # v4 format: algorithm:hexvalue
        assert evidence["hash"].startswith("sha256:")

    def test_add_evidence_includes_all_fields(self) -> None:
        """add_evidence should include all required fields."""
        generator = XARFGenerator()
        evidence = generator.add_evidence(
            content_type="text/plain",
            description="Test evidence",
            payload="test data",
        )

        assert evidence["content_type"] == "text/plain"
        assert evidence["description"] == "Test evidence"
        assert evidence["payload"] == "test data"
        assert "hash" in evidence


class TestSampleReportGeneration:
    """Test sample report generation for testing."""

    def test_generate_sample_report_valid(self) -> None:
        """generate_sample_report should create valid v4 report."""
        generator = XARFGenerator()
        report = generator.generate_sample_report(
            category="messaging",
            report_type="spam",
        )

        # Should have all required fields
        assert "xarf_version" in report
        assert "report_id" in report
        assert "timestamp" in report
        assert "reporter" in report
        assert "sender" in report
        assert "source_identifier" in report
        assert "category" in report
        assert "type" in report

        # Reporter and sender should have v4 fields
        assert "domain" in report["reporter"]
        assert "domain" in report["sender"]

    def test_generate_sample_report_with_evidence(self) -> None:
        """generate_sample_report should include evidence when requested."""
        generator = XARFGenerator()
        report = generator.generate_sample_report(
            category="messaging",
            report_type="spam",
            include_evidence=True,
        )

        assert "evidence" in report
        assert len(report["evidence"]) > 0

    def test_generate_sample_report_without_evidence(self) -> None:
        """generate_sample_report should exclude evidence when not requested."""
        generator = XARFGenerator()
        report = generator.generate_sample_report(
            category="messaging",
            report_type="spam",
            include_evidence=False,
        )

        assert "evidence" not in report


class TestBackwardCompatibility:
    """Test backward compatibility with old API."""

    def test_reporter_contact_string_deprecated(self) -> None:
        """Old reporter_contact string API should still work (deprecated)."""
        generator = XARFGenerator()

        # Old API used reporter_contact as string
        # New API uses reporter dict with org, contact, domain
        # This test documents the expected behavior change
        with pytest.raises((XARFError, TypeError)):
            # Old API should fail - we require the new dict format
            generator.generate_report(
                category="messaging",
                report_type="spam",
                source_identifier="192.0.2.1",
                reporter_contact="abuse@test.com",  # type: ignore[call-arg]
                reporter_org="Test Org",  # type: ignore[call-arg]
            )


class TestAllCategories:
    """Test generator works with all categories."""

    @pytest.mark.parametrize(
        "category,report_type",
        [
            ("messaging", "spam"),
            ("connection", "ddos"),
            ("content", "phishing"),
            ("infrastructure", "botnet"),
            ("copyright", "infringement"),
            ("vulnerability", "cve"),
            ("reputation", "blocklist"),
        ],
    )
    def test_generate_report_all_categories(
        self, category: str, report_type: str
    ) -> None:
        """Generator should work with all valid category/type combinations."""
        generator = XARFGenerator()

        # Skip if category/type not in schema
        categories = schema_registry.get_categories()
        if category not in categories:
            pytest.skip(f"Category {category} not in schema")

        types = schema_registry.get_types_for_category(category)
        if report_type not in types:
            pytest.skip(f"Type {report_type} not in schema for {category}")

        report = generator.generate_report(
            category=category,
            report_type=report_type,
            source_identifier="192.0.2.1",
            reporter={
                "org": "Test Org",
                "contact": "abuse@test.com",
                "domain": "test.com",
            },
            sender={
                "org": "Sender Org",
                "contact": "sender@sender.com",
                "domain": "sender.com",
            },
        )

        assert report["category"] == category
        assert report["type"] == report_type
