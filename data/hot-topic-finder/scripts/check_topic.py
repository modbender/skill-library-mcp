#!/usr/bin/env python3
"""Check topic usage"""
import sqlite3, os, argparse
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/.openclaw/data/topic_history.db")

def check(topic):
    if not os.path.exists(DB_PATH):
        return {"exists": False, "status": "unused"}
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT use_count, last_used FROM topic_history WHERE topic = ?", (topic,)).fetchone()
    conn.close()
    if not row: return {"exists": False, "status": "unused"}
    days = (datetime.now() - datetime.strptime(row[1], "%Y-%m-%d")).days
    status = "used_today" if days < 1 else "used_recently" if days < 7 else "used_long_ago"
    return {"exists": True, "use_count": row[0], "last_used": row[1], "days": days, "status": status}

if __name__ == "__main__":
    args = argparse.ArgumentParser().parse_args()
    result = check("房价下跌趋势")  # Demo
    if not result["exists"]:
        print(f"✅ 未使用")
    else:
        print(f"⚠️ 已使用 {result['use_count']} 次 | {result['last_used']} ({result['days']}天前)")