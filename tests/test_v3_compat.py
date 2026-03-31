"""Tests for XARF v3 backwards compatibility.

Mirrors ``v3-legacy.test.ts`` in ``xarf-javascript/tests/``.
"""

from __future__ import annotations

import base64
import hashlib
import warnings as warnings_module
from typing import Any

import pytest

from xarf import parse
from xarf.exceptions import XARFParseError
from xarf.v3_compat import (
    XARFv3DeprecationWarning,
    convert_v3_to_v4,
    get_v3_deprecation_warning,
    is_v3_report,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spam_v3(
    *,
    version: str = "3",
    reporter_org: str | None = "Test Org",
    reporter_email: str = "abuse@example.com",
    source_ip: str = "192.0.2.1",
    protocol: str | None = "smtp",
) -> dict[str, Any]:
    """Build a minimal v3 spam report for testing."""
    reporter: dict[str, Any] = {"ReporterOrgEmail": reporter_email}
    if reporter_org is not None:
        reporter["ReporterOrg"] = reporter_org
    report: dict[str, Any] = {
        "ReportType": "Spam",
        "Date": "2024-01-15T10:00:00Z",
        "SourceIp": source_ip,
    }
    if protocol is not None:
        report["Protocol"] = protocol
    return {"Version": version, "ReporterInfo": reporter, "Report": report}


# ===========================================================================
# is_v3_report — detection
# ===========================================================================


class TestIsV3Report:
    def test_detects_version_3(self) -> None:
        assert is_v3_report(
            {
                "Version": "3",
                "ReporterInfo": {"ReporterOrgEmail": "t@example.com"},
                "Report": {"ReportType": "Spam", "Date": "2024-01-15T10:00:00Z"},
            }
        )

    def test_detects_version_3_0(self) -> None:
        assert is_v3_report(
            {
                "Version": "3.0",
                "ReporterInfo": {"ReporterOrgEmail": "t@example.com"},
                "Report": {"ReportType": "DDoS", "Date": "2024-01-15T10:00:00Z"},
            }
        )

    def test_detects_version_3_0_0(self) -> None:
        assert is_v3_report(
            {
                "Version": "3.0.0",
                "ReporterInfo": {"ReporterOrgEmail": "t@example.com"},
                "Report": {"ReportType": "Spam", "Date": "2024-01-15T10:00:00Z"},
            }
        )

    def test_does_not_detect_v4_as_v3(self) -> None:
        assert not is_v3_report(
            {
                "xarf_version": "4.2.0",
                "report_id": "abc",
                "timestamp": "2024-01-15T10:00:00Z",
                "category": "messaging",
                "type": "spam",
            }
        )

    def test_does_not_detect_empty_dict(self) -> None:
        assert not is_v3_report({})

    def test_does_not_detect_version_4(self) -> None:
        assert not is_v3_report({"Version": "4.0.0"})

    def test_does_not_detect_v3_without_report_key(self) -> None:
        # Version "3" but missing the "Report" key
        assert not is_v3_report(
            {
                "Version": "3",
                "ReporterInfo": {"ReporterOrgEmail": "t@example.com"},
            }
        )

    def test_does_not_detect_v3_without_reporter_info(self) -> None:
        assert not is_v3_report(
            {
                "Version": "3",
                "Report": {"ReportType": "Spam"},
            }
        )


# ===========================================================================
# convert_v3_to_v4 — spam
# ===========================================================================


class TestSpamConversion:
    def test_converts_full_spam_report(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Anti-Spam Service",
                "ReporterOrgEmail": "abuse@antispam.example",
            },
            "Report": {
                "ReportType": "Spam",
                "Date": "2024-01-15T14:30:25Z",
                "SourceIp": "192.168.1.100",
                "Protocol": "smtp",
                "SmtpMailFromAddress": "spammer@evil.example",
                "SmtpMessageSubject": "Buy now!",
                "AttackDescription": "Spam email detected",
            },
        }

        msgs: list[str] = []
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3, conversion_warnings=msgs)

        assert v4["xarf_version"] == "4.2.0"
        assert v4["category"] == "messaging"
        assert v4["type"] == "spam"
        assert v4["source_identifier"] == "192.168.1.100"
        assert v4["reporter"]["org"] == "Anti-Spam Service"
        assert v4["reporter"]["contact"] == "abuse@antispam.example"
        assert v4["reporter"]["domain"] == "antispam.example"
        assert v4["sender"]["org"] == "Anti-Spam Service"
        assert v4["sender"]["contact"] == "abuse@antispam.example"
        assert v4["sender"]["domain"] == "antispam.example"
        assert v4["timestamp"] == "2024-01-15T14:30:25Z"
        assert v4["description"] == "Spam email detected"
        assert v4["legacy_version"] == "3"
        assert v4["_internal"]["original_report_type"] == "Spam"
        assert "converted_at" in v4["_internal"]
        # Category-specific
        assert v4["protocol"] == "smtp"
        assert v4["smtp_from"] == "spammer@evil.example"
        assert v4["subject"] == "Buy now!"

    def test_converts_lowercase_spam_type(self) -> None:
        v3 = _spam_v3()
        v3["Report"]["ReportType"] = "spam"
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "messaging"
        assert v4["type"] == "spam"

    def test_source_from_source_ip_and_port(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "abuse@example.com"},
            "Report": {
                "ReportType": "spam",
                "Date": "2024-01-15T10:00:00Z",
                "Protocol": "smtp",
                "Source": {"IP": "10.0.0.1", "Port": 25},
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["source_identifier"] == "10.0.0.1"
        assert v4["source_port"] == 25

    def test_smtp_from_from_additional_info(self) -> None:
        v3 = _spam_v3()
        v3["Report"]["AdditionalInfo"] = {"SMTPFrom": "from@example.com"}
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["smtp_from"] == "from@example.com"

    def test_no_description_field_when_absent(self) -> None:
        v3 = _spam_v3()
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert "description" not in v4


# ===========================================================================
# convert_v3_to_v4 — connection types
# ===========================================================================


class TestConnectionConversion:
    def _ddos(self, **extra: Any) -> dict[str, Any]:
        report: dict[str, Any] = {
            "ReportType": "DDoS",
            "Date": "2024-01-15T15:00:00Z",
            "SourceIp": "203.0.113.50",
            "Protocol": "tcp",
        }
        report.update(extra)
        return {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "DDoS Protection",
                "ReporterOrgEmail": "ddos@example.com",
            },
            "Report": report,
        }

    def test_converts_ddos_full(self) -> None:
        v3 = self._ddos(
            DestinationIp="198.51.100.10", DestinationPort=80, AttackCount=10000
        )
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "connection"
        assert v4["type"] == "ddos"
        assert v4["source_identifier"] == "203.0.113.50"
        assert v4["destination_ip"] == "198.51.100.10"
        assert v4["destination_port"] == 80
        assert v4["protocol"] == "tcp"
        assert v4["attack_count"] == 10000
        assert v4["first_seen"] == "2024-01-15T15:00:00Z"

    def test_ddos_absent_optional_fields_not_in_result(self) -> None:
        v3 = self._ddos()  # no DestinationIp, DestinationPort, AttackCount
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert "destination_ip" not in v4
        assert "destination_port" not in v4
        assert "attack_count" not in v4

    def test_converts_login_attack(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "security@example.com"},
            "Report": {
                "ReportType": "Login-Attack",
                "Date": "2024-01-15T12:00:00Z",
                "SourceIp": "192.0.2.50",
                "DestinationIp": "203.0.113.10",
                "DestinationPort": 22,
                "Protocol": "tcp",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "connection"
        assert v4["type"] == "login_attack"

    def test_converts_port_scan(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "security@example.com"},
            "Report": {
                "ReportType": "Port-Scan",
                "Date": "2024-01-15T12:00:00Z",
                "SourceIp": "192.0.2.99",
                "Protocol": "tcp",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "connection"
        assert v4["type"] == "port_scan"

    def test_converts_lowercase_ddos(self) -> None:
        v3 = self._ddos()
        v3["Report"]["ReportType"] = "ddos"
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["type"] == "ddos"


# ===========================================================================
# convert_v3_to_v4 — content types
# ===========================================================================


class TestContentConversion:
    def test_converts_phishing(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "phishing@example.com"},
            "Report": {
                "ReportType": "Phishing",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.100",
                "Url": "http://evil-phishing.example",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "content"
        assert v4["type"] == "phishing"
        assert v4["url"] == "http://evil-phishing.example"

    def test_converts_malware(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "malware@example.com"},
            "Report": {
                "ReportType": "Malware",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.150",
                "Url": "http://malware-site.example",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "content"
        assert v4["type"] == "malware"

    def test_url_from_additional_info(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "test@example.com"},
            "Report": {
                "ReportType": "Phishing",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
                "AdditionalInfo": {"URL": "http://phish.example/login"},
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["url"] == "http://phish.example/login"

    def test_url_from_source_url(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Security Vendor",
                "ReporterOrgEmail": "abuse@security.example",
            },
            "Report": {
                "ReportType": "Phishing",
                "Date": "2024-01-15T10:00:00Z",
                "Source": {"URL": "https://malicious-example.net/banking-login/"},
                "Url": "https://malicious-example.net/banking-login/",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["url"] == "https://malicious-example.net/banking-login/"


# ===========================================================================
# convert_v3_to_v4 — other categories
# ===========================================================================


class TestOtherCategoryConversion:
    def test_converts_botnet(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "botnet@example.com"},
            "Report": {
                "ReportType": "Botnet",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.200",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "infrastructure"
        assert v4["type"] == "botnet"

    def test_converts_copyright(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "dmca@example.com"},
            "Report": {
                "ReportType": "Copyright",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.250",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["category"] == "copyright"
        assert v4["type"] == "copyright"


# ===========================================================================
# convert_v3_to_v4 — evidence conversion
# ===========================================================================


class TestEvidenceConversion:
    def test_converts_attachment_with_description(self) -> None:
        payload = "SGVsbG8gV29ybGQ="  # base64("Hello World")
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "test@example.com"},
            "Report": {
                "ReportType": "Spam",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
                "Protocol": "smtp",
                "Attachment": [
                    {
                        "ContentType": "message/rfc822",
                        "Data": payload,
                        "Description": "Original email",
                    }
                ],
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)

        assert v4.get("evidence") is not None
        ev = v4["evidence"][0]
        assert ev["content_type"] == "message/rfc822"
        assert ev["payload"] == payload
        assert ev["description"] == "Original email"
        raw = base64.b64decode(payload)
        assert ev["size"] == len(raw)
        expected_hash = "sha256:" + hashlib.sha256(raw).hexdigest()
        assert ev["hash"] == expected_hash

    def test_converts_samples_without_description(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "test@example.com"},
            "Report": {
                "ReportType": "Malware",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
                "Url": "http://malware.example/payload",
                "Samples": [
                    {
                        "ContentType": "application/octet-stream",
                        "Data": "bWFsd2FyZWRhdGE=",
                    }
                ],
            },
        }
        msgs: list[str] = []
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3, conversion_warnings=msgs)

        ev = v4["evidence"][0]
        assert ev["content_type"] == "application/octet-stream"
        assert "description" not in ev
        assert any("no description" in m for m in msgs)


# ===========================================================================
# Error cases
# ===========================================================================


class TestUnknownType:
    def test_raises_on_unknown_report_type(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "test@example.com"},
            "Report": {
                "ReportType": "UnknownType",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(
                XARFParseError, match="unknown ReportType 'UnknownType'"
            ):
                convert_v3_to_v4(v3)


class TestReporterEmailHandling:
    def test_raises_when_both_emails_absent(self) -> None:
        v3 = {
            "Version": "3",
            "ReporterInfo": {},
            "Report": {
                "ReportType": "Spam",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(XARFParseError, match="missing reporter email"):
                convert_v3_to_v4(v3)

    def test_raises_when_email_has_no_domain(self) -> None:
        v3 = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "not-an-email"},
            "Report": {
                "ReportType": "Spam",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(XARFParseError, match="not a valid email address"):
                convert_v3_to_v4(v3)

    def test_warns_when_reporter_org_missing(self) -> None:
        v3 = _spam_v3(reporter_org=None)
        msgs: list[str] = []
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3, conversion_warnings=msgs)
        assert any("No ReporterOrg found" in m for m in msgs)
        assert v4["reporter"]["org"] == "Unknown Organization"


class TestSourceIdentifierHandling:
    def test_raises_when_no_source_identifier(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Test Org",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {"ReportType": "Botnet", "Date": "2024-01-15T10:00:00Z"},
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(XARFParseError, match="no source identifier found"):
                convert_v3_to_v4(v3)

    def test_extracts_from_source_url(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Security Vendor",
                "ReporterOrgEmail": "abuse@security.example",
            },
            "Report": {
                "ReportType": "Phishing",
                "Date": "2024-01-15T10:00:00Z",
                "Source": {"URL": "https://malicious-example.net/banking-login/"},
                "Url": "https://malicious-example.net/banking-login/",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["source_identifier"] == "https://malicious-example.net/banking-login/"

    def test_extracts_from_url_field(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Test Org",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportType": "Malware",
                "Date": "2024-01-15T10:00:00Z",
                "Url": "http://malware.example/payload.exe",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["source_identifier"] == "http://malware.example/payload.exe"


class TestMissingProtocol:
    def test_raises_when_messaging_protocol_missing(self) -> None:
        v3 = _spam_v3(protocol=None)
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(
                XARFParseError, match="missing protocol for messaging type"
            ):
                convert_v3_to_v4(v3)

    def test_raises_when_connection_protocol_missing(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Test Org",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportType": "DDoS",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.1",
                # No Protocol
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(
                XARFParseError, match="missing protocol for connection type"
            ):
                convert_v3_to_v4(v3)


class TestMissingUrl:
    def test_raises_when_content_url_missing(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Test Org",
                "ReporterOrgEmail": "test@example.com",
            },
            "Report": {
                "ReportType": "Phishing",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.100",
                # No Url / Source.URL / AdditionalInfo.URL
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            with pytest.raises(XARFParseError, match="missing URL for content type"):
                convert_v3_to_v4(v3)


# ===========================================================================
# evidence_source — pass-through only when present
# ===========================================================================


class TestEvidenceSource:
    def test_evidence_source_set_when_detection_method_present(self) -> None:
        v3 = _spam_v3()
        v3["Report"]["AdditionalInfo"] = {
            "DetectionMethod": "spamtrap",
            "Protocol": "smtp",
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert v4["evidence_source"] == "spamtrap"

    def test_evidence_source_absent_when_no_detection_method(self) -> None:
        v3 = _spam_v3()
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            v4 = convert_v3_to_v4(v3)
        assert "evidence_source" not in v4


# ===========================================================================
# Deprecation warning emission
# ===========================================================================


class TestDeprecationWarningEmission:
    def test_emits_deprecation_warning_on_convert(self) -> None:
        v3 = _spam_v3()
        with warnings_module.catch_warnings(record=True) as caught:
            warnings_module.simplefilter("always")
            convert_v3_to_v4(v3)
        dep_warnings = [
            w for w in caught if issubclass(w.category, XARFv3DeprecationWarning)
        ]
        assert len(dep_warnings) == 1

    def test_deprecation_warning_is_subclass_of_deprecation_warning(self) -> None:
        assert issubclass(XARFv3DeprecationWarning, DeprecationWarning)


# ===========================================================================
# get_v3_deprecation_warning message content
# ===========================================================================


class TestGetV3DeprecationWarning:
    def test_message_contains_expected_phrases(self) -> None:
        msg = get_v3_deprecation_warning()
        assert "DEPRECATION WARNING" in msg
        assert "v3 format" in msg
        assert "converted to v4" in msg
        assert "future major version" in msg


# ===========================================================================
# parse() integration — v3 auto-detection
# ===========================================================================


class TestParserV3Integration:
    def test_parses_v3_spam_report_automatically(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {
                "ReporterOrg": "Test Security",
                "ReporterOrgEmail": "abuse@test.example",
            },
            "Report": {
                "ReportType": "Spam",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.100",
                "Protocol": "smtp",
                "SmtpMailFromAddress": "spammer@evil.example",
                "SmtpMessageSubject": "Spam subject",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            result = parse(v3)

        assert result.report is not None
        assert result.report.xarf_version == "4.2.0"
        assert result.report.category == "messaging"
        assert result.report.type == "spam"
        assert result.report.legacy_version == "3"
        assert len(result.warnings) > 0
        assert any("DEPRECATION WARNING" in w.message for w in result.warnings)

    def test_parses_v3_ddos_with_no_errors(self) -> None:
        v3: dict[str, Any] = {
            "Version": "3",
            "ReporterInfo": {"ReporterOrgEmail": "abuse@example.com"},
            "Report": {
                "ReportType": "DDoS",
                "Date": "2024-01-15T10:00:00Z",
                "SourceIp": "192.0.2.50",
                "SourcePort": 54321,
                "DestinationIp": "203.0.113.10",
                "Protocol": "tcp",
            },
        }
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            result = parse(v3)

        assert result.errors == []
        assert len(result.warnings) > 0

    def test_parse_v3_warnings_mention_v3_format(self) -> None:
        v3 = _spam_v3()
        with warnings_module.catch_warnings():
            warnings_module.simplefilter("ignore", XARFv3DeprecationWarning)
            result = parse(v3)
        assert any("v3" in w.message.lower() for w in result.warnings)
