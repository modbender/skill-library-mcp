"""Tests for the TTL Cache module."""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from cache import TTLCache


class TestTTLCache:
    def test_set_and_get(self):
        cache = TTLCache(default_ttl=10.0)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_expiry(self):
        cache = TTLCache(default_ttl=0.1)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        time.sleep(0.15)
        assert cache.get("key1") is None

    def test_custom_ttl(self):
        cache = TTLCache(default_ttl=10.0)
        cache.set("short", "val", ttl=0.1)
        cache.set("long", "val", ttl=10.0)
        time.sleep(0.15)
        assert cache.get("short") is None
        assert cache.get("long") == "val"

    def test_invalidate(self):
        cache = TTLCache()
        cache.set("key1", "val1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = TTLCache()
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_prune(self):
        cache = TTLCache(default_ttl=0.1)
        cache.set("a", 1)
        cache.set("b", 2)
        time.sleep(0.15)
        removed = cache.prune()
        assert removed == 2
