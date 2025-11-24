"""XARF v3 Backwards Compatibility Module.

This module provides automatic conversion from XARF v3 format to v4 format,
allowing parsers to transparently handle legacy reports.
"""

import uuid
import warnings
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class XARFv3DeprecationWarning(DeprecationWarning):
    """Warning for usage of deprecated XARF v3 format."""


# Enable deprecation warnings by default
warnings.simplefilter("always", XARFv3DeprecationWarning)


def is_v3_report(data: Dict[str, Any]) -> bool:
    """Detect if a report is XARF v3 format.

    Args:
        data: Parsed JSON data

    Returns:
        bool: True if report is v3 format
    """
    # v3 has "Version" field, v4 has "xarf_version"
    return "Version" in data and "xarf_version" not in data


def convert_v3_to_v4(v3_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert XARF v3 report to v4 format.

    Args:
        v3_data: XARF v3 report data

    Returns:
        Dict[str, Any]: Converted XARF v4 report

    Raises:
        ValueError: If v3 data is invalid or cannot be converted
    """
    warnings.warn(
        "XARF v3 format is deprecated. Please upgrade to XARF v4. "
        "This report will be automatically converted, but v3 support "
        "will be removed in a future version.",
        XARFv3DeprecationWarning,
        stacklevel=3,
    )

    # Extract v3 structure
    reporter_info = v3_data.get("ReporterInfo", {})
    report = v3_data.get("Report", {})
    source = report.get("Source", {})

    # Map v3 ReportClass to v4 category
    report_class = report.get("ReportClass", "").lower()
    category_map = {
        "messaging": "messaging",
        "activity": "messaging",  # v3 often used Activity for messaging
        "connection": "connection",
        "content": "content",
        "infrastructure": "infrastructure",
        "copyright": "copyright",
        "vulnerability": "vulnerability",
        "reputation": "reputation",
    }
    category = category_map.get(report_class, "other")

    # Map v3 ReportType to v4 type
    report_type = report.get("ReportType", "").lower()

    # Build base v4 structure
    v4_data: Dict[str, Any] = {
        "xarf_version": "4.0.0",
        "report_id": str(uuid.uuid4()),
        "timestamp": report.get("Date")
        or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reporter": {
            "org": reporter_info.get("ReporterOrg", "Unknown"),
            "contact": (
                reporter_info.get("ReporterOrgEmail")
                or reporter_info.get("ReporterContactEmail")
                or "unknown@example.com"
            ),
            "type": "automated",  # v3 didn't distinguish, assume automated
        },
        "source_identifier": source.get("IP", "0.0.0.0"),
        "category": category,
        "type": report_type,
        "evidence_source": _map_evidence_source(
            report.get("AdditionalInfo", {}).get("DetectionMethod")
        ),
        # Indicate this was converted from v3
        "legacy_version": "3",
        "_internal": {
            "converted_from_v3": True,
            "original_version": v3_data.get("Version"),
        },
    }

    # Convert evidence/attachments
    attachments = report.get("Attachment", [])
    if attachments:
        v4_data["evidence"] = _convert_attachments(attachments)

    # Add category-specific fields based on type
    if category == "messaging":
        _add_messaging_fields(v4_data, report)
    elif category == "connection":
        _add_connection_fields(v4_data, report, source)
    elif category == "content":
        _add_content_fields(v4_data, report)
    elif category == "infrastructure":
        _add_infrastructure_fields(v4_data, report)

    # Add tags if available
    tags = []
    if report.get("ReportClass"):
        tags.append(f"legacy:category:{report['ReportClass']}")
    if report.get("ReportType"):
        tags.append(f"legacy:type:{report['ReportType']}")
    if tags:
        v4_data["tags"] = tags

    return v4_data


def _map_evidence_source(v3_method: Optional[str]) -> str:
    """Map v3 detection method to v4 evidence source."""
    if not v3_method:
        return "automated_scan"

    method_lower = v3_method.lower()
    if "spamtrap" in method_lower:
        return "spamtrap"
    elif "honeypot" in method_lower:
        return "honeypot"
    elif "user" in method_lower or "manual" in method_lower:
        return "user_report"
    elif "scan" in method_lower:
        return "automated_scan"
    elif "vuln" in method_lower:
        return "vulnerability_scan"
    else:
        return "automated_scan"


def _convert_attachments(v3_attachments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert v3 Attachment array to v4 evidence format."""
    v4_evidence = []
    for attachment in v3_attachments:
        evidence_item = {
            "content_type": attachment.get("ContentType", "text/plain"),
            "description": attachment.get("Description", "Evidence from v3 report"),
            "payload": attachment.get("Data", ""),
        }
        v4_evidence.append(evidence_item)
    return v4_evidence


def _add_messaging_fields(v4_data: Dict[str, Any], v3_report: Dict[str, Any]) -> None:
    """Add messaging-specific fields from v3 to v4."""
    additional_info = v3_report.get("AdditionalInfo", {})

    v4_data["protocol"] = additional_info.get("Protocol", "smtp")
    if "SMTPFrom" in additional_info:
        v4_data["smtp_from"] = additional_info["SMTPFrom"]
    if "Subject" in additional_info:
        v4_data["subject"] = additional_info["Subject"]
    if "SMTPTo" in additional_info:
        v4_data["smtp_to"] = additional_info["SMTPTo"]
    if "MessageId" in additional_info:
        v4_data["message_id"] = additional_info["MessageId"]


def _add_connection_fields(
    v4_data: Dict[str, Any], v3_report: Dict[str, Any], v3_source: Dict[str, Any]
) -> None:
    """Add connection-specific fields from v3 to v4."""
    additional_info = v3_report.get("AdditionalInfo", {})

    # Required fields
    v4_data["destination_ip"] = v3_report.get("DestinationIp", "0.0.0.0")
    v4_data["protocol"] = additional_info.get("Protocol", "tcp")

    # Optional fields
    if "Port" in v3_source:
        v4_data["source_port"] = v3_source["Port"]
    if "DestinationPort" in v3_report:
        v4_data["destination_port"] = v3_report["DestinationPort"]
    if "AttackType" in additional_info:
        v4_data["attack_type"] = additional_info["AttackType"]
    if "PacketCount" in additional_info:
        v4_data["packet_count"] = additional_info["PacketCount"]
    if "ByteCount" in additional_info:
        v4_data["byte_count"] = additional_info["ByteCount"]


def _add_content_fields(v4_data: Dict[str, Any], v3_report: Dict[str, Any]) -> None:
    """Add content-specific fields from v3 to v4."""
    additional_info = v3_report.get("AdditionalInfo", {})

    # Required field
    v4_data["url"] = v3_report.get("URL") or additional_info.get(
        "URL", "http://unknown"
    )

    # Optional fields
    if "ContentType" in additional_info:
        v4_data["content_type"] = additional_info["ContentType"]
    if "AttackType" in additional_info:
        v4_data["attack_type"] = additional_info["AttackType"]


def _add_infrastructure_fields(
    v4_data: Dict[str, Any], v3_report: Dict[str, Any]
) -> None:
    """Add infrastructure-specific fields from v3 to v4."""
    additional_info = v3_report.get("AdditionalInfo", {})

    # Infrastructure reports don't have many required fields beyond base
    if "BotnetName" in additional_info:
        v4_data["tags"] = v4_data.get("tags", []) + [
            f"botnet:{additional_info['BotnetName']}"
        ]
    if "MalwareFamily" in additional_info:
        v4_data["tags"] = v4_data.get("tags", []) + [
            f"malware:{additional_info['MalwareFamily']}"
        ]
