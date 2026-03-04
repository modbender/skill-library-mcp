"""Email store for persistence and deduplication."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from kaimail.models import ParsedEmail


class EmailStore:
    """
    Persist fetched emails to JSONL and track seen message IDs.

    Structure:
        memory/email-store/
        ├── emails.jsonl      # All fetched emails, one per line
        ├── seen.json         # Set of seen message IDs
        └── index.json        # Optional: index by date, category, etc.
    """

    def __init__(self, base_path: str = "memory/email-store"):
        self.base_path = Path(base_path)
        self.emails_file = self.base_path / "emails.jsonl"
        self.seen_file = self.base_path / "seen.json"
        self.index_file = self.base_path / "index.json"

        # Ensure directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Load seen IDs into memory
        self._seen_ids: set[str] = self._load_seen()

    def _load_seen(self) -> set[str]:
        """Load seen message IDs from disk."""
        if self.seen_file.exists():
            with open(self.seen_file, "r") as f:
                data = json.load(f)
                return set(data.get("seen", []))
        return set()

    def _save_seen(self) -> None:
        """Save seen message IDs to disk."""
        with open(self.seen_file, "w") as f:
            json.dump(
                {
                    "seen": list(self._seen_ids),
                    "updated_at": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    def is_seen(self, message_id: str) -> bool:
        """Check if a message has been seen."""
        return message_id in self._seen_ids

    def mark_seen(self, message_id: str) -> None:
        """Mark a message as seen."""
        self._seen_ids.add(message_id)
        self._save_seen()

    def mark_seen_batch(self, message_ids: list[str]) -> None:
        """Mark multiple messages as seen."""
        self._seen_ids.update(message_ids)
        self._save_seen()

    def save(self, email: ParsedEmail) -> None:
        """Save a parsed email to the store."""
        # Mark as seen
        self.mark_seen(email.id)

        # Append to JSONL file
        with open(self.emails_file, "a") as f:
            f.write(email.model_dump_json() + "\n")

    def save_batch(self, emails: list[ParsedEmail]) -> None:
        """Save multiple emails to the store."""
        if not emails:
            return

        # Mark all as seen
        self.mark_seen_batch([e.id for e in emails])

        # Append all to JSONL
        with open(self.emails_file, "a") as f:
            for email in emails:
                f.write(email.model_dump_json() + "\n")

    def load_all(self) -> list[ParsedEmail]:
        """Load all emails from the store."""
        if not self.emails_file.exists():
            return []

        emails = []
        with open(self.emails_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    emails.append(ParsedEmail.model_validate_json(line))

        return emails

    def load_recent(self, limit: int = 100) -> list[ParsedEmail]:
        """Load the most recent N emails."""
        all_emails = self.load_all()
        # Sort by date descending
        all_emails.sort(key=lambda e: e.date, reverse=True)
        return all_emails[:limit]

    def load_by_category(self, category: str) -> list[ParsedEmail]:
        """Load emails filtered by category."""
        all_emails = self.load_all()
        return [e for e in all_emails if e.category == category]

    def load_by_sender(self, sender_domain: str) -> list[ParsedEmail]:
        """Load emails filtered by sender domain."""
        all_emails = self.load_all()
        return [e for e in all_emails if sender_domain.lower() in e.sender_domain.lower()]

    def load_since(self, since: datetime) -> list[ParsedEmail]:
        """Load emails since a given datetime."""
        all_emails = self.load_all()
        return [e for e in all_emails if e.date >= since]

    def get_by_id(self, message_id: str) -> Optional[ParsedEmail]:
        """Get a specific email by ID."""
        all_emails = self.load_all()
        for email in all_emails:
            if email.id == message_id:
                return email
        return None

    def count(self) -> int:
        """Count total emails in store."""
        if not self.emails_file.exists():
            return 0

        count = 0
        with open(self.emails_file, "r") as f:
            for _ in f:
                count += 1
        return count

    def seen_count(self) -> int:
        """Count seen message IDs."""
        return len(self._seen_ids)

    def clear(self) -> None:
        """Clear all stored emails and seen IDs."""
        if self.emails_file.exists():
            os.remove(self.emails_file)
        self._seen_ids.clear()
        self._save_seen()

    def sync_seen_from_stored(self) -> int:
        """
        Sync seen IDs from stored emails.

        Useful for rebuilding seen.json from emails.jsonl.
        Returns count of IDs synced.
        """
        emails = self.load_all()
        ids = [e.id for e in emails]
        self._seen_ids.update(ids)
        self._save_seen()
        return len(ids)

    def export_for_bot(
        self,
        category: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        Export emails as plain dicts for bot consumption.

        Returns only essential fields for downstream processing.
        """
        emails = self.load_all()

        if category:
            emails = [e for e in emails if e.category == category]

        if since:
            emails = [e for e in emails if e.date >= since]

        # Sort by date descending
        emails.sort(key=lambda e: e.date, reverse=True)
        emails = emails[:limit]

        return [
            {
                "id": e.id,
                "date": e.date.isoformat(),
                "sender": e.sender_email,
                "sender_name": e.sender_name,
                "subject": e.subject_clean,
                "preview": e.body_preview,
                "category": e.category,
                "labels": e.labels,
            }
            for e in emails
        ]
