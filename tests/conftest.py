"""Shared pytest fixtures, constants, and helpers for the XARF test suite.

This module provides:

- Directory path constants pointing to sample data locations.
- A helper function :func:`_load_spec_samples` to enumerate canonical spec samples.
- Module-level valid report dicts used across multiple test files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Directory constants
# ---------------------------------------------------------------------------

#: Path to the canonical xarf-spec v4 samples (relative to this file's location).
SPEC_SAMPLES_DIR: Path = (
    Path(__file__).parent.parent.parent / "xarf-spec" / "samples" / "v4"
)

#: Root of the shared parser-test suite samples bundled as a git subtree.
SHARED_SAMPLES_DIR: Path = Path(__file__).parent / "shared" / "samples"

#: Convenience pointer to the invalid shared samples.
INVALID_SAMPLES_DIR: Path = SHARED_SAMPLES_DIR / "invalid"

#: Convenience pointer to the v3 backward-compatibility samples.
V3_SAMPLES_DIR: Path = SHARED_SAMPLES_DIR / "valid" / "v3"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_spec_samples() -> list[tuple[Path, str]]:
    """Return a list of ``(path, stem)`` tuples for every JSON file in SPEC_SAMPLES_DIR.

    Returns:
        A sorted list of ``(path, stem)`` tuples.  Returns an empty list when
        :data:`SPEC_SAMPLES_DIR` does not exist (e.g. in CI environments that do
        not have the full monorepo checked out).
    """
    if not SPEC_SAMPLES_DIR.exists():
        return []
    return [(p, p.stem) for p in sorted(SPEC_SAMPLES_DIR.glob("*.json"))]


# ---------------------------------------------------------------------------
# Shared contact info block reused across report dicts
# ---------------------------------------------------------------------------

_CONTACT: dict[str, str] = {
    "org": "ACME Security",
    "contact": "abuse@acme.example",
    "domain": "acme.example",
}

# ---------------------------------------------------------------------------
# Module-level valid report dicts
# ---------------------------------------------------------------------------

#: Minimal valid ``connection/ddos`` report dict.
VALID_DDOS_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "connection",
    "type": "ddos",
    "evidence_source": "honeypot",
    "source_port": 12345,
    "destination_ip": "203.0.113.10",
    "protocol": "tcp",
    "first_seen": "2024-01-15T09:00:00Z",
}

#: Minimal valid ``messaging/spam`` report dict.  Uses ``protocol="sms"`` to
#: avoid the ``smtp_from`` requirement that applies to SMTP spam reports.
VALID_SPAM_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "messaging",
    "type": "spam",
    "evidence_source": "honeypot",
    "protocol": "sms",
}

#: Minimal valid ``content/phishing`` report dict.
VALID_PHISHING_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "content",
    "type": "phishing",
    "evidence_source": "honeypot",
    "url": "https://phishing.example.com/login",
}

#: Minimal valid ``infrastructure/botnet`` report dict.
VALID_BOTNET_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b812-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "infrastructure",
    "type": "botnet",
    "evidence_source": "honeypot",
    "compromise_evidence": "C2 communication observed",
}

#: Minimal valid ``copyright/copyright`` report dict.
VALID_COPYRIGHT_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b813-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "copyright",
    "type": "copyright",
    "evidence_source": "honeypot",
    "infringing_url": "https://piracy.example.com/movie.mp4",
    "infringement_type": "Copyright",
}

#: Minimal valid ``vulnerability/cve`` report dict.
VALID_CVE_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b814-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "vulnerability",
    "type": "cve",
    "evidence_source": "honeypot",
    "cve_id": "CVE-2024-1234",
    "service": "Apache httpd",
    "service_port": 80,
    "cvss_score": 9.8,
}

#: Minimal valid ``reputation/blocklist`` report dict.
VALID_BLOCKLIST_REPORT: dict[str, Any] = {
    "xarf_version": "4.2.0",
    "report_id": "6ba7b815-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2024-01-15T10:30:00Z",
    "reporter": _CONTACT,
    "sender": _CONTACT,
    "source_identifier": "192.0.2.1",
    "category": "reputation",
    "type": "blocklist",
    "evidence_source": "honeypot",
    "threat_type": "spam",
    "blocklist_name": "test-blocklist",
    "reason": "Spam source",
}
