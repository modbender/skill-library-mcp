#!/usr/bin/env python3
"""
finviz-crawler v3.2 — Crawl4AI + RSS hybrid financial news crawler.

Architecture:
  - SQLite stores METADATA ONLY
  - Title stored LOWERCASE in DB (dedup key via sha256 hash)
  - publish_at = system local time in ISO 8601 (configurable via FINVIZ_TZ or TZ env)
  - article_path NULL until written to disk; real filename after crawl
  - Full article content stored as .md files on disk (underscore_joined filenames)
  - Crawl4AI with Playwright for crawlable sites (Reuters, Yahoo, BBC, etc.)
  - RSS feeds for paywalled sites (Bloomberg, MarketWatch) — summaries only
  - Bot/paywall detection rejects garbage content
  - Per-domain rate limiting, user-agent rotation, robots.txt respected
  - Clean shutdown on SIGTERM/SIGINT

Usage:
    python3 finviz_crawler.py [--db PATH] [--articles-dir PATH] [--sleep SECONDS]
"""
import argparse
import asyncio
import hashlib
import logging
import os
import re
import signal
import sqlite3
import time
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import feedparser
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

def _detect_local_tz() -> ZoneInfo:
    """Detect local timezone from env or system. Fallback to UTC."""
    for env_key in ("FINVIZ_TZ", "TZ"):
        tz_name = os.environ.get(env_key)
        if tz_name:
            try:
                return ZoneInfo(tz_name)
            except Exception:
                pass
    try:
        with open("/etc/timezone") as f:
            return ZoneInfo(f.read().strip())
    except Exception:
        pass
    return ZoneInfo("UTC")

LOCAL_TZ = _detect_local_tz()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FINVIZ_NEWS_URL = "https://finviz.com/news.ashx"
FINVIZ_QUOTE_URL = "https://finviz.com/quote.ashx?t={ticker}&p=d"
DEFAULT_DB = os.path.expanduser("~/Downloads/Finviz/finviz.db")
DEFAULT_ARTICLES_DIR = os.path.expanduser("~/Downloads/Finviz/articles")
DEFAULT_SLEEP = 300
DOMAIN_DELAY = 3.0
BATCH_SIZE = 50
MAX_RETRIES = 3
EXPIRY_DAYS = int(os.environ.get("FINVIZ_EXPIRY_DAYS", "7"))  # overwritten by CLI --expiry-days

# Tickers to scrape news for (loaded from DB or env)
DEFAULT_TICKERS = ["QQQ", "AMZN", "GOOGL", "TSLA", "META", "NVDA"]


def _load_tickers() -> list[str]:
    """Load tickers from DB tickers table, plus defaults as fallback."""
    db_path = os.path.expanduser("~/Downloads/Finviz/finviz.db")
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            rows = conn.execute("SELECT symbol FROM tickers").fetchall()
            conn.close()
            if rows:
                tickers = [r[0] for r in rows]
                # Add any extras from env
                env_tickers = os.environ.get("FINVIZ_TICKERS", "")
                if env_tickers:
                    for t in env_tickers.split(","):
                        t = t.strip().upper()
                        if t and t not in tickers:
                            tickers.append(t)
                return tickers
        except Exception:
            pass
    # Fallback to defaults + env
    tickers = list(DEFAULT_TICKERS)
    env_tickers = os.environ.get("FINVIZ_TICKERS", "")
    if env_tickers:
        for t in env_tickers.split(","):
            t = t.strip().upper()
            if t and t not in tickers:
                tickers.append(t)
    return tickers

AD_DOMAINS = {
    "adclick.g.doubleclick.net", "googleads.g.doubleclick.net",
    "ad.doubleclick.net", "pagead2.googlesyndication.com",
    "ads.google.com", "adsrvr.org",
}

# Domains that block crawlers — use RSS instead
RSS_FEEDS = {
    "bloomberg.com": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://feeds.bloomberg.com/technology/news.rss",
    ],
    "marketwatch.com": [
        "https://feeds.marketwatch.com/marketwatch/topstories",
        "https://feeds.marketwatch.com/marketwatch/marketpulse",
    ],
}
RSS_DOMAINS = set(RSS_FEEDS.keys())

# Bot-blocked / paywall / captcha patterns
BOT_BLOCK_PATTERNS = [
    r"we.ve detected unusual activity",
    r"please click the box below",
    r"are you a robot",
    r"captcha",
    r"access denied",
    r"enable javascript.*cookies",
    r"subscribe to continue reading",
    r"create a free account to continue",
    r"this content is for subscribers",
]
BOT_BLOCK_RE = re.compile("|".join(BOT_BLOCK_PATTERNS), re.IGNORECASE)

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
]

log = logging.getLogger("finviz-crawler")

# ---------------------------------------------------------------------------
# Shutdown
# ---------------------------------------------------------------------------
shutdown_event = asyncio.Event()


def _handle_signal(signum, _frame):
    log.info("Received %s — requesting clean shutdown", signal.Signals(signum).name)
    shutdown_event.set()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_domain(url: str) -> str:
    try:
        d = re.sub(r"^www\.", "", urlparse(url).netloc.lower())
        return d if d else "unknown"
    except Exception:
        return "unknown"


def sanitize_filename(title: str, max_len: int = 120) -> str:
    """Turn a title into a human-readable underscore_joined filename."""
    s = unicodedata.normalize("NFKD", title)
    s = s.encode("ascii", "ignore").decode("ascii").lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    if len(s) > max_len:
        s = s[:max_len].rsplit("_", 1)[0]
    return s or "untitled"


def title_hash(title: str) -> str:
    """sha256 hash of normalized lowercase title for dedup."""
    normalized = re.sub(r"\s+", " ", title.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def now_seattle() -> str:
    """Current time in America/Los_Angeles as ISO 8601."""
    return datetime.now(LOCAL_TZ).isoformat()


def is_bot_blocked(content: str) -> bool:
    """Reject bot-detection / paywall / captcha content."""
    if not content:
        return True
    if len(content) < 2000 and BOT_BLOCK_RE.search(content):
        return True
    if len(content) < 200:
        return True
    return False


def clean_html(html_str: str) -> str:
    """Strip HTML tags from RSS summary content."""
    text = re.sub(r"<[^>]+>", " ", html_str)
    text = re.sub(r"&\w+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def init_db(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title_hash   TEXT    UNIQUE NOT NULL,
            title        TEXT    NOT NULL,
            url          TEXT    NOT NULL,
            domain       TEXT    NOT NULL DEFAULT 'unknown',
            source       TEXT    NOT NULL DEFAULT 'unknown',
            publish_at   TEXT    NOT NULL,
            article_path TEXT,
            fetched_at   TEXT    NOT NULL,
            crawled_at   TEXT    NOT NULL DEFAULT '',
            status       TEXT    NOT NULL DEFAULT 'pending',
            retry_count  INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.execute("CREATE INDEX IF NOT EXISTS idx_title_hash ON articles(title_hash)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON articles(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fetched ON articles(fetched_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_publish ON articles(publish_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_domain ON articles(domain)")

    # Add ticker column if missing (for ticker-specific news)
    try:
        conn.execute("SELECT ticker FROM articles LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE articles ADD COLUMN ticker TEXT DEFAULT NULL")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_ticker ON articles(ticker)")
        conn.commit()
    conn.commit()
    return conn


def title_exists(conn: sqlite3.Connection, title: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM articles WHERE title_hash = ?", (title_hash(title),)
    ).fetchone() is not None


def insert_headline(conn: sqlite3.Connection, item: dict, ticker: str | None = None):
    ts = now_seattle()
    domain = item.get("domain") or extract_domain(item["url"])
    source = item.get("source") or domain
    title_lower = item["title"].strip().lower()

    conn.execute(
        """INSERT OR IGNORE INTO articles
           (title_hash, title, url, domain, source, publish_at, fetched_at,
            status, retry_count, crawled_at, ticker)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', 0, '', ?)""",
        (
            title_hash(item["title"]),
            title_lower,
            item["url"],
            domain,
            source,
            ts,
            ts,
            ticker,
        ),
    )


def insert_rss_article(conn: sqlite3.Connection, title: str, url: str,
                        domain: str, summary: str, articles_dir: str,
                        ticker: str | None = None) -> bool:
    """Insert an RSS article directly as done (with summary content on disk).
    Returns True if new article was inserted."""
    if title_exists(conn, title):
        return False

    ts = now_seattle()
    title_lower = title.strip().lower()
    thash = title_hash(title)

    # Save summary to disk
    filename = save_article(articles_dir, title_lower, url, domain, ts,
                            f"*[RSS summary — full article behind paywall]*\n\n{summary}",
                            ticker=ticker)

    conn.execute(
        """INSERT OR IGNORE INTO articles
           (title_hash, title, url, domain, source, publish_at, fetched_at,
            status, retry_count, crawled_at, article_path, ticker)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'done', 0, ?, ?, ?)""",
        (thash, title_lower, url, domain, domain, ts, ts, ts, filename, ticker),
    )
    return True


def get_pending(conn: sqlite3.Connection, limit: int = BATCH_SIZE) -> list[dict]:
    rows = conn.execute(
        """SELECT title_hash, title, url, domain, retry_count, fetched_at, publish_at, ticker
           FROM articles
           WHERE status = 'pending' AND retry_count < ?
           ORDER BY CASE WHEN ticker IS NOT NULL THEN 0 ELSE 1 END,
                    fetched_at ASC
           LIMIT ?""",
        (MAX_RETRIES, limit),
    ).fetchall()
    return [
        {"title_hash": r[0], "title": r[1], "url": r[2], "domain": r[3],
         "retry_count": r[4], "fetched_at": r[5], "publish_at": r[6], "ticker": r[7]}
        for r in rows
    ]


def mark_done(conn: sqlite3.Connection, thash: str, article_path: str):
    conn.execute(
        "UPDATE articles SET status='done', crawled_at=?, article_path=? WHERE title_hash=?",
        (now_seattle(), article_path, thash),
    )
    conn.commit()


def mark_retry(conn: sqlite3.Connection, thash: str):
    conn.execute(
        """UPDATE articles SET retry_count = retry_count + 1,
           status = CASE WHEN retry_count >= ? THEN 'failed' ELSE 'pending' END
           WHERE title_hash = ?""",
        (MAX_RETRIES - 1, thash),
    )
    conn.commit()


def db_stats(conn: sqlite3.Connection) -> dict:
    r = {}
    for status in ("done", "pending", "failed"):
        r[status] = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE status=?", (status,)
        ).fetchone()[0]
    r["total"] = sum(r.values())
    return r


def expire_old_articles(conn: sqlite3.Connection, articles_dir: str,
                        days: int = EXPIRY_DAYS) -> dict:
    """Delete DB rows and .md files older than `days` days. Returns counts."""
    cutoff = (datetime.now(LOCAL_TZ) - timedelta(days=days)).isoformat()
    stats = {"db_deleted": 0, "files_deleted": 0, "file_errors": 0}

    # Get article_path for files to delete
    rows = conn.execute(
        "SELECT article_path FROM articles WHERE publish_at < ? AND article_path IS NOT NULL",
        (cutoff,),
    ).fetchall()

    for (filename,) in rows:
        filepath = os.path.join(articles_dir, filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                stats["files_deleted"] += 1
                # Clean empty subfolder
                parent = os.path.dirname(filepath)
                if parent != articles_dir and os.path.isdir(parent) and not os.listdir(parent):
                    os.rmdir(parent)
        except Exception as e:
            stats["file_errors"] += 1
            log.warning("  Expiry: failed to delete %s: %s", filename, e)

    # Delete all old rows (including those without article_path)
    cursor = conn.execute("DELETE FROM articles WHERE publish_at < ?", (cutoff,))
    stats["db_deleted"] = cursor.rowcount
    conn.commit()

    return stats


# ---------------------------------------------------------------------------
# Article file storage
# ---------------------------------------------------------------------------
def save_article(articles_dir: str, title: str, url: str, domain: str,
                 publish_at: str, content: str, ticker: str | None = None) -> str:
    """Save article as .md file in ticker subfolder. Returns relative path (ticker/filename)."""
    subfolder = (ticker or "market").lower()
    target_dir = os.path.join(articles_dir, subfolder)
    Path(target_dir).mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(title) + ".md"
    filepath = os.path.join(target_dir, filename)

    if os.path.exists(filepath):
        with open(filepath, "r", errors="replace") as f:
            first_line = f.readline()
        if title.lower() not in first_line.lower():
            filename = f"{sanitize_filename(title)}_{title_hash(title)[:8]}.md"
            filepath = os.path.join(target_dir, filename)

    with open(filepath, "w") as f:
        f.write(f"# {title}\n\n")
        f.write(f"- **URL:** {url}\n")
        f.write(f"- **Source:** {domain}\n")
        f.write(f"- **Published:** {publish_at}\n")
        f.write(f"- **Crawled:** {now_seattle()}\n\n")
        f.write("---\n\n")
        f.write(content)

    return f"{subfolder}/{filename}"


# ---------------------------------------------------------------------------
# RSS feed fetcher — for paywalled domains
# ---------------------------------------------------------------------------
def fetch_rss_articles(conn: sqlite3.Connection, articles_dir: str) -> dict:
    """Fetch RSS feeds for paywalled domains. Insert new articles directly as done."""
    stats = {"new": 0, "skipped": 0, "errors": 0}

    for domain, feeds in RSS_FEEDS.items():
        for feed_url in feeds:
            try:
                d = feedparser.parse(feed_url)
                if not d.entries:
                    log.warning("  RSS empty: %s", feed_url)
                    continue

                for entry in d.entries:
                    title = entry.get("title", "").strip()
                    url = entry.get("link", "")
                    summary = clean_html(entry.get("summary", ""))

                    if not title or len(title) < 10 or not summary:
                        continue

                    if insert_rss_article(conn, title, url, domain, summary, articles_dir):
                        stats["new"] += 1
                        log.info("  📡 RSS [%s]: \"%s\"", domain, title[:70])
                    else:
                        stats["skipped"] += 1

            except Exception as e:
                stats["errors"] += 1
                log.error("  RSS error (%s): %s", feed_url, str(e)[:100])

    conn.commit()
    return stats


# ---------------------------------------------------------------------------
# Finviz headline parsing
# ---------------------------------------------------------------------------
def parse_finviz_headlines(html: str) -> list[dict]:
    items = []
    seen_titles = set()

    pattern = re.compile(
        r'(\d{1,2}:\d{2}(?:AM|PM)).*?'
        r'<a[^>]+href="([^"]+)"[^>]*class="[^"]*nn-tab-link[^"]*"[^>]*>\s*(.+?)\s*</a>',
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(html):
        time_str, url, raw_title = m.group(1), m.group(2), m.group(3)
        title = re.sub(r"<[^>]+>", "", raw_title).strip()
        domain = extract_domain(url)
        norm = title.lower().strip()
        if not title or len(title) < 10 or norm in seen_titles or domain in AD_DOMAINS:
            continue
        seen_titles.add(norm)
        items.append({"time": time_str, "title": title, "url": url,
                       "source": domain, "domain": domain})

    # Fallback pattern
    if not items:
        pattern2 = re.compile(
            r'(\d{1,2}:\d{2}(?:AM|PM)).*?'
            r'<a[^>]+href="(https?://[^"]+)"[^>]*>\s*(.+?)\s*</a>',
            re.DOTALL | re.IGNORECASE,
        )
        for m in pattern2.finditer(html):
            time_str, url, raw_title = m.group(1), m.group(2), m.group(3)
            title = re.sub(r"<[^>]+>", "", raw_title).strip()
            domain = extract_domain(url)
            norm = title.lower().strip()
            if (not title or len(title) < 10 or norm in seen_titles
                    or "finviz.com" in url or domain in AD_DOMAINS):
                continue
            seen_titles.add(norm)
            items.append({"time": time_str, "title": title, "url": url,
                           "source": domain, "domain": domain})

    return items


# ---------------------------------------------------------------------------
# Ticker-specific headline parsing (from finviz.com/quote.ashx?t=TICKER)
# ---------------------------------------------------------------------------
def parse_ticker_headlines(html: str) -> list[dict]:
    """Parse news headlines from a finviz ticker quote page (news-table)."""
    items = []
    seen_titles = set()

    # Pattern matches the news-table structure:
    # <td>Feb-21-26 10:28PM</td> or <td>06:01PM</td>
    # <a class="tab-link-news" href="...">title</a>
    pattern = re.compile(
        r'<td[^>]*>\s*((?:[A-Z][a-z]{2}-\d{2}-\d{2}\s+)?\d{1,2}:\d{2}(?:AM|PM))\s*</td>'
        r'.*?<a\s+class="tab-link-news"\s+href="([^"]+)"[^>]*>([^<]+)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    for m in pattern.finditer(html):
        time_str, url, title = m.group(1).strip(), m.group(2), m.group(3).strip()
        domain = extract_domain(url)
        norm = title.lower().strip()
        if not title or len(title) < 10 or norm in seen_titles or domain in AD_DOMAINS:
            continue
        seen_titles.add(norm)
        items.append({"time": time_str, "title": title, "url": url,
                       "source": domain, "domain": domain})

    return items


async def crawl_ticker_headlines(crawler: AsyncWebCrawler, ticker: str,
                                  conn: sqlite3.Connection, ua_idx: int) -> int:
    """Scrape news headlines for a specific ticker from finviz quote page."""
    url = FINVIZ_QUOTE_URL.format(ticker=ticker)
    ua = USER_AGENTS[ua_idx % len(USER_AGENTS)]
    config = CrawlerRunConfig(
        page_timeout=30000,
        wait_until="domcontentloaded",
        delay_before_return_html=2,
        user_agent=ua,
        exclude_all_images=True,
        verbose=False,
    )
    try:
        result = await crawler.arun(url=url, config=config)
        if not result.success or not result.html:
            log.warning("Ticker %s fetch failed: %s", ticker, result.error_message or "unknown")
            return 0

        headlines = parse_ticker_headlines(result.html)
        new_count = 0
        for item in headlines:
            if not title_exists(conn, item["title"]):
                insert_headline(conn, item, ticker=ticker)
                new_count += 1
                log.info("  NEW [%s]: \"%s\" (%s)", ticker, item["title"][:70], item["source"])
        conn.commit()
        log.info("Ticker %s: %d new / %d total headlines", ticker, new_count, len(headlines))
        return new_count
    except Exception as e:
        log.error("Ticker %s error: %s", ticker, str(e)[:100])
        return 0


# ---------------------------------------------------------------------------
# Crawl4AI article fetcher — skips RSS domains
# ---------------------------------------------------------------------------
async def crawl_articles(crawler: AsyncWebCrawler, articles: list[dict],
                         conn: sqlite3.Connection, articles_dir: str,
                         ua_idx: int) -> dict:
    stats = {"crawled": 0, "failed": 0, "skipped_rss": 0}
    if not articles:
        return stats

    # Interleave across domains for politeness
    by_domain: dict[str, list[dict]] = {}
    for a in articles:
        by_domain.setdefault(a["domain"], []).append(a)
    interleaved: list[dict] = []
    domain_lists = list(by_domain.values())
    max_len = max(len(v) for v in domain_lists) if domain_lists else 0
    for i in range(max_len):
        for dl in domain_lists:
            if i < len(dl):
                interleaved.append(dl[i])

    for idx, article in enumerate(interleaved):
        if shutdown_event.is_set():
            log.info("Shutdown requested — stopping article crawl")
            break

        url = article["url"]
        title = article["title"]
        domain = article["domain"]
        retries = article["retry_count"]
        publish = article["publish_at"]
        thash = article["title_hash"]
        ticker = article.get("ticker")

        # Skip RSS domains — they're handled by fetch_rss_articles
        if domain in RSS_DOMAINS:
            # Mark as failed so they don't stay pending forever
            # (RSS may or may not have this specific article)
            mark_retry(conn, thash)
            stats["skipped_rss"] += 1
            continue

        ua = USER_AGENTS[(ua_idx + idx) % len(USER_AGENTS)]

        log.info("[%d/%d] Crawling: \"%s\"", idx + 1, len(interleaved), title[:80])
        log.info("  URL: %s", url[:120])
        log.info("  Domain: %s | Retry: %d/%d | Published: %s",
                 domain, retries, MAX_RETRIES, publish[:19])

        try:
            config = CrawlerRunConfig(
                only_text=True,
                check_robots_txt=True,
                page_timeout=20000,
                wait_until="domcontentloaded",
                user_agent=ua,
                exclude_all_images=True,
                exclude_external_links=True,
                remove_overlay_elements=True,
                verbose=False,
            )
            t0 = time.monotonic()
            result = await crawler.arun(url=url, config=config)
            elapsed = time.monotonic() - t0

            content = None
            if result.success and result.markdown:
                md = result.markdown
                content = md.raw_markdown if hasattr(md, "raw_markdown") else str(md)
            elif result.success and result.html:
                text = re.sub(r"<script[^>]*>.*?</script>", "", result.html,
                              flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<style[^>]*>.*?</style>", "", text,
                              flags=re.DOTALL | re.IGNORECASE)
                text = re.sub(r"<[^>]+>", " ", text)
                text = re.sub(r"\s+", " ", text).strip()
                if len(text) > 200:
                    content = text

            if content and not is_bot_blocked(content) and len(content) > 200:
                filename = save_article(articles_dir, title, url, domain, publish, content, ticker=ticker)
                mark_done(conn, thash, filename)
                stats["crawled"] += 1
                log.info("  ✓ Done in %.1fs — %d chars → %s", elapsed, len(content), filename)
            else:
                mark_retry(conn, thash)
                stats["failed"] += 1
                reason = "bot-blocked" if (content and is_bot_blocked(content)) else "no content"
                log.warning("  ✗ Failed in %.1fs — %s (%d chars)", elapsed, reason,
                            len(content) if content else 0)

        except Exception as e:
            mark_retry(conn, thash)
            stats["failed"] += 1
            log.error("  ✗ Exception: %s", str(e)[:150])

        # Per-domain rate limit
        await interruptible_sleep(DOMAIN_DELAY)

    return stats


# ---------------------------------------------------------------------------
# Async helpers
# ---------------------------------------------------------------------------
async def interruptible_sleep(seconds: float):
    try:
        await asyncio.wait_for(shutdown_event.wait(), timeout=seconds)
    except asyncio.TimeoutError:
        pass


async def crawl_headlines(crawler: AsyncWebCrawler, ua_idx: int) -> list[dict]:
    ua = USER_AGENTS[ua_idx % len(USER_AGENTS)]
    config = CrawlerRunConfig(
        page_timeout=30000,
        wait_until="domcontentloaded",
        delay_before_return_html=2,
        user_agent=ua,
        exclude_all_images=True,
        verbose=False,
    )
    result = await crawler.arun(url=FINVIZ_NEWS_URL, config=config)
    if result.success and result.html:
        return parse_finviz_headlines(result.html)
    log.warning("Headline fetch failed: %s", result.error_message or "unknown")
    return []


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
async def run_daemon(args):
    conn = init_db(args.db)
    articles_dir = args.articles_dir
    Path(articles_dir).mkdir(parents=True, exist_ok=True)
    ua_idx = 0
    cycle = 0

    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium",
        text_mode=True,
        light_mode=True,
        verbose=False,
        extra_args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"],
    )

    log.info("Starting Crawl4AI browser...")
    async with AsyncWebCrawler(config=browser_config) as crawler:
        log.info("Browser ready. Entering main loop.")

        while not shutdown_event.is_set():
            cycle += 1
            t0 = time.monotonic()
            log.info("=== Cycle %d ===", cycle)

            # 1. Fetch finviz headlines
            try:
                headlines = await crawl_headlines(crawler, ua_idx)
                ua_idx += 1
                log.info("Parsed %d finviz headlines", len(headlines))
            except Exception as e:
                log.error("Headline fetch error: %s", e)
                headlines = []

            if shutdown_event.is_set():
                break

            # 2. Insert new headlines
            new_count = 0
            for item in headlines:
                if not title_exists(conn, item["title"]):
                    insert_headline(conn, item)
                    new_count += 1
                    log.info("  NEW: [%s] \"%s\" (%s)",
                             item["time"], item["title"][:70], item["source"])
            conn.commit()
            log.info("New finviz: %d / %d total", new_count, len(headlines))

            if shutdown_event.is_set():
                break

            # 3. Fetch RSS feeds (Bloomberg, MarketWatch)
            log.info("Fetching RSS feeds...")
            rss_stats = fetch_rss_articles(conn, articles_dir)
            log.info("RSS: new=%d skipped=%d errors=%d",
                     rss_stats["new"], rss_stats["skipped"], rss_stats["errors"])

            if shutdown_event.is_set():
                break

            # 3b. Crawl ticker-specific headlines
            tickers = _load_tickers()
            if tickers:
                log.info("Scraping ticker news for: %s", ", ".join(tickers))
                for ticker in tickers:
                    if shutdown_event.is_set():
                        break
                    await crawl_ticker_headlines(crawler, ticker, conn, ua_idx)
                    ua_idx += 1
                    await interruptible_sleep(2)  # Be polite between ticker pages

            if shutdown_event.is_set():
                break

            # 4. Crawl pending articles (non-RSS domains only)
            pending = get_pending(conn, limit=BATCH_SIZE)
            stats_before = db_stats(conn)
            log.info("Pending: %d (batch: %d) | DB: %s",
                     stats_before["pending"], len(pending), stats_before)

            if pending and not shutdown_event.is_set():
                cstats = await crawl_articles(
                    crawler, pending, conn, articles_dir, ua_idx
                )
                ua_idx += cstats["crawled"] + cstats["failed"]
                log.info("Crawl: done=%d failed=%d skipped_rss=%d",
                         cstats["crawled"], cstats["failed"], cstats["skipped_rss"])

            # 5. Expire old articles (configurable, 0=disabled)
            _expiry = getattr(args, 'expiry_days', EXPIRY_DAYS)
            if _expiry > 0:
                exp = expire_old_articles(conn, articles_dir, days=_expiry)
                if exp["db_deleted"]:
                    log.info("Expiry: %d rows deleted, %d files removed (>%dd old)",
                             exp["db_deleted"], exp["files_deleted"], _expiry)

            elapsed = time.monotonic() - t0
            final = db_stats(conn)
            article_count = len(list(Path(articles_dir).rglob("*.md")))
            log.info("Cycle %d done in %.1fs | DB: %s | Articles on disk: %d",
                     cycle, elapsed, final, article_count)

            # 6. Sleep
            if not shutdown_event.is_set():
                log.info("Sleeping %ds...", args.sleep)
                await interruptible_sleep(args.sleep)

    conn.close()
    log.info("finviz-crawler exiting cleanly")


def main():
    parser = argparse.ArgumentParser(description="Finviz crawler v3.2 (Crawl4AI + RSS)")
    parser.add_argument("--db", default=DEFAULT_DB, help="SQLite database path")
    parser.add_argument("--articles-dir", default=DEFAULT_ARTICLES_DIR, help="Directory for .md article files")
    parser.add_argument("--sleep", type=int, default=DEFAULT_SLEEP, help="Seconds between crawl cycles (default: 300)")
    parser.add_argument("--expiry-days", type=int, default=EXPIRY_DAYS, help="Auto-delete articles older than N days (default: 7, 0=never)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # Override module-level expiry from CLI
    global EXPIRY_DAYS
    EXPIRY_DAYS = args.expiry_days

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    log.info("finviz-crawler v3.2 starting (db=%s, articles=%s, sleep=%ds)",
             args.db, args.articles_dir, args.sleep)

    asyncio.run(run_daemon(args))


if __name__ == "__main__":
    main()
