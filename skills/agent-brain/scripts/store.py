"""Storage abstraction for Agent Brain.

All memory operations go through a MemoryStore implementation.
Currently: SQLiteStore (default), JsonStore (legacy).
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class MemoryStore(ABC):
    """Abstract interface for memory storage backends."""

    @abstractmethod
    def init(self):
        """Create or migrate the storage schema."""

    @abstractmethod
    def close(self):
        """Clean up connections/resources."""

    @abstractmethod
    def read_all(self) -> dict:
        """Return full memory state as a dict (entries + meta)."""

    @abstractmethod
    def get_active_entries(self, memory_classes: list[str] | None = None) -> list:
        """Return non-superseded entries, optionally filtered by memory class."""

    @abstractmethod
    def get_entry(self, entry_id: str) -> dict | None:
        """Return a single entry by ID, or None."""

    @abstractmethod
    def add_entry(self, entry: dict) -> str:
        """Insert an entry dict. Returns the entry ID."""

    @abstractmethod
    def update_entry(self, entry_id: str, field: str, value):
        """Update a single field on an entry. Raises if not found."""

    @abstractmethod
    def touch_entry(self, entry_id: str, timestamp: str):
        """Update last_accessed and increment access_count."""

    @abstractmethod
    def bulk_touch(self, entry_ids: set, timestamp: str):
        """Update last_accessed and access_count for multiple entries."""

    @abstractmethod
    def mark_superseded(self, old_id: str, new_id: str):
        """Set superseded_by on old entry."""

    @abstractmethod
    def increment_success(self, entry_id: str, timestamp: str) -> dict:
        """Increment success_count, touch entry. Returns updated entry."""

    @abstractmethod
    def get_meta(self, key: str) -> str | None:
        """Read a meta value by key."""

    @abstractmethod
    def set_meta(self, key: str, value: str):
        """Write a meta value."""

    @abstractmethod
    def get_session(self) -> dict | None:
        """Return current session dict or None."""

    @abstractmethod
    def start_session(self, session_id: int, context: str | None, timestamp: str):
        """Set current session."""

    @abstractmethod
    def get_session_counter(self) -> int:
        """Return current session counter."""

    @abstractmethod
    def set_session_counter(self, value: int):
        """Set session counter."""

    @abstractmethod
    def run_decay(self, now_str: str, decay_fn) -> int:
        """Run decay on all active entries using decay_fn(entry, now_str).
        decay_fn returns the new confidence or None if no change.
        Returns count of decayed entries."""

    @abstractmethod
    def export_json(self) -> str:
        """Return full memory as JSON string."""

    @abstractmethod
    def log_activity(self, timestamp: str, action: str, entry_id: str | None, detail: str):
        """Append an activity log entry."""

    @abstractmethod
    def get_log(self, limit: int = 50, action: str | None = None) -> list:
        """Return recent log entries as list of dicts, newest first."""
