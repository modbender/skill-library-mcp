#!/usr/bin/env python3
"""
clawhub_snapshot.py — ClawHub Skills Tracker (stdlib-only, runs inside OpenClaw container)

Fetches all skills from the ClawHub REST API, stores daily snapshots in SQLite,
calculates 7-day install velocity for trending analysis.

Usage:
    python3 clawhub_snapshot.py snapshot                # Daily: record snapshot
    python3 clawhub_snapshot.py report [--top N]        # Weekly: snapshot + rank + markdown
    python3 clawhub_snapshot.py trending [--top N]      # Quick: show top N from DB
    python3 clawhub_snapshot.py status                  # Show DB health
    python3 clawhub_snapshot.py community [--save]      # Placeholder for community signals

No pip dependencies. Uses urllib, json, sqlite3 (all Python stdlib).
"""

import argparse
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --- Config ---
CLAWHUB_API = "https://clawhub.ai/api/v1/skills"
PAGE_LIMIT = 100
PAGE_DELAY = 0.75
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0

DATA_DIR = Path(os.environ.get(
    "SKILLS_WEEKLY_DATA",
    # Use workspace volume (writable) inside Docker, fallback for host
    "/home/node/.openclaw/workspace/data/skills-weekly"
    if Path("/home/node/.openclaw/workspace").exists()
    else os.path.expanduser("~/.local/share/skills-weekly")
))
DB_PATH = DATA_DIR / "metrics.db"
SIGNALS_PATH = DATA_DIR / "weekly_signals.json"

# Also write reports to host mount if available (set HOST_OUTPUT_DIR env var)
HOST_OUTPUT = Path(os.environ.get("HOST_OUTPUT_DIR", "/mnt/host/skills-weekly"))


# --- Database ---

def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS skills (
            slug TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            summary TEXT DEFAULT '',
            author TEXT DEFAULT '',
            clawhub_url TEXT DEFAULT '',
            created_at INTEGER DEFAULT 0,
            updated_at INTEGER DEFAULT 0,
            latest_version TEXT DEFAULT '',
            os_support TEXT DEFAULT '',
            systems TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS metrics_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL REFERENCES skills(slug),
            timestamp TEXT NOT NULL,
            downloads INTEGER NOT NULL DEFAULT 0,
            stars INTEGER NOT NULL DEFAULT 0,
            installs_current INTEGER NOT NULL DEFAULT 0,
            installs_all_time INTEGER NOT NULL DEFAULT 0,
            versions INTEGER NOT NULL DEFAULT 0,
            comments INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS idx_mh_slug_ts
            ON metrics_history (slug, timestamp);
    """)
    conn.close()
    return DB_PATH


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# --- ClawHub API ---

def fetch_page(url, params):
    """Fetch one page from ClawHub API with retry logic."""
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v)
    full_url = f"{url}?{qs}" if qs else url

    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(full_url, headers={
                "User-Agent": "OpenclawSkillsWeekly/1.0",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                return data.get("items", []), data.get("nextCursor")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"  [429] Rate limited, backing off {wait:.0f}s")
                time.sleep(wait)
                continue
            print(f"  [HTTP {e.code}] {e.reason}")
            return [], None
        except Exception as e:
            wait = RETRY_BACKOFF * (2 ** attempt)
            print(f"  [ERROR] {e}, retrying in {wait:.0f}s")
            time.sleep(wait)
    return [], None


def normalise(item):
    """Flatten ClawHub API item into DB-compatible dict."""
    stats = item.get("stats") or {}
    lv = item.get("latestVersion") or {}
    meta = item.get("metadata") or {}
    slug = item.get("slug", "")
    author = slug.split("/")[0] if "/" in slug else ""
    return {
        "slug": slug,
        "display_name": item.get("displayName") or slug,
        "summary": item.get("summary") or "",
        "author": author,
        "downloads": stats.get("downloads", 0) or 0,
        "stars": stats.get("stars", 0) or 0,
        "installs_current": stats.get("installsCurrent", 0) or 0,
        "installs_all_time": stats.get("installsAllTime", 0) or 0,
        "versions": stats.get("versions", 0) or 0,
        "comments": stats.get("comments", 0) or 0,
        "created_at": item.get("createdAt", 0) or 0,
        "updated_at": item.get("updatedAt", 0) or 0,
        "latest_version": lv.get("version", ""),
        "os_support": ",".join(meta.get("os") or []),
        "systems": ",".join(meta.get("systems") or []),
        "clawhub_url": f"https://clawhub.ai/skills/{slug}" if slug else "",
    }


def discover_all(sort="downloads", max_pages=0):
    """Paginate through all ClawHub skills."""
    print(f"[SNAPSHOT] Fetching from {CLAWHUB_API} (sort={sort})...")
    all_skills = []
    cursor = None
    page = 0

    while True:
        params = {"sort": sort, "limit": str(PAGE_LIMIT)}
        if cursor:
            params["cursor"] = cursor

        items, next_cursor = fetch_page(CLAWHUB_API, params)
        if not items and page == 0:
            print("[SNAPSHOT] No items on first page — API may be down")
            break

        for item in items:
            all_skills.append(normalise(item))

        page += 1
        print(f"  Page {page}: {len(items)} skills (total: {len(all_skills)})")

        cursor = next_cursor
        if not cursor or not items:
            break
        if max_pages and page >= max_pages:
            break
        time.sleep(PAGE_DELAY)

    print(f"[SNAPSHOT] Done: {len(all_skills)} skills fetched in {page} pages")
    return all_skills


def record_snapshot(skills):
    """Upsert skills and record metrics snapshot."""
    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    try:
        for s in skills:
            conn.execute("""
                INSERT INTO skills (slug, display_name, summary, author, clawhub_url,
                                    created_at, updated_at, latest_version, os_support, systems)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    display_name=excluded.display_name, summary=excluded.summary,
                    author=excluded.author, clawhub_url=excluded.clawhub_url,
                    updated_at=excluded.updated_at, latest_version=excluded.latest_version,
                    os_support=excluded.os_support, systems=excluded.systems
            """, (s["slug"], s["display_name"], s["summary"], s["author"],
                  s["clawhub_url"], s["created_at"], s["updated_at"],
                  s["latest_version"], s["os_support"], s["systems"]))

        conn.executemany("""
            INSERT INTO metrics_history (slug, timestamp, downloads, stars,
                                         installs_current, installs_all_time, versions, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(s["slug"], now, s["downloads"], s["stars"], s["installs_current"],
               s["installs_all_time"], s["versions"], s["comments"]) for s in skills])
        conn.commit()
    finally:
        conn.close()

    print(f"[SNAPSHOT] Recorded {len(skills)} skills at {now[:19]}")


# --- Velocity / Trending ---

def get_velocity(slug, days=7):
    """Calculate install velocity for one skill."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    conn = get_conn()
    rows = conn.execute("""
        SELECT installs_current, downloads, stars, timestamp
        FROM metrics_history WHERE slug = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    """, (slug, cutoff)).fetchall()
    conn.close()

    if len(rows) < 2:
        r = rows[-1] if rows else None
        return {
            "slug": slug,
            "installs_delta": 0,
            "downloads_delta": 0,
            "stars_delta": 0,
            "pct_increase": 0.0,
            "snapshots": len(rows),
            "latest_installs": r["installs_current"] if r else 0,
            "latest_downloads": r["downloads"] if r else 0,
            "latest_stars": r["stars"] if r else 0,
        }

    e, l = rows[0], rows[-1]
    id_ = l["installs_current"] - e["installs_current"]
    dd = l["downloads"] - e["downloads"]
    sd = l["stars"] - e["stars"]
    base = e["installs_current"]
    pct = (id_ / base * 100) if base > 0 else (100.0 if id_ > 0 else 0.0)

    return {
        "slug": slug,
        "installs_delta": id_, "downloads_delta": dd, "stars_delta": sd,
        "pct_increase": round(pct, 2), "snapshots": len(rows),
        "latest_installs": l["installs_current"],
        "latest_downloads": l["downloads"],
        "latest_stars": l["stars"],
    }


def rank_trending(top_n=10, days=7):
    """Rank all skills by trending velocity."""
    conn = get_conn()
    slugs = [r["slug"] for r in conn.execute("SELECT slug FROM skills").fetchall()]
    conn.close()

    scored = []
    for slug in slugs:
        v = get_velocity(slug, days)
        # On first run, use raw installs as proxy
        if v["snapshots"] <= 1:
            v["installs_delta"] = v["latest_installs"]
            v["downloads_delta"] = v["latest_downloads"]

        # Composite: 35% installs delta + 15% downloads delta + 30% pct + 20% stars
        id_n = min(max(v["installs_delta"], 0), 2000) / 2000
        dd_n = min(max(v["downloads_delta"], 0), 10000) / 10000
        pn = min(max(v["pct_increase"], 0), 500) / 500
        sn = min(v["latest_stars"], 200) / 200
        score = 0.35 * id_n + 0.15 * dd_n + 0.30 * pn + 0.20 * sn

        v["score"] = round(score, 4)

        # Get metadata
        conn2 = get_conn()
        row = conn2.execute("SELECT * FROM skills WHERE slug = ?", (slug,)).fetchone()
        conn2.close()
        if row:
            v["display_name"] = row["display_name"]
            v["summary"] = row["summary"]
            v["author"] = row["author"]
            v["clawhub_url"] = row["clawhub_url"]
        scored.append(v)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_n]


# --- Output ---

def render_report(ranked, week_label=""):
    """Generate markdown report."""
    if not week_label:
        week_label = f"Week of {datetime.now().strftime('%b %d, %Y')}"

    lines = [
        f"# OpenClaw Skills Weekly — {week_label}",
        "",
        f"*Top {len(ranked)} trending ClawHub skills ranked by 7-day install velocity.*",
        "",
        "| # | Skill | Installs | 7d Delta | DL Delta | Stars | Score |",
        "|---|-------|----------|----------|----------|-------|-------|",
    ]
    for i, r in enumerate(ranked, 1):
        name = r.get("display_name", r["slug"])
        snap = f"({r['snapshots']}d)" if r["snapshots"] > 1 else "(new)"
        lines.append(
            f"| {i} | [{name}]({r.get('clawhub_url', '')}) "
            f"| {r['latest_installs']:,} "
            f"| +{r['installs_delta']:,} {snap} "
            f"| +{r['downloads_delta']:,} "
            f"| {r['latest_stars']} "
            f"| {r['score']:.4f} |"
        )

    lines += ["", "---", ""]

    # Append community signals if available
    if SIGNALS_PATH.exists():
        try:
            signals = json.loads(SIGNALS_PATH.read_text())
            if signals:
                lines.append("## Community Buzz This Week")
                lines.append("")
                for s in signals:
                    title = s.get("title", "")
                    url = s.get("url", "")
                    summary = s.get("summary", "")
                    cat = s.get("category", "discussion")
                    link = f"[{title}]({url})" if url else title
                    lines.append(f"- **[{cat}]** {link}")
                    if summary:
                        lines.append(f"  {summary}")
                    lines.append("")
                lines.append("---")
        except (json.JSONDecodeError, OSError):
            pass

    return "\n".join(lines)


def db_status():
    """Print DB health info."""
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM metrics_history").fetchone()[0]
    dates = conn.execute(
        "SELECT DISTINCT DATE(timestamp) as d FROM metrics_history ORDER BY d"
    ).fetchall()
    skill_count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]

    top = conn.execute("""
        SELECT m.slug, m.installs_current, m.downloads, m.stars, s.display_name
        FROM metrics_history m JOIN skills s ON s.slug = m.slug
        WHERE m.timestamp = (SELECT MAX(timestamp) FROM metrics_history WHERE slug = m.slug)
        ORDER BY m.installs_current DESC LIMIT 15
    """).fetchall()
    conn.close()

    print(f"DB: {DB_PATH}")
    print(f"Skills: {skill_count}")
    print(f"Snapshot rows: {total}")
    print(f"Snapshot dates: {len(dates)}")
    for d in dates[-7:]:
        print(f"  {d['d']}")
    print(f"\nTop 15 by current installs:")
    for r in top:
        print(f"  {r['display_name']:35s} installs={r['installs_current']:>6,}  dl={r['downloads']:>8,}  stars={r['stars']:>4}")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="ClawHub Skills Tracker")
    parser.add_argument("mode", choices=["snapshot", "report", "trending", "status", "community"],
                        help="Operation mode")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--sort", default="downloads")
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument("--save", action="store_true")
    args = parser.parse_args()

    init_db()

    if args.mode == "status":
        db_status()
        return

    if args.mode == "snapshot":
        skills = discover_all(sort=args.sort, max_pages=args.max_pages)
        if skills:
            record_snapshot(skills)
            # Print summary
            conn = get_conn()
            dates = conn.execute(
                "SELECT DISTINCT DATE(timestamp) as d FROM metrics_history"
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM metrics_history").fetchone()[0]
            conn.close()
            print(f"[SNAPSHOT] DB: {len(dates)} snapshot dates, {total} total rows")
        return

    if args.mode == "trending":
        ranked = rank_trending(top_n=args.top, days=args.days)
        print(f"\nTop {len(ranked)} trending skills ({args.days}-day velocity):\n")
        for i, r in enumerate(ranked, 1):
            snap = f"({r['snapshots']} snapshots)" if r["snapshots"] > 1 else "(first run)"
            print(f"  #{i:2d} {r.get('display_name', r['slug']):35s} "
                  f"score={r['score']:.4f} "
                  f"installs_delta=+{r['installs_delta']:,} "
                  f"pct=+{r['pct_increase']:.1f}% "
                  f"stars={r['latest_stars']} {snap}")
        return

    if args.mode == "report":
        # Snapshot first
        skills = discover_all(sort=args.sort, max_pages=args.max_pages)
        if skills:
            record_snapshot(skills)

        # Rank
        ranked = rank_trending(top_n=args.top, days=args.days)

        # Render
        md = render_report(ranked)
        report_name = f"openclaw_weekly_{datetime.now().strftime('%Y%m%d')}.md"

        # Save locally
        local_path = DATA_DIR / report_name
        local_path.write_text(md)
        print(f"[REPORT] Saved: {local_path}")

        # Also save to host mount if available
        if HOST_OUTPUT.exists():
            host_path = HOST_OUTPUT / report_name
            host_path.write_text(md)
            print(f"[REPORT] Also saved to host: {host_path}")

        # Print to stdout for Claude to see
        print("\n" + md)
        return

    if args.mode == "community":
        print("[COMMUNITY] Community signal capture")
        print("  This mode is invoked by the OpenClaw gateway's WebSearch tool.")
        print("  The SKILL.md instructs Claude to search and save signals.")
        print(f"  Signals file: {SIGNALS_PATH}")
        if SIGNALS_PATH.exists():
            signals = json.loads(SIGNALS_PATH.read_text())
            print(f"  Current signals: {len(signals)}")
            for s in signals:
                print(f"    [{s.get('category', '?')}] {s.get('title', '?')}")
        else:
            print("  No signals captured yet.")
        return


if __name__ == "__main__":
    main()
