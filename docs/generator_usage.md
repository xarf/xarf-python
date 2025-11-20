# XARF Generator Usage Guide

The `XARFGenerator` class provides a comprehensive API for generating XARF v4.0.0 compliant reports programmatically.

## Installation

```python
from xarf import XARFGenerator
```

## Basic Usage

### Creating a Simple Report

```python
from xarf import XARFGenerator

# Initialize the generator
generator = XARFGenerator()

# Generate a minimal report
report = generator.generate_report(
    category="connection",
    report_type="ddos",
    source_identifier="192.0.2.100",
    reporter_contact="abuse@example.com"
)

print(report)
```

### Adding Organization Information

```python
report = generator.generate_report(
    category="content",
    report_type="phishing",
    source_identifier="203.0.113.50",
    reporter_contact="abuse@example.com",
    reporter_org="Security Operations Team"
)
```

### Reporting on Behalf of Another Organization

```python
report = generator.generate_report(
    category="copyright",
    report_type="infringement",
    source_identifier="198.51.100.25",
    reporter_contact="reporter@agency.com",
    reporter_org="Anti-Piracy Agency",
    on_behalf_of={
        "org": "Copyright Holder Inc.",
        "contact": "legal@copyrightholder.com"
    }
)
```

## Adding Evidence

### Creating Evidence Items

```python
# Create evidence with automatic hashing
evidence = generator.add_evidence(
    content_type="text/plain",
    description="Server access log excerpt showing malicious activity",
    payload="2025-01-20 10:15:23 192.0.2.100 GET /admin/backdoor.php"
)

# Use evidence in a report
report = generator.generate_report(
    category="connection",
    report_type="sql_injection",
    source_identifier="192.0.2.100",
    reporter_contact="security@example.com",
    evidence=[evidence]
)
```

### Multiple Evidence Items

```python
# Log evidence
log_evidence = generator.add_evidence(
    content_type="text/plain",
    description="Firewall logs showing attack pattern",
    payload="[BLOCK] 192.0.2.100 -> 203.0.113.50:443 SYN flood detected"
)

# Screenshot evidence
screenshot_evidence = generator.add_evidence(
    content_type="image/png",
    description="Screenshot of phishing page",
    payload="iVBORw0KGgoAAAANSUhEUg..."  # Base64 encoded image
)

report = generator.generate_report(
    category="content",
    report_type="phishing",
    source_identifier="192.0.2.100",
    reporter_contact="abuse@example.com",
    evidence=[log_evidence, screenshot_evidence]
)
```

## Advanced Features

### Full Report with All Optional Fields

```python
report = generator.generate_report(
    category="vulnerability",
    report_type="cve",
    source_identifier="192.0.2.150",
    reporter_contact="security@research.org",
    reporter_org="Security Research Lab",
    reporter_type="manual",
    evidence_source="researcher_analysis",
    description="Critical remote code execution vulnerability in web server",
    severity="critical",
    confidence=0.95,
    tags=["cve-2025-12345", "rce", "critical", "web-server"],
    occurrence={
        "start": "2025-01-20T10:00:00Z",
        "end": "2025-01-20T11:00:00Z"
    },
    target={
        "ip": "203.0.113.100",
        "port": 443,
        "url": "https://vulnerable-server.example.com/admin"
    }
)
```

### Adding Category-Specific Fields

Each XARF category supports specific fields. You can add them using `additional_fields`:

```python
# DDoS attack report with connection-specific fields
report = generator.generate_report(
    category="connection",
    report_type="ddos",
    source_identifier="192.0.2.100",
    reporter_contact="abuse@example.com",
    additional_fields={
        "destination_ip": "203.0.113.100",
        "destination_port": 80,
        "protocol": "tcp",
        "attack_vector": "syn_flood",
        "peak_pps": 250000,
        "peak_bps": 1200000000,
        "duration_seconds": 2700,
        "total_packets": 11250000,
        "total_bytes": 3240000000,
        "botnet_participation": True,
        "mitigation_applied": True
    }
)
```

## Generating Sample Reports

### For Testing and Development

```python
# Generate a complete sample report with random data
sample_report = generator.generate_sample_report(
    category="connection",
    report_type="ddos",
    include_evidence=True,
    include_optional=True
)

# Generate minimal sample without optional fields
minimal_sample = generator.generate_sample_report(
    category="messaging",
    report_type="spam",
    include_evidence=False,
    include_optional=False
)
```

## All Supported Categories and Types

### Abuse
- `ddos` - DDoS attacks
- `malware` - Malware distribution
- `phishing` - Phishing attempts
- `spam` - Spam messages
- `scanner` - Port scanning

### Connection
- `compromised` - Compromised systems
- `botnet` - Botnet activity
- `malicious_traffic` - Malicious network traffic
- `ddos` - DDoS participation
- `port_scan` - Port scanning
- `login_attack` - Brute force attacks
- `sql_injection` - SQL injection attempts
- `reconnaissance` - Network reconnaissance
- `scraping` - Web scraping
- `vuln_scanning` - Vulnerability scanning
- `bot` - Bot activity
- `infected_host` - Infected hosts

### Content
- `illegal` - Illegal content
- `malicious` - Malicious content
- `policy_violation` - Policy violations
- `phishing` - Phishing pages
- `malware` - Malware hosting
- `fraud` - Fraudulent content
- `exposed_data` - Data exposure
- `csam` / `csem` - Child exploitation material
- `brand_infringement` - Brand infringement
- `suspicious_registration` - Suspicious registrations
- `remote_compromise` - Remote compromise

### Copyright
- `infringement` - Copyright infringement
- `dmca` - DMCA violations
- `trademark` - Trademark infringement
- `p2p` - P2P file sharing
- `cyberlocker` - Cyberlocker abuse
- `link_site` - Link sites
- `ugc_platform` - UGC platform violations
- `usenet` - Usenet violations
- `copyright` - Generic copyright issues

### Infrastructure
- `botnet` - Botnet infrastructure
- `compromised_server` - Compromised servers

### Messaging
- `bulk_messaging` - Bulk messaging
- `spam` - Spam messages

### Reputation
- `blocklist` - Blocklist entries
- `threat_intelligence` - Threat intelligence

### Vulnerability
- `cve` - CVE vulnerabilities
- `misconfiguration` - Security misconfigurations
- `open_service` - Open services

## Utility Methods

### Generate UUID

```python
report_id = generator.generate_uuid()
# e.g., "550e8400-e29b-41d4-a716-446655440000"
```

### Generate Timestamp

```python
timestamp = generator.generate_timestamp()
# e.g., "2025-01-20T14:30:45Z"
```

### Generate Hash

```python
# SHA256 hash (default)
hash_sha256 = generator.generate_hash("data to hash")

# Other algorithms
hash_sha512 = generator.generate_hash("data", "sha512")
hash_sha1 = generator.generate_hash("data", "sha1")
hash_md5 = generator.generate_hash("data", "md5")
```

### Random Evidence Generation

```python
# Generate random evidence for testing
evidence = generator.generate_random_evidence(
    category="connection",
    description="Test evidence"
)
```

## Validation

The generator automatically validates:

- Category names (must be one of 8 valid categories)
- Type names (must be valid for the category)
- Reporter type (automated, manual, hybrid)
- Evidence source (valid evidence collection method)
- Severity levels (low, medium, high, critical)
- Confidence scores (0.0 to 1.0)
- Required field presence
- Data format consistency

## Error Handling

```python
from xarf import XARFGenerator, XARFError

generator = XARFGenerator()

try:
    report = generator.generate_report(
        category="invalid_category",  # Invalid!
        report_type="test",
        source_identifier="192.0.2.1",
        reporter_contact="abuse@example.com"
    )
except XARFError as e:
    print(f"Generation failed: {e}")
```

## JSON Serialization

All generated reports are JSON-serializable:

```python
import json

report = generator.generate_report(
    category="connection",
    report_type="ddos",
    source_identifier="192.0.2.100",
    reporter_contact="abuse@example.com"
)

# Serialize to JSON
json_string = json.dumps(report, indent=2)

# Save to file
with open("xarf_report.json", "w") as f:
    json.dump(report, f, indent=2)
```

## Best Practices

1. **Always include descriptive information**: Use the `description` field to provide context
2. **Add evidence when possible**: Include logs, screenshots, or other supporting data
3. **Set appropriate severity**: Use severity levels to indicate impact
4. **Use confidence scores**: Indicate your certainty about the report
5. **Tag reports appropriately**: Use tags for categorization and searching
6. **Include occurrence times**: Specify when the incident occurred
7. **Provide target information**: Include affected systems/resources
8. **Use proper evidence types**: Match evidence content_type to actual data
9. **Hash all evidence**: The generator automatically computes hashes
10. **Validate before sending**: Ensure all required fields are present

## Integration Example

```python
import json
from xarf import XARFGenerator

def create_abuse_report(source_ip, evidence_logs, severity="medium"):
    """Create an abuse report from detected incidents."""
    generator = XARFGenerator()

    # Prepare evidence
    evidence_items = []
    for log in evidence_logs:
        evidence_items.append(
            generator.add_evidence(
                content_type="text/plain",
                description=f"Log from {log['timestamp']}",
                payload=log['content']
            )
        )

    # Generate report
    report = generator.generate_report(
        category="connection",
        report_type="malicious_traffic",
        source_identifier=source_ip,
        reporter_contact="security@example.com",
        reporter_org="Security Operations Center",
        evidence=evidence_items,
        severity=severity,
        tags=["automated", "ids", "malicious"]
    )

    return report

# Usage
logs = [
    {"timestamp": "2025-01-20 10:15:23", "content": "Malicious packet detected"},
    {"timestamp": "2025-01-20 10:15:24", "content": "Multiple attempts blocked"}
]

report = create_abuse_report("192.0.2.100", logs, "high")
print(json.dumps(report, indent=2))
```

## Security Considerations

1. **UUID Generation**: Uses `uuid.uuid4()` for cryptographically secure random UUIDs
2. **Random Data**: Uses `secrets` module for secure random generation
3. **Hash Algorithms**: Supports SHA-256, SHA-512, SHA-1, and MD5
4. **Input Validation**: All inputs are validated before report generation
5. **Type Safety**: Full type hints for IDE support and static analysis
6. **No Sensitive Data**: Never include credentials or sensitive PII in reports

## Further Reading

- [XARF Specification](https://xarf.org)
- [XARF Parser Documentation](../README.md)
- [GitHub Repository](https://github.com/xarf/xarf-parser-python)
