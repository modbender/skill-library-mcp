#!/usr/bin/env python3
"""
NIMA Precognition Query Script

Standalone script for querying precognitions from SQLite.
Called by nima-recall-live hook — avoids inline Python in JS.

Usage:
    python3 query_precognitions.py <query_text> [--limit N] [--compact]

Output: JSON with compact predictions and hash for dedup.
"""

import hashlib
import json
import os
import sqlite3
import sys
from pathlib import Path


def get_precognitions(query_text: str, limit: int = 3) -> dict:
    """Query active precognitions and return compact format.
    
    Note: query_text is currently unused. Precognitions are pattern-based
    predictions about future sessions, not query-dependent. The parameter
    is kept for future relevance-filtering.
    """
    nima_home = os.environ.get("NIMA_HOME", os.path.expanduser("~/.nima"))
    db_path = Path(nima_home) / "memory" / "precognitions.sqlite"
    
    if not db_path.exists():
        return {"parts": [], "hash": ""}
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        rows = conn.execute("""
            SELECT what, confidence, who
            FROM precognitions
            WHERE status = 'active' OR status = 'pending'
            ORDER BY confidence DESC
            LIMIT ?
        """, (limit,)).fetchall()
        
        conn.close()
    except Exception:
        return {"parts": [], "hash": ""}
    
    if not rows:
        return {"parts": [], "hash": ""}
    
    compact_parts = []
    for row in rows:
        text = row["what"] or ""
        confidence = row["confidence"] if row["confidence"] is not None else 0.5
        who = row["who"] or ""
        
        # Shorten to ~60 chars
        short = text[:60].strip()
        if len(text) > 60:
            short += "…"
        
        conf_str = f"({confidence * 100:.0f}%)"
        if who:
            compact_parts.append(f"{short} (w/ {who}) {conf_str}")
        else:
            compact_parts.append(f"{short} {conf_str}")
    
    # Hash for dedup
    h = hashlib.sha256("\n".join(compact_parts).encode()).hexdigest()[:8]
    
    return {"parts": compact_parts, "hash": h}


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    limit = 3
    
    # Parse --limit flag
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[idx + 1])
            except ValueError:
                pass
    
    result = get_precognitions(query, limit)
    print(json.dumps(result))
