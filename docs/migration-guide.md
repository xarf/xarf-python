# XARF v3 to v4 Migration Guide

## Overview

XARF v4 Python parser provides **automatic backwards compatibility** with XARF v3 format. Your existing v3 reports will be automatically converted to v4 format when parsed, with deprecation warnings to help you migrate.

## Quick Start

### No Code Changes Required

The parser automatically detects and converts v3 reports:

```python
from xarf import XARFParser

parser = XARFParser()

# Works with both v3 and v4 reports automatically
v3_report_json = '''
{
  "Version": "3.0.0",
  "ReporterInfo": {
    "ReporterOrg": "Security Team",
    "ReporterOrgEmail": "abuse@example.com"
  },
  "Report": {
    "ReportClass": "Messaging",
    "ReportType": "spam",
    "Date": "2024-01-15T10:00:00Z",
    "Source": {"IP": "192.0.2.1"},
    "AdditionalInfo": {
      "Protocol": "smtp",
      "SMTPFrom": "spammer@example.com",
      "Subject": "Spam Message",
      "DetectionMethod": "spamtrap"
    }
  }
}
'''

# Automatically converted to v4 format
report = parser.parse(v3_report_json)
print(f"Category: {report.category}")  # messaging
print(f"Type: {report.type}")          # spam
print(f"From: {report.smtp_from}")     # spammer@example.com
```

## Deprecation Warnings

When parsing v3 reports, you'll receive a deprecation warning:

```python
import warnings
from xarf import XARFParser
from xarf.v3_compat import XARFv3DeprecationWarning

# See deprecation warnings
warnings.simplefilter("always", XARFv3DeprecationWarning)

parser = XARFParser()
report = parser.parse(v3_json)
# DeprecationWarning: XARF v3 format is deprecated. Please upgrade to XARF v4.
```

### Suppressing Warnings (Temporary)

If you need to suppress warnings during migration:

```python
import warnings
from xarf.v3_compat import XARFv3DeprecationWarning

# Suppress v3 warnings temporarily
warnings.simplefilter("ignore", XARFv3DeprecationWarning)

# Your code here
```

## Field Mapping Reference

### Base Fields

| v3 Field | v4 Field | Notes |
|----------|----------|-------|
| `Version` | `xarf_version` | Always becomes "4.0.0" |
| N/A | `report_id` | Auto-generated UUID v4 |
| `Report.Date` | `timestamp` | Preserved as-is |
| `ReporterInfo.ReporterOrg` | `reporter.org` | Direct mapping |
| `ReporterInfo.ReporterOrgEmail` | `reporter.contact` | Preferred over ContactEmail |
| `ReporterInfo.ReporterContactEmail` | `reporter.contact` | Fallback if OrgEmail missing |
| N/A | `reporter.type` | Set to "automated" |
| `Report.Source.IP` | `source_identifier` | Direct mapping |
| `Report.ReportClass` | `category` | Lowercase conversion |
| `Report.ReportType` | `type` | Lowercase conversion |
| `Report.AdditionalInfo.DetectionMethod` | `evidence_source` | Mapped to v4 values |

### Category-Specific Mapping

#### Messaging Reports

| v3 Field | v4 Field |
|----------|----------|
| `AdditionalInfo.Protocol` | `protocol` |
| `AdditionalInfo.SMTPFrom` | `smtp_from` |
| `AdditionalInfo.SMTPTo` | `smtp_to` |
| `AdditionalInfo.Subject` | `subject` |
| `AdditionalInfo.MessageId` | `message_id` |

#### Connection Reports

| v3 Field | v4 Field |
|----------|----------|
| `Report.DestinationIp` | `destination_ip` |
| `Report.DestinationPort` | `destination_port` |
| `AdditionalInfo.Protocol` | `protocol` |
| `Source.Port` | `source_port` |
| `AdditionalInfo.AttackType` | `attack_type` |
| `AdditionalInfo.PacketCount` | `packet_count` |
| `AdditionalInfo.ByteCount` | `byte_count` |

#### Content Reports

| v3 Field | v4 Field |
|----------|----------|
| `Report.URL` or `AdditionalInfo.URL` | `url` |
| `AdditionalInfo.ContentType` | `content_type` |
| `AdditionalInfo.AttackType` | `attack_type` |

### Evidence Conversion

v3 `Attachment` array is converted to v4 `evidence` format:

```python
# v3 Format
"Attachment": [
  {
    "ContentType": "message/rfc822",
    "Description": "Spam email",
    "Data": "base64data..."
  }
]

# Converted to v4
"evidence": [
  {
    "content_type": "message/rfc822",
    "description": "Spam email",
    "payload": "base64data..."
  }
]
```

### Evidence Source Mapping

| v3 DetectionMethod | v4 evidence_source |
|-------------------|-------------------|
| Contains "spamtrap" | `spamtrap` |
| Contains "honeypot" | `honeypot` |
| Contains "user" or "manual" | `user_report` |
| Contains "scan" | `automated_scan` |
| Contains "vuln" | `vulnerability_scan` |
| Other/Missing | `automated_scan` |

### Legacy Metadata

Converted reports include metadata to track conversion:

```json
{
  "legacy_version": "3",
  "_internal": {
    "converted_from_v3": true,
    "original_version": "3.0.0"
  },
  "tags": [
    "legacy:class:Messaging",
    "legacy:type:spam"
  ]
}
```

## Migration Strategies

### Strategy 1: Gradual Migration (Recommended)

1. **Keep sending v3 reports** - Parser handles them automatically
2. **Monitor deprecation warnings** - Track which systems need updating
3. **Update report generators** - Migrate to v4 format over time
4. **Remove v3 support eventually** - Once all sources upgraded

```python
# Phase 1: Auto-conversion (current)
parser = XARFParser()
report = parser.parse(v3_or_v4_json)  # Works with both

# Phase 2: Track what needs migration
import warnings
warnings.simplefilter("always", XARFv3DeprecationWarning)
# Monitor warnings to find v3 sources

# Phase 3: Update report generators to v4
# ... upgrade systems ...

# Phase 4: Eventually require v4 only
# (Future version may remove v3 support)
```

### Strategy 2: Explicit Conversion

If you want to convert and store v4 reports:

```python
from xarf import convert_v3_to_v4, is_v3_report
import json

# Check if report is v3
data = json.loads(report_json)
if is_v3_report(data):
    # Convert to v4 and store
    v4_data = convert_v3_to_v4(data)
    v4_json = json.dumps(v4_data)
    # Store v4_json instead of original
```

### Strategy 3: Validation Mode

Validate that conversions work correctly:

```python
from xarf import XARFParser, is_v3_report, convert_v3_to_v4

parser = XARFParser(strict=True)

if is_v3_report(data):
    v4_data = convert_v3_to_v4(data)
    # Validate converted report
    report = parser.parse(v4_data)
    errors = parser.get_errors()
    if errors:
        print(f"Conversion issues: {errors}")
```

## Breaking Changes from v3

While the parser handles conversion automatically, be aware of these conceptual changes:

### 1. Class → Category Rename

v3 used `ReportClass`, v4 uses `category`:
- More accurate terminology
- Avoids confusion with programming classes

### 2. Reporter Structure

v3 had flat `ReporterInfo`, v4 has structured `reporter` object:

```python
# v3
"ReporterInfo": {
  "ReporterOrg": "...",
  "ReporterOrgEmail": "...",
  "ReporterContactEmail": "...",
  "ReporterContactName": "..."
}

# v4
"reporter": {
  "org": "...",
  "contact": "...",
  "type": "automated|manual|hybrid"
}
```

### 3. Required Fields

v4 has stricter requirements:
- `report_id` (UUID v4) is required
- `evidence_source` is required
- `reporter.type` is required

### 4. Evidence Format

Renamed for clarity:
- `Attachment` → `evidence`
- `Data` → `payload`

## Pydantic V2 Migration

The parser has been updated to Pydantic V2. If you use the models directly:

### Old (Pydantic V1)

```python
from xarf.models import XARFReport

class Config:
    allow_population_by_field_name = True
    extra = "allow"
```

### New (Pydantic V2)

```python
from xarf.models import XARFReport
from pydantic import ConfigDict

model_config = ConfigDict(
    populate_by_name=True,
    extra="allow"
)
```

Validators also changed:

```python
# Old
@validator("category")
def validate_category(cls, v):
    return v

# New
@field_validator("category")
@classmethod
def validate_category(cls, v: str) -> str:
    return v
```

## Testing Your Migration

### Test with Sample v3 Reports

```python
import pytest
from xarf import XARFParser

def test_my_v3_reports():
    """Test that our v3 reports convert correctly."""
    parser = XARFParser()

    # Your actual v3 report
    v3_json = load_sample_v3_report()

    # Should parse without errors
    report = parser.parse(v3_json)

    # Verify expected values
    assert report.category == "messaging"
    assert report.type == "spam"
    # ... test your specific fields
```

### Validate All Historical Reports

```python
from xarf import XARFParser
import json
import glob

parser = XARFParser(strict=False)
failed = []

for report_file in glob.glob("reports/*.json"):
    with open(report_file) as f:
        try:
            data = json.load(f)
            report = parser.parse(data)
            if parser.get_errors():
                failed.append((report_file, parser.get_errors()))
        except Exception as e:
            failed.append((report_file, str(e)))

if failed:
    print(f"Failed to parse {len(failed)} reports:")
    for filename, error in failed:
        print(f"  {filename}: {error}")
```

## Support and Questions

- **Specification**: See [XARF v4 Specification](https://github.com/xarf/xarf-spec)
- **Issues**: Report bugs at [GitHub Issues](https://github.com/xarf/xarf-parser-python/issues)
- **Community**: Join discussions at [XARF Discussions](https://github.com/xarf/xarf-spec/discussions)

## Timeline

- **Now (v4.0.0-alpha)**: Full v3 compatibility, deprecation warnings
- **v4.0.0-beta**: Enhanced validation, migration tools
- **v4.0.0-stable**: Production-ready, v3 support continues
- **v5.0.0 (future)**: v3 support may be removed (with advance notice)

We recommend migrating to v4 format when convenient, but there's no rush - v3 support will continue for the foreseeable future.
