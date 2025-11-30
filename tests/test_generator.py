"""Tests for XARF Report Generator."""

import uuid
from datetime import datetime, timezone

from xarf.models import ContactInfo, MessagingReport


class TestReportGeneration:
    """Test report generation and helper functions."""

    def test_create_messaging_report(self):
        """Test creating a messaging report programmatically."""
        reporter = ContactInfo(
            org="Test Organization", contact="abuse@test.com", domain="test.com"
        )
        sender = ContactInfo(
            org="Test Organization", contact="abuse@test.com", domain="test.com"
        )

        report = MessagingReport(
            xarf_version="4.0.0",
            report_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            reporter=reporter,
            sender=sender,
            source_identifier="192.0.2.1",
            category="messaging",
            type="spam",
            evidence_source="spamtrap",
            protocol="smtp",
            smtp_from="spammer@example.com",
            subject="Spam Message",
        )

        assert report.category == "messaging"
        assert report.type == "spam"
        assert report.smtp_from == "spammer@example.com"
