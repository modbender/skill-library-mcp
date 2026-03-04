"""Comprehensive subreddit intelligence scanning.

Combines about info, top posts, and strategy extraction into
full intelligence reports for single or multiple subreddits.
"""

import sys
from typing import Any, Dict, List

from . import cascade_fetcher
from .deep_reader import read_top_posts
from .strategy_extractor import extract_strategy


def _log(msg: str) -> None:
    print(f"[scanner] {msg}", file=sys.stderr)


def _safe_fetch_about(subreddit: str) -> Dict[str, Any]:
    try:
        return cascade_fetcher.fetch_about(subreddit)
    except Exception as e:
        _log(f"fetch_about({subreddit}) failed: {e}")
        return {"error": str(e)}


def _format_about(raw: Dict) -> Dict[str, Any]:
    if "error" in raw:
        return raw
    return {
        "name": raw.get("display_name", raw.get("subreddit", "")),
        "title": raw.get("title", ""),
        "subscribers": raw.get("subscribers", 0),
        "active_users": raw.get("accounts_active", raw.get("active_user_count", 0)),
        "description": raw.get("public_description", "")[:200],
        "created_utc": raw.get("created_utc", ""),
    }


def scan_subreddit(
    subreddit: str, sort: str = "top",
    timeframe: str = "week", limit: int = 25,
) -> Dict[str, Any]:
    _log(f"Scanning r/{subreddit} ({sort}/{timeframe}, limit={limit})")
    about = _format_about(_safe_fetch_about(subreddit))
    _log(f"r/{subreddit}: about fetched")
    posts = read_top_posts(subreddit, sort, timeframe, limit)
    _log(f"r/{subreddit}: {len(posts)} posts fetched")
    strategy = extract_strategy(posts)
    return {
        "subreddit": subreddit,
        "about": about,
        "posts_fetched": len(posts),
        "strategy": strategy,
        "data_source": "cascade",
    }


def bulk_scan(
    subreddits: List[str], sort: str = "top",
    timeframe: str = "week", limit: int = 25,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for sub in subreddits:
        try:
            results[sub] = scan_subreddit(sub, sort, timeframe, limit)
        except Exception as e:
            _log(f"r/{sub} scan failed: {e}")
            results[sub] = {"subreddit": sub, "error": str(e)}
    return {"subreddits": results, "comparison": _compare_results(results)}


def _compare_results(results: Dict[str, Dict]) -> Dict[str, Any]:
    valid = {k: v for k, v in results.items() if "error" not in v}
    if len(valid) < 2:
        return {"note": "Need 2+ successful scans for comparison"}
    return {
        "by_subscribers": _rank_by_field(valid, ["about", "subscribers"]),
        "by_engagement": _rank_by_engagement(valid),
    }


def _rank_by_field(results: Dict[str, Dict], path: List[str]) -> List[Dict]:
    items: List[Dict] = []
    for name, data in results.items():
        val = data
        for key in path:
            val = val.get(key, {}) if isinstance(val, dict) else {}
        items.append({"subreddit": name, "value": val if not isinstance(val, dict) else 0})
    return sorted(items, key=lambda x: x["value"], reverse=True)


def _rank_by_engagement(results: Dict[str, Dict]) -> List[Dict]:
    items: List[Dict] = []
    for name, data in results.items():
        types = data.get("strategy", {}).get("content_types", {})
        avg_scores = [v.get("avg_score", 0) for v in types.values()]
        avg = round(sum(avg_scores) / len(avg_scores), 1) if avg_scores else 0
        items.append({"subreddit": name, "avg_score_across_types": avg})
    return sorted(items, key=lambda x: x["avg_score_across_types"], reverse=True)
