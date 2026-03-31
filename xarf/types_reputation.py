"""XARF v4 Reputation category type definitions.

Mirrors ``types-reputation.ts`` from the JavaScript reference implementation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict

from xarf.models import XARFReport


class ReputationBaseReport(XARFReport):
    """Shared fields for all reputation-category reports.

    Attributes:
        category: Always ``"reputation"`` for this category.
        threat_type: Type of threat associated with this reputation entry (required).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Literal["reputation"]
    threat_type: str


class BlocklistReport(ReputationBaseReport):
    """Reputation - Blocklist report.

    Attributes:
        type: Always ``"blocklist"``.
    """

    type: Literal["blocklist"]


class ThreatIntelligenceReport(ReputationBaseReport):
    """Reputation - Threat Intelligence report.

    Attributes:
        type: Always ``"threat_intelligence"``.
    """

    type: Literal["threat_intelligence"]


# Category-level union alias (for isinstance checks and type annotations).
ReputationReport = BlocklistReport | ThreatIntelligenceReport
"""Union of all reputation-category report types."""
