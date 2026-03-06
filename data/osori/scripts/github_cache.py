#!/usr/bin/env python3
"""GitHub open-count cache helpers for Osori.

Cache schema:
{
  "version": 1,
  "updatedAt": <unix-seconds>,
  "entries": {
    "open_count:pr:owner/repo": {"value": 3, "fetchedAt": 1700000000},
    ...
  }
}
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

CACHE_VERSION = 1
DEFAULT_CACHE_PATH = os.path.expanduser("~/.openclaw/osori-cache.json")


def _now() -> int:
    return int(time.time())


def _default_cache() -> Dict[str, Any]:
    return {
        "version": CACHE_VERSION,
        "updatedAt": _now(),
        "entries": {},
    }


def _normalize_cache(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return _default_cache()

    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        entries = {}

    normalized_entries: Dict[str, Dict[str, int]] = {}
    for k, v in entries.items():
        if not isinstance(v, dict):
            continue
        try:
            value = int(v.get("value"))
            fetched_at = int(v.get("fetchedAt"))
        except Exception:
            continue
        normalized_entries[str(k)] = {"value": value, "fetchedAt": fetched_at}

    return {
        "version": CACHE_VERSION,
        "updatedAt": int(payload.get("updatedAt", _now())) if isinstance(payload.get("updatedAt"), int) else _now(),
        "entries": normalized_entries,
    }


def load_cache(cache_path: str | None = None) -> Dict[str, Any]:
    path = Path(cache_path or DEFAULT_CACHE_PATH).expanduser()
    if not path.exists():
        return _default_cache()

    try:
        with path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return _normalize_cache(payload)
    except Exception:
        return _default_cache()


def save_cache(cache: Dict[str, Any], cache_path: str | None = None) -> bool:
    path = Path(cache_path or DEFAULT_CACHE_PATH).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    cache_doc = _normalize_cache(cache)
    cache_doc["updatedAt"] = _now()

    tmp_path = None
    try:
        fd, tmp_path = tempfile.mkstemp(prefix=".osori-cache-", suffix=".tmp", dir=str(path.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(cache_doc, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
        tmp_path = None
        return True
    except Exception:
        return False
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


def _cache_key(kind: str, repo: str) -> str:
    return f"open_count:{kind}:{repo}"


def get_open_count(
    kind: str,
    repo: str,
    ttl_seconds: int = 600,
    cache_path: str | None = None,
    fetch_open_count: Callable[[], int | None] | None = None,
) -> Tuple[str, str]:
    """Return (value, cache_state).

    cache_state: hit|miss|stale-fallback|fetch-failed|skip
    """
    if not repo:
        return "n/a", "skip"

    ttl = int(ttl_seconds)
    cache = load_cache(cache_path)
    key = _cache_key(kind, repo)
    entry = cache.get("entries", {}).get(key)

    now = _now()
    if isinstance(entry, dict):
        try:
            age = now - int(entry.get("fetchedAt", 0))
            # ttl<=0 means always refresh (never hit cache)
            if ttl > 0 and age <= ttl:
                return str(int(entry["value"])), "hit"
        except Exception:
            pass

    if fetch_open_count is None:
        if isinstance(entry, dict) and "value" in entry:
            try:
                return str(int(entry["value"])), "stale-fallback"
            except Exception:
                pass
        return "n/a", "fetch-failed"

    value = fetch_open_count()
    if value is None:
        if isinstance(entry, dict) and "value" in entry:
            try:
                return str(int(entry["value"])), "stale-fallback"
            except Exception:
                pass
        return "n/a", "fetch-failed"

    try:
        value_int = int(value)
    except Exception:
        return "n/a", "fetch-failed"

    cache_entries = cache.setdefault("entries", {})
    if not isinstance(cache_entries, dict):
        cache_entries = {}
        cache["entries"] = cache_entries

    cache_entries[key] = {"value": value_int, "fetchedAt": now}
    save_cache(cache, cache_path)
    return str(value_int), "miss"


# ── High-level helper ────────────────────────────────

def gh_count(
    kind: str,
    repo: str,
    ttl_seconds: int = 600,
    cache_path: str | None = None,
) -> str:
    """Return open PR or issue count as a string (or 'n/a').

    Uses gh CLI to fetch and the TTL cache to avoid API spam.
    """
    import json
    import shutil
    import subprocess

    if not repo or shutil.which("gh") is None:
        return "n/a"

    def _run(cmd, timeout=12):
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return p.returncode, p.stdout.strip()
        except Exception:
            return 1, ""

    def fetch():
        rc, out = _run(["gh", kind, "list", "-R", repo, "--state", "open", "--json", "number", "--limit", "200"])
        if rc != 0 or not out:
            return None
        try:
            return len(json.loads(out))
        except Exception:
            return None

    value, _state = get_open_count(
        kind=kind,
        repo=repo,
        ttl_seconds=ttl_seconds,
        cache_path=cache_path or DEFAULT_CACHE_PATH,
        fetch_open_count=fetch,
    )
    return value
