"""Shared test fixtures for XARF tests.

All test data follows XARF v4 spec from xarf-core.json:
- reporter/sender use 'domain' not 'type'
- sender is required
- evidence_source is optional (recommended)
"""

from typing import Any

import pytest


def create_v4_contact(
    org: str = "Test Organization",
    contact: str = "abuse@test.org",
    domain: str = "test.org",
) -> dict[str, str]:
    """Create a v4-compliant contact_info object.

    Per xarf-core.json $defs/contact_info:
    - org: Organization name (required)
    - contact: Contact email (required)
    - domain: Organization domain (required)
    """
    return {
        "org": org,
        "contact": contact,
        "domain": domain,
    }


def create_v4_base_report(
    category: str = "messaging",
    report_type: str = "spam",
    **overrides: Any,
) -> dict[str, Any]:
    """Create a v4-compliant base XARF report.

    Per xarf-core.json required fields:
    - xarf_version, report_id, timestamp
    - reporter, sender (both contact_info)
    - source_identifier, category, type

    Args:
        category: Report category (messaging, connection, content, etc.)
        report_type: Specific type within category
        **overrides: Override any field

    Returns:
        Dict with all required fields for a valid v4 report
    """
    report = {
        "xarf_version": "4.0.0",
        "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "timestamp": "2024-01-15T10:30:00Z",
        "reporter": create_v4_contact(),
        "sender": create_v4_contact(
            org="Sender Organization",
            contact="sender@sender.org",
            domain="sender.org",
        ),
        "source_identifier": "192.0.2.1",
        "source_port": 25,
        "category": category,
        "type": report_type,
    }
    report.update(overrides)
    return report


def create_v4_messaging_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant messaging report.

    Includes messaging-specific fields like protocol, smtp_from.
    """
    report = create_v4_base_report(
        category="messaging",
        report_type="spam",
        protocol="smtp",
        smtp_from="spammer@example.com",
    )
    report.update(overrides)
    return report


def create_v4_connection_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant connection report.

    Includes connection-specific fields like destination_ip, protocol.
    """
    report = create_v4_base_report(
        category="connection",
        report_type="ddos",
        destination_ip="203.0.113.1",
        protocol="tcp",
        destination_port=80,
        first_seen="2024-01-15T10:00:00Z",
    )
    report.update(overrides)
    return report


def create_v4_content_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant content report.

    Includes content-specific fields like url.
    Note: v4 uses 'phishing' not 'phishing_site'.
    """
    report = create_v4_base_report(
        category="content",
        report_type="phishing",  # v4 uses 'phishing' not 'phishing_site'
        url="https://phishing.example.com",
    )
    report.update(overrides)
    return report


def create_v4_infrastructure_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant infrastructure report."""
    report = create_v4_base_report(
        category="infrastructure",
        report_type="open_resolver",
    )
    report.update(overrides)
    return report


def create_v4_copyright_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant copyright report."""
    report = create_v4_base_report(
        category="copyright",
        report_type="dmca",
    )
    report.update(overrides)
    return report


def create_v4_vulnerability_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant vulnerability report."""
    report = create_v4_base_report(
        category="vulnerability",
        report_type="exposed_service",
    )
    report.update(overrides)
    return report


def create_v4_reputation_report(**overrides: Any) -> dict[str, Any]:
    """Create a v4-compliant reputation report."""
    report = create_v4_base_report(
        category="reputation",
        report_type="blocklist",
    )
    report.update(overrides)
    return report


# Pytest fixtures for common test data
@pytest.fixture
def v4_contact() -> dict[str, str]:
    """Fixture for v4-compliant contact info."""
    return create_v4_contact()


@pytest.fixture
def v4_base_report() -> dict[str, Any]:
    """Fixture for v4-compliant base report."""
    return create_v4_base_report()


@pytest.fixture
def v4_messaging_report() -> dict[str, Any]:
    """Fixture for v4-compliant messaging report."""
    return create_v4_messaging_report()


@pytest.fixture
def v4_connection_report() -> dict[str, Any]:
    """Fixture for v4-compliant connection report."""
    return create_v4_connection_report()


@pytest.fixture
def v4_content_report() -> dict[str, Any]:
    """Fixture for v4-compliant content report."""
    return create_v4_content_report()
