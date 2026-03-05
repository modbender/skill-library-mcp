"""
reddit_capture.py — Reddit + Hacker News Signal Capture

Fetches OpenClaw/ClawHub discussions from Reddit and Hacker News.
Structures them via Claude Haiku into the standard signal schema.
Appends to data/weekly_signals.json (same file as x_capture.py).

All APIs are free and require no authentication.
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

import anthropic

SIGNALS_PATH = Path(__file__).parent / "data" / "weekly_signals.json"

# Reddit search queries (no auth needed)
REDDIT_QUERIES = [
    "openclaw OR clawhub",
    "openclaw skills",
    "clawhub skill marketplace",
]

REDDIT_SUBREDDITS = [
    "ClaudeAI",
    "LocalLLaMA",
    "artificial",
]

# Hacker News queries (Algolia API, free)
HN_QUERIES = ["openclaw", "clawhub"]

HAIKU_MODEL = "claude-haiku-4-5-20251001"

STRUCTURE_PROMPT = """You are a signal classifier for an AI agent skills newsletter.

Given these community posts about OpenClaw/ClawHub, extract structured signals.

For EACH relevant post, output a JSON object with:
- "date": ISO date string (YYYY-MM-DD)
- "category": one of "tutorial", "security", "ecosystem", "showcase", "discussion", "market"
- "title": concise descriptive title (not the raw post title)
- "url": the post URL
- "summary": 1-2 sentence summary of what's discussed
- "tags": list of 2-4 lowercase tags
- "source": "{source}"

Skip posts that are:
- Not about OpenClaw, ClawHub, or AI agent skills
- Spam, low-effort, or duplicates
- Job postings or self-promotion without substance

Output a JSON array of signal objects. If no posts are relevant, output [].
"""


def _fetch_json(url: str) -> dict | list | None:
    """Fetch JSON from a URL with User-Agent header."""
    try:
        req = Request(url, headers={
            "User-Agent": "OpenClawSkillsWeekly/1.0 (signal capture bot)",
        })
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  [WARN] Fetch failed {url[:80]}: {e}")
        return None


def _search_reddit(days: int = 7) -> list[dict]:
    """Search Reddit for OpenClaw/ClawHub posts. No auth required."""
    posts = []
    seen_ids = set()

    for query in REDDIT_QUERIES:
        url = (
            f"https://www.reddit.com/search.json"
            f"?q={query.replace(' ', '+')}&sort=new&limit=50&t=week"
        )
        data = _fetch_json(url)
        if not data or "data" not in data:
            continue

        for child in data["data"].get("children", []):
            post = child.get("data", {})
            post_id = post.get("id", "")
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            created = datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc)
            posts.append({
                "title": post.get("title", ""),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "subreddit": post.get("subreddit", ""),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "date": created.strftime("%Y-%m-%d"),
                "selftext": (post.get("selftext", "") or "")[:500],
            })
        time.sleep(1)  # Reddit rate limit politeness

    # Also check specific subreddits
    for sub in REDDIT_SUBREDDITS:
        url = (
            f"https://www.reddit.com/r/{sub}/search.json"
            f"?q=openclaw+OR+clawhub&sort=new&limit=25&t=week&restrict_sr=on"
        )
        data = _fetch_json(url)
        if not data or "data" not in data:
            continue

        for child in data["data"].get("children", []):
            post = child.get("data", {})
            post_id = post.get("id", "")
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            created = datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc)
            posts.append({
                "title": post.get("title", ""),
                "url": f"https://reddit.com{post.get('permalink', '')}",
                "subreddit": post.get("subreddit", ""),
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "date": created.strftime("%Y-%m-%d"),
                "selftext": (post.get("selftext", "") or "")[:500],
            })
        time.sleep(1)

    print(f"  [REDDIT] Found {len(posts)} posts")
    return posts


def _search_hackernews(days: int = 7) -> list[dict]:
    """Search Hacker News via Algolia API. Free, no auth."""
    cutoff = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    posts = []
    seen_ids = set()

    for query in HN_QUERIES:
        url = (
            f"https://hn.algolia.com/api/v1/search_by_date"
            f"?query={query}&tags=story"
            f"&numericFilters=created_at_i>{cutoff}"
        )
        data = _fetch_json(url)
        if not data:
            continue

        for hit in data.get("hits", []):
            hn_id = hit.get("objectID", "")
            if hn_id in seen_ids:
                continue
            seen_ids.add(hn_id)

            posts.append({
                "title": hit.get("title", ""),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hn_id}",
                "hn_url": f"https://news.ycombinator.com/item?id={hn_id}",
                "points": hit.get("points", 0),
                "num_comments": hit.get("num_comments", 0),
                "date": datetime.fromtimestamp(
                    hit.get("created_at_i", 0), tz=timezone.utc
                ).strftime("%Y-%m-%d"),
            })

    print(f"  [HN] Found {len(posts)} stories")
    return posts


def _fix_json(text: str) -> str:
    """Try to fix common LLM JSON issues (trailing commas, unescaped quotes)."""
    import re
    # Remove trailing commas before ] or }
    text = re.sub(r',\s*([}\]])', r'\1', text)
    # Fix unescaped newlines inside strings
    text = text.replace('\n', '\\n')
    # Restore structural newlines (between array items and object braces)
    text = re.sub(r'\\n(\s*[{\[\]},])', lambda m: '\n' + m.group(1), text)
    return text


def _structure_batch(posts: list[dict], source: str, client) -> list[dict]:
    """Structure a single batch of posts via Haiku."""
    post_text = "\n\n".join(
        f"Title: {p['title']}\nURL: {p['url']}\nDate: {p['date']}\n"
        f"Score: {p.get('score', p.get('points', 0))}, "
        f"Comments: {p.get('num_comments', 0)}\n"
        f"{'Subreddit: ' + p['subreddit'] if 'subreddit' in p else ''}\n"
        f"{p.get('selftext', '')[:200]}"
        for p in posts
    )

    prompt = STRUCTURE_PROMPT.replace("{source}", source) + f"\n\nPosts:\n{post_text}"

    try:
        msg = client.messages.create(
            model=HAIKU_MODEL,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text.strip()
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            raw = text[start:end]
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return json.loads(_fix_json(raw))
    except (anthropic.APIError, json.JSONDecodeError) as e:
        print(f"  [WARN] Batch structuring failed for {source}: {e}")

    return []


def _structure_signals(posts: list[dict], source: str, api_key: str) -> list[dict]:
    """Use Haiku to classify and structure raw posts into signal schema.
    Batches posts in chunks of 30 to avoid LLM output truncation."""
    if not posts:
        return []

    client = anthropic.Anthropic(api_key=api_key)
    batch_size = 30
    all_signals = []

    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        signals = _structure_batch(batch, source, client)
        all_signals.extend(signals)
        if i + batch_size < len(posts):
            time.sleep(0.5)  # Rate limit politeness

    print(f"  [STRUCTURE] {len(all_signals)} signals from {source} ({len(posts)} posts in {(len(posts) - 1) // batch_size + 1} batches)")
    return all_signals


def _dedup_and_append(new_signals: list[dict]) -> int:
    """Deduplicate by URL and append to weekly_signals.json."""
    SIGNALS_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if SIGNALS_PATH.exists():
        try:
            existing = json.loads(SIGNALS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing_urls = {s.get("url", "") for s in existing}
    added = 0

    for sig in new_signals:
        url = sig.get("url", "")
        if url and url not in existing_urls:
            existing.append(sig)
            existing_urls.add(url)
            added += 1

    SIGNALS_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    print(f"  [DEDUP] {added} new signals added ({len(existing)} total)")
    return added


def capture(days: int = 7, skip_haiku: bool = False) -> int:
    """
    Full capture: Reddit + HN search → structure → dedup → append.
    Returns number of new signals added.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    print("[REDDIT+HN] Searching for OpenClaw/ClawHub signals...")

    # Fetch from both sources
    reddit_posts = _search_reddit(days=days)
    hn_posts = _search_hackernews(days=days)

    all_signals = []

    if reddit_posts and api_key and not skip_haiku:
        all_signals.extend(_structure_signals(reddit_posts, "reddit", api_key))
    elif reddit_posts:
        # Fallback: create basic signals without Haiku structuring
        for p in reddit_posts:
            all_signals.append({
                "date": p["date"],
                "category": "discussion",
                "title": p["title"][:100],
                "url": p["url"],
                "summary": p.get("selftext", "")[:200] or p["title"],
                "tags": ["reddit", p.get("subreddit", "").lower()],
                "source": "reddit",
            })

    if hn_posts and api_key and not skip_haiku:
        all_signals.extend(_structure_signals(hn_posts, "hackernews", api_key))
    elif hn_posts:
        for p in hn_posts:
            all_signals.append({
                "date": p["date"],
                "category": "discussion",
                "title": p["title"][:100],
                "url": p.get("hn_url", p["url"]),
                "summary": p["title"],
                "tags": ["hackernews"],
                "source": "hackernews",
            })

    if not all_signals:
        print("[REDDIT+HN] No signals found")
        return 0

    return _dedup_and_append(all_signals)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    capture()
