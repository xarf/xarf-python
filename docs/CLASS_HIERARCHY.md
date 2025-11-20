# XARF Python Library - Class Hierarchy

## Overview

This document details the complete class hierarchy and relationships in the XARF Python library.

## Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         BaseModel                            │
│                        (Pydantic)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬──────────────────┐
        │              │               │                  │
   ┌────▼────┐   ┌────▼─────┐   ┌───▼────────┐   ┌─────▼──────┐
   │ XARFRe- │   │ Evidence │   │ Validation │   │ XARFReport │
   │ porter  │   │          │   │ Result     │   │   (Base)   │
   └─────────┘   └──────────┘   └────────────┘   └─────┬──────┘
                                                         │
                      ┌──────────────────────────────────┼──────────────────┬────────────────┐
                      │                                  │                  │                │
               ┌──────▼──────────┐             ┌────────▼──────────┐      │                │
               │ MessagingReport │             │ ConnectionReport  │      │                │
               └─────────────────┘             └───────────────────┘      │                │
                                                                           │                │
               ┌───────────────────────────────────────────────────────┐  │                │
               │                                                       │  │                │
        ┌──────▼──────────┐  ┌──────────────────┐  ┌────────────────▼──▼────┐  ┌──────────▼─────────┐
        │  ContentReport  │  │Infrastructure    │  │ CopyrightReport         │  │ Vulnerability      │
        │                 │  │    Report        │  │                         │  │     Report         │
        └─────────────────┘  └──────────────────┘  └─────────────────────────┘  └────────────────────┘
                                                                                           │
                                                                              ┌────────────▼────────────┐
                                                                              │   ReputationReport      │
                                                                              └─────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        Exception                             │
│                        (Built-in)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                ┌──────▼──────┐
                │  XARFError  │
                │   (Base)    │
                └──────┬──────┘
                       │
      ┌────────────────┼────────────────┬────────────────┬───────────────┐
      │                │                │                │               │
┌─────▼──────────┐ ┌──▼──────────┐ ┌───▼──────────┐ ┌───▼──────────┐ ┌─▼──────────────┐
│ XARFParseError │ │ XARFValida- │ │ XARFSchema   │ │ XARFGenera-  │ │ XARFTypeError  │
│                │ │ tionError   │ │    Error     │ │ tionError    │ │                │
└────────────────┘ └─────────────┘ └──────────────┘ └──────────────┘ └────────────────┘
```

## Core Classes

### 1. Data Models

#### XARFReport (Base Class)

```python
class XARFReport(BaseModel):
    """Base XARF v4 Report.

    All XARF reports inherit from this base class.
    Provides common fields required by all report types.
    """

    # Required fields
    xarf_version: str
    report_id: str
    timestamp: datetime
    reporter: XARFReporter
    source_identifier: str
    category: str  # Aliased as "class" in JSON
    type: str
    evidence_source: str

    # Optional fields
    evidence: List[Evidence]
    tags: List[str]
    internal: Optional[dict[str, Any]]
```

**Inheritance Hierarchy**:
- BaseModel (Pydantic)
  - XARFReport
    - MessagingReport
    - ConnectionReport
    - ContentReport
    - InfrastructureReport
    - CopyrightReport
    - VulnerabilityReport
    - ReputationReport

#### MessagingReport

```python
class MessagingReport(XARFReport):
    """Messaging class report (spam, phishing, social engineering)."""

    category: Literal["messaging"] = "messaging"
    type: Literal["spam", "phishing", "social_engineering"]

    # Email-specific fields
    protocol: Optional[str]
    smtp_from: Optional[str]
    smtp_to: Optional[str]
    subject: Optional[str]
    message_id: Optional[str]
    sender_display_name: Optional[str]
```

**Specializations**:
- Validates email-specific requirements
- Enforces SMTP field requirements for email reports
- Subject required for spam/phishing types

#### ConnectionReport

```python
class ConnectionReport(XARFReport):
    """Connection class report (DDoS, port scans, login attacks)."""

    category: Literal["connection"] = "connection"
    type: Literal["ddos", "port_scan", "login_attack", "ip_spoofing"]

    # Required connection fields
    destination_ip: str
    protocol: str

    # Optional fields
    destination_port: Optional[int]
    source_port: Optional[int]
    packet_count: Optional[int]
    byte_count: Optional[int]
```

**Specializations**:
- Validates IP address formats
- Enforces port number ranges (1-65535)
- Validates protocol specifications

#### ContentReport

```python
class ContentReport(XARFReport):
    """Content class report (phishing sites, malware, defacement)."""

    category: Literal["content"] = "content"
    type: Literal["phishing_site", "malware_distribution",
                  "defacement", "spamvertised", "web_hack"]

    # Required content fields
    url: str

    # Optional fields
    content_type: Optional[str]
    affected_pages: Optional[List[str]]
    cms_platform: Optional[str]
```

**Specializations**:
- Validates URL formats
- Enforces URL scheme requirements
- Validates affected pages list

### 2. Supporting Models

#### XARFReporter

```python
class XARFReporter(BaseModel):
    """Reporter information for XARF reports."""

    org: str
    contact: str
    type: Literal["automated", "manual", "hybrid"]
```

**Usage**: Embedded in all XARFReport instances to identify reporter.

#### Evidence

```python
class Evidence(BaseModel):
    """Evidence attachment for XARF reports."""

    content_type: str
    description: str
    payload: str  # Base64-encoded
```

**Usage**: Embedded in XARFReport evidence list.

### 3. Validation Classes

#### ValidationResult

```python
class ValidationResult:
    """Container for validation results."""

    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]

    def raise_on_error(self) -> None:
        """Raise exception if validation failed."""

    def to_dict(self) -> dict:
        """Convert to dictionary."""
```

**Usage**: Returned by XARFValidator methods.

### 4. Exception Classes

#### XARFError (Base Exception)

```python
class XARFError(Exception):
    """Base exception for all XARF errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details

    def to_dict(self) -> dict:
        """Convert to dictionary for structured logging."""
```

**Exception Hierarchy**:
- Exception (Built-in)
  - XARFError
    - XARFParseError
    - XARFValidationError
    - XARFSchemaError
    - XARFGenerationError
    - XARFTypeError

#### XARFParseError

```python
class XARFParseError(XARFError):
    """Raised when parsing fails."""
```

**When Raised**:
- Invalid JSON syntax
- Cannot decode input
- Unexpected data format

#### XARFValidationError

```python
class XARFValidationError(XARFError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        errors: Optional[List[dict]] = None,
        warnings: Optional[List[dict]] = None
    ):
        super().__init__(message)
        self.errors = errors or []
        self.warnings = warnings or []
```

**When Raised**:
- Schema validation failure
- Business rule violation
- Field validation failure

#### XARFSchemaError

```python
class XARFSchemaError(XARFError):
    """Raised when schema operations fail."""
```

**When Raised**:
- Schema file not found
- Invalid schema format
- Schema loading failure

#### XARFGenerationError

```python
class XARFGenerationError(XARFError):
    """Raised when report generation fails."""
```

**When Raised**:
- Missing required fields
- Invalid field values
- Builder validation failure

## Service Classes

### 1. XARFParser

```python
class XARFParser:
    """XARF v4 Report Parser."""

    def __init__(
        self,
        strict: bool = False,
        validate_schema: bool = True,
        cache_schemas: bool = True
    ):
        self.strict = strict
        self.validate_schema = validate_schema
        self._schema_cache = {} if cache_schemas else None
        self.errors: List[str] = []

    def parse(self, data: Union[str, bytes, dict, Path]) -> XARFReport:
        """Parse XARF report."""

    def parse_batch(self, data: Iterable) -> Iterator[XARFReport]:
        """Parse multiple reports."""

    def get_errors(self) -> List[ValidationError]:
        """Get validation errors."""
```

**Responsibilities**:
- Parse JSON to Python objects
- Instantiate appropriate report subclass
- Handle multiple input formats
- Coordinate with validator

### 2. XARFValidator

```python
class XARFValidator:
    """XARF v4 Report Validator."""

    def __init__(
        self,
        schema_version: str = "4.0.0",
        strict: bool = True
    ):
        self.schema_version = schema_version
        self.strict = strict
        self._schema_loader = SchemaLoader()

    def validate(self, report: Union[XARFReport, dict]) -> ValidationResult:
        """Validate a XARF report comprehensively."""

    def validate_schema(self, data: dict) -> ValidationResult:
        """Validate against JSON Schema."""

    def validate_business_rules(self, report: XARFReport) -> ValidationResult:
        """Validate class-specific business rules."""

    def validate_evidence(self, evidence: List[Evidence]) -> ValidationResult:
        """Validate evidence items."""
```

**Responsibilities**:
- Schema validation
- Business rule validation
- Field validation
- Evidence validation

### 3. XARFGenerator

```python
class XARFGenerator:
    """XARF v4 Report Generator."""

    @staticmethod
    def create_messaging_report(**kwargs) -> MessagingReport:
        """Create messaging report."""

    @staticmethod
    def create_connection_report(**kwargs) -> ConnectionReport:
        """Create connection report."""

    @staticmethod
    def create_content_report(**kwargs) -> ContentReport:
        """Create content report."""
```

**Responsibilities**:
- Factory methods for report creation
- Automatic field population
- Validation on creation

### 4. ReportBuilder

```python
class ReportBuilder:
    """Fluent builder for XARF reports."""

    def __init__(self):
        self._data = {}

    def set_category(self, category: str) -> ReportBuilder:
        """Set report category."""
        return self

    def set_type(self, type: str) -> ReportBuilder:
        """Set report type."""
        return self

    def set_source(self, identifier: str) -> ReportBuilder:
        """Set source identifier."""
        return self

    def build(self) -> XARFReport:
        """Build and validate report."""
```

**Responsibilities**:
- Fluent interface for report construction
- Incremental report building
- Validation on build

## Relationships

### Composition

- XARFReport **contains** XARFReporter (1:1)
- XARFReport **contains** Evidence (1:many)

### Inheritance

- All report types **inherit from** XARFReport
- All exceptions **inherit from** XARFError
- All models **inherit from** BaseModel (Pydantic)

### Dependencies

- XARFParser **depends on** XARFValidator
- XARFParser **creates** XARFReport subclasses
- XARFValidator **validates** XARFReport instances
- XARFGenerator **creates** XARFReport instances
- ReportBuilder **creates** XARFReport instances

## Design Patterns

### 1. Factory Pattern

**XARFGenerator** implements the Factory pattern:
```python
report = XARFGenerator.create_messaging_report(...)
```

### 2. Builder Pattern

**ReportBuilder** implements the Builder pattern:
```python
report = (ReportBuilder()
    .set_category("messaging")
    .set_type("spam")
    .build())
```

### 3. Template Method Pattern

**XARFReport** base class defines template:
- Subclasses override validation methods
- Base class provides common validation

### 4. Strategy Pattern

**Validation** uses Strategy pattern:
- Different validation strategies for each report class
- Pluggable validators for extension

## Type System

### Type Annotations

All classes use modern Python type hints:

```python
from typing import Union, Optional, List, Literal, Iterator
from pathlib import Path
from datetime import datetime

# Type aliases
ReportType = Union[
    MessagingReport,
    ConnectionReport,
    ContentReport,
    InfrastructureReport,
    CopyrightReport,
    VulnerabilityReport,
    ReputationReport
]

InputFormat = Union[str, bytes, dict, Path]
```

### Generic Types

Pydantic models support generic typing:

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    success: bool
    data: T
    errors: List[str]

# Usage
def parse_with_metadata(data: str) -> Response[XARFReport]:
    """Parse and return report with metadata."""
```

## Extension Points

### Custom Report Classes

```python
from xarf.models import XARFReport

class CustomReport(XARFReport):
    """Custom organization-specific report."""
    category: Literal["custom"]
    custom_field: str
```

### Custom Validators

```python
from xarf.validator import XARFValidator

class CustomValidator(XARFValidator):
    """Custom validation logic."""

    def validate_business_rules(self, report: XARFReport) -> ValidationResult:
        result = super().validate_business_rules(report)
        # Add custom validation
        return result
```

### Custom Evidence Types

```python
from xarf.models import Evidence

class EnhancedEvidence(Evidence):
    """Enhanced evidence with additional metadata."""
    source_url: Optional[str] = None
    captured_at: Optional[datetime] = None
```

## Summary

The XARF Python library uses a clean class hierarchy with:

1. **Inheritance** for report type specialization
2. **Composition** for embedded objects (Reporter, Evidence)
3. **Separation of Concerns** between parsing, validation, generation
4. **Type Safety** with Pydantic models and type hints
5. **Extensibility** through well-defined extension points
6. **Design Patterns** for common use cases

This architecture provides a solid, maintainable foundation for XARF report processing.
