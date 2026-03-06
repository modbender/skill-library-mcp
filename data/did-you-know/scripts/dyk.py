#!/usr/bin/env python3
"""Fetch Wikipedia "Did You Know?" facts and serve them one at a time."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import sys
import time
from typing import TypeVar
import urllib.parse
import urllib.request

_T = TypeVar("_T")

# MediaWiki API endpoint for the DYK template wikitext.
API_URL = (
    "https://en.wikipedia.org/w/api.php"
    "?action=query&format=json&prop=revisions&titles=Template:Did_you_know"
    "&rvprop=content&rvslots=main"
)

# Wikitext parsing helpers.
RE_HOOK_LINE = re.compile(r"^\*\s*\.{3}\s*that\s+(.*)$", re.IGNORECASE)
RE_LINK = re.compile(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]")
RE_BOLD_SECTION = re.compile(r"'''(.*?)'''", re.DOTALL)

# On-disk cache of daily hook collections.
DATA_PATH = Path.home() / ".openclaw" / "dyk-facts.json"
MAX_COLLECTIONS = 10
REFRESH_INTERVAL = 12 * 60 * 60  # DYK sets rotate every 12–24 h
MSG_PREFIX = "Did you know that "
MSG_SUFFIX = "?"
MSG_URL_SEPARATOR = "\n"
MSG_BODY_SEPARATOR = "\n\n"


def title_to_url(title: str) -> str:
    """Convert a Wikipedia article title into a human-readable URL."""
    encoded = (
        "https://en.wikipedia.org/wiki/"
        + urllib.parse.quote(title.replace(" ", "_"), safe="/:@")
    )
    return urllib.parse.unquote(encoded)


def retry_with_backoff(func: Callable[[], _T], retries: int = 3, backoff: float = 2.0) -> _T:
    """Retry a function with exponential backoff between attempts."""
    last_exc = None
    for attempt in range(retries):
        try:
            return func()
        except Exception as exc:
            last_exc = exc
            if attempt < retries - 1:
                delay = backoff * (2 ** attempt)
                print(
                    f"Attempt {attempt + 1} failed ({exc}), retrying in {delay}s...",
                    file=sys.stderr,
                )
                time.sleep(delay)
    raise RuntimeError(f"Failed after {retries} attempts: {last_exc}")


def now_utc() -> datetime:
    """Return the current UTC time."""
    return datetime.now(timezone.utc)


def to_iso_z(ts: datetime) -> str:
    """Serialize a datetime as ISO 8601 with a trailing Z."""
    return ts.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(ts: str) -> datetime | None:
    """Parse ISO timestamps, accepting a trailing Z."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def normalize_text(text: str) -> str:
    """Strip wiki markup and normalize whitespace for display."""
    possessive_token = "__DYK_POSSESSIVE__"
    text = text.replace("&nbsp;", " ")
    text = text.replace("{{'s}}", possessive_token)
    while "{{" in text:
        cleaned = re.sub(r"\{\{[^{}]*\}\}", "", text)
        if cleaned == text:
            break
        text = cleaned
    text = text.replace("'''", "").replace("''", "")
    text = text.replace(possessive_token, "'s")

    def replace_link(match: re.Match) -> str:
        title = match.group(1).strip()
        label = match.group(2).strip() if match.group(2) else title
        return label

    text = RE_LINK.sub(replace_link, text)
    text = re.sub(r"\s*\([^)]*pictured[^)]*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_hooks_section(wikitext: str) -> str | None:
    """Return the hooks section contents or None if markers are missing."""
    start = wikitext.find("<!--Hooks-->")
    end = wikitext.find("<!--HooksEnd-->")
    if start == -1 or end == -1 or end <= start:
        return None
    return wikitext[start + len("<!--Hooks-->") : end]


def extract_hook_titles(line: str) -> list[str]:
    """Prefer bold-linked titles; otherwise fall back to the first link."""
    titles = []
    for segment in RE_BOLD_SECTION.findall(line):
        for match in RE_LINK.finditer(segment):
            titles.append(match.group(1).strip())
    if titles:
        return titles
    match = RE_LINK.search(line)
    if not match:
        return []
    return [match.group(1).strip()]


def fetch_wikitext(retries: int = 3, backoff: float = 2.0) -> str:
    """Fetch the DYK template wikitext with simple retry/backoff."""
    def _fetch():
        req = urllib.request.Request(
            API_URL,
            headers={
                "User-Agent": "did-you-know/0.1 (https://en.wikipedia.org/wiki/User:Jonathan_Deamer)"
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        pages = payload.get("query", {}).get("pages", {})
        for page in pages.values():
            revisions = page.get("revisions", [])
            if revisions:
                return revisions[0]["slots"]["main"]["*"]
        raise RuntimeError("No wikitext found in API response")

    try:
        return retry_with_backoff(_fetch, retries=retries, backoff=backoff)
    except Exception as exc:
        raise RuntimeError("Failed to fetch Did You Know hooks") from exc


def collect_hooks(exclude_urls: set[str] | None = None) -> list[dict]:
    """Fetch, parse, and normalize hook candidates from the DYK template."""
    wikitext = fetch_wikitext()
    section = extract_hooks_section(wikitext)
    if not section:
        return []
    hooks: list[dict] = []
    seen_urls: set[str] = set(exclude_urls or set())
    for raw in section.splitlines():
        raw = raw.strip()
        match = RE_HOOK_LINE.match(raw)
        if not match:
            continue
        hook_line = match.group(1)
        titles = extract_hook_titles(hook_line)
        if not titles:
            continue
        normalized = normalize_text(hook_line)
        if not normalized:
            continue
        urls = [title_to_url(title) for title in titles]
        if any(url in seen_urls for url in urls):
            continue
        seen_urls.update(urls)
        hooks.append({"text": normalized, "urls": urls, "returned": False})
    return hooks


def stored_urls(store: dict) -> set[str]:
    """Collect all URLs from cached hooks across stored collections."""
    urls: set[str] = set()
    for coll in store.get("collections", []):
        for hook in coll.get("hooks", []):
            urls.update(urllib.parse.unquote(url) for url in hook.get("urls", []))
    return urls


def refresh_due(store: dict, now: datetime) -> bool:
    """Return True if the last fetch is older than REFRESH_INTERVAL."""
    collections = store.get("collections", [])
    if not collections:
        return True
    last = collections[-1]
    fetched_at = last.get("fetched_at")
    if not fetched_at:
        return True
    parsed = parse_iso(fetched_at)
    if parsed is None:
        return True
    return (now - parsed).total_seconds() >= REFRESH_INTERVAL


def load_store() -> dict:
    """Load the on-disk cache, returning an empty structure if missing/invalid."""
    if not DATA_PATH.exists():
        return {"collections": []}
    try:
        text = DATA_PATH.read_text(encoding="utf-8")
        data = json.loads(text)
        if not isinstance(data, dict) or "collections" not in data:
            return {"collections": []}
        return data
    except json.JSONDecodeError:
        return {"collections": []}


def save_store(store: dict) -> None:
    """Persist the cache to disk."""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def trim_store(store: dict) -> None:
    """Keep only the most recent MAX_COLLECTIONS collections."""
    collections = store.setdefault("collections", [])
    while len(collections) > MAX_COLLECTIONS:
        collections.pop(0)


def ensure_fresh(store: dict) -> None:
    """Ensure a fresh collection exists, refreshing from the network if needed."""
    now = now_utc()
    collections = store.setdefault("collections", [])
    if not refresh_due(store, now):
        return
    try:
        hooks = collect_hooks(exclude_urls=stored_urls(store))
    except Exception as exc:
        print(f"DYK refresh failed: {exc}", file=sys.stderr)
        if collections:
            return
        raise
    if not hooks:
        # All hooks were duplicates of ones we already have.  DYK sets
        # rotate once or twice per day, so the template may not have
        # changed yet.  By leaving fetched_at stale, refresh_due stays
        # True and we re-check on the next invocation.
        return
    collections.append(
        {
            "date": now.date().isoformat(),
            "fetched_at": to_iso_z(now),
            "hooks": hooks,
        }
    )
    trim_store(store)


def format_hook(hook: dict) -> str:
    """Format a hook with prefix, trailing '?', and one URL per line."""
    text = hook.get("text", "")
    urls = [urllib.parse.unquote(url) for url in hook.get("urls", [])]
    message = f"{MSG_PREFIX}{text}"
    if not message.endswith(MSG_SUFFIX):
        message += MSG_SUFFIX
    if not urls:
        return message
    return message + MSG_BODY_SEPARATOR + MSG_URL_SEPARATOR.join(urls)


def next_hook(store: dict) -> str:
    """Return the next unserved hook and mark it as returned."""
    collections = store.get("collections", [])
    for coll in reversed(collections):
        for hook in coll.get("hooks", []):
            if not hook.get("returned"):
                hook["returned"] = True
                return format_hook(hook)
    return "No more facts to share today; check back tomorrow!"


def main() -> int:
    """Script entrypoint: refresh cache if needed and print the next hook."""
    store = load_store()
    try:
        ensure_fresh(store)
        result = next_hook(store)
        save_store(store)
    except Exception as exc:
        print(f"DYK error: {exc}", file=sys.stderr)
        print("Something went wrong with the fact-fetching; please try again later.")
        return 1
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
