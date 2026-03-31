"""Tests for xarf.generator — Phase 5.

Covers:
- create_report(): auto-metadata, all 7 categories, typed return, strict mode
- create_evidence(): all 4 hash algorithms, bytes/str input, base64 encoding
"""

from __future__ import annotations

import base64
import hashlib
import re
import uuid
from typing import Any

import pytest

from xarf import (
    BlocklistReport,
    BotnetReport,
    ContactInfo,
    CopyrightCopyrightReport,
    CreateReportResult,
    CveReport,
    DdosReport,
    FraudReport,
    SpamReport,
    ThreatIntelligenceReport,
    XARFEvidence,
    create_evidence,
    create_report,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

REPORTER: dict[str, Any] = {
    "org": "ACME Security",
    "contact": "abuse@acme.example",
    "domain": "acme.example",
}

SENDER: dict[str, Any] = {
    "org": "Bad Actor Inc",
    "contact": "noreply@bad.example",
    "domain": "bad.example",
}


def _base_kwargs(**extra: Any) -> dict[str, Any]:
    """Return the minimum kwargs shared by every create_report() call."""
    return {
        "source_identifier": "192.0.2.1",
        "reporter": REPORTER,
        "sender": SENDER,
        **extra,
    }


def _spam_kwargs(**extra: Any) -> dict[str, Any]:
    """Return kwargs for a minimal valid messaging/spam report.

    Includes ``protocol="sms"`` to satisfy the schema-required ``protocol``
    field while avoiding the conditional ``smtp_from``/``source_port``
    requirement triggered only when ``protocol="smtp"``.
    """
    return _base_kwargs(protocol="sms", **extra)


# ---------------------------------------------------------------------------
# create_evidence() — hashing and encoding
# ---------------------------------------------------------------------------


class TestCreateEvidence:
    """Tests for the create_evidence() helper."""

    def test_returns_xarf_evidence(self) -> None:
        ev = create_evidence("text/plain", b"hello")
        assert isinstance(ev, XARFEvidence)

    def test_description_optional(self) -> None:
        ev = create_evidence("text/plain", b"x")
        assert ev.description is None

    def test_size_equals_byte_length(self) -> None:
        payload = b"Hello, XARF!"
        ev = create_evidence("text/plain", payload)
        assert ev.size == len(payload)

    def test_size_for_str_payload(self) -> None:
        # "café" is 5 UTF-8 bytes (é = 2 bytes)
        ev = create_evidence("text/plain", "café")
        assert ev.size == len("café".encode())

    def test_payload_is_base64_encoded(self) -> None:
        raw = b"test payload"
        ev = create_evidence("text/plain", raw)
        decoded = base64.b64decode(ev.payload)
        assert decoded == raw

    def test_str_payload_encodes_utf8(self) -> None:
        text = "Hello"
        ev = create_evidence("text/plain", text)
        decoded = base64.b64decode(ev.payload)
        assert decoded == text.encode("utf-8")

    @pytest.mark.parametrize(
        ("algorithm", "hasher"),
        [
            ("sha256", hashlib.sha256),
            ("sha512", hashlib.sha512),
            ("sha1", hashlib.sha1),
            ("md5", hashlib.md5),
        ],
    )
    def test_hash_algorithm_correctness(self, algorithm: str, hasher: Any) -> None:
        payload = b"test data for hashing"
        ev = create_evidence("text/plain", payload, hash_algorithm=algorithm)  # type: ignore[arg-type]
        expected_hex = hasher(payload).hexdigest()
        assert ev.hash == f"{algorithm}:{expected_hex}"

    def test_hash_default_is_sha256(self) -> None:
        payload = b"default algo"
        ev = create_evidence("text/plain", payload)
        expected = hashlib.sha256(payload).hexdigest()
        assert ev.hash == f"sha256:{expected}"

    def test_hash_format_matches_spec_pattern(self) -> None:
        """Hash must match the schema pattern: algorithm:hexvalue."""
        ev = create_evidence("text/plain", b"check")
        assert re.match(r"^(sha256|sha512|sha1|md5):[a-f0-9]+$", ev.hash)

    def test_empty_payload(self) -> None:
        ev = create_evidence("text/plain", b"")
        assert ev.size == 0
        expected = hashlib.sha256(b"").hexdigest()
        assert ev.hash == f"sha256:{expected}"


# ---------------------------------------------------------------------------
# create_report() — return type and auto-metadata
# ---------------------------------------------------------------------------


class TestCreateReportReturnType:
    """Verify that create_report() returns CreateReportResult with typed model."""

    def test_returns_create_report_result(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert isinstance(result, CreateReportResult)

    def test_report_is_spam_report(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert isinstance(result.report, SpamReport)

    def test_report_field_is_none_on_invalid_category(self) -> None:
        result = create_report(
            category="nonexistent",
            type="fake",
            **_base_kwargs(),
        )
        assert result.report is None
        assert result.errors

    def test_info_is_none_by_default(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert result.info is None

    def test_info_populated_when_show_missing_optional(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            show_missing_optional=True,
            **_spam_kwargs(),
        )
        assert isinstance(result.info, list)
        # Each entry must be a dict with "field" and "message" keys
        for entry in result.info:
            assert "field" in entry
            assert "message" in entry


class TestCreateReportAutoMetadata:
    """Verify that auto-filled metadata fields are correct."""

    def test_xarf_version_is_spec_version(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert result.report is not None
        assert result.report.xarf_version == "4.2.0"

    def test_report_id_is_valid_uuid(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert result.report is not None
        # Must not raise ValueError
        parsed = uuid.UUID(result.report.report_id)
        assert parsed.version == 4

    def test_timestamp_is_iso8601(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert result.report is not None
        # ISO 8601 with timezone offset or Z
        assert re.match(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$",
            result.report.timestamp,
        )

    def test_category_and_type_preserved(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert result.report is not None
        assert result.report.category == "messaging"
        assert result.report.type == "spam"

    def test_source_identifier_preserved(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            **_spam_kwargs(),
        )
        assert result.report is not None
        assert result.report.source_identifier == "192.0.2.1"


# ---------------------------------------------------------------------------
# create_report() — all 7 categories
# ---------------------------------------------------------------------------


class TestCreateReportAllCategories:
    """Verify that all 7 XARF categories produce valid, typed Pydantic models."""

    def test_messaging_spam(self) -> None:
        # protocol="sms" avoids the smtp_from/source_port conditional requirement
        result = create_report(
            category="messaging",
            type="spam",
            protocol="sms",
            **_base_kwargs(),
        )
        assert isinstance(result.report, SpamReport)
        assert not result.errors

    def test_connection_ddos(self) -> None:
        # source_identifier is an IP → source_port is required (min=1)
        result = create_report(
            category="connection",
            type="ddos",
            protocol="tcp",
            first_seen="2024-01-01T00:00:00+00:00",
            source_port=443,
            **_base_kwargs(),
        )
        assert isinstance(result.report, DdosReport)
        assert not result.errors

    def test_content_fraud(self) -> None:
        result = create_report(
            category="content",
            type="fraud",
            fraud_type="investment",
            url="https://fake-exchange.example.com",
            **_base_kwargs(),
        )
        assert isinstance(result.report, FraudReport)
        assert not result.errors

    def test_infrastructure_botnet(self) -> None:
        result = create_report(
            category="infrastructure",
            type="botnet",
            compromise_evidence="C2 communication observed in network logs",
            **_base_kwargs(),
        )
        assert isinstance(result.report, BotnetReport)
        assert not result.errors

    def test_copyright_copyright(self) -> None:
        result = create_report(
            category="copyright",
            type="copyright",
            infringing_url="https://pirate.example.com/file.mp4",
            **_base_kwargs(),
        )
        assert isinstance(result.report, CopyrightCopyrightReport)
        assert not result.errors

    def test_vulnerability_cve(self) -> None:
        result = create_report(
            category="vulnerability",
            type="cve",
            service="apache_httpd",
            service_port=443,
            cve_id="CVE-2024-12345",
            **_base_kwargs(),
        )
        assert isinstance(result.report, CveReport)
        assert not result.errors

    def test_reputation_blocklist(self) -> None:
        result = create_report(
            category="reputation",
            type="blocklist",
            threat_type="scanning_source",
            **_base_kwargs(),
        )
        assert isinstance(result.report, BlocklistReport)
        assert not result.errors

    def test_reputation_threat_intelligence(self) -> None:
        result = create_report(
            category="reputation",
            type="threat_intelligence",
            threat_type="malware_distribution",
            **_base_kwargs(),
        )
        assert isinstance(result.report, ThreatIntelligenceReport)
        assert not result.errors


# ---------------------------------------------------------------------------
# create_report() — ContactInfo input variant
# ---------------------------------------------------------------------------


class TestCreateReportContactInfo:
    """Verify that ContactInfo objects are accepted in place of dicts."""

    def test_contact_info_reporter(self) -> None:
        reporter = ContactInfo(
            org="Security Team",
            contact="sec@example.net",
            domain="example.net",
        )
        sender = ContactInfo(
            org="Sender Org",
            contact="s@sender.example",
            domain="sender.example",
        )
        result = create_report(
            category="messaging",
            type="spam",
            protocol="sms",
            source_identifier="10.0.0.1",
            reporter=reporter,
            sender=sender,
        )
        assert isinstance(result.report, SpamReport)
        assert not result.errors

    def test_mixed_dict_and_contact_info(self) -> None:
        reporter = ContactInfo(
            org="Reporter Org",
            contact="r@reporter.example",
            domain="reporter.example",
        )
        result = create_report(
            category="messaging",
            type="spam",
            protocol="sms",
            source_identifier="10.0.0.2",
            reporter=reporter,
            sender=SENDER,
        )
        assert not result.errors


# ---------------------------------------------------------------------------
# create_report() — evidence kwarg with XARFEvidence objects
# ---------------------------------------------------------------------------


class TestCreateReportWithEvidence:
    """Verify that XARFEvidence objects in evidence= kwarg are serialised."""

    def test_evidence_xarf_evidence_object(self) -> None:
        ev = create_evidence("text/plain", b"log line", description="Server log")
        result = create_report(
            category="messaging",
            type="spam",
            evidence=[ev],
            **_spam_kwargs(),
        )
        assert not result.errors
        assert result.report is not None
        assert result.report.evidence is not None
        assert len(result.report.evidence) == 1
        # Verify _to_jsonable serialisation round-trips the evidence correctly
        item = result.report.evidence[0]
        assert item.content_type == ev.content_type
        assert item.payload == ev.payload
        assert item.hash == ev.hash
        assert item.size == ev.size

    def test_evidence_dict(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            evidence=[{"content_type": "text/plain", "payload": "aGVsbG8="}],
            **_spam_kwargs(),
        )
        assert not result.errors


# ---------------------------------------------------------------------------
# create_report() — strict mode
# ---------------------------------------------------------------------------


class TestCreateReportStrictMode:
    """Verify strict-mode behaviour: errors → report=None."""

    def test_strict_invalid_category_returns_none(self) -> None:
        result = create_report(
            category="nonexistent",
            type="fake",
            strict=True,
            **_base_kwargs(),
        )
        assert result.report is None
        assert result.errors

    def test_strict_promotes_recommended_to_required(self) -> None:
        # Non-strict: missing recommended fields produces no errors
        result_normal = create_report(
            category="messaging",
            type="spam",
            strict=False,
            **_spam_kwargs(),
        )
        assert not result_normal.errors

        # Strict: missing recommended fields produce errors (e.g. source_port,
        # evidence, confidence, smtp_to, subject, message_id become required)
        result_strict = create_report(
            category="messaging",
            type="spam",
            strict=True,
            **_spam_kwargs(),
        )
        assert result_strict.errors

    def test_unknown_field_produces_warning_non_strict(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            completely_unknown_field_xyz="value",
            **_spam_kwargs(),
        )
        assert not result.errors
        assert any("completely_unknown_field_xyz" in w.field for w in result.warnings)

    def test_strict_unknown_field_becomes_error(self) -> None:
        result = create_report(
            category="messaging",
            type="spam",
            strict=True,
            completely_unknown_field_xyz="value",
            **_spam_kwargs(),
        )
        assert result.report is None
        assert any("completely_unknown_field_xyz" in e.field for e in result.errors)
