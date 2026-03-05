"""
In-memory TTL cache for exchange data.

Reduces redundant API calls by caching responses for a configurable
time-to-live period. Thread-safe for use with async strategies.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional


class TTLCache:
    """Simple thread-safe in-memory cache with per-key TTL."""

    def __init__(self, default_ttl: float = 60.0) -> None:
        self._default_ttl = default_ttl
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if it exists and has not expired."""
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            if time.time() > entry["expires_at"]:
                del self._store[key]
                return None
            return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Store a value with an optional custom TTL."""
        with self._lock:
            self._store[key] = {
                "value": value,
                "expires_at": time.time() + (ttl if ttl is not None else self._default_ttl),
            }

    def invalidate(self, key: str) -> None:
        """Remove a specific key from the cache."""
        with self._lock:
            self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        with self._lock:
            self._store.clear()

    def prune(self) -> int:
        """Remove all expired entries. Returns the number of entries removed."""
        now = time.time()
        removed = 0
        with self._lock:
            expired_keys = [
                k for k, v in self._store.items() if now > v["expires_at"]
            ]
            for k in expired_keys:
                del self._store[k]
                removed += 1
        return removed
