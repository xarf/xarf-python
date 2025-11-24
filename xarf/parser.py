"""XARF v4 Parser Implementation."""

import json
from datetime import datetime
from typing import Any, Dict, List, Union

from .exceptions import XARFParseError, XARFValidationError
from .models import ConnectionReport, ContentReport, MessagingReport, XARFReport
from .v3_compat import convert_v3_to_v4, is_v3_report


class XARFParser:
    """XARF v4 Report Parser.

    Parses and validates XARF v4 abuse reports from JSON.
    """

    def __init__(self, strict: bool = False):
        """Initialize parser.

        Args:
            strict: If True, raise exceptions on validation errors.
                   If False, collect errors for later retrieval.
        """
        self.strict = strict
        self.errors: List[str] = []

        # Supported categories in alpha version
        self.supported_categories = {"messaging", "connection", "content"}

    def parse(self, json_data: Union[str, Dict[str, Any]]) -> XARFReport:
        """Parse XARF report from JSON.

        Supports both XARF v4 and v3 (with automatic conversion).

        Args:
            json_data: JSON string or dictionary containing XARF report

        Returns:
            XARFReport: Parsed report object

        Raises:
            XARFParseError: If parsing fails
            XARFValidationError: If validation fails (strict mode)
        """
        self.errors.clear()

        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
        except json.JSONDecodeError as e:
            raise XARFParseError(f"Invalid JSON: {e}")

        # Auto-detect and convert v3 reports
        if is_v3_report(data):
            try:
                data = convert_v3_to_v4(data)
            except Exception as e:
                raise XARFParseError(f"Failed to convert XARF v3 report: {e}")

        # Validate basic structure
        if not self.validate_structure(data):
            if self.strict:
                raise XARFValidationError("Validation failed", self.errors)

        # Parse based on category
        report_category = data.get("category")

        if report_category not in self.supported_categories:
            error_msg = (
                f"Unsupported category '{report_category}' in alpha "
                f"version. Supported: {self.supported_categories}"
            )
            if self.strict:
                raise XARFValidationError(error_msg)
            else:
                self.errors.append(error_msg)
                # Fall back to base model
                return XARFReport(**data)

        try:
            if report_category == "messaging":
                return MessagingReport(**data)
            elif report_category == "connection":
                return ConnectionReport(**data)
            elif report_category == "content":
                return ContentReport(**data)
            else:
                return XARFReport(**data)

        except Exception as e:
            raise XARFParseError(f"Failed to parse {report_category} report: {e}")

    def validate(self, json_data: Union[str, Dict[str, Any]]) -> bool:
        """Validate XARF report without parsing.

        Args:
            json_data: JSON string or dictionary containing XARF report

        Returns:
            bool: True if valid, False otherwise
        """
        self.errors.clear()

        try:
            if isinstance(json_data, str):
                data = json.loads(json_data)
            else:
                data = json_data
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

        return self.validate_structure(data)

    def validate_structure(self, data: Dict[str, Any]) -> bool:
        """Validate basic XARF structure.

        Args:
            data: Parsed JSON data

        Returns:
            bool: True if structure is valid
        """
        required_fields = {
            "xarf_version",
            "report_id",
            "timestamp",
            "reporter",
            "source_identifier",
            "category",
            "type",
            "evidence_source",
        }

        # Check required fields
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            self.errors.append(f"Missing required fields: {missing_fields}")
            return False

        # Check XARF version
        if data.get("xarf_version") != "4.0.0":
            self.errors.append(f"Unsupported XARF version: {data.get('xarf_version')}")
            return False

        # Validate reporter structure
        reporter = data.get("reporter", {})
        if not isinstance(reporter, dict):
            self.errors.append("Reporter must be an object")
            return False

        reporter_required = {"org", "contact", "type"}
        missing_reporter = reporter_required - set(reporter.keys())
        if missing_reporter:
            self.errors.append(f"Missing reporter fields: {missing_reporter}")
            return False

        # Validate reporter type
        if reporter.get("type") not in ["automated", "manual", "hybrid"]:
            self.errors.append(f"Invalid reporter type: {reporter.get('type')}")
            return False

        # Validate timestamp format
        try:
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            self.errors.append(f"Invalid timestamp format: {data.get('timestamp')}")
            return False

        # Category-specific validation
        return self.validate_category_specific(data)

    def validate_category_specific(self, data: Dict[str, Any]) -> bool:
        """Validate category-specific requirements.

        Args:
            data: Parsed JSON data

        Returns:
            bool: True if category-specific validation passes
        """
        report_category = data.get("category")
        report_type = data.get("type")

        if report_category == "messaging":
            return self.validate_messaging(data, report_type or "")
        elif report_category == "connection":
            return self.validate_connection(data, report_type or "")
        elif report_category == "content":
            return self.validate_content(data, report_type or "")

        return True

    def validate_messaging(self, data: Dict[str, Any], report_type: str) -> bool:
        """Validate messaging category reports."""
        valid_types = {"spam", "phishing", "social_engineering"}
        if report_type not in valid_types:
            self.errors.append(f"Invalid messaging type: {report_type}")
            return False

        # Email-specific validation
        if data.get("protocol") == "smtp":
            if not data.get("smtp_from"):
                self.errors.append("smtp_from required for email reports")
                return False
            if report_type in ["spam", "phishing"] and not data.get("subject"):
                self.errors.append("subject required for spam/phishing reports")
                return False

        return True

    def validate_connection(self, data: Dict[str, Any], report_type: str) -> bool:
        """Validate connection category reports."""
        valid_types = {"ddos", "port_scan", "login_attack", "ip_spoofing"}
        if report_type not in valid_types:
            self.errors.append(f"Invalid connection type: {report_type}")
            return False

        # Required fields for connection reports
        if not data.get("destination_ip"):
            self.errors.append("destination_ip required for connection reports")
            return False

        if not data.get("protocol"):
            self.errors.append("protocol required for connection reports")
            return False

        return True

    def validate_content(self, data: Dict[str, Any], report_type: str) -> bool:
        """Validate content category reports."""
        valid_types = {
            "phishing_site",
            "malware_distribution",
            "defacement",
            "spamvertised",
            "web_hack",
        }
        if report_type not in valid_types:
            self.errors.append(f"Invalid content type: {report_type}")
            return False

        # URL required for content reports
        if not data.get("url"):
            self.errors.append("url required for content reports")
            return False

        return True

    def get_errors(self) -> List[str]:
        """Get validation errors from last parse/validate call.

        Returns:
            List[str]: List of validation error messages
        """
        return self.errors.copy()
