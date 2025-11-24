# XARF v4 Python Parser

[![CI](https://github.com/xarf/xarf-python/actions/workflows/ci.yml/badge.svg)](https://github.com/xarf/xarf-python/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/xarf-parser.svg)](https://pypi.org/project/xarf-parser/)
[![Python versions](https://img.shields.io/pypi/pyversions/xarf-parser.svg)](https://pypi.org/project/xarf-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for parsing, validating, and generating XARF v4 (eXtended Abuse Reporting Format) reports.

## 🚀 Status: Alpha Development

This library is currently in **alpha** development (v4.0.0-alpha). It supports the core XARF v4 categories with full parsing, validation, and generation capabilities.

### Supported Categories

- ✅ **messaging** - Email spam, phishing, social engineering
- ✅ **connection** - DDoS, port scans, login attacks, brute force
- ✅ **content** - Phishing sites, malware distribution, defacement, fraud
- 🚧 **infrastructure** - Compromised systems, botnets (coming soon)
- 🚧 **copyright** - DMCA, P2P, cyberlockers (coming soon)
- 🚧 **vulnerability** - CVE reports, misconfigurations (coming soon)
- 🚧 **reputation** - Threat intelligence, blocklists (coming soon)

---

## 📦 Installation

```bash
# Alpha releases (recommended for early testing)
pip install xarf-parser==4.0.0a1

# Install from source for latest development
git clone https://github.com/xarf/xarf-parser-python.git
cd xarf-parser-python
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

---

## ✨ XARF v3 Backwards Compatibility

**Automatic conversion from XARF v3 to v4!** This parser transparently handles legacy v3 reports with automatic conversion and deprecation warnings.

```python
from xarf import XARFParser

parser = XARFParser()

# Works seamlessly with both v3 and v4 reports
v3_report = '''
{
  "Version": "3.0.0",
  "ReporterInfo": {
    "ReporterOrg": "Security Team",
    "ReporterOrgEmail": "abuse@example.com"
  },
  "Report": {
    "ReportClass": "Messaging",
    "ReportType": "spam",
    ...
  }
}
'''

# Automatically converted to v4 format
report = parser.parse(v3_report)
print(f"Category: {report.category}")  # messaging
```

See the **[Migration Guide](docs/migration-guide.md)** for complete v3 to v4 conversion details.

---

## 🔧 Quick Start

### Parsing XARF Reports

```python
from xarf import XARFParser

# Initialize parser
parser = XARFParser()

# Parse a XARF report from JSON string
report_json = '''
{
  "xarf_version": "4.0.0",
  "report_id": "550e8400-e29b-41d4-a716-446655440000",
  "category": "content",
  "type": "phishing",
  "timestamp": "2024-01-15T14:30:00Z",
  "source_identifier": "203.0.113.45",
  "reporter": {
    "org": "Security Team",
    "contact": "abuse@example.com",
    "type": "automated"
  },
  "url": "https://evil-site.example.com/phishing"
}
'''

report = parser.parse(report_json)

# Access report data
print(f"Category: {report.category}")
print(f"Type: {report.type}")
print(f"Source: {report.source_identifier}")
print(f"URL: {report.url}")

# Validate report structure
if parser.validate(report_json):
    print("✅ Report is valid")
else:
    print("❌ Validation errors:", parser.get_errors())
```

### Generating XARF Reports

```python
from xarf.generator import XARFGenerator

# Initialize generator
generator = XARFGenerator()

# Generate a phishing report
report = generator.create_content_report(
    report_type="phishing",
    source_identifier="203.0.113.45",
    url="https://evil-phishing.example.com/login",
    reporter_org="Security Research Lab",
    reporter_contact="abuse@security-lab.example",
    description="Phishing site targeting banking customers",
    evidence=[
        {
            "content_type": "image/png",
            "description": "Screenshot of phishing page",
            "payload": "iVBORw0KGgoAAAANSUhEUg...",  # base64 encoded
            "hashes": ["sha256:a665a45920422f9d417e4867efdc4fb8..."]
        }
    ]
)

# Report is automatically validated and includes:
# - Auto-generated UUID for report_id
# - Current timestamp in ISO 8601 format
# - Proper XARF v4 structure

print(report.to_json())
```

---

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

### Current (Alpha v4.0.0)

- ✅ **Parsing**: Parse XARF v4 JSON reports into Python objects
- ✅ **Validation**: JSON Schema validation with category-specific rules
- ✅ **Generation**: Create XARF v4 reports programmatically
- ✅ **Evidence Handling**: Support for text, images, and binary evidence
- ✅ **Category Support**: messaging, connection, content
- ✅ **Reporter Info**: Including `on_behalf_of` for infrastructure providers
- ✅ **XARF v3 Compatibility**: Automatic conversion with deprecation warnings
- ✅ **Pydantic V2**: Modern validation with full type safety
- ✅ **Python 3.8-3.12**: Full compatibility

### Planned (Beta)

- 🚧 Complete category coverage (all 7 categories)
- 🚧 Advanced validation rules (business logic)
- 🚧 Evidence compression support
- 🚧 Bulk processing utilities
- 🚧 Performance optimizations
- 🚧 CLI tools for validation and conversion

### Future

- 🔮 CLI tools for validation and generation
- 🔮 SIEM integration adapters
- 🔮 Report signing and encryption
- 🔮 Multi-format export (XML, CSV)

## 📊 Supported Categories & Types

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
    "category": "messaging",
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

### Generate DDoS Report

```python
from xarf.generator import XARFGenerator

generator = XARFGenerator()

ddos_report = generator.create_connection_report(
    report_type="ddos",
    source_identifier="203.0.113.50",
    destination_ip="198.51.100.10",
    protocol="tcp",
    destination_port=80,
    reporter_org="Network Operations Center",
    reporter_contact="noc@example.com",
    attack_type="syn_flood",
    duration_minutes=45,
    packet_count=1500000,
    description="Volumetric SYN flood attack against web services"
)

print(f"Attack lasted {ddos_report.duration_minutes} minutes")
print(f"Total packets: {ddos_report.packet_count}")
```

### Using `on_behalf_of` for Infrastructure Providers

```python
from xarf.generator import XARFGenerator

generator = XARFGenerator()

# Infrastructure provider (Abusix) sending report for client (Swisscom)
report = generator.create_report(
    category="messaging",
    report_type="spam",
    source_identifier="192.0.2.150",
    reporter_org="Abusix",
    reporter_contact="reports@abusix.com",
    on_behalf_of={
        "org": "Swisscom",
        "contact": "abuse@swisscom.ch"
    },
    description="Spam detected by Swisscom's infrastructure"
)

# The report clearly shows Abusix is reporting on behalf of Swisscom
print(f"Reporter: {report.reporter.org}")
print(f"On behalf of: {report.reporter.on_behalf_of.org}")
```

## 🔍 Validation

The parser performs multiple validation levels:

1. **JSON Schema** - Structure and required fields
2. **Data Types** - Field type validation
3. **Business Rules** - Category-specific requirements
4. **Evidence** - Content type and size validation

```python
from xarf import XARFParser, XARFValidationError

# Non-strict mode: collect errors without raising exception
parser = XARFParser(strict=False)
is_valid = parser.validate(report_json)

if not is_valid:
    errors = parser.get_errors()
    for error in errors:
        print(f"Error: {error}")

# Strict mode: raise exception on first error
strict_parser = XARFParser(strict=True)
try:
    report = strict_parser.parse(report_json)
except XARFValidationError as e:
    print(f"Validation failed: {e}")
    print(f"Errors: {e.errors}")
```

---

## 🔒 Security Best Practices

### 1. Always Validate Input

```python
from xarf import XARFParser, XARFValidationError

parser = XARFParser(strict=True)

def process_external_report(report_json: str):
    """Safely process XARF report from external source."""
    try:
        # Validate before processing
        if not parser.validate(report_json):
            raise ValueError(f"Invalid report: {parser.get_errors()}")

        report = parser.parse(report_json)
        # Process validated report
        return report

    except XARFValidationError as e:
        # Log validation errors
        log_security_event(f"Invalid XARF report received: {e.errors}")
        raise
```

### 2. Limit Evidence Size

```python
MAX_EVIDENCE_SIZE = 5 * 1024 * 1024  # 5MB per evidence item
MAX_TOTAL_SIZE = 15 * 1024 * 1024   # 15MB total

def validate_evidence_size(report):
    """Enforce evidence size limits."""
    total_size = 0
    for evidence_item in report.evidence or []:
        item_size = evidence_item.get('size', 0)

        if item_size > MAX_EVIDENCE_SIZE:
            raise ValueError(f"Evidence item too large: {item_size} bytes")

        total_size += item_size

    if total_size > MAX_TOTAL_SIZE:
        raise ValueError(f"Total evidence too large: {total_size} bytes")
```

### 3. Verify Evidence Hashes

```python
import hashlib
import base64

def verify_evidence_hash(evidence_item: dict) -> bool:
    """Verify evidence payload matches declared hash."""
    if 'hash' not in evidence_item:
        return True  # Hash is optional

    # Parse hash format: "algorithm:hexvalue"
    hash_string = evidence_item['hash']
    algorithm, expected_hash = hash_string.split(':', 1)

    # Decode base64 payload
    payload_bytes = base64.b64decode(evidence_item['payload'])

    # Compute hash
    if algorithm == 'sha256':
        computed_hash = hashlib.sha256(payload_bytes).hexdigest()
    elif algorithm == 'sha512':
        computed_hash = hashlib.sha512(payload_bytes).hexdigest()
    elif algorithm == 'md5':
        computed_hash = hashlib.md5(payload_bytes).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    return computed_hash == expected_hash
```

---

## 🧬 Development

```bash
# Setup development environment
git clone https://github.com/xarf/xarf-parser-python.git
cd xarf-parser-python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev,test]"

# Run tests with coverage
pytest --cov=xarf --cov-report=term -v tests/

# Run quality checks
black --check .
flake8 xarf/ tests/
mypy xarf/

# Auto-format code
black .
```

### CI/CD Workflows

This project uses two GitHub Actions workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`)
   - Runs on every push to `main` and all pull requests
   - Tests against Python 3.8, 3.9, 3.10, 3.11, and 3.12
   - Runs linting checks: black, flake8, mypy
   - Uploads coverage reports to Codecov

2. **PyPI Publish Workflow** (`.github/workflows/publish.yml`)
   - Runs on GitHub releases
   - Manual workflow dispatch with Test PyPI option
   - Builds distribution packages
   - Publishes to PyPI or Test PyPI

## 📚 Documentation

- **[XARF v4 Specification](https://xarf.org/docs/specification/)** - Complete technical reference
- **[v3 to v4 Migration Guide](docs/migration-guide.md)** - Automatic conversion and compatibility
- **[CHANGELOG](CHANGELOG.md)** - Version history and breaking changes
- **[Sample Reports](https://xarf.org/docs/types/)** - Real-world examples by category
- **[Common Fields](https://xarf.org/docs/common-fields/)** - Field reference
- **[Best Practices](https://xarf.org/docs/best-practices/)** - Implementation guidelines

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

- **Bug Reports**: Use GitHub Issues
- **Feature Requests**: Discuss in GitHub Discussions  
- **Pull Requests**: Follow our coding standards
- **Testing**: Add tests for new features

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🔗 Related Projects

- **[xarf-spec](https://github.com/xarf/xarf-spec)** - XARF v4 specification and JSON schemas
- **[xarf.org](https://xarf.org)** - Official XARF website and documentation
- **xarf-parser-js** (coming soon) - JavaScript/TypeScript parser
- **xarf-parser-go** (coming soon) - Go implementation

## 📈 Versioning

This project follows semantic versioning with alpha/beta releases:

- `4.0.0a1`, `4.0.0a2` - Alpha releases (current)
- `4.0.0b1`, `4.0.0b2` - Beta releases (planned)  
- `4.0.0` - Stable release (Q2 2024)

## 🎯 Roadmap

### Alpha Phase (Current - v4.0.0a1)

- [x] Core parser foundation
- [x] JSON schema validation
- [x] messaging, connection, content categories
- [x] Generator functionality
- [x] `on_behalf_of` support
- [ ] Evidence handling improvements
- [ ] Performance benchmarks

### Beta Phase (Q1 2024)

- [ ] Complete category coverage (all 7)
- [ ] XARF v3 compatibility layer
- [ ] Advanced validation rules
- [ ] CLI tools
- [ ] Comprehensive documentation

### Stable Release (Q2 2024)

- [ ] Production-ready performance
- [ ] >95% test coverage
- [ ] Integration examples
- [ ] Community feedback incorporated
- [ ] Performance optimizations

---

## 💬 Support

- **Documentation**: https://xarf.org
- **GitHub Issues**: https://github.com/xarf/xarf-parser-python/issues
- **Discussions**: https://github.com/xarf/xarf-spec/discussions
- **Email**: contact@xarf.org

---

**Note:** This library implements the official [XARF v4 specification](https://xarf.org/docs/specification/). Always refer to the specification for authoritative technical details.