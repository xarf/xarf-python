"""XARF Report Generator.

This module provides functionality for generating XARF v4.0.0 compliant reports
programmatically with proper validation and type safety.

Aligned with the JavaScript reference implementation (xarf-javascript).
"""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any, TypedDict

from .exceptions import XARFError
from .schema_registry import schema_registry


class ContactInfo(TypedDict):
    """Contact information for reporter/sender.

    Per xarf-core.json $defs/contact_info:
    - org: Organization name (required)
    - contact: Contact email address (required)
    - domain: Organization domain for verification (required)
    """

    org: str
    contact: str
    domain: str


class XARFGenerator:
    """Generator for creating XARF v4.0.0 compliant reports.

    This class provides methods to generate complete XARF reports with all
    required fields, proper validation, and support for all 7 report categories.

    Example:
        >>> generator = XARFGenerator()
        >>> report = generator.generate_report(
        ...     category="connection",
        ...     report_type="ddos",
        ...     source_identifier="192.0.2.100",
        ...     reporter={
        ...         "org": "Example Security Team",
        ...         "contact": "abuse@example.com",
        ...         "domain": "example.com",
        ...     },
        ...     sender={
        ...         "org": "Example Security Team",
        ...         "contact": "abuse@example.com",
        ...         "domain": "example.com",
        ...     },
        ... )
    """

    # XARF v4.0.0 specification constants
    XARF_VERSION = "4.0.0"

    # Evidence content types by category
    EVIDENCE_CONTENT_TYPES: dict[str, list[str]] = {
        "messaging": ["message/rfc822", "text/plain", "text/html"],
        "connection": ["application/pcap", "text/plain", "application/json"],
        "content": ["image/png", "text/html", "application/pdf"],
        "infrastructure": ["application/pcap", "text/plain", "application/json"],
        "copyright": ["text/html", "image/png", "application/pdf"],
        "vulnerability": ["text/plain", "application/json", "image/png"],
        "reputation": ["application/json", "text/plain", "text/csv"],
    }

    def __init__(self) -> None:
        """Initialize the XARF generator."""

    @property
    def valid_categories(self) -> set[str]:
        """Get valid categories from schema registry.

        Returns:
            Set of valid category names.
        """
        return schema_registry.get_categories()

    def get_types_for_category(self, category: str) -> set[str]:
        """Get valid types for a category from schema registry.

        Args:
            category: The category to get types for.

        Returns:
            Set of valid type names.
        """
        return schema_registry.get_types_for_category(category)

    @property
    def valid_evidence_sources(self) -> set[str]:
        """Get valid evidence sources from schema registry.

        Returns:
            Set of valid evidence source values.
        """
        return schema_registry.get_evidence_sources()

    @property
    def valid_severities(self) -> set[str]:
        """Get valid severity levels from schema registry.

        Returns:
            Set of valid severity values.
        """
        return schema_registry.get_severities()

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

    def generate_hash(self, data: str | bytes, algorithm: str = "sha256") -> str:
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
            return hashlib.sha1(data).hexdigest()  # noqa: S324 - legacy support
        elif algorithm == "md5":
            return hashlib.md5(data).hexdigest()  # noqa: S324 - legacy support
        else:
            raise XARFError(f"Unsupported hash algorithm: {algorithm}")

    def add_evidence(
        self,
        content_type: str,
        description: str,
        payload: str | bytes,
        hash_algorithm: str = "sha256",
    ) -> dict[str, str]:
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

        hash_value = self.generate_hash(payload_bytes, hash_algorithm)
        # v4 format: algorithm:hexvalue
        evidence_hash = f"{hash_algorithm}:{hash_value}"

        return {
            "content_type": content_type,
            "description": description,
            "payload": payload_str,
            "hash": evidence_hash,
        }

    def _validate_contact_info(
        self, contact: dict[str, Any] | None, field_name: str
    ) -> None:
        """Validate contact info structure.

        Args:
            contact: Contact info dict to validate.
            field_name: Name of the field for error messages.

        Raises:
            XARFError: If validation fails.
        """
        if contact is None:
            raise XARFError(f"{field_name} is required")

        required_fields = schema_registry.get_contact_required_fields()
        for field in required_fields:
            if field not in contact or not contact[field]:
                raise XARFError(f"{field_name}.{field} is required")

    def _validate_category_and_type(self, category: str, report_type: str) -> None:
        """Validate category and type against schema.

        Args:
            category: Report category.
            report_type: Report type.

        Raises:
            XARFError: If validation fails.
        """
        valid_categories = self.valid_categories
        if category not in valid_categories:
            raise XARFError(
                f"Invalid category '{category}'. Must be one of: "
                f"{', '.join(sorted(valid_categories))}"
            )

        valid_types = self.get_types_for_category(category)
        if report_type not in valid_types:
            raise XARFError(
                f"Invalid type '{report_type}' for category '{category}'. "
                f"Must be one of: {', '.join(sorted(valid_types))}"
            )

    def _validate_evidence_source(self, evidence_source: str | None) -> None:
        """Validate evidence source if provided.

        Args:
            evidence_source: Evidence source to validate.

        Raises:
            XARFError: If validation fails.
        """
        if evidence_source is None:
            return

        valid_sources = self.valid_evidence_sources
        if valid_sources and evidence_source not in valid_sources:
            raise XARFError(
                f"Invalid evidence_source '{evidence_source}'. Must be one of: "
                f"{', '.join(sorted(valid_sources))}"
            )

    def _validate_confidence(self, confidence: float | None) -> None:
        """Validate confidence score if provided.

        Args:
            confidence: Confidence score to validate.

        Raises:
            XARFError: If validation fails.
        """
        if confidence is not None and not (0.0 <= confidence <= 1.0):
            raise XARFError("confidence must be between 0.0 and 1.0")

    def generate_report(
        self,
        category: str,
        report_type: str,
        source_identifier: str,
        reporter: dict[str, str],
        sender: dict[str, str],
        evidence_source: str | None = None,
        description: str | None = None,
        evidence: list[dict[str, str]] | None = None,
        confidence: float | None = None,
        tags: list[str] | None = None,
        additional_fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate a complete XARF v4.0.0 report.

        Args:
            category: Report category (e.g., "connection", "content").
            report_type: Specific type within category (e.g., "ddos", "phishing").
            source_identifier: Source IP address or identifier.
            reporter: Reporter contact info dict with org, contact, domain.
            sender: Sender contact info dict with org, contact, domain.
            evidence_source: How the evidence was collected (optional, recommended).
            description: Human-readable description of the incident.
            evidence: List of evidence items (dictionaries with content_type,
                     description, payload, and hash).
            confidence: Confidence score between 0.0 and 1.0.
            tags: List of tags for categorization.
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
            ...     reporter={
            ...         "org": "Example Security",
            ...         "contact": "abuse@example.com",
            ...         "domain": "example.com",
            ...     },
            ...     sender={
            ...         "org": "Example Security",
            ...         "contact": "abuse@example.com",
            ...         "domain": "example.com",
            ...     },
            ... )
            >>> report["xarf_version"]
            '4.0.0'
        """
        # Validate required parameters
        if not source_identifier:
            raise XARFError("source_identifier is required")

        # Validate contact info (v4 requires reporter and sender)
        self._validate_contact_info(reporter, "reporter")
        self._validate_contact_info(sender, "sender")

        # Validate category and type against schema
        self._validate_category_and_type(category, report_type)

        # Validate optional fields
        self._validate_evidence_source(evidence_source)
        self._validate_confidence(confidence)

        # Build base report structure (v4 compliant)
        report: dict[str, Any] = {
            "xarf_version": self.XARF_VERSION,
            "report_id": self.generate_uuid(),
            "timestamp": self.generate_timestamp(),
            "reporter": {
                "org": reporter["org"],
                "contact": reporter["contact"],
                "domain": reporter["domain"],
            },
            "sender": {
                "org": sender["org"],
                "contact": sender["contact"],
                "domain": sender["domain"],
            },
            "source_identifier": source_identifier,
            "category": category,
            "type": report_type,
        }

        # Add optional fields only if provided
        if evidence_source:
            report["evidence_source"] = evidence_source

        if description:
            report["description"] = description

        if evidence:
            report["evidence"] = evidence

        if confidence is not None:
            report["confidence"] = confidence

        if tags:
            report["tags"] = tags

        # Add any additional category-specific fields
        if additional_fields:
            report.update(additional_fields)

        return report

    def generate_random_evidence(
        self, category: str, description: str | None = None
    ) -> dict[str, str]:
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

    def _generate_sample_contacts(
        self,
    ) -> tuple[dict[str, str], dict[str, str]]:
        """Generate sample contact info for reporter and sender.

        Returns:
            Tuple of (reporter, sender) contact info dicts.
        """
        sample_orgs = [
            "Security Operations Center",
            "Abuse Response Team",
            "Network Security Team",
            "Threat Intelligence Unit",
            "SOC Team",
        ]
        sample_domains = ["example.com", "security.net", "abuse.org", "soc.io"]

        reporter_org = secrets.choice(sample_orgs)
        sender_org = secrets.choice(sample_orgs)
        reporter_domain = secrets.choice(sample_domains)
        sender_domain = secrets.choice(sample_domains)

        reporter = {
            "org": reporter_org,
            "contact": f"abuse@{reporter_domain}",
            "domain": reporter_domain,
        }

        sender = {
            "org": sender_org,
            "contact": f"report@{sender_domain}",
            "domain": sender_domain,
        }

        return reporter, sender

    def generate_sample_report(
        self,
        category: str,
        report_type: str,
        include_evidence: bool = True,
        include_optional: bool = True,
    ) -> dict[str, Any]:
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
        self._validate_category_and_type(category, report_type)

        # Generate random test data
        source_ip = f"192.0.2.{secrets.randbelow(256)}"
        reporter, sender = self._generate_sample_contacts()

        # Build report parameters
        params: dict[str, Any] = {
            "category": category,
            "report_type": report_type,
            "source_identifier": source_ip,
            "reporter": reporter,
            "sender": sender,
            "description": f"Sample {report_type} report for testing",
        }

        # Add evidence if requested
        if include_evidence:
            params["evidence"] = [self.generate_random_evidence(category)]

        # Add optional fields if requested
        if include_optional:
            severities = list(self.valid_severities)
            if severities:
                params["additional_fields"] = {
                    "severity": secrets.choice(severities),
                }
            params["confidence"] = round(0.7 + secrets.randbelow(30) / 100, 2)
            params["tags"] = [
                f"category:{category}",
                f"type:{report_type}",
                "source:sample",
            ]

        return self.generate_report(**params)
