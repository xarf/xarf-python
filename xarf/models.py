"""XARF Data Models.

Pydantic models for XARF v4 abuse reports, aligned with the JSON Schema spec.
"""

from datetime import datetime
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ContactInfo(BaseModel):
    """XARF Contact Information (reporter/sender).

    Per xarf-core.json $defs/contact_info:
    - org: Organization name (required)
    - contact: Contact email address (required)
    - domain: Organization domain for verification (required)
    """

    org: str = Field(..., max_length=200, description="Organization name")
    contact: str = Field(..., description="Contact email address")
    domain: str = Field(..., description="Organization domain for verification")

    model_config = ConfigDict(extra="forbid")


# Alias for backward compatibility
XARFReporter = ContactInfo


class XARFEvidence(BaseModel):
    """XARF Evidence item.

    Per xarf-core.json $defs/evidence_item:
    - content_type: MIME type (required)
    - payload: Base64-encoded data (required)
    - description: Human-readable description (recommended, optional)
    - hash: Integrity hash in format 'algorithm:hexvalue' (recommended, optional)
    - size: Size in bytes (optional)
    """

    content_type: str = Field(..., description="MIME type of the evidence content")
    payload: str = Field(..., description="Base64-encoded evidence data")
    description: Optional[str] = Field(
        None, max_length=500, description="Human-readable description"
    )
    hash: Optional[str] = Field(
        None,
        pattern=r"^(md5|sha1|sha256|sha512):[a-fA-F0-9]+$",
        description="Hash for integrity verification",
    )
    size: Optional[int] = Field(
        None, ge=0, le=5242880, description="Size in bytes (max 5MB)"
    )

    model_config = ConfigDict(extra="forbid")


class XARFReport(BaseModel):
    """Base XARF v4 Report model.

    Per xarf-core.json, required fields are:
    - xarf_version, report_id, timestamp
    - reporter, sender (both ContactInfo)
    - source_identifier, category, type

    Optional/recommended fields:
    - evidence_source (recommended)
    - source_port (recommended for CGNAT)
    - evidence, tags, confidence, description
    - legacy_version, _internal
    """

    # Required base fields (per xarf-core.json)
    xarf_version: str = Field(
        ..., pattern=r"^4\.[0-9]+\.[0-9]+$", description="XARF schema version"
    )
    report_id: str = Field(..., description="Unique report identifier (UUID)")
    timestamp: Union[datetime, str] = Field(
        ..., description="ISO 8601 timestamp of abuse incident"
    )
    reporter: ContactInfo = Field(
        ..., description="Organization that owns/generated the complaint"
    )
    sender: ContactInfo = Field(
        ..., description="Organization that transmitted/filed this report"
    )
    source_identifier: str = Field(
        ..., description="IP address, domain, or identifier of abuse source"
    )
    category: str = Field(..., description="Primary abuse classification category")
    type: str = Field(..., description="Specific abuse type within the category")

    # Recommended fields
    evidence_source: Optional[str] = Field(
        None, description="Quality/reliability indicator for evidence"
    )
    source_port: Optional[int] = Field(
        None,
        ge=1,
        le=65535,
        description="Source port (critical for CGNAT identification)",
    )
    evidence: Optional[list[XARFEvidence]] = Field(
        default=None, description="Evidence items supporting this report"
    )
    confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )

    # Optional fields
    tags: Optional[list[str]] = Field(
        default=None, description="Namespaced tags for categorization"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Human-readable description"
    )
    on_behalf_of: Optional[ContactInfo] = Field(
        None, description="Original reporter if sender is filing on their behalf"
    )
    legacy_version: Optional[str] = Field(
        None, description="Original XARF version if converted from v3"
    )
    # Note: _internal from schema is handled via extra="allow" since Pydantic
    # doesn't allow field names starting with underscore

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Allow category-specific fields including _internal
    )


class MessagingReport(XARFReport):
    """XARF Messaging category report.

    For spam, phishing, malware distribution via email/messaging.
    """

    # Protocol information
    protocol: Optional[str] = Field(None, description="Messaging protocol (smtp, etc)")

    # Email-specific fields
    smtp_from: Optional[str] = Field(None, description="SMTP envelope sender")
    smtp_to: Optional[str] = Field(None, description="SMTP envelope recipient")
    subject: Optional[str] = Field(None, description="Email subject line")
    message_id: Optional[str] = Field(None, description="Email Message-ID header")

    # Common messaging fields
    sender_display_name: Optional[str] = Field(
        None, description="Display name of sender"
    )
    target_victim: Optional[str] = Field(
        None, description="Intended victim of the message"
    )
    message_content: Optional[str] = Field(None, description="Message body content")


class ConnectionReport(XARFReport):
    """XARF Connection category report.

    For DDoS, port scans, brute force, unauthorized access attempts.
    """

    # Connection-specific fields
    destination_ip: Optional[str] = Field(None, description="Target IP address")
    destination_port: Optional[int] = Field(
        None, ge=1, le=65535, description="Target port"
    )
    protocol: Optional[str] = Field(
        None, description="Network protocol (tcp, udp, icmp)"
    )

    # Attack metrics
    attack_type: Optional[str] = Field(None, description="Type of attack")
    duration_minutes: Optional[int] = Field(None, description="Attack duration")
    packet_count: Optional[int] = Field(None, description="Number of packets")
    byte_count: Optional[int] = Field(None, description="Total bytes transferred")

    # Login attack specific
    attempt_count: Optional[int] = Field(None, description="Number of login attempts")
    successful_logins: Optional[int] = Field(
        None, description="Number of successful logins"
    )
    usernames_attempted: Optional[list[str]] = Field(
        default=None, description="Usernames tried"
    )
    attack_pattern: Optional[str] = Field(
        None, description="Pattern of attack (sequential, distributed, etc)"
    )


class ContentReport(XARFReport):
    """XARF Content category report.

    For malicious content, web hacks, defacement, malware hosting.
    """

    # Content-specific fields
    url: Optional[str] = Field(None, description="URL of malicious content")
    content_type: Optional[str] = Field(None, description="Type of content")
    attack_type: Optional[str] = Field(None, description="Type of content attack")

    # Web hack specific
    affected_pages: Optional[list[str]] = Field(
        default=None, description="List of affected pages"
    )
    cms_platform: Optional[str] = Field(None, description="CMS platform if applicable")
    vulnerability_exploited: Optional[str] = Field(
        None, description="Vulnerability that was exploited"
    )
    affected_parameters: Optional[list[str]] = Field(
        default=None, description="Affected URL parameters"
    )
    payload_detected: Optional[str] = Field(
        None, description="Malicious payload detected"
    )
    data_exposed: Optional[list[str]] = Field(
        default=None, description="Types of data exposed"
    )
    database_type: Optional[str] = Field(
        None, description="Database type if SQL injection"
    )
    records_potentially_affected: Optional[int] = Field(
        None, description="Number of records potentially affected"
    )


class InfrastructureReport(XARFReport):
    """XARF Infrastructure category report.

    For DNS abuse, BGP hijacking, certificate issues.
    """

    # DNS-specific fields
    domain_name: Optional[str] = Field(None, description="Affected domain name")
    dns_record_type: Optional[str] = Field(None, description="DNS record type")
    malicious_records: Optional[list[str]] = Field(
        default=None, description="Malicious DNS records"
    )

    # BGP-specific fields
    asn: Optional[int] = Field(None, description="Autonomous System Number")
    prefix: Optional[str] = Field(None, description="IP prefix")
    legitimate_origin: Optional[int] = Field(None, description="Legitimate origin ASN")

    # Certificate-specific fields
    certificate_serial: Optional[str] = Field(None, description="Certificate serial")
    certificate_issuer: Optional[str] = Field(None, description="Certificate issuer")


class CopyrightReport(XARFReport):
    """XARF Copyright category report.

    For DMCA notices, piracy, trademark violations.
    """

    # Copyright-specific fields
    work_title: Optional[str] = Field(None, description="Title of copyrighted work")
    work_type: Optional[str] = Field(
        None, description="Type of work (movie, music, software, etc)"
    )
    rights_holder: Optional[str] = Field(None, description="Copyright holder name")
    infringing_url: Optional[str] = Field(None, description="URL of infringing content")
    original_url: Optional[str] = Field(None, description="URL of original content")
    dmca_notice_id: Optional[str] = Field(None, description="DMCA notice identifier")


class VulnerabilityReport(XARFReport):
    """XARF Vulnerability category report.

    For open resolvers, exposed services, misconfigurations.
    """

    # Vulnerability-specific fields
    vulnerability_type: Optional[str] = Field(None, description="Type of vulnerability")
    cve_id: Optional[str] = Field(None, description="CVE identifier if applicable")
    cvss_score: Optional[float] = Field(None, ge=0.0, le=10.0, description="CVSS score")
    affected_service: Optional[str] = Field(None, description="Affected service name")
    affected_version: Optional[str] = Field(None, description="Affected version")
    remediation: Optional[str] = Field(None, description="Recommended remediation")


class ReputationReport(XARFReport):
    """XARF Reputation category report.

    For blocklist entries, reputation scoring.
    """

    # Reputation-specific fields
    blocklist_name: Optional[str] = Field(None, description="Name of blocklist")
    blocklist_url: Optional[str] = Field(None, description="URL of blocklist")
    listing_reason: Optional[str] = Field(None, description="Reason for listing")
    first_seen: Optional[Union[datetime, str]] = Field(
        None, description="When first observed"
    )
    last_seen: Optional[Union[datetime, str]] = Field(
        None, description="When last observed"
    )
    reputation_score: Optional[float] = Field(None, description="Reputation score")
