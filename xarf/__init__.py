"""XARF v4 Python library.

A Python library for parsing, generating, and validating XARF v4
(eXtended Abuse Reporting Format) reports. Includes backwards
compatibility with XARF v3.

Example:
    >>> from xarf import parse, create_report, create_evidence
    >>> result = parse(json_data)
    >>> result.report
    SpamReport(...)
"""

from xarf.exceptions import (
    XARFError,
    XARFParseError,
    XARFSchemaError,
    XARFValidationError,
)
from xarf.models import (
    AnyXARFReport,
    ContactInfo,
    CreateReportResult,
    ParseResult,
    ValidationError,
    ValidationWarning,
    XARFEvidence,
    XARFReport,
)
from xarf.types_connection import (
    ConnectionBaseReport,
    ConnectionReport,
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
    ContentReport,
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
    CopyrightReport,
    CopyrightUgcPlatformReport,
    CopyrightUsenetReport,
    CyberlockerTakedownInfo,
    CyberlockerUploaderInfo,
    FileInfo,
    LinkedContentItem,
    LinkSiteLinkInfo,
    LinkSiteRanking,
    MessageInfo,
    PeerInfo,
    SwarmInfo,
    UgcContentInfo,
    UgcMatchDetails,
    UgcMonetizationInfo,
    UgcUploaderInfo,
    UsenetEncodingInfo,
    UsenetNzbInfo,
    UsenetServerInfo,
)
from xarf.types_infrastructure import (
    BotnetReport,
    CompromisedServerReport,
    InfrastructureBaseReport,
    InfrastructureReport,
)
from xarf.types_messaging import (
    BulkIndicators,
    BulkMessagingReport,
    MessagingBaseReport,
    MessagingReport,
    SpamIndicators,
    SpamReport,
)
from xarf.types_reputation import (
    BlocklistReport,
    ReputationBaseReport,
    ReputationReport,
    ThreatIntelligenceReport,
)
from xarf.types_vulnerability import (
    CveReport,
    ImpactAssessment,
    MisconfigurationReport,
    OpenServiceReport,
    VulnerabilityBaseReport,
    VulnerabilityReport,
)
from xarf.v3_compat import convert_v3_to_v4, is_v3_report

__version__ = "0.1.0.dev0"
__author__ = "XARF Project"
__email__ = "contact@xarf.org"

# Spec version this library was built against.
SPEC_VERSION = "4.2.0"

__all__ = [
    # Version
    "SPEC_VERSION",
    # Result types
    "AnyXARFReport",
    "ParseResult",
    "CreateReportResult",
    "ValidationError",
    "ValidationWarning",
    # Base models
    "XARFReport",
    "XARFEvidence",
    "ContactInfo",
    # Exceptions
    "XARFError",
    "XARFValidationError",
    "XARFParseError",
    "XARFSchemaError",
    # v3 compatibility
    "is_v3_report",
    "convert_v3_to_v4",
    # Messaging
    "MessagingBaseReport",
    "SpamIndicators",
    "SpamReport",
    "BulkIndicators",
    "BulkMessagingReport",
    "MessagingReport",
    # Connection
    "ConnectionBaseReport",
    "LoginAttackReport",
    "PortScanReport",
    "DdosReport",
    "InfectedHostReport",
    "ReconnaissanceReport",
    "ScrapingReport",
    "SqlInjectionReport",
    "VulnerabilityScanReport",
    "ConnectionReport",
    # Content
    "ContentBaseReport",
    "PhishingReport",
    "MalwareReport",
    "CsamReport",
    "CsemReport",
    "ExposedDataReport",
    "BrandInfringementReport",
    "FraudReport",
    "CompromiseIndicator",
    "WebshellDetails",
    "RemoteCompromiseReport",
    "RegistrantDetails",
    "SuspiciousRegistrationReport",
    "ContentReport",
    # Infrastructure
    "InfrastructureBaseReport",
    "BotnetReport",
    "CompromisedServerReport",
    "InfrastructureReport",
    # Copyright
    "CopyrightBaseReport",
    "CopyrightCopyrightReport",
    "SwarmInfo",
    "PeerInfo",
    "CopyrightP2pReport",
    "FileInfo",
    "CyberlockerTakedownInfo",
    "CyberlockerUploaderInfo",
    "CopyrightCyberlockerReport",
    "UgcContentInfo",
    "UgcUploaderInfo",
    "UgcMatchDetails",
    "UgcMonetizationInfo",
    "CopyrightUgcPlatformReport",
    "LinkSiteLinkInfo",
    "LinkedContentItem",
    "LinkSiteRanking",
    "CopyrightLinkSiteReport",
    "MessageInfo",
    "UsenetEncodingInfo",
    "UsenetNzbInfo",
    "UsenetServerInfo",
    "CopyrightUsenetReport",
    "CopyrightReport",
    # Vulnerability
    "VulnerabilityBaseReport",
    "ImpactAssessment",
    "CveReport",
    "OpenServiceReport",
    "MisconfigurationReport",
    "VulnerabilityReport",
    # Reputation
    "ReputationBaseReport",
    "BlocklistReport",
    "ThreatIntelligenceReport",
    "ReputationReport",
]
