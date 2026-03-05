#!/usr/bin/env python3
import sqlite3
import json
import argparse
import time
import os

# Safe default DB Path
DEFAULT_DB_PATH = "/etc/pihole/pihole-FTL.db"

def query_db(db_path, query, params=None):
    """Run SQL query safely using python-sqlite3 (readonly connection preferred)"""
    if not os.path.exists(db_path):
        return {"error": f"Database file not found at {db_path}. Ensure you have read permissions."}
        
    try:
        # Connect in read-only mode using URI
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        return {"error": str(e)}

def get_summary(db_path, hours=24):
    timestamp = int(time.time()) - (hours * 3600)
    
    # Total Queries
    total_res = query_db(db_path, "SELECT count(*) FROM queries WHERE timestamp >= ?", (timestamp,))
    if isinstance(total_res, dict) and "error" in total_res: return total_res
    total = total_res[0][0] if total_res else 0
    
    # Blocked Queries (Common blocked status codes)
    blocked_res = query_db(db_path, "SELECT count(*) FROM queries WHERE timestamp >= ? AND status IN (1,4,5,6,7,8,9,10,11,14,15)", (timestamp,))
    blocked = blocked_res[0][0] if blocked_res else 0
    
    # Calculate percentage
    pct = (blocked / total * 100) if total > 0 else 0.0

    return {
        "period_hours": hours,
        "total_queries": total,
        "blocked_queries": blocked,
        "percent_blocked": round(pct, 2)
    }

def get_top_domains(db_path, limit=10, hours=24):
    timestamp = int(time.time()) - (hours * 3600)
    query = "SELECT domain, count(domain) as cnt FROM queries WHERE timestamp >= ? GROUP BY domain ORDER BY cnt DESC LIMIT ?"
    
    raw = query_db(db_path, query, (timestamp, limit))
    
    results = []
    if isinstance(raw, list):
        for row in raw:
            results.append({"domain": row[0], "count": row[1]})
            
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Pi-hole FTL Database Safely")
    parser.add_argument("--summary", action="store_true", help="Get summary stats")
    parser.add_argument("--top", type=int, help="Get top N domains")
    parser.add_argument("--hours", type=int, default=24, help="Time window in hours (default: 24)")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=f"Path to FTL db (default: {DEFAULT_DB_PATH})")
    
    args = parser.parse_args()
    
    output = {}
    
    if args.summary:
        output["summary"] = get_summary(args.db, args.hours)
        
    if args.top:
        output["top_domains"] = get_top_domains(args.db, args.top, args.hours)
        
    print(json.dumps(output, indent=2))
