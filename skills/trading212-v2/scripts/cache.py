"""
Simple in-memory TTL cache for Trading212 API responses.

Prevents redundant API calls when running multiple modes in sequence
or when the same data is needed by multiple parts of the application.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple


class TTLCache:
    """Thread-unsafe, in-memory cache with per-key time-to-live."""

    def __init__(self, default_ttl: float = 60.0) -> None:
        """
        Parameters
        ----------
        default_ttl:
            Default time-to-live in seconds for cached entries.
        """
        self._default_ttl = default_ttl
        # key -> (value, expiry_timestamp)
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Return the cached value if it exists and has not expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.time() > expiry:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Store a value with a TTL (defaults to ``default_ttl``)."""
        ttl = ttl if ttl is not None else self._default_ttl
        self._store[key] = (value, time.time() + ttl)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from the cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._store.clear()

    def cached_call(
        self,
        key: str,
        fn: Callable[..., Any],
        *args: Any,
        ttl: Optional[float] = None,
        **kwargs: Any,
    ) -> Any:
        """Return a cached result or call *fn* and cache its return value.

        Parameters
        ----------
        key:
            Cache key.
        fn:
            Callable to invoke on cache miss.
        ttl:
            Optional override for the TTL of this entry.
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        result = fn(*args, **kwargs)
        self.set(key, result, ttl=ttl)
        return result
