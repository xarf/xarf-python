# XARF Python Library - Comprehensive Architecture Design

## Executive Summary

The XARF Python library provides a modern, type-safe implementation for parsing, validating, and generating XARF v4 abuse reports. This architecture design aligns with abusix-parsers quality standards while maintaining minimal dependencies and extensibility.

## 1. Package Structure

### 1.1 Rename: xarf-parser → xarf

**Package Name**: `xarf` (PyPI: `xarf`)
**Current**: `xarf-parser` (transitional alpha name)
**Rationale**: Cleaner import syntax, room for future expansion beyond parsing

```
xarf/
├── __init__.py              # Public API surface
├── parser.py                # Parser implementation
├── validator.py             # Validation engine (NEW)
├── generator.py             # Report generation (NEW)
├── models.py                # Pydantic data models
├── exceptions.py            # Exception hierarchy
├── schemas/                 # JSON Schema files (NEW)
│   ├── __init__.py
│   ├── loader.py           # Schema loading/caching
│   ├── v4/                 # XARF v4 schemas
│   │   ├── base.json
│   │   ├── messaging.json
│   │   ├── connection.json
│   │   ├── content.json
│   │   ├── infrastructure.json
│   │   ├── copyright.json
│   │   ├── vulnerability.json
│   │   └── reputation.json
├── utils/                   # Utilities (NEW)
│   ├── __init__.py
│   ├── validators.py       # Field validators (email, IP, URL)
│   ├── encoders.py         # Evidence encoding/decoding
│   └── converters.py       # Type converters
├── constants.py             # Constants and enums (NEW)
└── py.typed                 # PEP 561 type marker (NEW)
```

### 1.2 Module Organization Rationale

- **Separation of Concerns**: Parser, Validator, Generator are distinct responsibilities
- **Schema Co-location**: JSON schemas bundled with package for offline validation
- **Type Safety**: Full type hints with py.typed marker for mypy support
- **Utils Package**: Reusable validators and utilities extracted from core modules

## 2. Core Components

### 2.1 Parser Component (xarf/parser.py)

**Responsibility**: Parse XARF JSON into typed Python objects

```python
class XARFParser:
    """XARF v4 Report Parser.

    Parses XARF JSON reports into strongly-typed Python objects.
    Supports strict and lenient parsing modes.
    """

    def __init__(
        self,
        strict: bool = False,
        validate_schema: bool = True,
        cache_schemas: bool = True
    ):
        """Initialize parser.

        Args:
            strict: Raise exceptions on validation errors
            validate_schema: Perform JSON Schema validation
            cache_schemas: Cache loaded schemas for performance
        """

    def parse(
        self,
        data: Union[str, bytes, dict, Path]
    ) -> XARFReport:
        """Parse XARF report from various input formats."""

    def parse_batch(
        self,
        data: Iterable[Union[str, dict]]
    ) -> Iterator[XARFReport]:
        """Parse multiple reports efficiently."""

    def get_errors(self) -> List[ValidationError]:
        """Get validation errors from last parse (lenient mode)."""
```

**Key Features**:
- Multiple input formats: JSON string, bytes, dict, file path
- Batch parsing with iterator for memory efficiency
- Error accumulation in lenient mode
- Schema validation integration

### 2.2 Validator Component (xarf/validator.py - NEW)

**Responsibility**: Multi-level validation of XARF reports

```python
class XARFValidator:
    """XARF v4 Report Validator.

    Performs comprehensive validation:
    1. JSON Schema validation
    2. Business rule validation
    3. Field-level validation (emails, IPs, URLs)
    4. Cross-field validation
    """

    def __init__(
        self,
        schema_version: str = "4.0.0",
        strict: bool = True
    ):
        """Initialize validator."""

    def validate(
        self,
        report: Union[XARFReport, dict]
    ) -> ValidationResult:
        """Validate a XARF report comprehensively."""

    def validate_schema(self, data: dict) -> ValidationResult:
        """Validate against JSON Schema only."""

    def validate_business_rules(
        self,
        report: XARFReport
    ) -> ValidationResult:
        """Validate class-specific business rules."""

    def validate_evidence(
        self,
        evidence: List[Evidence]
    ) -> ValidationResult:
        """Validate evidence items."""


class ValidationResult:
    """Validation result container."""

    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationWarning]

    def raise_on_error(self) -> None:
        """Raise exception if validation failed."""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
```

**Validation Levels**:
1. **Schema Validation**: JSON Schema compliance
2. **Business Rules**: Class-specific requirements (e.g., email reports need smtp_from)
3. **Field Validation**: Email addresses, IP addresses, URLs, timestamps
4. **Evidence Validation**: Content type matching, size limits, encoding

### 2.3 Generator Component (xarf/generator.py - NEW)

**Responsibility**: Generate XARF reports programmatically

```python
class XARFGenerator:
    """XARF v4 Report Generator.

    Build XARF reports programmatically with validation.
    Provides fluent builder API and direct instantiation.
    """

    @staticmethod
    def create_messaging_report(
        source_ip: str,
        report_type: Literal["spam", "phishing", "social_engineering"],
        **kwargs
    ) -> MessagingReport:
        """Create a messaging class report."""

    @staticmethod
    def create_connection_report(
        source_ip: str,
        destination_ip: str,
        protocol: str,
        report_type: Literal["ddos", "port_scan", "login_attack"],
        **kwargs
    ) -> ConnectionReport:
        """Create a connection class report."""

    @staticmethod
    def create_content_report(
        source_ip: str,
        url: str,
        report_type: Literal["phishing_site", "malware_distribution"],
        **kwargs
    ) -> ContentReport:
        """Create a content class report."""


class ReportBuilder:
    """Fluent builder for XARF reports.

    Example:
        report = (ReportBuilder()
            .set_category("messaging")
            .set_type("spam")
            .set_source("192.0.2.100")
            .set_reporter("Spam Detection", "noreply@example.com", "automated")
            .add_evidence("message/rfc822", "Full email", payload)
            .build())
    """

    def set_category(self, category: str) -> ReportBuilder:
        """Set report category (not 'class')."""

    def set_type(self, type: str) -> ReportBuilder:
        """Set report type."""

    def set_source(self, identifier: str) -> ReportBuilder:
        """Set source identifier."""

    def set_reporter(
        self,
        org: str,
        contact: str,
        type: str
    ) -> ReportBuilder:
        """Set reporter information."""

    def add_evidence(
        self,
        content_type: str,
        description: str,
        payload: str
    ) -> ReportBuilder:
        """Add evidence item."""

    def build(self) -> XARFReport:
        """Build and validate the report."""
```

**Key Features**:
- Factory methods for each report class
- Fluent builder pattern for complex reports
- Automatic field population (report_id, timestamp)
- Validation on build

### 2.4 Models Component (xarf/models.py - ENHANCED)

**Responsibility**: Type-safe data models using Pydantic v2

**CRITICAL**: The field is called `category`, not `class` or `classification`.

```python
# Base Models
class XARFReporter(BaseModel):
    """Reporter information."""
    org: str = Field(..., min_length=1, max_length=255)
    contact: str = Field(..., min_length=1, max_length=255)
    type: Literal["automated", "manual", "hybrid"]

class Evidence(BaseModel):
    """Evidence attachment."""
    content_type: str = Field(..., pattern=r"^[\w-]+/[\w-]+$")
    description: str = Field(..., min_length=1, max_length=1000)
    payload: str = Field(..., description="Base64-encoded evidence")

    @field_validator("payload")
    def validate_base64(cls, v: str) -> str:
        """Validate base64 encoding."""
        # Validation logic

# Base Report
class XARFReport(BaseModel):
    """Base XARF v4 Report.

    All XARF reports inherit from this base class.
    Field name is 'category' not 'class' or 'classification'.
    """

    # Required fields
    xarf_version: str = Field(default="4.0.0", pattern=r"^4\.0\.0$")
    report_id: str = Field(..., description="UUID v4")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reporter: XARFReporter
    source_identifier: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., alias="class")  # IMPORTANT: Use 'category'
    type: str
    evidence_source: Literal[
        "spamtrap", "honeypot", "user_report",
        "automated_scan", "manual_analysis", "vulnerability_scan",
        "researcher_analysis", "threat_intelligence"
    ]

    # Optional fields
    evidence: List[Evidence] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    internal: Optional[dict[str, Any]] = Field(default=None, alias="_internal")

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both 'category' and 'class'
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"  # Strict: no extra fields
    )

    @field_validator("report_id")
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID format."""
        try:
            uuid.UUID(v, version=4)
        except ValueError:
            raise ValueError("report_id must be a valid UUID v4")
        return v

    @field_validator("category")
    def validate_category(cls, v: str) -> str:
        """Validate XARF category."""
        valid = {
            "messaging", "connection", "content",
            "infrastructure", "copyright", "vulnerability", "reputation"
        }
        if v not in valid:
            raise ValueError(f"Invalid category: {v}")
        return v

# Specialized Reports
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

    @model_validator(mode="after")
    def validate_email_fields(self) -> Self:
        """Validate email-specific requirements."""
        if self.protocol == "smtp":
            if not self.smtp_from:
                raise ValueError("smtp_from required for SMTP reports")
            if self.type in ["spam", "phishing"] and not self.subject:
                raise ValueError("subject required for spam/phishing")
        return self

class ConnectionReport(XARFReport):
    """Connection class report."""
    category: Literal["connection"] = "connection"
    type: Literal["ddos", "port_scan", "login_attack", "ip_spoofing"]

    destination_ip: str = Field(..., description="IPv4 or IPv6")
    protocol: str
    destination_port: Optional[int] = Field(None, ge=1, le=65535)
    source_port: Optional[int] = Field(None, ge=1, le=65535)

    @field_validator("destination_ip", "source_identifier")
    def validate_ip(cls, v: str) -> str:
        """Validate IP address format."""
        # Use utils.validators.validate_ip()
        return v

class ContentReport(XARFReport):
    """Content class report."""
    category: Literal["content"] = "content"
    type: Literal[
        "phishing_site", "malware_distribution",
        "defacement", "spamvertised", "web_hack"
    ]

    url: str = Field(..., description="Full URL")

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        # Use utils.validators.validate_url()
        return v
```

## 3. Field Naming: Use "category" (not "class")

**CRITICAL DECISION**: The XARF field is called `category`, not `class` or `classification`.

**Implementation Strategy**:
```python
# In models.py
class XARFReport(BaseModel):
    category: str = Field(..., alias="class")

    model_config = ConfigDict(
        populate_by_name=True  # Accept both 'category' and 'class'
    )

# Python API uses 'category'
report.category  # ✓ Preferred
report.class_    # ✗ Avoid (Python keyword)

# JSON serialization uses 'class'
report.model_dump(by_alias=True)  # → {"class": "messaging", ...}
```

**Rationale**:
- `class` is Python reserved keyword (requires `class_` workaround)
- `category` is more Pythonic and readable
- JSON compatibility via Pydantic aliases
- Aligns with XARF spec which describes it as a category

## 4. Quality Standards (Match abusix-parsers)

### 4.1 Code Quality Metrics

**Target Standards**:
- Test Coverage: ≥ 95%
- Type Coverage: 100% (mypy strict mode)
- Cyclomatic Complexity: ≤ 10 per function
- Documentation: 100% public API documented
- Performance: Parse 1000 reports/sec on standard hardware

### 4.2 Testing Strategy

```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── unit/                    # Unit tests
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_generator.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── test_end_to_end.py
│   └── test_schema_validation.py
├── performance/             # Performance tests
│   ├── test_parsing_speed.py
│   └── test_memory_usage.py
├── fixtures/                # Test data
│   ├── valid/              # Valid XARF reports
│   │   ├── messaging_spam.json
│   │   ├── connection_ddos.json
│   │   └── content_phishing.json
│   └── invalid/            # Invalid reports for error testing
│       ├── missing_fields.json
│       ├── invalid_types.json
│       └── business_rule_violations.json
└── shared/                  # Shared test suite
    ├── samples/            # Official XARF samples
    └── test-definitions/   # Test case definitions
```

**Test Categories**:
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end workflows
3. **Performance Tests**: Speed and memory benchmarks
4. **Conformance Tests**: Official XARF test suite compliance
5. **Property-Based Tests**: Hypothesis for edge cases

**Test Coverage Targets**:
- parser.py: 100%
- validator.py: 100%
- generator.py: 100%
- models.py: 95% (exclude __repr__, etc.)
- utils: 100%

## 5. Dependencies: Minimal, Modern, Secure

### 5.1 Core Dependencies

```toml
[project]
dependencies = [
    "pydantic>=2.5.0,<3.0.0",       # Data validation
    "python-dateutil>=2.8.0",        # Datetime parsing
    "email-validator>=2.1.0",        # Email validation
]
```

**Rationale**:
- **Pydantic v2**: 5-50x faster than v1, better type hints
- **python-dateutil**: Robust datetime parsing
- **email-validator**: RFC-compliant email validation
- **No jsonschema**: Use Pydantic validation instead (removes dependency)

### 5.2 Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-benchmark>=4.0.0",
    "hypothesis>=6.88.0",           # Property-based testing
    "ruff>=0.1.0",                  # Fast linter (replaces flake8, isort)
    "black>=23.11.0",               # Code formatter
    "mypy>=1.7.0",                  # Type checker
    "pre-commit>=3.5.0",            # Git hooks
]
```

## 6. Public API Surface

### 6.1 Top-Level Imports

```python
# xarf/__init__.py
"""XARF v4 Python Library.

Parse, validate, and generate XARF abuse reports.
"""

__version__ = "4.0.0"

# Parser
from .parser import XARFParser

# Validator
from .validator import XARFValidator, ValidationResult

# Generator
from .generator import XARFGenerator, ReportBuilder

# Models
from .models import (
    XARFReport,
    MessagingReport,
    ConnectionReport,
    ContentReport,
    XARFReporter,
    Evidence,
)

# Exceptions
from .exceptions import (
    XARFError,
    XARFParseError,
    XARFValidationError,
    XARFSchemaError,
    XARFGenerationError,
)

__all__ = [
    # Parser
    "XARFParser",
    # Validator
    "XARFValidator",
    "ValidationResult",
    # Generator
    "XARFGenerator",
    "ReportBuilder",
    # Models
    "XARFReport",
    "MessagingReport",
    "ConnectionReport",
    "ContentReport",
    "XARFReporter",
    "Evidence",
    # Exceptions
    "XARFError",
    "XARFParseError",
    "XARFValidationError",
    "XARFSchemaError",
    "XARFGenerationError",
]
```

### 6.2 Usage Examples

**Parse a XARF Report**:
```python
import xarf

# Parse from JSON string
parser = xarf.XARFParser()
report = parser.parse('{"xarf_version": "4.0.0", ...}')

# Access typed fields
print(f"Category: {report.category}")
print(f"Type: {report.type}")
```

**Validate a XARF Report**:
```python
import xarf

validator = xarf.XARFValidator()
result = validator.validate(report)

if result.is_valid:
    print("Report is valid")
else:
    for error in result.errors:
        print(f"Error: {error}")
```

**Generate a XARF Report**:
```python
import xarf

# Using factory method
report = xarf.XARFGenerator.create_messaging_report(
    source_ip="192.0.2.100",
    report_type="spam",
    smtp_from="spammer@example.com",
    subject="Spam Subject",
    reporter={
        "org": "Spam Detection Service",
        "contact": "noreply@example.com",
        "type": "automated"
    }
)

# Using builder
report = (xarf.ReportBuilder()
    .set_category("messaging")
    .set_type("spam")
    .set_source("192.0.2.100")
    .build())
```

## 7. Extension Points

### 7.1 Custom Validators

```python
from xarf.validator import XARFValidator

class CustomValidator(XARFValidator):
    """Custom validator with additional rules."""

    def validate_business_rules(self, report):
        result = super().validate_business_rules(report)
        # Add custom validation
        return result
```

### 7.2 Custom Report Types

```python
from xarf.models import XARFReport

class CustomReport(XARFReport):
    """Custom report type."""
    category: Literal["custom"]
    internal_ticket_id: Optional[str] = None
```

## 8. Architecture Decision Records

### ADR-001: Use Pydantic for Data Models
**Status**: Accepted
**Decision**: Use Pydantic v2 for all data models
**Consequences**: Strong typing, automatic validation, JSON serialization

### ADR-002: Field Name is "category" not "class"
**Status**: Accepted
**Decision**: Use "category" field with "class" alias
**Consequences**: Better Python API, JSON compatibility maintained

### ADR-003: No XARF v3 Converter
**Status**: Accepted
**Decision**: No v3 → v4 converter in this library
**Consequences**: Users must migrate externally, simpler codebase

### ADR-004: Separate Validator Component
**Status**: Accepted
**Decision**: Extract validation to separate component
**Consequences**: Better SRP, reusable validation, clearer code

### ADR-005: Bundle JSON Schemas with Package
**Status**: Accepted
**Decision**: Include schemas in package distribution
**Consequences**: Larger package size, offline capable

### ADR-006: Use Ruff Instead of Flake8
**Status**: Accepted
**Decision**: Adopt Ruff for linting
**Consequences**: 10-100x faster CI, fewer dependencies

## 9. Summary

This architecture provides:

1. **Best Practices**: Matches abusix-parsers quality standards
2. **Type-Safe**: Full type hints with mypy strict mode
3. **Well-Tested**: ≥95% test coverage
4. **Performant**: Optimized for speed and memory
5. **Extensible**: Clear extension points
6. **Secure**: Defense-in-depth security measures
7. **Modern**: Python 3.8+ features and tooling
8. **Documented**: Comprehensive documentation

**Key Design Decisions**:
- Package name: `xarf` (from `xarf-parser`)
- Field name: `category` (not `class`)
- No v3 converter (deprecated format)
- Pydantic v2 for data models
- Separate Parser, Validator, Generator components
- Minimal dependencies

**Implementation Priority**:
1. Core models with 'category' field
2. Enhanced parser with batch support
3. Validator component
4. Generator component with builder pattern
5. Comprehensive test suite
6. Documentation and examples
7. Performance optimization
