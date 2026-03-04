"""Deep post and comment reader with nested tree flattening."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from . import cascade_fetcher


def _normalize_post(raw: Dict) -> Dict[str, Any]:
    return {
        "title": raw.get("title", ""),
        "author": raw.get("author", "[deleted]"),
        "subreddit": raw.get("subreddit", ""),
        "score": raw.get("score", 0),
        "upvote_ratio": raw.get("upvote_ratio", 0),
        "num_comments": raw.get("num_comments", 0),
        "created_utc": _format_ts(raw.get("created_utc", 0)),
        "url": raw.get("url", ""),
        "permalink": f"https://reddit.com{raw.get('permalink', '')}",
        "selftext": raw.get("selftext", ""),
        "link_flair_text": raw.get("link_flair_text"),
        "is_self": raw.get("is_self", True),
        "domain": raw.get("domain", ""),
        "over_18": raw.get("over_18", False),
    }


def _format_ts(ts: Any) -> str:
    if not ts:
        return ""
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except (ValueError, TypeError, OSError):
        return str(ts)


def _flatten_comments(node: Any, depth: int = 0, max_depth: int = 10) -> List[Dict]:
    if depth > max_depth or not isinstance(node, dict):
        return []
    kind = node.get("kind", "")
    data = node.get("data", node)
    if kind == "Listing":
        results: List[Dict] = []
        for child in data.get("children", []):
            results.extend(_flatten_comments(child, depth, max_depth))
        return results
    if kind == "more":
        return []
    comment = _extract_comment(data, depth)
    results = [comment] if comment else []
    replies = data.get("replies")
    if isinstance(replies, dict):
        results.extend(_flatten_comments(replies, depth + 1, max_depth))
    return results


def _extract_comment(data: Dict, depth: int) -> Optional[Dict]:
    body = data.get("body", "")
    if not body or body == "[deleted]" or body == "[removed]":
        return None
    return {
        "author": data.get("author", "[deleted]"),
        "body": body,
        "score": data.get("score", 0),
        "depth": depth,
        "created_utc": _format_ts(data.get("created_utc", 0)),
        "is_op": data.get("is_submitter", False),
    }


def _comment_stats(comments: List[Dict]) -> Dict[str, Any]:
    if not comments:
        return {"total": 0}
    authors = {c["author"] for c in comments}
    scores = [c["score"] for c in comments]
    return {
        "total": len(comments),
        "unique_authors": len(authors),
        "avg_score": round(sum(scores) / len(scores), 1),
        "max_score": max(scores),
        "max_depth": max(c["depth"] for c in comments),
    }


def deep_read(post_url: str, comment_depth: int = 8, comment_limit: int = 200) -> Dict[str, Any]:
    raw = cascade_fetcher.fetch_comments_raw(post_url, comment_depth, comment_limit)
    if isinstance(raw, list) and len(raw) >= 2:
        post_data = raw[0].get("data", {}).get("children", [{}])[0].get("data", {})
        comments_raw = raw[1]
    elif isinstance(raw, dict):
        post_data = raw
        comments_raw = {}
    else:
        raise ValueError(f"Unexpected response format from {post_url}")

    post = _normalize_post(post_data)
    comments = _flatten_comments(comments_raw)
    stats = _comment_stats(comments)
    return {"post": post, "comments": comments, "comment_stats": stats}


def read_top_posts(subreddit: str, sort: str = "top", timeframe: str = "week", limit: int = 10) -> List[Dict]:
    raw_posts = cascade_fetcher.fetch_posts(subreddit, sort, timeframe, limit)
    return [_normalize_post(p) for p in raw_posts]
