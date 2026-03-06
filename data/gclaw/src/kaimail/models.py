"""Pydantic models for email data structures."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EmailCategory(str, Enum):
    """Email classification categories.

    Priority order (highest to lowest):
    1. security - always flag security alerts
    2. travel - flights, hotels, cruises
    3. github_notification - GitHub CI/PR/issue
    4. restaurant_reservation - local restaurant bookings
    5. finance - invoices, billing, payments
    6. ecommerce_order - order confirmations/shipping
    7. health_insurance - medical/insurance
    8. receipt - payment confirmations
    9. newsletter - Substack, known newsletters
    10. entertainment - streaming/gaming/events
    11. social - LinkedIn/Discord digests
    12. professional_event - conferences/webinars
    13. kids_education - kids apps/school
    14. local_food - food/restaurant promos
    15. notification - generic system notifications
    16. promotional - catch-all marketing
    17. personal - default fallback
    """

    # High priority - security & travel
    SECURITY = "security"
    TRAVEL = "travel"

    # GitHub-specific notifications
    GITHUB_NOTIFICATION = "github_notification"

    # Reservations & transactions
    RESTAURANT_RESERVATION = "restaurant_reservation"
    FINANCE = "finance"
    ECOMMERCE_ORDER = "ecommerce_order"
    HEALTH_INSURANCE = "health_insurance"
    RECEIPT = "receipt"

    # Content & updates
    NEWSLETTER = "newsletter"
    ENTERTAINMENT = "entertainment"
    SOCIAL = "social"
    PROFESSIONAL_EVENT = "professional_event"
    KIDS_EDUCATION = "kids_education"
    LOCAL_FOOD = "local_food"

    # Generic categories
    NOTIFICATION = "notification"
    PROMOTIONAL = "promotional"
    PERSONAL = "personal"
    UNKNOWN = "unknown"


class Email(BaseModel):
    """Raw email message from Gmail API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    thread_id: str = Field(alias="threadId")
    date: str
    from_address: str = Field(alias="from")
    subject: str
    labels: list[str] = Field(default_factory=list)


class ThreadMessage(BaseModel):
    """A single message within a thread."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    from_address: str = Field(alias="from")
    to: str
    subject: str
    date: str
    body: str
    attachments: list[str] = Field(default_factory=list)


class Thread(BaseModel):
    """Email thread containing one or more messages."""

    thread_id: str
    messages: list[ThreadMessage] = Field(default_factory=list)
    message_count: int = 0

    @property
    def primary_message(self) -> Optional[ThreadMessage]:
        """Get the first (original) message in the thread."""
        return self.messages[0] if self.messages else None

    @property
    def subject(self) -> str:
        """Get thread subject from primary message."""
        return self.primary_message.subject if self.primary_message else ""


class ParsedEmail(BaseModel):
    """Parsed and cleaned email with extracted metadata."""

    model_config = ConfigDict(use_enum_values=True)

    id: str
    thread_id: str
    date: datetime
    sender_email: str
    sender_name: str
    sender_domain: str
    subject: str
    subject_clean: str  # Without Re:, Fwd:, etc.
    body_text: str  # Cleaned body (stripped HTML, footers, etc.)
    body_preview: str  # First ~200 chars
    labels: list[str] = Field(default_factory=list)
    category: EmailCategory = EmailCategory.UNKNOWN
    is_forwarded: bool = False
    is_reply: bool = False
    has_attachments: bool = False


class EmailBatch(BaseModel):
    """Batch of emails fetched in a single query."""

    emails: list[Email] = Field(default_factory=list)
    query: str
    fetched_at: datetime = Field(default_factory=datetime.now)
    next_page_token: Optional[str] = None

    @property
    def count(self) -> int:
        return len(self.emails)

    @property
    def ids(self) -> list[str]:
        return [e.id for e in self.emails]
