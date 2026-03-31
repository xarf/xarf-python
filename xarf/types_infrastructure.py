"""XARF v4 Infrastructure category type definitions.

Mirrors ``types-infrastructure.ts`` from the JavaScript reference implementation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict

from xarf.models import XARFReport


class InfrastructureBaseReport(XARFReport):
    """Shared fields for all infrastructure-category reports.

    Attributes:
        category: Always ``"infrastructure"`` for this category.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Literal["infrastructure"]


class BotnetReport(InfrastructureBaseReport):
    """Infrastructure - Botnet report.

    Attributes:
        type: Always ``"botnet"``.
        compromise_evidence: Evidence that the host is part of a botnet (required).
        bot_capabilities: Capabilities of the bot (e.g. ``["ddos", "spam"]``).
        c2_protocol: Command-and-control protocol used (e.g. ``"irc"``, ``"http"``).
        c2_server: Hostname or IP of the C2 server.
        malware_family: Malware family associated with the botnet.
    """

    type: Literal["botnet"]
    compromise_evidence: str
    bot_capabilities: list[str] | None = None
    c2_protocol: str | None = None
    c2_server: str | None = None
    malware_family: str | None = None


class CompromisedServerReport(InfrastructureBaseReport):
    """Infrastructure - Compromised Server report.

    Attributes:
        type: Always ``"compromised_server"``.
        compromise_method: How the server was compromised (required,
            e.g. ``"brute_force"``).
    """

    type: Literal["compromised_server"]
    compromise_method: str


# Category-level union alias (for isinstance checks and type annotations).
InfrastructureReport = BotnetReport | CompromisedServerReport
"""Union of all infrastructure-category report types."""
