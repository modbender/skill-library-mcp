#!/usr/bin/env python3
"""
NIMA Memory Health Check CLI
=============================

Verify database connectivity and get statistics.

Usage:
  python3 health_check.py
  python3 health_check.py --verbose
  python3 health_check.py --json

Author: NIMA Core Team
Date: 2026-02-15
"""

import sqlite3
import json
import sys
import os
import time
from pathlib import Path

DEFAULT_DB = os.path.expanduser("~/.nima/memory/graph.sqlite")

def health_check(db_path: str = DEFAULT_DB, verbose: bool = False):
    """
    Perform health check on NIMA memory database.
    
    Returns:
        dict: Health check results
    """
    if not os.path.exists(db_path):
        return {
            "ok": False,
            "error": "Database file not found",
            "path": db_path
        }
    
    try:
        # Connect with timeout using context manager for automatic cleanup
        with sqlite3.connect(db_path, timeout=2.0) as db:
            # Check tables exist
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [t[0] for t in tables]
            
            if 'memory_nodes' not in table_names:
                return {
                    "ok": False,
                    "error": "memory_nodes table missing",
                    "tables": table_names
                }
            
            # Get stats
            node_count = db.execute("SELECT COUNT(*) FROM memory_nodes").fetchone()[0]
            turn_count = db.execute("SELECT COUNT(*) FROM memory_turns").fetchone()[0]
            
            # Layer distribution
            layers = db.execute("SELECT layer, COUNT(*) FROM memory_nodes GROUP BY layer").fetchall()
            layer_dist = {layer: count for layer, count in layers}
            
            # Recent activity (last 24h)
            now_ts = int(time.time() * 1000)
            day_ago = now_ts - (24 * 60 * 60 * 1000)
            recent_count = db.execute("SELECT COUNT(*) FROM memory_nodes WHERE timestamp > ?", (day_ago,)).fetchone()[0]
            
            # Database file size
            db_size = os.path.getsize(db_path)
            
            # FTS table check
            fts_exists = 'memory_fts' in table_names
            
            # Get first and last memory timestamps
            first_ts = db.execute("SELECT MIN(timestamp) FROM memory_nodes").fetchone()[0]
            last_ts = db.execute("SELECT MAX(timestamp) FROM memory_nodes").fetchone()[0]
            
            from datetime import datetime
            first_date = datetime.fromtimestamp(first_ts / 1000).strftime("%Y-%m-%d %H:%M") if first_ts else None
            last_date = datetime.fromtimestamp(last_ts / 1000).strftime("%Y-%m-%d %H:%M") if last_ts else None
            
            result = {
                "ok": True,
                "stats": {
                    "nodes": node_count,
                    "turns": turn_count,
                    "layers": layer_dist,
                    "recent_24h": recent_count,
                    "db_size_bytes": db_size,
                    "db_size_mb": round(db_size / (1024 * 1024), 2),
                    "tables": table_names,
                    "fts_enabled": fts_exists,
                    "first_memory": first_date,
                    "last_memory": last_date
                }
            }
            
            if verbose:
                # Add top contributors
                top_who = db.execute("""
                    SELECT who, COUNT(*) as count 
                    FROM memory_nodes 
                    WHERE layer = 'input' AND who != '' 
                    GROUP BY who 
                    ORDER BY count DESC 
                    LIMIT 5
                """).fetchall()
                result["stats"]["top_contributors"] = [{"who": w, "count": c} for w, c in top_who]
                
                # Add average FE score
                avg_fe = db.execute("SELECT AVG(fe_score) FROM memory_nodes").fetchone()[0]
                result["stats"]["avg_fe_score"] = round(avg_fe, 3) if avg_fe else None
            
            # Context manager handles db.close() automatically
            return result
        
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "path": db_path
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="NIMA Memory Health Check")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed stats")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    result = health_check(args.db, verbose=args.verbose)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["ok"]:
            print("✅ NIMA Memory Health Check: PASSED")
            print()
            stats = result["stats"]
            print(f"📊 Database Stats:")
            print(f"  Location: {args.db}")
            print(f"  Size: {stats['db_size_mb']} MB")
            print(f"  Nodes: {stats['nodes']:,}")
            print(f"  Turns: {stats['turns']:,}")
            print(f"  Recent (24h): {stats['recent_24h']:,}")
            print()
            print(f"📁 Layer Distribution:")
            for layer, count in sorted(stats['layers'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / stats['nodes'] * 100) if stats['nodes'] > 0 else 0
                print(f"  {layer:20s} {count:6,} ({pct:5.1f}%)")
            print()
            print(f"⏰ Timeline:")
            print(f"  First memory: {stats.get('first_memory', 'N/A')}")
            print(f"  Last memory:  {stats.get('last_memory', 'N/A')}")
            print()
            print(f"🔍 Features:")
            print(f"  FTS search: {'✅ Enabled' if stats['fts_enabled'] else '❌ Disabled'}")
            
            if args.verbose and "top_contributors" in stats:
                print()
                print(f"👥 Top Contributors:")
                for contrib in stats["top_contributors"]:
                    print(f"  {contrib['who']:20s} {contrib['count']:6,} memories")
                
                if stats.get("avg_fe_score"):
                    print()
                    print(f"🧠 Average Free Energy: {stats['avg_fe_score']:.3f}")
        else:
            print(f"❌ NIMA Memory Health Check: FAILED")
            print()
            print(f"Error: {result['error']}")
            if result.get("path"):
                print(f"Path: {result['path']}")
            sys.exit(1)

if __name__ == "__main__":
    main()
