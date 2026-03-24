"""XARF v4 base models, result types, and report union.

This module defines the foundational Pydantic models (ContactInfo, XARFEvidence,
XARFReport), result dataclasses (ParseResult, CreateReportResult), and the
AnyXARFReport discriminated union used throughout the library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Discriminator, Field, Tag

# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class ValidationError:
    """A single validation error found during parsing or report creation.

    Attributes:
        field: The field path where the error occurred (e.g. ``"reporter.org"``).
        message: Human-readable description of the error.
        value: The offending value, if available.
    """

    field: str
    message: str
    value: object = None


@dataclass
class ValidationWarning:
    """A non-fatal warning produced during validation.

    Attributes:
        field: The field path where the warning applies.
        message: Human-readable description of the warning.
    """

    field: str
    message: str


@dataclass
class ParseResult:
    """Result returned by :func:`xarf.parse`.

    Attributes:
        report: The parsed report, or ``None`` if parsing failed entirely.
        errors: List of validation errors encountered.
        warnings: List of non-fatal warnings.
        info: Optional metadata dict (populated when ``show_missing_optional=True``).
    """

    report: AnyXARFReport | None
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    info: dict[str, object] | None = None


@dataclass
class CreateReportResult:
    """Result returned by :func:`xarf.create_report`.

    Attributes:
        report: The created report, or ``None`` if creation failed.
        errors: List of validation errors encountered.
        warnings: List of non-fatal warnings.
        info: Optional metadata dict.
    """

    report: AnyXARFReport | None
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    info: dict[str, object] | None = None


# ---------------------------------------------------------------------------
# Base Pydantic models
# ---------------------------------------------------------------------------


class ContactInfo(BaseModel):
    """Contact information for a reporter or sender.

    Attributes:
        org: Name of the organization.
        contact: Contact email address or identifier.
        domain: Domain associated with the organization.
    """

    model_config = ConfigDict(populate_by_name=True)

    org: str
    contact: str
    domain: str


class XARFEvidence(BaseModel):
    """A single evidence item attached to an XARF report.

    Attributes:
        content_type: MIME type of the evidence payload (e.g. ``"message/rfc822"``).
        payload: Base64-encoded or raw evidence data.
        description: Human-readable description of this evidence item.
        hash: Hex digest of the payload (algorithm indicated by ``hash_algorithm``).
        size: Size of the payload in bytes.
    """

    model_config = ConfigDict(populate_by_name=True)

    content_type: str
    payload: str
    description: str | None = None
    hash: str | None = None
    size: int | None = None


class XARFReport(BaseModel):
    """Base XARF v4 report structure shared by all report types.

    Fields marked *Recommended* in the XARF spec (``x-recommended: true``) are
    modelled as plain optional fields here. Strict-mode validation in
    :mod:`xarf.schema_validator` promotes them to required at validation time.

    Attributes:
        xarf_version: XARF specification version (e.g. ``"4.2.0"``).
        report_id: Unique identifier for this report (UUID recommended).
        timestamp: ISO 8601 datetime string of when the incident was observed.
        reporter: Contact information for the reporting party.
        sender: Contact information for the sending/originating party.
        source_identifier: IP address, domain, or other identifier of the source.
        category: One of the 7 XARF abuse categories.
        type: Report type within the category (e.g. ``"spam"``, ``"ddos"``).
        evidence_source: How the evidence was collected (recommended).
        source_port: Source TCP/UDP port (recommended).
        description: Free-text description of the incident.
        legacy_version: Set to ``"3"`` only for reports converted from XARF v3.
        evidence: List of attached evidence items.
        tags: Arbitrary string tags for categorization.
        confidence: Confidence score for the report (0-100).
        internal: Internal metadata; serialized as ``_internal`` in JSON.
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )

    # Required fields
    xarf_version: str
    report_id: str
    timestamp: str
    reporter: ContactInfo
    sender: ContactInfo
    source_identifier: str
    category: str
    type: str

    # Recommended fields (optional in schema; promoted to required under strict mode)
    evidence_source: str | None = None
    source_port: int | None = None

    # Optional fields
    description: str | None = None
    legacy_version: str | None = None
    evidence: list[XARFEvidence] | None = None
    tags: list[str] | None = None
    confidence: int | None = None
    internal: dict[str, object] | None = Field(default=None, alias="_internal")


# ---------------------------------------------------------------------------
# AnyXARFReport discriminated union
# ---------------------------------------------------------------------------
# Concrete type imports live at the bottom to avoid circular imports.
# models.py defines XARFReport; category files import XARFReport from models;
# models.py then imports the concrete types after XARFReport is fully defined.


def _report_discriminator(v: dict[str, object] | XARFReport) -> str:
    """Derive a composite discriminator key ``"<category>/<type>"`` from a report.

    Args:
        v: A raw dict or an already-constructed :class:`XARFReport` subclass.

    Returns:
        A string of the form ``"<category>/<type>"`` used to select the concrete
        model class during Pydantic discriminated-union validation.
    """
    if isinstance(v, dict):
        return f"{v.get('category')}/{v.get('type')}"
    return f"{v.category}/{v.type}"


from xarf.types_connection import (  # noqa: E402
    DdosReport,
    InfectedHostReport,
    LoginAttackReport,
    PortScanReport,
    ReconnaissanceReport,
    ScrapingReport,
    SqlInjectionReport,
    VulnerabilityScanReport,
)
from xarf.types_content import (  # noqa: E402
    BrandInfringementReport,
    CsamReport,
    CsemReport,
    ExposedDataReport,
    FraudReport,
    MalwareReport,
    PhishingReport,
    RemoteCompromiseReport,
    SuspiciousRegistrationReport,
)
from xarf.types_copyright import (  # noqa: E402
    CopyrightCopyrightReport,
    CopyrightCyberlockerReport,
    CopyrightLinkSiteReport,
    CopyrightP2pReport,
    CopyrightUgcPlatformReport,
    CopyrightUsenetReport,
)
from xarf.types_infrastructure import (  # noqa: E402
    BotnetReport,
    CompromisedServerReport,
)
from xarf.types_messaging import BulkMessagingReport, SpamReport  # noqa: E402
from xarf.types_reputation import (  # noqa: E402
    BlocklistReport,
    ThreatIntelligenceReport,
)
from xarf.types_vulnerability import (  # noqa: E402
    CveReport,
    MisconfigurationReport,
    OpenServiceReport,
)

AnyXARFReport = Annotated[
    # messaging
    Annotated[SpamReport, Tag("messaging/spam")]
    | Annotated[BulkMessagingReport, Tag("messaging/bulk_messaging")]
    # connection
    | Annotated[LoginAttackReport, Tag("connection/login_attack")]
    | Annotated[PortScanReport, Tag("connection/port_scan")]
    | Annotated[DdosReport, Tag("connection/ddos")]
    | Annotated[InfectedHostReport, Tag("connection/infected_host")]
    | Annotated[ReconnaissanceReport, Tag("connection/reconnaissance")]
    | Annotated[ScrapingReport, Tag("connection/scraping")]
    | Annotated[SqlInjectionReport, Tag("connection/sql_injection")]
    | Annotated[VulnerabilityScanReport, Tag("connection/vulnerability_scan")]
    # content
    | Annotated[PhishingReport, Tag("content/phishing")]
    | Annotated[MalwareReport, Tag("content/malware")]
    | Annotated[CsamReport, Tag("content/csam")]
    | Annotated[CsemReport, Tag("content/csem")]
    | Annotated[ExposedDataReport, Tag("content/exposed_data")]
    | Annotated[BrandInfringementReport, Tag("content/brand_infringement")]
    | Annotated[FraudReport, Tag("content/fraud")]
    | Annotated[RemoteCompromiseReport, Tag("content/remote_compromise")]
    | Annotated[SuspiciousRegistrationReport, Tag("content/suspicious_registration")]
    # copyright
    | Annotated[CopyrightCopyrightReport, Tag("copyright/copyright")]
    | Annotated[CopyrightP2pReport, Tag("copyright/p2p")]
    | Annotated[CopyrightCyberlockerReport, Tag("copyright/cyberlocker")]
    | Annotated[CopyrightUgcPlatformReport, Tag("copyright/ugc_platform")]
    | Annotated[CopyrightLinkSiteReport, Tag("copyright/link_site")]
    | Annotated[CopyrightUsenetReport, Tag("copyright/usenet")]
    # infrastructure
    | Annotated[BotnetReport, Tag("infrastructure/botnet")]
    | Annotated[CompromisedServerReport, Tag("infrastructure/compromised_server")]
    # vulnerability
    | Annotated[CveReport, Tag("vulnerability/cve")]
    | Annotated[OpenServiceReport, Tag("vulnerability/open_service")]
    | Annotated[MisconfigurationReport, Tag("vulnerability/misconfiguration")]
    # reputation
    | Annotated[BlocklistReport, Tag("reputation/blocklist")]
    | Annotated[ThreatIntelligenceReport, Tag("reputation/threat_intelligence")],
    Discriminator(_report_discriminator),
]
"""Union of all 32 concrete XARF report types with a composite discriminator.

Pydantic resolves the correct subclass at runtime using the composite
``"<category>/<type>"`` key produced by :func:`_report_discriminator`.

Example:
    >>> from pydantic import TypeAdapter
    >>> from xarf.models import AnyXARFReport
    >>> adapter = TypeAdapter(AnyXARFReport)
    >>> report = adapter.validate_python({"category": "messaging", "type": "spam", ...})
"""
