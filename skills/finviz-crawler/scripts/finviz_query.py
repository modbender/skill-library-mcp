#!/usr/bin/env python3
"""
finviz-query — Read from the crawler's SQLite DB + article files for summarization.
Used by cron jobs. SQLite has metadata, article content is on disk as .md files.

Usage:
    python3 finviz_query.py --hours 12              # last 12h by publish_at
    python3 finviz_query.py --hours 168             # last 7 days
    python3 finviz_query.py --hours 12 --titles-only # compact headline list
    python3 finviz_query.py --stats                  # DB + disk stats
    python3 finviz_query.py --list-tickers           # show tracked tickers
    python3 finviz_query.py --add-ticker NVDA        # add ticker(s) to track
    python3 finviz_query.py --add-ticker "NVDA:nvidia,jensen" "TSLA:tesla,elon"
    python3 finviz_query.py --remove-ticker NVDA TSLA  # remove ticker(s)
    python3 finviz_query.py --list-articles --hours 24  # list downloaded articles
"""
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_DB = os.path.expanduser("~/Downloads/Finviz/finviz.db")
DEFAULT_ARTICLES_DIR = os.path.expanduser("~/Downloads/Finviz/articles")


def get_conn(db_path: str) -> sqlite3.Connection:
    if not os.path.exists(db_path):
        print(json.dumps({"error": f"Database not found: {db_path}"}))
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS tickers (
        symbol TEXT PRIMARY KEY,
        keywords TEXT NOT NULL DEFAULT '[]',
        added_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn


def list_tickers(db: str) -> None:
    conn = get_conn(db)
    rows = conn.execute("SELECT symbol, keywords, added_at FROM tickers ORDER BY symbol").fetchall()
    conn.close()
    if not rows:
        print("No tickers tracked. Add with: --add-ticker NVDA")
        return
    print(f"{'Symbol':<10} {'Keywords':<40} {'Added'}")
    print("-" * 70)
    for r in rows:
        kw = ", ".join(json.loads(r["keywords"]))
        added = r["added_at"][:10]
        print(f"{r['symbol']:<10} {kw:<40} {added}")
    print(f"\n{len(rows)} ticker(s) tracked")


def add_tickers(db: str, specs: list[str]) -> None:
    conn = get_conn(db)
    now = datetime.now(timezone.utc).isoformat()
    added = []
    for spec in specs:
        # Format: "NVDA" or "NVDA:nvidia,jensen huang"
        if ":" in spec:
            sym, kw_str = spec.split(":", 1)
            keywords = [k.strip() for k in kw_str.split(",") if k.strip()]
        else:
            sym = spec.strip()
            keywords = [sym.lower()]
        sym = sym.strip().upper()
        if not sym:
            continue
        conn.execute(
            "INSERT OR REPLACE INTO tickers (symbol, keywords, added_at) VALUES (?, ?, ?)",
            (sym, json.dumps(keywords), now),
        )
        added.append(sym)
    conn.commit()
    conn.close()
    if added:
        print(f"Added: {', '.join(added)}")
    else:
        print("Nothing to add")


def remove_tickers(db: str, symbols: list[str], articles_db: str = DEFAULT_DB, articles_dir: str = DEFAULT_ARTICLES_DIR) -> None:
    conn = get_conn(db)
    removed = []
    for sym in symbols:
        sym = sym.strip().upper()
        cur = conn.execute("DELETE FROM tickers WHERE symbol = ?", (sym,))
        if cur.rowcount:
            removed.append(sym)
    conn.commit()
    conn.close()

    if not removed:
        print("No matching tickers found")
        return

    # Delete articles from finviz DB and disk
    if os.path.exists(articles_db):
        fconn = sqlite3.connect(articles_db)
        fconn.row_factory = sqlite3.Row
        for sym in removed:
            # Delete files from disk (subfolder)
            subfolder = os.path.join(articles_dir, sym.lower())
            file_count = 0
            if os.path.isdir(subfolder):
                import shutil
                file_count = len([f for f in os.listdir(subfolder) if f.endswith(".md")])
                shutil.rmtree(subfolder)

            # Also delete any old flat-path files referenced in DB
            rows = fconn.execute(
                "SELECT article_path FROM articles WHERE ticker = ? AND article_path IS NOT NULL",
                (sym,),
            ).fetchall()
            for r in rows:
                fp = os.path.join(articles_dir, r["article_path"])
                if os.path.exists(fp):
                    os.remove(fp)
                    file_count += 1

            # Delete DB rows
            cur = fconn.execute("DELETE FROM articles WHERE ticker = ?", (sym,))
            db_count = cur.rowcount
            print(f"  {sym}: {db_count} DB rows, {file_count} files removed")
        fconn.commit()
        fconn.close()

    print(f"Removed: {', '.join(removed)}")


def list_articles(conn: sqlite3.Connection, articles_dir: str, hours: float) -> None:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute(
        """SELECT title, url, domain, publish_at, article_path, ticker
           FROM articles WHERE publish_at >= ? AND status = 'done'
           ORDER BY publish_at DESC""",
        (cutoff,),
    ).fetchall()

    has_content = 0
    for r in rows:
        ap = r["article_path"] or ""
        has_file = "✓" if ap and os.path.exists(os.path.join(articles_dir, ap)) else "✗"
        ticker = r["ticker"] or "—"
        pub = r["publish_at"][:16] if r["publish_at"] else "?"
        if has_file == "✓":
            has_content += 1
        print(f"[{pub}] [{ticker:<6}] {has_file} {r['title'][:80]}")

    print(f"\n{len(rows)} articles in last {hours}h ({has_content} with content)")


def query_recent(conn: sqlite3.Connection, articles_dir: str,
                 hours: float | None = None, since: str | None = None,
                 include_content: bool = False) -> list[dict]:
    if since:
        cutoff = since
    elif hours:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    else:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()

    rows = conn.execute(
        """SELECT title, url, domain, source, publish_at, article_path,
                  fetched_at, crawled_at, status, retry_count
           FROM articles
           WHERE publish_at >= ? AND status = 'done'
           ORDER BY publish_at DESC""",
        (cutoff,),
    ).fetchall()

    results = []
    for r in rows:
        item = dict(r)
        if include_content and item.get("article_path"):
            fpath = os.path.join(articles_dir, item["article_path"])
            if os.path.exists(fpath):
                with open(fpath, "r", errors="replace") as f:
                    item["content"] = f.read()
            else:
                item["content"] = None
        results.append(item)

    return results


def db_stats(conn: sqlite3.Connection, articles_dir: str) -> dict:
    stats = {}
    for status in ("done", "pending", "failed"):
        stats[status] = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE status=?", (status,)
        ).fetchone()[0]
    stats["total"] = sum(stats.values())

    stats["oldest"] = conn.execute("SELECT MIN(publish_at) FROM articles").fetchone()[0]
    stats["newest"] = conn.execute("SELECT MAX(publish_at) FROM articles").fetchone()[0]

    last_24h = conn.execute(
        "SELECT COUNT(*) FROM articles WHERE publish_at >= ?",
        ((datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(),),
    ).fetchone()[0]
    stats["last_24h"] = last_24h

    # Disk stats
    articles_path = Path(articles_dir)
    if articles_path.exists():
        files = list(articles_path.rglob("*.md"))
        stats["articles_on_disk"] = len(files)
        stats["total_size_mb"] = round(sum(f.stat().st_size for f in files) / 1048576, 2)
    else:
        stats["articles_on_disk"] = 0
        stats["total_size_mb"] = 0

    return stats


def main():
    parser = argparse.ArgumentParser(description="Query finviz crawler DB")
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--articles-dir", default=DEFAULT_ARTICLES_DIR)
    parser.add_argument("--db", default=DEFAULT_DB)
    parser.add_argument("--hours", type=float, default=12,
                        help="Articles published in last N hours (default: 12)")
    parser.add_argument("--since", help="Articles since ISO date (overrides --hours)")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--titles-only", action="store_true")
    parser.add_argument("--with-content", action="store_true",
                        help="Include article content from disk")
    parser.add_argument("--list-tickers", action="store_true",
                        help="List tracked tickers")
    parser.add_argument("--add-ticker", nargs="+", metavar="SPEC",
                        help="Add ticker(s): NVDA or NVDA:nvidia,jensen")
    parser.add_argument("--remove-ticker", nargs="+", metavar="SYMBOL",
                        help="Remove ticker(s): NVDA TSLA")
    parser.add_argument("--list-articles", action="store_true",
                        help="List downloaded articles with status")
    args = parser.parse_args()

    # Ticker management (doesn't need main DB)
    if args.list_tickers:
        list_tickers(args.db)
        return
    if args.add_ticker:
        add_tickers(args.db, args.add_ticker)
        return
    if args.remove_ticker:
        remove_tickers(args.db, args.remove_ticker, args.db, args.articles_dir)
        return

    conn = get_conn(args.db)

    if args.stats:
        print(json.dumps(db_stats(conn, args.articles_dir), indent=2))
        return

    if args.list_articles:
        list_articles(conn, args.articles_dir, args.hours)
        return

    articles = query_recent(
        conn, args.articles_dir,
        hours=args.hours, since=args.since,
        include_content=args.with_content,
    )

    if args.titles_only:
        for a in articles:
            pub = a.get("publish_at", "")[:16]
            print(f"[{pub}] {a['title']}  ({a.get('domain', '')})")
    else:
        output = {
            "query": {"hours": args.hours, "since": args.since},
            "count": len(articles),
            "articles": articles,
        }
        print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
