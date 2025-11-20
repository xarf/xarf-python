# XARF Python Library - Architecture Summary

## Quick Reference

This document provides a quick reference to the complete architecture design for implementation teams.

## Key Design Decisions

### 1. Package Rename
- **From**: `xarf-parser`
- **To**: `xarf`
- **Why**: Cleaner imports, broader scope beyond parsing

### 2. Field Naming
- **Python API**: Use `category` (not `class_`)
- **JSON Output**: Use `class` (via Pydantic alias)
- **Why**: `class` is Python keyword, `category` is more Pythonic

### 3. No v3 Converter
- **Decision**: No XARF v3 to v4 converter in this library
- **Why**: v3 is deprecated, simpler codebase, users migrate externally

## Module Structure

```
xarf/
├── parser.py          # XARFParser - Parse JSON to objects
├── validator.py       # XARFValidator - Multi-level validation (NEW)
├── generator.py       # XARFGenerator - Create reports (NEW)
├── models.py          # Pydantic data models
├── exceptions.py      # Exception hierarchy
├── constants.py       # Constants and enums (NEW)
├── schemas/           # JSON Schema files (NEW)
│   ├── loader.py
│   └── v4/*.json
├── utils/             # Utilities (NEW)
│   ├── validators.py
│   ├── encoders.py
│   └── converters.py
└── py.typed           # Type hint marker (NEW)
```

## Core Components

### Parser (xarf/parser.py)
```python
parser = XARFParser(strict=False, validate_schema=True)
report = parser.parse(json_string)  # or dict, bytes, Path
reports = parser.parse_batch(iterable)  # Batch processing
errors = parser.get_errors()  # Get validation errors
```

### Validator (xarf/validator.py - NEW)
```python
validator = XARFValidator(schema_version="4.0.0")
result = validator.validate(report)  # Full validation
result = validator.validate_schema(dict_data)  # Schema only
result = validator.validate_business_rules(report)  # Business rules
```

### Generator (xarf/generator.py - NEW)
```python
# Factory method
report = XARFGenerator.create_messaging_report(
    source_ip="192.0.2.100",
    report_type="spam",
    reporter={...}
)

# Builder pattern
report = (ReportBuilder()
    .set_category("messaging")
    .set_type("spam")
    .build())
```

## Data Models

### Hierarchy
```
BaseModel (Pydantic)
└── XARFReport (base)
    ├── MessagingReport
    ├── ConnectionReport
    ├── ContentReport
    ├── InfrastructureReport (future)
    ├── CopyrightReport (future)
    ├── VulnerabilityReport (future)
    └── ReputationReport (future)
```

### Base Report Fields
```python
class XARFReport(BaseModel):
    # Required
    xarf_version: str = "4.0.0"
    report_id: str  # UUID v4
    timestamp: datetime
    reporter: XARFReporter
    source_identifier: str
    category: str  # Aliased as "class" in JSON
    type: str
    evidence_source: str

    # Optional
    evidence: List[Evidence] = []
    tags: List[str] = []
    internal: Optional[dict] = None
```

### Specialized Reports

**MessagingReport**:
- Types: `spam`, `phishing`, `social_engineering`
- Required: `smtp_from` (for SMTP), `subject` (for spam/phishing)

**ConnectionReport**:
- Types: `ddos`, `port_scan`, `login_attack`, `ip_spoofing`
- Required: `destination_ip`, `protocol`

**ContentReport**:
- Types: `phishing_site`, `malware_distribution`, `defacement`, `spamvertised`, `web_hack`
- Required: `url`

## Quality Standards

### Testing
- **Coverage**: ≥95% overall, 100% for core modules
- **Types**: Unit, integration, performance, conformance, property-based
- **Frameworks**: pytest, pytest-cov, hypothesis

### Type Safety
- **Type Hints**: 100% coverage on public API
- **Type Checker**: mypy strict mode
- **Marker**: py.typed file for PEP 561

### Performance
- **Parse Speed**: 1000+ reports/sec
- **Memory**: <10KB per report
- **Concurrency**: Thread-safe, linear scaling

### Code Quality
- **Linter**: Ruff (replaces flake8, isort)
- **Formatter**: Black (88 char line length)
- **Complexity**: ≤10 cyclomatic complexity per function

## Dependencies

### Core (Minimal)
```toml
dependencies = [
    "pydantic>=2.5.0,<3.0.0",
    "python-dateutil>=2.8.0",
    "email-validator>=2.1.0",
]
```

### Development
```toml
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "hypothesis>=6.88.0",
    "ruff>=0.1.0",
    "black>=23.11.0",
    "mypy>=1.7.0",
]
```

## Public API

### Imports
```python
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

## Usage Examples

### Parse Report
```python
parser = XARFParser()
report = parser.parse('{"xarf_version": "4.0.0", ...}')
print(f"Category: {report.category}")
print(f"Type: {report.type}")
```

### Validate Report
```python
validator = XARFValidator()
result = validator.validate(report)
if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error}")
```

### Generate Report
```python
report = XARFGenerator.create_messaging_report(
    source_ip="192.0.2.100",
    report_type="spam",
    reporter={"org": "My Org", "contact": "me@example.com", "type": "automated"},
    evidence_source="spamtrap",
    smtp_from="spammer@bad.example"
)

json_output = report.model_dump_json(by_alias=True, exclude_none=True)
```

## Implementation Priority

### Phase 1: Core Foundation
1. Update models.py with `category` field
2. Enhance parser.py with batch support
3. Update exceptions.py with enhanced hierarchy
4. Create constants.py for enums

### Phase 2: New Components
5. Create validator.py (extract from parser)
6. Create generator.py with factory methods
7. Create utils/ package with validators
8. Bundle schemas/ in package

### Phase 3: Quality
9. Comprehensive test suite (≥95% coverage)
10. Type hints on all public API
11. Documentation and examples
12. Performance optimization

### Phase 4: Polish
13. CLI tool (optional)
14. Integration examples
15. Migration guide
16. Release preparation

## Extension Points

### Custom Validators
```python
class CustomValidator(XARFValidator):
    def validate_business_rules(self, report):
        result = super().validate_business_rules(report)
        # Add custom validation
        return result
```

### Custom Report Types
```python
class CustomReport(XARFReport):
    category: Literal["custom"]
    custom_field: str
```

## Security Considerations

### Input Validation
- Size limits: 10MB max report, 5MB max evidence
- Type validation: All fields validated
- Format validation: Email, IP, URL validators
- Evidence limits: Max 10 items per report

### Resource Protection
- No arbitrary code execution
- No pickle/YAML deserialization
- Schema size limits
- Memory usage monitoring

## CI/CD Pipeline

### GitHub Actions Workflows
- **test.yml**: Run tests on Python 3.8-3.12
- **lint.yml**: Ruff, Black, mypy checks
- **security.yml**: pip-audit, dependency review
- **docs.yml**: Build and deploy documentation
- **release.yml**: Publish to PyPI

### Quality Gates
- All tests pass
- Coverage ≥95%
- No type errors
- No linting errors
- Security audit passes

## Documentation

### Structure
```
docs/
├── ARCHITECTURE.md          # Full architecture design
├── CLASS_HIERARCHY.md       # Class relationships
├── API_SURFACE.md          # Public API reference
├── getting-started.md      # Quick start guide
├── api-reference/          # Detailed API docs
├── guides/                 # User guides
└── examples/               # Code examples
```

### Tools
- **MkDocs**: Documentation site generator
- **MkDocs Material**: Modern theme
- **mkdocstrings**: API docs from docstrings

## Versioning

### Format
- `4.0.0a1` - Alpha release
- `4.0.0b1` - Beta release
- `4.0.0rc1` - Release candidate
- `4.0.0` - Stable release

### Semantic Versioning
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes only

## Migration Path

### Alpha → Beta
- Complete all 7 report classes
- Add missing features
- Performance optimization
- Documentation improvements

### Beta → Stable
- Production testing
- Community feedback
- Final bug fixes
- Release announcement

## Success Metrics

### Quality
- Test coverage: ≥95%
- Type coverage: 100%
- Zero critical security issues
- Documentation completeness: 100%

### Performance
- Parse speed: 1000+ reports/sec
- Memory efficiency: <10KB per report
- Startup time: <100ms

### Adoption
- PyPI downloads
- GitHub stars
- Community contributions
- Integration examples

## Related Documents

- **ARCHITECTURE.md**: Full architecture design (50+ pages)
- **CLASS_HIERARCHY.md**: Complete class relationships and patterns
- **API_SURFACE.md**: Public API specification
- **README.md**: User-facing documentation

## Quick Commands

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check xarf/
black --check xarf/

# Type checking
mypy xarf/

# Build documentation
mkdocs build

# Build package
python -m build

# Publish to PyPI
python -m twine upload dist/*
```

## Contact & Resources

- **Repository**: https://github.com/xarf/xarf-parser-python
- **Documentation**: https://xarf.readthedocs.io
- **Specification**: https://github.com/xarf/xarf-spec
- **Website**: https://xarf.org
- **Issues**: https://github.com/xarf/xarf-parser-python/issues

---

**Last Updated**: 2025-11-20
**Version**: 4.0.0a1
**Status**: Architecture design complete, implementation in progress
