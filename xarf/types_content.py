"""XARF v4 Content category type definitions.

Mirrors ``types-content.ts`` from the JavaScript reference implementation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from xarf.models import XARFReport


class ContentBaseReport(XARFReport):
    """Shared fields for all content-category reports.

    Mirrors ``content-base.json`` in the spec.

    Attributes:
        category: Always ``"content"`` for this category.
        url: URL where the abusive content is hosted (required).
        domain: Domain associated with the abusive content.
        target_brand: Brand being targeted or impersonated.
        verified_at: ISO 8601 timestamp when the content was verified.
        verification_method: Method used to verify the content (e.g. ``"manual"``).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Literal["content"]
    url: str
    domain: str | None = None
    target_brand: str | None = None
    verified_at: str | None = None
    verification_method: str | None = None


class PhishingReport(ContentBaseReport):
    """Content - Phishing report.

    Attributes:
        type: Always ``"phishing"``.
        cloned_site: URL of the legitimate site being cloned.
        credential_fields: Form field names harvesting credentials.
        lure_type: Social-engineering lure used (e.g. ``"banking"``,
            ``"tech_support"``).
        submission_url: URL where harvested credentials are submitted.
    """

    type: Literal["phishing"]
    cloned_site: str | None = None
    credential_fields: list[str] | None = None
    lure_type: str | None = None
    submission_url: str | None = None


class MalwareReport(ContentBaseReport):
    """Content - Malware report.

    Attributes:
        type: Always ``"malware"``.
        distribution_method: How the malware is distributed (e.g. ``"drive_by"``).
        file_hashes: Map of hash algorithm to hex digest (e.g. ``{"sha256": "ab..."}``.
        malware_family: Known malware family name.
        malware_type: Malware classification (e.g. ``"trojan"``, ``"ransomware"``).
    """

    type: Literal["malware"]
    distribution_method: str | None = None
    file_hashes: dict[str, str] | None = None
    malware_family: str | None = None
    malware_type: str | None = None


class CsamReport(ContentBaseReport):
    """Content - CSAM (Child Sexual Abuse Material) report.

    Attributes:
        type: Always ``"csam"``.
        classification: CSAM classification level (required).
        detection_method: Method used to detect the content (required).
        content_removed: Whether the content has been removed.
        hash_values: Map of hash algorithm to hex digest for matching.
        media_type: Media type of the content (e.g. ``"image"``, ``"video"``).
        ncmec_report_id: NCMEC CyberTipline report ID, if filed.
    """

    type: Literal["csam"]
    classification: str
    detection_method: str
    content_removed: bool | None = None
    hash_values: dict[str, str] | None = None
    media_type: str | None = None
    ncmec_report_id: str | None = None


class CsemReport(ContentBaseReport):
    """Content - CSEM (Child Sexual Exploitation Material) report.

    Attributes:
        type: Always ``"csem"``.
        detection_method: Method used to detect the content (required).
        exploitation_type: Type of exploitation depicted (required).
        evidence_type: Types of evidence collected.
        platform: Platform where the content was found.
        reporting_obligations: Legal reporting obligations triggered.
        victim_age_range: Estimated age range of the victim(s).
    """

    type: Literal["csem"]
    detection_method: str
    exploitation_type: str
    evidence_type: list[str] | None = None
    platform: str | None = None
    reporting_obligations: list[str] | None = None
    victim_age_range: str | None = None


class ExposedDataReport(ContentBaseReport):
    """Content - Exposed Data report.

    Attributes:
        type: Always ``"exposed_data"``.
        data_types: Categories of data exposed (required,
            e.g. ``["pii", "credentials"]``).
        exposure_method: How the data was exposed (required,
            e.g. ``"misconfigured_bucket"``).
        affected_organization: Organization whose data was exposed.
        encryption_status: Encryption status of the exposed data.
        record_count: Approximate number of records exposed.
        sensitive_fields: Specific sensitive field names exposed.
    """

    type: Literal["exposed_data"]
    data_types: list[str]
    exposure_method: str
    affected_organization: str | None = None
    encryption_status: str | None = None
    record_count: int | None = None
    sensitive_fields: list[str] | None = None


class BrandInfringementReport(ContentBaseReport):
    """Content - Brand Infringement report.

    Attributes:
        type: Always ``"brand_infringement"``.
        infringement_type: Type of infringement (required, e.g. ``"trademark"``).
        legitimate_site: URL of the legitimate brand site (required).
        infringing_elements: Specific elements that infringe the brand.
        similarity_score: Similarity score between infringing and legitimate site (0–1).
    """

    type: Literal["brand_infringement"]
    infringement_type: str
    legitimate_site: str
    infringing_elements: list[str] | None = None
    similarity_score: float | None = None


class FraudReport(ContentBaseReport):
    """Content - Fraud report.

    Attributes:
        type: Always ``"fraud"``.
        fraud_type: Type of fraud (required, e.g. ``"investment_scam"``).
        claimed_entity: Entity fraudulently claimed or impersonated.
        payment_methods: Payment methods promoted or used by the fraud.
    """

    type: Literal["fraud"]
    fraud_type: str
    claimed_entity: str | None = None
    payment_methods: list[str] | None = None


class CompromiseIndicator(BaseModel):
    """A single indicator of compromise (IOC).

    Attributes:
        type: IOC type (e.g. ``"file_path"``, ``"process"``).
        value: The indicator value.
        description: Human-readable description of this IOC.
    """

    model_config = ConfigDict(populate_by_name=True)

    type: Literal[
        "file_path",
        "process",
        "network_connection",
        "user_account",
        "scheduled_task",
        "registry_key",
        "service",
    ]
    value: str
    description: str | None = None


class WebshellDetails(BaseModel):
    """Details about a webshell found on a compromised server.

    Attributes:
        family: Known webshell family name.
        capabilities: Capabilities provided by the webshell.
        password_protected: Whether the webshell is password-protected.
    """

    model_config = ConfigDict(populate_by_name=True)

    family: str | None = None
    capabilities: (
        list[
            Literal[
                "file_manager",
                "command_execution",
                "database_access",
                "network_scanning",
                "privilege_escalation",
                "persistence",
                "other",
            ]
        ]
        | None
    ) = None
    password_protected: bool | None = None


class RemoteCompromiseReport(ContentBaseReport):
    """Content - Remote Compromise report.

    Attributes:
        type: Always ``"remote_compromise"``.
        compromise_type: How the system was compromised (required, e.g. ``"webshell"``).
        affected_cms: CMS platform affected (e.g. ``"wordpress"``).
        compromise_indicators: List of indicators of compromise found.
        malicious_activities: Malicious activities observed on the host.
        persistence_mechanisms: Persistence mechanisms installed by the attacker.
        webshell_details: Details about a webshell, if present.
    """

    type: Literal["remote_compromise"]
    compromise_type: str
    affected_cms: str | None = None
    compromise_indicators: list[CompromiseIndicator] | None = None
    malicious_activities: list[str] | None = None
    persistence_mechanisms: list[str] | None = None
    webshell_details: WebshellDetails | None = None


class RegistrantDetails(BaseModel):
    """Details about the domain registrant.

    Attributes:
        email_domain: Domain of the registrant email address.
        country: Country of the registrant.
        privacy_protected: Whether WHOIS privacy protection is enabled.
        bulk_registrations: Number of bulk domain registrations by this registrant.
    """

    model_config = ConfigDict(populate_by_name=True)

    email_domain: str | None = None
    country: str | None = None
    privacy_protected: bool | None = None
    bulk_registrations: int | None = None


class SuspiciousRegistrationReport(ContentBaseReport):
    """Content - Suspicious Registration report.

    Attributes:
        type: Always ``"suspicious_registration"``.
        registration_date: ISO 8601 date when the domain was registered (required).
        suspicious_indicators: Reasons the registration is considered
            suspicious (required).
        days_since_registration: Number of days since the domain was registered.
        predicted_usage: Predicted abuse types for the domain.
        registrant_details: Details about the registrant.
        risk_score: Risk score for the registration (0–100).
        targeted_brands: Brands the domain appears to target.
    """

    type: Literal["suspicious_registration"]
    registration_date: str
    suspicious_indicators: list[str]
    days_since_registration: int | None = None
    predicted_usage: list[str] | None = None
    registrant_details: RegistrantDetails | None = None
    risk_score: float | None = None
    targeted_brands: list[str] | None = None


# Category-level union alias (for isinstance checks and type annotations).
ContentReport = (
    PhishingReport
    | MalwareReport
    | CsamReport
    | CsemReport
    | ExposedDataReport
    | BrandInfringementReport
    | FraudReport
    | RemoteCompromiseReport
    | SuspiciousRegistrationReport
)
"""Union of all content-category report types."""
