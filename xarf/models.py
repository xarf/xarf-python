"""XARF Data Models."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class XARFReporter(BaseModel):
    """XARF Reporter information."""
    org: str
    contact: str
    type: str = Field(..., regex="^(automated|manual|hybrid)$")


class XARFEvidence(BaseModel):
    """XARF Evidence item."""
    content_type: str
    description: str
    payload: str


class XARFReport(BaseModel):
    """Base XARF v4 Report model."""
    
    # Required base fields
    xarf_version: str = Field(..., regex="^4\\.0\\.0$")
    report_id: str
    timestamp: datetime
    reporter: XARFReporter
    source_identifier: str
    class_: str = Field(..., alias="class")
    type: str
    evidence_source: str
    
    # Optional base fields
    evidence: Optional[List[XARFEvidence]] = []
    tags: Optional[List[str]] = []
    _internal: Optional[Dict[str, Any]] = None
    
    # Class-specific fields (will be populated based on class)
    additional_fields: Optional[Dict[str, Any]] = {}
    
    class Config:
        allow_population_by_field_name = True
        extra = "allow"  # Allow additional fields for class-specific data
    
    @validator("class_")
    def validate_class(cls, v):
        """Validate XARF class field."""
        valid_classes = {
            "messaging", "connection", "content", 
            "infrastructure", "copyright", "vulnerability", "reputation"
        }
        if v not in valid_classes:
            raise ValueError(f"Invalid class '{v}'. Must be one of: {valid_classes}")
        return v
    
    @validator("evidence_source")
    def validate_evidence_source(cls, v):
        """Validate evidence source field."""
        valid_sources = {
            "spamtrap", "honeypot", "user_report", 
            "automated_scan", "manual_analysis", "vulnerability_scan",
            "researcher_analysis", "threat_intelligence"
        }
        if v not in valid_sources:
            raise ValueError(f"Invalid evidence_source '{v}'. Must be one of: {valid_sources}")
        return v


class MessagingReport(XARFReport):
    """XARF Messaging class report."""
    
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
    """XARF Connection class report."""
    
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
    """XARF Content class report."""
    
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