"""Email fetcher with deduplication and bot context enforcement."""

import os
from typing import Optional

from kaimail.bot_context import BotContext
from kaimail.classifier import EmailClassifier
from kaimail.client import GogGmailClient
from kaimail.models import ParsedEmail
from kaimail.parser import EmailParser
from kaimail.store import EmailStore


class EmailFetcher:
    """
    Fetch emails with bot context enforcement and deduplication.

    The fetcher is the main entry point for bots to get emails.
    It enforces access controls and handles the fetch → parse → classify → store pipeline.
    """

    def __init__(
        self,
        client: GogGmailClient,
        parser: EmailParser,
        classifier: EmailClassifier,
        store: EmailStore,
        context: BotContext,
    ):
        self.client = client
        self.parser = parser
        self.classifier = classifier
        self.store = store
        self.context = context

    @classmethod
    def create(
        cls,
        context: BotContext,
        store_path: str = "memory/email-store",
        account: str = os.environ.get("GCLAW_GMAIL_ACCOUNT", "your@gmail.com"),
        keyring_password: Optional[str] = None,
    ) -> "EmailFetcher":
        """Create a fetcher with all dependencies."""
        return cls(
            client=GogGmailClient(account=account, keyring_password=keyring_password),
            parser=EmailParser(),
            classifier=EmailClassifier(),
            store=EmailStore(base_path=store_path),
            context=context,
        )

    def fetch(
        self,
        labels: Optional[list[str]] = None,
        senders: Optional[list[str]] = None,
        newer_than_days: Optional[int] = None,
        is_unread: bool = False,
        max_results: int = 50,
        extra_query: str = "",
        skip_seen: bool = True,
    ) -> list[ParsedEmail]:
        """
        Fetch emails matching criteria, respecting bot context.

        Args:
            labels: Gmail labels to search (must be in bot's allowlist)
            senders: Sender addresses/domains to filter
            newer_than_days: Only fetch emails newer than N days
            is_unread: Only fetch unread emails
            max_results: Maximum results (capped by bot's max_results)
            extra_query: Additional Gmail search query
            skip_seen: Skip emails already in the store (default True)

        Returns:
            List of parsed and classified emails
        """
        # Build query respecting bot constraints
        query = self.context.build_query(
            labels=labels,
            senders=senders,
            newer_than_days=newer_than_days,
            is_unread=is_unread,
            extra_query=extra_query,
        )

        # Cap results
        capped_results = self.context.enforce_max_results(max_results)

        # Fetch from Gmail
        batch = self.client.search_messages(query=query, max_results=capped_results)

        # Process each email
        parsed_emails: list[ParsedEmail] = []

        for email in batch.emails:
            # Skip if already seen
            if skip_seen and self.store.is_seen(email.id):
                continue

            # Get full thread for body content
            try:
                thread = self.client.get_thread(email.thread_id)
            except Exception:
                thread = None

            # Parse
            parsed = self.parser.parse_email(email, thread)

            # Classify
            parsed = self.classifier.classify_and_update(parsed)

            # Store
            self.store.save(parsed)

            parsed_emails.append(parsed)

        return parsed_emails

    def fetch_by_category(
        self,
        category: str,
        newer_than_days: int = 30,
        max_results: int = 50,
    ) -> list[ParsedEmail]:
        """
        Fetch emails and filter by category.

        Useful for bots that only care about specific email types.
        """
        emails = self.fetch(
            newer_than_days=newer_than_days,
            max_results=max_results,
        )

        return [e for e in emails if e.category == category]

    def get_stored(
        self,
        category: Optional[str] = None,
        limit: int = 100,
    ) -> list[ParsedEmail]:
        """
        Get previously fetched emails from the store.

        This doesn't make any gog calls - just reads from local storage.
        """
        emails = self.store.load_recent(limit=limit)

        if category:
            emails = [e for e in emails if e.category == category]

        return emails

    def get_new_since_last_fetch(
        self,
        labels: Optional[list[str]] = None,
        max_results: int = 50,
    ) -> list[ParsedEmail]:
        """
        Fetch only emails that haven't been seen before.

        This is the primary method for incremental fetching.
        """
        return self.fetch(
            labels=labels,
            max_results=max_results,
            skip_seen=True,
        )

    def mark_all_seen(self) -> int:
        """
        Mark all currently stored emails as seen.

        Returns the number of emails marked.
        """
        return self.store.sync_seen_from_stored()
