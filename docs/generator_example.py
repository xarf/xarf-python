#!/usr/bin/env python3
"""
Example usage of the XARF Generator.

This demonstrates the key features of the XARFGenerator class.
Run this after installing the xarf package: pip install -e .
"""

import json
from xarf import XARFGenerator, XARFError


def main():
    """Demonstrate XARF generator functionality."""
    print("XARF Generator Examples")
    print("=" * 80)

    generator = XARFGenerator()

    # Example 1: Simple DDoS report
    print("\n1. Simple DDoS Report")
    print("-" * 80)
    try:
        report = generator.generate_report(
            category="connection",
            report_type="ddos",
            source_identifier="192.0.2.100",
            reporter_contact="abuse@example.com",
            reporter_org="Security Operations Center"
        )
        print(json.dumps(report, indent=2))
    except XARFError as e:
        print(f"Error: {e}")

    # Example 2: Phishing report with evidence
    print("\n\n2. Phishing Report with Evidence")
    print("-" * 80)
    try:
        evidence = generator.add_evidence(
            content_type="text/html",
            description="Source code of phishing page",
            payload="<html><head><title>Login</title></head><body>Fake login form</body></html>"
        )

        report = generator.generate_report(
            category="content",
            report_type="phishing",
            source_identifier="203.0.113.50",
            reporter_contact="phishing-reports@example.com",
            reporter_org="Brand Protection Team",
            description="Phishing site impersonating our login page",
            evidence=[evidence],
            severity="high",
            confidence=0.95,
            tags=["phishing", "brand-impersonation", "credential-theft"]
        )
        print(json.dumps(report, indent=2))
    except XARFError as e:
        print(f"Error: {e}")

    # Example 3: Report on behalf of another organization
    print("\n\n3. Report on Behalf of Client")
    print("-" * 80)
    try:
        report = generator.generate_report(
            category="copyright",
            report_type="infringement",
            source_identifier="198.51.100.75",
            reporter_contact="takedown@agency.com",
            reporter_org="Copyright Protection Agency",
            on_behalf_of={
                "org": "Movie Studio Inc.",
                "contact": "legal@moviestudio.com"
            },
            description="Unauthorized distribution of copyrighted content",
            severity="medium"
        )
        print(json.dumps(report, indent=2))
    except XARFError as e:
        print(f"Error: {e}")

    # Example 4: Vulnerability report with full details
    print("\n\n4. Vulnerability Report with Full Details")
    print("-" * 80)
    try:
        log_evidence = generator.add_evidence(
            content_type="text/plain",
            description="Vulnerability scan results",
            payload="CVE-2025-12345 detected on port 443\nRemote Code Execution possible"
        )

        report = generator.generate_report(
            category="vulnerability",
            report_type="cve",
            source_identifier="192.0.2.200",
            reporter_contact="security@research.org",
            reporter_org="Security Research Lab",
            reporter_type="manual",
            evidence_source="vulnerability_scan",
            description="Critical RCE vulnerability in web server",
            evidence=[log_evidence],
            severity="critical",
            confidence=0.98,
            tags=["cve-2025-12345", "rce", "critical", "web-server"],
            occurrence={
                "start": "2025-01-20T10:00:00Z",
                "end": "2025-01-20T11:30:00Z"
            },
            target={
                "ip": "203.0.113.100",
                "port": 443,
                "url": "https://vulnerable.example.com"
            },
            additional_fields={
                "cve_id": "CVE-2025-12345",
                "cvss_score": 9.8,
                "affected_component": "web-server v2.1.0"
            }
        )
        print(json.dumps(report, indent=2))
    except XARFError as e:
        print(f"Error: {e}")

    # Example 5: Generate sample report
    print("\n\n5. Auto-Generated Sample Report")
    print("-" * 80)
    try:
        sample = generator.generate_sample_report(
            category="messaging",
            report_type="spam",
            include_evidence=True,
            include_optional=True
        )
        print(json.dumps(sample, indent=2))
    except XARFError as e:
        print(f"Error: {e}")

    # Example 6: Demonstrate utility methods
    print("\n\n6. Utility Methods")
    print("-" * 80)
    print(f"Generated UUID: {generator.generate_uuid()}")
    print(f"Generated Timestamp: {generator.generate_timestamp()}")
    print(f"SHA-256 Hash: {generator.generate_hash('test data')}")
    print(f"SHA-512 Hash: {generator.generate_hash('test data', 'sha512')}")

    # Example 7: All supported categories
    print("\n\n7. All Supported Categories and Types")
    print("-" * 80)
    for category in sorted(generator.VALID_CATEGORIES):
        types = generator.EVENT_TYPES.get(category, [])
        print(f"  {category:15} ({len(types):2} types): {', '.join(sorted(types))}")

    # Example 8: Error handling
    print("\n\n8. Error Handling Examples")
    print("-" * 80)

    # Invalid category
    try:
        generator.generate_report(
            category="invalid_category",
            report_type="test",
            source_identifier="192.0.2.1",
            reporter_contact="abuse@example.com"
        )
    except XARFError as e:
        print(f"✓ Caught expected error: {e}")

    # Invalid type for category
    try:
        generator.generate_report(
            category="connection",
            report_type="invalid_type",
            source_identifier="192.0.2.1",
            reporter_contact="abuse@example.com"
        )
    except XARFError as e:
        print(f"✓ Caught expected error: {e}")

    # Missing required field
    try:
        generator.generate_report(
            category="connection",
            report_type="ddos",
            source_identifier="",  # Empty!
            reporter_contact="abuse@example.com"
        )
    except XARFError as e:
        print(f"✓ Caught expected error: {e}")

    print("\n" + "=" * 80)
    print("Examples completed successfully!")


if __name__ == "__main__":
    main()
