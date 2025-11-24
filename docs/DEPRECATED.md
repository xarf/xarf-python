# XARF Python Library - Deprecated Features

**Library Version**: 4.0.0+
**Last Updated**: 2025-01-23

## Overview

This document lists all deprecated features in the XARF Python library, their replacements, and removal timelines. Deprecation follows semantic versioning with clear migration paths.

## Deprecation Policy

- **Warning Period**: Minimum 12 months before removal
- **Documentation**: All deprecations documented with examples
- **Warnings**: Python `DeprecationWarning` issued when used
- **Alternatives**: Clear migration path provided

## Currently Deprecated Features

### 1. Field Name: `class_` Property

**Status**: ⚠️ Deprecated since v4.0.0 (2024-01-20)
**Removal**: v5.0.0 (estimated 2025-Q1)
**Reason**: XARF v4 spec renamed field to `category`

#### What's Deprecated

```python
from xarf import XARFParser

parser = XARFParser()
report = parser.parse(report_json)

# ❌ Deprecated - will be removed in v5.0.0
old_value = report.class_
if report.class_ == "messaging":
    process_messaging(report)
```

#### Migration Path

```python
# ✅ Use this instead
new_value = report.category
if report.category == "messaging":
    process_messaging(report)
```

#### Deprecation Warning

```python
DeprecationWarning: Accessing 'class_' property is deprecated.
Use 'category' instead. This will be removed in v5.0.0.
```

---

### 2. Parameter Name: `report_class` in Generator

**Status**: ⚠️ Deprecated since v4.0.0 (2024-01-20)
**Removal**: v5.0.0 (estimated 2025-Q1)
**Reason**: Renamed to `category` for consistency

#### What's Deprecated

```python
from xarf.generator import XARFGenerator

gen = XARFGenerator()

# ❌ Deprecated parameter name
report = gen.create_report(
    report_class="messaging",  # Old parameter
    report_type="spam",
    source_identifier="192.0.2.1",
    reporter_org="Security Team",
    reporter_contact="abuse@example.com"
)
```

#### Migration Path

```python
# ✅ Use this instead
report = gen.create_report(
    category="messaging",  # New parameter
    report_type="spam",
    source_identifier="192.0.2.1",
    reporter_org="Security Team",
    reporter_contact="abuse@example.com"
)
```

---

### 3. JSON Field: `"class"` in Report Structure

**Status**: ⚠️ Deprecated for generation since v4.0.0 (2024-01-20)
**Parsing Support**: Indefinite (auto-conversion to `category`)
**Generation**: Never output (v4.0.0+)
**Reason**: XARF v4 spec standardizes on `category`

#### What's Deprecated

```python
# ❌ Deprecated JSON structure (parsing still works)
report_json = {
    "xarf_version": "4.0.0",
    "class": "messaging",  # Deprecated field name
    "type": "spam"
}
```

#### Migration Path

```python
# ✅ Use this instead
report_json = {
    "xarf_version": "4.0.0",
    "category": "messaging",  # New field name
    "type": "spam"
}
```

**Note**: Parsing of `"class"` field will be supported indefinitely for backwards compatibility, but all generated reports use `"category"`.

---

### 4. Module: `xarf.converter` (Removed)

**Status**: ❌ Removed in v4.0.0
**Removal Date**: 2024-01-20
**Reason**: Being redesigned for better v3→v4 conversion
**Planned Return**: v4.1.0 or v4.2.0

#### What Was Removed

```python
# ❌ No longer available
from xarf.converter import XARFConverter

converter = XARFConverter()
v4_report = converter.convert_v3_to_v4(v3_report)
```

#### Temporary Workaround

```python
def simple_v3_to_v4(v3_report: dict) -> dict:
    """Basic v3 to v4 conversion."""
    v4_report = v3_report.copy()

    # Update version
    v4_report["xarf_version"] = "4.0.0"

    # Migrate class to category
    if "class" in v4_report:
        v4_report["category"] = v4_report.pop("class")

    # Map v3 structure to v4
    if "Report" in v4_report:
        report_data = v4_report.pop("Report")
        v4_report.update(report_data)

    if "ReporterInfo" in v4_report:
        reporter_data = v4_report.pop("ReporterInfo")
        v4_report["reporter"] = {
            "org": reporter_data.get("ReporterOrg"),
            "contact": reporter_data.get("ReporterOrgEmail"),
            "type": "unknown"
        }

    return v4_report
```

---

## Previously Deprecated (Now Removed)

### Python 3.7 Support

**Deprecated**: v3.5.0 (2023-06-01)
**Removed**: v4.0.0 (2024-01-20)
**Reason**: Python 3.7 reached end of life (June 2023)

#### What Changed

- Minimum Python version is now 3.8+
- Library uses Python 3.8+ features (walrus operator, etc.)

---

## Future Deprecations

### Planned for v4.1.0

No new deprecations planned.

### Planned for v5.0.0 (2025)

#### 1. Legacy v3 Auto-Conversion (Under Review)

**Status**: 🔍 Under consideration
**Potential Change**: Move to optional module
**Reason**: Reduce complexity, improve performance

```python
# May require explicit opt-in for v3 support
from xarf.legacy import V3CompatibleParser

parser = V3CompatibleParser()  # Explicit v3 support
report = parser.parse(v3_json)
```

---

## Deprecation Timeline

| Feature | Deprecated | Warning Period | Removal | Status |
|---------|------------|----------------|---------|--------|
| `class_` property | v4.0.0 (2024-01) | 12 months | v5.0.0 (2025-01) | ⚠️ Active |
| `report_class` param | v4.0.0 (2024-01) | 12 months | v5.0.0 (2025-01) | ⚠️ Active |
| `"class"` JSON field | v4.0.0 (2024-01) | Indefinite | Never (parsing) | 🔒 Permanent parsing support |
| `xarf.converter` module | v4.0.0 (2024-01) | - | Removed | ❌ Removed (returning in v4.1+) |
| Python 3.7 | v3.5.0 (2023-06) | 8 months | v4.0.0 (2024-01) | ❌ Removed |

---

## Handling Deprecation Warnings

### Viewing Warnings

```python
import warnings

# Show all deprecation warnings
warnings.filterwarnings('default', category=DeprecationWarning)

# Or show them once
warnings.filterwarnings('once', category=DeprecationWarning)

# Or make them errors (strict mode)
warnings.filterwarnings('error', category=DeprecationWarning)
```

### Suppressing Specific Warnings (Not Recommended)

```python
import warnings

# Suppress specific warning (not recommended)
warnings.filterwarnings(
    'ignore',
    message='.*class_.*',
    category=DeprecationWarning
)
```

**Warning**: Suppressing deprecation warnings can lead to breaking changes when features are removed.

---

## Migration Checklist

Use this checklist when updating deprecated code:

### Code Updates

- [ ] Replace all `report.class_` with `report.category`
- [ ] Update `report_class` parameters to `category`
- [ ] Change JSON `"class"` fields to `"category"`
- [ ] Update function signatures using `class` parameter names
- [ ] Update tests for new field names
- [ ] Update documentation and comments

### Testing

- [ ] Run tests with deprecation warnings enabled
- [ ] Verify all warnings resolved
- [ ] Test with both v3 and v4 sample data
- [ ] Validate generated reports against v4 schema

### Documentation

- [ ] Update README examples
- [ ] Update API documentation
- [ ] Update internal wiki/docs
- [ ] Update training materials

---

## Getting Deprecation Notices

### Command Line

```bash
# Run with warnings visible
python -W default::DeprecationWarning your_script.py

# Or use pytest
pytest -W default::DeprecationWarning

# Make warnings errors (fail fast)
python -W error::DeprecationWarning your_script.py
```

### Programmatic Detection

```python
import warnings

def check_for_deprecations():
    """Detect deprecated usage in codebase."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)

        # Your code here
        report = parser.parse(data)
        _ = report.class_  # Triggers warning

        # Check warnings
        for warning in w:
            if issubclass(warning.category, DeprecationWarning):
                print(f"Deprecation: {warning.message}")
                print(f"File: {warning.filename}:{warning.lineno}")
```

---

## Staying Informed

### How to Track Deprecations

1. **CHANGELOG.md**: Read before upgrading
2. **GitHub Releases**: Subscribe to release notifications
3. **Documentation**: Check deprecation notices
4. **This File**: Review regularly for updates

### Subscribe to Updates

- GitHub Watch: https://github.com/xarf/xarf-python
- Release RSS: https://github.com/xarf/xarf-python/releases.atom
- PyPI RSS: https://pypi.org/rss/project/xarf-parser/releases.xml

---

## Support and Questions

### If You're Affected by a Deprecation

1. **Review migration path** in this document
2. **Check MIGRATION_GUIDE.md** for detailed steps
3. **Search GitHub issues** for related discussions
4. **Open new issue** if you need help

### Reporting Issues

If you believe a deprecation is:
- Too aggressive
- Missing migration path
- Incorrectly implemented

Please open an issue: https://github.com/xarf/xarf-python/issues

---

## Related Documentation

- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) - Step-by-step migration
- [COMPATIBILITY.md](COMPATIBILITY.md) - Backwards compatibility
- [CHANGELOG.md](../CHANGELOG.md) - Complete version history
- [README.md](../README.md) - Library overview

---

**Last Updated**: 2025-01-23
**Review Schedule**: Quarterly
**Next Review**: 2025-04-23
