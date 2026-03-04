"""Persistent send-retry queue backed by a JSON file.

When an SMTP send fails, the message can be enqueued for later retry.
On the next heartbeat (or manual invocation) the queue is drained.

Queue file layout (JSON)::

    {
      "version": 1,
      "messages": [
        {
          "id": "uuid",
          "account": "work",
          "message": { ... serialised EmailMessage dict ... },
          "enqueued_at": "2026-02-24T12:00:00",
          "attempts": 1,
          "last_error": "Connection refused",
          "next_retry_after": "2026-02-24T12:05:00"
        }
      ]
    }
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from typing import Any

from .models import EmailMessage

logger = logging.getLogger("clawMail.send_queue")

_MAX_ATTEMPTS = 5
_BACKOFF_MINUTES = [1, 5, 15, 60, 240]  # exponential-ish


class SendQueue:
    """File-backed queue for messages that failed to send."""

    def __init__(self, path: str, max_attempts: int = _MAX_ATTEMPTS) -> None:
        self.path = path
        self.max_attempts = max_attempts
        self._entries: list[dict[str, Any]] = []
        self._load()

    # ── Public API ────────────────────────────────────────────────

    def enqueue(
        self,
        message: EmailMessage,
        account: str = "",
        error: str = "",
    ) -> str:
        """Add a failed message to the retry queue.  Returns the queue ID."""
        entry_id = str(uuid.uuid4())[:8]
        self._entries.append({
            "id": entry_id,
            "account": account,
            "message": message.to_dict(),
            "enqueued_at": datetime.now().isoformat(),
            "attempts": 0,
            "last_error": error,
            "next_retry_after": datetime.now().isoformat(),
        })
        self._save()
        logger.info("Enqueued message %s for retry (account=%s)", entry_id, account)
        return entry_id

    def peek(self) -> list[dict[str, Any]]:
        """Return all entries that are ready for retry now."""
        now = datetime.now()
        ready = []
        for e in self._entries:
            if e["attempts"] >= self.max_attempts:
                continue
            nra = e.get("next_retry_after", "")
            if nra:
                try:
                    if datetime.fromisoformat(nra) > now:
                        continue
                except (ValueError, TypeError):
                    pass
            ready.append(e)
        return ready

    def mark_sent(self, entry_id: str) -> None:
        """Remove a successfully sent entry from the queue."""
        self._entries = [e for e in self._entries if e["id"] != entry_id]
        self._save()

    def mark_failed(self, entry_id: str, error: str = "") -> None:
        """Record a failed retry attempt and schedule the next one."""
        for e in self._entries:
            if e["id"] == entry_id:
                e["attempts"] += 1
                e["last_error"] = error
                idx = min(e["attempts"] - 1, len(_BACKOFF_MINUTES) - 1)
                delay = timedelta(minutes=_BACKOFF_MINUTES[idx])
                e["next_retry_after"] = (datetime.now() + delay).isoformat()
                break
        self._save()

    def remove_expired(self) -> int:
        """Remove entries that have exceeded max_attempts.  Returns count removed."""
        before = len(self._entries)
        self._entries = [
            e for e in self._entries if e["attempts"] < self.max_attempts
        ]
        removed = before - len(self._entries)
        if removed:
            self._save()
        return removed

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._entries)

    @property
    def size(self) -> int:
        return len(self._entries)

    # ── Persistence ───────────────────────────────────────────────

    def _load(self) -> None:
        if not os.path.exists(self.path):
            self._entries = []
            return
        try:
            with open(self.path) as f:
                data = json.load(f)
            self._entries = data.get("messages", [])
        except Exception as exc:
            logger.warning("Failed to load send queue %s: %s", self.path, exc)
            self._entries = []

    def _save(self) -> None:
        data = {"version": 1, "messages": self._entries}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)
