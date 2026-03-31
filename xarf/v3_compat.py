"""XARF v3 Backwards Compatibility Module.

Provides automatic detection and conversion of XARF v3 reports to v4 format,
allowing parsers to transparently handle legacy reports.

Mirrors ``v3-legacy.ts`` in ``xarf-javascript/src/``.
"""

from __future__ import annotations

import base64
import hashlib
import uuid
import warnings
from datetime import datetime, timezone
from typing import Any

from xarf.exceptions import XARFParseError

# ---------------------------------------------------------------------------
# Deprecation warning class
# ---------------------------------------------------------------------------


class XARFv3DeprecationWarning(DeprecationWarning):
    """Warning emitted when an XARF v3 report is detected and auto-converted."""


# Show each unique call site once rather than suppressing entirely (the Python
# default silences DeprecationWarning outside __main__ and test runners).
warnings.simplefilter("default", XARFv3DeprecationWarning)

# ---------------------------------------------------------------------------
# Type mapping — mirrors V3_TYPE_MAPPING in v3-legacy.ts exactly
# (PascalCase and lowercase variant for each of the 8 supported v3 types)
# ---------------------------------------------------------------------------

_V3_TYPE_MAPPING: dict[str, tuple[str, str]] = {
    "Spam": ("messaging", "spam"),
    "spam": ("messaging", "spam"),
    "Login-Attack": ("connection", "login_attack"),
    "login-attack": ("connection", "login_attack"),
    "Port-Scan": ("connection", "port_scan"),
    "port-scan": ("connection", "port_scan"),
    "DDoS": ("connection", "ddos"),
    "ddos": ("connection", "ddos"),
    "Phishing": ("content", "phishing"),
    "phishing": ("content", "phishing"),
    "Malware": ("content", "malware"),
    "malware": ("content", "malware"),
    "Botnet": ("infrastructure", "botnet"),
    "botnet": ("infrastructure", "botnet"),
    "Copyright": ("copyright", "copyright"),
    "copyright": ("copyright", "copyright"),
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def is_v3_report(data: dict[str, Any]) -> bool:
    """Detect if a report is XARF v3 format.

    Mirrors ``isXARFv3()`` in ``v3-legacy.ts``.  Checks for the presence of
    ``Version`` (string equal to ``"3"``, ``"3.0"``, or ``"3.0.0"``),
    ``ReporterInfo``, and ``Report`` keys.

    Args:
        data: Parsed JSON data to inspect.

    Returns:
        ``True`` if *data* is a v3-format XARF report.
    """
    version = data.get("Version")
    return (
        isinstance(version, str)
        and version in ("3", "3.0", "3.0.0")
        and "ReporterInfo" in data
        and "Report" in data
    )


def convert_v3_to_v4(
    v3_data: dict[str, Any],
    conversion_warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Convert an XARF v3 report to v4 format.

    Mirrors ``convertV3toV4()`` in ``v3-legacy.ts``.  Emits an
    :class:`XARFv3DeprecationWarning` via :func:`warnings.warn` and raises
    :class:`~xarf.exceptions.XARFParseError` for unrecoverable conversion
    failures (unknown type, missing required fields).

    Args:
        v3_data: Parsed XARF v3 report dict.
        conversion_warnings: Optional list to collect non-fatal conversion
            messages (e.g. missing ``ReporterOrg``).  Mirrors the ``warnings``
            parameter in the JS implementation.

    Returns:
        A dict representing the converted XARF v4 report.

    Raises:
        XARFParseError: If the v3 ``ReportType`` is not in the supported
            mapping, required fields are missing, or source/contact info
            cannot be extracted.

    Example:
        >>> v4 = convert_v3_to_v4(v3_dict)
        >>> v4["xarf_version"]
        '4.2.0'
    """
    warnings.warn(
        get_v3_deprecation_warning(),
        XARFv3DeprecationWarning,
        stacklevel=3,
    )

    report = v3_data.get("Report", {})
    reporter_info = v3_data.get("ReporterInfo", {})

    # ------------------------------------------------------------------
    # Resolve category and type via the type mapping
    # ------------------------------------------------------------------
    report_type = report.get("ReportType", "")
    mapping = _V3_TYPE_MAPPING.get(report_type)
    if mapping is None:
        supported = ", ".join(sorted(set(_V3_TYPE_MAPPING.keys())))
        raise XARFParseError(
            f"Cannot convert v3 report: unknown ReportType '{report_type}'. "
            f"Supported types: {supported}"
        )
    category, v4_type = mapping

    # ------------------------------------------------------------------
    # Extract required fields
    # ------------------------------------------------------------------
    source_identifier = _extract_source_identifier(report)
    contact_info = _extract_contact_info(reporter_info, conversion_warnings)

    # ------------------------------------------------------------------
    # Evidence (Attachment or Samples)
    # ------------------------------------------------------------------
    raw_attachments = report.get("Attachment") or report.get("Samples")
    evidence = _convert_attachments(raw_attachments, conversion_warnings)

    # ------------------------------------------------------------------
    # Build base v4 report
    # ------------------------------------------------------------------
    v4_data: dict[str, Any] = {
        "xarf_version": "4.2.0",
        "report_id": str(uuid.uuid4()),
        "timestamp": report.get("Date"),
        "reporter": contact_info,
        "sender": contact_info,
        "source_identifier": source_identifier,
        "category": category,
        "type": v4_type,
        "legacy_version": "3",
        "_internal": {
            "original_report_type": report_type,
            "converted_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    # description is optional
    if report.get("AttackDescription"):
        v4_data["description"] = report["AttackDescription"]

    # evidence_source only if explicitly provided in the v3 report
    evidence_source = (report.get("AdditionalInfo") or {}).get("DetectionMethod")
    if evidence_source:
        v4_data["evidence_source"] = evidence_source

    if evidence is not None:
        v4_data["evidence"] = evidence

    # ------------------------------------------------------------------
    # Category-specific fields
    # ------------------------------------------------------------------
    if category == "messaging":
        _add_messaging_fields(v4_data, report)
    elif category == "connection":
        _add_connection_fields(v4_data, report)
    elif category == "content":
        _add_content_fields(v4_data, report)

    return v4_data


def get_v3_deprecation_warning() -> str:
    """Return the canonical v3 deprecation warning message.

    Mirrors ``getV3DeprecationWarning()`` in ``v3-legacy.ts``.

    Returns:
        A formatted deprecation warning string.
    """
    return (
        "DEPRECATION WARNING: XARF v3 format detected. "
        "The v3 format has been automatically converted to v4. "
        "Please update your systems to generate v4 reports directly. "
        "v3 support will be removed in a future major version."
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _extract_source_identifier(report: dict[str, Any]) -> str:
    """Extract a source identifier from a v3 report dict.

    Checks ``Source.IP``, ``SourceIp``, ``Source.URL``, and ``Url`` in that
    order, mirroring ``extractSourceIdentifier()`` in ``v3-legacy.ts``.

    Args:
        report: The inner ``Report`` dict from a v3 report.

    Returns:
        The source identifier string.

    Raises:
        XARFParseError: If no source identifier can be found.
    """
    source = report.get("Source") or {}
    if source.get("IP"):
        return str(source["IP"])
    if report.get("SourceIp"):
        return str(report["SourceIp"])
    if source.get("URL"):
        return str(source["URL"])
    if report.get("Url"):
        return str(report["Url"])
    raise XARFParseError(
        "Cannot convert v3 report: no source identifier found "
        "(expected Source.IP, SourceIp, Source.URL, or Url)"
    )


def _extract_contact_info(
    reporter_info: dict[str, Any],
    conversion_warnings: list[str] | None = None,
) -> dict[str, str]:
    """Extract contact info from a v3 ``ReporterInfo`` dict.

    Mirrors ``extractContactInfo()`` in ``v3-legacy.ts``.

    Args:
        reporter_info: The ``ReporterInfo`` dict from a v3 report.
        conversion_warnings: Optional list to append non-fatal warnings to.

    Returns:
        A dict with ``org``, ``contact``, and ``domain`` keys.

    Raises:
        XARFParseError: If no email address is present or the email has no
            domain part.
    """
    contact = reporter_info.get("ReporterContactEmail") or reporter_info.get(
        "ReporterOrgEmail"
    )
    if not contact:
        raise XARFParseError(
            "Cannot convert v3 report: missing reporter email "
            "(ReporterContactEmail and ReporterOrgEmail are both absent)"
        )
    parts = contact.split("@", 1)
    if len(parts) < 2 or not parts[1]:
        raise XARFParseError(
            f"Cannot convert v3 report: reporter email '{contact}' "
            "is not a valid email address"
        )
    domain = parts[1]

    org = reporter_info.get("ReporterOrg")
    if not org:
        if conversion_warnings is not None:
            conversion_warnings.append(
                'No ReporterOrg found in v3 report, using "Unknown Organization"'
            )
        org = "Unknown Organization"

    return {"org": org, "contact": contact, "domain": domain}


def _convert_attachments(
    v3_attachments: list[dict[str, Any]] | None,
    conversion_warnings: list[str] | None = None,
) -> list[dict[str, Any]] | None:
    """Convert v3 ``Attachment`` / ``Samples`` items to v4 evidence format.

    Mirrors ``convertEvidence()`` in ``v3-legacy.ts``.  Computes a sha256
    hash and byte size from the base64-encoded ``Data`` field.

    Args:
        v3_attachments: List of v3 attachment dicts, or ``None``.
        conversion_warnings: Optional list to append non-fatal warnings to.

    Returns:
        A list of v4 evidence dicts, or ``None`` if *v3_attachments* is empty
        or ``None``.
    """
    if not v3_attachments:
        return None

    result = []
    for attachment in v3_attachments:
        description = attachment.get("Description")
        if not description and conversion_warnings is not None:
            conversion_warnings.append(
                "Evidence attachment has no description, omitting field"
            )

        raw_data = attachment.get("Data", "")
        try:
            raw_bytes = base64.b64decode(raw_data)
        except ValueError:
            raw_bytes = b""

        digest = hashlib.sha256(raw_bytes).hexdigest()

        item: dict[str, Any] = {
            "content_type": attachment.get("ContentType", "application/octet-stream"),
            "payload": raw_data,
            "hash": f"sha256:{digest}",
            "size": len(raw_bytes),
        }
        if description:
            item["description"] = description

        result.append(item)

    return result


def _add_messaging_fields(v4_data: dict[str, Any], report: dict[str, Any]) -> None:
    """Merge messaging-specific fields into *v4_data*.

    Mirrors ``addMessagingFields()`` in ``v3-legacy.ts``.

    Args:
        v4_data: The partially-built v4 report dict (mutated in-place).
        report: The inner ``Report`` dict from the v3 report.

    Raises:
        XARFParseError: If no protocol can be determined.
    """
    additional_info: dict[str, Any] = report.get("AdditionalInfo") or {}
    protocol = report.get("Protocol") or additional_info.get("Protocol")
    if not protocol:
        raise XARFParseError(
            "Cannot convert v3 report: missing protocol for messaging type"
        )

    v4_data["protocol"] = protocol

    smtp_from = report.get("SmtpMailFromAddress") or additional_info.get("SMTPFrom")
    if smtp_from:
        v4_data["smtp_from"] = smtp_from

    smtp_to = report.get("SmtpRcptToAddress")
    if smtp_to:
        v4_data["smtp_to"] = smtp_to

    subject = report.get("SmtpMessageSubject") or additional_info.get("Subject")
    if subject:
        v4_data["subject"] = subject

    source = report.get("Source") or {}
    source_port = source.get("Port") or report.get("SourcePort")
    if source_port is not None:
        v4_data["source_port"] = source_port


def _add_connection_fields(v4_data: dict[str, Any], report: dict[str, Any]) -> None:
    """Merge connection-specific fields into *v4_data*.

    Mirrors ``addConnectionFields()`` in ``v3-legacy.ts``.

    Args:
        v4_data: The partially-built v4 report dict (mutated in-place).
        report: The inner ``Report`` dict from the v3 report.

    Raises:
        XARFParseError: If no protocol is present.
    """
    protocol = report.get("Protocol")
    if not protocol:
        raise XARFParseError(
            "Cannot convert v3 report: missing protocol for connection type"
        )

    v4_data["protocol"] = protocol
    # first_seen is required for connection types in v4
    v4_data["first_seen"] = report.get("Date")

    if report.get("DestinationIp"):
        v4_data["destination_ip"] = report["DestinationIp"]

    source = report.get("Source") or {}
    source_port = source.get("Port") or report.get("SourcePort")
    if source_port is not None:
        v4_data["source_port"] = source_port

    if report.get("DestinationPort") is not None:
        v4_data["destination_port"] = report["DestinationPort"]

    if report.get("AttackCount") is not None:
        v4_data["attack_count"] = report["AttackCount"]


def _add_content_fields(v4_data: dict[str, Any], report: dict[str, Any]) -> None:
    """Merge content-specific fields into *v4_data*.

    Mirrors ``addContentFields()`` in ``v3-legacy.ts``.

    Args:
        v4_data: The partially-built v4 report dict (mutated in-place).
        report: The inner ``Report`` dict from the v3 report.

    Raises:
        XARFParseError: If no URL can be found.
    """
    additional_info: dict[str, Any] = report.get("AdditionalInfo") or {}
    source: dict[str, Any] = report.get("Source") or {}
    url = report.get("Url") or additional_info.get("URL") or source.get("URL")
    if not url:
        raise XARFParseError(
            f"Cannot convert v3 report: missing URL for content type "
            f"'{v4_data.get('type')}'. Content reports require a URL field"
        )
    v4_data["url"] = url
