#!/usr/bin/env python3
"""
Kiro Search Aggregator
Aggregate Google, Scholar, YouTube, and X search into a single ranked brief.

Plugin producer: kiroai.io
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


SERPER_BASE = "https://google.serper.dev"
SERPAPI_BASE = "https://serpapi.com/search.json"
X_RECENT_SEARCH = "https://api.x.com/2/tweets/search/recent"


@dataclass
class SearchItem:
    source: str
    title: str
    url: str
    snippet: str
    published_at: Optional[str]
    score: float
    meta: Dict[str, Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def request_json(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    body: Optional[Dict[str, Any]] = None,
    timeout: int = 20,
) -> Dict[str, Any]:
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
        url = f"{url}?{query}"

    req_headers = {"User-Agent": "kiro-search-aggregator/0.1"}
    if headers:
        req_headers.update(headers)

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, data=data, headers=req_headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            raw = exc.read()
            if raw:
                detail = raw.decode("utf-8", errors="replace")
        except Exception:
            pass
        msg = f"HTTP {exc.code} {exc.reason} @ {url}"
        if detail:
            msg += f" | response={detail[:700]}"
        raise RuntimeError(msg) from exc


def parse_iso(ts: Optional[str]) -> Optional[float]:
    if not ts:
        return None
    try:
        norm = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(norm).timestamp()
    except Exception:
        return None


def recency_bonus(published_at: Optional[str]) -> float:
    ts = parse_iso(published_at)
    if ts is None:
        return 0.0
    age_h = max(0.0, (time.time() - ts) / 3600.0)
    if age_h < 6:
        return 2.5
    if age_h < 24:
        return 1.5
    if age_h < 72:
        return 0.8
    return 0.0


def source_base_score(source: str) -> float:
    weights = {
        "google": 5.0,
        "scholar": 6.0,
        "youtube": 4.0,
        "x": 4.5,
    }
    return weights.get(source, 3.0)


def score_item(source: str, rank_index: int, published_at: Optional[str]) -> float:
    rank_bonus = max(0.0, 3.5 - (rank_index * 0.35))
    return round(source_base_score(source) + rank_bonus + recency_bonus(published_at), 4)


def search_google_serper(query: str, per_source: int) -> List[SearchItem]:
    key = (os.getenv("SERPER_API_KEY") or "").strip()
    if not key:
        return []
    payload = request_json(
        method="POST",
        url=f"{SERPER_BASE}/search",
        headers={"X-API-KEY": key},
        body={"q": query, "num": per_source},
    )
    items: List[SearchItem] = []
    for i, row in enumerate(payload.get("organic", [])[:per_source]):
        items.append(
            SearchItem(
                source="google",
                title=str(row.get("title") or ""),
                url=str(row.get("link") or ""),
                snippet=str(row.get("snippet") or ""),
                published_at=None,
                score=score_item("google", i, None),
                meta={"position": row.get("position")},
            )
        )
    return items


def search_youtube_serper(query: str, per_source: int) -> List[SearchItem]:
    key = (os.getenv("SERPER_API_KEY") or "").strip()
    if not key:
        return []
    payload = request_json(
        method="POST",
        url=f"{SERPER_BASE}/videos",
        headers={"X-API-KEY": key},
        body={"q": query, "num": per_source},
    )
    items: List[SearchItem] = []
    for i, row in enumerate(payload.get("videos", [])[:per_source]):
        published = row.get("publishedAt")
        items.append(
            SearchItem(
                source="youtube",
                title=str(row.get("title") or ""),
                url=str(row.get("link") or ""),
                snippet=str(row.get("snippet") or ""),
                published_at=str(published) if published else None,
                score=score_item("youtube", i, str(published) if published else None),
                meta={
                    "channel": row.get("channelName"),
                    "duration": row.get("duration"),
                },
            )
        )
    return items


def search_scholar_serpapi(query: str, per_source: int) -> List[SearchItem]:
    key = (os.getenv("SERPAPI_API_KEY") or "").strip()
    if not key:
        return []
    payload = request_json(
        method="GET",
        url=SERPAPI_BASE,
        params={
            "engine": "google_scholar",
            "q": query,
            "num": per_source,
            "api_key": key,
        },
    )
    items: List[SearchItem] = []
    for i, row in enumerate(payload.get("organic_results", [])[:per_source]):
        pub_info = row.get("publication_info") or {}
        summary = pub_info.get("summary") or ""
        year_match = re.search(r"\b(20\d{2}|19\d{2})\b", str(summary))
        year = year_match.group(1) if year_match else None
        items.append(
            SearchItem(
                source="scholar",
                title=str(row.get("title") or ""),
                url=str(row.get("link") or ""),
                snippet=str(row.get("snippet") or summary or ""),
                published_at=f"{year}-01-01T00:00:00+00:00" if year else None,
                score=score_item("scholar", i, f"{year}-01-01T00:00:00+00:00" if year else None),
                meta={"cited_by": ((row.get("inline_links") or {}).get("cited_by") or {}).get("total")},
            )
        )
    return items


def search_x_recent(query: str, per_source: int) -> List[SearchItem]:
    token = (os.getenv("X_BEARER_TOKEN") or "").strip()
    if not token:
        return []
    payload = request_json(
        method="GET",
        url=X_RECENT_SEARCH,
        headers={"Authorization": f"Bearer {token}"},
        params={
            "query": f"{query} -is:retweet -is:reply",
            "max_results": max(10, min(100, per_source)),
            "tweet.fields": "created_at,public_metrics,lang,author_id",
            "user.fields": "username,name",
            "expansions": "author_id",
        },
    )

    users = {u.get("id"): u for u in payload.get("includes", {}).get("users", [])}
    items: List[SearchItem] = []
    for i, row in enumerate(payload.get("data", [])[:per_source]):
        author_id = row.get("author_id")
        user = users.get(author_id, {})
        username = str(user.get("username") or "unknown")
        tid = str(row.get("id") or "")
        if not tid:
            continue
        created_at = str(row.get("created_at") or "")
        metrics = row.get("public_metrics") or {}
        metric_signal = (
            int(metrics.get("like_count") or 0)
            + int(metrics.get("retweet_count") or 0) * 2
            + int(metrics.get("reply_count") or 0) * 2
        )
        score = score_item("x", i, created_at) + min(3.0, metric_signal / 20.0)
        items.append(
            SearchItem(
                source="x",
                title=f"@{username}",
                url=f"https://x.com/{username}/status/{tid}",
                snippet=str(row.get("text") or ""),
                published_at=created_at or None,
                score=round(score, 4),
                meta={"metrics": metrics, "lang": row.get("lang")},
            )
        )
    return items


def source_status(selected: List[str]) -> Dict[str, Dict[str, Any]]:
    return {
        "google": {"selected": "google" in selected, "configured": bool((os.getenv("SERPER_API_KEY") or "").strip())},
        "youtube": {"selected": "youtube" in selected, "configured": bool((os.getenv("SERPER_API_KEY") or "").strip())},
        "scholar": {"selected": "scholar" in selected, "configured": bool((os.getenv("SERPAPI_API_KEY") or "").strip())},
        "x": {"selected": "x" in selected, "configured": bool((os.getenv("X_BEARER_TOKEN") or "").strip())},
    }


def summarize(items: List[SearchItem]) -> Dict[str, Any]:
    by_source: Dict[str, int] = {}
    for item in items:
        by_source[item.source] = by_source.get(item.source, 0) + 1
    return {
        "total_results": len(items),
        "source_counts": by_source,
        "top_scores": [round(i.score, 3) for i in items[:5]],
    }


def render_markdown(result: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# Search Brief: {result['query']}")
    lines.append("")
    lines.append(f"- Generated at: {result['generated_at']}")
    lines.append(f"- Sources: {', '.join(result['sources'])}")
    lines.append(f"- Total results: {result['summary']['total_results']}")
    lines.append("")
    lines.append("## Top Results")
    lines.append("")
    for idx, row in enumerate(result["results"][:20], start=1):
        lines.append(f"{idx}. [{row['title']}]({row['url']})")
        lines.append(f"   - source: `{row['source']}` | score: `{row['score']}`")
        if row.get("published_at"):
            lines.append(f"   - published_at: `{row['published_at']}`")
        if row.get("snippet"):
            lines.append(f"   - {row['snippet'][:260]}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate multi-source search for Kiro")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument(
        "--sources",
        default="google,scholar,youtube,x",
        help="Comma-separated sources: google,scholar,youtube,x",
    )
    parser.add_argument("--per-source", type=int, default=5, help="Results per source")
    parser.add_argument("--top-k", type=int, default=20, help="Final merged top-k")
    parser.add_argument("--out-dir", default="outputs/search-aggregator", help="Output folder")
    args = parser.parse_args()

    selected = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    source_map = {
        "google": search_google_serper,
        "scholar": search_scholar_serpapi,
        "youtube": search_youtube_serper,
        "x": search_x_recent,
    }
    unknown = [s for s in selected if s not in source_map]
    if unknown:
        raise SystemExit(f"unknown sources: {', '.join(unknown)}")

    merged: List[SearchItem] = []
    errors: Dict[str, str] = {}
    for source in selected:
        fn = source_map[source]
        try:
            merged.extend(fn(args.query, args.per_source))
        except Exception as exc:
            errors[source] = str(exc)

    merged.sort(key=lambda x: x.score, reverse=True)
    merged = merged[: max(1, args.top_k)]

    result = {
        "generated_at": now_iso(),
        "query": args.query,
        "sources": selected,
        "source_status": source_status(selected),
        "errors": errors,
        "summary": summarize(merged),
        "results": [asdict(i) for i in merged],
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "latest.md").write_text(render_markdown(result), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
