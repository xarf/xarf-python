"""XARF v4 Connection category type definitions.

Mirrors ``types-connection.ts`` from the JavaScript reference implementation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict

from xarf.models import XARFReport


class ConnectionBaseReport(XARFReport):
    """Shared fields for all connection-category reports.

    Attributes:
        category: Always ``"connection"`` for this category.
        first_seen: ISO 8601 timestamp of when the activity was first observed.
        protocol: Network protocol (e.g. ``"tcp"``, ``"udp"``, ``"icmp"``).
        destination_ip: Destination IP address targeted by the source.
        destination_port: Destination port number.
        last_seen: ISO 8601 timestamp of when the activity was last observed.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Literal["connection"]
    first_seen: str
    protocol: str
    destination_ip: str | None = None
    destination_port: int | None = None
    last_seen: str | None = None


class LoginAttackReport(ConnectionBaseReport):
    """Connection - Login Attack report.

    Attributes:
        type: Always ``"login_attack"``.
    """

    type: Literal["login_attack"]


class PortScanReport(ConnectionBaseReport):
    """Connection - Port Scan report.

    Attributes:
        type: Always ``"port_scan"``.
    """

    type: Literal["port_scan"]


class DdosReport(ConnectionBaseReport):
    """Connection - DDoS (Distributed Denial of Service) report.

    Attributes:
        type: Always ``"ddos"``.
        amplification_factor: Amplification factor used in the attack.
        attack_vector: Attack vector description (e.g. ``"udp_flood"``, ``"ntp"``).
        duration_seconds: Duration of the attack in seconds.
        mitigation_applied: Whether active mitigation was applied.
        peak_bps: Peak attack bandwidth in bits per second.
        peak_pps: Peak attack rate in packets per second.
        service_impact: Description of the impact on services.
        threshold_exceeded: Description of which thresholds were exceeded.
    """

    type: Literal["ddos"]
    amplification_factor: float | None = None
    attack_vector: str | None = None
    duration_seconds: int | None = None
    mitigation_applied: bool | None = None
    peak_bps: int | None = None
    peak_pps: int | None = None
    service_impact: str | None = None
    threshold_exceeded: str | None = None


class InfectedHostReport(ConnectionBaseReport):
    """Connection - Infected Host report.

    Attributes:
        type: Always ``"infected_host"``.
        bot_type: Type of bot or malicious agent (required).
        accepts_cookies: Whether the bot accepts cookies.
        api_endpoints_accessed: API endpoints accessed by the bot.
        behavior_pattern: Description of observed behaviour patterns.
        bot_name: Known name of the bot or malware family.
        follows_crawl_delay: Whether the bot respects crawl-delay directives.
        javascript_execution: Whether the bot executes JavaScript.
        request_rate: Observed request rate in requests per second.
        respects_robots_txt: Whether the bot respects ``robots.txt``.
        total_requests: Total number of requests observed.
        user_agent: User-Agent string used by the bot.
        verification_status: Status of bot verification checks.
    """

    type: Literal["infected_host"]
    bot_type: str
    accepts_cookies: bool | None = None
    api_endpoints_accessed: list[str] | None = None
    behavior_pattern: str | None = None
    bot_name: str | None = None
    follows_crawl_delay: bool | None = None
    javascript_execution: bool | None = None
    request_rate: float | None = None
    respects_robots_txt: bool | None = None
    total_requests: int | None = None
    user_agent: str | None = None
    verification_status: str | None = None


class ReconnaissanceReport(ConnectionBaseReport):
    """Connection - Reconnaissance report.

    Attributes:
        type: Always ``"reconnaissance"``.
        probed_resources: List of resources probed by the source (required).
        automated_tool: Whether an automated tool was detected.
        http_methods: HTTP methods observed in the reconnaissance activity.
        resource_categories: Categories of resources targeted.
        response_codes: HTTP response codes returned to the source.
        successful_probes: Resources that responded successfully.
        total_probes: Total number of probe attempts.
        user_agent: User-Agent string used during reconnaissance.
    """

    type: Literal["reconnaissance"]
    probed_resources: list[str]
    automated_tool: bool | None = None
    http_methods: list[str] | None = None
    resource_categories: list[str] | None = None
    response_codes: list[int] | None = None
    successful_probes: list[str] | None = None
    total_probes: int | None = None
    user_agent: str | None = None


class ScrapingReport(ConnectionBaseReport):
    """Connection - Scraping report.

    Attributes:
        type: Always ``"scraping"``.
        total_requests: Total number of requests made by the scraper (required).
        bot_signature: Signature or fingerprint of the scraping tool.
        concurrent_connections: Number of concurrent connections observed.
        data_volume: Total volume of data scraped in bytes.
        request_rate: Request rate in requests per second.
        respects_robots_txt: Whether the scraper respects ``robots.txt``.
        scraping_pattern: Description of the scraping pattern observed.
        session_duration: Duration of the scraping session in seconds.
        target_content: Type of content being scraped.
        unique_urls: Number of unique URLs accessed.
        user_agent: User-Agent string used by the scraper.
    """

    type: Literal["scraping"]
    total_requests: int
    bot_signature: str | None = None
    concurrent_connections: int | None = None
    data_volume: int | None = None
    request_rate: float | None = None
    respects_robots_txt: bool | None = None
    scraping_pattern: str | None = None
    session_duration: int | None = None
    target_content: str | None = None
    unique_urls: int | None = None
    user_agent: str | None = None


class SqlInjectionReport(ConnectionBaseReport):
    """Connection - SQL Injection report.

    Attributes:
        type: Always ``"sql_injection"``.
        attack_technique: SQL injection technique used (e.g. ``"blind"``, ``"union"``).
        attempts_count: Number of injection attempts observed.
        http_method: HTTP method used (e.g. ``"GET"``, ``"POST"``).
        injection_point: Where injection was attempted (e.g. ``"query_param"``).
        payload_sample: Sample of the injection payload observed.
        target_url: URL targeted by the SQL injection attempt.
    """

    type: Literal["sql_injection"]
    attack_technique: str | None = None
    attempts_count: int | None = None
    http_method: str | None = None
    injection_point: str | None = None
    payload_sample: str | None = None
    target_url: str | None = None


class VulnerabilityScanReport(ConnectionBaseReport):
    """Connection - Vulnerability Scan report.

    Attributes:
        type: Always ``"vulnerability_scan"``.
        scan_type: Type of vulnerability scan (e.g. ``"port_scan"``) (required).
        scan_rate: Scan rate in probes per second.
        scanner_signature: Identified scanner tool or signature.
        targeted_ports: List of ports targeted by the scan.
        targeted_services: List of services or service names targeted.
        total_requests: Total number of scan probe requests.
        user_agent: User-Agent string used by the scanner.
        vulnerabilities_probed: CVE IDs or vulnerability names probed.
    """

    type: Literal["vulnerability_scan"]
    scan_type: str
    scan_rate: float | None = None
    scanner_signature: str | None = None
    targeted_ports: list[int] | None = None
    targeted_services: list[str] | None = None
    total_requests: int | None = None
    user_agent: str | None = None
    vulnerabilities_probed: list[str] | None = None


# Category-level union alias (for isinstance checks and type annotations).
ConnectionReport = (
    LoginAttackReport
    | PortScanReport
    | DdosReport
    | InfectedHostReport
    | ReconnaissanceReport
    | ScrapingReport
    | SqlInjectionReport
    | VulnerabilityScanReport
)
"""Union of all connection-category report types."""
