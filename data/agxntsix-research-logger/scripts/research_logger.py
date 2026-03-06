#!/usr/bin/env python3
"""
AgxntSix Research Logger — Auto-saves deep search results to SQLite + Langfuse

Usage:
  research_logger.py log <tier> <query> [--topic TOPIC] [--project PROJECT]
  research_logger.py search <query>     # search past research in SQLite
  research_logger.py recent [--limit 10]

This wraps deep_search.py and automatically persists results.
"""
import argparse
import json
import os
import sys
from datetime import datetime

# Langfuse
os.environ.setdefault("LANGFUSE_SECRET_KEY", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
os.environ.setdefault("LANGFUSE_PUBLIC_KEY", "pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4")
os.environ.setdefault("LANGFUSE_HOST", "http://langfuse-web:3000")

try:
    from langfuse import observe, get_client
    TRACING = True
except ImportError:
    TRACING = False
    def observe(**kwargs):
        def decorator(fn): return fn
        return decorator

# Add tools dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_session_id():
    return datetime.now().strftime("session-%Y%m%d-%H")

def save_to_sqlite(query, tier, answer, citations, topic=None, project=None, tokens=None):
    """Save research result to SQLite via structured_db."""
    import sqlite3
    DB_PATH = os.path.expanduser("~/.openclaw/workspace/.data/sqlite/agxntsix.db")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS research (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL, source_url TEXT, source_type TEXT,
        summary TEXT, full_text TEXT, tags TEXT,
        project_id INTEGER, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    
    tags = json.dumps([f"tier:{tier}", f"topic:{topic or 'general'}"])
    sources = "\n".join(citations[:10]) if citations else ""
    
    conn.execute(
        "INSERT INTO research (topic, source_url, source_type, summary, full_text, tags) VALUES (?,?,?,?,?,?)",
        [query, sources, f"perplexity-{tier}", answer[:500], answer, tags]
    )
    conn.commit()
    row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return row_id

@observe(name="research-log")
def log_research(args):
    """Run a deep search and auto-save results."""
    if TRACING:
        try:
            lf = get_client()
            lf.update_current_trace(
                session_id=get_session_id(),
                user_id="agxntsix",
                tags=["research", f"tier-{args.tier}", f"topic-{args.topic or 'general'}"],
                metadata={"topic": args.topic, "project": args.project}
            )
        except Exception:
            pass
    
    # Import and run deep search
    from deep_search import search as deep_search
    
    # Capture stdout
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    result = deep_search(args.tier, args.query, args.focus)
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    if result is None:
        try:
            result = json.loads(output)
        except:
            print(output)
            return
    
    # Save to SQLite
    row_id = save_to_sqlite(
        query=args.query,
        tier=args.tier,
        answer=result.get("answer", ""),
        citations=result.get("citations", []),
        topic=args.topic,
        project=args.project,
        tokens=result.get("tokens")
    )
    
    result["sqlite_id"] = row_id
    result["saved"] = True
    print(json.dumps(result, indent=2))

def search_research(args):
    """Search past research in SQLite."""
    import sqlite3
    DB_PATH = os.path.expanduser("~/.openclaw/workspace/.data/sqlite/agxntsix.db")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, topic, source_type, summary, created_at FROM research WHERE topic LIKE ? OR summary LIKE ? ORDER BY created_at DESC LIMIT 20",
        [f"%{args.query}%", f"%{args.query}%"]
    ).fetchall()
    conn.close()
    print(json.dumps([dict(r) for r in rows], indent=2, default=str))

def recent_research(args):
    """Show recent research entries."""
    import sqlite3
    DB_PATH = os.path.expanduser("~/.openclaw/workspace/.data/sqlite/agxntsix.db")
    if not os.path.exists(DB_PATH):
        print(json.dumps([]))
        return
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, topic, source_type, summary, created_at FROM research ORDER BY created_at DESC LIMIT ?",
        [args.limit]
    ).fetchall()
    conn.close()
    print(json.dumps([dict(r) for r in rows], indent=2, default=str))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgxntSix Research Logger")
    sub = parser.add_subparsers(dest="command")
    
    l = sub.add_parser("log")
    l.add_argument("tier", choices=["quick", "pro", "deep"])
    l.add_argument("query")
    l.add_argument("--topic", default=None)
    l.add_argument("--project", default=None)
    l.add_argument("--focus", default="internet")
    
    s = sub.add_parser("search")
    s.add_argument("query")
    
    r = sub.add_parser("recent")
    r.add_argument("--limit", type=int, default=10)
    
    args = parser.parse_args()
    commands = {"log": log_research, "search": search_research, "recent": recent_research}
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
    
    if TRACING:
        try:
            get_client().flush()
        except:
            pass
