#!/usr/bin/env python3
"""
Link Brain v4.0.0 - Personal knowledge base for saved links.

This is a local-only CLI tool that stores URLs with summaries and tags in a
SQLite database at ~/.link-brain/brain.db. All data stays local.

v4.0.0 adds auto-save mode, which uses urllib to fetch URL content for local
summarization and tagging. This is the only network call in the script, and
it only happens when you explicitly use --auto or auto-save. No telemetry,
no external APIs, no LLMs. Pure algorithmic text processing.

What it does:
  - Saves URLs with titles, summaries, and tags to a local SQLite database
  - Auto-save mode: fetches page content and auto-generates title, tags, summary
  - Full-text search using SQLite FTS5, with natural language query parsing
  - Knowledge graph visualization (interactive HTML)
  - Collections / reading lists with markdown and HTML export
  - Spaced repetition review system
  - Imports bookmarks from browsers (Chrome, Safari, Firefox)
  - Imports exports from YouTube, Reddit, Pocket, Instapaper, Raindrop.io, Hacker News
  - Tracks read status, ratings, streaks, and milestones
  - Generates digests, insights, recommendations, and weekly summaries
  - Suggests tags based on your collection patterns

All data stays in ~/.link-brain/. No subprocess calls. No eval/exec.
No writing outside the data directory. The only network call is in auto-save
mode (urllib) to fetch page content for local summarization.

Commands:
  setup        Create data directory and show welcome message
  save         Save a URL with title, summary, and tags (--auto for autonomous mode)
  auto-save    Autonomous save: fetch, summarize, tag, and save a URL (no LLM needed)
  search       Search saved links (supports natural language queries)
  graph        Generate interactive knowledge graph visualization
  collection   Manage collections / reading lists
  review       Spaced repetition review system
  recent       Show recently saved links
  tags         List all tags or filter by tag
  get          Full details for a saved link
  delete       Delete a saved link by ID
  related      Find links related to a given link by shared tags
  suggest-tags Suggest tags for a URL based on your collection
  digest       Generate a digest of links to review
  recommend    Recommend links based on your top tags
  gems         Surface your highest-rated links
  random       Pull random unread links from your backlog
  read         Mark a link as read
  unread       Show unread links
  rate         Rate a link (1-5)
  streak       Show your current streak and activity stats
  insights     Reading personality and collection analytics
  weekly       Weekly summary formatted for WhatsApp
  scan         Scan bookmarks from browsers or services
  sync         Compare source bookmarks against DB, flag removals
  sources      Show connected sources and sync status
  import       Import from bookmark export files (HTML, JSON, CSV, platform exports)
  stats        Show collection stats
  export       Export all links as JSON
  help         Show help organized by use case
"""

VERSION = "4.3.0"

WHATS_NEW = "Quickstart: auto-detects browser bookmarks and imports them in one shot. Zero-config first run."

import argparse
import csv
import hashlib
import html.parser
import json
import math
import os
import plistlib
import random
import re
import shutil
import sqlite3
import string
import sys
import tempfile
import webbrowser
from collections import Counter
from datetime import datetime, timezone, timedelta
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

DB_DIR = Path(os.environ.get("LINK_BRAIN_DIR", Path.home() / ".link-brain"))
DB_PATH = DB_DIR / "brain.db"
CONFIG_PATH = DB_DIR / "config.json"

# --- Color helpers ---
USE_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code, text):
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _bold(text): return _c("1", text)
def _dim(text): return _c("2", text)
def _green(text): return _c("32", text)
def _yellow(text): return _c("33", text)
def _cyan(text): return _c("36", text)
def _red(text): return _c("31", text)
def _magenta(text): return _c("35", text)


def load_config():
    defaults = {"digest_count": 5, "digest_mode": "shuffle"}
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                user = json.load(f)
            defaults.update(user)
        except Exception:
            pass
    return defaults


def get_db():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA foreign_keys=ON")

    db.executescript("""
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '',
            source_type TEXT NOT NULL DEFAULT 'article',
            saved_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS link_tags (
            link_id INTEGER NOT NULL REFERENCES links(id) ON DELETE CASCADE,
            tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
            PRIMARY KEY (link_id, tag_id)
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS links_fts USING fts5(
            title, summary, tags, url,
            content='links',
            content_rowid='id'
        );

        CREATE TRIGGER IF NOT EXISTS links_ai AFTER INSERT ON links BEGIN
            INSERT INTO links_fts(rowid, title, summary, tags, url)
            VALUES (new.id, new.title, new.summary, new.tags, new.url);
        END;

        CREATE TRIGGER IF NOT EXISTS links_ad AFTER DELETE ON links BEGIN
            INSERT INTO links_fts(links_fts, rowid, title, summary, tags, url)
            VALUES ('delete', old.id, old.title, old.summary, old.tags, old.url);
        END;

        CREATE TRIGGER IF NOT EXISTS links_au AFTER UPDATE ON links BEGIN
            INSERT INTO links_fts(links_fts, rowid, title, summary, tags, url)
            VALUES ('delete', old.id, old.title, old.summary, old.tags, old.url);
            INSERT INTO links_fts(rowid, title, summary, tags, url)
            VALUES (new.id, new.title, new.summary, new.tags, new.url);
        END;

        CREATE TABLE IF NOT EXISTS sources (
            name TEXT PRIMARY KEY,
            path TEXT,
            last_synced_at TEXT,
            last_bookmark_count INTEGER DEFAULT 0,
            config TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS streaks (
            date TEXT PRIMARY KEY,
            saves_count INTEGER DEFAULT 0,
            reads_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS collection_links (
            collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
            link_id INTEGER NOT NULL REFERENCES links(id) ON DELETE CASCADE,
            added_at TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            PRIMARY KEY (collection_id, link_id)
        );

        CREATE TABLE IF NOT EXISTS reviews (
            link_id INTEGER PRIMARY KEY REFERENCES links(id) ON DELETE CASCADE,
            next_review_at TEXT NOT NULL,
            interval_days INTEGER NOT NULL DEFAULT 1,
            review_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            last_reviewed_at TEXT
        );
    """)

    _migrate(db)
    return db


def _migrate(db):
    cols = {r[1] for r in db.execute("PRAGMA table_info(links)").fetchall()}

    migrations = [
        ("rating",              "ALTER TABLE links ADD COLUMN rating INTEGER"),
        ("is_read",             "ALTER TABLE links ADD COLUMN is_read BOOLEAN DEFAULT 0"),
        ("last_digested_at",    "ALTER TABLE links ADD COLUMN last_digested_at TEXT"),
        ("source",              "ALTER TABLE links ADD COLUMN source TEXT DEFAULT 'manual'"),
        ("source_id",           "ALTER TABLE links ADD COLUMN source_id TEXT"),
        ("removed_from_source", "ALTER TABLE links ADD COLUMN removed_from_source BOOLEAN DEFAULT 0"),
    ]

    needs_rebuild = False
    for col_name, alter_sql in migrations:
        if col_name not in cols:
            db.execute(alter_sql)
            needs_rebuild = True

    if needs_rebuild:
        db.execute("INSERT INTO links_fts(links_fts) VALUES('rebuild')")

    # Ensure tables exist for upgrades
    db.execute("""
        CREATE TABLE IF NOT EXISTS streaks (
            date TEXT PRIMARY KEY,
            saves_count INTEGER DEFAULT 0,
            reads_count INTEGER DEFAULT 0
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS collection_links (
            collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
            link_id INTEGER NOT NULL REFERENCES links(id) ON DELETE CASCADE,
            added_at TEXT NOT NULL,
            position INTEGER DEFAULT 0,
            PRIMARY KEY (collection_id, link_id)
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            link_id INTEGER PRIMARY KEY REFERENCES links(id) ON DELETE CASCADE,
            next_review_at TEXT NOT NULL,
            interval_days INTEGER NOT NULL DEFAULT 1,
            review_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            last_reviewed_at TEXT
        )
    """)

    # Meta table for version tracking
    db.execute("""
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    db.commit()


def _check_whats_new(db):
    """Show what's new message once after upgrade. Returns True if shown."""
    row = db.execute("SELECT value FROM meta WHERE key = 'last_seen_version'").fetchone()
    last_seen = row["value"] if row else None
    if last_seen == VERSION:
        return False
    db.execute(
        "INSERT INTO meta (key, value) VALUES ('last_seen_version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = ?",
        (VERSION, VERSION)
    )
    db.commit()
    if last_seen is not None:  # Only show on upgrade, not first install
        print()
        print(f"🆕 Link Brain v{VERSION} — What's new:")
        print(f"   {WHATS_NEW}")
        print(f"   Run: brain.py help for details")
        print()
    return last_seen is not None


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def normalize_url(url):
    url = url.strip()
    if not url:
        return url
    p = urlparse(url)
    host = (p.hostname or "").lower()
    path = p.path.rstrip("/") or "/"
    normalized = f"{p.scheme}://{host}"
    if p.port and p.port not in (80, 443):
        normalized += f":{p.port}"
    normalized += path
    if p.query:
        normalized += f"?{p.query}"
    return normalized


def make_source_id(source_name, url):
    key = f"{source_name}:{normalize_url(url)}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def url_exists(db, url):
    norm = normalize_url(url)
    row = db.execute("SELECT id FROM links WHERE url = ? LIMIT 1", (url,)).fetchone()
    if row:
        return row["id"]
    row = db.execute("SELECT id FROM links WHERE url = ? LIMIT 1", (norm,)).fetchone()
    if row:
        return row["id"]
    rows = db.execute("SELECT id, url FROM links").fetchall()
    for r in rows:
        if normalize_url(r["url"]) == norm:
            return r["id"]
    return None


def detect_source_type(url):
    url_lower = url.lower()
    if any(x in url_lower for x in ["youtube.com", "youtu.be", "vimeo.com"]):
        return "video"
    elif any(x in url_lower for x in ["podcasts.apple", "spotify.com/episode", "overcast.fm"]):
        return "podcast"
    elif url_lower.endswith(".pdf"):
        return "pdf"
    elif any(x in url_lower for x in ["twitter.com", "x.com", "threads.net", "mastodon"]):
        return "social"
    elif any(x in url_lower for x in ["github.com", "gitlab.com"]):
        return "repo"
    return "article"


def ensure_tags(db, tag_names):
    tag_ids = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        db.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
        row = db.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
        if row:
            tag_ids.append(row["id"])
    return tag_ids


def _ensure_review_entry(db, link_id):
    """Add a link to the review queue if not already there."""
    existing = db.execute("SELECT link_id FROM reviews WHERE link_id = ?", (link_id,)).fetchone()
    if not existing:
        now = now_iso()
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        db.execute(
            "INSERT INTO reviews (link_id, next_review_at, interval_days, review_count, created_at) VALUES (?, ?, 1, 0, ?)",
            (link_id, tomorrow, now)
        )


# --- Streak & milestone tracking ---

def track_activity(db, activity_type):
    today = today_str()
    if activity_type == "save":
        db.execute(
            """INSERT INTO streaks (date, saves_count, reads_count)
               VALUES (?, 1, 0)
               ON CONFLICT(date) DO UPDATE SET saves_count = saves_count + 1""",
            (today,)
        )
    elif activity_type == "read":
        db.execute(
            """INSERT INTO streaks (date, saves_count, reads_count)
               VALUES (?, 0, 1)
               ON CONFLICT(date) DO UPDATE SET reads_count = reads_count + 1""",
            (today,)
        )
    db.commit()

    messages = []
    if activity_type == "save":
        total_saves = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
        for milestone in [500, 100, 50, 10]:
            if total_saves == milestone:
                messages.append(f"🎯 {milestone} links saved!")
                break

    streak_days = _calculate_streak(db)
    for milestone in [30, 7, 3]:
        if streak_days == milestone:
            messages.append(f"🔥 {milestone}-day streak!")
            break

    return messages


def _calculate_streak(db):
    rows = db.execute(
        "SELECT date FROM streaks WHERE saves_count > 0 OR reads_count > 0 ORDER BY date DESC"
    ).fetchall()
    if not rows:
        return 0
    dates = [datetime.strptime(r["date"], "%Y-%m-%d").date() for r in rows]
    today = datetime.now(timezone.utc).date()
    if dates[0] < today - timedelta(days=1):
        return 0
    streak = 1
    for i in range(1, len(dates)):
        if dates[i - 1] - dates[i] == timedelta(days=1):
            streak += 1
        else:
            break
    return streak


def _get_domain(url):
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def _suggest_tags_for_url(db, url):
    domain = _get_domain(url).lower()
    if not domain:
        return []
    rows = db.execute("SELECT tags FROM links WHERE url LIKE ?", (f"%{domain}%",)).fetchall()
    if not rows:
        return []
    tag_counts = {}
    for row in rows:
        if row["tags"]:
            for t in row["tags"].split(","):
                t = t.strip().lower()
                if t:
                    tag_counts[t] = tag_counts.get(t, 0) + 1
    sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
    return [t for t, _ in sorted_tags[:5]]


def bulk_insert_links(db, bookmarks, source_name):
    now = now_iso()
    imported = 0
    skipped = 0
    imported_ids = []

    for bm in bookmarks:
        url = bm.get("url", "").strip()
        if not url or not url.startswith(("http://", "https://")):
            skipped += 1
            continue
        if url_exists(db, url):
            skipped += 1
            continue

        title = bm.get("title", "").strip() or url
        tags_list = bm.get("tags", [])
        if isinstance(tags_list, str):
            tags_list = [t.strip().lower() for t in tags_list.split(",") if t.strip()]
        tags_str = ", ".join(tags_list)
        summary = bm.get("summary", "")
        source_type = detect_source_type(url)
        sid = make_source_id(source_name, url)

        cursor = db.execute(
            """INSERT INTO links (url, title, summary, tags, source_type, saved_at, updated_at, source, source_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (url, title, summary, tags_str, source_type, now, now, source_name, sid)
        )
        link_id = cursor.lastrowid
        imported_ids.append(link_id)

        # Add to review queue
        _ensure_review_entry(db, link_id)

        tag_ids = ensure_tags(db, tags_list)
        for tid in tag_ids:
            db.execute("INSERT OR IGNORE INTO link_tags (link_id, tag_id) VALUES (?, ?)",
                       (link_id, tid))
        imported += 1

    db.commit()

    total_in_source = db.execute(
        "SELECT COUNT(*) as n FROM links WHERE source = ?", (source_name,)
    ).fetchone()["n"]
    db.execute(
        """INSERT INTO sources (name, last_synced_at, last_bookmark_count)
           VALUES (?, ?, ?)
           ON CONFLICT(name) DO UPDATE SET last_synced_at = ?, last_bookmark_count = ?""",
        (source_name, now, total_in_source, now, total_in_source)
    )
    db.commit()

    return imported, skipped, imported_ids


def link_to_dict(row):
    d = dict(row)
    if d.get("tags"):
        d["tags"] = [t.strip() for t in d["tags"].split(",") if t.strip()]
    else:
        d["tags"] = []
    d.pop("rank", None)
    return d


# =====================================================================
# Feature 1: Auto-save (autonomous mode)
# =====================================================================

# Stop words for keyword extraction
_STOP_WORDS = set("""
a about above after again against all am an and any are aren't as at be because
been before being below between both but by can't cannot could couldn't did
didn't do does doesn't doing don't down during each few for from further get got
had hadn't has hasn't have haven't having he he'd he'll he's her here here's hers
herself him himself his how how's i i'd i'll i'm i've if in into is isn't it it's
its itself let's me more most mustn't my myself no nor not of off on once only or
other ought our ours ourselves out over own same shan't she she'd she'll she's
should shouldn't so some such than that that's the their theirs them themselves
then there there's these they they'd they'll they're they've this those through
to too under until up upon us very was wasn't we we'd we'll we're we've were
weren't what what's when when's where where's which while who who's whom why
why's will with won't would wouldn't you you'd you'll you're you've your yours
yourself yourselves also just like one two three even still many much will can may
new use used get got been would could should make made way well back even give
take come think know see look want say tell find going go made right big long
thing things people time year years day days really using good said first last
page site web article read post click home help need work best part found
next start end point link try data set list
great small large big high low old new full called makes become becomes became
making getting having doing going looking coming taking thinking knowing seeing
understanding using working building running based around without
really actually basically simply just also already however provides
important remarkable perfect ideal significant major core distinctive
requires requires features feature designed provides including includes
enforces constraints prevent manifest require designed
every often most another between where when while
""".split())


class SimpleHTMLTextExtractor(html.parser.HTMLParser):
    """Extract readable text from HTML. No external dependencies."""

    SKIP_TAGS = {'script', 'style', 'noscript', 'nav', 'footer', 'header', 'aside', 'svg', 'path'}

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.title = ""
        self._in_title = False
        self._title_parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        if tag == 'title':
            self._in_title = True
            self._title_parts = []
        if tag in ('p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'tr', 'blockquote'):
            self.text_parts.append('\n')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == 'title':
            self._in_title = False
            self.title = ''.join(self._title_parts).strip()

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data)
        if self._skip_depth == 0:
            self.text_parts.append(data)

    def get_text(self):
        raw = ''.join(self.text_parts)
        # Collapse whitespace
        lines = []
        for line in raw.split('\n'):
            cleaned = ' '.join(line.split())
            if cleaned:
                lines.append(cleaned)
        return '\n'.join(lines)


def _fetch_url_content(url):
    """
    Fetches the URL to read the page content for summarization.
    This is the only network call in the script. It uses Python's built-in
    urllib so there are no external dependencies. Only called in auto-save mode.
    """
    import urllib.request
    import urllib.error

    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; LinkBrain/4.0)',
            'Accept': 'text/html,application/xhtml+xml,text/plain',
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get('Content-Type', '')
            charset = 'utf-8'
            if 'charset=' in content_type:
                charset = content_type.split('charset=')[-1].split(';')[0].strip()
            raw = resp.read(500_000)  # Cap at 500KB
            return raw.decode(charset, errors='replace')
    except Exception as e:
        return None


def _extract_keywords(text, existing_tags=None, top_n=5):
    """Extract the most meaningful keywords from text using frequency analysis."""
    # Tokenize: only keep alphabetic words 3+ chars
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    # Filter stop words
    words = [w for w in words if w not in _STOP_WORDS and len(w) < 30]

    counts = Counter(words)

    # Boost words that match existing tags in the collection
    if existing_tags:
        existing_set = set(t.lower() for t in existing_tags)
        for word in counts:
            if word in existing_set:
                counts[word] *= 3

    # Deduplicate plurals: group "database"/"databases" together, keep whichever has higher count
    def _variants(word):
        """Return possible singular/plural variants for dedup grouping."""
        v = {word}
        if word.endswith('ies') and len(word) > 4:
            v.add(word[:-3] + 'y')
        if word.endswith('es') and len(word) > 3:
            v.add(word[:-2])
            v.add(word[:-1])
        if word.endswith('s') and len(word) > 3 and not word.endswith('ss'):
            v.add(word[:-1])
        # also generate plurals from singular
        v.add(word + 's')
        v.add(word + 'es')
        return v

    top = []
    seen = set()
    for w, _ in counts.most_common(top_n * 4):
        variants = _variants(w)
        if variants & seen:
            continue
        seen.update(variants)
        top.append(w)
        if len(top) >= top_n:
            break
    return top


def _extractive_summary(text, num_sentences=3):
    """Generate an extractive summary by picking the most important sentences.
    Uses position bias (early sentences matter more) and keyword density."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter out very short or very long sentences
    sentences = [s.strip() for s in sentences if 20 < len(s.strip()) < 500]

    if not sentences:
        # Fallback: just take the first chunk of text
        return text[:300].strip() if text else ""

    if len(sentences) <= num_sentences:
        return ' '.join(sentences)

    # Get keyword frequencies for scoring
    all_words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    all_words = [w for w in all_words if w not in _STOP_WORDS]
    word_freq = Counter(all_words)

    scored = []
    for i, sent in enumerate(sentences):
        words = re.findall(r'[a-zA-Z]{3,}', sent.lower())
        words = [w for w in words if w not in _STOP_WORDS]

        # Keyword density score
        if words:
            keyword_score = sum(word_freq.get(w, 0) for w in words) / len(words)
        else:
            keyword_score = 0

        # Position bias: first sentences get a boost
        position_score = 1.0 / (1 + i * 0.3)

        # Length preference: medium-length sentences preferred
        length_score = min(len(words) / 15.0, 1.0)

        total = keyword_score * position_score * length_score
        scored.append((total, i, sent))

    # Pick top sentences, maintain original order
    scored.sort(key=lambda x: -x[0])
    top = sorted(scored[:num_sentences], key=lambda x: x[1])

    return ' '.join(s for _, _, s in top)


def _auto_generate_metadata(url, html_content, db):
    """Auto-generate title, tags, summary, and source_type from HTML content."""
    extractor = SimpleHTMLTextExtractor()
    try:
        extractor.feed(html_content)
    except Exception:
        pass

    title = extractor.title or ""
    text = extractor.get_text()
    source_type = detect_source_type(url)

    # Strip the title from the body text so the summary doesn't repeat it
    if title:
        # Remove exact title matches and close variants (e.g. with site suffix stripped)
        for variant in [title, title.split(' - ')[0], title.split(' | ')[0]]:
            variant = variant.strip()
            if variant and text.startswith(variant):
                text = text[len(variant):].lstrip('\n ')

    # Get existing tags from collection for cross-referencing
    existing_tag_rows = db.execute("SELECT name FROM tags").fetchall()
    existing_tags = [r["name"] for r in existing_tag_rows]

    # Auto-generate tags
    tags = _extract_keywords(text, existing_tags, top_n=5)

    # Add domain-based tag suggestions
    domain_tags = _suggest_tags_for_url(db, url)
    for dt in domain_tags[:2]:
        if dt not in tags:
            tags.append(dt)

    # Cap at 5 tags
    tags = tags[:5]

    # Auto-generate summary
    summary = _extractive_summary(text, num_sentences=3)
    # Truncate if too long
    if len(summary) > 500:
        summary = summary[:497] + "..."

    # Clean up title
    if title:
        # Remove common suffixes like " - Site Name" or " | Brand"
        for sep in [' | ', ' - ', ' :: ', ' – ', ' — ']:
            if sep in title:
                parts = title.split(sep)
                if len(parts[-1]) < 30:
                    title = sep.join(parts[:-1])
                break

    if not title:
        title = url

    return title, tags, summary, source_type


def cmd_auto_save(args):
    """Autonomous save: fetch URL, extract content, generate metadata, save."""
    db = get_db()
    url = args.url

    # Check for duplicate
    existing_id = url_exists(db, url)
    if existing_id:
        link = db.execute("SELECT * FROM links WHERE id = ?", (existing_id,)).fetchone()
        print(json.dumps({"status": "duplicate", "existing_link": link_to_dict(link)}))
        return

    # Fetches URL content for local summarization. This is the only network call in the script.
    html_content = _fetch_url_content(url)
    if not html_content:
        print(json.dumps({"error": f"Could not fetch {url}. Try saving manually with brain.py save."}))
        return

    title, tags, summary, source_type = _auto_generate_metadata(url, html_content, db)

    now = now_iso()
    tags_str = ", ".join(tags)

    cursor = db.execute(
        """INSERT INTO links (url, title, summary, tags, source_type, saved_at, updated_at, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'manual')""",
        (url, title, summary, tags_str, source_type, now, now)
    )
    link_id = cursor.lastrowid

    tag_ids = ensure_tags(db, tags)
    for tid in tag_ids:
        db.execute("INSERT OR IGNORE INTO link_tags (link_id, tag_id) VALUES (?, ?)",
                   (link_id, tid))

    # Add to review queue
    _ensure_review_entry(db, link_id)

    db.commit()

    milestones = track_activity(db, "save")

    link = db.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
    result = {"status": "saved", "auto": True, "link": link_to_dict(link)}
    if milestones:
        result["milestones"] = milestones

    print(json.dumps(result, indent=2))


# =====================================================================
# Feature 2: Knowledge Graph Visualization
# =====================================================================

def cmd_graph(args):
    """Generate an interactive HTML knowledge graph visualization."""
    db = get_db()

    rows = db.execute("SELECT * FROM links ORDER BY saved_at DESC").fetchall()
    if not rows:
        print(json.dumps({"status": "empty", "message": "No links to visualize. Save some links first!"}))
        return

    links = [link_to_dict(r) for r in rows]

    # Build nodes and edges
    nodes = []
    tag_to_links = {}
    all_tags = set()

    for link in links:
        node = {
            "id": link["id"],
            "title": link["title"][:60],
            "url": link["url"],
            "summary": (link["summary"] or "")[:150],
            "tags": link["tags"],
            "rating": link.get("rating") or 0,
            "source_type": link.get("source_type", "article"),
        }
        nodes.append(node)
        for tag in link["tags"]:
            tag = tag.lower()
            all_tags.add(tag)
            if tag not in tag_to_links:
                tag_to_links[tag] = []
            tag_to_links[tag].append(link["id"])

    # Build edges: links that share tags
    edges = []
    edge_set = set()
    for tag, link_ids in tag_to_links.items():
        for i in range(len(link_ids)):
            for j in range(i + 1, min(len(link_ids), i + 10)):  # Cap connections per tag
                a, b = min(link_ids[i], link_ids[j]), max(link_ids[i], link_ids[j])
                if (a, b) not in edge_set:
                    edge_set.add((a, b))
                    edges.append({"source": a, "target": b})

    # Generate color palette for tags
    sorted_tags = sorted(all_tags)
    tag_colors = {}
    palette = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e67e22", "#e91e63", "#00bcd4", "#8bc34a",
        "#ff5722", "#607d8b", "#795548", "#cddc39", "#ff9800",
    ]
    for i, tag in enumerate(sorted_tags):
        tag_colors[tag] = palette[i % len(palette)]

    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)
    tag_colors_json = json.dumps(tag_colors)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Link Brain - Knowledge Graph</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0a0a0a; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; overflow: hidden; }}
canvas {{ display: block; cursor: grab; }}
canvas:active {{ cursor: grabbing; }}
#tooltip {{
    position: fixed; display: none; background: #1a1a2e; border: 1px solid #333;
    border-radius: 8px; padding: 12px 16px; max-width: 320px; pointer-events: none;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5); z-index: 100; font-size: 13px;
}}
#tooltip .tt-title {{ font-weight: 600; font-size: 14px; margin-bottom: 4px; color: #fff; }}
#tooltip .tt-summary {{ color: #aaa; font-size: 12px; line-height: 1.4; }}
#tooltip .tt-tags {{ margin-top: 6px; }}
#tooltip .tt-tag {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin: 2px; }}
#header {{
    position: fixed; top: 16px; left: 16px; z-index: 50;
    background: rgba(10,10,10,0.8); padding: 12px 16px; border-radius: 8px;
    backdrop-filter: blur(10px); border: 1px solid #222;
}}
#header h1 {{ font-size: 16px; margin-bottom: 4px; }}
#header p {{ font-size: 12px; color: #888; }}
#legend {{
    position: fixed; bottom: 16px; left: 16px; z-index: 50;
    background: rgba(10,10,10,0.8); padding: 12px 16px; border-radius: 8px;
    backdrop-filter: blur(10px); border: 1px solid #222; max-height: 300px;
    overflow-y: auto; font-size: 12px;
}}
#legend .tag-item {{ display: flex; align-items: center; margin: 3px 0; cursor: pointer; }}
#legend .tag-dot {{ width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; flex-shrink: 0; }}
</style>
</head>
<body>
<div id="header">
    <h1>🧠 Link Brain</h1>
    <p>{len(nodes)} links, {len(edges)} connections</p>
</div>
<div id="tooltip">
    <div class="tt-title"></div>
    <div class="tt-summary"></div>
    <div class="tt-tags"></div>
</div>
<div id="legend"></div>
<canvas id="graph"></canvas>
<script>
const nodes = {nodes_json};
const edges = {edges_json};
const tagColors = {tag_colors_json};

const canvas = document.getElementById('graph');
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');

let W, H;
function resize() {{
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
}}
resize();
window.addEventListener('resize', resize);

// Initialize positions
const idToIdx = {{}};
nodes.forEach((n, i) => {{
    idToIdx[n.id] = i;
    n.x = W/2 + (Math.random() - 0.5) * Math.min(W, H) * 0.6;
    n.y = H/2 + (Math.random() - 0.5) * Math.min(W, H) * 0.6;
    n.vx = 0;
    n.vy = 0;
    n.radius = Math.max(4, Math.min(12, 4 + (n.rating || 0) * 1.6));
    n.color = '#666';
    if (n.tags.length > 0) {{
        n.color = tagColors[n.tags[0].toLowerCase()] || '#666';
    }}
}});

// Build legend
const legend = document.getElementById('legend');
const tagCounts = {{}};
nodes.forEach(n => n.tags.forEach(t => {{ tagCounts[t] = (tagCounts[t]||0)+1; }}));
const sortedTags = Object.entries(tagCounts).sort((a,b) => b[1]-a[1]).slice(0, 20);
sortedTags.forEach(([tag, count]) => {{
    const el = document.createElement('div');
    el.className = 'tag-item';
    el.innerHTML = '<span class="tag-dot" style="background:' + (tagColors[tag]||'#666') + '"></span>' + tag + ' (' + count + ')';
    legend.appendChild(el);
}});

// Pan and zoom
let panX = 0, panY = 0, zoom = 1;
let dragging = false, dragNode = null, lastMouse = null;

canvas.addEventListener('wheel', e => {{
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.9 : 1.1;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    panX = mx - (mx - panX) * factor;
    panY = my - (my - panY) * factor;
    zoom *= factor;
}});

function screenToWorld(sx, sy) {{
    return [(sx - panX) / zoom, (sy - panY) / zoom];
}}

function findNode(sx, sy) {{
    const [wx, wy] = screenToWorld(sx, sy);
    for (let i = nodes.length - 1; i >= 0; i--) {{
        const n = nodes[i];
        const dx = wx - n.x, dy = wy - n.y;
        if (dx*dx + dy*dy < (n.radius/zoom + 4) * (n.radius/zoom + 4)) return n;
    }}
    return null;
}}

canvas.addEventListener('mousedown', e => {{
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const node = findNode(mx, my);
    if (node) {{
        dragNode = node;
        dragNode._fixed = true;
    }} else {{
        dragging = true;
    }}
    lastMouse = [e.clientX, e.clientY];
}});

canvas.addEventListener('mousemove', e => {{
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    if (dragging && lastMouse) {{
        panX += e.clientX - lastMouse[0];
        panY += e.clientY - lastMouse[1];
        lastMouse = [e.clientX, e.clientY];
    }} else if (dragNode) {{
        const [wx, wy] = screenToWorld(mx, my);
        dragNode.x = wx;
        dragNode.y = wy;
        lastMouse = [e.clientX, e.clientY];
    }} else {{
        const node = findNode(mx, my);
        if (node) {{
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX + 15) + 'px';
            tooltip.style.top = (e.clientY + 15) + 'px';
            tooltip.querySelector('.tt-title').textContent = node.title;
            tooltip.querySelector('.tt-summary').textContent = node.summary || '';
            const tagsEl = tooltip.querySelector('.tt-tags');
            tagsEl.innerHTML = '';
            node.tags.forEach(t => {{
                const span = document.createElement('span');
                span.className = 'tt-tag';
                span.textContent = t;
                span.style.background = tagColors[t.toLowerCase()] || '#444';
                span.style.color = '#fff';
                tagsEl.appendChild(span);
            }});
            canvas.style.cursor = 'pointer';
        }} else {{
            tooltip.style.display = 'none';
            canvas.style.cursor = 'grab';
        }}
    }}
}});

canvas.addEventListener('mouseup', e => {{
    dragging = false;
    if (dragNode) {{ dragNode._fixed = false; dragNode = null; }}
    lastMouse = null;
}});

canvas.addEventListener('click', e => {{
    const rect = canvas.getBoundingClientRect();
    const node = findNode(e.clientX - rect.left, e.clientY - rect.top);
    if (node && node.url) window.open(node.url, '_blank');
}});

// Force simulation
function simulate() {{
    const alpha = 0.3;
    const repulsion = 800;
    const attraction = 0.005;
    const centerForce = 0.0005;

    // Center gravity
    nodes.forEach(n => {{
        if (n._fixed) return;
        n.vx += (W/2 - n.x) * centerForce;
        n.vy += (H/2 - n.y) * centerForce;
    }});

    // Repulsion (Barnes-Hut approximation: just use subset for large graphs)
    const step = nodes.length > 200 ? 3 : 1;
    for (let i = 0; i < nodes.length; i++) {{
        if (nodes[i]._fixed) continue;
        for (let j = i + step; j < nodes.length; j += step) {{
            const dx = nodes[i].x - nodes[j].x;
            const dy = nodes[i].y - nodes[j].y;
            const d2 = dx*dx + dy*dy + 1;
            const f = repulsion / d2;
            const fx = dx * f, fy = dy * f;
            nodes[i].vx += fx;
            nodes[i].vy += fy;
            if (!nodes[j]._fixed) {{
                nodes[j].vx -= fx;
                nodes[j].vy -= fy;
            }}
        }}
    }}

    // Attraction along edges
    edges.forEach(e => {{
        const si = idToIdx[e.source], ti = idToIdx[e.target];
        if (si === undefined || ti === undefined) return;
        const s = nodes[si], t = nodes[ti];
        const dx = t.x - s.x, dy = t.y - s.y;
        const d = Math.sqrt(dx*dx + dy*dy) + 1;
        const f = (d - 100) * attraction;
        const fx = dx/d * f, fy = dy/d * f;
        if (!s._fixed) {{ s.vx += fx; s.vy += fy; }}
        if (!t._fixed) {{ t.vx -= fx; t.vy -= fy; }}
    }});

    // Apply velocity with damping
    nodes.forEach(n => {{
        if (n._fixed) return;
        n.vx *= 0.6;
        n.vy *= 0.6;
        n.x += n.vx;
        n.y += n.vy;
    }});
}}

function draw() {{
    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);

    // Draw edges
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 0.5 / zoom;
    edges.forEach(e => {{
        const si = idToIdx[e.source], ti = idToIdx[e.target];
        if (si === undefined || ti === undefined) return;
        ctx.beginPath();
        ctx.moveTo(nodes[si].x, nodes[si].y);
        ctx.lineTo(nodes[ti].x, nodes[ti].y);
        ctx.stroke();
    }});

    // Draw nodes
    nodes.forEach(n => {{
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.globalAlpha = 0.85;
        ctx.fill();
        ctx.globalAlpha = 1;
    }});

    ctx.restore();
}}

function loop() {{
    simulate();
    draw();
    requestAnimationFrame(loop);
}}
loop();
</script>
</body>
</html>"""

    graph_path = DB_DIR / "graph.html"
    with open(graph_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    if args.open:
        webbrowser.open(f"file://{graph_path}")

    print(json.dumps({
        "status": "ok",
        "path": str(graph_path),
        "nodes": len(nodes),
        "edges": len(edges),
        "tags": len(all_tags),
    }))


# =====================================================================
# Feature 3: Smart Natural Language Search
# =====================================================================

def _parse_natural_query(query):
    """Parse natural language search query into structured filters."""
    q = query.lower().strip()
    filters = {
        "topic_words": [],
        "time_filter": None,  # (after_date, before_date)
        "source_filter": None,  # domain substring
        "status_filter": None,  # "read", "unread"
        "rating_filter": None,  # "rated", "unrated", or min_rating int
        "sort": None,  # "newest", "oldest", "best"
    }

    now = datetime.now(timezone.utc)
    remaining = q

    # Time references
    time_patterns = [
        (r'\b(?:last|past)\s+(\d+)\s+days?\b', lambda m: (now - timedelta(days=int(m.group(1))), now)),
        (r'\b(?:last|past)\s+(\d+)\s+weeks?\b', lambda m: (now - timedelta(weeks=int(m.group(1))), now)),
        (r'\b(?:last|past)\s+(\d+)\s+months?\b', lambda m: (now - timedelta(days=int(m.group(1))*30), now)),
        (r'\byesterday\b', lambda m: (now - timedelta(days=1), now)),
        (r'\btoday\b', lambda m: (now - timedelta(hours=24), now)),
        (r'\blast\s+week\b', lambda m: (now - timedelta(weeks=1), now)),
        (r'\bthis\s+week\b', lambda m: (now - timedelta(days=now.weekday()), now)),
        (r'\blast\s+month\b', lambda m: (now - timedelta(days=30), now)),
        (r'\bthis\s+month\b', lambda m: (now.replace(day=1, hour=0, minute=0, second=0), now)),
        (r'\bthis\s+year\b', lambda m: (now.replace(month=1, day=1, hour=0, minute=0, second=0), now)),
        (r'\bin\s+(january|february|march|april|may|june|july|august|september|october|november|december)\b',
         lambda m: _month_range(m.group(1), now)),
    ]

    for pattern, handler in time_patterns:
        m = re.search(pattern, remaining)
        if m:
            result = handler(m)
            if result:
                filters["time_filter"] = (result[0].isoformat(), result[1].isoformat())
            remaining = remaining[:m.start()] + remaining[m.end():]
            break

    # Source filters: "from github", "from twitter", "from x"
    source_m = re.search(r'\bfrom\s+(\w+(?:\.\w+)?)\b', remaining)
    if source_m:
        source = source_m.group(1)
        source_map = {
            "twitter": "twitter.com", "x": "x.com",
            "github": "github.com", "reddit": "reddit.com",
            "youtube": "youtube.com", "hn": "news.ycombinator.com",
            "hackernews": "news.ycombinator.com",
        }
        filters["source_filter"] = source_map.get(source, source)
        remaining = remaining[:source_m.start()] + remaining[source_m.end():]

    # Status filters
    if re.search(r'\bunread\b', remaining):
        filters["status_filter"] = "unread"
        remaining = re.sub(r'\bunread\b', '', remaining)
    elif re.search(r'\bread\b', remaining):
        # Disambiguate: "read" as status vs topic word
        if re.search(r'\b(?:already|marked?|is)\s+read\b', remaining) or remaining.strip() in ("read", "read stuff", "read links"):
            filters["status_filter"] = "read"
            remaining = re.sub(r'\bread\b', '', remaining)

    # Rating filters
    if re.search(r'\b(?:best|top\s*rated|highest\s*rated)\b', remaining):
        filters["rating_filter"] = "best"
        filters["sort"] = "best"
        remaining = re.sub(r'\b(?:best|top\s*rated|highest\s*rated|rated)\b', '', remaining)
    elif re.search(r'\b(?:unrated|no\s*rating)\b', remaining):
        filters["rating_filter"] = "unrated"
        remaining = re.sub(r'\b(?:unrated|no\s*rating)\b', '', remaining)
    elif re.search(r'\brated\b', remaining):
        filters["rating_filter"] = "rated"
        remaining = re.sub(r'\brated\b', '', remaining)
    else:
        star_m = re.search(r'\b(\d)\s*stars?\b', remaining)
        if star_m:
            filters["rating_filter"] = int(star_m.group(1))
            remaining = remaining[:star_m.start()] + remaining[star_m.end():]

    # Sort hints
    if re.search(r'\bnewest\b', remaining):
        filters["sort"] = "newest"
        remaining = re.sub(r'\bnewest\b', '', remaining)
    elif re.search(r'\boldest\b', remaining):
        filters["sort"] = "oldest"
        remaining = re.sub(r'\boldest\b', '', remaining)

    # Clean up remaining words to get topic
    noise = {"what", "did", "i", "save", "saved", "about", "stuff", "things",
             "something", "anything", "links", "articles", "my", "the", "a",
             "show", "find", "get", "me", "with", "that", "those", "some",
             "any", "all", "have"}
    words = remaining.split()
    topic_words = [w for w in words if w.lower() not in noise and len(w) > 1]
    filters["topic_words"] = topic_words

    return filters


def _month_range(month_name, now):
    """Get date range for a named month in the current or previous year."""
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    month_num = months.get(month_name.lower())
    if not month_num:
        return None
    year = now.year if month_num <= now.month else now.year - 1
    start = datetime(year, month_num, 1, tzinfo=timezone.utc)
    if month_num == 12:
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year, month_num + 1, 1, tzinfo=timezone.utc)
    return (start, end)


def _smart_search(db, query, limit=20):
    """Execute a smart search with natural language parsing."""
    filters = _parse_natural_query(query)

    has_special = (
        filters["time_filter"] or filters["source_filter"] or
        filters["status_filter"] or filters["rating_filter"] or
        filters["sort"]
    )

    if not has_special and not filters["topic_words"]:
        # Empty query
        return []

    conditions = []
    params = []

    # Topic search via FTS or LIKE
    topic = " ".join(filters["topic_words"])

    # Time filter
    if filters["time_filter"]:
        after, before = filters["time_filter"]
        conditions.append("saved_at >= ?")
        params.append(after)
        conditions.append("saved_at <= ?")
        params.append(before)

    # Source filter
    if filters["source_filter"]:
        conditions.append("url LIKE ?")
        params.append(f"%{filters['source_filter']}%")

    # Status filter
    if filters["status_filter"] == "unread":
        conditions.append("(is_read = 0 OR is_read IS NULL)")
    elif filters["status_filter"] == "read":
        conditions.append("is_read = 1")

    # Rating filter
    if filters["rating_filter"] == "best":
        conditions.append("rating IS NOT NULL")
    elif filters["rating_filter"] == "rated":
        conditions.append("rating IS NOT NULL")
    elif filters["rating_filter"] == "unrated":
        conditions.append("rating IS NULL")
    elif isinstance(filters["rating_filter"], int):
        conditions.append("rating = ?")
        params.append(filters["rating_filter"])

    # Sort
    sort_order = "saved_at DESC"
    if filters["sort"] == "newest":
        sort_order = "saved_at DESC"
    elif filters["sort"] == "oldest":
        sort_order = "saved_at ASC"
    elif filters["sort"] == "best":
        sort_order = "rating DESC, saved_at DESC"

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    if topic:
        # Try FTS first with conditions
        fts_terms = re.sub(r'[^\w\s]', ' ', topic).split()
        if fts_terms:
            fts_expr = " OR ".join(f'"{t}"*' for t in fts_terms if t)
            try:
                if conditions:
                    fts_conditions = " AND ".join(conditions)
                    sql = f"""SELECT links.* FROM links_fts
                              JOIN links ON links.id = links_fts.rowid
                              WHERE links_fts MATCH ? AND {fts_conditions}
                              ORDER BY {sort_order} LIMIT ?"""
                    rows = db.execute(sql, [fts_expr] + params + [limit]).fetchall()
                else:
                    sql = f"""SELECT links.*, rank FROM links_fts
                              JOIN links ON links.id = links_fts.rowid
                              WHERE links_fts MATCH ?
                              ORDER BY {sort_order} LIMIT ?"""
                    rows = db.execute(sql, [fts_expr, limit]).fetchall()

                if rows:
                    return [link_to_dict(r) for r in rows]
            except Exception:
                pass

        # Fallback: LIKE search with conditions
        like = f"%{topic}%"
        like_cond = "(title LIKE ? OR summary LIKE ? OR tags LIKE ? OR url LIKE ?)"
        if conditions:
            sql = f"SELECT * FROM links WHERE {like_cond} AND {' AND '.join(conditions)} ORDER BY {sort_order} LIMIT ?"
            rows = db.execute(sql, [like, like, like, like] + params + [limit]).fetchall()
        else:
            sql = f"SELECT * FROM links WHERE {like_cond} ORDER BY {sort_order} LIMIT ?"
            rows = db.execute(sql, [like, like, like, like, limit]).fetchall()
        return [link_to_dict(r) for r in rows]
    else:
        # No topic, just filters
        sql = f"SELECT * FROM links {where_clause} ORDER BY {sort_order} LIMIT ?"
        rows = db.execute(sql, params + [limit]).fetchall()
        return [link_to_dict(r) for r in rows]


# =====================================================================
# Feature 4: Collections / Reading Lists
# =====================================================================

def cmd_collection(args):
    """Manage collections / reading lists."""
    db = get_db()
    sub = args.collection_command

    if sub == "create":
        name = args.name
        desc = args.description or ""
        now = now_iso()
        try:
            db.execute(
                "INSERT INTO collections (name, description, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (name, desc, now, now)
            )
            db.commit()
            coll = db.execute("SELECT * FROM collections WHERE name = ?", (name,)).fetchone()
            print(json.dumps({"status": "created", "collection": dict(coll)}))
        except sqlite3.IntegrityError:
            print(json.dumps({"error": f"Collection '{name}' already exists."}))

    elif sub == "add":
        coll = _find_collection(db, args.collection)
        if not coll:
            print(json.dumps({"error": f"Collection '{args.collection}' not found."}))
            return
        link = db.execute("SELECT * FROM links WHERE id = ?", (args.link_id,)).fetchone()
        if not link:
            print(json.dumps({"error": f"No link with ID {args.link_id}."}))
            return
        now = now_iso()
        try:
            pos = db.execute(
                "SELECT COALESCE(MAX(position), 0) + 1 as p FROM collection_links WHERE collection_id = ?",
                (coll["id"],)
            ).fetchone()["p"]
            db.execute(
                "INSERT INTO collection_links (collection_id, link_id, added_at, position) VALUES (?, ?, ?, ?)",
                (coll["id"], args.link_id, now, pos)
            )
            db.execute("UPDATE collections SET updated_at = ? WHERE id = ?", (now, coll["id"]))
            db.commit()
            print(json.dumps({"status": "added", "collection": coll["name"], "link_id": args.link_id}))
        except sqlite3.IntegrityError:
            print(json.dumps({"error": f"Link {args.link_id} is already in '{coll['name']}'."}))

    elif sub == "remove":
        coll = _find_collection(db, args.collection)
        if not coll:
            print(json.dumps({"error": f"Collection '{args.collection}' not found."}))
            return
        deleted = db.execute(
            "DELETE FROM collection_links WHERE collection_id = ? AND link_id = ?",
            (coll["id"], args.link_id)
        ).rowcount
        db.commit()
        if deleted:
            print(json.dumps({"status": "removed", "collection": coll["name"], "link_id": args.link_id}))
        else:
            print(json.dumps({"error": f"Link {args.link_id} not in '{coll['name']}'."}))

    elif sub == "list":
        rows = db.execute("""
            SELECT c.*, COUNT(cl.link_id) as link_count
            FROM collections c
            LEFT JOIN collection_links cl ON c.id = cl.collection_id
            GROUP BY c.id ORDER BY c.updated_at DESC
        """).fetchall()
        if not rows:
            print(json.dumps({"status": "empty", "message": "No collections yet. Create one: brain.py collection create \"My List\""}))
            return
        print(json.dumps([dict(r) for r in rows], indent=2))

    elif sub == "show":
        coll = _find_collection(db, args.name)
        if not coll:
            print(json.dumps({"error": f"Collection '{args.name}' not found."}))
            return
        rows = db.execute("""
            SELECT l.*, cl.added_at as added_to_collection, cl.position
            FROM links l
            JOIN collection_links cl ON l.id = cl.link_id
            WHERE cl.collection_id = ?
            ORDER BY cl.position
        """, (coll["id"],)).fetchall()
        links = [link_to_dict(r) for r in rows]
        print(json.dumps({
            "collection": dict(coll),
            "links": links,
            "count": len(links),
        }, indent=2))

    elif sub == "export":
        coll = _find_collection(db, args.name)
        if not coll:
            print(json.dumps({"error": f"Collection '{args.name}' not found."}))
            return
        rows = db.execute("""
            SELECT l.* FROM links l
            JOIN collection_links cl ON l.id = cl.link_id
            WHERE cl.collection_id = ?
            ORDER BY cl.position
        """, (coll["id"],)).fetchall()
        links = [link_to_dict(r) for r in rows]

        if args.html:
            output = _export_collection_html(coll, links)
        else:
            output = _export_collection_markdown(coll, links)

        export_ext = ".html" if args.html else ".md"
        safe_name = re.sub(r'[^\w\s-]', '', coll["name"]).strip().replace(' ', '-').lower()
        export_path = DB_DIR / f"collection-{safe_name}{export_ext}"
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(output)

        print(json.dumps({
            "status": "exported",
            "path": str(export_path),
            "format": "html" if args.html else "markdown",
            "links": len(links),
        }))

    else:
        print(json.dumps({"error": "Unknown collection command. Try: create, add, remove, list, show, export"}))


def _find_collection(db, name_or_id):
    """Find collection by name or ID."""
    try:
        cid = int(name_or_id)
        row = db.execute("SELECT * FROM collections WHERE id = ?", (cid,)).fetchone()
        if row:
            return dict(row)
    except (ValueError, TypeError):
        pass
    row = db.execute("SELECT * FROM collections WHERE name = ? COLLATE NOCASE", (name_or_id,)).fetchone()
    if row:
        return dict(row)
    # Fuzzy match
    row = db.execute("SELECT * FROM collections WHERE name LIKE ? COLLATE NOCASE", (f"%{name_or_id}%",)).fetchone()
    if row:
        return dict(row)
    return None


def _export_collection_markdown(coll, links):
    lines = [f"# {coll['name']}", ""]
    if coll.get("description"):
        lines.append(coll["description"])
        lines.append("")
    lines.append(f"*{len(links)} links*")
    lines.append("")
    for i, link in enumerate(links, 1):
        rating_str = f" {'⭐' * link.get('rating', 0)}" if link.get("rating") else ""
        lines.append(f"## {i}. {link['title']}{rating_str}")
        lines.append(f"<{link['url']}>")
        lines.append("")
        if link.get("summary"):
            lines.append(link["summary"])
            lines.append("")
        if link["tags"]:
            lines.append("Tags: " + ", ".join(link["tags"]))
            lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


def _export_collection_html(coll, links):
    items_html = ""
    for i, link in enumerate(links, 1):
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in link["tags"])
        rating_html = f'<span class="rating">{"⭐" * link.get("rating", 0)}</span>' if link.get("rating") else ""
        summary_html = f'<p class="summary">{_html_escape(link.get("summary", ""))}</p>' if link.get("summary") else ""
        items_html += f"""
        <div class="link-card">
            <h2><a href="{_html_escape(link['url'])}" target="_blank">{_html_escape(link['title'])}</a> {rating_html}</h2>
            {summary_html}
            <div class="tags">{tags_html}</div>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_html_escape(coll['name'])}</title>
<style>
body {{ max-width: 700px; margin: 40px auto; padding: 0 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #fafafa; color: #333; line-height: 1.6; }}
h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
.meta {{ color: #888; font-size: 14px; margin-bottom: 24px; }}
.link-card {{ background: #fff; border: 1px solid #e8e8e8; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; }}
.link-card h2 {{ font-size: 16px; margin: 0 0 6px; }}
.link-card h2 a {{ color: #1a73e8; text-decoration: none; }}
.link-card h2 a:hover {{ text-decoration: underline; }}
.summary {{ color: #555; font-size: 14px; margin: 6px 0; }}
.tags {{ margin-top: 8px; }}
.tag {{ display: inline-block; background: #e8f0fe; color: #1967d2; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 4px; }}
.rating {{ font-size: 14px; }}
</style>
</head>
<body>
<h1>{_html_escape(coll['name'])}</h1>
<p class="meta">{len(links)} links</p>
{items_html}
</body>
</html>"""


def _html_escape(text):
    """Escape HTML special characters."""
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# =====================================================================
# Feature 5: Spaced Repetition
# =====================================================================

_REVIEW_INTERVALS = [1, 3, 7, 14, 30, 90]


def cmd_review(args):
    """Spaced repetition review system."""
    db = get_db()
    sub = args.review_command or "next"

    if sub == "next" or sub is None:
        now = now_iso()
        row = db.execute("""
            SELECT l.*, r.next_review_at, r.interval_days, r.review_count
            FROM reviews r
            JOIN links l ON l.id = r.link_id
            WHERE r.next_review_at <= ?
            ORDER BY r.next_review_at ASC
            LIMIT 1
        """, (now,)).fetchone()
        if not row:
            # Show when the next one is due
            next_row = db.execute("""
                SELECT r.next_review_at FROM reviews r ORDER BY r.next_review_at ASC LIMIT 1
            """).fetchone()
            msg = "No links due for review."
            if next_row:
                msg += f" Next review at {next_row['next_review_at'][:16]}."
            print(json.dumps({"status": "empty", "message": msg}))
            return
        link = link_to_dict(row)
        link["review"] = {
            "next_review_at": row["next_review_at"],
            "interval_days": row["interval_days"],
            "review_count": row["review_count"],
        }
        print(json.dumps({"status": "ok", "link": link}, indent=2))

    elif sub == "done":
        link_id = args.id
        review = db.execute("SELECT * FROM reviews WHERE link_id = ?", (link_id,)).fetchone()
        if not review:
            print(json.dumps({"error": f"Link {link_id} is not in the review queue."}))
            return
        now = now_iso()
        current_interval = review["interval_days"]
        # Advance to next interval
        next_interval = current_interval
        for iv in _REVIEW_INTERVALS:
            if iv > current_interval:
                next_interval = iv
                break
        else:
            next_interval = 90  # Max

        next_review = (datetime.now(timezone.utc) + timedelta(days=next_interval)).isoformat()
        db.execute(
            """UPDATE reviews SET interval_days = ?, next_review_at = ?,
               review_count = review_count + 1, last_reviewed_at = ? WHERE link_id = ?""",
            (next_interval, next_review, now, link_id)
        )
        db.commit()
        print(json.dumps({
            "status": "reviewed",
            "link_id": link_id,
            "previous_interval": current_interval,
            "next_interval": next_interval,
            "next_review_at": next_review[:16],
        }))

    elif sub == "skip":
        link_id = args.id
        review = db.execute("SELECT * FROM reviews WHERE link_id = ?", (link_id,)).fetchone()
        if not review:
            print(json.dumps({"error": f"Link {link_id} is not in the review queue."}))
            return
        # Push next_review_at forward by 1 day, keep interval the same
        next_review = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        db.execute("UPDATE reviews SET next_review_at = ? WHERE link_id = ?", (next_review, link_id))
        db.commit()
        print(json.dumps({"status": "skipped", "link_id": link_id, "next_review_at": next_review[:16]}))

    elif sub == "reset":
        link_id = args.id
        review = db.execute("SELECT * FROM reviews WHERE link_id = ?", (link_id,)).fetchone()
        if not review:
            print(json.dumps({"error": f"Link {link_id} is not in the review queue."}))
            return
        next_review = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        db.execute(
            "UPDATE reviews SET interval_days = 1, next_review_at = ?, review_count = 0 WHERE link_id = ?",
            (next_review, link_id)
        )
        db.commit()
        print(json.dumps({"status": "reset", "link_id": link_id, "next_review_at": next_review[:16]}))

    elif sub == "stats":
        now = now_iso()
        total = db.execute("SELECT COUNT(*) as n FROM reviews").fetchone()["n"]
        overdue = db.execute("SELECT COUNT(*) as n FROM reviews WHERE next_review_at <= ?", (now,)).fetchone()["n"]
        reviewed = db.execute("SELECT COUNT(*) as n FROM reviews WHERE review_count > 0").fetchone()["n"]
        avg_interval = db.execute("SELECT AVG(interval_days) as avg FROM reviews").fetchone()["avg"]

        # Interval distribution
        dist = db.execute("""
            SELECT interval_days, COUNT(*) as cnt FROM reviews GROUP BY interval_days ORDER BY interval_days
        """).fetchall()

        print(json.dumps({
            "total_in_queue": total,
            "overdue": overdue,
            "reviewed_at_least_once": reviewed,
            "never_reviewed": total - reviewed,
            "avg_interval_days": round(avg_interval, 1) if avg_interval else 0,
            "interval_distribution": {str(r["interval_days"]): r["cnt"] for r in dist},
        }, indent=2))

    else:
        print(json.dumps({"error": "Unknown review command. Try: done, skip, reset, stats (or just 'review' for next)"}))


# ---- Browser bookmark parsers ----

def _parse_chrome_bookmarks(path=None):
    if path is None:
        candidates = [
            Path.home() / "Library/Application Support/Google/Chrome/Default/Bookmarks",
            Path.home() / "Library/Application Support/Google/Chrome/Profile 1/Bookmarks",
            Path.home() / ".config/google-chrome/Default/Bookmarks",
            Path.home() / ".config/chromium/Default/Bookmarks",
            Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Bookmarks",
        ]
        path = None
        for c in candidates:
            if c.exists():
                path = c
                break
        if not path:
            return None, "Chrome bookmarks file not found. Try --path to specify location."
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    bookmarks = []
    def walk(node):
        if node.get("type") == "url":
            bookmarks.append({"url": node.get("url", ""), "title": node.get("name", ""), "tags": []})
        for child in node.get("children", []):
            walk(child)
    roots = data.get("roots", {})
    for root_name in roots:
        if isinstance(roots[root_name], dict):
            walk(roots[root_name])
    return bookmarks, str(path)


def _parse_safari_bookmarks(path=None):
    if path is None:
        path = Path.home() / "Library/Safari/Bookmarks.plist"
    path = Path(path)
    if not path.exists():
        return None, f"Safari bookmarks file not found: {path}"
    try:
        with open(path, "rb") as f:
            data = plistlib.load(f)
    except PermissionError:
        return None, (
            f"Permission denied reading {path}. "
            f"On macOS, grant Full Disk Access to Terminal in System Settings > Privacy & Security."
        )
    bookmarks = []
    def walk(node):
        if isinstance(node, dict):
            url_dict = node.get("URIDictionary", {})
            url = node.get("URLString", "")
            if url and url.startswith(("http://", "https://")):
                bookmarks.append({"url": url, "title": url_dict.get("title", node.get("Title", "")), "tags": []})
            for child in node.get("Children", []):
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(data)
    return bookmarks, str(path)


def _parse_firefox_bookmarks(path=None):
    if path is None:
        profiles_dir = Path.home() / "Library/Application Support/Firefox/Profiles"
        if not profiles_dir.exists():
            profiles_dir = Path.home() / ".mozilla/firefox"
        if not profiles_dir.exists():
            return None, "Firefox profiles directory not found."
        candidates = list(profiles_dir.glob("*/places.sqlite"))
        if not candidates:
            return None, "No Firefox places.sqlite found."
        path = max(candidates, key=lambda p: p.stat().st_mtime)
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    tmp = Path(tempfile.mkdtemp()) / "places.sqlite"
    shutil.copy2(path, tmp)
    for ext in ["-wal", "-shm"]:
        src = Path(str(path) + ext)
        if src.exists():
            shutil.copy2(src, Path(str(tmp) + ext))
    try:
        fdb = sqlite3.connect(str(tmp))
        fdb.row_factory = sqlite3.Row
        rows = fdb.execute(
            """SELECT mb.title, mp.url FROM moz_bookmarks mb
               JOIN moz_places mp ON mb.fk = mp.id
               WHERE mp.url LIKE 'http%' ORDER BY mb.dateAdded DESC"""
        ).fetchall()
        fdb.close()
    finally:
        tmp.unlink(missing_ok=True)
        tmp.parent.rmdir()
    bookmarks = [{"url": r["url"], "title": r["title"] or "", "tags": []} for r in rows]
    return bookmarks, str(path)


def _parse_x_bookmarks(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    bookmarks = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "url" in item:
                bookmarks.append({"url": item["url"], "title": item.get("title", item.get("text", "")), "tags": ["x-bookmark"]})
            elif isinstance(item, dict) and "tweet" in item:
                tweet = item["tweet"]
                tweet_id = tweet.get("id_str", tweet.get("id", ""))
                text = tweet.get("full_text", tweet.get("text", ""))[:120]
                url = f"https://x.com/i/status/{tweet_id}" if tweet_id else ""
                entities = tweet.get("entities", {})
                urls = entities.get("urls", [])
                if urls:
                    for u in urls:
                        expanded = u.get("expanded_url", u.get("url", ""))
                        if expanded and not expanded.startswith("https://t.co"):
                            bookmarks.append({"url": expanded, "title": text, "tags": ["x-bookmark"]})
                if url:
                    bookmarks.append({"url": url, "title": text, "tags": ["x-bookmark"]})
    elif isinstance(data, dict):
        items = data.get("bookmarks", data.get("data", []))
        if isinstance(items, list):
            for item in items:
                if "url" in item:
                    bookmarks.append({"url": item["url"], "title": item.get("title", item.get("text", "")), "tags": ["x-bookmark"]})
    return bookmarks, str(path)


# ---- Platform-specific export parsers ----

def _parse_youtube_takeout(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    ext = path.suffix.lower()
    bookmarks = []
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = data.get("items", data.get("videos", data.get("data", [])))
        for item in data:
            if not isinstance(item, dict):
                continue
            url = item.get("titleUrl", item.get("url", ""))
            title = item.get("title", item.get("name", ""))
            if title.startswith("Watched "):
                title = title[8:]
            subtitles = item.get("subtitles", [])
            channel = subtitles[0].get("name", "") if subtitles else ""
            summary = f"By {channel}" if channel else ""
            if not url and "videoId" in item:
                url = f"https://www.youtube.com/watch?v={item['videoId']}"
            if not url and "id" in item:
                vid = item["id"]
                if isinstance(vid, str) and len(vid) == 11:
                    url = f"https://www.youtube.com/watch?v={vid}"
            if url and url.startswith(("http://", "https://")):
                bookmarks.append({"url": url, "title": title, "summary": summary, "tags": ["youtube"]})
    elif ext in (".html", ".htm"):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        for m in re.finditer(
            r'<a\s+href="(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^"]+)"[^>]*>([^<]*)</a>',
            content, re.IGNORECASE
        ):
            url, title = m.group(1), m.group(2).strip()
            if url and title:
                bookmarks.append({"url": url, "title": title, "tags": ["youtube"]})
    elif ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = ""
                title = ""
                for k, v in row.items():
                    kl = (k or "").lower().strip()
                    if kl in ("url", "video url", "link", "titleurl"):
                        url = v or ""
                    elif kl in ("title", "video title", "name"):
                        title = v or ""
                if url:
                    bookmarks.append({"url": url, "title": title, "tags": ["youtube"]})
    if not bookmarks:
        return None, f"No YouTube videos found in {path.name}."
    return bookmarks, str(path)


def _parse_reddit_export(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    ext = path.suffix.lower()
    bookmarks = []
    if ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        reader = csv.DictReader(StringIO(content))
        for row in reader:
            url = ""
            title = ""
            subreddit = ""
            for k, v in row.items():
                kl = (k or "").lower().strip()
                if kl in ("permalink", "url", "link"):
                    url = v or ""
                elif kl in ("title", "name", "body"):
                    title = v or ""
                elif kl in ("subreddit", "community"):
                    subreddit = v or ""
            if url and url.startswith("/r/"):
                url = f"https://www.reddit.com{url}"
            elif url and not url.startswith("http"):
                if re.match(r'^[a-z0-9]+$', url):
                    url = f"https://www.reddit.com/comments/{url}"
            tags = ["reddit"]
            if subreddit:
                tags.append(subreddit.lower().strip("/").split("/")[-1])
            if url and url.startswith("http"):
                bookmarks.append({"url": url, "title": title[:200], "tags": tags})
    elif ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("saved", data.get("posts", data.get("data", [])))
        for item in items:
            if not isinstance(item, dict):
                continue
            url = item.get("permalink", item.get("url", item.get("link", "")))
            title = item.get("title", item.get("name", item.get("body", "")))[:200]
            subreddit = item.get("subreddit", item.get("community", ""))
            if url and url.startswith("/r/"):
                url = f"https://www.reddit.com{url}"
            tags = ["reddit"]
            if subreddit:
                tags.append(subreddit.lower())
            if url and url.startswith("http"):
                bookmarks.append({"url": url, "title": title, "tags": tags})
    elif ext in (".html", ".htm"):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        parser = BookmarkHTMLParser()
        parser.feed(content)
        for bm in parser.bookmarks:
            bm["tags"] = bm.get("tags", []) + ["reddit"]
            bookmarks.append(bm)
    if not bookmarks:
        return None, f"No Reddit posts found in {path.name}."
    return bookmarks, str(path)


def _parse_pocket_export(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    ext = path.suffix.lower()
    bookmarks = []
    if ext in (".html", ".htm") or content.strip().startswith(("<", "<!DOCTYPE")):
        parser = BookmarkHTMLParser()
        parser.feed(content)
        for bm in parser.bookmarks:
            existing_tags = bm.get("tags", [])
            if "pocket" not in existing_tags:
                existing_tags.append("pocket")
            bm["tags"] = existing_tags
            bookmarks.append(bm)
    elif ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("list", data.get("items", data.get("bookmarks", [])))
        if isinstance(items, dict):
            items = list(items.values())
        for item in items:
            if not isinstance(item, dict):
                continue
            url = item.get("resolved_url", item.get("given_url", item.get("url", "")))
            title = item.get("resolved_title", item.get("given_title", item.get("title", "")))
            tags = list(item.get("tags", {}).keys()) if isinstance(item.get("tags"), dict) else item.get("tags", [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(",") if t.strip()]
            tags.append("pocket")
            if url and url.startswith("http"):
                bookmarks.append({"url": url, "title": title, "tags": tags})
    elif ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = ""
                title = ""
                tags = ["pocket"]
                for k, v in row.items():
                    kl = (k or "").lower().strip()
                    if kl in ("url", "link", "resolved_url", "given_url"):
                        url = v or ""
                    elif kl in ("title", "resolved_title", "given_title"):
                        title = v or ""
                    elif kl in ("tags",):
                        tags += [t.strip().lower() for t in (v or "").split(",") if t.strip()]
                if url and url.startswith("http"):
                    bookmarks.append({"url": url, "title": title, "tags": tags})
    if not bookmarks:
        return None, f"No bookmarks found in {path.name}."
    return bookmarks, str(path)


def _parse_instapaper_export(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    bookmarks = []
    ext = path.suffix.lower()
    if ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = ""
                title = ""
                folder = ""
                selection = ""
                for k, v in row.items():
                    kl = (k or "").lower().strip()
                    if kl == "url": url = v or ""
                    elif kl == "title": title = v or ""
                    elif kl == "folder": folder = v or ""
                    elif kl == "selection": selection = v or ""
                tags = ["instapaper"]
                if folder and folder.lower() not in ("unread", "archive", "starred"):
                    tags.append(folder.lower())
                summary = selection[:300] if selection else ""
                if url and url.startswith("http"):
                    bookmarks.append({"url": url, "title": title, "summary": summary, "tags": tags})
    elif ext in (".html", ".htm"):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        parser = BookmarkHTMLParser()
        parser.feed(content)
        for bm in parser.bookmarks:
            bm["tags"] = bm.get("tags", []) + ["instapaper"]
            bookmarks.append(bm)
    if not bookmarks:
        return None, f"No bookmarks found in {path.name}."
    return bookmarks, str(path)


def _parse_raindrop_export(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    bookmarks = []
    ext = path.suffix.lower()
    if ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = ""
                title = ""
                note = ""
                excerpt = ""
                folder = ""
                tags_str = ""
                for k, v in row.items():
                    kl = (k or "").lower().strip()
                    if kl == "url": url = v or ""
                    elif kl == "title": title = v or ""
                    elif kl == "note": note = v or ""
                    elif kl == "excerpt": excerpt = v or ""
                    elif kl == "folder": folder = v or ""
                    elif kl == "tags": tags_str = v or ""
                tags = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
                tags.append("raindrop")
                if folder and folder.lower() not in ("unsorted",):
                    tags.append(folder.lower())
                summary = note or excerpt or ""
                if len(summary) > 300:
                    summary = summary[:300]
                if url and url.startswith("http"):
                    bookmarks.append({"url": url, "title": title, "summary": summary, "tags": tags})
    elif ext in (".html", ".htm"):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        parser = BookmarkHTMLParser()
        parser.feed(content)
        for bm in parser.bookmarks:
            bm["tags"] = bm.get("tags", []) + ["raindrop"]
            bookmarks.append(bm)
    if not bookmarks:
        return None, f"No bookmarks found in {path.name}."
    return bookmarks, str(path)


def _parse_hackernews_export(path):
    path = Path(path)
    if not path.exists():
        return None, f"File not found: {path}"
    bookmarks = []
    ext = path.suffix.lower()
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("hits", data.get("items", data.get("stories", [])))
        for item in items:
            if not isinstance(item, dict):
                continue
            url = item.get("url", item.get("link", ""))
            title = item.get("title", item.get("story_title", ""))
            hn_id = item.get("objectID", item.get("id", item.get("story_id", "")))
            points = item.get("points", item.get("score", ""))
            num_comments = item.get("num_comments", "")
            if not url and hn_id:
                url = f"https://news.ycombinator.com/item?id={hn_id}"
            summary_parts = []
            if points: summary_parts.append(f"{points} points")
            if num_comments: summary_parts.append(f"{num_comments} comments")
            summary = ", ".join(summary_parts)
            tags = ["hackernews"]
            if url and url.startswith("http"):
                bookmarks.append({"url": url, "title": title, "summary": summary, "tags": tags})
                if hn_id and not url.startswith("https://news.ycombinator.com"):
                    hn_url = f"https://news.ycombinator.com/item?id={hn_id}"
                    bookmarks.append({"url": hn_url, "title": f"HN Discussion: {title}", "summary": summary, "tags": ["hackernews", "discussion"]})
    elif ext == ".csv":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = ""
                title = ""
                for k, v in row.items():
                    kl = (k or "").lower().strip()
                    if kl in ("url", "link"): url = v or ""
                    elif kl in ("title", "name", "story_title"): title = v or ""
                if url and url.startswith("http"):
                    bookmarks.append({"url": url, "title": title, "tags": ["hackernews"]})
    elif ext in (".html", ".htm"):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        parser = BookmarkHTMLParser()
        parser.feed(content)
        for bm in parser.bookmarks:
            bm["tags"] = bm.get("tags", []) + ["hackernews"]
            bookmarks.append(bm)
    if not bookmarks:
        return None, f"No items found in {path.name}."
    return bookmarks, str(path)


# ---- Bookmark HTML parser (Netscape format) ----

class BookmarkHTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.bookmarks = []
        self._current_url = None
        self._current_tags = []
        self._in_a = False
        self._title_parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            d = dict(attrs)
            href = d.get("href", "")
            if href.startswith(("http://", "https://")):
                self._current_url = href
                self._current_tags = [t.strip().lower() for t in d.get("tags", "").split(",") if t.strip()]
                self._in_a = True
                self._title_parts = []

    def handle_data(self, data):
        if self._in_a:
            self._title_parts.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._in_a:
            self._in_a = False
            if self._current_url:
                self.bookmarks.append({
                    "url": self._current_url,
                    "title": "".join(self._title_parts).strip(),
                    "tags": self._current_tags,
                })
            self._current_url = None


# ---- Commands ----

def _link_not_found(link_id):
    return json.dumps({
        "error": f"No link with ID {link_id}. Try `brain.py recent` to see your latest saves."
    })


def cmd_save(args):
    db = get_db()

    # Auto mode: fetch and auto-generate everything
    if args.auto:
        # Reuse auto-save logic
        class FakeArgs:
            pass
        fake = FakeArgs()
        fake.url = args.url
        cmd_auto_save(fake)
        return

    now = now_iso()

    tag_list = []
    if args.tags:
        tag_list = [t.strip().lower() for t in args.tags.split(",") if t.strip()]

    suggested = []
    if not tag_list:
        suggested = _suggest_tags_for_url(db, args.url)

    tags_str = ", ".join(tag_list)
    source_type = detect_source_type(args.url)

    cursor = db.execute(
        """INSERT INTO links (url, title, summary, tags, source_type, saved_at, updated_at, source)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'manual')""",
        (args.url, args.title or "", args.summary or "", tags_str, source_type, now, now)
    )
    link_id = cursor.lastrowid

    tag_ids = ensure_tags(db, tag_list)
    for tid in tag_ids:
        db.execute("INSERT OR IGNORE INTO link_tags (link_id, tag_id) VALUES (?, ?)",
                   (link_id, tid))

    # Add to review queue
    _ensure_review_entry(db, link_id)

    db.commit()

    milestones = track_activity(db, "save")

    link = db.execute("SELECT * FROM links WHERE id = ?", (link_id,)).fetchone()
    result = {"status": "saved", "link": link_to_dict(link)}

    if suggested and not tag_list:
        result["suggested_tags"] = suggested
    if milestones:
        result["milestones"] = milestones

    print(json.dumps(result))


def cmd_search(args):
    db = get_db()
    query = args.query
    limit = args.limit or 20

    # Try smart search first
    results = _smart_search(db, query, limit)

    if not results:
        # Fall back to original FTS
        fts_query = re.sub(r'[^\w\s]', ' ', query)
        terms = fts_query.split()
        if terms:
            fts_expr = " OR ".join(f'"{t}"*' for t in terms if t)
            rows = db.execute(
                """SELECT links.*, rank FROM links_fts
                   JOIN links ON links.id = links_fts.rowid
                   WHERE links_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (fts_expr, limit)
            ).fetchall()
            results = [link_to_dict(r) for r in rows]

        if not results:
            like_pattern = f"%{query}%"
            rows = db.execute(
                """SELECT * FROM links
                   WHERE title LIKE ? OR summary LIKE ? OR tags LIKE ? OR url LIKE ?
                   ORDER BY saved_at DESC LIMIT ?""",
                (like_pattern, like_pattern, like_pattern, like_pattern, limit)
            ).fetchall()
            results = [link_to_dict(r) for r in rows]

    print(json.dumps(results, indent=2))


def cmd_recent(args):
    db = get_db()
    limit = args.limit or 20
    rows = db.execute("SELECT * FROM links ORDER BY saved_at DESC LIMIT ?", (limit,)).fetchall()
    if not rows:
        print(json.dumps({"status": "empty", "message": "No links yet. Save your first one: brain.py save <url>"}))
        return
    print(json.dumps([link_to_dict(r) for r in rows], indent=2))


def cmd_tags(args):
    db = get_db()
    if args.name:
        tag_name = args.name.lower()
        rows = db.execute(
            """SELECT links.* FROM links
               JOIN link_tags ON links.id = link_tags.link_id
               JOIN tags ON tags.id = link_tags.tag_id
               WHERE tags.name = ?
               ORDER BY links.saved_at DESC""",
            (tag_name,)
        ).fetchall()
        if not rows:
            print(json.dumps({"status": "empty", "message": f"No links tagged '{tag_name}'."}))
            return
        print(json.dumps([link_to_dict(r) for r in rows], indent=2))
    else:
        rows = db.execute(
            """SELECT tags.name, COUNT(link_tags.link_id) as count
               FROM tags JOIN link_tags ON tags.id = link_tags.tag_id
               GROUP BY tags.name ORDER BY count DESC"""
        ).fetchall()
        if not rows:
            print(json.dumps({"status": "empty", "message": "No tags yet."}))
            return
        print(json.dumps([dict(r) for r in rows], indent=2))


def cmd_get(args):
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if row:
        print(json.dumps(link_to_dict(row), indent=2))
    else:
        print(_link_not_found(args.id))


def cmd_delete(args):
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if row:
        db.execute("DELETE FROM links WHERE id = ?", (args.id,))
        db.commit()
        print(json.dumps({"status": "deleted", "link": link_to_dict(row)}))
    else:
        print(_link_not_found(args.id))


def cmd_stats(args):
    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    if total == 0:
        print(json.dumps({"status": "empty", "message": "No links yet."}))
        return
    by_type = db.execute("SELECT source_type, COUNT(*) as n FROM links GROUP BY source_type ORDER BY n DESC").fetchall()
    tag_count = db.execute("SELECT COUNT(*) as n FROM tags").fetchone()["n"]
    recent = db.execute("SELECT saved_at FROM links ORDER BY saved_at DESC LIMIT 1").fetchone()
    oldest = db.execute("SELECT saved_at FROM links ORDER BY saved_at ASC LIMIT 1").fetchone()
    unread = db.execute("SELECT COUNT(*) as n FROM links WHERE is_read = 0 OR is_read IS NULL").fetchone()["n"]
    rated = db.execute("SELECT COUNT(*) as n FROM links WHERE rating IS NOT NULL").fetchone()["n"]
    avg_rating = db.execute("SELECT AVG(rating) as avg FROM links WHERE rating IS NOT NULL").fetchone()["avg"]
    by_source = db.execute("SELECT COALESCE(source, 'manual') as src, COUNT(*) as n FROM links GROUP BY src ORDER BY n DESC").fetchall()
    removed = db.execute("SELECT COUNT(*) as n FROM links WHERE removed_from_source = 1").fetchone()["n"]
    streak = _calculate_streak(db)
    collections_count = db.execute("SELECT COUNT(*) as n FROM collections").fetchone()["n"]
    review_queue = db.execute("SELECT COUNT(*) as n FROM reviews").fetchone()["n"]

    stats = {
        "total_links": total, "total_tags": tag_count, "unread": unread,
        "rated": rated, "avg_rating": round(avg_rating, 1) if avg_rating else None,
        "current_streak": streak, "removed_from_source": removed,
        "collections": collections_count, "review_queue": review_queue,
        "by_type": {r["source_type"]: r["n"] for r in by_type},
        "by_source": {r["src"]: r["n"] for r in by_source},
        "newest": recent["saved_at"] if recent else None,
        "oldest": oldest["saved_at"] if oldest else None,
    }
    print(json.dumps(stats, indent=2))


def cmd_export(args):
    db = get_db()
    rows = db.execute("SELECT * FROM links ORDER BY saved_at DESC").fetchall()
    print(json.dumps([link_to_dict(r) for r in rows], indent=2))


def _parse_since(since_str):
    m = re.match(r'^(\d+)([dwm])$', since_str.strip())
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    if unit == 'd': return datetime.now(timezone.utc) - timedelta(days=n)
    elif unit == 'w': return datetime.now(timezone.utc) - timedelta(weeks=n)
    elif unit == 'm': return datetime.now(timezone.utc) - timedelta(days=n * 30)
    return None


def cmd_digest(args):
    db = get_db()
    config = load_config()
    count = args.count or config.get("digest_count", 5)
    mode = args.mode or config.get("digest_mode", "shuffle")
    conditions = []
    params = []
    if args.unread_only:
        conditions.append("(is_read = 0 OR is_read IS NULL)")
    if args.since:
        cutoff = _parse_since(args.since)
        if cutoff:
            conditions.append("saved_at >= ?")
            params.append(cutoff.isoformat())
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    if mode == "newest":
        order = "ORDER BY (last_digested_at IS NULL) DESC, saved_at DESC"
    elif mode == "oldest":
        order = "ORDER BY (last_digested_at IS NULL) DESC, saved_at ASC"
    else:
        order = "ORDER BY (last_digested_at IS NULL) DESC, saved_at DESC"
    pool_size = count * 4 if mode == "shuffle" else count
    query = f"SELECT * FROM links {where} {order} LIMIT ?"
    params.append(pool_size)
    rows = db.execute(query, params).fetchall()
    results = [link_to_dict(r) for r in rows]
    if mode == "shuffle":
        never = [r for r in results if not r.get("last_digested_at")]
        rest = [r for r in results if r.get("last_digested_at")]
        random.shuffle(never)
        random.shuffle(rest)
        results = (never + rest)[:count]
    else:
        results = results[:count]
    if not results:
        print(json.dumps({"status": "empty", "message": "No links match your digest criteria."}))
        return
    now = now_iso()
    for r in results:
        db.execute("UPDATE links SET last_digested_at = ?, updated_at = ? WHERE id = ?", (now, now, r["id"]))
    db.commit()
    print(json.dumps({"status": "ok", "count": len(results), "links": results}))


def cmd_rate(args):
    if args.rating < 1 or args.rating > 5:
        print(json.dumps({"error": "Rating must be between 1 and 5."}))
        return
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(_link_not_found(args.id))
        return
    now = now_iso()
    db.execute("UPDATE links SET rating = ?, updated_at = ? WHERE id = ?", (args.rating, now, args.id))
    db.commit()
    updated = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    print(json.dumps({"status": "rated", "link": link_to_dict(updated)}))


def cmd_read(args):
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(_link_not_found(args.id))
        return
    now = now_iso()
    db.execute("UPDATE links SET is_read = 1, updated_at = ? WHERE id = ?", (now, args.id))
    db.commit()
    milestones = track_activity(db, "read")
    updated = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    result = {"status": "marked_read", "link": link_to_dict(updated)}
    if milestones:
        result["milestones"] = milestones
    print(json.dumps(result))


def cmd_unread(args):
    db = get_db()
    limit = args.limit or 20
    rows = db.execute(
        "SELECT * FROM links WHERE is_read = 0 OR is_read IS NULL ORDER BY saved_at DESC LIMIT ?",
        (limit,)
    ).fetchall()
    if not rows:
        print(json.dumps({"status": "empty", "message": "All caught up! No unread links."}))
        return
    print(json.dumps([link_to_dict(r) for r in rows], indent=2))


def cmd_recommend(args):
    db = get_db()
    limit = args.limit or 10
    top_tags = db.execute(
        """SELECT tags.name, COUNT(link_tags.link_id) as cnt
           FROM tags JOIN link_tags ON tags.id = link_tags.tag_id
           GROUP BY tags.name ORDER BY cnt DESC LIMIT 10"""
    ).fetchall()
    if not top_tags:
        print(json.dumps({"status": "empty", "message": "No tags found."}))
        return
    tag_names = [r["name"] for r in top_tags]
    placeholders = ",".join("?" for _ in tag_names)
    rows = db.execute(
        f"""SELECT DISTINCT links.* FROM links
            JOIN link_tags ON links.id = link_tags.link_id
            JOIN tags ON tags.id = link_tags.tag_id
            WHERE tags.name IN ({placeholders})
              AND (links.is_read = 0 OR links.is_read IS NULL)
            ORDER BY links.saved_at DESC LIMIT ?""",
        (*tag_names, limit)
    ).fetchall()
    print(json.dumps({
        "status": "ok", "top_tags": tag_names[:5],
        "recommendations": [link_to_dict(r) for r in rows]
    }, indent=2))


def cmd_related(args):
    db = get_db()
    row = db.execute("SELECT * FROM links WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(_link_not_found(args.id))
        return
    link = link_to_dict(row)
    if not link["tags"]:
        print(json.dumps({"status": "empty", "message": f"Link #{args.id} has no tags."}))
        return
    tag_names = link["tags"]
    placeholders = ",".join("?" for _ in tag_names)
    rows = db.execute(
        f"""SELECT links.*, COUNT(DISTINCT tags.name) as shared_tags
            FROM links JOIN link_tags ON links.id = link_tags.link_id
            JOIN tags ON tags.id = link_tags.tag_id
            WHERE tags.name IN ({placeholders}) AND links.id != ?
              AND (links.is_read = 0 OR links.is_read IS NULL)
            GROUP BY links.id ORDER BY shared_tags DESC, links.saved_at DESC LIMIT 5""",
        (*tag_names, args.id)
    ).fetchall()
    source = "unread"
    if not rows:
        rows = db.execute(
            f"""SELECT links.*, COUNT(DISTINCT tags.name) as shared_tags
                FROM links JOIN link_tags ON links.id = link_tags.link_id
                JOIN tags ON tags.id = link_tags.tag_id
                WHERE tags.name IN ({placeholders}) AND links.id != ?
                GROUP BY links.id ORDER BY shared_tags DESC, links.saved_at DESC LIMIT 5""",
            (*tag_names, args.id)
        ).fetchall()
        source = "all"
    if not rows:
        print(json.dumps({"status": "empty", "message": "No related links found."}))
        return
    results = []
    for r in rows:
        d = link_to_dict(r)
        d["shared_tag_count"] = r["shared_tags"]
        results.append(d)
    print(json.dumps({"status": "ok", "source_link": link, "source": source, "related": results}, indent=2))


def cmd_suggest_tags(args):
    db = get_db()
    suggestions = _suggest_tags_for_url(db, args.url)
    if not suggestions:
        domain = _get_domain(args.url)
        print(json.dumps({"status": "empty", "message": f"No tag patterns found for {domain}."}))
        return
    print(json.dumps({"status": "ok", "url": args.url, "domain": _get_domain(args.url), "suggested_tags": suggestions}, indent=2))


def cmd_gems(args):
    db = get_db()
    count = args.count or 5
    results = []
    unread_gems = db.execute(
        "SELECT * FROM links WHERE rating >= 4 AND (is_read = 0 OR is_read IS NULL) ORDER BY rating DESC, saved_at DESC LIMIT ?",
        (count,)
    ).fetchall()
    for r in unread_gems:
        d = link_to_dict(r)
        d["gem_type"] = "unread_gem"
        results.append(d)
    remaining = count - len(results)
    if remaining > 0:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        old_favs = db.execute(
            "SELECT * FROM links WHERE rating >= 4 AND is_read = 1 AND updated_at < ? ORDER BY rating DESC, updated_at ASC LIMIT ?",
            (cutoff, remaining)
        ).fetchall()
        for r in old_favs:
            d = link_to_dict(r)
            d["gem_type"] = "revisit"
            results.append(d)
    if not results:
        print(json.dumps({"status": "empty", "message": "No gems yet. Rate some links 4 or 5 stars first."}))
        return
    print(json.dumps({"status": "ok", "count": len(results), "gems": results}, indent=2))


def cmd_random(args):
    db = get_db()
    count = args.count or 1
    rows = db.execute(
        "SELECT * FROM links WHERE is_read = 0 OR is_read IS NULL ORDER BY RANDOM() LIMIT ?",
        (count,)
    ).fetchall()
    if not rows:
        print(json.dumps({"status": "empty", "message": "No unread links in your backlog."}))
        return
    print(json.dumps({
        "status": "ok", "message": "🎲 Here's something from your backlog...",
        "count": len(rows), "links": [link_to_dict(r) for r in rows]
    }, indent=2))


def cmd_streak(args):
    db = get_db()
    streak = _calculate_streak(db)
    total_days = db.execute("SELECT COUNT(*) as n FROM streaks WHERE saves_count > 0 OR reads_count > 0").fetchone()["n"]
    total_saves_tracked = db.execute("SELECT COALESCE(SUM(saves_count), 0) as n FROM streaks").fetchone()["n"]
    total_reads_tracked = db.execute("SELECT COALESCE(SUM(reads_count), 0) as n FROM streaks").fetchone()["n"]
    rows = db.execute("SELECT date FROM streaks WHERE saves_count > 0 OR reads_count > 0 ORDER BY date DESC").fetchall()
    best_streak = 0
    if rows:
        dates = [datetime.strptime(r["date"], "%Y-%m-%d").date() for r in rows]
        current_run = 1
        for i in range(1, len(dates)):
            if dates[i - 1] - dates[i] == timedelta(days=1):
                current_run += 1
            else:
                best_streak = max(best_streak, current_run)
                current_run = 1
        best_streak = max(best_streak, current_run)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    recent = db.execute("SELECT date, saves_count, reads_count FROM streaks WHERE date >= ? ORDER BY date DESC", (week_ago,)).fetchall()
    print(json.dumps({
        "current_streak": streak, "best_streak": best_streak,
        "total_active_days": total_days, "total_saves_tracked": total_saves_tracked,
        "total_reads_tracked": total_reads_tracked, "recent_7_days": [dict(r) for r in recent],
    }, indent=2))


def cmd_insights(args):
    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    if total == 0:
        print(json.dumps({"status": "empty", "message": "No links yet."}))
        return
    tag_rows = db.execute(
        "SELECT tags.name, COUNT(link_tags.link_id) as cnt FROM tags JOIN link_tags ON tags.id = link_tags.tag_id GROUP BY tags.name ORDER BY cnt DESC"
    ).fetchall()
    total_tag_uses = sum(r["cnt"] for r in tag_rows) if tag_rows else 0
    tag_personality = []
    if total_tag_uses > 0:
        for r in tag_rows[:10]:
            pct = round(r["cnt"] / total_tag_uses * 100)
            if pct >= 1:
                tag_personality.append({"tag": r["name"], "percent": pct, "count": r["cnt"]})
    day_rows = db.execute(
        """SELECT CASE CAST(strftime('%w', saved_at) AS INTEGER)
             WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'
             WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'
             WHEN 6 THEN 'Saturday' END as day_name, COUNT(*) as cnt
           FROM links GROUP BY day_name ORDER BY cnt DESC"""
    ).fetchall()
    busiest_day = day_rows[0]["day_name"] if day_rows else "N/A"
    busiest_count = day_rows[0]["cnt"] if day_rows else 0
    read_count = db.execute("SELECT COUNT(*) as n FROM links WHERE is_read = 1").fetchone()["n"]
    unread_count = total - read_count
    read_pct = round(read_count / total * 100) if total > 0 else 0
    rating_row = db.execute("SELECT AVG(rating) as avg, COUNT(*) as cnt FROM links WHERE rating IS NOT NULL").fetchone()
    avg_rating = round(rating_row["avg"], 1) if rating_row["avg"] else None
    rated_count = rating_row["cnt"]
    oldest_unread = db.execute("SELECT * FROM links WHERE is_read = 0 OR is_read IS NULL ORDER BY saved_at ASC LIMIT 1").fetchone()
    first_link = db.execute("SELECT saved_at FROM links ORDER BY saved_at ASC LIMIT 1").fetchone()
    time_span_days = None
    if first_link:
        try:
            first_dt = datetime.fromisoformat(first_link["saved_at"].replace("Z", "+00:00"))
            time_span_days = (datetime.now(timezone.utc) - first_dt).days
        except Exception:
            pass
    print(json.dumps({
        "total_links": total, "tag_personality": tag_personality,
        "busiest_save_day": {"day": busiest_day, "count": busiest_count},
        "read_vs_unread": {"read": read_count, "unread": unread_count, "read_percent": read_pct},
        "ratings": {"average": avg_rating, "rated_count": rated_count},
        "oldest_unread": link_to_dict(oldest_unread) if oldest_unread else None,
        "collection_span_days": time_span_days,
    }, indent=2))


def cmd_weekly(args):
    db = get_db()
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    saved_this_week = db.execute("SELECT COUNT(*) as n FROM links WHERE saved_at >= ?", (week_ago,)).fetchone()["n"]
    read_this_week = db.execute("SELECT COUNT(*) as n FROM links WHERE is_read = 1 AND updated_at >= ?", (week_ago,)).fetchone()["n"]
    top_tags_week = db.execute(
        """SELECT tags.name, COUNT(link_tags.link_id) as cnt FROM links
           JOIN link_tags ON links.id = link_tags.link_id JOIN tags ON tags.id = link_tags.tag_id
           WHERE links.saved_at >= ? GROUP BY tags.name ORDER BY cnt DESC LIMIT 5""",
        (week_ago,)
    ).fetchall()
    streak = _calculate_streak(db)
    total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    unread = db.execute("SELECT COUNT(*) as n FROM links WHERE is_read = 0 OR is_read IS NULL").fetchone()["n"]
    result = {
        "saved_this_week": saved_this_week, "read_this_week": read_this_week,
        "top_tags": [{"tag": r["name"], "count": r["cnt"]} for r in top_tags_week],
        "current_streak": streak, "total_links": total, "unread_backlog": unread,
    }
    lines = ["📚 *Weekly Link Brain Summary*", "",
             f"📥 *Saved:* {saved_this_week} links", f"📖 *Read:* {read_this_week} links"]
    if top_tags_week:
        tags_str = ", ".join(f"{r['name']} ({r['cnt']})" for r in top_tags_week)
        lines.append(f"🏷️ *Top tags:* {tags_str}")
    if streak > 0:
        lines.append(f"🔥 *Streak:* {streak} day{'s' if streak != 1 else ''}")
    lines.append(f"📊 *Total:* {total} links ({unread} unread)")
    result["formatted"] = "\n".join(lines)
    print(json.dumps(result, indent=2))


def cmd_scan(args):
    db = get_db()
    source = args.source.lower()
    parsers = {
        "chrome": ("chrome", _parse_chrome_bookmarks),
        "safari": ("safari", _parse_safari_bookmarks),
        "firefox": ("firefox", _parse_firefox_bookmarks),
        "x": ("x", None), "twitter": ("x", None),
    }
    if source not in parsers:
        print(json.dumps({"error": f"Unknown source: {source}. Supported: {', '.join(parsers.keys())}"}))
        return
    source_name, parser_fn = parsers[source]
    if source_name == "x":
        if not args.path:
            print(json.dumps({"error": "X/Twitter scan needs --path pointing to your bookmark export JSON."}))
            return
        bookmarks, used_path = _parse_x_bookmarks(args.path)
    else:
        bookmarks, used_path = parser_fn(args.path)
    if bookmarks is None:
        print(json.dumps({"error": used_path}))
        return
    if not bookmarks:
        print(json.dumps({"status": "empty", "message": f"No bookmarks found in {source_name}.", "path": used_path}))
        return
    imported, skipped, imported_ids = bulk_insert_links(db, bookmarks, source_name)
    if imported > 0:
        today = today_str()
        db.execute(
            """INSERT INTO streaks (date, saves_count, reads_count) VALUES (?, ?, 0)
               ON CONFLICT(date) DO UPDATE SET saves_count = saves_count + ?""",
            (today, imported, imported)
        )
        db.commit()
    db.execute("UPDATE sources SET path = ? WHERE name = ?", (used_path, source_name))
    db.commit()
    result = {
        "status": "ok", "source": source_name, "path": used_path,
        "found": len(bookmarks), "imported": imported, "skipped_duplicates": skipped,
        "imported_ids": imported_ids, "needs_summarization": imported > 0,
    }
    if imported > 0:
        result["message"] = f"Imported {imported} links from {source_name}. Skipped {skipped} duplicates."
    else:
        result["message"] = f"All {len(bookmarks)} bookmarks from {source_name} already in the DB."
    print(json.dumps(result, indent=2))


def cmd_sync(args):
    db = get_db()
    source = args.source.lower()
    source_map = {"twitter": "x"}
    source_name = source_map.get(source, source)
    parsers = {"chrome": _parse_chrome_bookmarks, "safari": _parse_safari_bookmarks, "firefox": _parse_firefox_bookmarks}
    if source_name == "x":
        if not args.path:
            print(json.dumps({"error": "X/Twitter sync needs --path."}))
            return
        bookmarks, used_path = _parse_x_bookmarks(args.path)
    elif source_name in parsers:
        bookmarks, used_path = parsers[source_name](args.path)
    else:
        print(json.dumps({"error": f"Unknown source: {source_name}."}))
        return
    if bookmarks is None:
        print(json.dumps({"error": used_path}))
        return
    source_urls = set()
    for bm in bookmarks:
        url = bm.get("url", "").strip()
        if url:
            source_urls.add(normalize_url(url))
    db_links = db.execute("SELECT id, url, removed_from_source FROM links WHERE source = ?", (source_name,)).fetchall()
    now = now_iso()
    newly_removed = []
    still_present = 0
    already_flagged = 0
    for link in db_links:
        norm = normalize_url(link["url"])
        if norm not in source_urls:
            if not link["removed_from_source"]:
                if args.auto_delete:
                    db.execute("DELETE FROM links WHERE id = ?", (link["id"],))
                else:
                    db.execute("UPDATE links SET removed_from_source = 1, updated_at = ? WHERE id = ?", (now, link["id"]))
                newly_removed.append({"id": link["id"], "url": link["url"]})
            else:
                already_flagged += 1
        else:
            if link["removed_from_source"]:
                db.execute("UPDATE links SET removed_from_source = 0, updated_at = ? WHERE id = ?", (now, link["id"]))
            still_present += 1
    imported, skipped, imported_ids = bulk_insert_links(db, bookmarks, source_name)
    db.commit()
    print(json.dumps({
        "status": "ok", "source": source_name, "in_source": len(bookmarks), "in_db": len(db_links),
        "still_present": still_present, "newly_removed": len(newly_removed),
        "already_flagged": already_flagged, "action": "deleted" if args.auto_delete else "flagged",
        "new_imports": imported, "removed_links": newly_removed[:20],
    }, indent=2))


def cmd_sources(args):
    db = get_db()
    sources = db.execute("SELECT * FROM sources ORDER BY name").fetchall()
    by_source = db.execute(
        """SELECT COALESCE(source, 'manual') as src, COUNT(*) as total,
                  SUM(CASE WHEN removed_from_source = 1 THEN 1 ELSE 0 END) as removed,
                  SUM(CASE WHEN is_read = 0 OR is_read IS NULL THEN 1 ELSE 0 END) as unread
           FROM links GROUP BY src ORDER BY total DESC"""
    ).fetchall()
    source_stats = {}
    for r in by_source:
        source_stats[r["src"]] = {"total": r["total"], "removed": r["removed"], "unread": r["unread"]}
    result = []
    seen = set()
    for s in sources:
        name = s["name"]
        seen.add(name)
        stats = source_stats.get(name, {"total": 0, "removed": 0, "unread": 0})
        result.append({"name": name, "path": s["path"], "last_synced_at": s["last_synced_at"],
                       "links": stats["total"], "removed": stats["removed"], "unread": stats["unread"]})
    for src, stats in source_stats.items():
        if src not in seen:
            result.append({"name": src, "path": None, "last_synced_at": None,
                          "links": stats["total"], "removed": stats["removed"], "unread": stats["unread"]})
    print(json.dumps(result, indent=2))


def _auto_detect_source(filepath):
    name = filepath.name.lower()
    if any(x in name for x in ("watch-history", "watch_history", "liked-video", "liked_video", "youtube")):
        return "youtube"
    if any(x in name for x in ("saved_posts", "saved_comments", "reddit")):
        return "reddit"
    if "pocket" in name or "ril_export" in name:
        return "pocket"
    if "instapaper" in name:
        return "instapaper"
    if "raindrop" in name:
        return "raindrop"
    if any(x in name for x in ("hackernews", "hacker_news", "hn_favorites", "hn-favorites")):
        return "hackernews"
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            peek = f.read(4000)
        if "getpocket.com" in peek or ">Pocket Export<" in peek:
            return "pocket"
        if "youtube.com/watch" in peek and ("titleUrl" in peek or "Watched " in peek):
            return "youtube"
        if "reddit.com" in peek and ("permalink" in peek or "subreddit" in peek):
            return "reddit"
        if "instapaper.com" in peek:
            return "instapaper"
        if "raindrop" in peek.lower():
            return "raindrop"
    except Exception:
        pass
    return None


def cmd_import(args):
    db = get_db()
    filepath = Path(args.file)
    if not filepath.exists():
        print(json.dumps({"error": f"File not found: {filepath}."}))
        return
    platform_parsers = {
        "youtube": ("youtube", _parse_youtube_takeout), "reddit": ("reddit", _parse_reddit_export),
        "pocket": ("pocket", _parse_pocket_export), "instapaper": ("instapaper", _parse_instapaper_export),
        "raindrop": ("raindrop", _parse_raindrop_export), "raindrop.io": ("raindrop", _parse_raindrop_export),
        "hackernews": ("hackernews", _parse_hackernews_export), "hn": ("hackernews", _parse_hackernews_export),
        "x": ("x", _parse_x_bookmarks), "twitter": ("x", _parse_x_bookmarks),
    }
    if args.source:
        source_key = args.source.lower()
        if source_key not in platform_parsers:
            print(json.dumps({"error": f"Unknown source '{args.source}'."}))
            return
        source_name, parser_fn = platform_parsers[source_key]
        bookmarks_result, used_path = parser_fn(filepath)
        if bookmarks_result is None:
            print(json.dumps({"error": used_path}))
            return
        if not bookmarks_result:
            print(json.dumps({"status": "empty", "message": f"No bookmarks found in {filepath.name}"}))
            return
        imported, skipped, imported_ids = bulk_insert_links(db, bookmarks_result, source_name)
        print(json.dumps({"status": "ok", "file": str(filepath), "source": source_name,
                          "found": len(bookmarks_result), "imported": imported,
                          "skipped_duplicates": skipped, "imported_ids": imported_ids}, indent=2))
        return

    source_name = _auto_detect_source(filepath)
    if source_name and source_name in platform_parsers:
        real_name, parser_fn = platform_parsers[source_name]
        bookmarks_result, used_path = parser_fn(filepath)
        if bookmarks_result and len(bookmarks_result) > 0:
            imported, skipped, imported_ids = bulk_insert_links(db, bookmarks_result, real_name)
            print(json.dumps({"status": "ok", "file": str(filepath), "source": real_name,
                              "auto_detected": True, "found": len(bookmarks_result), "imported": imported,
                              "skipped_duplicates": skipped, "imported_ids": imported_ids}, indent=2))
            return

    source_name = f"import:{filepath.name}"
    ext = filepath.suffix.lower()
    bookmarks = []
    if ext in (".html", ".htm"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        parser = BookmarkHTMLParser()
        parser.feed(content)
        bookmarks = parser.bookmarks
    elif ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "url" in item:
                    bookmarks.append({"url": item["url"], "title": item.get("title", ""),
                                     "summary": item.get("summary", ""), "tags": item.get("tags", [])})
        elif isinstance(data, dict):
            items = data.get("bookmarks", data.get("links", data.get("data", data.get("items", []))))
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and "url" in item:
                        bookmarks.append({"url": item["url"], "title": item.get("title", ""),
                                         "summary": item.get("summary", ""), "tags": item.get("tags", [])})
    elif ext == ".csv":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = ""
                title = ""
                tags = []
                for k, v in row.items():
                    kl = (k or "").lower().strip()
                    if kl in ("url", "link", "href", "uri"): url = v or ""
                    elif kl in ("title", "name"): title = v or ""
                    elif kl in ("tags", "labels", "categories"):
                        tags = [t.strip().lower() for t in (v or "").split(",") if t.strip()]
                if url:
                    bookmarks.append({"url": url, "title": title, "tags": tags})
    else:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(1000)
        if content.strip().startswith(("<", "<!DOCTYPE")):
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                full = f.read()
            parser = BookmarkHTMLParser()
            parser.feed(full)
            bookmarks = parser.bookmarks
        elif content.strip().startswith(("[", "{")):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "url" in item:
                        bookmarks.append({"url": item["url"], "title": item.get("title", ""), "tags": item.get("tags", [])})
        else:
            print(json.dumps({"error": f"Can't detect format for {filepath.name}."}))
            return
    if not bookmarks:
        print(json.dumps({"status": "empty", "message": f"No bookmarks found in {filepath.name}"}))
        return
    imported, skipped, imported_ids = bulk_insert_links(db, bookmarks, source_name)
    print(json.dumps({"status": "ok", "file": str(filepath), "source": source_name,
                      "found": len(bookmarks), "imported": imported,
                      "skipped_duplicates": skipped, "imported_ids": imported_ids}, indent=2))


def _detect_browsers():
    """Detect available browser bookmarks without importing. Returns list of (name, count, path)."""
    results = []
    parsers = [
        ("Chrome", _parse_chrome_bookmarks),
        ("Safari", _parse_safari_bookmarks),
        ("Firefox", _parse_firefox_bookmarks),
    ]
    for name, parser_fn in parsers:
        try:
            bookmarks, path = parser_fn()
            if bookmarks and len(bookmarks) > 0:
                results.append((name.lower(), len(bookmarks), path))
        except Exception:
            pass
    return results


def cmd_quickstart(args):
    """All-in-one first run: setup + detect browsers + import all + generate GUI."""
    db = get_db()

    total_imported = 0
    total_skipped = 0
    sources_imported = []

    parsers = [
        ("chrome", _parse_chrome_bookmarks),
        ("safari", _parse_safari_bookmarks),
        ("firefox", _parse_firefox_bookmarks),
    ]

    for source_name, parser_fn in parsers:
        try:
            bookmarks, path = parser_fn()
            if bookmarks and len(bookmarks) > 0:
                imported, skipped, ids = bulk_insert_links(db, bookmarks, source_name)
                total_imported += imported
                total_skipped += skipped
                sources_imported.append({
                    "name": source_name,
                    "found": len(bookmarks),
                    "imported": imported,
                    "skipped": skipped,
                    "path": path,
                })
        except Exception:
            pass

    total_links = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    tag_count = db.execute("SELECT COUNT(*) as n FROM tags").fetchone()["n"]
    unread = db.execute("SELECT COUNT(*) as n FROM links WHERE is_read = 0 OR is_read IS NULL").fetchone()["n"]

    result = {
        "status": "ok",
        "sources_imported": sources_imported,
        "total_imported": total_imported,
        "total_skipped": total_skipped,
        "total_links": total_links,
        "total_tags": tag_count,
        "unread": unread,
        "data_dir": str(DB_DIR),
    }

    # Generate GUI console if we have links
    if total_links > 0:
        try:
            class GuiArgs:
                no_open = True
            # Suppress gui output by capturing it
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            cmd_gui(GuiArgs())
            sys.stdout = old_stdout
            result["gui_path"] = str(DB_DIR / "console.html")
        except Exception:
            sys.stdout = old_stdout if 'old_stdout' in dir() else sys.stdout

    # Show milestones
    if total_imported > 0:
        milestones = track_activity(db, "save")
        if milestones:
            result["milestones"] = milestones

    print(json.dumps(result, indent=2))


def cmd_setup(args):
    DB_DIR.mkdir(parents=True, exist_ok=True)
    already_existed = DB_PATH.exists()
    db = get_db()

    # Detect available browser bookmarks
    browsers = _detect_browsers()

    if already_existed:
        total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
        result = {
            "status": "already_setup",
            "version": VERSION,
            "data_dir": str(DB_DIR),
            "total_links": total,
        }
        if browsers:
            result["browsers_detected"] = [
                {"name": n, "count": c, "path": p} for n, c, p in browsers
            ]
        # Also print human-readable
        print(f"🧠 {_bold('Link Brain')} v{VERSION}")
        print(f"   Data: {DB_DIR}")
        print(f"   Links: {total}")
        if browsers:
            print()
            print(f"   {_bold('Bookmarks available to import:')}")
            for name, count, _ in browsers:
                print(f"   - {name}: {_bold(str(count))} bookmarks")
            print(f"   Run: brain.py quickstart (imports everything automatically)")
        print(f"   {_green('Ready to go.')}")
    else:
        result = {
            "status": "created",
            "version": VERSION,
            "data_dir": str(DB_DIR),
        }
        print(f"🧠 {_bold('Link Brain')} v{VERSION}")
        print()
        print("Your personal knowledge base for links.")
        print()
        print(f"   {_green('Created')} {DB_DIR}")

        if browsers:
            total_bm = sum(c for _, c, _ in browsers)
            result["browsers_detected"] = [
                {"name": n, "count": c, "path": p} for n, c, p in browsers
            ]
            print()
            print(f"{_bold(f'Found {total_bm} bookmarks on your machine:')}")
            for name, count, _ in browsers:
                print(f"   {name}: {_bold(str(count))} bookmarks")
            print()
            print(f"  {_cyan('brain.py quickstart')}    Import everything and open the visual console")
            print(f"  {_cyan('brain.py scan chrome')}   Import just Chrome")
        else:
            print()
            print(f"{_bold('Get started:')}")
            print()
            print(f"  {_cyan('brain.py save <url> --auto')}    Save and auto-summarize a link")
            print(f"  {_cyan('brain.py scan chrome')}          Import browser bookmarks")

        print()
        print(f"Run {_cyan('brain.py help')} to see everything you can do.")


def cmd_feedback(args):
    """Save feedback locally and generate a GitHub issue URL."""
    import platform
    from urllib.parse import quote

    message = args.message
    label = "link-brain"
    extra_labels = []

    if args.bug:
        message = args.bug
        extra_labels.append("bug")
    elif args.idea:
        message = args.idea
        extra_labels.append("enhancement")

    # Gather system info
    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    db_size = "unknown"
    if DB_PATH.exists():
        size_bytes = DB_PATH.stat().st_size
        if size_bytes > 1_000_000:
            db_size = f"{size_bytes / 1_000_000:.1f} MB"
        else:
            db_size = f"{size_bytes / 1_000:.1f} KB"

    sys_info = (
        f"Link Brain v{VERSION}\n"
        f"Python {sys.version.split()[0]}\n"
        f"OS: {platform.system()} {platform.release()}\n"
        f"Links: {total}\n"
        f"DB size: {db_size}"
    )

    # Save to local log
    feedback_log = DB_DIR / "feedback.log"
    DB_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(feedback_log, "a", encoding="utf-8") as f:
        f.write(f"\n--- {timestamp} ---\n{message}\n{sys_info}\n")

    # Build GitHub issue URL
    title = message[:60].replace("\n", " ")
    body = f"{message}\n\n---\n```\n{sys_info}\n```"
    labels = ",".join([label] + extra_labels)
    url = (
        f"https://github.com/openclaw/openclaw/issues/new"
        f"?title={quote(title)}&body={quote(body)}&labels={quote(labels)}"
    )

    print()
    print(f"Thanks! Your feedback helps make Link Brain better. 🧠")
    print()
    print(f"Open an issue:")
    print(f"  {url}")
    print()


def cmd_debug(args):
    """Print system info for bug reports."""
    import platform

    db = get_db()
    total = db.execute("SELECT COUNT(*) as n FROM links").fetchone()["n"]
    db_size = "unknown"
    if DB_PATH.exists():
        size_bytes = DB_PATH.stat().st_size
        if size_bytes > 1_000_000:
            db_size = f"{size_bytes / 1_000_000:.1f} MB"
        else:
            db_size = f"{size_bytes / 1_000:.1f} KB"

    # Check install method
    install_via = "manual"
    skill_dir = Path(__file__).resolve().parent.parent
    if (skill_dir / ".clawhub").exists() or "clawhub" in str(skill_dir).lower():
        install_via = "clawhub"

    print()
    print(_bold("🧠 Link Brain Debug Info"))
    print()
    print(f"  Version:      {VERSION}")
    print(f"  Python:       {sys.version.split()[0]}")
    print(f"  OS:           {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  DB location:  {DB_PATH}")
    print(f"  DB size:      {db_size}")
    print(f"  Total links:  {total}")
    print(f"  Installed via: {install_via}")

    # Recent errors from feedback log
    feedback_log = DB_DIR / "feedback.log"
    if feedback_log.exists():
        content = feedback_log.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        recent = lines[-10:] if len(lines) > 10 else lines
        if recent:
            print()
            print(f"  Recent feedback log:")
            for line in recent:
                print(f"    {line}")
    print()


def cmd_gui(args):
    """Generate and open an interactive HTML console."""
    db = get_db()

    # Gather all data
    all_links = [link_to_dict(r) for r in db.execute("SELECT * FROM links ORDER BY saved_at DESC").fetchall()]
    total = len(all_links)
    read_count = sum(1 for l in all_links if l.get("is_read"))
    unread_count = total - read_count
    ratings = [l["rating"] for l in all_links if l.get("rating")]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    streak = _calculate_streak(db)

    # Collection span
    if all_links:
        dates = [l["saved_at"][:10] for l in all_links if l.get("saved_at")]
        if dates:
            earliest = min(dates)
            try:
                days_span = (datetime.now(timezone.utc).date() - datetime.strptime(earliest, "%Y-%m-%d").date()).days
            except Exception:
                days_span = 0
        else:
            days_span = 0
    else:
        days_span = 0

    # Tag counts
    tag_counter = Counter()
    for l in all_links:
        for t in l["tags"]:
            tag_counter[t.lower()] += 1
    top_tags = tag_counter.most_common(30)

    # Collections
    coll_rows = db.execute("""
        SELECT c.*, COUNT(cl.link_id) as link_count
        FROM collections c
        LEFT JOIN collection_links cl ON c.id = cl.collection_id
        GROUP BY c.id ORDER BY c.updated_at DESC
    """).fetchall()
    collections = []
    for c in coll_rows:
        cd = dict(c)
        links_in = db.execute("""
            SELECT l.id, l.title, l.url FROM links l
            JOIN collection_links cl ON l.id = cl.link_id
            WHERE cl.collection_id = ? ORDER BY cl.position
        """, (cd["id"],)).fetchall()
        cd["links"] = [dict(r) for r in links_in]
        collections.append(cd)

    # Reviews
    now = now_iso()
    overdue = db.execute("""
        SELECT l.*, r.next_review_at, r.interval_days, r.review_count
        FROM reviews r JOIN links l ON l.id = r.link_id
        WHERE r.next_review_at <= ? ORDER BY r.next_review_at ASC
    """, (now,)).fetchall()
    overdue_links = [link_to_dict(r) for r in overdue]
    overdue_count = len(overdue_links)

    # Timeline (last 30 days)
    timeline = []
    for i in range(30):
        d = (datetime.now(timezone.utc) - timedelta(days=29 - i)).strftime("%Y-%m-%d")
        row = db.execute("SELECT saves_count, reads_count FROM streaks WHERE date = ?", (d,)).fetchone()
        timeline.append({
            "date": d,
            "saves": row["saves_count"] if row else 0,
            "reads": row["reads_count"] if row else 0,
        })

    # Recent activity
    recent = all_links[:10]

    # Build graph data (top 100)
    graph_links = all_links[:100]
    graph_nodes = []
    tag_to_ids = {}
    for l in graph_links:
        graph_nodes.append({
            "id": l["id"], "title": l["title"][:60], "url": l["url"],
            "summary": (l.get("summary") or "")[:150],
            "tags": l["tags"], "rating": l.get("rating") or 0,
        })
        for t in l["tags"]:
            t = t.lower()
            tag_to_ids.setdefault(t, []).append(l["id"])

    graph_edges = []
    edge_set = set()
    for tag, ids in tag_to_ids.items():
        for i in range(len(ids)):
            for j in range(i + 1, min(len(ids), i + 8)):
                a, b = min(ids[i], ids[j]), max(ids[i], ids[j])
                if (a, b) not in edge_set:
                    edge_set.add((a, b))
                    graph_edges.append({"source": a, "target": b})

    # Tag colors
    sorted_tags = sorted(set(t.lower() for l in all_links for t in l["tags"]))
    palette = [
        "#e74c3c", "#3498db", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e67e22", "#e91e63", "#00bcd4", "#8bc34a",
        "#ff5722", "#607d8b", "#795548", "#cddc39", "#ff9800",
    ]
    tag_colors = {t: palette[i % len(palette)] for i, t in enumerate(sorted_tags)}

    data = {
        "version": VERSION,
        "total": total,
        "readCount": read_count,
        "unreadCount": unread_count,
        "avgRating": avg_rating,
        "streak": streak,
        "daysSpan": days_span,
        "topTags": [{"name": t, "count": c} for t, c in top_tags],
        "tagColors": tag_colors,
        "links": all_links,
        "collections": collections,
        "overdueReviews": overdue_links[:5],
        "overdueCount": overdue_count,
        "timeline": timeline,
        "recent": recent,
        "graphNodes": graph_nodes,
        "graphEdges": graph_edges,
    }

    data_json = json.dumps(data, default=str)

    html = _generate_gui_html(data_json)

    output_path = DB_DIR / "console.html"
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    if not getattr(args, "no_open", False):
        webbrowser.open(f"file://{output_path}")

    print(json.dumps({"status": "ok", "path": str(output_path), "links": total}))


def _generate_gui_html(data_json):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Link Brain Console</title>
<style>
:root[data-theme="dark"] {{
  --bg: #0a0a0a; --bg-card: #141414; --bg-card-hover: #1a1a1a;
  --bg-input: #1a1a1a; --border: #222; --border-hover: #333;
  --text: #e8e8e8; --text-dim: #888; --text-muted: #555;
  --accent: #6366f1; --accent-glow: rgba(99,102,241,0.15);
  --green: #22c55e; --amber: #f59e0b; --red: #ef4444;
  --tag-bg: rgba(99,102,241,0.12); --tag-text: #a5b4fc;
  --shadow: 0 2px 16px rgba(0,0,0,0.4);
}}
:root[data-theme="light"] {{
  --bg: #f8f8f8; --bg-card: #fff; --bg-card-hover: #f0f0ff;
  --bg-input: #fff; --border: #e0e0e0; --border-hover: #ccc;
  --text: #1a1a1a; --text-dim: #666; --text-muted: #999;
  --accent: #4f46e5; --accent-glow: rgba(79,70,229,0.08);
  --green: #16a34a; --amber: #d97706; --red: #dc2626;
  --tag-bg: rgba(79,70,229,0.08); --tag-text: #4f46e5;
  --shadow: 0 2px 12px rgba(0,0,0,0.08);
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  background: var(--bg); color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  line-height: 1.6; -webkit-font-smoothing: antialiased;
}}
h1, h2, h3 {{ font-family: "SF Mono", "Fira Code", "Cascadia Code", "JetBrains Mono", monospace; font-weight: 600; }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 0 24px; }}

/* Animations */
@keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: translateY(0); }} }}
.fade-in {{ animation: fadeUp 0.4s ease-out both; }}
.fade-in:nth-child(2) {{ animation-delay: 0.05s; }}
.fade-in:nth-child(3) {{ animation-delay: 0.1s; }}
.fade-in:nth-child(4) {{ animation-delay: 0.15s; }}
.fade-in:nth-child(5) {{ animation-delay: 0.2s; }}
.fade-in:nth-child(6) {{ animation-delay: 0.25s; }}

/* Header */
.header {{
  padding: 48px 0 32px; display: flex; align-items: center;
  justify-content: space-between; flex-wrap: wrap; gap: 16px;
}}
.header-left {{ display: flex; align-items: center; gap: 16px; }}
.header h1 {{ font-size: 28px; letter-spacing: -0.5px; }}
.version-badge {{
  background: var(--accent-glow); color: var(--accent); font-size: 12px;
  padding: 3px 10px; border-radius: 20px; font-weight: 500;
  font-family: "SF Mono", monospace;
}}
.header-right {{ display: flex; align-items: center; gap: 16px; }}
.total-count {{ font-size: 14px; color: var(--text-dim); }}
.total-count strong {{ font-size: 20px; color: var(--text); }}
.theme-toggle {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 6px 10px; cursor: pointer; font-size: 18px; transition: all 0.2s;
  color: var(--text);
}}
.theme-toggle:hover {{ border-color: var(--accent); }}

/* Stats Grid */
.stats-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px; margin-bottom: 40px;
}}
.stat-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 20px; transition: all 0.2s;
}}
.stat-card:hover {{ border-color: var(--border-hover); background: var(--bg-card-hover); transform: translateY(-1px); }}
.stat-label {{ font-size: 12px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
.stat-value {{ font-size: 32px; font-weight: 700; font-family: "SF Mono", monospace; }}
.stat-sub {{ font-size: 12px; color: var(--text-dim); margin-top: 4px; }}
.progress-bar {{ height: 4px; background: var(--border); border-radius: 2px; margin-top: 8px; overflow: hidden; }}
.progress-fill {{ height: 100%; background: var(--green); border-radius: 2px; transition: width 0.6s ease; }}
.star {{ color: var(--amber); }}
.tag-pill {{
  display: inline-block; background: var(--tag-bg); color: var(--tag-text);
  padding: 2px 10px; border-radius: 20px; font-size: 12px; margin: 2px;
  font-weight: 500;
}}

/* Section */
.section {{ margin-bottom: 48px; }}
.section-title {{
  font-size: 18px; margin-bottom: 20px; display: flex; align-items: center; gap: 10px;
}}
.section-title .emoji {{ font-size: 20px; }}

/* Search */
.search-wrap {{
  position: sticky; top: 0; z-index: 20; padding: 16px 0;
  background: var(--bg); margin-bottom: 24px;
}}
.search-input {{
  width: 100%; padding: 14px 20px; font-size: 16px;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  color: var(--text); outline: none; transition: all 0.2s;
  font-family: inherit;
}}
.search-input:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }}
.search-input::placeholder {{ color: var(--text-muted); }}
.search-results {{ display: none; }}
.search-results.active {{ display: block; }}

/* Link Card */
.link-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px 20px; margin-bottom: 8px; transition: all 0.2s; cursor: pointer;
}}
.link-card:hover {{ border-color: var(--border-hover); background: var(--bg-card-hover); }}
.link-title {{ font-size: 15px; font-weight: 600; margin-bottom: 4px; }}
.link-title a {{ color: var(--text); text-decoration: none; }}
.link-title a:hover {{ color: var(--accent); }}
.link-summary {{ font-size: 13px; color: var(--text-dim); margin-bottom: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.link-meta {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-size: 12px; }}
.badge {{
  display: inline-block; padding: 1px 8px; border-radius: 20px; font-size: 11px; font-weight: 500;
}}
.badge-read {{ background: rgba(34,197,94,0.12); color: var(--green); }}
.badge-unread {{ background: rgba(239,68,68,0.12); color: var(--red); }}
.link-date {{ color: var(--text-muted); font-size: 11px; }}

/* Tag Cloud */
.tag-cloud {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; justify-content: center; padding: 20px 0; }}
.tag-cloud-item {{
  display: inline-block; padding: 4px 14px; border-radius: 20px; cursor: pointer;
  transition: all 0.2s; border: 1px solid transparent; font-weight: 500;
}}
.tag-cloud-item:hover {{ transform: scale(1.08); border-color: var(--accent); }}
.tag-cloud-item.active {{ border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-glow); }}

/* Graph */
.graph-container {{ position: relative; border-radius: 12px; overflow: hidden; border: 1px solid var(--border); background: #050508; }}
.graph-container canvas {{ display: block; width: 100%; cursor: grab; }}
.graph-container canvas:active {{ cursor: grabbing; }}
#graph-tooltip {{
  position: absolute; display: none; background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 10px 14px; max-width: 280px; pointer-events: none;
  box-shadow: var(--shadow); z-index: 10; font-size: 12px;
}}
#graph-tooltip .gtt {{ font-weight: 600; font-size: 13px; margin-bottom: 3px; color: var(--text); }}
#graph-tooltip .gts {{ color: var(--text-dim); font-size: 11px; }}

/* Collections */
.coll-card {{
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px;
  padding: 16px 20px; margin-bottom: 8px; cursor: pointer; transition: all 0.2s;
}}
.coll-card:hover {{ border-color: var(--border-hover); }}
.coll-header {{ display: flex; justify-content: space-between; align-items: center; }}
.coll-name {{ font-weight: 600; font-size: 15px; }}
.coll-count {{ background: var(--accent-glow); color: var(--accent); padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 500; }}
.coll-links {{ display: none; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border); }}
.coll-links.open {{ display: block; }}
.coll-link {{ font-size: 13px; padding: 4px 0; }}
.coll-link a {{ color: var(--accent); text-decoration: none; }}
.coll-link a:hover {{ text-decoration: underline; }}

/* Timeline */
.timeline {{ display: flex; align-items: flex-end; gap: 3px; height: 120px; padding: 10px 0; }}
.timeline-bar {{ flex: 1; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: 1px; min-width: 0; }}
.tbar {{ border-radius: 3px 3px 0 0; min-height: 2px; width: 100%; transition: height 0.3s; }}
.tbar-save {{ background: var(--accent); }}
.tbar-read {{ background: var(--green); }}
.timeline-label {{ font-size: 9px; color: var(--text-muted); margin-top: 4px; writing-mode: vertical-lr; text-orientation: mixed; height: 30px; overflow: hidden; }}
.timeline-legend {{ display: flex; gap: 16px; font-size: 12px; color: var(--text-dim); margin-top: 8px; }}
.timeline-legend span::before {{ content: ""; display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }}
.tl-saves::before {{ background: var(--accent); }}
.tl-reads::before {{ background: var(--green); }}

/* Empty State */
.empty-state {{
  text-align: center; padding: 40px 20px; color: var(--text-dim); font-size: 14px;
}}
.empty-state .emoji-big {{ font-size: 36px; margin-bottom: 12px; }}
.empty-state code {{ background: var(--bg-card); padding: 2px 8px; border-radius: 4px; font-size: 13px; }}

/* Footer */
.footer {{
  text-align: center; padding: 48px 0 32px; color: var(--text-muted); font-size: 13px;
  border-top: 1px solid var(--border); margin-top: 32px;
}}
.footer a {{ color: var(--accent); text-decoration: none; }}

/* Responsive */
@media (max-width: 768px) {{
  .header {{ padding: 24px 0 20px; }}
  .header h1 {{ font-size: 22px; }}
  .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
  .stat-value {{ font-size: 24px; }}
}}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header fade-in">
    <div class="header-left">
      <h1>&#x1f9e0; Link Brain</h1>
      <span class="version-badge" id="vbadge"></span>
    </div>
    <div class="header-right">
      <div class="total-count"><strong id="total-count"></strong> links</div>
      <button class="theme-toggle" id="theme-toggle" title="Toggle theme">&#x1f319;</button>
    </div>
  </div>

  <!-- Stats -->
  <div class="stats-grid" id="stats-grid"></div>

  <!-- Search -->
  <div class="section">
    <div class="search-wrap">
      <input class="search-input" id="search" type="text" placeholder="Search links... title, tags, URL, summary" autocomplete="off">
    </div>
    <div class="search-results" id="search-results"></div>
  </div>

  <!-- Tag Cloud -->
  <div class="section fade-in" id="tag-section">
    <h2 class="section-title"><span class="emoji">&#x1f3f7;</span> Tags</h2>
    <div class="tag-cloud" id="tag-cloud"></div>
    <div id="tag-filtered-links"></div>
  </div>

  <!-- Knowledge Graph -->
  <div class="section fade-in" id="graph-section">
    <h2 class="section-title"><span class="emoji">&#x1f578;</span> Knowledge Graph</h2>
    <div class="graph-container">
      <canvas id="graph" height="500"></canvas>
      <div id="graph-tooltip"><div class="gtt"></div><div class="gts"></div></div>
    </div>
  </div>

  <!-- Collections -->
  <div class="section fade-in" id="coll-section">
    <h2 class="section-title"><span class="emoji">&#x1f4da;</span> Collections</h2>
    <div id="coll-list"></div>
  </div>

  <!-- Review Queue -->
  <div class="section fade-in" id="review-section">
    <h2 class="section-title"><span class="emoji">&#x1f504;</span> Review Queue</h2>
    <div id="review-list"></div>
  </div>

  <!-- Timeline -->
  <div class="section fade-in" id="timeline-section">
    <h2 class="section-title"><span class="emoji">&#x1f4c8;</span> Reading Timeline <span style="font-size:12px;color:var(--text-dim);font-weight:400;font-family:inherit;">last 30 days</span></h2>
    <div class="timeline" id="timeline"></div>
    <div class="timeline-legend"><span class="tl-saves">Saved</span><span class="tl-reads">Read</span></div>
  </div>

  <!-- Recent -->
  <div class="section fade-in" id="recent-section">
    <h2 class="section-title"><span class="emoji">&#x1f570;</span> Recent Activity</h2>
    <div id="recent-list"></div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <div>Made with &#x1f9e0; by <a href="https://github.com/jakes420" target="_blank">@jakes420</a></div>
    <div style="margin-top:4px;"><code>brain.py feedback</code> to share ideas</div>
    <div style="margin-top:4px;" id="footer-info"></div>
  </div>
</div>

<script>
const DATA = ''' + data_json + ''';

// Theme toggle
const html = document.documentElement;
const toggle = document.getElementById('theme-toggle');
const savedTheme = localStorage.getItem('lb-theme') || 'dark';
html.dataset.theme = savedTheme;
toggle.textContent = savedTheme === 'dark' ? '\\u2600' : '\\uD83C\\uDF19';
toggle.addEventListener('click', () => {
  const t = html.dataset.theme === 'dark' ? 'light' : 'dark';
  html.dataset.theme = t;
  localStorage.setItem('lb-theme', t);
  toggle.textContent = t === 'dark' ? '\\u2600' : '\\uD83C\\uDF19';
});

// Helpers
function esc(s) { const d = document.createElement('div'); d.textContent = s || ''; return d.innerHTML; }
function stars(n) { return n > 0 ? '\\u2B50'.repeat(Math.min(n, 5)) : ''; }
function relDate(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  const diff = Math.floor((now - d) / 86400000);
  if (diff === 0) return 'today';
  if (diff === 1) return 'yesterday';
  if (diff < 7) return diff + 'd ago';
  if (diff < 30) return Math.floor(diff/7) + 'w ago';
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
function tagPill(t, clickable) {
  const col = DATA.tagColors[t.toLowerCase()] || '#6366f1';
  return '<span class="tag-pill" style="background:' + col + '18;color:' + col + '"' +
    (clickable ? ' onclick="filterByTag(\\''+esc(t)+'\\')"' : '') + '>' + esc(t) + '</span>';
}
function linkCard(l) {
  const badge = l.is_read ? '<span class="badge badge-read">read</span>' : '<span class="badge badge-unread">unread</span>';
  const tagsHtml = (l.tags || []).map(t => tagPill(t, false)).join('');
  const ratingHtml = l.rating ? '<span class="star">' + stars(l.rating) + '</span>' : '';
  return '<div class="link-card" onclick="window.open(\\''+esc(l.url)+'\\',\\'_blank\\')">' +
    '<div class="link-title"><a href="'+esc(l.url)+'" target="_blank" onclick="event.stopPropagation()">'+esc(l.title)+'</a></div>' +
    (l.summary ? '<div class="link-summary">'+esc(l.summary)+'</div>' : '') +
    '<div class="link-meta">'+badge+' '+ratingHtml+' '+tagsHtml+' <span class="link-date">'+relDate(l.saved_at)+'</span></div></div>';
}

// Header
document.getElementById('vbadge').textContent = 'v' + DATA.version;
document.getElementById('total-count').textContent = DATA.total;
document.getElementById('footer-info').textContent = 'v' + DATA.version + ' \\u00B7 ' + DATA.total + ' links';

// Stats
const sg = document.getElementById('stats-grid');
const readPct = DATA.total > 0 ? Math.round(DATA.readCount / DATA.total * 100) : 0;
const statsCards = [
  { label: 'Total Links', value: DATA.total, sub: '' },
  { label: 'Read / Unread', value: DATA.readCount + ' / ' + DATA.unreadCount, sub: '<div class="progress-bar"><div class="progress-fill" style="width:'+readPct+'%"></div></div>' },
  { label: 'Current Streak', value: DATA.streak > 0 ? DATA.streak + ' \\uD83D\\uDD25' : '0', sub: DATA.streak > 0 ? 'days in a row' : 'Start a streak by reading something today' },
  { label: 'Avg Rating', value: DATA.avgRating > 0 ? stars(Math.round(DATA.avgRating)) : '\\u2014', sub: DATA.avgRating > 0 ? DATA.avgRating + ' / 5' : 'No ratings yet' },
  { label: 'Collecting For', value: DATA.daysSpan, sub: DATA.daysSpan === 1 ? 'day' : 'days' },
  { label: 'Top Tags', value: '', sub: DATA.topTags.slice(0,3).map(t => tagPill(t.name, false)).join(' ') || 'No tags yet' },
];
sg.innerHTML = statsCards.map(s =>
  '<div class="stat-card fade-in"><div class="stat-label">'+s.label+'</div>' +
  '<div class="stat-value">'+s.value+'</div>' +
  '<div class="stat-sub">'+s.sub+'</div></div>'
).join('');

// Search
const searchInput = document.getElementById('search');
const searchResults = document.getElementById('search-results');
searchInput.addEventListener('input', () => {
  const q = searchInput.value.toLowerCase().trim();
  if (!q) { searchResults.className = 'search-results'; searchResults.innerHTML = ''; return; }
  const matches = DATA.links.filter(l =>
    (l.title||'').toLowerCase().includes(q) ||
    (l.summary||'').toLowerCase().includes(q) ||
    (l.url||'').toLowerCase().includes(q) ||
    (l.tags||[]).some(t => t.toLowerCase().includes(q))
  ).slice(0, 30);
  searchResults.className = 'search-results active';
  searchResults.innerHTML = matches.length ? matches.map(linkCard).join('') :
    '<div class="empty-state">No matches found</div>';
});

// Tag Cloud
const tc = document.getElementById('tag-cloud');
if (DATA.topTags.length === 0) {
  tc.innerHTML = '<div class="empty-state"><div class="emoji-big">\\uD83C\\uDFF7\\uFE0F</div>No tags yet. Add tags when you save links.</div>';
} else {
  const maxCount = Math.max(...DATA.topTags.map(t => t.count));
  tc.innerHTML = DATA.topTags.map(t => {
    const size = Math.max(12, Math.min(28, 12 + (t.count / maxCount) * 16));
    const col = DATA.tagColors[t.name] || '#6366f1';
    return '<span class="tag-cloud-item" style="font-size:'+size+'px;background:'+col+'14;color:'+col+'" onclick="filterByTag(\\''+esc(t.name)+'\\')" data-tag="'+esc(t.name)+'">'+esc(t.name)+' <small style="opacity:0.5">'+t.count+'</small></span>';
  }).join('');
}

let activeTag = null;
function filterByTag(tag) {
  const fl = document.getElementById('tag-filtered-links');
  if (activeTag === tag) {
    activeTag = null;
    fl.innerHTML = '';
    document.querySelectorAll('.tag-cloud-item').forEach(e => e.classList.remove('active'));
    return;
  }
  activeTag = tag;
  document.querySelectorAll('.tag-cloud-item').forEach(e => e.classList.toggle('active', e.dataset.tag === tag));
  const matches = DATA.links.filter(l => (l.tags||[]).some(t => t.toLowerCase() === tag.toLowerCase())).slice(0, 50);
  fl.innerHTML = matches.map(linkCard).join('');
}

// Knowledge Graph
const graphCanvas = document.getElementById('graph');
if (DATA.graphNodes.length === 0) {
  document.getElementById('graph-section').innerHTML = '<h2 class="section-title"><span class="emoji">\\uD83D\\uDD78</span> Knowledge Graph</h2><div class="empty-state"><div class="emoji-big">\\uD83D\\uDD78\\uFE0F</div>Save some links to see your knowledge graph</div>';
} else {
  const gctx = graphCanvas.getContext('2d');
  const gw = graphCanvas.parentElement.clientWidth;
  const gh = 500;
  graphCanvas.width = gw * (window.devicePixelRatio || 1);
  graphCanvas.height = gh * (window.devicePixelRatio || 1);
  graphCanvas.style.height = gh + 'px';
  gctx.scale(window.devicePixelRatio || 1, window.devicePixelRatio || 1);

  const gNodes = DATA.graphNodes.map((n, i) => ({
    ...n, x: gw/2 + (Math.random()-0.5)*gw*0.6, y: gh/2 + (Math.random()-0.5)*gh*0.6,
    vx: 0, vy: 0, r: Math.max(4, Math.min(12, 4 + (n.rating||0)*1.6)),
    color: DATA.tagColors[(n.tags[0]||'').toLowerCase()] || '#666',
  }));
  const gIdMap = {}; gNodes.forEach((n,i) => gIdMap[n.id] = i);
  const gEdges = DATA.graphEdges.filter(e => gIdMap[e.source] !== undefined && gIdMap[e.target] !== undefined);

  let gPanX = 0, gPanY = 0, gZoom = 1, gDrag = null, gPanning = false, gLast = null;

  function gScreen(sx, sy) { return [(sx - gPanX)/gZoom, (sy - gPanY)/gZoom]; }
  function gFindNode(sx, sy) {
    const [wx,wy] = gScreen(sx, sy);
    for (let i = gNodes.length-1; i >= 0; i--) {
      const n = gNodes[i], dx = wx-n.x, dy = wy-n.y;
      if (dx*dx+dy*dy < (n.r/gZoom+4)*(n.r/gZoom+4)) return n;
    }
    return null;
  }

  graphCanvas.addEventListener('wheel', e => {
    e.preventDefault();
    const f = e.deltaY > 0 ? 0.92 : 1.08;
    const r = graphCanvas.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    gPanX = mx - (mx - gPanX)*f; gPanY = my - (my - gPanY)*f; gZoom *= f;
  }, {passive: false});

  graphCanvas.addEventListener('mousedown', e => {
    const r = graphCanvas.getBoundingClientRect();
    const n = gFindNode(e.clientX - r.left, e.clientY - r.top);
    if (n) { gDrag = n; gDrag._fixed = true; } else gPanning = true;
    gLast = [e.clientX, e.clientY];
  });
  graphCanvas.addEventListener('mousemove', e => {
    const r = graphCanvas.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    if (gPanning && gLast) { gPanX += e.clientX-gLast[0]; gPanY += e.clientY-gLast[1]; gLast=[e.clientX,e.clientY]; }
    else if (gDrag) { const [wx,wy] = gScreen(mx,my); gDrag.x=wx; gDrag.y=wy; gLast=[e.clientX,e.clientY]; }
    else {
      const n = gFindNode(mx, my);
      const tt = document.getElementById('graph-tooltip');
      if (n) {
        tt.style.display = 'block'; tt.style.left = (mx+15)+'px'; tt.style.top = (my+15)+'px';
        tt.querySelector('.gtt').textContent = n.title;
        tt.querySelector('.gts').textContent = n.summary || '';
      } else tt.style.display = 'none';
    }
  });
  graphCanvas.addEventListener('mouseup', () => { gPanning=false; if(gDrag){gDrag._fixed=false; gDrag=null;} gLast=null; });
  graphCanvas.addEventListener('click', e => {
    const r = graphCanvas.getBoundingClientRect();
    const n = gFindNode(e.clientX-r.left, e.clientY-r.top);
    if (n && n.url) window.open(n.url, '_blank');
  });

  function gSim() {
    gNodes.forEach(n => { if(n._fixed) return; n.vx+=(gw/2-n.x)*0.0005; n.vy+=(gh/2-n.y)*0.0005; });
    for (let i=0;i<gNodes.length;i++) { if(gNodes[i]._fixed) continue;
      for (let j=i+1;j<gNodes.length;j++) {
        const dx=gNodes[i].x-gNodes[j].x, dy=gNodes[i].y-gNodes[j].y, d2=dx*dx+dy*dy+1, f=600/d2;
        gNodes[i].vx+=dx*f; gNodes[i].vy+=dy*f;
        if(!gNodes[j]._fixed){gNodes[j].vx-=dx*f; gNodes[j].vy-=dy*f;}
    }}
    gEdges.forEach(e => {
      const s=gNodes[gIdMap[e.source]], t=gNodes[gIdMap[e.target]];
      const dx=t.x-s.x, dy=t.y-s.y, d=Math.sqrt(dx*dx+dy*dy)+1, f=(d-80)*0.004;
      if(!s._fixed){s.vx+=dx/d*f; s.vy+=dy/d*f;}
      if(!t._fixed){t.vx-=dx/d*f; t.vy-=dy/d*f;}
    });
    gNodes.forEach(n => { if(n._fixed) return; n.vx*=0.6; n.vy*=0.6; n.x+=n.vx; n.y+=n.vy; });
  }
  function gDraw() {
    gctx.clearRect(0, 0, gw, gh); gctx.save(); gctx.translate(gPanX, gPanY); gctx.scale(gZoom, gZoom);
    gctx.strokeStyle = 'rgba(255,255,255,0.05)'; gctx.lineWidth = 0.5/gZoom;
    gEdges.forEach(e => { const s=gNodes[gIdMap[e.source]], t=gNodes[gIdMap[e.target]]; gctx.beginPath(); gctx.moveTo(s.x,s.y); gctx.lineTo(t.x,t.y); gctx.stroke(); });
    gNodes.forEach(n => { gctx.beginPath(); gctx.arc(n.x, n.y, n.r, 0, Math.PI*2); gctx.fillStyle=n.color; gctx.globalAlpha=0.85; gctx.fill(); gctx.globalAlpha=1; });
    gctx.restore();
  }
  function gLoop() { gSim(); gDraw(); requestAnimationFrame(gLoop); }
  gLoop();
}

// Collections
const collList = document.getElementById('coll-list');
if (DATA.collections.length === 0) {
  collList.innerHTML = '<div class="empty-state"><div class="emoji-big">\\uD83D\\uDCDA</div>No collections yet. Create one:<br><code>brain.py collection create "My List"</code></div>';
} else {
  collList.innerHTML = DATA.collections.map((c, i) => {
    const linksHtml = c.links.map(l => '<div class="coll-link"><a href="'+esc(l.url)+'" target="_blank">'+esc(l.title)+'</a></div>').join('');
    return '<div class="coll-card" onclick="this.querySelector(\\'.coll-links\\').classList.toggle(\\'open\\')">' +
      '<div class="coll-header"><span class="coll-name">'+esc(c.name)+'</span><span class="coll-count">'+c.link_count+'</span></div>' +
      (c.description ? '<div style="font-size:12px;color:var(--text-dim);margin-top:4px">'+esc(c.description)+'</div>' : '') +
      '<div class="coll-links">'+(linksHtml || '<div style="color:var(--text-muted);font-size:12px">Empty collection</div>')+'</div></div>';
  }).join('');
}

// Reviews
const revList = document.getElementById('review-list');
if (DATA.overdueCount === 0) {
  revList.innerHTML = '<div class="empty-state"><div class="emoji-big">\\uD83C\\uDF89</div>All caught up! Nothing to review right now.</div>';
} else {
  revList.innerHTML = '<div style="margin-bottom:12px;color:var(--text-dim);font-size:13px">'+DATA.overdueCount+' overdue for review</div>' +
    DATA.overdueReviews.map(linkCard).join('');
}

// Timeline
const tl = document.getElementById('timeline');
const maxTl = Math.max(1, ...DATA.timeline.map(d => d.saves + d.reads));
tl.innerHTML = DATA.timeline.map(d => {
  const sh = Math.max(2, (d.saves/maxTl)*80);
  const rh = Math.max(2, (d.reads/maxTl)*80);
  const label = d.date.slice(5);
  return '<div class="timeline-bar" title="'+d.date+': '+d.saves+' saved, '+d.reads+' read">' +
    '<div class="tbar tbar-read" style="height:'+rh+'px"></div>' +
    '<div class="tbar tbar-save" style="height:'+sh+'px"></div>' +
    '</div>';
}).join('');

// Recent
const recentList = document.getElementById('recent-list');
if (DATA.recent.length === 0) {
  recentList.innerHTML = '<div class="empty-state"><div class="emoji-big">\\uD83E\\uDDE0</div>Your brain is empty.<br>Run <code>brain.py quickstart</code> to import your browser bookmarks instantly.<br>Or save a link: <code>brain.py save &lt;url&gt; --auto</code></div>';
} else {
  recentList.innerHTML = DATA.recent.map(linkCard).join('');
}
</script>
</body>
</html>'''


def cmd_help(args):
    print(f"🧠 {_bold('Link Brain')} v{VERSION}")
    print()
    print(f"{_bold('🚀 Get started')}")
    print(f"  {_cyan('quickstart')}               Auto-import all browser bookmarks + open GUI")
    print(f"  {_cyan('setup')}                    First-time setup (detects your browsers)")
    print()
    print(f"{_bold('📥 Save stuff')}")
    print(f"  {_cyan('save')} <url>              Save a URL (add --title, --summary, --tags)")
    print(f"  {_cyan('save')} <url> --auto       Auto-fetch, summarize, and tag (no LLM needed)")
    print(f"  {_cyan('auto-save')} <url>         Shortcut for save --auto")
    print(f"  {_cyan('scan')} <source>           Pull bookmarks from chrome, safari, or firefox")
    print(f"  {_cyan('import')} <file>           Import from Pocket, YouTube, Reddit, and more")
    print()
    print(f"{_bold('🔍 Find stuff')}")
    print(f"  {_cyan('search')} <query>          Full-text search (supports natural language)")
    print(f"  {_cyan('tags')} [name]             List all tags, or show links for a tag")
    print(f"  {_cyan('get')} <id>                Full details for a link")
    print(f"  {_cyan('related')} <id>            Find links with similar tags")
    print(f"  {_cyan('suggest-tags')} <url>      Get tag suggestions based on your patterns")
    print()
    print(f"{_bold('✨ Discover stuff')}")
    print(f"  {_cyan('digest')}                  Get a batch of links to review")
    print(f"  {_cyan('recommend')}               Surface links based on your top tags")
    print(f"  {_cyan('gems')}                    Your highest-rated links and hidden gems")
    print(f"  {_cyan('random')}                  Pull a random link from your backlog")
    print(f"  {_cyan('graph')}                   Interactive knowledge graph visualization")
    print(f"  {_cyan('gui')}                     Open the visual console in your browser")
    print()
    print(f"{_bold('📖 Track your reading')}")
    print(f"  {_cyan('read')} <id>               Mark as read")
    print(f"  {_cyan('unread')}                  Show unread links")
    print(f"  {_cyan('rate')} <id> <1-5>         Rate a link")
    print(f"  {_cyan('streak')}                  Your current streak and activity")
    print(f"  {_cyan('insights')}                Reading personality and analytics")
    print(f"  {_cyan('weekly')}                  Weekly summary (WhatsApp-ready)")
    print()
    print(f"{_bold('📚 Collections')}")
    print(f"  {_cyan('collection create')} <name>           Create a reading list")
    print(f"  {_cyan('collection add')} <name> <id>         Add link to collection")
    print(f"  {_cyan('collection remove')} <name> <id>      Remove link from collection")
    print(f"  {_cyan('collection list')}                    List all collections")
    print(f"  {_cyan('collection show')} <name>             Show links in a collection")
    print(f"  {_cyan('collection export')} <name>           Export as markdown")
    print(f"  {_cyan('collection export')} <name> --html    Export as HTML page")
    print()
    print(f"{_bold('🔄 Spaced Repetition')}")
    print(f"  {_cyan('review')}                  Show next link due for review")
    print(f"  {_cyan('review done')} <id>        Mark reviewed (advances interval)")
    print(f"  {_cyan('review skip')} <id>        Skip for now")
    print(f"  {_cyan('review reset')} <id>       Reset interval to 1 day")
    print(f"  {_cyan('review stats')}            Review queue stats")
    print()
    print(f"{_bold('🔧 Manage')}")
    print(f"  {_cyan('recent')}                  Last saved links")
    print(f"  {_cyan('delete')} <id>             Remove a link")
    print(f"  {_cyan('stats')}                   Collection overview")
    print(f"  {_cyan('export')}                  Dump everything as JSON")
    print(f"  {_cyan('sources')}                 Connected sources and sync status")
    print(f"  {_cyan('sync')} <source>           Check for removed bookmarks")
    print(f"  {_cyan('setup')}                   First-time setup")
    print()
    print(f"{_bold('💬 Feedback')}")
    print(f"  {_cyan('feedback')} <message>       Send feedback or suggestions")
    print(f"  {_cyan('feedback')} --bug <msg>     Report a bug")
    print(f"  {_cyan('feedback')} --idea <msg>    Suggest a feature")
    print(f"  {_cyan('debug')}                    System info for bug reports")


def main():
    parser = argparse.ArgumentParser(
        description=f"Link Brain v{VERSION} - Personal knowledge base for saved links.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("setup")
    sub.add_parser("quickstart")
    sub.add_parser("help")

    # save
    p_save = sub.add_parser("save")
    p_save.add_argument("url")
    p_save.add_argument("--title", "-t")
    p_save.add_argument("--summary", "-s")
    p_save.add_argument("--tags", "-g")
    p_save.add_argument("--auto", "-a", action="store_true", help="Auto-fetch and generate metadata")

    # auto-save
    p_autosave = sub.add_parser("auto-save")
    p_autosave.add_argument("url")

    # search
    p_search = sub.add_parser("search")
    p_search.add_argument("query")
    p_search.add_argument("--limit", "-n", type=int, default=20)

    # graph
    p_graph = sub.add_parser("graph")
    p_graph.add_argument("--open", "-o", action="store_true", help="Open in default browser")

    # gui
    p_gui = sub.add_parser("gui")
    p_gui.add_argument("--no-open", action="store_true", help="Generate without opening")

    # collection
    p_coll = sub.add_parser("collection")
    coll_sub = p_coll.add_subparsers(dest="collection_command")
    p_cc = coll_sub.add_parser("create")
    p_cc.add_argument("name")
    p_cc.add_argument("--description", "-d", default="")
    p_ca = coll_sub.add_parser("add")
    p_ca.add_argument("collection")
    p_ca.add_argument("link_id", type=int)
    p_cr = coll_sub.add_parser("remove")
    p_cr.add_argument("collection")
    p_cr.add_argument("link_id", type=int)
    coll_sub.add_parser("list")
    p_cs = coll_sub.add_parser("show")
    p_cs.add_argument("name")
    p_ce = coll_sub.add_parser("export")
    p_ce.add_argument("name")
    p_ce.add_argument("--html", action="store_true")

    # review
    p_rev = sub.add_parser("review")
    rev_sub = p_rev.add_subparsers(dest="review_command")
    p_rd = rev_sub.add_parser("done")
    p_rd.add_argument("id", type=int)
    p_rs = rev_sub.add_parser("skip")
    p_rs.add_argument("id", type=int)
    p_rr = rev_sub.add_parser("reset")
    p_rr.add_argument("id", type=int)
    rev_sub.add_parser("stats")
    rev_sub.add_parser("next")

    # recent
    p_recent = sub.add_parser("recent")
    p_recent.add_argument("--limit", "-n", type=int, default=20)

    # tags
    p_tags = sub.add_parser("tags")
    p_tags.add_argument("name", nargs="?")

    # get
    p_get = sub.add_parser("get")
    p_get.add_argument("id", type=int)

    # delete
    p_del = sub.add_parser("delete")
    p_del.add_argument("id", type=int)

    sub.add_parser("stats")
    sub.add_parser("export")

    # digest
    p_digest = sub.add_parser("digest")
    p_digest.add_argument("--count", "-c", type=int)
    p_digest.add_argument("--mode", "-m", choices=["shuffle", "newest", "oldest"])
    p_digest.add_argument("--unread-only", "-u", action="store_true")
    p_digest.add_argument("--since")

    # rate
    p_rate = sub.add_parser("rate")
    p_rate.add_argument("id", type=int)
    p_rate.add_argument("rating", type=int)

    # read
    p_read = sub.add_parser("read")
    p_read.add_argument("id", type=int)

    # unread
    p_unread = sub.add_parser("unread")
    p_unread.add_argument("--limit", "-n", type=int, default=20)

    # recommend
    p_recommend = sub.add_parser("recommend")
    p_recommend.add_argument("--limit", "-n", type=int, default=10)

    # related
    p_related = sub.add_parser("related")
    p_related.add_argument("id", type=int)

    # suggest-tags
    p_suggest = sub.add_parser("suggest-tags")
    p_suggest.add_argument("url")

    # gems
    p_gems = sub.add_parser("gems")
    p_gems.add_argument("--count", "-c", type=int, default=5)

    # random
    p_random = sub.add_parser("random")
    p_random.add_argument("--count", "-c", type=int, default=1)

    sub.add_parser("streak")
    sub.add_parser("insights")
    sub.add_parser("weekly")

    # scan
    p_scan = sub.add_parser("scan")
    p_scan.add_argument("source")
    p_scan.add_argument("--path", "-p")

    # sync
    p_sync = sub.add_parser("sync")
    p_sync.add_argument("source")
    p_sync.add_argument("--path", "-p")
    p_sync.add_argument("--auto-delete", action="store_true")

    sub.add_parser("sources")

    # feedback
    p_feedback = sub.add_parser("feedback")
    p_feedback.add_argument("message", nargs="?", default="")
    p_feedback.add_argument("--bug", "-b")
    p_feedback.add_argument("--idea", "-i")

    # debug
    sub.add_parser("debug")

    # import
    p_import = sub.add_parser("import")
    p_import.add_argument("file")
    p_import.add_argument("--source", "-s")

    args = parser.parse_args()

    if not args.command:
        cmd_help(args)
        return

    commands = {
        "setup": cmd_setup, "quickstart": cmd_quickstart, "help": cmd_help,
        "save": cmd_save, "auto-save": cmd_auto_save,
        "search": cmd_search, "recent": cmd_recent,
        "tags": cmd_tags, "get": cmd_get, "delete": cmd_delete,
        "stats": cmd_stats, "export": cmd_export, "digest": cmd_digest,
        "rate": cmd_rate, "read": cmd_read, "unread": cmd_unread,
        "recommend": cmd_recommend, "scan": cmd_scan, "sync": cmd_sync,
        "sources": cmd_sources, "import": cmd_import,
        "related": cmd_related, "suggest-tags": cmd_suggest_tags,
        "gems": cmd_gems, "random": cmd_random,
        "streak": cmd_streak, "insights": cmd_insights,
        "weekly": cmd_weekly, "graph": cmd_graph,
        "collection": cmd_collection, "review": cmd_review,
        "feedback": cmd_feedback, "debug": cmd_debug, "gui": cmd_gui,
    }

    # Show what's new on upgrade (for non-meta commands)
    if args.command not in ("setup", "help", "feedback", "debug"):
        try:
            db = get_db()
            _check_whats_new(db)
        except Exception:
            pass

    commands[args.command](args)


if __name__ == "__main__":
    main()