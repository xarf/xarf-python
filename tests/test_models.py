"""Tests for Phase 1: Models & Type System."""

from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError as PydanticValidationError

from xarf.models import (
    AnyXARFReport,
    ContactInfo,
    CreateReportResult,
    ParseResult,
    ValidationError,
    ValidationWarning,
    XARFEvidence,
    XARFReport,
    _report_discriminator,
)
from xarf.types_connection import (
    ConnectionBaseReport,
    DdosReport,
    InfectedHostReport,
    LoginAttackReport,
    PortScanReport,
    ReconnaissanceReport,
    ScrapingReport,
    SqlInjectionReport,
    VulnerabilityScanReport,
)
from xarf.types_content import (
    BrandInfringementReport,
    CompromiseIndicator,
    ContentBaseReport,
    CsamReport,
    CsemReport,
    ExposedDataReport,
    FraudReport,
    MalwareReport,
    PhishingReport,
    RegistrantDetails,
    RemoteCompromiseReport,
    SuspiciousRegistrationReport,
    WebshellDetails,
)
from xarf.types_copyright import (
    CopyrightBaseReport,
    CopyrightCopyrightReport,
    CopyrightCyberlockerReport,
    CopyrightLinkSiteReport,
    CopyrightP2pReport,
    CopyrightUgcPlatformReport,
    CopyrightUsenetReport,
    MessageInfo,
    SwarmInfo,
)
from xarf.types_infrastructure import BotnetReport, CompromisedServerReport
from xarf.types_messaging import (
    BulkIndicators,
    BulkMessagingReport,
    MessagingBaseReport,
    SpamIndicators,
    SpamReport,
)
from xarf.types_reputation import BlocklistReport, ThreatIntelligenceReport
from xarf.types_vulnerability import (
    CveReport,
    ImpactAssessment,
    MisconfigurationReport,
    OpenServiceReport,
    VulnerabilityBaseReport,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

REPORTER = {"org": "Example Corp", "contact": "abuse@example.com", "domain": "example.com"}
SENDER = {"org": "Bad Actor LLC", "contact": "noreply@bad.example", "domain": "bad.example"}

BASE_FIELDS: dict[str, object] = {
    "xarf_version": "4.2.0",
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-01-01T12:00:00Z",
    "reporter": REPORTER,
    "sender": SENDER,
    "source_identifier": "192.0.2.1",
}


# ---------------------------------------------------------------------------
# Result dataclass tests
# ---------------------------------------------------------------------------


class TestValidationError:
    """Tests for the ValidationError dataclass."""

    def test_required_fields(self) -> None:
        """ValidationError requires field and message."""
        err = ValidationError(field="reporter.org", message="Missing required field")
        assert err.field == "reporter.org"
        assert err.message == "Missing required field"
        assert err.value is None

    def test_optional_value(self) -> None:
        """ValidationError accepts an optional value."""
        err = ValidationError(field="confidence", message="Out of range", value=150)
        assert err.value == 150


class TestValidationWarning:
    """Tests for the ValidationWarning dataclass."""

    def test_required_fields(self) -> None:
        """ValidationWarning requires field and message."""
        warn = ValidationWarning(field="evidence_source", message="Recommended field missing")
        assert warn.field == "evidence_source"
        assert warn.message == "Recommended field missing"


class TestParseResult:
    """Tests for the ParseResult dataclass."""

    def test_with_report(self) -> None:
        """ParseResult holds a report and empty error/warning lists."""
        report = SpamReport(
            **BASE_FIELDS,
            category="messaging",
            type="spam",
            protocol="smtp",
        )
        result = ParseResult(report=report, errors=[], warnings=[])
        assert result.report is report
        assert result.errors == []
        assert result.warnings == []
        assert result.info is None

    def test_without_report(self) -> None:
        """ParseResult can hold None for report on failure."""
        result = ParseResult(
            report=None,
            errors=[ValidationError(field="category", message="Missing")],
            warnings=[],
        )
        assert result.report is None
        assert len(result.errors) == 1

    def test_with_info(self) -> None:
        """ParseResult accepts optional info list of field-message dicts."""
        result = ParseResult(
            report=None,
            errors=[],
            warnings=[],
            info=[{"field": "evidence_source", "message": "RECOMMENDED: ..."}],
        )
        assert result.info is not None
        assert isinstance(result.info, list)
        assert result.info[0]["field"] == "evidence_source"


class TestCreateReportResult:
    """Tests for the CreateReportResult dataclass."""

    def test_structure(self) -> None:
        """CreateReportResult has the same structure as ParseResult."""
        result = CreateReportResult(report=None, errors=[], warnings=[])
        assert result.report is None
        assert result.info is None


# ---------------------------------------------------------------------------
# Base model tests
# ---------------------------------------------------------------------------


class TestContactInfo:
    """Tests for the ContactInfo model."""

    def test_valid(self) -> None:
        """ContactInfo accepts valid org/contact/domain."""
        ci = ContactInfo(org="ACME", contact="admin@acme.com", domain="acme.com")
        assert ci.org == "ACME"
        assert ci.contact == "admin@acme.com"
        assert ci.domain == "acme.com"

    def test_missing_field(self) -> None:
        """ContactInfo raises on missing required field."""
        with pytest.raises(PydanticValidationError):
            ContactInfo(org="ACME", contact="admin@acme.com")  # type: ignore[call-arg]


class TestXARFEvidence:
    """Tests for the XARFEvidence model."""

    def test_required_fields(self) -> None:
        """XARFEvidence requires content_type and payload."""
        ev = XARFEvidence(content_type="message/rfc822", payload="base64data==")
        assert ev.content_type == "message/rfc822"
        assert ev.payload == "base64data=="
        assert ev.description is None
        assert ev.hash is None
        assert ev.size is None

    def test_all_fields(self) -> None:
        """XARFEvidence accepts all optional fields."""
        ev = XARFEvidence(
            content_type="application/octet-stream",
            payload="abc123",
            description="Malware sample",
            hash="deadbeef",
            size=1024,
        )
        assert ev.hash == "deadbeef"
        assert ev.size == 1024


class TestXARFReport:
    """Tests for the base XARFReport model."""

    def test_required_fields(self) -> None:
        """XARFReport accepts all required base fields."""
        report = XARFReport(
            **BASE_FIELDS,
            category="messaging",
            type="spam",
        )
        assert report.xarf_version == "4.2.0"
        assert report.category == "messaging"
        assert report.type == "spam"

    def test_recommended_fields_default_none(self) -> None:
        """Recommended fields default to None."""
        report = XARFReport(**BASE_FIELDS, category="messaging", type="spam")
        assert report.evidence_source is None
        assert report.source_port is None

    def test_optional_fields_default_none(self) -> None:
        """Optional fields default to None."""
        report = XARFReport(**BASE_FIELDS, category="messaging", type="spam")
        assert report.description is None
        assert report.legacy_version is None
        assert report.evidence is None
        assert report.tags is None
        assert report.confidence is None
        assert report.internal is None

    def test_internal_field_alias(self) -> None:
        """The _internal field is aliased as 'internal' in Python."""
        report = XARFReport(
            **BASE_FIELDS,
            category="connection",
            type="ddos",
            **{"_internal": {"ticket": "INC-001"}},
        )
        assert report.internal == {"ticket": "INC-001"}

    def test_extra_fields_allowed(self) -> None:
        """Extra fields pass through via extra='allow'."""
        report = XARFReport(
            **BASE_FIELDS,
            category="messaging",
            type="spam",
            custom_field="custom_value",
        )
        assert report.model_extra is not None
        assert report.model_extra.get("custom_field") == "custom_value"

    def test_evidence_list(self) -> None:
        """XARFReport accepts a list of XARFEvidence items."""
        report = XARFReport(
            **BASE_FIELDS,
            category="messaging",
            type="spam",
            evidence=[{"content_type": "text/plain", "payload": "hello"}],
        )
        assert report.evidence is not None
        assert len(report.evidence) == 1
        assert isinstance(report.evidence[0], XARFEvidence)


# ---------------------------------------------------------------------------
# Messaging type tests
# ---------------------------------------------------------------------------


class TestSpamReport:
    """Tests for SpamReport."""

    def test_valid_minimal(self) -> None:
        """SpamReport requires category, type, and protocol."""
        report = SpamReport(
            **BASE_FIELDS,
            category="messaging",
            type="spam",
            protocol="smtp",
        )
        assert report.category == "messaging"
        assert report.type == "spam"
        assert report.protocol == "smtp"

    def test_optional_fields(self) -> None:
        """SpamReport optional fields default to None."""
        report = SpamReport(**BASE_FIELDS, category="messaging", type="spam", protocol="smtp")
        assert report.language is None
        assert report.message_id is None
        assert report.recipient_count is None
        assert report.smtp_to is None
        assert report.spam_indicators is None
        assert report.user_agent is None

    def test_spam_indicators_nested(self) -> None:
        """SpamReport accepts nested SpamIndicators."""
        report = SpamReport(
            **BASE_FIELDS,
            category="messaging",
            type="spam",
            protocol="smtp",
            spam_indicators={"suspicious_links": ["http://evil.example/"], "commercial_content": True},
        )
        assert report.spam_indicators is not None
        assert isinstance(report.spam_indicators, SpamIndicators)
        assert report.spam_indicators.commercial_content is True

    def test_wrong_type_literal_rejected(self) -> None:
        """SpamReport rejects type != 'spam'."""
        with pytest.raises(PydanticValidationError):
            SpamReport(
                **BASE_FIELDS,
                category="messaging",
                type="bulk_messaging",
                protocol="smtp",
            )


class TestBulkMessagingReport:
    """Tests for BulkMessagingReport."""

    def test_valid(self) -> None:
        """BulkMessagingReport requires recipient_count."""
        report = BulkMessagingReport(
            **BASE_FIELDS,
            category="messaging",
            type="bulk_messaging",
            protocol="smtp",
            recipient_count=5000,
        )
        assert report.recipient_count == 5000

    def test_bulk_indicators_nested(self) -> None:
        """BulkMessagingReport accepts nested BulkIndicators."""
        report = BulkMessagingReport(
            **BASE_FIELDS,
            category="messaging",
            type="bulk_messaging",
            protocol="smtp",
            recipient_count=100,
            bulk_indicators={"high_volume": True, "template_based": True},
        )
        assert report.bulk_indicators is not None
        assert isinstance(report.bulk_indicators, BulkIndicators)

    def test_missing_recipient_count(self) -> None:
        """BulkMessagingReport requires recipient_count."""
        with pytest.raises(PydanticValidationError):
            BulkMessagingReport(
                **BASE_FIELDS,
                category="messaging",
                type="bulk_messaging",
                protocol="smtp",
            )


# ---------------------------------------------------------------------------
# Connection type tests
# ---------------------------------------------------------------------------

CONNECTION_BASE: dict[str, object] = {
    **BASE_FIELDS,
    "category": "connection",
    "first_seen": "2026-01-01T00:00:00Z",
    "protocol": "tcp",
}


class TestConnectionReports:
    """Tests for connection-category report types."""

    def test_login_attack(self) -> None:
        """LoginAttackReport constructs correctly."""
        r = LoginAttackReport(**CONNECTION_BASE, type="login_attack")
        assert r.type == "login_attack"
        assert r.category == "connection"

    def test_port_scan(self) -> None:
        """PortScanReport constructs correctly."""
        r = PortScanReport(**CONNECTION_BASE, type="port_scan")
        assert r.type == "port_scan"

    def test_ddos(self) -> None:
        """DdosReport accepts optional fields."""
        r = DdosReport(
            **CONNECTION_BASE,
            type="ddos",
            peak_bps=10_000_000,
            attack_vector="udp_flood",
        )
        assert r.peak_bps == 10_000_000
        assert r.attack_vector == "udp_flood"

    def test_infected_host_requires_bot_type(self) -> None:
        """InfectedHostReport requires bot_type."""
        with pytest.raises(PydanticValidationError):
            InfectedHostReport(**CONNECTION_BASE, type="infected_host")

    def test_infected_host(self) -> None:
        """InfectedHostReport constructs with bot_type."""
        r = InfectedHostReport(**CONNECTION_BASE, type="infected_host", bot_type="mirai")
        assert r.bot_type == "mirai"

    def test_reconnaissance_requires_probed_resources(self) -> None:
        """ReconnaissanceReport requires probed_resources."""
        with pytest.raises(PydanticValidationError):
            ReconnaissanceReport(**CONNECTION_BASE, type="reconnaissance")

    def test_reconnaissance(self) -> None:
        """ReconnaissanceReport constructs with probed_resources."""
        r = ReconnaissanceReport(
            **CONNECTION_BASE,
            type="reconnaissance",
            probed_resources=["/admin", "/.env"],
        )
        assert r.probed_resources == ["/admin", "/.env"]

    def test_scraping_requires_total_requests(self) -> None:
        """ScrapingReport requires total_requests."""
        with pytest.raises(PydanticValidationError):
            ScrapingReport(**CONNECTION_BASE, type="scraping")

    def test_vulnerability_scan_requires_scan_type(self) -> None:
        """VulnerabilityScanReport requires scan_type."""
        with pytest.raises(PydanticValidationError):
            VulnerabilityScanReport(**CONNECTION_BASE, type="vulnerability_scan")


# ---------------------------------------------------------------------------
# Content type tests
# ---------------------------------------------------------------------------

CONTENT_BASE: dict[str, object] = {
    **BASE_FIELDS,
    "category": "content",
    "url": "https://evil.example/phish",
}


class TestContentReports:
    """Tests for content-category report types."""

    def test_phishing(self) -> None:
        """PhishingReport constructs correctly."""
        r = PhishingReport(**CONTENT_BASE, type="phishing")
        assert r.type == "phishing"
        assert r.url == "https://evil.example/phish"

    def test_malware(self) -> None:
        """MalwareReport accepts file_hashes dict."""
        r = MalwareReport(
            **CONTENT_BASE,
            type="malware",
            file_hashes={"sha256": "abc123"},
        )
        assert r.file_hashes == {"sha256": "abc123"}

    def test_csam_requires_classification_and_detection(self) -> None:
        """CsamReport requires classification and detection_method."""
        with pytest.raises(PydanticValidationError):
            CsamReport(**CONTENT_BASE, type="csam", classification="level_a")

    def test_csam(self) -> None:
        """CsamReport constructs with required fields."""
        r = CsamReport(
            **CONTENT_BASE,
            type="csam",
            classification="level_a",
            detection_method="hash_match",
        )
        assert r.classification == "level_a"

    def test_exposed_data_requires_data_types_and_method(self) -> None:
        """ExposedDataReport requires data_types and exposure_method."""
        with pytest.raises(PydanticValidationError):
            ExposedDataReport(**CONTENT_BASE, type="exposed_data")

    def test_brand_infringement_requires_fields(self) -> None:
        """BrandInfringementReport requires infringement_type and legitimate_site."""
        with pytest.raises(PydanticValidationError):
            BrandInfringementReport(**CONTENT_BASE, type="brand_infringement")

    def test_remote_compromise_nested_indicators(self) -> None:
        """RemoteCompromiseReport accepts nested CompromiseIndicator and WebshellDetails."""
        r = RemoteCompromiseReport(
            **CONTENT_BASE,
            type="remote_compromise",
            compromise_type="webshell",
            compromise_indicators=[{"type": "file_path", "value": "/var/www/shell.php"}],
            webshell_details={"family": "c99", "password_protected": True},
        )
        assert r.compromise_indicators is not None
        assert isinstance(r.compromise_indicators[0], CompromiseIndicator)
        assert r.webshell_details is not None
        assert isinstance(r.webshell_details, WebshellDetails)

    def test_suspicious_registration_requires_fields(self) -> None:
        """SuspiciousRegistrationReport requires registration_date and suspicious_indicators."""
        with pytest.raises(PydanticValidationError):
            SuspiciousRegistrationReport(**CONTENT_BASE, type="suspicious_registration")


# ---------------------------------------------------------------------------
# Infrastructure type tests
# ---------------------------------------------------------------------------

INFRA_BASE: dict[str, object] = {**BASE_FIELDS, "category": "infrastructure"}


class TestInfrastructureReports:
    """Tests for infrastructure-category report types."""

    def test_botnet_requires_compromise_evidence(self) -> None:
        """BotnetReport requires compromise_evidence."""
        with pytest.raises(PydanticValidationError):
            BotnetReport(**INFRA_BASE, type="botnet")

    def test_botnet(self) -> None:
        """BotnetReport constructs correctly."""
        r = BotnetReport(
            **INFRA_BASE,
            type="botnet",
            compromise_evidence="C2 traffic observed to 10.0.0.1:6667",
            malware_family="mirai",
        )
        assert r.malware_family == "mirai"

    def test_compromised_server(self) -> None:
        """CompromisedServerReport requires compromise_method."""
        r = CompromisedServerReport(
            **INFRA_BASE,
            type="compromised_server",
            compromise_method="brute_force",
        )
        assert r.compromise_method == "brute_force"


# ---------------------------------------------------------------------------
# Copyright type tests
# ---------------------------------------------------------------------------

COPYRIGHT_BASE: dict[str, object] = {**BASE_FIELDS, "category": "copyright"}


class TestCopyrightReports:
    """Tests for copyright-category report types."""

    def test_copyright_copyright_requires_infringing_url(self) -> None:
        """CopyrightCopyrightReport requires infringing_url."""
        with pytest.raises(PydanticValidationError):
            CopyrightCopyrightReport(**COPYRIGHT_BASE, type="copyright")

    def test_copyright_copyright(self) -> None:
        """CopyrightCopyrightReport constructs correctly."""
        r = CopyrightCopyrightReport(
            **COPYRIGHT_BASE,
            type="copyright",
            infringing_url="https://pirate.example/movie.mkv",
        )
        assert r.type == "copyright"
        assert r.infringing_url == "https://pirate.example/movie.mkv"

    def test_p2p_requires_swarm_info(self) -> None:
        """CopyrightP2pReport requires swarm_info."""
        with pytest.raises(PydanticValidationError):
            CopyrightP2pReport(**COPYRIGHT_BASE, type="p2p", p2p_protocol="bittorrent")

    def test_p2p(self) -> None:
        """CopyrightP2pReport constructs with nested SwarmInfo."""
        r = CopyrightP2pReport(
            **COPYRIGHT_BASE,
            type="p2p",
            p2p_protocol="bittorrent",
            swarm_info={"info_hash": "abc123def456"},
        )
        assert r.p2p_protocol == "bittorrent"
        assert isinstance(r.swarm_info, SwarmInfo)
        assert r.swarm_info.info_hash == "abc123def456"

    def test_cyberlocker_requires_fields(self) -> None:
        """CopyrightCyberlockerReport requires hosting_service and infringing_url."""
        with pytest.raises(PydanticValidationError):
            CopyrightCyberlockerReport(**COPYRIGHT_BASE, type="cyberlocker")

    def test_ugc_platform_requires_fields(self) -> None:
        """CopyrightUgcPlatformReport requires infringing_url and platform_name."""
        with pytest.raises(PydanticValidationError):
            CopyrightUgcPlatformReport(**COPYRIGHT_BASE, type="ugc_platform")

    def test_link_site_requires_fields(self) -> None:
        """CopyrightLinkSiteReport requires infringing_url and site_name."""
        with pytest.raises(PydanticValidationError):
            CopyrightLinkSiteReport(**COPYRIGHT_BASE, type="link_site")

    def test_usenet_requires_newsgroup_and_message_info(self) -> None:
        """CopyrightUsenetReport requires newsgroup and message_info."""
        with pytest.raises(PydanticValidationError):
            CopyrightUsenetReport(**COPYRIGHT_BASE, type="usenet")

    def test_usenet(self) -> None:
        """CopyrightUsenetReport constructs with nested MessageInfo."""
        r = CopyrightUsenetReport(
            **COPYRIGHT_BASE,
            type="usenet",
            newsgroup="alt.binaries.example",
            message_info={"message_id": "<abc@news.example>"},
        )
        assert isinstance(r.message_info, MessageInfo)
        assert r.message_info.message_id == "<abc@news.example>"


# ---------------------------------------------------------------------------
# Vulnerability type tests
# ---------------------------------------------------------------------------

VULN_BASE: dict[str, object] = {**BASE_FIELDS, "category": "vulnerability", "service": "openssh"}


class TestVulnerabilityReports:
    """Tests for vulnerability-category report types."""

    def test_cve_requires_cve_id_and_port(self) -> None:
        """CveReport requires cve_id and service_port."""
        with pytest.raises(PydanticValidationError):
            CveReport(**VULN_BASE, type="cve")

    def test_cve(self) -> None:
        """CveReport constructs with impact assessment."""
        r = CveReport(
            **VULN_BASE,
            type="cve",
            cve_id="CVE-2024-12345",
            service_port=22,
            cvss_score=9.8,
            impact_assessment={"confidentiality": "high", "integrity": "high", "availability": "high"},
        )
        assert r.cve_id == "CVE-2024-12345"
        assert r.service_port == 22
        assert isinstance(r.impact_assessment, ImpactAssessment)
        assert r.impact_assessment.confidentiality == "high"

    def test_open_service(self) -> None:
        """OpenServiceReport constructs with just base fields."""
        r = OpenServiceReport(**VULN_BASE, type="open_service")
        assert r.type == "open_service"
        assert r.service == "openssh"

    def test_misconfiguration(self) -> None:
        """MisconfigurationReport constructs correctly."""
        r = MisconfigurationReport(**VULN_BASE, type="misconfiguration")
        assert r.type == "misconfiguration"


# ---------------------------------------------------------------------------
# Reputation type tests
# ---------------------------------------------------------------------------

REP_BASE: dict[str, object] = {
    **BASE_FIELDS,
    "category": "reputation",
    "threat_type": "phishing",
}


class TestReputationReports:
    """Tests for reputation-category report types."""

    def test_blocklist(self) -> None:
        """BlocklistReport constructs correctly."""
        r = BlocklistReport(**REP_BASE, type="blocklist")
        assert r.type == "blocklist"
        assert r.threat_type == "phishing"

    def test_threat_intelligence(self) -> None:
        """ThreatIntelligenceReport constructs correctly."""
        r = ThreatIntelligenceReport(**REP_BASE, type="threat_intelligence")
        assert r.type == "threat_intelligence"

    def test_missing_threat_type(self) -> None:
        """Reputation reports require threat_type."""
        with pytest.raises(PydanticValidationError):
            BlocklistReport(**BASE_FIELDS, category="reputation", type="blocklist")


# ---------------------------------------------------------------------------
# AnyXARFReport discriminated union tests
# ---------------------------------------------------------------------------

_adapter: TypeAdapter[AnyXARFReport] = TypeAdapter(AnyXARFReport)


class TestAnyXARFReportDiscriminator:
    """Tests for AnyXARFReport discriminated union resolution."""

    @pytest.mark.parametrize(
        ("category", "report_type", "extra"),
        [
            ("messaging", "spam", {"protocol": "smtp"}),
            ("messaging", "bulk_messaging", {"protocol": "smtp", "recipient_count": 100}),
            ("connection", "login_attack", {"first_seen": "2026-01-01T00:00:00Z", "protocol": "tcp"}),
            ("connection", "port_scan", {"first_seen": "2026-01-01T00:00:00Z", "protocol": "tcp"}),
            ("connection", "ddos", {"first_seen": "2026-01-01T00:00:00Z", "protocol": "udp"}),
            (
                "connection",
                "infected_host",
                {"first_seen": "2026-01-01T00:00:00Z", "protocol": "tcp", "bot_type": "mirai"},
            ),
            (
                "connection",
                "reconnaissance",
                {
                    "first_seen": "2026-01-01T00:00:00Z",
                    "protocol": "tcp",
                    "probed_resources": ["/"],
                },
            ),
            (
                "connection",
                "scraping",
                {"first_seen": "2026-01-01T00:00:00Z", "protocol": "http", "total_requests": 1000},
            ),
            (
                "connection",
                "sql_injection",
                {"first_seen": "2026-01-01T00:00:00Z", "protocol": "http"},
            ),
            (
                "connection",
                "vulnerability_scan",
                {"first_seen": "2026-01-01T00:00:00Z", "protocol": "tcp", "scan_type": "port"},
            ),
            ("content", "phishing", {"url": "https://evil.example/"}),
            ("content", "malware", {"url": "https://evil.example/payload.exe"}),
            (
                "content",
                "csam",
                {
                    "url": "https://evil.example/",
                    "classification": "a",
                    "detection_method": "hash",
                },
            ),
            (
                "content",
                "csem",
                {
                    "url": "https://evil.example/",
                    "detection_method": "hash",
                    "exploitation_type": "grooming",
                },
            ),
            (
                "content",
                "exposed_data",
                {
                    "url": "https://evil.example/",
                    "data_types": ["pii"],
                    "exposure_method": "bucket",
                },
            ),
            (
                "content",
                "brand_infringement",
                {
                    "url": "https://evil.example/",
                    "infringement_type": "trademark",
                    "legitimate_site": "https://legit.example/",
                },
            ),
            (
                "content",
                "fraud",
                {"url": "https://evil.example/", "fraud_type": "investment_scam"},
            ),
            (
                "content",
                "remote_compromise",
                {"url": "https://evil.example/", "compromise_type": "webshell"},
            ),
            (
                "content",
                "suspicious_registration",
                {
                    "url": "https://evil.example/",
                    "registration_date": "2026-01-01",
                    "suspicious_indicators": ["typosquat"],
                },
            ),
            (
                "copyright",
                "copyright",
                {"infringing_url": "https://pirate.example/file"},
            ),
            (
                "copyright",
                "p2p",
                {
                    "p2p_protocol": "bittorrent",
                    "swarm_info": {"info_hash": "abc123"},
                },
            ),
            (
                "copyright",
                "cyberlocker",
                {
                    "hosting_service": "megaupload",
                    "infringing_url": "https://mega.example/file",
                },
            ),
            (
                "copyright",
                "ugc_platform",
                {
                    "infringing_url": "https://tube.example/video",
                    "platform_name": "TubeSite",
                },
            ),
            (
                "copyright",
                "link_site",
                {
                    "infringing_url": "https://links.example/page",
                    "site_name": "LinkDump",
                },
            ),
            (
                "copyright",
                "usenet",
                {
                    "newsgroup": "alt.binaries.example",
                    "message_info": {"message_id": "<abc@news.example>"},
                },
            ),
            (
                "infrastructure",
                "botnet",
                {"compromise_evidence": "C2 traffic observed"},
            ),
            (
                "infrastructure",
                "compromised_server",
                {"compromise_method": "brute_force"},
            ),
            (
                "vulnerability",
                "cve",
                {"service": "openssh", "cve_id": "CVE-2024-1234", "service_port": 22},
            ),
            ("vulnerability", "open_service", {"service": "redis"}),
            ("vulnerability", "misconfiguration", {"service": "nginx"}),
            ("reputation", "blocklist", {"threat_type": "spam"}),
            ("reputation", "threat_intelligence", {"threat_type": "malware"}),
        ],
    )
    def test_discriminator_resolves_correct_type(
        self,
        category: str,
        report_type: str,
        extra: dict[str, object],
    ) -> None:
        """AnyXARFReport discriminator resolves each of the 32 concrete types."""
        data: dict[str, object] = {
            **BASE_FIELDS,
            "category": category,
            "type": report_type,
            **extra,
        }
        report = _adapter.validate_python(data)
        assert report.category == category
        assert report.type == report_type

    def test_unknown_category_raises(self) -> None:
        """AnyXARFReport raises on unknown category/type combination."""
        data: dict[str, object] = {
            **BASE_FIELDS,
            "category": "unknown",
            "type": "spam",
        }
        with pytest.raises(PydanticValidationError):
            _adapter.validate_python(data)

    def test_unknown_type_raises(self) -> None:
        """AnyXARFReport raises on valid category but unknown type."""
        data: dict[str, object] = {
            **BASE_FIELDS,
            "category": "messaging",
            "type": "unknown_type",
            "protocol": "smtp",
        }
        with pytest.raises(PydanticValidationError):
            _adapter.validate_python(data)

    def test_extra_fields_pass_through(self) -> None:
        """AnyXARFReport passes extra fields through via extra='allow'."""
        data: dict[str, object] = {
            **BASE_FIELDS,
            "category": "messaging",
            "type": "spam",
            "protocol": "smtp",
            "custom_extension": "value",
        }
        report = _adapter.validate_python(data)
        assert report.model_extra is not None
        assert report.model_extra.get("custom_extension") == "value"


class TestReportDiscriminatorFunction:
    """Tests for the _report_discriminator helper."""

    def test_dict_input(self) -> None:
        """_report_discriminator extracts key from a dict."""
        key = _report_discriminator({"category": "messaging", "type": "spam"})
        assert key == "messaging/spam"

    def test_model_input(self) -> None:
        """_report_discriminator extracts key from a model instance."""
        report = SpamReport(**BASE_FIELDS, category="messaging", type="spam", protocol="smtp")
        key = _report_discriminator(report)
        assert key == "messaging/spam"

    def test_missing_keys_returns_none_string(self) -> None:
        """_report_discriminator returns 'None/None' for empty dict."""
        key = _report_discriminator({})
        assert key == "None/None"
