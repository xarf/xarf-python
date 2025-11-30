# XARF v4.0.0 Python Parser - Stable Release 🎉

We're excited to announce the **stable release** of the XARF v4.0.0 Python parser! This production-ready library provides comprehensive support for parsing, validating, and generating XARF v4 abuse reports.

## 🚀 What's New

### Production Ready
- **Stable Release**: Graduated from Beta to Production/Stable
- **Python 3.8-3.12 Support**: Fully tested across all modern Python versions
- **Comprehensive Test Coverage**: 80%+ code coverage with extensive test suite
- **Type Hints**: Full type annotation support for better IDE integration

### XARF v3 Backwards Compatibility
- **Automatic Conversion**: Seamlessly converts v3 reports to v4 format
- **Detection**: `is_v3_report()` function to identify v3 reports
- **Explicit Conversion**: `convert_v3_to_v4()` for manual conversion
- **Deprecation Warnings**: Helpful warnings when processing v3 reports
- **Migration Guide**: Complete documentation for upgrading from v3

### Modern Python Support
- **Pydantic V2**: Migrated to Pydantic V2 API for better performance
- **Python 3.13 Compatible**: Fixed all datetime deprecations
- **Type Safety**: Enhanced type hints throughout the codebase

## 📦 Installation

```bash
pip install xarf
```

## 🎯 Quick Start

### Parse a XARF Report

```python
from xarf import XARFParser

# Parse a XARF report
parser = XARFParser()
report = parser.parse('{"xarf_version": "4.0.0", "category": "messaging", ...}')

# Access report data
print(f"Category: {report.category}")
print(f"Type: {report.type}")
print(f"Source: {report.source_identifier}")
```

### Generate a XARF Report

```python
from xarf import XARFReport
from datetime import datetime, timezone

# Create a new report
report = XARFReport(
    xarf_version="4.0.0",
    report_id="550e8400-e29b-41d4-a716-446655440000",
    timestamp=datetime.now(timezone.utc).isoformat(),
    category="connection",
    type="ddos",
    reporter={
        "org": "Security Operations",
        "contact": "abuse@example.com",
        "type": "automated"
    },
    sender={
        "org": "Security Operations",
        "contact": "abuse@example.com"
    },
    source_identifier="192.0.2.100"
)

# Validate and export
if report.validate():
    json_output = report.to_json(indent=2)
    print(json_output)
```

### Convert XARF v3 to v4

```python
from xarf import XARFParser, is_v3_report, convert_v3_to_v4

# Check if report is v3
json_data = {...}  # Your XARF v3 report
if is_v3_report(json_data):
    # Convert to v4
    v4_report = convert_v3_to_v4(json_data)
    print(f"Converted to v4: {v4_report['category']}")

# Or use automatic conversion
parser = XARFParser()
report = parser.parse(json_data)  # Automatically converts v3 to v4
```

## ✨ Features

### Supported Categories
- ✅ **messaging** - Email spam, phishing, social engineering
- ✅ **connection** - DDoS, port scans, login attacks, brute force
- ✅ **content** - Phishing sites, malware distribution, defacement, fraud
- ✅ **infrastructure** - Compromised systems, botnets
- ✅ **copyright** - DMCA, P2P, cyberlockers
- ✅ **vulnerability** - CVE reports, misconfigurations
- ✅ **reputation** - Threat intelligence, blocklists

### Core Capabilities
- 📋 Parse and validate XARF v4 reports
- 🔄 Convert XARF v3 reports to v4 format
- ✏️ Generate new XARF v4 reports
- 🔍 Comprehensive JSON schema validation
- 📝 Type-safe Python models with Pydantic
- 🧪 Extensive test coverage (80%+)
- 📚 Complete documentation and examples

## 🔧 Technical Details

### Requirements
- Python 3.8 or higher
- Dependencies:
  - `pydantic>=2.0.0` - Data validation
  - `jsonschema>=4.0.0` - Schema validation
  - `python-dateutil>=2.8.0` - Date handling
  - `email-validator>=2.0.0` - Email validation

### Breaking Changes from v3

#### Field Rename: `class` → `category`
The field previously named `class` has been renamed to `category` to align with the official XARF v4 specification and avoid conflicts with programming language reserved keywords.

**Migration:**
```python
# XARF v3
report.class_  # Old way (reserved word workaround)

# XARF v4
report.category  # New way (clean, no workarounds)
```

**Automatic Conversion:**
The parser automatically converts v3 reports, so you don't need to update your existing reports immediately. A deprecation warning will guide you through the migration.

## 📖 Documentation

- **Official Website**: https://xarf.org
- **GitHub Repository**: https://github.com/xarf/xarf-python
- **XARF Specification**: https://github.com/xarf/xarf-spec
- **Migration Guide**: [docs/migration-guide.md](https://github.com/xarf/xarf-python/blob/main/docs/migration-guide.md)
- **Examples**: See the `examples/` directory

## 🤝 Contributing

We welcome contributions! Please see:
- [CONTRIBUTING.md](https://github.com/xarf/xarf-python/blob/main/CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](https://github.com/xarf/xarf-python/blob/main/CODE_OF_CONDUCT.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/xarf/xarf-python/blob/main/LICENSE) file for details.

## 🔗 Links

- PyPI: https://pypi.org/project/xarf/
- GitHub: https://github.com/xarf/xarf-python
- Issues: https://github.com/xarf/xarf-python/issues
- Discussions: https://github.com/xarf/xarf-spec/discussions

## 🙏 Acknowledgments

Thanks to all the contributors who helped make XARF v4 possible, and to the abuse handling community for their feedback and support.

---

**Full Changelog**: [CHANGELOG.md](https://github.com/xarf/xarf-python/blob/main/CHANGELOG.md)
