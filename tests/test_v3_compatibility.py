"""Tests for XARF v3 backwards compatibility."""

import json
import warnings

from xarf import XARFParser, convert_v3_to_v4, is_v3_report
from xarf.models import ConnectionReport, ContentReport, MessagingReport
from xarf.v3_compat import XARFv3DeprecationWarning


class TestV3Detection:
    """Test v3 format detection."""

    def test_detect_v3_report(self):
        """Test detection of v3 format."""
        v3_data = {
            "Version": "3.0.0",
            "ReporterInfo": {"ReporterOrg": "Test"},
            "Report": {"ReportClass": "Messaging", "ReportType": "spam"},
        }

        assert is_v3_report(v3_data) is True

    def test_detect_v4_report(self):
        """Test v4 format is not detected as v3."""
        v4_data = {
            "xarf_version": "4.0.0",
            "report_id": "test-id",
            "category": "messaging",
        }

        assert is_v3_report(v4_data) is False

    def test_detect_invalid_format(self):
        """Test detection with neither v3 nor v4 markers."""
        invalid_data = {"some_field": "value"}

        assert is_v3_report(invalid_data) is False


class TestV3Conversion:
    """Test v3 to v4 conversion."""

    def test_convert_v3_spam_report(self):
        """Test conversion of v3 spam report."""
        v3_report = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Example Anti-Spam",
                "ReporterOrgEmail": "abuse@example.com",
            },
            "Report": {
                "ReportClass": "Messaging",
                "ReportType": "spam",
                "Date": "2024-01-15T14:30:25Z",
                "Source": {"IP": "192.168.1.100", "Port": 25},
                "Attachment": [
                    {
                        "ContentType": "message/rfc822",
                        "Description": "Original spam message",
                        "Data": "VGVzdCBkYXRh",
                    }
                ],
                "AdditionalInfo": {
                    "Protocol": "smtp",
                    "SMTPFrom": "spammer@example.com",
                    "Subject": "Test Spam",
                    "DetectionMethod": "spamtrap",
                },
            },
        }

        # Suppress deprecation warning for this test
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            v4_report = convert_v3_to_v4(v3_report)

        # Verify base fields
        assert v4_report["xarf_version"] == "4.0.0"
        assert "report_id" in v4_report
        assert v4_report["timestamp"] == "2024-01-15T14:30:25Z"
        assert v4_report["category"] == "messaging"
        assert v4_report["type"] == "spam"
        assert v4_report["source_identifier"] == "192.168.1.100"
        assert v4_report["evidence_source"] == "spamtrap"

        # Verify reporter
        assert v4_report["reporter"]["org"] == "Example Anti-Spam"
        assert v4_report["reporter"]["contact"] == "abuse@example.com"
        assert v4_report["reporter"]["type"] == "automated"

        # Verify messaging-specific fields
        assert v4_report["protocol"] == "smtp"
        assert v4_report["smtp_from"] == "spammer@example.com"
        assert v4_report["subject"] == "Test Spam"

        # Verify evidence conversion
        assert len(v4_report["evidence"]) == 1
        assert v4_report["evidence"][0]["content_type"] == "message/rfc822"
        assert v4_report["evidence"][0]["payload"] == "VGVzdCBkYXRh"

        # Verify legacy markers
        assert v4_report["legacy_version"] == "3"
        assert v4_report["_internal"]["converted_from_v3"] is True

    def test_convert_v3_ddos_report(self):
        """Test conversion of v3 DDoS report."""
        v3_report = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Security Monitor",
                "ReporterContactEmail": "security@example.com",
            },
            "Report": {
                "ReportClass": "Connection",
                "ReportType": "ddos",
                "Date": "2024-01-15T11:00:00Z",
                "Source": {"IP": "203.0.113.50", "Port": 12345},
                "DestinationIp": "198.51.100.10",
                "DestinationPort": 80,
                "AdditionalInfo": {
                    "Protocol": "tcp",
                    "AttackType": "syn_flood",
                    "PacketCount": 1500000,
                    "DetectionMethod": "honeypot",
                },
            },
        }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            v4_report = convert_v3_to_v4(v3_report)

        assert v4_report["category"] == "connection"
        assert v4_report["type"] == "ddos"
        assert v4_report["destination_ip"] == "198.51.100.10"
        assert v4_report["destination_port"] == 80
        assert v4_report["protocol"] == "tcp"
        assert v4_report["attack_type"] == "syn_flood"
        assert v4_report["packet_count"] == 1500000
        assert v4_report["source_port"] == 12345

    def test_convert_v3_phishing_report(self):
        """Test conversion of v3 phishing report."""
        v3_report = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Web Security",
                "ReporterOrgEmail": "web@example.com",
            },
            "Report": {
                "ReportClass": "Content",
                "ReportType": "phishing",
                "Date": "2024-01-15T12:00:00Z",
                "Source": {"IP": "192.0.2.50"},
                "URL": "http://phishing.example.com/fake-bank",
                "AdditionalInfo": {
                    "ContentType": "text/html",
                    "DetectionMethod": "user_report",
                },
            },
        }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            v4_report = convert_v3_to_v4(v3_report)

        assert v4_report["category"] == "content"
        assert v4_report["type"] == "phishing"
        assert v4_report["url"] == "http://phishing.example.com/fake-bank"
        assert v4_report["content_type"] == "text/html"
        assert v4_report["evidence_source"] == "user_report"

    def test_deprecation_warning_emitted(self):
        """Test that deprecation warning is emitted on v3 conversion."""
        v3_report = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Test",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportClass": "Messaging",
                "ReportType": "spam",
                "Date": "2024-01-15T10:00:00Z",
                "Source": {"IP": "192.0.2.1"},
                "AdditionalInfo": {},
            },
        }

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            convert_v3_to_v4(v3_report)

            assert len(w) == 1
            assert issubclass(w[0].category, XARFv3DeprecationWarning)
            assert "v3 format is deprecated" in str(w[0].message).lower()


class TestV3ParserIntegration:
    """Test v3 compatibility in XARFParser."""

    def test_parser_auto_converts_v3_spam(self):
        """Test parser automatically converts v3 reports."""
        v3_json = json.dumps(
            {
                "Version": "3.0.0",
                "ReporterInfo": {
                    "ReporterOrg": "Spam Filter",
                    "ReporterOrgEmail": "abuse@filter.example",
                },
                "Report": {
                    "ReportClass": "Messaging",
                    "ReportType": "spam",
                    "Date": "2024-01-15T10:30:00Z",
                    "Source": {"IP": "192.0.2.100"},
                    "AdditionalInfo": {
                        "Protocol": "smtp",
                        "SMTPFrom": "spam@bad.example",
                        "Subject": "Spam Message",
                        "DetectionMethod": "spamtrap",
                    },
                },
            }
        )

        parser = XARFParser()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            report = parser.parse(v3_json)

        assert isinstance(report, MessagingReport)
        assert report.category == "messaging"
        assert report.type == "spam"
        assert report.smtp_from == "spam@bad.example"
        assert report.subject == "Spam Message"

    def test_parser_auto_converts_v3_ddos(self):
        """Test parser converts v3 DDoS reports."""
        v3_data = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Network Monitor",
                "ReporterOrgEmail": "noc@example.com",
            },
            "Report": {
                "ReportClass": "Connection",
                "ReportType": "ddos",
                "Date": "2024-01-15T11:00:00Z",
                "Source": {"IP": "203.0.113.50"},
                "DestinationIp": "198.51.100.10",
                "AdditionalInfo": {"Protocol": "tcp", "DetectionMethod": "automated"},
            },
        }

        parser = XARFParser()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            report = parser.parse(v3_data)

        assert isinstance(report, ConnectionReport)
        assert report.category == "connection"
        assert report.type == "ddos"
        assert report.destination_ip == "198.51.100.10"
        assert report.protocol == "tcp"

    def test_parser_auto_converts_v3_phishing(self):
        """Test parser converts v3 phishing reports."""
        v3_data = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Phishing Watch",
                "ReporterOrgEmail": "phishing@watch.example",
            },
            "Report": {
                "ReportClass": "Content",
                "ReportType": "phishing",
                "Date": "2024-01-15T12:00:00Z",
                "Source": {"IP": "192.0.2.200"},
                "URL": "http://fake-bank.example.com",
                "AdditionalInfo": {"DetectionMethod": "user_report"},
            },
        }

        parser = XARFParser()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            report = parser.parse(v3_data)

        assert isinstance(report, ContentReport)
        assert report.category == "content"
        assert report.type == "phishing"
        assert report.url == "http://fake-bank.example.com"

    def test_parser_validates_converted_v3_report(self):
        """Test parser validates converted v3 reports."""
        v3_data = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Test Org",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportClass": "Messaging",
                "ReportType": "spam",
                "Date": "2024-01-15T10:00:00Z",
                "Source": {"IP": "192.0.2.1"},
                "AdditionalInfo": {
                    "Protocol": "smtp",
                    "SMTPFrom": "spam@example.com",
                    "Subject": "Test",
                    "DetectionMethod": "spamtrap",
                },
            },
        }

        parser = XARFParser()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            # Should parse without validation errors
            parser.parse(v3_data)
            assert parser.get_errors() == []


class TestV3EdgeCases:
    """Test edge cases in v3 conversion."""

    def test_missing_optional_fields(self):
        """Test conversion with missing optional fields."""
        minimal_v3 = {
            "Version": "3.0.0",
            "ReporterInfo": {},
            "Report": {
                "ReportClass": "Messaging",
                "ReportType": "spam",
                "Source": {},
            },
        }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            v4_report = convert_v3_to_v4(minimal_v3)

        # Should have defaults
        assert v4_report["reporter"]["org"] == "Unknown"
        assert "example.com" in v4_report["reporter"]["contact"]
        assert v4_report["source_identifier"] == "0.0.0.0"

    def test_activity_class_mapped_to_messaging(self):
        """Test v3 'Activity' class maps to 'messaging'."""
        v3_report = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Test",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportClass": "Activity",  # Old v3 class name
                "ReportType": "spam",
                "Date": "2024-01-15T10:00:00Z",
                "Source": {"IP": "192.0.2.1"},
                "AdditionalInfo": {},
            },
        }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            v4_report = convert_v3_to_v4(v3_report)

        assert v4_report["category"] == "messaging"

    def test_legacy_tags_added(self):
        """Test legacy information is preserved in tags."""
        v3_report = {
            "Version": "3.0.0",
            "ReporterInfo": {
                "ReporterOrg": "Test",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportClass": "Messaging",
                "ReportType": "spam",
                "Date": "2024-01-15T10:00:00Z",
                "Source": {"IP": "192.0.2.1"},
                "AdditionalInfo": {},
            },
        }

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", XARFv3DeprecationWarning)
            v4_report = convert_v3_to_v4(v3_report)

        assert "legacy:category:Messaging" in v4_report["tags"]
        assert "legacy:type:spam" in v4_report["tags"]
