"""
SenseGuard Cache Manager
SHA-256 based caching to avoid redundant scans.
Cache stored at ~/.openclaw/senseguard/cache.json
"""

import os
import json
import hashlib
import time
from typing import Optional, Dict


# Default cache expiry: 7 days
CACHE_EXPIRY_SECONDS = 7 * 24 * 60 * 60

# Default cache location
DEFAULT_CACHE_DIR = os.path.expanduser("~/.openclaw/senseguard")
DEFAULT_CACHE_FILE = os.path.join(DEFAULT_CACHE_DIR, "cache.json")


class CacheManager:
    """Manages scan result caching based on directory content hashes."""

    def __init__(self, cache_file: Optional[str] = None, expiry_seconds: int = CACHE_EXPIRY_SECONDS):
        self.cache_file = cache_file or DEFAULT_CACHE_FILE
        self.expiry_seconds = expiry_seconds
        self._cache: Dict[str, dict] = {}
        self._load()

    def _load(self):
        """Load cache from disk."""
        if os.path.isfile(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._cache = {}
        else:
            self._cache = {}

    def _save(self):
        """Persist cache to disk."""
        cache_dir = os.path.dirname(self.cache_file)
        os.makedirs(cache_dir, exist_ok=True)
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)

    def compute_hash(self, skill_dir: str) -> str:
        """Compute SHA-256 hash of all files in a skill directory."""
        hasher = hashlib.sha256()
        file_entries = []

        for root, dirs, filenames in os.walk(skill_dir):
            # Skip hidden dirs, cache, __pycache__
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "cache"))
            for fname in sorted(filenames):
                fpath = os.path.join(root, fname)
                rel_path = os.path.relpath(fpath, skill_dir)
                try:
                    with open(fpath, "rb") as f:
                        content = f.read()
                    file_entries.append((rel_path, content))
                except (OSError, IOError):
                    continue

        # Hash file paths + contents deterministically
        for rel_path, content in sorted(file_entries, key=lambda x: x[0]):
            hasher.update(rel_path.encode("utf-8"))
            hasher.update(content)

        return hasher.hexdigest()

    def get_cached(self, skill_dir: str) -> Optional[dict]:
        """Get cached scan result if hash matches and not expired."""
        current_hash = self.compute_hash(skill_dir)
        cache_key = os.path.abspath(skill_dir)

        entry = self._cache.get(cache_key)
        if entry is None:
            return None

        # Check hash match
        if entry.get("hash") != current_hash:
            return None

        # Check expiry
        cached_time = entry.get("timestamp", 0)
        if time.time() - cached_time > self.expiry_seconds:
            return None

        return entry.get("result")

    def store(self, skill_dir: str, result: dict, content_hash: Optional[str] = None):
        """Store scan result in cache."""
        if content_hash is None:
            content_hash = self.compute_hash(skill_dir)

        cache_key = os.path.abspath(skill_dir)
        self._cache[cache_key] = {
            "hash": content_hash,
            "timestamp": time.time(),
            "result": result,
        }
        self._save()

    def get_previous_result(self, skill_dir: str) -> Optional[dict]:
        """Get previous result regardless of hash/expiry (for diff comparison)."""
        cache_key = os.path.abspath(skill_dir)
        entry = self._cache.get(cache_key)
        if entry:
            return entry.get("result")
        return None

    def get_all_previous_results(self) -> Dict[str, dict]:
        """Get all cached results keyed by skill name (for batch diff)."""
        results = {}
        for cache_key, entry in self._cache.items():
            result = entry.get("result", {})
            skill_name = result.get("skill_name", os.path.basename(cache_key))
            results[skill_name] = result
        return results

    def invalidate(self, skill_dir: str):
        """Remove a specific entry from cache."""
        cache_key = os.path.abspath(skill_dir)
        if cache_key in self._cache:
            del self._cache[cache_key]
            self._save()

    def clear_all(self):
        """Clear entire cache."""
        self._cache = {}
        self._save()
