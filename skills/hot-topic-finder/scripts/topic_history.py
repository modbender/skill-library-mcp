#!/usr/bin/env python3
"""View topic history"""
import sqlite3, os
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/.openclaw/data/topic_history.db")

def history(days=30):
    if not os.path.exists(DB_PATH): return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT topic, use_count, last_used FROM topic_history WHERE last_used >= ? ORDER BY last_used DESC",
        ((datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),))
    return [{"topic": r[0], "use_count": r[1], "last_used": r[2]} for r in cursor.fetchall()]

if __name__ == "__main__":
    h = history(30)
    if not h: print("📭 暂无记录")
    else:
        print(f"\n📋 最近使用记录\n" + "-"*40)
        for x in h[:10]: print(f"{x['topic']:<20} {x['use_count']}次 | {x['last_used']}")