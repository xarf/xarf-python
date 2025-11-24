"""XARF Report Generator.

This module provides functionality for generating XARF v4.0.0 compliant reports
programmatically with proper validation and type safety.
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union

from .exceptions import XARFError


class XARFGenerator:
    """Generator for creating XARF v4.0.0 compliant reports.

    This class provides methods to generate complete XARF reports with all
    required fields, proper validation, and support for all 8 report categories.

    Example:
        >>> generator = XARFGenerator()
        >>> report = generator.generate_report(
        ...     category="connection",
        ...     report_type="ddos",
        ...     source_identifier="192.0.2.100",
        ...     reporter_contact="abuse@example.com",
        ...     reporter_org="Example Security Team"
        ... )
    """

    # XARF v4.0.0 specification constants
    XARF_VERSION = "4.0.0"

    # Valid categories as per XARF spec
    VALID_CATEGORIES = {
        "abuse",
        "messaging",
        "connection",
        "content",
        "copyright",
        "infrastructure",
        "vulnerability",
        "reputation",
    }

    # Valid types per category
    EVENT_TYPES: Dict[str, List[str]] = {
        "abuse": ["ddos", "malware", "phishing", "spam", "scanner"],
        "vulnerability": ["cve", "misconfiguration", "open_service"],
        "connection": [
            "compromised",
            "botnet",
            "malicious_traffic",
            "ddos",
            "port_scan",
            "login_attack",
            "sql_injection",
            "reconnaissance",
            "scraping",
            "vuln_scanning",
            "bot",
            "infected_host",
        ],
        "content": [
            "illegal",
            "malicious",
            "policy_violation",
            "phishing",
            "malware",
            "fraud",
            "exposed_data",
            "csam",
            "csem",
            "brand_infringement",
            "suspicious_registration",
            "remote_compromise",
        ],
        "copyright": [
            "infringement",
            "dmca",
            "trademark",
            "p2p",
            "cyberlocker",
            "link_site",
            "ugc_platform",
            "usenet",
            "copyright",
        ],
        "messaging": ["bulk_messaging", "spam"],
        "reputation": ["blocklist", "threat_intelligence"],
        "infrastructure": ["botnet", "compromised_server"],
    }

    # Valid evidence sources
    VALID_EVIDENCE_SOURCES = {
        "spamtrap",
        "honeypot",
        "user_report",
        "automated_scan",
        "manual_analysis",
        "vulnerability_scan",
        "researcher_analysis",
        "threat_intelligence",
        "flow_analysis",
        "ids_ips",
        "siem",
    }

    # Valid reporter types
    VALID_REPORTER_TYPES = {"automated", "manual", "hybrid"}

    # Valid severity levels
    VALID_SEVERITIES = {"low", "medium", "high", "critical"}

    # Evidence content types by category
    EVIDENCE_CONTENT_TYPES: Dict[str, List[str]] = {
        "abuse": ["application/pcap", "text/plain", "image/png"],
        "vulnerability": ["text/plain", "application/json", "image/png"],
        "connection": ["application/pcap", "text/plain", "application/json"],
        "content": ["image/png", "text/html", "application/pdf"],
        "copyright": ["text/html", "image/png", "application/pdf"],
        "messaging": ["message/rfc822", "text/plain", "text/html"],
        "reputation": ["application/json", "text/plain", "text/csv"],
        "infrastructure": ["application/pcap", "text/plain", "application/json"],
    }

    def __init__(self) -> None:
        """Initialize the XARF generator."""

    def generate_uuid(self) -> str:
        """Generate a UUID v4 for report identification.

        Uses Python's uuid.uuid4() which generates cryptographically secure
        random UUIDs as per RFC 4122.

        Returns:
            A string representation of a UUID v4.

        Example:
            >>> generator = XARFGenerator()
            >>> report_id = generator.generate_uuid()
            >>> len(report_id)
            36
        """
        return str(uuid.uuid4())

    def generate_timestamp(self) -> str:
        """Generate an ISO 8601 formatted timestamp with UTC timezone.

        Creates a timestamp in the format required by XARF specification:
        YYYY-MM-DDTHH:MM:SSZ

        Returns:
            ISO 8601 formatted timestamp string with UTC timezone.

        Example:
            >>> generator = XARFGenerator()
            >>> timestamp = generator.generate_timestamp()
            >>> timestamp.endswith('Z')
            True
        """
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def generate_hash(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Generate a cryptographic hash of the provided data.

        Args:
            data: The data to hash (string or bytes).
            algorithm: Hash algorithm to use (default: "sha256").
                      Supported: "sha256", "sha512", "sha1", "md5".

        Returns:
            Hexadecimal string representation of the hash.

        Raises:
            XARFError: If the algorithm is not supported.

        Example:
            >>> generator = XARFGenerator()
            >>> hash_val = generator.generate_hash("test data")
            >>> len(hash_val)
            64
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        elif algorithm == "sha1":
            return hashlib.sha1(data).hexdigest()  # nosec B324
        elif algorithm == "md5":
            return hashlib.md5(data).hexdigest()  # nosec B324
        else:
            raise XARFError(f"Unsupported hash algorithm: {algorithm}")

    def add_evidence(
        self,
        content_type: str,
        description: str,
        payload: Union[str, bytes],
        hash_algorithm: str = "sha256",
    ) -> Dict[str, str]:
        """Create an evidence item with automatic hashing.

        Args:
            content_type: MIME type of the evidence (e.g., "text/plain").
            description: Human-readable description of the evidence.
            payload: The evidence data (base64-encoded string or raw bytes).
            hash_algorithm: Algorithm to use for hashing (default: "sha256").

        Returns:
            Dictionary containing evidence fields including computed hash.

        Example:
            >>> generator = XARFGenerator()
            >>> evidence = generator.add_evidence(
            ...     content_type="text/plain",
            ...     description="Log excerpt",
            ...     payload="Sample log data"
            ... )
            >>> "hash" in evidence
            True
        """
        if isinstance(payload, bytes):
            payload_bytes = payload
            payload_str = payload.decode("utf-8", errors="ignore")
        else:
            payload_str = payload
            payload_bytes = payload.encode("utf-8")

        evidence_hash = self.generate_hash(payload_bytes, hash_algorithm)

        return {
            "content_type": content_type,
            "description": description,
            "payload": payload_str,
            "hash": evidence_hash,
        }

    def generate_report(
        self,
        category: str,
        report_type: str,
        source_identifier: str,
        reporter_contact: str,
        reporter_org: Optional[str] = None,
        reporter_type: str = "automated",
        evidence_source: str = "automated_scan",
        on_behalf_of: Optional[Dict[str, str]] = None,
        description: Optional[str] = None,
        evidence: Optional[List[Dict[str, str]]] = None,
        severity: Optional[str] = None,
        confidence: Optional[float] = None,
        tags: Optional[List[str]] = None,
        occurrence: Optional[Dict[str, str]] = None,
        target: Optional[Dict[str, Any]] = None,
        additional_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate a complete XARF v4.0.0 report.

        Args:
            category: Report category (e.g., "connection", "content").
            report_type: Specific type within category (e.g., "ddos", "phishing").
            source_identifier: Source IP address or identifier.
            reporter_contact: Contact email for the reporter.
            reporter_org: Organization name of the reporter (optional).
            reporter_type: Type of reporter (default: "automated").
            evidence_source: How the evidence was collected (default: "automated_scan").
            on_behalf_of: Dictionary with "org" and optional "contact" keys for
                         reporting on behalf of another entity.
            description: Human-readable description of the incident.
            evidence: List of evidence items (dictionaries with content_type,
                     description, payload, and hash).
            severity: Incident severity (low, medium, high, critical).
            confidence: Confidence score between 0.0 and 1.0.
            tags: List of tags for categorization.
            occurrence: Dictionary with "start" and "end" ISO 8601 timestamps.
            target: Dictionary with target information (ip, port, url, etc.).
            additional_fields: Category-specific fields to include in the report.

        Returns:
            Complete XARF report as a dictionary.

        Raises:
            XARFError: If validation fails or required fields are missing.

        Example:
            >>> generator = XARFGenerator()
            >>> report = generator.generate_report(
            ...     category="connection",
            ...     report_type="ddos",
            ...     source_identifier="192.0.2.100",
            ...     reporter_contact="abuse@example.com",
            ...     reporter_org="Example Security",
            ...     severity="high"
            ... )
            >>> report["xarf_version"]
            '4.0.0'
        """
        # Validate required parameters
        if not source_identifier:
            raise XARFError("source_identifier is required")
        if not reporter_contact:
            raise XARFError("reporter_contact is required")

        # Validate category
        if category not in self.VALID_CATEGORIES:
            raise XARFError(
                f"Invalid category '{category}'. Must be one of: "
                f"{', '.join(sorted(self.VALID_CATEGORIES))}"
            )

        # Validate type for category
        valid_types = self.EVENT_TYPES.get(category, [])
        if report_type not in valid_types:
            raise XARFError(
                f"Invalid type '{report_type}' for category '{category}'. "
                f"Must be one of: {', '.join(valid_types)}"
            )

        # Validate reporter_type
        if reporter_type not in self.VALID_REPORTER_TYPES:
            raise XARFError(
                f"Invalid reporter_type '{reporter_type}'. Must be one of: "
                f"{', '.join(sorted(self.VALID_REPORTER_TYPES))}"
            )

        # Validate evidence_source
        if evidence_source not in self.VALID_EVIDENCE_SOURCES:
            raise XARFError(
                f"Invalid evidence_source '{evidence_source}'. Must be one of: "
                f"{', '.join(sorted(self.VALID_EVIDENCE_SOURCES))}"
            )

        # Validate severity if provided
        if severity and severity not in self.VALID_SEVERITIES:
            raise XARFError(
                f"Invalid severity '{severity}'. Must be one of: "
                f"{', '.join(sorted(self.VALID_SEVERITIES))}"
            )

        # Validate confidence if provided
        if confidence is not None and not (0.0 <= confidence <= 1.0):
            raise XARFError("confidence must be between 0.0 and 1.0")

        # Build base report structure
        report: Dict[str, Any] = {
            "xarf_version": self.XARF_VERSION,
            "report_id": self.generate_uuid(),
            "timestamp": self.generate_timestamp(),
            "reporter": {"contact": reporter_contact, "type": reporter_type},
            "source_identifier": source_identifier,
            "category": category,
            "type": report_type,
            "evidence_source": evidence_source,
        }

        # Add optional reporter fields
        if reporter_org:
            report["reporter"]["org"] = reporter_org

        # Add on_behalf_of if provided
        if on_behalf_of:
            if "org" not in on_behalf_of:
                raise XARFError("on_behalf_of must contain 'org' key")
            report["reporter"]["on_behalf_of"] = on_behalf_of

        # Add optional fields
        if description:
            report["description"] = description

        if evidence:
            report["evidence"] = evidence

        if severity:
            report["severity"] = severity

        if confidence is not None:
            report["confidence"] = confidence

        if tags:
            report["tags"] = tags

        if occurrence:
            if "start" in occurrence and "end" in occurrence:
                report["occurrence"] = occurrence
            else:
                raise XARFError("occurrence must contain 'start' and 'end' keys")

        if target:
            report["target"] = target

        # Add any additional category-specific fields
        if additional_fields:
            report.update(additional_fields)

        return report

    def generate_random_evidence(
        self, category: str, description: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate random sample evidence for testing purposes.

        Args:
            category: Report category to determine appropriate content type.
            description: Custom description (auto-generated if not provided).

        Returns:
            Dictionary containing a sample evidence item.

        Example:
            >>> generator = XARFGenerator()
            >>> evidence = generator.generate_random_evidence("connection")
            >>> "content_type" in evidence
            True
        """
        # Select appropriate content type for category
        content_types = self.EVIDENCE_CONTENT_TYPES.get(category, ["text/plain"])
        content_type = secrets.choice(content_types)

        # Generate random payload data
        random_data = secrets.token_bytes(32)
        payload = random_data.hex()

        # Generate description if not provided
        if not description:
            description = f"Sample {category} evidence data"

        return self.add_evidence(
            content_type=content_type, description=description, payload=payload
        )

    def generate_sample_report(
        self,
        category: str,
        report_type: str,
        include_evidence: bool = True,
        include_optional: bool = True,
    ) -> Dict[str, Any]:
        """Generate a sample XARF report with randomized data for testing.

        Useful for generating test reports, examples, and documentation.

        Args:
            category: Report category (e.g., "connection").
            report_type: Specific type within category (e.g., "ddos").
            include_evidence: Whether to include sample evidence (default: True).
            include_optional: Whether to include optional fields (default: True).

        Returns:
            Complete sample XARF report.

        Raises:
            XARFError: If category or type is invalid.

        Example:
            >>> generator = XARFGenerator()
            >>> sample = generator.generate_sample_report("connection", "ddos")
            >>> sample["category"]
            'connection'
        """
        # Validate inputs
        if category not in self.VALID_CATEGORIES:
            raise XARFError(f"Invalid category: {category}")

        valid_types = self.EVENT_TYPES.get(category, [])
        if report_type not in valid_types:
            raise XARFError(f"Invalid type '{report_type}' for category '{category}'")

        # Generate random test data
        source_ip = f"192.0.2.{secrets.randbelow(256)}"

        sample_orgs = [
            "Security Operations Center",
            "Abuse Response Team",
            "Network Security Team",
            "Threat Intelligence Unit",
            "SOC Team",
        ]
        reporter_org = secrets.choice(sample_orgs)

        sample_domains = ["example.com", "security.net", "abuse.org", "soc.io"]
        reporter_contact = f"abuse@{secrets.choice(sample_domains)}"

        # Build report parameters
        params: Dict[str, Any] = {
            "category": category,
            "report_type": report_type,
            "source_identifier": source_ip,
            "reporter_contact": reporter_contact,
            "reporter_org": reporter_org,
            "description": f"Sample {report_type} report for testing",
        }

        # Add evidence if requested
        if include_evidence:
            params["evidence"] = [self.generate_random_evidence(category)]

        # Add optional fields if requested
        if include_optional:
            params["severity"] = secrets.choice(list(self.VALID_SEVERITIES))
            params["confidence"] = round(0.7 + secrets.randbelow(30) / 100, 2)
            params["tags"] = [category, report_type, "sample"]

            # Add target information
            target_ip = f"203.0.113.{secrets.randbelow(256)}"
            params["target"] = {
                "ip": target_ip,
                "port": secrets.choice([53, 80, 443, 8080, 22, 25]),
            }

            # Add occurrence time range
            now = datetime.now(timezone.utc)
            start = datetime.fromtimestamp(
                now.timestamp() - secrets.randbelow(7200), tz=timezone.utc
            )
            params["occurrence"] = {
                "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

        return self.generate_report(**params)
