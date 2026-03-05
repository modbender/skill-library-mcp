"""Extract content strategies and patterns from subreddit posts.

Analyzes title hooks, content types, timing, engagement patterns,
and generates actionable strategy recommendations.
"""

import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


def _classify_post_type(post: Dict) -> str:
    title = post.get("title", "").lower()
    is_self = post.get("is_self", True)
    if not is_self:
        return "link"
    if "?" in title:
        return "question"
    if any(w in title for w in ("how to", "how i", "guide", "tutorial", "step")):
        return "how-to"
    if any(w in title for w in ("tip", "advice", "lesson", "learned")):
        return "tip"
    if any(w in title for w in ("launched", "built", "shipping", "show", "introducing")):
        return "showcase"
    if re.search(r"\d+", title):
        return "list"
    return "discussion"


def _classify_hook(title: str) -> List[str]:
    hooks: List[str] = []
    if title.strip().endswith("?"):
        hooks.append("question")
    if re.search(r"\d+", title):
        hooks.append("number")
    if re.search(r"\[.*?\]|\(.*?\)", title):
        hooks.append("bracket")
    emotional = ("amazing", "insane", "shocking", "mistake", "fail", "success", "finally", "secret")
    if any(w in title.lower() for w in emotional):
        hooks.append("emotional")
    if any(w in title.lower() for w in ("i ", "my ", "i'm", "i've")):
        hooks.append("personal")
    return hooks if hooks else ["neutral"]


def _hour_from_post(post: Dict) -> int:
    ts = post.get("created_utc", "")
    try:
        dt = datetime.fromisoformat(str(ts))
        return dt.hour
    except (ValueError, TypeError):
        return -1


def _day_from_post(post: Dict) -> str:
    ts = post.get("created_utc", "")
    try:
        dt = datetime.fromisoformat(str(ts))
        return dt.strftime("%A")
    except (ValueError, TypeError):
        return "unknown"


def _engagement_by_group(posts: List[Dict], key_fn) -> Dict[str, Dict]:
    groups: Dict[str, List[Dict]] = {}
    for p in posts:
        key = key_fn(p)
        if isinstance(key, list):
            for k in key:
                groups.setdefault(k, []).append(p)
        else:
            groups.setdefault(str(key), []).append(p)
    return {k: _summarize_group(v) for k, v in groups.items()}


def _summarize_group(posts: List[Dict]) -> Dict[str, Any]:
    scores = [p.get("score", 0) for p in posts]
    comments = [p.get("num_comments", 0) for p in posts]
    return {
        "count": len(posts),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "avg_comments": round(sum(comments) / len(comments), 1) if comments else 0,
        "max_score": max(scores) if scores else 0,
    }


def extract_strategy(posts: List[Dict]) -> Dict[str, Any]:
    if not posts:
        return {"error": "no posts to analyze"}
    by_type = _engagement_by_group(posts, _classify_post_type)
    by_hook = _engagement_by_group(posts, lambda p: _classify_hook(p.get("title", "")))
    by_hour = _engagement_by_group(posts, _hour_from_post)
    by_day = _engagement_by_group(posts, _day_from_post)
    top_5 = sorted(posts, key=lambda p: p.get("score", 0), reverse=True)[:5]
    recommendations = _build_recommendations(by_type, by_hook, by_hour, by_day, top_5)
    return {
        "total_posts_analyzed": len(posts),
        "content_types": by_type,
        "hook_patterns": by_hook,
        "timing_by_hour": by_hour,
        "timing_by_day": by_day,
        "top_5_posts": [{"title": p["title"], "score": p.get("score", 0), "type": _classify_post_type(p)} for p in top_5],
        "recommendations": recommendations,
    }


def _best_from_group(group: Dict[str, Dict], metric: str = "avg_score") -> str:
    if not group:
        return "unknown"
    return max(group.items(), key=lambda x: x[1].get(metric, 0))[0]


def _build_recommendations(by_type, by_hook, by_hour, by_day, top_posts) -> List[str]:
    recs: List[str] = []
    best_type = _best_from_group(by_type)
    recs.append(f"Best content type: '{best_type}' posts get highest avg score")
    best_hook = _best_from_group(by_hook)
    recs.append(f"Best hook pattern: '{best_hook}' titles drive most engagement")
    valid_hours = {k: v for k, v in by_hour.items() if k != "-1"}
    best_hour = _best_from_group(valid_hours) if valid_hours else "unknown"
    recs.append(f"Best posting hour (UTC): {best_hour}:00")
    valid_days = {k: v for k, v in by_day.items() if k != "unknown"}
    best_day = _best_from_group(valid_days) if valid_days else "unknown"
    recs.append(f"Best posting day: {best_day}")
    if top_posts:
        top_types = Counter(_classify_post_type(p) for p in top_posts)
        dominant = top_types.most_common(1)[0][0]
        recs.append(f"Top 5 posts are mostly '{dominant}' type")
    return recs
