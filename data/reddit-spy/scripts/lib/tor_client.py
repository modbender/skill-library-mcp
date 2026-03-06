"""Tor-based Reddit client with circuit rotation on rate limits.

Routes through Tor SOCKS5 proxy for non-blacklisted IPs.
Automatically rotates circuits (new exit node) on 429 responses.
"""

import os
import time
from typing import Any, Dict, List, Optional

import requests

from .ua_pool import get_session_ua, reset_session_ua
from .rate_limiter import wait, mark

BASE_URLS = ["https://old.reddit.com", "https://www.reddit.com"]
TOR_PROXY = "socks5h://127.0.0.1:9050"
TOR_CONTROL_PORT = 9051
TOR_CONTROL_PASS = os.getenv("TOR_CONTROL_PASS", "openclaw_tor")
REQUEST_TIMEOUT = 25
CIRCUIT_COOLDOWN = 6
MAX_RETRIES = 2

_session: Optional[requests.Session] = None


def _is_tor_running() -> bool:
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", 9050), timeout=2)
        s.close()
        return True
    except (OSError, ConnectionRefusedError):
        return False


def is_available() -> bool:
    return _is_tor_running()


def _rotate_circuit() -> None:
    try:
        from stem import Signal
        from stem.control import Controller
        with Controller.from_port(port=TOR_CONTROL_PORT) as c:
            c.authenticate(password=TOR_CONTROL_PASS)
            c.signal(Signal.NEWNYM)
        time.sleep(CIRCUIT_COOLDOWN)
    except Exception:
        time.sleep(CIRCUIT_COOLDOWN)


def _build_session() -> requests.Session:
    s = requests.Session()
    s.proxies = {"http": TOR_PROXY, "https": TOR_PROXY}
    s.headers.update({
        "User-Agent": get_session_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    })
    return s


def _get_session() -> requests.Session:
    global _session
    if _session is None:
        _session = _build_session()
    return _session


def _reset_session() -> None:
    global _session
    reset_session_ua()
    _session = _build_session()


def fetch_json(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    for attempt in range(MAX_RETRIES + 1):
        session = _get_session()
        base = BASE_URLS[attempt % len(BASE_URLS)]
        wait("tor.reddit.com")
        try:
            resp = session.get(f"{base}{path}", params=params, timeout=REQUEST_TIMEOUT)
        except requests.exceptions.ConnectionError:
            if attempt < MAX_RETRIES:
                _rotate_circuit()
                _reset_session()
                continue
            raise
        mark("tor.reddit.com")
        if resp.status_code in (429, 403) and attempt < MAX_RETRIES:
            _rotate_circuit()
            _reset_session()
            continue
        if resp.status_code == 404 and attempt < MAX_RETRIES:
            continue
        resp.raise_for_status()
        return resp.json()
    return {}


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
