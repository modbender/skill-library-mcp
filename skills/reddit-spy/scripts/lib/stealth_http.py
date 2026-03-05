"""Stealth HTTP client targeting old.reddit.com JSON endpoints.

Uses persistent sessions, rotating user agents, realistic headers,
and optional proxy support to avoid Reddit's bot detection.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .ua_pool import get_session_ua
from .rate_limiter import wait, mark

BASE_URL = "https://old.reddit.com"
CACHE_DIR = Path.home() / ".openclaw" / ".reddit-spy-cache"
COOKIE_FILE = CACHE_DIR / "cookies.json"
REQUEST_TIMEOUT = 20

_session: Optional[requests.Session] = None


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _build_headers() -> Dict[str, str]:
    return {
        "User-Agent": get_session_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def _load_cookies(session: requests.Session) -> None:
    if not COOKIE_FILE.exists():
        return
    try:
        for name, value in json.loads(COOKIE_FILE.read_text()).items():
            session.cookies.set(name, value)
    except Exception:
        pass


def _save_cookies(session: requests.Session) -> None:
    _ensure_cache_dir()
    cookies = {c.name: c.value for c in session.cookies}
    COOKIE_FILE.write_text(json.dumps(cookies))


def _apply_proxy(session: requests.Session) -> None:
    proxy = os.getenv("REDDIT_PROXY_URL")
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}


def get_session() -> requests.Session:
    global _session
    if _session is not None:
        return _session
    _session = requests.Session()
    _session.headers.update(_build_headers())
    _apply_proxy(_session)
    _load_cookies(_session)
    return _session


def fetch_json(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    session = get_session()
    url = f"{BASE_URL}{path}"
    wait("old.reddit.com")
    resp = session.get(url, params=params, timeout=REQUEST_TIMEOUT)
    mark("old.reddit.com")
    _save_cookies(session)
    if resp.status_code == 403:
        raise PermissionError(f"403 blocked: {url}")
    if resp.status_code == 429:
        raise ConnectionError(f"429 rate limited: {url}")
    resp.raise_for_status()
    return resp.json()


def _extract_children(data: Dict) -> List[Dict]:
    return [c.get("data", c) for c in data.get("data", {}).get("children", [])]


def fetch_about(subreddit: str) -> Dict[str, Any]:
    data = fetch_json(f"/r/{subreddit}/about.json")
    return data.get("data", data)


def fetch_posts(subreddit: str, sort: str = "hot", timeframe: str = "week", limit: int = 25) -> List[Dict]:
    params = {"limit": min(limit, 100), "t": timeframe, "raw_json": 1}
    return _extract_children(fetch_json(f"/r/{subreddit}/{sort}.json", params))


def fetch_comments_raw(post_url: str, depth: int = 8, limit: int = 200) -> Any:
    path = _extract_path(post_url)
    if not path.endswith(".json"):
        path = path.rstrip("/") + "/.json"
    return fetch_json(path, {"depth": depth, "limit": limit, "raw_json": 1})


def _extract_path(url: str) -> str:
    url = url.strip()
    if url.startswith("/"):
        return url
    for domain in ("old.reddit.com", "www.reddit.com", "reddit.com"):
        if domain in url:
            return url.split(domain)[1]
    return url


def search_posts(subreddit: str, query: str, sort: str = "relevance", timeframe: str = "all", limit: int = 25) -> List[Dict]:
    params = {"q": query, "sort": sort, "t": timeframe, "limit": limit, "restrict_sr": "on", "raw_json": 1}
    return _extract_children(fetch_json(f"/r/{subreddit}/search.json", params))


def fetch_user_posts(username: str, limit: int = 25) -> List[Dict]:
    params = {"limit": limit, "raw_json": 1}
    return _extract_children(fetch_json(f"/user/{username}/submitted.json", params))
