"""PullPush API client for historical Reddit data access.

PullPush archives Reddit data and is accessible from any IP.
Data may lag behind real-time by weeks/months but provides
rich historical analysis for strategy extraction.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://api.pullpush.io/reddit"
REQUEST_TIMEOUT = 20
MIN_DELAY = 1.5
_last_request: float = 0.0


def _wait() -> None:
    global _last_request
    elapsed = time.monotonic() - _last_request
    if elapsed < MIN_DELAY:
        time.sleep(MIN_DELAY - elapsed)


def _mark() -> None:
    global _last_request
    _last_request = time.monotonic()


def _get(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    _wait()
    resp = requests.get(
        f"{BASE_URL}{endpoint}",
        params=params,
        headers={"User-Agent": "OpenClawRadar/1.0"},
        timeout=REQUEST_TIMEOUT,
    )
    _mark()
    resp.raise_for_status()
    return resp.json()


def _format_ts(ts: Any) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except (ValueError, TypeError, OSError):
        return str(ts)


def _normalize_post(raw: Dict) -> Dict[str, Any]:
    return {
        "title": raw.get("title", ""),
        "author": raw.get("author", "[deleted]"),
        "subreddit": raw.get("subreddit", ""),
        "score": raw.get("score", 0),
        "num_comments": raw.get("num_comments", 0),
        "created_utc": _format_ts(raw.get("created_utc", 0)),
        "url": raw.get("url", ""),
        "permalink": f"https://reddit.com{raw.get('permalink', '')}",
        "selftext": raw.get("selftext", ""),
        "link_flair_text": raw.get("link_flair_text"),
        "is_self": raw.get("is_self", True),
        "domain": raw.get("domain", ""),
        "upvote_ratio": raw.get("upvote_ratio", 0),
        "data_source": "pullpush",
    }


def _map_sort(sort: str) -> str:
    return "created_utc" if sort in ("new", "rising") else "score"


def _timeframe_to_epoch(timeframe: str) -> Optional[int]:
    import time as _time
    mapping = {"hour": 3600, "day": 86400, "week": 604800, "month": 2592000, "year": 31536000}
    seconds = mapping.get(timeframe)
    if seconds is None:
        return None
    return int(_time.time()) - seconds


def fetch_posts(
    subreddit: str, sort: str = "hot",
    timeframe: str = "week", limit: int = 25,
) -> List[Dict]:
    params: Dict[str, Any] = {
        "subreddit": subreddit,
        "size": min(limit, 100),
        "sort": "desc",
        "sort_type": _map_sort(sort),
    }
    after = _timeframe_to_epoch(timeframe)
    if after:
        params["after"] = after
    data = _get("/search/submission/", params)
    return [_normalize_post(p) for p in data.get("data", [])]


def search_posts(
    subreddit: str, query: str,
    sort: str = "relevance", timeframe: str = "all",
    limit: int = 25,
) -> List[Dict]:
    params: Dict[str, Any] = {
        "subreddit": subreddit,
        "q": query,
        "size": min(limit, 100),
        "sort": "desc",
        "sort_type": _map_sort(sort),
    }
    after = _timeframe_to_epoch(timeframe)
    if after:
        params["after"] = after
    data = _get("/search/submission/", params)
    return [_normalize_post(p) for p in data.get("data", [])]


def fetch_comments(
    subreddit: str, limit: int = 25,
    sort_type: str = "score",
) -> List[Dict]:
    params = {
        "subreddit": subreddit,
        "size": min(limit, 100),
        "sort": "desc",
        "sort_type": sort_type,
    }
    data = _get("/search/comment/", params)
    return [_normalize_comment(c) for c in data.get("data", [])]


def _normalize_comment(raw: Dict) -> Dict[str, Any]:
    return {
        "author": raw.get("author", "[deleted]"),
        "body": raw.get("body", ""),
        "score": raw.get("score", 0),
        "subreddit": raw.get("subreddit", ""),
        "created_utc": _format_ts(raw.get("created_utc", 0)),
        "permalink": raw.get("permalink", ""),
        "data_source": "pullpush",
    }


def fetch_user_posts(username: str, limit: int = 25) -> List[Dict]:
    params = {"author": username, "size": min(limit, 100), "sort": "desc", "sort_type": "score"}
    data = _get("/search/submission/", params)
    return [_normalize_post(p) for p in data.get("data", [])]


def is_available() -> bool:
    try:
        resp = requests.get(
            f"{BASE_URL}/search/submission/",
            params={"subreddit": "python", "size": 1},
            timeout=5,
        )
        return resp.status_code == 200
    except Exception:
        return False
