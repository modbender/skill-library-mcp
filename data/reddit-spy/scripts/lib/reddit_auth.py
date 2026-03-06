"""Reddit OAuth2 'script' app authentication for maximum reliability.

When configured, this gives 60 requests/minute with zero IP blocking.
Requires: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD.
"""

import os
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
API_BASE = "https://oauth.reddit.com"

_token: Optional[str] = None
_token_expires: float = 0.0


def _get_credentials() -> Optional[Tuple[str, str, str, str]]:
    vals = [os.getenv(k) for k in (
        "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET",
        "REDDIT_USERNAME", "REDDIT_PASSWORD",
    )]
    return (vals[0], vals[1], vals[2], vals[3]) if all(vals) else None


def _build_ua(username: str) -> str:
    return f"OpenClawRadar/1.0 (by /u/{username})"


def _authenticate(creds: Tuple[str, str, str, str]) -> str:
    global _token, _token_expires
    client_id, client_secret, username, password = creds
    resp = requests.post(
        TOKEN_URL,
        auth=(client_id, client_secret),
        data={"grant_type": "password", "username": username, "password": password},
        headers={"User-Agent": _build_ua(username)},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"OAuth error: {data}")
    _token = data["access_token"]
    _token_expires = time.time() + data.get("expires_in", 3600) - 60
    return _token


def get_token() -> Optional[str]:
    global _token, _token_expires
    creds = _get_credentials()
    if creds is None:
        return None
    if _token and time.time() < _token_expires:
        return _token
    return _authenticate(creds)


def is_configured() -> bool:
    return _get_credentials() is not None


def _headers() -> Dict[str, str]:
    creds = _get_credentials()
    token = get_token()
    username = creds[2] if creds else "unknown"
    return {"Authorization": f"Bearer {token}", "User-Agent": _build_ua(username)}


def fetch_oauth(path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    resp = requests.get(f"{API_BASE}{path}", headers=_headers(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_posts(subreddit: str, sort: str = "hot", timeframe: str = "week", limit: int = 25) -> List[Dict]:
    params = {"limit": min(limit, 100), "t": timeframe, "raw_json": 1}
    data = fetch_oauth(f"/r/{subreddit}/{sort}", params)
    return [c.get("data", c) for c in data.get("data", {}).get("children", [])]


def fetch_about(subreddit: str) -> Dict[str, Any]:
    data = fetch_oauth(f"/r/{subreddit}/about")
    return data.get("data", data)


def fetch_comments(permalink: str, depth: int = 8, limit: int = 200) -> Dict[str, Any]:
    params = {"depth": depth, "limit": limit, "raw_json": 1}
    return fetch_oauth(permalink, params)


def search(subreddit: str, query: str, sort: str = "relevance", timeframe: str = "all", limit: int = 25) -> List[Dict]:
    params = {"q": query, "sort": sort, "t": timeframe, "limit": limit, "restrict_sr": "on", "raw_json": 1}
    data = fetch_oauth(f"/r/{subreddit}/search", params)
    return [c.get("data", c) for c in data.get("data", {}).get("children", [])]


def fetch_user(username: str, limit: int = 25) -> List[Dict]:
    params = {"limit": limit, "raw_json": 1}
    data = fetch_oauth(f"/user/{username}/submitted", params)
    return [c.get("data", c) for c in data.get("data", {}).get("children", [])]
