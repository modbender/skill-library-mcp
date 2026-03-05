#!/usr/bin/env python3
"""
Muninn Social Research — "What are people saying about [topic]?"
Tiered retrieval: FxTwitter (free) → Web search → Browser (last resort)
Part of OEE's Ravens/Muninn intel network.
# 🐾 Hugin watches. Muninn remembers.
"""

import sys
import os
import json
import hashlib
import time
import logging
import subprocess
import re
import textwrap
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Add parent to path for sibling imports  # 🐾
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from ravens.fxtwitter import Tweet, search_tweets as fx_search, lookup_tweet

# ─── Config ───────────────────────────────────────────────────────────
CACHE_DIR = Path(__file__).parent / ".cache"
LOG_DIR = Path(__file__).parent / ".logs"
CACHE_TTL = 3600  # 1 hour  # 🐾
DEFAULT_DAYS = 7
MAX_RESULTS = 50

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("muninn")


# ─── Usage Logging ────────────────────────────────────────────────────
# 🐾 every step tracked

def _log_usage(tier: str, query: str, result_count: int, latency_ms: int):
    """Append usage log entry."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tier": tier,
        "query": query,
        "results": result_count,
        "latency_ms": latency_ms,
    }
    log_file = LOG_DIR / f"usage-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(entry) + "\n")
    log.debug(f"Logged: tier={tier} results={result_count}")


# ─── Cache ────────────────────────────────────────────────────────────
# 🐾 the raven remembers

def _cache_key(query: str) -> str:
    return hashlib.sha256(query.encode()).hexdigest()[:16]


def _tweet_from_dict(d: dict) -> Tweet:
    """Reconstruct Tweet from dict, ignoring extra keys. 🐾"""
    import inspect
    valid = {f.name for f in __import__('dataclasses').fields(Tweet)}
    return Tweet(**{k: v for k, v in d.items() if k in valid})


def _cache_get(query: str) -> Optional[list[dict]]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(query)}.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if time.time() - data.get("ts", 0) > CACHE_TTL:
        path.unlink(missing_ok=True)
        return None
    log.info(f"Cache hit for: {query[:60]}")
    return data.get("results", [])


def _cache_set(query: str, results: list[dict]):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(query)}.json"
    path.write_text(json.dumps({"ts": time.time(), "query": query, "results": results}))


# ─── Query Decomposition ─────────────────────────────────────────────
# 🐾 breaking the hunt into tracks

def decompose_topic(topic: str) -> list[str]:
    """Break a topic into 2-4 focused search queries for X/Twitter."""
    queries = []
    # Main query
    queries.append(f"{topic} site:x.com OR site:twitter.com")
    # Opinion/reaction query
    queries.append(f'"{topic}" opinions OR thoughts OR reaction')
    # News angle
    words = topic.split()
    if len(words) <= 4:
        queries.append(f"{topic} breaking OR update OR latest")
    # Controversy angle
    queries.append(f"{topic} controversy OR debate OR backlash OR criticism")
    return queries[:4]


# ─── Tier 1: FxTwitter (FREE) ────────────────────────────────────────
# 🐾 silent wings, no cost

def tier1_fxtwitter(query: str) -> list[Tweet]:
    """Try FxTwitter search — completely free, no auth."""
    t0 = time.time()
    results = fx_search(query)
    ms = int((time.time() - t0) * 1000)
    _log_usage("tier1_fxtwitter", query, len(results), ms)
    log.info(f"Tier 1 (FxTwitter): {len(results)} results for '{query[:50]}' ({ms}ms)")
    return results


# ─── Tier 2: Web Search Fallback ─────────────────────────────────────
# 🐾 broader sweep

def tier2_web_search(query: str) -> list[Tweet]:
    """Use web search to find tweets about the topic."""
    t0 = time.time()
    tweets = []

    try:
        # Use Brave search via subprocess calling web_search patterns
        # We'll parse search results for tweet URLs and content
        search_query = f"{query} site:x.com OR site:twitter.com"
        results = _brave_search(search_query)
        tweets = _parse_search_results(results)
    except Exception as e:
        log.warning(f"Tier 2 web search failed: {e}")

    ms = int((time.time() - t0) * 1000)
    _log_usage("tier2_web_search", query, len(tweets), ms)
    log.info(f"Tier 2 (Web Search): {len(tweets)} results for '{query[:50]}' ({ms}ms)")
    return tweets


def _brave_search(query: str) -> list[dict]:
    """Call Brave search API via curl, or fallback to DDG. 🐾"""
    import urllib.request
    import urllib.parse

    api_key = os.environ.get("BRAVE_API_KEY", "")
    if api_key:
        try:
            url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count=20"
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
            results = []
            for r in data.get("web", {}).get("results", []):
                results.append({"url": r.get("url", ""), "title": r.get("title", ""), "snippet": r.get("description", "")})
            if results:
                return results
        except Exception as e:
            log.warning(f"Brave search failed: {e}")

    # Fallback: try SearXNG public instances or DDG  # 🐾
    return _searx_search(query) or _ddg_search(query)


def _searx_search(query: str) -> list[dict]:
    """Try SearXNG public instances. 🐾"""
    import urllib.request
    import urllib.parse

    instances = [
        "https://search.bus-hit.me",
        "https://searx.be",
        "https://search.sapti.me",
    ]
    for base in instances:
        try:
            url = f"{base}/search?q={urllib.parse.quote(query)}&format=json&categories=general"
            req = urllib.request.Request(url, headers={"User-Agent": "MuninnRaven/1.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())
            results = []
            for r in data.get("results", []):
                results.append({"url": r.get("url", ""), "title": r.get("title", ""), "snippet": r.get("content", "")})
            if results:
                log.info(f"SearXNG ({base}): {len(results)} results")
                return results
        except Exception:
            continue
    return []


def _ddg_search(query: str) -> list[dict]:
    """DuckDuckGo HTML search — no API key needed. 🐾"""
    import urllib.request
    import urllib.parse

    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        log.warning(f"DDG search failed: {e}")
        return []

    results = []
    # Parse result snippets  # 🐾
    # DDG HTML results have class="result__a" for links and "result__snippet" for text
    link_pattern = re.compile(r'class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.S)
    snippet_pattern = re.compile(r'class="result__snippet"[^>]*>(.*?)</(?:td|div|span)', re.S)

    links = link_pattern.findall(html)
    snippets = snippet_pattern.findall(html)

    for i, (url, title) in enumerate(links[:20]):
        title = re.sub(r'<[^>]+>', '', title).strip()
        snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip() if i < len(snippets) else ""
        # Decode DDG redirect URLs
        if "uddg=" in url:
            m = re.search(r'uddg=([^&]+)', url)
            if m:
                url = urllib.parse.unquote(m.group(1))
        results.append({"url": url, "title": title, "snippet": snippet})

    return results


def _parse_search_results(results: list[dict]) -> list[Tweet]:
    """Extract tweet-like data from search results. 🐾"""
    tweets = []
    seen_urls = set()

    for r in results:
        url = r.get("url", "")
        # Filter for twitter/x.com URLs
        tweet_match = re.search(r'(?:twitter\.com|x\.com)/(\w+)/status/(\d+)', url)
        if not tweet_match:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        username = tweet_match.group(1)
        tweet_id = tweet_match.group(2)

        # Try to enrich via FxTwitter Tier 1 lookup (still free!)  # 🐾
        enriched = lookup_tweet(username, tweet_id)
        if enriched:
            tweets.append(enriched)
        else:
            # Create from search snippet
            text = r.get("snippet", r.get("title", ""))
            tweets.append(Tweet(
                id=tweet_id,
                text=text,
                author=username,
                url=f"https://x.com/{username}/status/{tweet_id}",
            ))

    return tweets


# ─── Tier 3: Browser Automation (Last Resort) ────────────────────────
# 🐾 heavy wings — use sparingly

def tier3_browser(query: str) -> list[Tweet]:
    """
    Browser/nitter fallback. Tries multiple nitter instances.
    EXPENSIVE — only used when Tier 1+2 return insufficient results. 🐾
    """
    t0 = time.time()
    tweets = []
    log.info(f"Tier 3 (Browser): Attempting for '{query[:50]}'")

    import urllib.parse, urllib.request
    nitter_instances = [
        "https://nitter.poast.org",
        "https://nitter.woodland.cafe",
        "https://n.opnxng.com",
    ]

    for base_url in nitter_instances:
        try:
            search_url = f"{base_url}/search?f=tweets&q={urllib.parse.quote(query)}"
            req = urllib.request.Request(search_url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            tweet_blocks = re.findall(r'href="(/[^"]+/status/(\d+))"', html)
            content_blocks = re.findall(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', html, re.S)

            seen = set()
            for i, (path, tid) in enumerate(tweet_blocks[:20]):
                if tid in seen:
                    continue
                seen.add(tid)
                m = re.match(r'/(\w+)/status/\d+', path)
                if not m:
                    continue
                username = m.group(1)
                text = re.sub(r'<[^>]+>', '', content_blocks[i]).strip() if i < len(content_blocks) else ""
                tweets.append(Tweet(
                    id=tid, text=text, author=username,
                    url=f"https://x.com/{username}/status/{tid}",
                ))
            if tweets:
                break
        except Exception as e:
            log.debug(f"Nitter {base_url} failed: {e}")
            continue

    ms = int((time.time() - t0) * 1000)
    _log_usage("tier3_browser", query, len(tweets), ms)
    log.info(f"Tier 3 (Browser): {len(tweets)} results ({ms}ms)")
    return tweets


# ─── Filtering & Dedup ───────────────────────────────────────────────
# 🐾 separating signal from noise

def filter_tweets(tweets: list[Tweet], days: int = DEFAULT_DAYS) -> list[Tweet]:
    """Filter, deduplicate, remove spam and RTs."""
    seen_ids = set()
    seen_texts = set()
    filtered = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for t in tweets:
        # Skip dupes
        if t.id in seen_ids:
            continue
        # Skip RTs
        if t.is_retweet or t.text.startswith("RT @"):
            continue
        # Skip near-duplicate text (first 80 chars)
        text_key = re.sub(r'\s+', ' ', t.text[:80].lower().strip())
        if text_key in seen_texts:
            continue
        # Spam heuristics  # 🐾
        spam_signals = [
            len(re.findall(r'#\w+', t.text)) > 5,  # hashtag spam
            t.text.count('🚀') > 2,  # rocket spam
            re.search(r'(follow me|check my|link in bio|giveaway|airdrop)', t.text, re.I),
            len(t.text) < 15,  # too short
        ]
        if sum(bool(s) for s in spam_signals) >= 2:
            continue
        # Timeframe filter (if we have date)
        if t.created_at:
            try:
                tweet_time = datetime.fromisoformat(t.created_at.replace("Z", "+00:00"))
                if tweet_time < cutoff:
                    continue
            except (ValueError, TypeError):
                pass

        seen_ids.add(t.id)
        seen_texts.add(text_key)
        filtered.append(t)

    # Rank by engagement  # 🐾
    filtered.sort(key=lambda t: t.engagement, reverse=True)
    return filtered[:MAX_RESULTS]


# ─── Tiered Retrieval ────────────────────────────────────────────────
# 🐾 cheapest flight path first

def research_topic(topic: str, days: int = DEFAULT_DAYS, min_results: int = 5) -> list[Tweet]:
    """Execute tiered retrieval for a topic."""
    queries = decompose_topic(topic)
    all_tweets: list[Tweet] = []

    for q in queries:
        # Check cache first
        cached = _cache_get(q)
        if cached:
            all_tweets.extend([_tweet_from_dict(c) if isinstance(c, dict) else c for c in cached])
            continue

        query_tweets: list[Tweet] = []

        # Tier 1: FxTwitter (free)  # 🐾
        query_tweets = tier1_fxtwitter(q)

        # Tier 2: Web search if insufficient
        if len(query_tweets) < 3:
            t2 = tier2_web_search(q)
            query_tweets.extend(t2)

        # Tier 3: Browser only if still insufficient
        if len(query_tweets) < 2:
            t3 = tier3_browser(topic)  # Use original topic, not decomposed
            query_tweets.extend(t3)

        # Cache results  # 🐾
        _cache_set(q, [t.to_dict() for t in query_tweets])
        all_tweets.extend(query_tweets)

    return filter_tweets(all_tweets, days)


# ─── Briefing Synthesis ──────────────────────────────────────────────
# 🐾 Muninn speaks

def synthesize_briefing(topic: str, tweets: list[Tweet]) -> str:
    """Synthesize collected tweets into an intel briefing."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not tweets:
        return textwrap.dedent(f"""\
        ═══ MUNINN INTEL BRIEFING ═══
        Topic: {topic}
        Generated: {now}
        
        ⚠️  No significant social media activity found.
        Tiers exhausted: FxTwitter → Web Search → Browser
        
        Possible reasons:
        - Topic too niche or misspelled
        - Activity outside search window
        - API/network issues
        ═════════════════════════════
        """)

    # Analyze sentiment distribution  # 🐾
    positive_words = {'great', 'love', 'amazing', 'good', 'best', 'excellent', 'awesome',
                      'happy', 'excited', 'bullish', 'win', 'success', 'beautiful', 'fantastic'}
    negative_words = {'bad', 'terrible', 'worst', 'hate', 'awful', 'horrible', 'disaster',
                      'fail', 'crash', 'scam', 'fraud', 'angry', 'disgusting', 'pathetic'}
    pos_count = neg_count = neu_count = 0

    for t in tweets:
        words = set(t.text.lower().split())
        p = len(words & positive_words)
        n = len(words & negative_words)
        if p > n:
            pos_count += 1
        elif n > p:
            neg_count += 1
        else:
            neu_count += 1

    total = len(tweets)
    sentiment = (
        f"Positive: {pos_count}/{total} ({100*pos_count//total}%) | "
        f"Negative: {neg_count}/{total} ({100*neg_count//total}%) | "
        f"Neutral: {neu_count}/{total} ({100*neu_count//total}%)"
    )

    # Extract key narratives (cluster by keyword overlap)  # 🐾
    narratives = _extract_narratives(tweets)

    # Notable posts (top by engagement)
    notable = tweets[:10]

    # Contrarian takes (minority sentiment)
    majority_positive = pos_count > neg_count
    contrarian = []
    for t in tweets:
        words = set(t.text.lower().split())
        is_pos = len(words & positive_words) > len(words & negative_words)
        if majority_positive and not is_pos and len(words & negative_words) > 0:
            contrarian.append(t)
        elif not majority_positive and is_pos and len(words & positive_words) > 0:
            contrarian.append(t)
    contrarian = contrarian[:3]

    # Build briefing  # 🐾
    lines = [
        f"═══ MUNINN INTEL BRIEFING ═══",
        f"Topic: {topic}",
        f"Generated: {now}",
        f"Tweets analyzed: {total}",
        f"",
        f"── SENTIMENT ──",
        f"{sentiment}",
        f"Overall lean: {'POSITIVE 📈' if pos_count > neg_count else 'NEGATIVE 📉' if neg_count > pos_count else 'MIXED ↔️'}",
        f"",
        f"── KEY NARRATIVES ──",
    ]
    for i, (label, count) in enumerate(narratives[:5], 1):
        lines.append(f"  {i}. {label} ({count} mentions)")

    lines.extend([
        f"",
        f"── NOTABLE POSTS ──",
    ])
    for i, t in enumerate(notable, 1):
        eng = f"❤️{t.likes} 🔁{t.retweets} 💬{t.replies}" if t.likes or t.retweets else ""
        text_preview = t.text[:120].replace('\n', ' ')
        lines.append(f"  {i}. @{t.author}: {text_preview}")
        if eng:
            lines.append(f"     {eng}")
        lines.append(f"     🔗 {t.url}")
        lines.append("")

    if contrarian:
        lines.append(f"── CONTRARIAN TAKES ──")
        for t in contrarian:
            text_preview = t.text[:120].replace('\n', ' ')
            lines.append(f"  • @{t.author}: {text_preview}")
            lines.append(f"    🔗 {t.url}")
        lines.append("")

    lines.append("═════════════════════════════")
    lines.append("# 🐾 Muninn has spoken.")

    return "\n".join(lines)


def _extract_narratives(tweets: list[Tweet]) -> list[tuple[str, int]]:
    """Extract dominant narrative themes via keyword frequency. 🐾"""
    # Simple keyword extraction (no ML deps needed)
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'don', 'now', 'this',
        'that', 'it', 'its', 'i', 'me', 'my', 'we', 'our', 'you', 'your',
        'he', 'she', 'they', 'them', 'their', 'what', 'which', 'who', 'whom',
        'and', 'but', 'or', 'if', 'while', 'about', 'up', 'his', 'her',
        'https', 'http', 'com', 'rt', 'amp', 'get', 'got', 'like', 'going',
        'think', 'know', 'say', 'said', 'one', 'new', 'also', 'people',
    }

    bigram_counts: dict[str, int] = {}
    for t in tweets:
        words = re.findall(r'[a-zA-Z]+', t.text.lower())
        words = [w for w in words if w not in stop_words and len(w) > 2]
        for i in range(len(words) - 1):
            bg = f"{words[i]} {words[i+1]}"
            bigram_counts[bg] = bigram_counts.get(bg, 0) + 1

    # Sort by frequency, take top narratives
    sorted_bg = sorted(bigram_counts.items(), key=lambda x: x[1], reverse=True)
    # Deduplicate overlapping bigrams
    used = set()
    narratives = []
    for bg, count in sorted_bg:
        if count < 2:
            break
        words = bg.split()
        if any(w in used for w in words):
            continue
        used.update(words)
        narratives.append((bg.title(), count))
        if len(narratives) >= 5:
            break

    return narratives


# ─── OpenClaw Integration ─────────────────────────────────────────────
# 🐾 when called as a library by the agent

def inject_search_results(topic: str, search_results: list[dict], days: int = DEFAULT_DAYS) -> str:
    """
    Accept pre-fetched search results (from OpenClaw web_search tool) and
    produce a briefing. Each result should have: url, title, snippet.
    This bypasses Tier 2/3 network calls entirely. 🐾
    """
    tweets = _parse_search_results(search_results)

    # Enrich tweet URLs via FxTwitter (Tier 1, free)
    enriched = []
    for t in tweets:
        looked_up = lookup_tweet(t.author, t.id)
        enriched.append(looked_up if looked_up else t)

    filtered = filter_tweets(enriched, days)
    return synthesize_briefing(topic, filtered)


# ─── Main ─────────────────────────────────────────────────────────────
# 🐾

def main():
    if len(sys.argv) < 2:
        print("Usage: python social_research.py \"topic here\"")
        print("  Options:")
        print("    --days N    Search window (default: 7)")
        print("    --verbose   Debug logging")
        sys.exit(1)

    topic = sys.argv[1]
    days = DEFAULT_DAYS
    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        days = int(sys.argv[idx + 1])
    if "--verbose" in sys.argv:
        logging.getLogger().setLevel(logging.DEBUG)

    print(f"🐦‍⬛ Muninn researching: \"{topic}\"")
    print(f"   Window: {days} days | Tiers: FxTwitter → Web → Browser")
    print()

    tweets = research_topic(topic, days=days)
    briefing = synthesize_briefing(topic, tweets)
    print(briefing)

    # Also save to file  # 🐾
    out_dir = Path(__file__).parent / ".briefings"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r'[^a-z0-9]+', '-', topic.lower())[:40]
    out_file = out_dir / f"{datetime.now().strftime('%Y%m%d-%H%M')}-{slug}.txt"
    out_file.write_text(briefing)
    print(f"\n📄 Briefing saved: {out_file}")


if __name__ == "__main__":
    main()
