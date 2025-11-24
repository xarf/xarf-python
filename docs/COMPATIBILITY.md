# XARF Python Library - Backwards Compatibility Guide

**Library Version**: 4.0.0+
**XARF Specification**: v4.0.0
**Last Updated**: 2025-01-23

## Overview

The XARF Python library v4.0.0 implements the XARF v4 specification with full backwards compatibility for XARF v3 reports. This guide details the compatibility strategy, breaking changes, and migration paths.

## Field Name Changes: `class` → `category`

### The Change

XARF v4 specification renamed the field from `class` (v3) to `category` (v4) to avoid conflicts with programming language reserved keywords and improve semantic clarity.

| Version | Field Name | Python Access | Status |
|---------|------------|---------------|--------|
| **v3** | `class` | `report.class_` (workaround) | ❌ Deprecated |
| **v4** | `category` | `report.category` (clean) | ✅ Current |

### Why This Matters

- **Python Keyword Conflict**: `class` is a reserved keyword requiring awkward workarounds
- **Better Semantics**: "category" more accurately describes abuse classification
- **Cross-Language Consistency**: Easier implementation across Java, JavaScript, C#, Go

## Compatibility Strategy

### Parsing Behavior

The parser accepts **both field names** with the following precedence:

```python
# Priority order when parsing:
# 1. "category" field (v4 standard)
# 2. "class" field (v3 compatibility)
# 3. Raise error if neither present

from xarf import XARFParser

parser = XARFParser()

# ✅ v4 format (recommended)
v4_report = parser.parse('{"category": "messaging", ...}')

# ✅ v3 format (backwards compatibility)
v3_report = parser.parse('{"class": "messaging", ...}')

# Both work identically
print(v4_report.category)  # "messaging"
print(v3_report.category)  # "messaging" (auto-converted)
```

### Generation Behavior

The generator **always** produces v4 format with `category`:

```python
from xarf.generator import XARFGenerator

gen = XARFGenerator()

report = gen.create_report(
    category="messaging",  # v4 parameter name
    report_type="spam",
    source_identifier="192.0.2.1",
    reporter_org="Security Team",
    reporter_contact="abuse@example.com"
)

# Output uses "category" field only
print(report.to_json())
# {"category": "messaging", ...}
```

## Migration Guide

### Step 1: Update Dependencies

```bash
# Upgrade to latest version
pip install --upgrade xarf-parser>=4.0.0

# Or specify exact version
pip install xarf-parser==4.0.0
```

### Step 2: Code Changes

#### Before (v3 / Pre-4.0.0)

```python
# JSON with "class" field
report_json = {
    "xarf_version": "4.0.0",
    "class": "connection",  # ❌ Old field name
    "type": "ddos"
}

# Awkward Python access
print(report.class_)  # ❌ Requires underscore
```

#### After (v4.0.0+)

```python
# JSON with "category" field
report_json = {
    "xarf_version": "4.0.0",
    "category": "connection",  # ✅ New field name
    "type": "ddos"
}

# Clean Python access
print(report.category)  # ✅ No workaround needed
```

### Step 3: Update Function Parameters

```python
# Before
def process_report(report_class: str, report_type: str):
    if report_class == "messaging":
        handle_messaging(report_type)

# After
def process_report(category: str, report_type: str):
    if category == "messaging":
        handle_messaging(report_type)
```

### Step 4: Update Tests

```python
# Before
def test_report():
    assert report.class_ == "content"

# After
def test_report():
    assert report.category == "content"
```

## Backwards Compatibility Features

### Auto-Detection and Conversion

The library automatically detects and converts v3 reports:

```python
from xarf import XARFParser

parser = XARFParser()

# Legacy v3 report (still works)
v3_json = '''
{
  "Version": "4.0.0",
  "ReporterInfo": {
    "ReporterOrg": "Security Team",
    "ReporterOrgEmail": "abuse@example.com"
  },
  "Report": {
    "ReportClass": "Activity",
    "ReportType": "Spam",
    "SourceIp": "192.0.2.1"
  }
}
'''

# Auto-converts to v4 format
report = parser.parse(v3_json)
print(report.category)  # "messaging" (auto-mapped from "Activity")
print(report.type)      # "spam" (normalized)
```

### Deprecation Warnings

```python
import warnings

# Using deprecated "class_" accessor triggers warning
report = parser.parse(report_json)

# Triggers DeprecationWarning (if implemented)
# "Accessing 'class_' is deprecated, use 'category' instead"
old_value = report.class_
```

## Common Migration Issues

### Issue 1: KeyError When Accessing Old JSON

**Problem**: Parsing old JSON with `"class"` field in strict v4 mode

**Solution**: Use permissive mode (default) for auto-conversion

```python
# Permissive mode (default) - auto-converts
parser = XARFParser(strict=False)
report = parser.parse(old_json)  # Works with "class" or "category"

# Strict mode - requires v4 format
strict_parser = XARFParser(strict=True)
try:
    report = strict_parser.parse(old_json)  # May fail with v3 format
except XARFValidationError as e:
    print(f"Use permissive mode for v3 reports: {e}")
```

### Issue 2: Database Schema Migration

**Problem**: Existing databases use `report_class` column

**Solution**: Database migration script

```python
import sqlite3

def migrate_database(db_path: str):
    """Migrate database from class to category field."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Add new column
    cursor.execute('''
        ALTER TABLE xarf_reports
        ADD COLUMN category VARCHAR(50)
    ''')

    # Copy data from old column
    cursor.execute('''
        UPDATE xarf_reports
        SET category = report_class
        WHERE category IS NULL
    ''')

    # Create index
    cursor.execute('''
        CREATE INDEX idx_category
        ON xarf_reports(category)
    ''')

    conn.commit()
    conn.close()
```

### Issue 3: Third-Party Integration

**Problem**: External systems expect `"class"` field

**Solution**: Compatibility wrapper

```python
class XARFCompatibilityWrapper:
    """Wrapper providing both old and new field formats."""

    def to_legacy_format(self, report: dict) -> dict:
        """Add 'class' field for legacy systems."""
        legacy_report = report.copy()
        if "category" in legacy_report:
            legacy_report["class"] = legacy_report["category"]
        return legacy_report

    def to_modern_format(self, report: dict) -> dict:
        """Convert 'class' to 'category' for v4."""
        modern_report = report.copy()
        if "class" in modern_report and "category" not in modern_report:
            modern_report["category"] = modern_report.pop("class")
        return modern_report

# Usage
wrapper = XARFCompatibilityWrapper()

# Sending to legacy API
legacy_data = wrapper.to_legacy_format(v4_report)
send_to_legacy_api(legacy_data)

# Receiving from legacy API
modern_data = wrapper.to_modern_format(received_data)
report = parser.parse(modern_data)
```

## Category Support Matrix

### Currently Supported (v4.0.0)

| Category | Status | Types Supported |
|----------|--------|-----------------|
| **messaging** | ✅ Full | spam, phishing, social_engineering |
| **connection** | ✅ Full | ddos, port_scan, login_attack, ip_spoofing |
| **content** | ✅ Full | phishing_site, malware_distribution, defacement, web_hack |
| **infrastructure** | 🚧 Planned | botnet, compromised_server |
| **copyright** | 🚧 Planned | infringement, dmca, p2p |
| **vulnerability** | 🚧 Planned | cve, misconfiguration, open_service |
| **reputation** | 🚧 Planned | blocklist, threat_intelligence |

### Planned Support (v4.1.0+)

All remaining categories will be added in minor version updates without breaking changes.

## Version Compatibility Matrix

| Python Library | XARF Spec | v3 Support | v4 Support | Notes |
|----------------|-----------|------------|------------|-------|
| 3.x.x | v3 | ✅ Native | ❌ None | End of life |
| 4.0.0-alpha | v4 | ✅ Auto-convert | ✅ Full | Alpha release |
| 4.0.0 | v4 | ✅ Auto-convert | ✅ Full | Stable (planned Q2 2024) |
| 4.1.0+ | v4 | ✅ Auto-convert | ✅ Full | All categories |

## Deprecation Timeline

| Date | Version | Action |
|------|---------|--------|
| **2024-01-20** | 4.0.0-alpha | `class_` marked deprecated |
| **Q2 2024** | 4.0.0 | Deprecation warnings enabled |
| **Q4 2024** | 4.1.0 | v3 auto-convert moves to optional module |
| **2025-Q1** | 5.0.0 | Breaking: Remove `class_` accessor |

## Testing Compatibility

### Running Compatibility Tests

```bash
# Run full test suite including compatibility tests
pytest tests/ -v

# Run only compatibility tests
pytest tests/test_compatibility.py -v

# Run with warnings visible
pytest tests/ -W default::DeprecationWarning
```

### Example Compatibility Test

```python
import pytest
from xarf import XARFParser

def test_v3_compatibility():
    """Ensure v3 reports parse correctly."""
    parser = XARFParser()

    v3_report = {
        "Version": "4.0.0",
        "ReporterInfo": {
            "ReporterOrg": "Test Org",
            "ReporterOrgEmail": "abuse@test.com"
        },
        "Report": {
            "ReportClass": "Activity",
            "ReportType": "Spam",
            "SourceIp": "192.0.2.1"
        }
    }

    report = parser.parse(v3_report)

    assert report.category == "messaging"
    assert report.type == "spam"
    assert report.source_identifier == "192.0.2.1"
```

## Best Practices

### For New Projects

1. ✅ Use `category` field in all new code
2. ✅ Use v4 JSON format exclusively
3. ✅ Test with v4 schema validation
4. ✅ Follow migration guide for consistency

### For Existing Projects

1. ✅ Enable deprecation warnings
2. ✅ Update code incrementally
3. ✅ Test with both v3 and v4 samples
4. ✅ Plan database migration
5. ✅ Update integration partners

### For Library Maintainers

1. ✅ Accept both `class` and `category` during transition
2. ✅ Emit deprecation warnings
3. ✅ Provide migration tools
4. ✅ Maintain backwards compatibility for 12+ months

## Getting Help

### Resources

- **Migration Guide**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Changelog**: [CHANGELOG.md](../CHANGELOG.md)
- **XARF Specification**: https://xarf.org/docs/specification/
- **GitHub Issues**: https://github.com/xarf/xarf-python/issues
- **GitHub Discussions**: https://github.com/xarf/xarf-spec/discussions

### Support Channels

- GitHub Issues for bugs
- GitHub Discussions for questions
- Email: contact@xarf.org

## Related Documentation

- [README.md](../README.md) - Library overview
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Detailed migration steps
- [DEPRECATED.md](DEPRECATED.md) - Deprecated features list
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation

---

**Status**: Production Ready
**Stability**: Stable
**Compatibility**: XARF v3 + v4
