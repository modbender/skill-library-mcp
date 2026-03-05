#!/usr/bin/env python3
"""Token-efficient local feed tooling for clawpod skill."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen

import feedparser
from rapidfuzz import fuzz


DEFAULT_TIMEOUT_SECONDS = 12
DEFAULT_UA = "clawpod-feed-tool/1.0 (+https://wherever.audio)"


@dataclass
class Episode:
    guid: str
    title: str
    pub_date: str
    pub_ts: float
    fallback_link: str
    description: str


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = html.unescape(str(value))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _to_iso8601(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_pub_dt(entry: Any) -> Optional[datetime]:
    parsed = getattr(entry, "published_parsed", None) or getattr(
        entry, "updated_parsed", None
    )
    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=timezone.utc)
        except (TypeError, ValueError):
            pass

    date_text = entry.get("published") or entry.get("updated")
    if date_text:
        try:
            dt = parsedate_to_datetime(date_text)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except (TypeError, ValueError):
            return None
    return None


def _pick_fallback_link(entry: Any, rss_url: str) -> str:
    link = _clean_text(entry.get("link"))
    if link and re.match(r"^https?://", link):
        return link
    enclosures = entry.get("enclosures") or []
    if enclosures and isinstance(enclosures, list):
        first = enclosures[0] or {}
        href = _clean_text(first.get("href") or first.get("url"))
        if href:
            return href
    return rss_url


def _pick_guid(entry: Any) -> str:
    for key in ("id", "guid"):
        value = _clean_text(entry.get(key))
        if value:
            return value
    # Last-resort fallback still allows deterministic link construction.
    return _clean_text(entry.get("link")) or _clean_text(entry.get("title"))


def fetch_feed(rss_url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Any:
    request = Request(rss_url, headers={"User-Agent": DEFAULT_UA})
    with urlopen(request, timeout=timeout_seconds) as response:
        data = response.read()
    return feedparser.parse(data)


def entries_to_episodes(entries: Iterable[Any], rss_url: str) -> List[Episode]:
    episodes: List[Episode] = []
    for entry in entries:
        title = _clean_text(entry.get("title"))
        guid = _pick_guid(entry)
        if not guid:
            continue
        pub_dt = _parse_pub_dt(entry)
        description = _clean_text(entry.get("summary") or entry.get("description"))
        episode = Episode(
            guid=guid,
            title=title,
            pub_date=_to_iso8601(pub_dt),
            pub_ts=pub_dt.timestamp() if pub_dt else 0.0,
            fallback_link=_pick_fallback_link(entry, rss_url),
            description=description,
        )
        episodes.append(episode)
    return episodes


def _fuzzy_score(query: str, episode: Episode) -> Tuple[float, Dict[str, float]]:
    q = query.strip()
    title = episode.title
    body = episode.description
    title_set = float(fuzz.token_set_ratio(q, title))
    title_partial = float(fuzz.partial_ratio(q, title))
    body_set = float(fuzz.token_set_ratio(q, body))
    score = 0.50 * title_set + 0.30 * title_partial + 0.20 * body_set
    breakdown = {
        "titleSet": round(title_set, 2),
        "titlePartial": round(title_partial, 2),
        "bodySet": round(body_set, 2),
    }
    return round(score, 3), breakdown


def _semantic_rerank_if_available(
    query: str, scored_rows: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], bool]:
    try:
        import numpy as np  # type: ignore
        from sentence_transformers import SentenceTransformer  # type: ignore
    except Exception:
        return scored_rows, False

    model = SentenceTransformer("all-MiniLM-L6-v2")
    docs = [f"{row['title']} {row.get('snippet', '')}".strip() for row in scored_rows]
    embeddings = model.encode([query] + docs, normalize_embeddings=True)
    qv = embeddings[0]
    doc_vecs = embeddings[1:]

    for idx, row in enumerate(scored_rows):
        cosine = float(np.dot(qv, doc_vecs[idx]))
        # Blend semantic + fuzzy while keeping output score scale 0-100.
        row["score"] = round((0.6 * row["score"]) + (0.4 * (cosine * 100.0)), 3)

    scored_rows.sort(key=lambda item: item["score"], reverse=True)
    return scored_rows, True


def build_search_result(
    rss_url: str,
    query: str,
    episodes: List[Episode],
    limit: int,
    use_semantic: bool,
    include_snippet: bool,
) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for episode in episodes:
        score, breakdown = _fuzzy_score(query, episode)
        row = {
            "guid": episode.guid,
            "title": episode.title,
            "pubDate": episode.pub_date,
            "fallbackLink": episode.fallback_link,
            "score": score,
        }
        if include_snippet:
            row["snippet"] = episode.description[:180]
        # Keep this internal and only expose when non-compact mode is requested later.
        row["_scoreBreakdown"] = breakdown
        rows.append(row)

    rows.sort(key=lambda item: item["score"], reverse=True)
    semantic_used = False
    if use_semantic and rows:
        rows, semantic_used = _semantic_rerank_if_available(query, rows)

    candidates = rows[: max(limit, 0)]
    for candidate in candidates:
        candidate.pop("_scoreBreakdown", None)

    return {
        "ok": True,
        "mode": "search",
        "rssUrl": rss_url,
        "query": query,
        "semanticUsed": semantic_used,
        "candidateCount": len(candidates),
        "candidates": candidates,
    }


def build_newest_result(rss_url: str, episodes: List[Episode], limit: int) -> Dict[str, Any]:
    items = sorted(episodes, key=lambda e: e.pub_ts, reverse=True)[: max(limit, 0)]
    return {
        "ok": True,
        "mode": "newest",
        "rssUrl": rss_url,
        "count": len(items),
        "items": [
            {
                "guid": item.guid,
                "title": item.title,
                "pubDate": item.pub_date,
                "fallbackLink": item.fallback_link,
            }
            for item in items
        ],
    }


def build_overview_result(rss_url: str, parsed_feed: Any, episodes: List[Episode]) -> Dict[str, Any]:
    meta = parsed_feed.feed or {}
    feed_description = _clean_text(meta.get("subtitle") or meta.get("description"))
    feed_description = feed_description[:200]
    last_build = _clean_text(meta.get("updated"))

    return {
        "ok": True,
        "mode": "overview",
        "rssUrl": rss_url,
        "feedTitle": _clean_text(meta.get("title")),
        "feedDescriptionShort": feed_description,
        "author": _clean_text(meta.get("author")),
        "language": _clean_text(meta.get("language")),
        "lastBuildDate": last_build,
        "itemCount": len(episodes),
    }


def error_payload(mode: str, rss_url: str, err_type: str, message: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "mode": mode,
        "rssUrl": rss_url,
        "error": {"type": err_type, "message": message},
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search and summarize podcast RSS feeds.")
    parser.add_argument("--mode", choices=["search", "newest", "overview"], required=True)
    parser.add_argument("--rss-url", required=True)
    parser.add_argument("--query", default="")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--semantic", action="store_true")
    parser.add_argument("--include-snippet", action="store_true")
    parser.add_argument("--compact", action="store_true", default=True)
    parser.add_argument("--no-compact", action="store_false", dest="compact")
    return parser.parse_args(argv)


def run(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    mode = args.mode
    rss_url = args.rss_url

    if mode == "search" and not args.query.strip():
        print(
            json.dumps(
                error_payload(mode, rss_url, "invalid_input", "search mode requires --query"),
                ensure_ascii=True,
            )
        )
        return 2

    limit_default = 5 if mode == "search" else 10
    limit = args.limit if args.limit is not None else limit_default

    try:
        parsed_feed = fetch_feed(rss_url)
    except URLError as exc:
        print(
            json.dumps(
                error_payload(mode, rss_url, "network_error", str(exc.reason)),
                ensure_ascii=True,
            )
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                error_payload(mode, rss_url, "fetch_error", str(exc)),
                ensure_ascii=True,
            )
        )
        return 1

    if parsed_feed.bozo and not parsed_feed.entries:
        print(
            json.dumps(
                error_payload(mode, rss_url, "parse_error", str(parsed_feed.bozo_exception)),
                ensure_ascii=True,
            )
        )
        return 1

    episodes = entries_to_episodes(parsed_feed.entries or [], rss_url=rss_url)
    if not episodes and mode in {"search", "newest"}:
        print(
            json.dumps(
                error_payload(mode, rss_url, "empty_feed", "feed has no usable items"),
                ensure_ascii=True,
            )
        )
        return 1

    if mode == "search":
        payload = build_search_result(
            rss_url=rss_url,
            query=args.query.strip(),
            episodes=episodes,
            limit=limit,
            use_semantic=args.semantic,
            include_snippet=args.include_snippet,
        )
    elif mode == "newest":
        payload = build_newest_result(rss_url=rss_url, episodes=episodes, limit=limit)
    else:
        payload = build_overview_result(
            rss_url=rss_url,
            parsed_feed=parsed_feed,
            episodes=episodes,
        )

    print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(run())
