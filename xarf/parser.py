"""XARF v4 Parser Implementation."""

import json
from typing import Dict, Any, Union, List
from datetime import datetime

from .models import XARFReport, MessagingReport, ConnectionReport, ContentReport
from .exceptions import XARFError, XARFValidationError, XARFParseError


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
        
        # Supported classes in alpha version
        self.supported_classes = {"messaging", "connection", "content"}
    
    def parse(self, json_data: Union[str, Dict[str, Any]]) -> XARFReport:
        """Parse XARF report from JSON.
        
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
        
        # Validate basic structure
        if not self.validate_structure(data):
            if self.strict:
                raise XARFValidationError("Validation failed", self.errors)
        
        # Parse based on class
        report_class = data.get("class")
        
        if report_class not in self.supported_classes:
            error_msg = f"Unsupported class '{report_class}' in alpha version. Supported: {self.supported_classes}"
            if self.strict:
                raise XARFValidationError(error_msg)
            else:
                self.errors.append(error_msg)
                # Fall back to base model
                return XARFReport(**data)
        
        try:
            if report_class == "messaging":
                return MessagingReport(**data)
            elif report_class == "connection":
                return ConnectionReport(**data) 
            elif report_class == "content":
                return ContentReport(**data)
            else:
                return XARFReport(**data)
                
        except Exception as e:
            raise XARFParseError(f"Failed to parse {report_class} report: {e}")
    
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
            "xarf_version", "report_id", "timestamp", "reporter",
            "source_identifier", "class", "type", "evidence_source"
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
        
        # Class-specific validation
        return self.validate_class_specific(data)
    
    def validate_class_specific(self, data: Dict[str, Any]) -> bool:
        """Validate class-specific requirements.
        
        Args:
            data: Parsed JSON data
            
        Returns:
            bool: True if class-specific validation passes
        """
        report_class = data.get("class")
        report_type = data.get("type")
        
        if report_class == "messaging":
            return self.validate_messaging(data, report_type)
        elif report_class == "connection":
            return self.validate_connection(data, report_type)
        elif report_class == "content":
            return self.validate_content(data, report_type)
        
        return True
    
    def validate_messaging(self, data: Dict[str, Any], report_type: str) -> bool:
        """Validate messaging class reports."""
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
        """Validate connection class reports."""
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
        """Validate content class reports."""
        valid_types = {"phishing_site", "malware_distribution", "defacement", "spamvertised", "web_hack"}
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