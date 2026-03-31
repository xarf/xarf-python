"""XARF v4 Messaging category type definitions.

Mirrors ``types-messaging.ts`` from the JavaScript reference implementation.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from xarf.models import XARFReport


class MessagingBaseReport(XARFReport):
    """Shared fields for all messaging-category reports.

    Attributes:
        category: Always ``"messaging"`` for this category.
        protocol: Messaging protocol used (e.g. ``"smtp"``, ``"imap"``).
        sender_name: Display name of the sending party.
        smtp_from: SMTP envelope sender address (MAIL FROM).
        subject: Subject line of the message.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    category: Literal["messaging"]
    protocol: str
    sender_name: str | None = None
    smtp_from: str | None = None
    subject: str | None = None


class SpamIndicators(BaseModel):
    """Spam analysis indicators found in the message.

    Attributes:
        suspicious_links: List of suspicious URLs found in the message.
        commercial_content: Whether the message contains commercial content.
        bulk_characteristics: Whether the message exhibits bulk-sending patterns.
    """

    model_config = ConfigDict(populate_by_name=True)

    suspicious_links: list[str] | None = None
    commercial_content: bool | None = None
    bulk_characteristics: bool | None = None


class SpamReport(MessagingBaseReport):
    """Messaging - Spam report.

    Attributes:
        type: Always ``"spam"``.
        language: Detected language of the message (e.g. ``"en"``).
        message_id: Message-ID header value.
        recipient_count: Number of recipients the message was sent to.
        smtp_to: SMTP envelope recipient address (RCPT TO).
        spam_indicators: Structured spam analysis indicators.
        user_agent: User-Agent or X-Mailer header value.
    """

    type: Literal["spam"]
    language: str | None = None
    message_id: str | None = None
    recipient_count: int | None = None
    smtp_to: str | None = None
    spam_indicators: SpamIndicators | None = None
    user_agent: str | None = None


class BulkIndicators(BaseModel):
    """Bulk messaging indicators found in the message.

    Attributes:
        high_volume: Whether the message was sent in high volume.
        template_based: Whether the message is template-generated.
        commercial_sender: Whether the sender is a commercial entity.
    """

    model_config = ConfigDict(populate_by_name=True)

    high_volume: bool | None = None
    template_based: bool | None = None
    commercial_sender: bool | None = None


class BulkMessagingReport(MessagingBaseReport):
    """Messaging - Bulk Messaging report.

    Attributes:
        type: Always ``"bulk_messaging"``.
        recipient_count: Number of recipients (required for bulk reports).
        bulk_indicators: Structured bulk-sending indicators.
        opt_in_evidence: Whether evidence of recipient opt-in exists.
        unsubscribe_provided: Whether an unsubscribe mechanism was provided.
    """

    type: Literal["bulk_messaging"]
    recipient_count: int
    bulk_indicators: BulkIndicators | None = None
    opt_in_evidence: bool | None = None
    unsubscribe_provided: bool | None = None


# Category-level union alias (for isinstance checks and type annotations).
MessagingReport = SpamReport | BulkMessagingReport
"""Union of all messaging-category report types."""
