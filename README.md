# XARF Python Library

![XARF Spec](https://img.shields.io/badge/XARF%20Spec-v4.2.0-blue)
[![PyPI version](https://badge.fury.io/py/xarf.svg)](https://pypi.org/project/xarf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/xarf/xarf-python/actions/workflows/ci.yml/badge.svg)](https://github.com/xarf/xarf-python/actions/workflows/ci.yml)

A Python library for parsing, validating, and generating [XARF v4](https://xarf.org) (eXtended Abuse Reporting Format) reports.

## Features

- **Parse** XARF reports from JSON with validation and typed results
- **Generate** XARF-compliant reports with auto-generated metadata (UUIDs, timestamps)
- **Validate** reports against the official JSON schemas with detailed errors and warnings
- **Full type support** with Pydantic v2 discriminated union models for all 7 categories
- **v3 backward compatibility** with automatic detection and conversion
- **Schema-driven** — validation rules derived from the official [xarf-spec](https://github.com/xarf/xarf-spec) schemas, not hardcoded

## Installation

```bash
pip install xarf
```

## Quick Start

### Parsing a Report

```python
from xarf import parse

# Missing first_seen and source_port produce validation warnings.
result = parse({
    "xarf_version": "4.2.0",
    "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2024-01-15T10:30:00Z",
    # "first_seen": "2024-01-15T10:00:00Z",
    "reporter": {
        "org": "Security Team",
        "contact": "abuse@example.com",
        "domain": "example.com",
    },
    "sender": {
        "org": "Security Team",
        "contact": "abuse@example.com",
        "domain": "example.com",
    },
    "source_identifier": "192.0.2.100",
    # "source_port": 1234,
    "category": "connection",
    "type": "ddos",
    "evidence_source": "honeypot",
    "destination_ip": "203.0.113.10",
    "protocol": "tcp",
})

if not result.errors:
    print(result.report.category)  # 'connection'
else:
    for e in result.errors:
        print(f"{e.field}: {e.message}")
```

### Creating a Report

```python
from xarf import create_report, create_evidence

# Returns XARFEvidence with content_type, payload (base64), hash, size, description
evidence = create_evidence(
    "message/rfc822",
    raw_email_bytes,
    description="Original spam email",
    hash_algorithm="sha256",
)

# xarf_version, report_id, and timestamp are auto-generated
result = create_report(
    category="messaging",
    type="spam",
    source_identifier="192.0.2.100",
    reporter={
        "org": "Example Security",
        "contact": "abuse@example.com",
        "domain": "example.com",
    },
    sender={
        "org": "Example Security",
        "contact": "abuse@example.com",
        "domain": "example.com",
    },
    evidence_source="spamtrap",
    description="Spam email detected from source",
    protocol="smtp",
    smtp_from="spammer@evil.example.com",
    evidence=[evidence],
)

import json
print(json.dumps(result.report.model_dump(by_alias=True, exclude_none=True), indent=2))
```

## API Reference

### `parse(json_data, strict=False, show_missing_optional=False)`

Parse and validate a XARF report from JSON. Supports both v4 and v3 (legacy) formats — v3 reports are automatically converted to v4 with deprecation warnings.

```python
from xarf import parse

result = parse(json_data, strict=False, show_missing_optional=False)
```

**Parameters:**

- `json_data: str | dict` — JSON string or dict containing a XARF report
- `strict: bool` — Return `report=None` on validation failures (default: `False`)
- `show_missing_optional: bool` — Populate `result.info` with missing optional field details (default: `False`)

**Returns `ParseResult`:**

- `report: AnyXARFReport | None` — The parsed report, typed by category (e.g., `DdosReport`, `SpamReport`)
- `errors: list[ValidationError]` — Structured validation errors (each has `.field`, `.message`, `.value`)
- `warnings: list[ValidationWarning]` — Structured validation warnings
- `info: list[dict[str, str]] | None` — Missing optional field info (only when `show_missing_optional=True`)

### `create_report(*, category, type, source_identifier, reporter, sender, **kwargs)`

Create a validated XARF report with auto-generated metadata. Automatically fills `xarf_version`, `report_id` (UUID v4), and `timestamp` (ISO 8601 UTC).

```python
from xarf import create_report

result = create_report(
    category="messaging",
    type="spam",
    source_identifier="192.0.2.100",
    reporter={"org": "...", "contact": "...", "domain": "..."},
    sender={"org": "...", "contact": "...", "domain": "..."},
    # category-specific fields as keyword arguments
    protocol="smtp",
)
```

**Parameters:**

- `category: str` — One of the 7 XARF categories
- `type: str` — Report type within the category
- `source_identifier: str` — IP address or identifier of the abuse source
- `reporter: dict | ContactInfo` — Reporting organization details
- `sender: dict | ContactInfo` — Sending organization details
- `strict: bool` — Return `report=None` on validation failures (default: `False`)
- `show_missing_optional: bool` — Populate `result.info` with missing optional field details (default: `False`)
- `**kwargs` — Category-specific fields (e.g., `protocol`, `destination_ip`, `smtp_from`)

**Returns `CreateReportResult`:**

- `report: AnyXARFReport | None` — The generated report
- `errors: list[ValidationError]` — Structured validation errors (`field`, `message`, `value`)
- `warnings: list[ValidationWarning]` — Structured validation warnings
- `info: list[dict[str, str]] | None` — Missing optional field info (only when `show_missing_optional=True`)

### `create_evidence(content_type, payload, *, description=None, hash_algorithm="sha256")`

Create an evidence object with automatic base64 encoding, hashing, and size calculation.

```python
from xarf import create_evidence

evidence = create_evidence(
    "message/rfc822",
    raw_bytes,
    description="Original email",
    hash_algorithm="sha256",
)
```

**Parameters:**

- `content_type: str` — MIME type of the evidence (e.g., `'message/rfc822'`)
- `payload: bytes | str` — The evidence data (strings are UTF-8 encoded)
- `description: str | None` — Human-readable description
- `hash_algorithm: Literal["sha256", "sha512", "sha1", "md5"]` — Hash algorithm (default: `"sha256"`)

**Returns `XARFEvidence`** with computed `hash`, `size`, and base64-encoded `payload`.

### `schema_registry`

Access schema-derived validation rules and metadata programmatically.

```python
from xarf import schema_registry

# Get all valid categories
schema_registry.get_categories()
# {'messaging', 'connection', 'content', 'infrastructure', 'copyright', 'vulnerability', 'reputation'}

# Get valid types for a category
schema_registry.get_types_for_category("connection")
# {'ddos', 'port_scan', 'login_attack', ...}

# Check if a category/type combination is valid
schema_registry.is_valid_type("connection", "ddos")  # True

# Get field metadata including descriptions
schema_registry.get_field_metadata("confidence")
# FieldMetadata(description='...', required=False, recommended=True, ...)
```

### Validation Details

Both `parse()` and `create_report()` run validation internally. Additional behaviors:

- **Unknown fields** trigger warnings (or cause `report=None` in strict mode)
- **Missing optional fields** can be discovered with `show_missing_optional=True`:

```python
result = parse(report, show_missing_optional=True)

if result.info:
    for item in result.info:
        print(f"{item['field']}: {item['message']}")
        # e.g., "description: OPTIONAL - Human-readable description of the abuse"
        # e.g., "confidence: RECOMMENDED - Confidence score between 0.0 and 1.0"
```

**Type narrowing** after parsing — use `isinstance` or check `.category`/`.type`:

```python
from xarf import parse, DdosReport

result = parse(json_data)
if isinstance(result.report, DdosReport):
    print(result.report.destination_ip)

# or check attributes directly
if result.report and result.report.category == "connection":
    print(result.report.type)
```

## v3 Backward Compatibility

The library automatically detects XARF v3 reports (by the `Version` field) and converts them to v4 during parsing. Converted reports include `legacy_version: '3'` and deprecation warnings.

```python
from xarf import parse

result = parse(v3_report)

print(result.report.xarf_version)   # '4.2.0'
print(result.report.category)       # mapped category (e.g., 'messaging')
print(result.report.legacy_version) # '3'
# result.warnings includes deprecation notice + conversion details
```

You can also use the low-level utilities directly:

```python
from xarf import is_v3_report, convert_v3_to_v4, get_v3_deprecation_warning

if is_v3_report(json_data):
    v4_data = convert_v3_to_v4(json_data)
    print(get_v3_deprecation_warning())
```

Unknown v3 report types cause a parse error listing the supported types. See [MIGRATION_V3_TO_V4.md](docs/MIGRATION_V3_TO_V4.md) for the full type mapping and migration strategies.

## Schema Management

This library validates against the official [xarf-spec](https://github.com/xarf/xarf-spec) JSON schemas. Schemas are bundled with the package and pinned to the spec version configured in `pyproject.toml`:

```toml
[tool.xarf]
spec_version = "v4.2.0"
```

```bash
# Re-fetch schemas (e.g., to pick up a newer spec version)
python -m xarf fetch-schemas

# Check whether a newer spec version is available
python -m xarf check-schema-updates
```

To update to a newer spec version, change `spec_version` in `pyproject.toml` and run `python -m xarf fetch-schemas`.

## Development

```bash
pytest                        # Run tests
pytest --cov=xarf             # Run tests with coverage
ruff check xarf/              # Lint
ruff format --check xarf/     # Check formatting
mypy --strict xarf/           # Type-check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Links

- [XARF Specification](https://xarf.org)
- [GitHub Repository](https://github.com/xarf/xarf-python)
- [PyPI Package](https://pypi.org/project/xarf/)
- [Issue Tracker](https://github.com/xarf/xarf-python/issues)
- [Migration Guide (v3 → v4)](docs/MIGRATION_V3_TO_V4.md)
- [License (MIT)](LICENSE)
