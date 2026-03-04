"""
discovery.py — ClawHub Ingestion Engine (v3 — Real API)

Uses the confirmed ClawHub REST API:
    GET https://clawhub.ai/api/v1/skills?sort=...&limit=100&cursor=...

No authentication required for reads. Cursor-based pagination.
Rate limit: undocumented — we use 0.75s delay between pages.

Configure via .env:
    CLAWHUB_BASE_URL=https://clawhub.ai   (override for testing)
"""

import os
import time
import httpx
from datetime import datetime, timezone


DEFAULT_BASE_URL = "https://clawhub.ai"
API_PATH = "/api/v1/skills"
REQUEST_TIMEOUT = 30.0
PAGE_DELAY = 0.75  # seconds between pages
PAGE_LIMIT = 100
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # seconds, doubles on each retry

HEADERS = {
    "User-Agent": "OpenclawSkillsWeekly/1.0",
    "Accept": "application/json",
}


def _normalise(item: dict) -> dict:
    """Flatten a ClawHub API skill item into our storage-compatible format."""
    stats = item.get("stats") or {}
    lv = item.get("latestVersion") or {}
    meta = item.get("metadata") or {}

    slug = item.get("slug", "")
    # Author is the first part of slug (e.g. "username/skill-name")
    author = slug.split("/")[0] if "/" in slug else ""

    return {
        "slug": slug,
        "display_name": item.get("displayName") or slug,
        "summary": item.get("summary") or "",
        "author": author,
        "downloads": stats.get("downloads", 0) or 0,
        "stars": stats.get("stars", 0) or 0,
        "installs_current": stats.get("installsCurrent", 0) or 0,
        "installs_all_time": stats.get("installsAllTime", 0) or 0,
        "versions": stats.get("versions", 0) or 0,
        "comments": stats.get("comments", 0) or 0,
        "created_at": item.get("createdAt", 0) or 0,
        "updated_at": item.get("updatedAt", 0) or 0,
        "latest_version": lv.get("version", ""),
        "os_support": ",".join(meta.get("os") or []),
        "systems": ",".join(meta.get("systems") or []),
        "clawhub_url": f"{DEFAULT_BASE_URL}/skills/{slug}" if slug else "",
    }


def _fetch_page(client: httpx.Client, url: str, params: dict) -> tuple[list[dict], str | None]:
    """Fetch one page with retry logic. Returns (items, nextCursor)."""
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.get(url, params=params)

            if resp.status_code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"  [RATE LIMIT] 429 — backing off {wait:.0f}s (attempt {attempt + 1}/{MAX_RETRIES})")
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            cursor = data.get("nextCursor")
            return items, cursor

        except httpx.TimeoutException:
            wait = RETRY_BACKOFF * (2 ** attempt)
            print(f"  [TIMEOUT] Retrying in {wait:.0f}s (attempt {attempt + 1}/{MAX_RETRIES})")
            time.sleep(wait)
        except httpx.HTTPStatusError as e:
            print(f"  [HTTP ERROR] {e.response.status_code}: {e}")
            return [], None
        except Exception as e:
            print(f"  [ERROR] {e}")
            return [], None

    print(f"  [FAILED] Max retries exceeded")
    return [], None


def discover(
    clawhub_url: str = "",
    sort: str = "downloads",
    mock: bool = False,
    max_pages: int = 0,
) -> list[dict]:
    """
    Fetch all skills from ClawHub via the public REST API.

    Args:
        clawhub_url: Base URL override (default: https://clawhub.ai)
        sort: Sort order — 'downloads', 'trending', 'installsCurrent', 'updated', 'stars'
        mock: If True, return synthetic data for offline dev
        max_pages: Limit pages fetched (0 = unlimited). Useful for testing.

    Returns:
        List of normalised skill dicts ready for storage.upsert_skills()
    """
    if mock:
        return _mock_skills()

    base = clawhub_url or os.getenv("CLAWHUB_BASE_URL", DEFAULT_BASE_URL)
    url = f"{base.rstrip('/')}{API_PATH}"

    print(f"[DISCOVERY] ClawHub API: {url}")
    print(f"[DISCOVERY] Sort: {sort}, page limit: {max_pages or 'unlimited'}")

    all_skills = []
    cursor = None
    page = 0

    with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        while True:
            params = {"sort": sort, "limit": PAGE_LIMIT}
            if cursor:
                params["cursor"] = cursor

            items, next_cursor = _fetch_page(client, url, params)

            if not items and page == 0:
                print("[DISCOVERY] No items returned on first page — API may be down")
                break

            for item in items:
                all_skills.append(_normalise(item))

            page += 1
            print(f"  Page {page}: {len(items)} skills (total: {len(all_skills)})")

            cursor = next_cursor
            if not cursor or not items:
                break
            if max_pages and page >= max_pages:
                print(f"  [DISCOVERY] Reached page limit ({max_pages})")
                break

            time.sleep(PAGE_DELAY)

    print(f"[DISCOVERY] Done: {len(all_skills)} skills fetched in {page} pages")
    return all_skills


def discover_incremental(
    clawhub_url: str = "",
    since_ts_ms: int = 0,
) -> list[dict]:
    """
    Fetch only skills updated since a given timestamp (milliseconds).
    Sorts by 'updated' and stops when we hit skills older than cutoff.
    """
    base = clawhub_url or os.getenv("CLAWHUB_BASE_URL", DEFAULT_BASE_URL)
    url = f"{base.rstrip('/')}{API_PATH}"

    print(f"[DISCOVERY] Incremental fetch since {since_ts_ms}")

    all_skills = []
    cursor = None
    page = 0

    with httpx.Client(headers=HEADERS, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        while True:
            params = {"sort": "updated", "limit": PAGE_LIMIT}
            if cursor:
                params["cursor"] = cursor

            items, next_cursor = _fetch_page(client, url, params)
            if not items:
                break

            hit_cutoff = False
            for item in items:
                if (item.get("updatedAt", 0) or 0) < since_ts_ms:
                    hit_cutoff = True
                    break
                all_skills.append(_normalise(item))

            page += 1
            cursor = next_cursor

            if hit_cutoff or not cursor:
                break

            time.sleep(PAGE_DELAY)

    print(f"[DISCOVERY] Incremental: {len(all_skills)} updated skills in {page} pages")
    return all_skills


# ---------------------------------------------------------------------------
# Mock mode (for offline development only)
# ---------------------------------------------------------------------------

def _mock_skills() -> list[dict]:
    """Synthetic stub data for development when ClawHub is unreachable."""
    print("  [MOCK] Using synthetic stub data for offline development")
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    stubs = [
        ("openclaw-team/browser-control", "Browser Control Skill", "Automate any browser interaction via natural language", 8420, 142, 210, 8420, 4.8),
        ("alexsjones/code-reviewer", "Code Reviewer", "AI-powered code review with inline suggestions", 6130, 98, 370, 6130, 4.6),
        ("openclaw-team/slack-notifier", "Slack Notifier", "Push structured notifications to Slack channels", 5890, 76, 180, 5890, 4.5),
        ("aidanpark/data-pipeline", "Data Pipeline Builder", "Construct ETL pipelines via agent conversation", 4200, 55, 120, 4200, 4.3),
        ("openpawz/web-scraper", "Web Scraper", "Extract structured data from any public webpage", 3980, 110, 290, 3980, 4.7),
        ("openclaw-team/image-analyser", "Image Analyser", "Vision-powered image description and tagging", 3100, 45, 95, 3100, 4.4),
        ("alexsjones/github-pr-agent", "GitHub PR Agent", "Automate PR reviews, labels, and merges", 2750, 88, 150, 2750, 4.2),
        ("contrib-user1/pdf-extractor", "PDF Extractor", "Parse and structure PDF documents into JSON", 2200, 32, 60, 2200, 4.1),
        ("contrib-user2/email-drafter", "Email Drafter", "Draft context-aware professional emails", 1800, 28, 40, 1800, 4.0),
        ("aidanpark/sql-query-agent", "SQL Query Agent", "Natural language to SQL with safety guardrails", 950, 65, 85, 950, 4.6),
    ]
    return [
        {
            "slug": slug,
            "display_name": name,
            "summary": desc,
            "author": slug.split("/")[0],
            "downloads": downloads,
            "stars": stars,
            "installs_current": inst_cur,
            "installs_all_time": inst_all,
            "versions": 3,
            "comments": 5,
            "created_at": now_ms - 86400000 * 30,
            "updated_at": now_ms,
            "latest_version": "1.0.0",
            "os_support": "darwin,linux,win32",
            "systems": "claude",
            "clawhub_url": f"https://clawhub.ai/skills/{slug}",
        }
        for slug, name, desc, downloads, stars, inst_cur, inst_all, _ in stubs
    ]
