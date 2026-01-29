"""Tests for XARF Report Generator (if implemented).

All test data follows XARF v4 spec from xarf-core.json.
"""

import uuid
from datetime import datetime, timezone

from xarf.models import ContactInfo, MessagingReport


class TestReportGeneration:
    """Test report generation and helper functions."""

    def test_create_messaging_report(self) -> None:
        """Test creating a messaging report programmatically.

        Per v4 spec:
        - ContactInfo uses 'domain' not 'type'
        - sender is required
        - evidence_source is optional
        """
        reporter = ContactInfo(
            org="Test Organization",
            contact="abuse@test.com",
            domain="test.com",
        )

        sender = ContactInfo(
            org="Sender Organization",
            contact="sender@sender.com",
            domain="sender.com",
        )

        report = MessagingReport(
            xarf_version="4.0.0",
            report_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            reporter=reporter,
            sender=sender,
            source_identifier="192.0.2.1",
            source_port=25,
            category="messaging",
            type="spam",
            protocol="smtp",
            smtp_from="spammer@example.com",
            subject="Spam Message",
        )

        assert report.category == "messaging"
        assert report.type == "spam"
        assert report.smtp_from == "spammer@example.com"
        assert report.sender.org == "Sender Organization"
