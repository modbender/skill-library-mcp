#!/usr/bin/env python3
"""
CompoundMind v0.1 - Wisdom Index
Searchable database of all distilled experiences.
Supports natural language queries with recency + importance weighting.
"""

import os
import sys
import json
import sqlite3
import argparse
import re
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXP_DIR = DATA_DIR / "experiences"
DB_PATH = DATA_DIR / "wisdom.db"

# Days of half-life for recency scoring
RECENCY_HALF_LIFE_DAYS = 30


def get_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS entries (
            id          TEXT PRIMARY KEY,
            source      TEXT,
            source_date TEXT,
            category    TEXT,
            domain      TEXT,
            importance  INTEGER DEFAULT 3,
            quality     TEXT,
            text        TEXT,
            tags        TEXT,
            extra_json  TEXT,
            indexed_at  TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
            id UNINDEXED,
            text,
            domain,
            tags,
            category,
            content='entries',
            content_rowid='rowid'
        );

        CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
            INSERT INTO entries_fts(rowid, id, text, domain, tags, category)
            VALUES (new.rowid, new.id, new.text, new.domain, new.tags, new.category);
        END;

        CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, id, text, domain, tags, category)
            VALUES ('delete', old.rowid, old.id, old.text, old.domain, old.tags, old.category);
        END;

        CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
            INSERT INTO entries_fts(entries_fts, rowid, id, text, domain, tags, category)
            VALUES ('delete', old.rowid, old.id, old.text, old.domain, old.tags, old.category);
            INSERT INTO entries_fts(rowid, id, text, domain, tags, category)
            VALUES (new.rowid, new.id, new.text, new.domain, new.tags, new.category);
        END;
    """)
    conn.commit()


def recency_score(source_date_str: str) -> float:
    """0.0-1.0 score, decays exponentially with age."""
    try:
        src = date.fromisoformat(source_date_str)
        days_old = (date.today() - src).days
        return 0.5 ** (days_old / RECENCY_HALF_LIFE_DAYS)
    except Exception:
        return 0.5


def build_entry_id(exp_id: str, category: str, idx: int) -> str:
    return f"{exp_id}:{category}:{idx}"


def load_experience_to_db(conn: sqlite3.Connection, exp_path: Path) -> int:
    """Load one experience JSON file into the DB. Returns count of new entries."""
    exp = json.loads(exp_path.read_text())
    exp_id = exp["id"]
    source = exp["source"]
    source_date = exp.get("source_date", "")
    indexed_at = datetime.now().isoformat()
    added = 0

    # Check if this experience is already indexed with same content
    cursor = conn.execute(
        "SELECT COUNT(*) FROM entries WHERE id LIKE ? AND source=?",
        (f"{exp_id}:%", source)
    )
    existing = cursor.fetchone()[0]

    # Process each category
    def upsert(entry_id, category, domain, importance, quality, text, tags, extra):
        nonlocal added
        if not text or not text.strip():
            return
        # Delete first to avoid FTS5 trigger conflict with OR REPLACE
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.execute("""
            INSERT INTO entries
            (id, source, source_date, category, domain, importance, quality, text, tags, extra_json, indexed_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            entry_id, source, source_date, category, domain,
            importance, quality, text,
            json.dumps(tags) if isinstance(tags, list) else (tags or ""),
            json.dumps(extra) if extra else None,
            indexed_at
        ))
        added += 1

    for i, lesson in enumerate(exp.get("lessons", [])):
        upsert(
            build_entry_id(exp_id, "lesson", i),
            "lesson",
            lesson.get("domain", "general"),
            lesson.get("importance", 3),
            lesson.get("outcome", "neutral"),
            lesson.get("text", ""),
            lesson.get("tags", []),
            None
        )

    for i, decision in enumerate(exp.get("decisions", [])):
        text = f"Context: {decision.get('context', '')} | Action: {decision.get('action', '')} | Outcome: {decision.get('outcome', '')}"
        upsert(
            build_entry_id(exp_id, "decision", i),
            "decision",
            decision.get("domain", "general"),
            3,
            decision.get("quality", "neutral"),
            text,
            [],
            decision
        )

    for i, skill in enumerate(exp.get("skill_updates", [])):
        text = f"Skill: {skill.get('skill', '')} | {skill.get('change', '')} | Evidence: {skill.get('evidence', '')}"
        upsert(
            build_entry_id(exp_id, "skill", i),
            "skill",
            skill.get("domain", "general"),
            4,
            "positive",
            text,
            [skill.get("skill", "")],
            skill
        )

    for i, rel in enumerate(exp.get("relationships", [])):
        text = f"{rel.get('person', '')} - {rel.get('insight', '')}"
        upsert(
            build_entry_id(exp_id, "relationship", i),
            "relationship",
            "communication",
            4,
            "neutral",
            text,
            [rel.get("person", ""), rel.get("interaction_type", "")],
            rel
        )

    for i, fact in enumerate(exp.get("facts", [])):
        upsert(
            build_entry_id(exp_id, "fact", i),
            "fact",
            fact.get("domain", "general"),
            fact.get("importance", 2) if "importance" in fact else 2,
            "neutral",
            fact.get("fact", ""),
            fact.get("tags", []),
            None
        )

    conn.commit()
    return added


def rebuild_index():
    """Rebuild the wisdom index from all experience files."""
    conn = get_db()
    init_db(conn)

    exp_files = sorted(EXP_DIR.glob("*.json"))
    if not exp_files:
        print("No experience files found. Run distill.py first.")
        return

    print(f"Indexing {len(exp_files)} experience files...")
    total = 0
    for f in exp_files:
        count = load_experience_to_db(conn, f)
        total += count

    cursor = conn.execute("SELECT COUNT(*) FROM entries")
    db_total = cursor.fetchone()[0]
    print(f"Done. Added {total} entries. Total in index: {db_total}")
    conn.close()


def search(query: str, domain: str = None, category: str = None, limit: int = 10, verbose: bool = False) -> list[dict]:
    """Search the wisdom index. Returns ranked results."""
    conn = get_db()
    init_db(conn)

    # Build FTS query - handle special chars
    fts_query = " OR ".join(f'"{w}"' for w in query.split() if len(w) > 2)
    if not fts_query:
        fts_query = query

    filters = []
    params = [fts_query]

    if domain:
        filters.append("e.domain = ?")
        params.append(domain)
    if category:
        filters.append("e.category = ?")
        params.append(category)

    where_clause = ""
    if filters:
        where_clause = "AND " + " AND ".join(filters)

    try:
        sql = f"""
            SELECT e.*, bm25(entries_fts) AS fts_score
            FROM entries_fts
            JOIN entries e ON entries_fts.id = e.id
            WHERE entries_fts MATCH ?
            {where_clause}
            ORDER BY fts_score
            LIMIT {limit * 3}
        """
        rows = conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError:
        # Fallback: LIKE search
        sql = f"""
            SELECT e.*, 0 AS fts_score
            FROM entries e
            WHERE (e.text LIKE ? OR e.tags LIKE ? OR e.domain LIKE ?)
            {where_clause}
            LIMIT {limit * 3}
        """
        like_q = f"%{query}%"
        params2 = [like_q, like_q, like_q]
        if domain:
            params2.append(domain)
        if category:
            params2.append(category)
        rows = conn.execute(sql, params2).fetchall()

    conn.close()

    results = []
    for row in rows:
        rec = dict(row)
        # Recency score (0-1)
        rec["recency_score"] = recency_score(rec.get("source_date", ""))
        # Importance score (normalized 0-1)
        rec["importance_score"] = rec.get("importance", 3) / 5.0
        # Combined rank: fts gives lower = better, so negate; add recency + importance
        fts = rec.get("fts_score", 0) or 0
        rec["rank"] = (-fts) * 0.5 + rec["recency_score"] * 0.3 + rec["importance_score"] * 0.2
        results.append(rec)

    results.sort(key=lambda x: x["rank"], reverse=True)
    return results[:limit]


def format_results(results: list[dict], verbose: bool = False) -> str:
    if not results:
        return "No results found."

    lines = []
    for i, r in enumerate(results, 1):
        cat_emoji = {
            "lesson": "**",
            "decision": "->",
            "skill": "^",
            "relationship": "@",
            "fact": "i"
        }.get(r["category"], "*")

        date_str = r.get("source_date", "unknown")
        domain = r.get("domain", "")
        text = r.get("text", "")

        lines.append(f"{i}. [{cat_emoji} {r['category'].upper()}] [{domain}] [{date_str}]")
        lines.append(f"   {text}")

        if verbose and r.get("extra_json"):
            extra = json.loads(r["extra_json"]) if isinstance(r["extra_json"], str) else r["extra_json"]
            if extra:
                lines.append(f"   Extra: {json.dumps(extra, ensure_ascii=False)[:200]}")

        # Quality/outcome indicator
        qual = r.get("quality") or r.get("outcome")
        if qual and qual not in ("neutral", "null", "None"):
            lines.append(f"   Outcome: {qual}")
        lines.append("")

    return "\n".join(lines)


def stats():
    """Print index statistics."""
    conn = get_db()
    init_db(conn)

    total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
    by_cat = conn.execute(
        "SELECT category, COUNT(*) as n FROM entries GROUP BY category ORDER BY n DESC"
    ).fetchall()
    by_domain = conn.execute(
        "SELECT domain, COUNT(*) as n FROM entries GROUP BY domain ORDER BY n DESC"
    ).fetchall()
    oldest = conn.execute("SELECT MIN(source_date) FROM entries").fetchone()[0]
    newest = conn.execute("SELECT MAX(source_date) FROM entries").fetchone()[0]
    conn.close()

    print(f"Wisdom Index Stats")
    print(f"==================")
    print(f"Total entries: {total}")
    print(f"Date range: {oldest} to {newest}")
    print()
    print("By category:")
    for row in by_cat:
        print(f"  {row['category']:15} {row['n']}")
    print()
    print("By domain:")
    for row in by_domain:
        print(f"  {row['domain']:15} {row['n']}")


def main():
    parser = argparse.ArgumentParser(description="CompoundMind Wisdom Index")
    sub = parser.add_subparsers(dest="cmd")

    # rebuild
    sub.add_parser("rebuild", help="Rebuild index from all experience files")

    # search
    sp = sub.add_parser("search", help="Search the wisdom index")
    sp.add_argument("query", nargs="+", help="Search terms")
    sp.add_argument("--domain", help="Filter by domain (trading|coding|social|etc)")
    sp.add_argument("--category", help="Filter by category (lesson|decision|skill|relationship|fact)")
    sp.add_argument("--limit", type=int, default=10, help="Max results")
    sp.add_argument("--verbose", "-v", action="store_true")

    # stats
    sub.add_parser("stats", help="Show index statistics")

    args = parser.parse_args()

    if args.cmd == "rebuild":
        rebuild_index()
    elif args.cmd == "search":
        q = " ".join(args.query)
        results = search(q, domain=args.domain, category=args.category, limit=args.limit)
        print(f"Results for: '{q}'\n")
        print(format_results(results, verbose=args.verbose))
    elif args.cmd == "stats":
        stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
