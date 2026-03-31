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

from xarf._version import SPEC_VERSION
from xarf.exceptions import (
    XARFError,
    XARFParseError,
    XARFSchemaError,
    XARFValidationError,
)
from xarf.generator import create_evidence, create_report
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
from xarf.parser import parse
from xarf.schema_registry import (
    FieldMetadata,
    SchemaRegistry,
    schema_registry,
)
from xarf.schema_validator import SchemaValidator, schema_validator
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
from xarf.v3_compat import (
    XARFv3DeprecationWarning,
    convert_v3_to_v4,
    get_v3_deprecation_warning,
    is_v3_report,
)
from xarf.validator import ValidationResult

__version__ = "0.1.0.dev0"
__author__ = "XARF Project"
__email__ = "contact@xarf.org"

__all__ = [
    # Version
    "SPEC_VERSION",
    # Public API functions
    "parse",
    "create_report",
    "create_evidence",
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
    # Schema registry
    "schema_registry",
    "SchemaRegistry",
    "FieldMetadata",
    # Schema validator
    "SchemaValidator",
    "schema_validator",
    # Validator
    "ValidationResult",
    # v3 compatibility
    "is_v3_report",
    "convert_v3_to_v4",
    "get_v3_deprecation_warning",
    "XARFv3DeprecationWarning",
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
