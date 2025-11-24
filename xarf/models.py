"""XARF Data Models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class XARFReporter(BaseModel):
    """XARF Reporter information."""

    org: str
    contact: str
    type: str = Field(..., pattern="^(automated|manual|hybrid)$")


class XARFEvidence(BaseModel):
    """XARF Evidence item."""

    content_type: str
    description: str
    payload: str


class XARFReport(BaseModel):
    """Base XARF v4 Report model."""

    # Required base fields
    xarf_version: str = Field(..., pattern="^4\\.0\\.0$")
    report_id: str
    timestamp: datetime
    reporter: XARFReporter
    on_behalf_of: Optional[XARFReporter] = None
    source_identifier: str
    category: str = Field(..., alias="category")
    type: str
    evidence_source: str

    # Optional base fields
    evidence: Optional[List[XARFEvidence]] = []
    tags: Optional[List[str]] = []
    _internal: Optional[Dict[str, Any]] = None

    # Category-specific fields (will be populated based on category)
    additional_fields: Optional[Dict[str, Any]] = {}

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Allow additional fields for category-specific data
    )

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate XARF category field."""
        valid_categories = {
            "messaging",
            "connection",
            "content",
            "infrastructure",
            "copyright",
            "vulnerability",
            "reputation",
            "other",
        }
        if v not in valid_categories:
            raise ValueError(
                f"Invalid category '{v}'. Must be one of: {valid_categories}"
            )
        return v

    @field_validator("evidence_source")
    @classmethod
    def validate_evidence_source(cls, v: str) -> str:
        """Validate evidence source field."""
        valid_sources = {
            "spamtrap",
            "honeypot",
            "user_report",
            "automated_scan",
            "manual_analysis",
            "vulnerability_scan",
            "researcher_analysis",
            "threat_intelligence",
        }
        if v not in valid_sources:
            raise ValueError(
                f"Invalid evidence_source '{v}'. Must be one of: {valid_sources}"
            )
        return v


class MessagingReport(XARFReport):
    """XARF Messaging category report."""

    # Required for messaging
    protocol: Optional[str] = None

    # Email-specific fields
    smtp_from: Optional[str] = None
    smtp_to: Optional[str] = None
    subject: Optional[str] = None
    message_id: Optional[str] = None

    # Common messaging fields
    sender_display_name: Optional[str] = None
    target_victim: Optional[str] = None
    message_content: Optional[str] = None


class ConnectionReport(XARFReport):
    """XARF Connection category report."""

    # Required for connection
    destination_ip: str
    protocol: str

    # Optional connection fields
    destination_port: Optional[int] = None
    source_port: Optional[int] = None
    attack_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    packet_count: Optional[int] = None
    byte_count: Optional[int] = None

    # Login attack specific
    attempt_count: Optional[int] = None
    successful_logins: Optional[int] = None
    usernames_attempted: Optional[List[str]] = []
    attack_pattern: Optional[str] = None


class ContentReport(XARFReport):
    """XARF Content category report."""

    # Required for content
    url: str

    # Optional content fields
    content_type: Optional[str] = None
    attack_type: Optional[str] = None
    affected_pages: Optional[List[str]] = []
    cms_platform: Optional[str] = None
    vulnerability_exploited: Optional[str] = None

    # Web hack specific
    affected_parameters: Optional[List[str]] = []
    payload_detected: Optional[str] = None
    data_exposed: Optional[List[str]] = []
    database_type: Optional[str] = None
    records_potentially_affected: Optional[int] = None
