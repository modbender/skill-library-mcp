"""Bot context for access control and isolation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BotContext:
    """
    Per-bot access control context.

    Each consumer bot (digest, travel, health, etc.) gets its own context
    that restricts which emails it can access.

    Example:
        digest_ctx = BotContext(
            bot_id="digest",
            allowed_labels=["Thoughts", "INBOX"],
            max_results=100,
        )

        travel_ctx = BotContext(
            bot_id="travel",
            allowed_labels=["Travel"],
            allowed_senders=["booking.com", "expedia.com", "airlines"],
            max_results=50,
        )
    """

    bot_id: str
    allowed_labels: list[str] = field(default_factory=list)
    allowed_senders: list[str] = field(default_factory=list)
    max_results: int = 50
    readonly: bool = True

    def can_access_label(self, label: str) -> bool:
        """Check if this bot can access a specific label."""
        if not self.allowed_labels:
            return True  # Empty = no restrictions
        return label in self.allowed_labels

    def can_access_sender(self, sender_domain: str) -> bool:
        """Check if this bot can access emails from a sender domain."""
        if not self.allowed_senders:
            return True  # Empty = no restrictions
        return any(allowed.lower() in sender_domain.lower() for allowed in self.allowed_senders)

    def filter_labels_for_query(self, labels: list[str]) -> list[str]:
        """Filter requested labels to only those allowed."""
        if not self.allowed_labels:
            return labels
        return [lbl for lbl in labels if lbl in self.allowed_labels]

    def build_query(
        self,
        labels: Optional[list[str]] = None,
        senders: Optional[list[str]] = None,
        newer_than_days: Optional[int] = None,
        is_unread: bool = False,
        extra_query: str = "",
    ) -> str:
        """
        Build a Gmail search query respecting bot constraints.

        Raises ValueError if requested labels/senders are outside allowlist.
        """
        parts: list[str] = []

        # Handle labels
        if labels:
            allowed = self.filter_labels_for_query(labels)
            if len(allowed) != len(labels):
                disallowed = set(labels) - set(allowed)
                raise ValueError(f"Bot '{self.bot_id}' cannot access labels: {disallowed}")
            for label in allowed:
                parts.append(f"label:{label}")
        elif self.allowed_labels:
            # If no labels specified but we have restrictions, query all allowed
            label_query = " OR ".join(f"label:{lbl}" for lbl in self.allowed_labels)
            if len(self.allowed_labels) > 1:
                parts.append(f"({label_query})")
            else:
                parts.append(label_query)

        # Handle senders
        if senders:
            for sender in senders:
                if not self.can_access_sender(sender):
                    raise ValueError(f"Bot '{self.bot_id}' cannot access sender: {sender}")
                parts.append(f"from:{sender}")
        elif self.allowed_senders:
            # Auto-filter to allowed senders
            sender_query = " OR ".join(f"from:{s}" for s in self.allowed_senders)
            if len(self.allowed_senders) > 1:
                parts.append(f"({sender_query})")
            else:
                parts.append(sender_query)

        # Time filter
        if newer_than_days:
            parts.append(f"newer_than:{newer_than_days}d")

        # Unread filter
        if is_unread:
            parts.append("is:unread")

        # Extra query
        if extra_query:
            parts.append(extra_query)

        return " ".join(parts)

    def enforce_max_results(self, requested: int) -> int:
        """Cap requested results to bot's maximum."""
        return min(requested, self.max_results)
