# XARF Python Library - Public API Surface

## Overview

This document defines the complete public API surface of the XARF Python library. Only items listed here are considered part of the stable public API and subject to semantic versioning guarantees.

## Top-Level Package: `xarf`

### Version Information

```python
import xarf

xarf.__version__  # str: Current version (e.g., "4.0.0")
xarf.__author__   # str: "XARF Project"
```

## Parser Module: `xarf.parser`

### XARFParser

```python
from xarf import XARFParser

class XARFParser:
    """XARF v4 Report Parser."""

    def __init__(
        self,
        strict: bool = False,
        validate_schema: bool = True,
        cache_schemas: bool = True
    ) -> None:
        """Initialize parser.

        Args:
            strict: If True, raise exceptions on validation errors.
                   If False, collect errors for later retrieval.
            validate_schema: If True, perform JSON Schema validation.
            cache_schemas: If True, cache loaded schemas for performance.
        """

    def parse(
        self,
        data: Union[str, bytes, dict, Path]
    ) -> XARFReport:
        """Parse XARF report from various input formats.

        Args:
            data: XARF report data. Can be:
                - JSON string
                - UTF-8 encoded bytes
                - Python dictionary
                - Path to JSON file

        Returns:
            XARFReport: Parsed report (subclass based on category).

        Raises:
            XARFParseError: If parsing fails.
            XARFValidationError: If validation fails (strict mode only).
        """

    def parse_batch(
        self,
        data: Iterable[Union[str, dict]]
    ) -> Iterator[XARFReport]:
        """Parse multiple reports efficiently.

        Args:
            data: Iterable of XARF reports (strings or dicts).

        Yields:
            XARFReport: Parsed reports.

        Raises:
            XARFParseError: If parsing fails.
            XARFValidationError: If validation fails (strict mode only).
        """

    def get_errors(self) -> List[str]:
        """Get validation errors from last parse/validate call.

        Only populated in lenient mode (strict=False).

        Returns:
            List[str]: List of validation error messages.
        """
```

**Usage Examples**:

```python
# Parse from JSON string
parser = XARFParser()
report = parser.parse('{"xarf_version": "4.0.0", ...}')

# Parse from file
from pathlib import Path
report = parser.parse(Path("report.json"))

# Parse from dictionary
data = {"xarf_version": "4.0.0", ...}
report = parser.parse(data)

# Batch parsing
reports = parser.parse_batch([report1_json, report2_json, ...])
for report in reports:
    print(report.category)

# Lenient mode
parser = XARFParser(strict=False)
report = parser.parse(invalid_json)
if parser.get_errors():
    print("Validation errors:", parser.get_errors())
```

## Validator Module: `xarf.validator`

### XARFValidator

```python
from xarf import XARFValidator

class XARFValidator:
    """XARF v4 Report Validator."""

    def __init__(
        self,
        schema_version: str = "4.0.0",
        strict: bool = True
    ) -> None:
        """Initialize validator.

        Args:
            schema_version: XARF schema version to validate against.
            strict: If True, fail on any validation error.
                   If False, continue and collect all errors.
        """

    def validate(
        self,
        report: Union[XARFReport, dict]
    ) -> ValidationResult:
        """Validate a XARF report comprehensively.

        Performs all validation levels:
        - JSON Schema validation
        - Business rule validation
        - Field-level validation
        - Evidence validation

        Args:
            report: XARF report to validate (object or dict).

        Returns:
            ValidationResult: Validation results with errors/warnings.
        """

    def validate_schema(self, data: dict) -> ValidationResult:
        """Validate against JSON Schema only.

        Args:
            data: Report data as dictionary.

        Returns:
            ValidationResult: Schema validation results.
        """

    def validate_business_rules(
        self,
        report: XARFReport
    ) -> ValidationResult:
        """Validate class-specific business rules.

        Args:
            report: Parsed XARF report.

        Returns:
            ValidationResult: Business rule validation results.
        """

    def validate_evidence(
        self,
        evidence: List[Evidence]
    ) -> ValidationResult:
        """Validate evidence items.

        Args:
            evidence: List of evidence objects.

        Returns:
            ValidationResult: Evidence validation results.
        """
```

### ValidationResult

```python
from xarf import ValidationResult

class ValidationResult:
    """Container for validation results."""

    is_valid: bool
    """True if validation passed, False otherwise."""

    errors: List[dict]
    """List of validation errors."""

    warnings: List[dict]
    """List of validation warnings (non-fatal)."""

    def raise_on_error(self) -> None:
        """Raise XARFValidationError if validation failed.

        Raises:
            XARFValidationError: If is_valid is False.
        """

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Returns:
            dict: Dictionary representation of validation result.
        """
```

**Usage Examples**:

```python
# Validate parsed report
validator = XARFValidator()
result = validator.validate(report)

if result.is_valid:
    print("Report is valid")
else:
    for error in result.errors:
        print(f"Error: {error}")
    for warning in result.warnings:
        print(f"Warning: {warning}")

# Validate and raise exception
result = validator.validate(report)
result.raise_on_error()  # Raises if invalid

# Schema validation only
result = validator.validate_schema(report_dict)
```

## Generator Module: `xarf.generator`

### XARFGenerator

```python
from xarf import XARFGenerator

class XARFGenerator:
    """XARF v4 Report Generator."""

    @staticmethod
    def create_messaging_report(
        source_ip: str,
        report_type: Literal["spam", "phishing", "social_engineering"],
        reporter: dict,
        evidence_source: str,
        **kwargs
    ) -> MessagingReport:
        """Create a messaging class report.

        Args:
            source_ip: Source IP address or identifier.
            report_type: Type of messaging abuse.
            reporter: Reporter information dict with keys:
                - org: Organization name
                - contact: Contact email
                - type: Reporter type ("automated", "manual", "hybrid")
            evidence_source: Evidence source type.
            **kwargs: Additional fields (smtp_from, subject, etc.)

        Returns:
            MessagingReport: Created and validated report.

        Raises:
            XARFGenerationError: If required fields missing or invalid.
        """

    @staticmethod
    def create_connection_report(
        source_ip: str,
        destination_ip: str,
        protocol: str,
        report_type: Literal["ddos", "port_scan", "login_attack", "ip_spoofing"],
        reporter: dict,
        evidence_source: str,
        **kwargs
    ) -> ConnectionReport:
        """Create a connection class report.

        Args:
            source_ip: Source IP address.
            destination_ip: Destination IP address.
            protocol: Network protocol (tcp, udp, etc.)
            report_type: Type of connection abuse.
            reporter: Reporter information dict.
            evidence_source: Evidence source type.
            **kwargs: Additional fields (ports, packet_count, etc.)

        Returns:
            ConnectionReport: Created and validated report.

        Raises:
            XARFGenerationError: If required fields missing or invalid.
        """

    @staticmethod
    def create_content_report(
        source_ip: str,
        url: str,
        report_type: Literal[
            "phishing_site", "malware_distribution",
            "defacement", "spamvertised", "web_hack"
        ],
        reporter: dict,
        evidence_source: str,
        **kwargs
    ) -> ContentReport:
        """Create a content class report.

        Args:
            source_ip: Source IP address or identifier.
            url: URL of abusive content.
            report_type: Type of content abuse.
            reporter: Reporter information dict.
            evidence_source: Evidence source type.
            **kwargs: Additional fields (content_type, cms_platform, etc.)

        Returns:
            ContentReport: Created and validated report.

        Raises:
            XARFGenerationError: If required fields missing or invalid.
        """
```

### ReportBuilder

```python
from xarf import ReportBuilder

class ReportBuilder:
    """Fluent builder for XARF reports."""

    def __init__(self) -> None:
        """Initialize report builder."""

    def set_category(self, category: str) -> ReportBuilder:
        """Set report category.

        Args:
            category: Report category (messaging, connection, etc.)

        Returns:
            ReportBuilder: Self for method chaining.
        """

    def set_type(self, type: str) -> ReportBuilder:
        """Set report type.

        Args:
            type: Report type (spam, ddos, etc.)

        Returns:
            ReportBuilder: Self for method chaining.
        """

    def set_source(self, identifier: str) -> ReportBuilder:
        """Set source identifier.

        Args:
            identifier: Source IP or other identifier.

        Returns:
            ReportBuilder: Self for method chaining.
        """

    def set_reporter(
        self,
        org: str,
        contact: str,
        type: str
    ) -> ReportBuilder:
        """Set reporter information.

        Args:
            org: Organization name.
            contact: Contact email.
            type: Reporter type (automated, manual, hybrid).

        Returns:
            ReportBuilder: Self for method chaining.
        """

    def add_evidence(
        self,
        content_type: str,
        description: str,
        payload: str
    ) -> ReportBuilder:
        """Add evidence item.

        Args:
            content_type: MIME type of evidence.
            description: Evidence description.
            payload: Base64-encoded evidence data.

        Returns:
            ReportBuilder: Self for method chaining.
        """

    def add_tag(self, tag: str) -> ReportBuilder:
        """Add tag to report.

        Args:
            tag: Tag string.

        Returns:
            ReportBuilder: Self for method chaining.
        """

    def build(self) -> XARFReport:
        """Build and validate the report.

        Returns:
            XARFReport: Created report (type based on category).

        Raises:
            XARFGenerationError: If required fields missing or invalid.
        """
```

**Usage Examples**:

```python
# Using factory methods
report = XARFGenerator.create_messaging_report(
    source_ip="192.0.2.100",
    report_type="spam",
    reporter={
        "org": "Spam Detection Service",
        "contact": "noreply@example.com",
        "type": "automated"
    },
    evidence_source="spamtrap",
    smtp_from="spammer@bad.example",
    subject="Spam Subject"
)

# Using builder pattern
report = (ReportBuilder()
    .set_category("messaging")
    .set_type("spam")
    .set_source("192.0.2.100")
    .set_reporter("My Org", "noreply@example.com", "automated")
    .add_evidence("message/rfc822", "Full email", base64_payload)
    .add_tag("spam:bulk")
    .build())
```

## Models Module: `xarf.models`

### XARFReport (Base)

```python
from xarf import XARFReport

class XARFReport(BaseModel):
    """Base XARF v4 Report."""

    # Required fields
    xarf_version: str
    report_id: str
    timestamp: datetime
    reporter: XARFReporter
    source_identifier: str
    category: str  # Use 'category' in Python, 'class' in JSON
    type: str
    evidence_source: str

    # Optional fields
    evidence: List[Evidence] = []
    tags: List[str] = []
    internal: Optional[dict[str, Any]] = None

    # Pydantic methods
    model_dump(
        self,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
        **kwargs
    ) -> dict:
        """Convert to dictionary.

        Args:
            by_alias: Use field aliases (e.g., 'class' instead of 'category').
            exclude_none: Exclude None values.

        Returns:
            dict: Dictionary representation.
        """

    model_dump_json(
        self,
        *,
        by_alias: bool = False,
        exclude_none: bool = False,
        **kwargs
    ) -> str:
        """Convert to JSON string.

        Args:
            by_alias: Use field aliases.
            exclude_none: Exclude None values.

        Returns:
            str: JSON representation.
        """
```

### MessagingReport

```python
from xarf import MessagingReport

class MessagingReport(XARFReport):
    """Messaging class report."""

    category: Literal["messaging"] = "messaging"
    type: Literal["spam", "phishing", "social_engineering"]

    # Email-specific fields
    protocol: Optional[str] = None
    smtp_from: Optional[str] = None
    smtp_to: Optional[str] = None
    subject: Optional[str] = None
    message_id: Optional[str] = None
    sender_display_name: Optional[str] = None
```

### ConnectionReport

```python
from xarf import ConnectionReport

class ConnectionReport(XARFReport):
    """Connection class report."""

    category: Literal["connection"] = "connection"
    type: Literal["ddos", "port_scan", "login_attack", "ip_spoofing"]

    # Required
    destination_ip: str
    protocol: str

    # Optional
    destination_port: Optional[int] = None
    source_port: Optional[int] = None
    packet_count: Optional[int] = None
    byte_count: Optional[int] = None
```

### ContentReport

```python
from xarf import ContentReport

class ContentReport(XARFReport):
    """Content class report."""

    category: Literal["content"] = "content"
    type: Literal[
        "phishing_site", "malware_distribution",
        "defacement", "spamvertised", "web_hack"
    ]

    # Required
    url: str

    # Optional
    content_type: Optional[str] = None
    affected_pages: Optional[List[str]] = None
    cms_platform: Optional[str] = None
```

### XARFReporter

```python
from xarf import XARFReporter

class XARFReporter(BaseModel):
    """Reporter information."""

    org: str
    contact: str
    type: Literal["automated", "manual", "hybrid"]
```

### Evidence

```python
from xarf import Evidence

class Evidence(BaseModel):
    """Evidence attachment."""

    content_type: str
    description: str
    payload: str  # Base64-encoded
```

**Usage Examples**:

```python
# Access report fields
report: MessagingReport = parser.parse(data)
print(report.category)  # "messaging"
print(report.type)  # "spam"
print(report.smtp_from)  # "spammer@example.com"

# Export to JSON
json_output = report.model_dump_json(by_alias=True, exclude_none=True)

# Export to dict
dict_output = report.model_dump(by_alias=True)

# Access nested fields
print(report.reporter.org)
print(report.evidence[0].content_type)
```

## Exceptions Module: `xarf.exceptions`

### XARFError

```python
from xarf import XARFError

class XARFError(Exception):
    """Base exception for all XARF errors."""

    message: str
    details: dict

    def to_dict(self) -> dict:
        """Convert to dictionary for structured logging."""
```

### XARFParseError

```python
from xarf import XARFParseError

class XARFParseError(XARFError):
    """Raised when parsing fails."""
```

### XARFValidationError

```python
from xarf import XARFValidationError

class XARFValidationError(XARFError):
    """Raised when validation fails."""

    errors: List[dict]
    warnings: List[dict]
```

### XARFSchemaError

```python
from xarf import XARFSchemaError

class XARFSchemaError(XARFError):
    """Raised when schema operations fail."""
```

### XARFGenerationError

```python
from xarf import XARFGenerationError

class XARFGenerationError(XARFError):
    """Raised when report generation fails."""
```

**Usage Examples**:

```python
try:
    report = parser.parse(invalid_json)
except XARFParseError as e:
    print(f"Parse error: {e.message}")
    print(f"Details: {e.details}")

try:
    report = parser.parse(invalid_report)
except XARFValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  - {error}")
```

## Complete Import Example

```python
# All public API imports
from xarf import (
    # Parser
    XARFParser,

    # Validator
    XARFValidator,
    ValidationResult,

    # Generator
    XARFGenerator,
    ReportBuilder,

    # Models
    XARFReport,
    MessagingReport,
    ConnectionReport,
    ContentReport,
    XARFReporter,
    Evidence,

    # Exceptions
    XARFError,
    XARFParseError,
    XARFValidationError,
    XARFSchemaError,
    XARFGenerationError,
)
```

## Stability Guarantees

### Semantic Versioning

- **Major version (4.x.x → 5.x.x)**: Breaking changes allowed
- **Minor version (4.0.x → 4.1.x)**: New features, backward compatible
- **Patch version (4.0.0 → 4.0.1)**: Bug fixes only, fully compatible

### Deprecation Policy

1. Features marked deprecated in minor release
2. Deprecation warnings issued for 6+ months
3. Removed in next major release
4. Migration guide provided

### Experimental Features

Features marked with `@experimental` decorator are not subject to stability guarantees:

```python
@experimental
def advanced_feature():
    """This feature may change without notice."""
```

## Summary

The XARF Python library public API consists of:

- **3 service classes**: XARFParser, XARFValidator, XARFGenerator
- **1 builder class**: ReportBuilder
- **7+ data model classes**: XARFReport and subclasses
- **5 exception classes**: XARFError and subclasses
- **1 result class**: ValidationResult

All public API items are exported from the top-level `xarf` package for convenient importing.
