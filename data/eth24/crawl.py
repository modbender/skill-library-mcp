#!/usr/bin/env python3
"""Crawl Ethereum tweets via hybrid discovery: Grok x_search + X API v2 + RSS."""

import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import httpx

SCRIPT_DIR = Path(__file__).parent
CONFIG = json.loads((SCRIPT_DIR / "config.json").read_text())

X_API_BASE = "https://api.x.com/2"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _x_headers():
    token = os.environ.get("X_BEARER_TOKEN")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}"}


def _strip_tco(text):
    """Remove t.co shortened URLs from tweet text."""
    return re.sub(r"https?://t\.co/\S+", "", text).strip()


def _score(metrics):
    """Engagement score from public_metrics."""
    return (metrics.get("like_count", 0) + metrics.get("retweet_count", 0)) / 2


# ---------------------------------------------------------------------------
# 1. Grok x_search — contextual discovery
# ---------------------------------------------------------------------------

def grok_discover():
    """Use Grok x_search to find important Ethereum tweets.

    Returns list of dicts: {url, handle, tweet_id, source}.
    Falls back gracefully if XAI_API_KEY is missing or the call fails.
    """
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        print("  XAI_API_KEY not set, skipping Grok discovery", file=sys.stderr)
        return []

    topic = CONFIG.get("topic", "Ethereum")
    terms = CONFIG["crawl"].get("x_search_terms", [])
    lookback = CONFIG["crawl"].get("lookback_hours", 24)
    now = datetime.now(timezone.utc)

    query = (
        f"Find the most important and discussed {topic} tweets from the last "
        f"{lookback} hours. Topics: {', '.join(terms)}. "
        f"Focus on protocol updates, governance, L2 developments, core dev "
        f"activity, and ecosystem milestones. Exclude pure price commentary "
        f"and shilling. Return specific tweets with their URLs."
    )

    payload = {
        "model": "grok-4-1-fast",
        "input": query,
        "tools": [{"type": "x_search"}],
    }

    try:
        resp = httpx.post(
            "https://api.x.ai/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  Grok x_search error: {e}", file=sys.stderr)
        return []

    # Extract text from output blocks
    text = ""
    for block in data.get("output", []):
        if not isinstance(block, dict):
            continue
        # Direct text block
        if block.get("type") == "output_text":
            text += block.get("text", "")
        # Nested content blocks
        for c in block.get("content", []):
            if isinstance(c, dict) and c.get("type") == "output_text":
                text += c.get("text", "")

    # Extract all tweet URLs: both x.com/handle/status/ID and x.com/i/status/ID
    # Prefer real handles over /i/ redirects for the same tweet ID
    by_id = {}
    url_re = re.compile(r"https://x\.com/(\w+)/status/(\d+)")
    for match in url_re.finditer(text):
        handle, tweet_id = match.groups()
        existing = by_id.get(tweet_id)
        # Keep the version with a real handle (not "i")
        if not existing or (existing["handle"] == "" and handle != "i"):
            by_id[tweet_id] = {
                "url": f"https://x.com/{handle}/status/{tweet_id}",
                "handle": handle if handle != "i" else "",
                "tweet_id": tweet_id,
                "source": "grok",
            }

    return list(by_id.values())


# ---------------------------------------------------------------------------
# 2. X API v2 — keyword search with engagement metrics
# ---------------------------------------------------------------------------

def _build_query():
    """Build X API search query from config terms."""
    terms = CONFIG["crawl"].get("x_search_terms", ["Ethereum"])
    return "(" + " OR ".join(terms) + ") -is:retweet -is:reply lang:en"


def search_x_api(query, max_pages=3):
    """Search recent tweets via X API v2. Returns (tweets, users_map)."""
    headers = _x_headers()
    if not headers:
        return [], {}

    lookback = CONFIG["crawl"].get("lookback_hours", 24)
    start = (datetime.now(timezone.utc) - timedelta(hours=lookback)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    params = {
        "query": query,
        "max_results": 100,
        "tweet.fields": "created_at,public_metrics,author_id,entities",
        "user.fields": "username,name,verified",
        "expansions": "author_id",
        "start_time": start,
    }

    all_tweets = []
    users_map = {}

    for page in range(max_pages):
        try:
            resp = httpx.get(
                f"{X_API_BASE}/tweets/search/recent",
                headers=headers,
                params=params,
                timeout=30,
            )

            if resp.status_code == 429:
                reset = resp.headers.get("x-rate-limit-reset", "")
                wait = max(int(reset) - int(time.time()), 1) if reset else 60
                print(f"  Rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  X API search error (page {page + 1}): {e}", file=sys.stderr)
            break

        for u in data.get("includes", {}).get("users", []):
            users_map[u["id"]] = u

        for t in data.get("data", []):
            all_tweets.append(t)

        next_token = data.get("meta", {}).get("next_token")
        if not next_token:
            break
        params["next_token"] = next_token
        count = data.get("meta", {}).get("result_count", 0)
        print(f"  Page {page + 1}: {count} tweets", file=sys.stderr)

        time.sleep(0.35)

    return all_tweets, users_map


# ---------------------------------------------------------------------------
# 3. X API v2 — tweet lookup by IDs (enrich Grok's discoveries)
# ---------------------------------------------------------------------------

def lookup_tweets(tweet_ids):
    """Fetch full tweet data for a list of IDs. Returns (tweets, users_map)."""
    headers = _x_headers()
    if not headers or not tweet_ids:
        return [], {}

    all_tweets = []
    users_map = {}

    # X API allows up to 100 IDs per request
    for i in range(0, len(tweet_ids), 100):
        batch = tweet_ids[i : i + 100]
        try:
            resp = httpx.get(
                f"{X_API_BASE}/tweets",
                headers=headers,
                params={
                    "ids": ",".join(batch),
                    "tweet.fields": "created_at,public_metrics,author_id,entities",
                    "user.fields": "username,name,verified",
                    "expansions": "author_id",
                },
                timeout=30,
            )

            if resp.status_code == 429:
                reset = resp.headers.get("x-rate-limit-reset", "")
                wait = max(int(reset) - int(time.time()), 1) if reset else 60
                print(f"  Rate limited on lookup, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  X API lookup error: {e}", file=sys.stderr)
            continue

        for u in data.get("includes", {}).get("users", []):
            users_map[u["id"]] = u
        for t in data.get("data", []):
            all_tweets.append(t)

        time.sleep(0.35)

    return all_tweets, users_map


# ---------------------------------------------------------------------------
# 4. Merge, score, filter
# ---------------------------------------------------------------------------

def _raw_to_enriched(raw_tweet, users_map, source="x_api"):
    """Convert a raw X API tweet object to our enriched format."""
    metrics = raw_tweet.get("public_metrics", {})
    author = users_map.get(raw_tweet.get("author_id"), {})
    handle = author.get("username", "")
    return {
        "id": raw_tweet["id"],
        "text": _strip_tco(raw_tweet.get("text", "")),
        "url": f"https://x.com/{handle}/status/{raw_tweet['id']}" if handle else "",
        "handle": handle,
        "author_name": author.get("name", ""),
        "created_at": raw_tweet.get("created_at", ""),
        "likes": metrics.get("like_count", 0),
        "retweets": metrics.get("retweet_count", 0),
        "replies": metrics.get("reply_count", 0),
        "quotes": metrics.get("quote_count", 0),
        "engagement_score": _score(metrics),
        "source": source,
    }


def crawl_x():
    """Hybrid crawl: Grok discovery + X API search, merged and scored."""
    print("> Crawling X (hybrid: Grok + X API)...", file=sys.stderr)

    seen_ids = set()
    candidates = []

    # --- Grok contextual discovery ---
    print("  [Grok] Contextual discovery...", file=sys.stderr)
    grok_tweets = grok_discover()
    print(f"  [Grok] Found {len(grok_tweets)} tweet URLs", file=sys.stderr)

    # Enrich Grok's picks with real metrics via X API lookup
    grok_ids = [t["tweet_id"] for t in grok_tweets]
    if grok_ids:
        raw_looked_up, lu_users = lookup_tweets(grok_ids)
        for raw in raw_looked_up:
            enriched = _raw_to_enriched(raw, lu_users, source="grok")
            if enriched["id"] not in seen_ids:
                candidates.append(enriched)
                seen_ids.add(enriched["id"])
        print(
            f"  [Grok] Enriched {len(raw_looked_up)}/{len(grok_ids)} with metrics",
            file=sys.stderr,
        )

    # --- X API keyword search ---
    query = _build_query()
    print(f"  [X API] Keyword search: {query}", file=sys.stderr)
    raw_search, search_users = search_x_api(query)
    api_added = 0
    for raw in raw_search:
        if raw["id"] not in seen_ids:
            candidates.append(_raw_to_enriched(raw, search_users, source="x_api"))
            seen_ids.add(raw["id"])
            api_added += 1
    print(f"  [X API] Added {api_added} new tweets ({len(raw_search)} total fetched)", file=sys.stderr)

    if not candidates:
        print("  No candidates found from any source", file=sys.stderr)
        return []

    # --- Spam filter: high likes/RTs but 0 replies = likely botted ---
    spam_removed = 0
    clean = []
    for t in candidates:
        if t["replies"] == 0 and t["engagement_score"] >= 50:
            spam_removed += 1
            continue
        text_lower = t["text"].lower()
        if any(w in text_lower for w in ["airdrop", "claiming your", "claim your", "grab your tokens"]):
            spam_removed += 1
            continue
        clean.append(t)
    if spam_removed:
        print(f"  Spam filtered: {spam_removed} tweets removed", file=sys.stderr)
    candidates = clean

    # --- Score, filter, return ---
    candidates.sort(key=lambda x: x["engagement_score"], reverse=True)

    # Max 2 tweets per account
    max_per_account = CONFIG["crawl"].get("max_per_account", 2)
    handle_counts = {}
    deduped = []
    for t in candidates:
        h = t["handle"].lower()
        if handle_counts.get(h, 0) >= max_per_account:
            continue
        handle_counts[h] = handle_counts.get(h, 0) + 1
        deduped.append(t)
    if len(deduped) < len(candidates):
        print(f"  Per-account cap: {len(candidates) - len(deduped)} duplicates removed", file=sys.stderr)
    candidates = deduped

    floor = CONFIG["crawl"].get("engagement_floor", 200)
    max_cand = CONFIG["crawl"].get("max_candidates", 50)
    filtered = [t for t in candidates if t["engagement_score"] >= floor]

    if len(filtered) < 10 and len(candidates) >= 10:
        floor = floor // 2
        filtered = [t for t in candidates if t["engagement_score"] >= floor]
        print(f"  Lowered floor to {floor} ({len(filtered)} candidates)", file=sys.stderr)

    if len(filtered) < 10:
        filtered = candidates[:max_cand]

    result = filtered[:max_cand]
    grok_count = sum(1 for t in result if t["source"] == "grok")
    api_count = sum(1 for t in result if t["source"] == "x_api")
    top = result[0]["engagement_score"] if result else 0
    print(
        f"  Final: {len(result)} candidates (grok: {grok_count}, x_api: {api_count}, "
        f"floor: {floor}, top: {top:.0f})",
        file=sys.stderr,
    )
    return result


# ---------------------------------------------------------------------------
# RSS
# ---------------------------------------------------------------------------

def crawl_rss():
    """Fetch RSS feeds for supplementary context."""
    print("> Crawling RSS feeds...", file=sys.stderr)
    feeds = CONFIG["crawl"].get("rss_feeds", {})
    lookback = CONFIG["crawl"].get("lookback_hours", 24)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback * 2)
    articles = []

    for name, url in feeds.items():
        print(f"  {name}...", file=sys.stderr)
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub:
                    pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue
                articles.append({
                    "source": "rss",
                    "feed": name,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"  RSS error ({name}): {e}", file=sys.stderr)

    print(f"  {len(articles)} articles", file=sys.stderr)
    return articles


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    data = {
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "tweets": crawl_x(),
        "rss": crawl_rss(),
    }

    today = datetime.now().strftime("%Y-%m-%d")
    out_dir = SCRIPT_DIR / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "crawled.json"
    out_path.write_text(json.dumps(data, indent=2))
    print(f"> Saved to {out_path}", file=sys.stderr)
    print(json.dumps(data))


if __name__ == "__main__":
    main()
