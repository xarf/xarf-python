# XARF v4 Python Parser (Alpha)

A Python library for parsing and validating XARF v4 (eXtended Abuse Reporting Format) reports.

## 🚀 Status: Alpha Development

This library is currently in **alpha** development. It supports parsing the core XARF v4 classes:

- ✅ **messaging** - Email spam, phishing, social engineering
- ✅ **connection** - DDoS, port scans, login attacks  
- ✅ **content** - Phishing sites, malware distribution, defacement
- 🚧 **infrastructure** - Compromised systems (coming soon)
- 🚧 **copyright** - DMCA, trademark violations (coming soon)
- 🚧 **vulnerability** - CVE reports, misconfigurations (coming soon)
- 🚧 **reputation** - Threat intelligence (coming soon)

## 📦 Installation

```bash
# Alpha releases (recommended for early testing)
pip install xarf-parser==4.0.0a1

# Development installation
git clone https://github.com/xarf/xarf-parser-python.git
cd xarf-parser-python
pip install -e .
```

## 🔧 Quick Start

```python
from xarf import XARFParser

# Initialize parser
parser = XARFParser()

# Parse a XARF report from JSON string
report_json = '{"xarf_version": "4.0.0", ...}'
report = parser.parse(report_json)

# Access report data
print(f"Report class: {report.class_}")
print(f"Report type: {report.type}")
print(f"Source: {report.source_identifier}")

# Validate report structure
if parser.validate(report_json):
    print("Report is valid")
else:
    print("Validation errors:", parser.get_errors())
```

## 📋 JSON Schema Validation

This parser uses the official JSON schemas from the [XARF specification repository](https://github.com/xarf/xarf-spec/tree/main/schemas/v4):

```python
# Validate against official XARF v4 schema
from xarf.validation import validate_xarf_report

# Schema URLs reference the spec repository
validation_result = validate_xarf_report(
    report_json, 
    schema_url="https://raw.githubusercontent.com/xarf/xarf-spec/main/schemas/v4/xarf-v4-master.json"
)
```

## 📋 Features

### Current (Alpha)
- ✅ JSON Schema validation
- ✅ Basic field parsing
- ✅ Evidence handling (text, images, PDFs)
- ✅ Support for messaging, connection, content classes
- ✅ Python 3.8+ compatibility

### Planned (Beta)
- 🚧 Complete class coverage (all 7 classes)
- 🚧 Business rule validation
- 🚧 XARF v3 backward compatibility
- 🚧 Evidence compression support
- 🚧 Performance optimizations

### Future
- 🔮 CLI tools
- 🔮 Integration adapters (SIEM, etc.)
- 🔮 Bulk processing utilities

## 📊 Supported Classes & Types

### messaging
- `spam` - Email spam reports
- `phishing` - Phishing emails
- `social_engineering` - Social engineering attempts

### connection
- `ddos` - Distributed denial of service attacks
- `port_scan` - Port scanning attempts
- `login_attack` - Brute force/credential attacks
- `ip_spoofing` - IP address spoofing

### content
- `phishing_site` - Phishing websites
- `malware_distribution` - Malware hosting sites
- `defacement` - Website defacements
- `spamvertised` - Spam-advertised content
- `web_hack` - Web application attacks

## 🧪 Examples

### Parse Email Spam Report
```python
import json
from xarf import XARFParser

spam_report = {
    "xarf_version": "4.0.0",
    "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": {
        "org": "Spam Detection Service",
        "contact": "noreply@spamdetect.example",
        "type": "automated"
    },
    "source_identifier": "192.0.2.100",
    "class": "messaging",
    "type": "spam",
    "evidence_source": "spamtrap",
    "protocol": "smtp",
    "smtp_from": "spammer@badexample.com",
    "subject": "Get Rich Quick Scheme!",
    "evidence": [
        {
            "content_type": "message/rfc822",
            "description": "Full email message captured by spamtrap",
            "payload": "UmVjZWl2ZWQ6IGZyb20gYmFkZXhhbXBsZS5jb20="
        }
    ],
    "tags": ["spam:bulk", "category:financial"]
}

parser = XARFParser()
report = parser.parse(json.dumps(spam_report))
print(f"Detected {report.type} from {report.smtp_from}")
```

### Validate DDoS Report
```python
ddos_report_json = '''
{
    "xarf_version": "4.0.0",
    "class": "connection",
    "type": "ddos",
    "source_identifier": "203.0.113.50",
    "destination_ip": "198.51.100.10",
    "protocol": "tcp",
    "destination_port": 80,
    "attack_type": "syn_flood",
    "duration_minutes": 45
}
'''

if parser.validate(ddos_report_json):
    print("DDoS report is valid")
    report = parser.parse(ddos_report_json)
    print(f"Attack duration: {report.duration_minutes} minutes")
```

## 🔍 Validation

The parser performs multiple levels of validation:

1. **JSON Schema** - Structure and required fields
2. **Data Types** - Field type validation
3. **Business Rules** - Class-specific requirements
4. **Evidence** - Content type matching and size limits

```python
# Get detailed validation results
parser = XARFParser(strict=True)
try:
    report = parser.parse(json_string)
except XARFValidationError as e:
    print("Validation failed:")
    for error in e.errors:
        print(f"  - {error}")
```

## 🧬 Development

```bash
# Setup development environment
git clone https://github.com/xarf/xarf-parser-python.git
cd xarf-parser-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 xarf/
black xarf/

# Type checking
mypy xarf/
```

## 📚 Documentation

- **[XARF v4 Specification](https://github.com/xarf/xarf-spec)** - Complete technical reference
- **[Sample Reports](https://github.com/xarf/xarf-spec/tree/master/samples/v4)** - Real-world examples
- **[Migration Guide](https://github.com/xarf/xarf-spec/blob/master/2_XARF_v4_Technical_Specification.md#xarf-v3-migration)** - Upgrading from XARF v3

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

- **Bug Reports**: Use GitHub Issues
- **Feature Requests**: Discuss in GitHub Discussions  
- **Pull Requests**: Follow our coding standards
- **Testing**: Add tests for new features

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[xarf-spec](https://github.com/xarf/xarf-spec)** - XARF v4 specification and samples
- **[xarf.org](https://xarf.org)** - Official XARF website
- **JavaScript Parser** (coming soon)
- **Go Parser** (coming soon)

## 📈 Versioning

This project follows semantic versioning with alpha/beta releases:

- `4.0.0a1`, `4.0.0a2` - Alpha releases (current)
- `4.0.0b1`, `4.0.0b2` - Beta releases (planned)  
- `4.0.0` - Stable release (Q2 2024)

## 🎯 Roadmap

### Alpha Phase (Current)
- [x] Core parser foundation
- [x] JSON schema validation
- [x] messaging, connection, content classes
- [ ] Evidence handling improvements
- [ ] Performance benchmarks

### Beta Phase (Q1 2024)
- [ ] Complete class coverage (all 7)
- [ ] XARF v3 compatibility layer
- [ ] Advanced validation rules
- [ ] CLI tools
- [ ] Documentation improvements

### Stable Release (Q2 2024)
- [ ] Production-ready performance
- [ ] Comprehensive test coverage
- [ ] Integration examples
- [ ] Community feedback incorporation