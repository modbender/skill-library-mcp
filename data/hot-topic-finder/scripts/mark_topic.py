#!/usr/bin/env python3
"""Mark topic as used"""
import sqlite3, os, argparse
from datetime import datetime

DB_PATH = os.path.expanduser("~/.openclaw/data/topic_history.db")

def mark(topic, source="manual", heat=0):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS topic_history (
        id INTEGER PRIMARY KEY, topic TEXT UNIQUE, source TEXT, heat INTEGER,
        first_used DATE, last_used DATE, use_count INTEGER DEFAULT 0, tags TEXT)""")
    today = datetime.now().strftime("%Y-%m-%d")
    existing = conn.execute("SELECT use_count FROM topic_history WHERE topic = ?", (topic,)).fetchone()
    if existing:
        conn.execute("UPDATE topic_history SET last_used=?, use_count=use_count+1 WHERE topic=?", (today, topic))
    else:
        conn.execute("INSERT INTO topic_history VALUES (NULL, ?, ?, ?, ?, ?, 1, '')", (topic, source, heat, today, today))
    conn.commit(); conn.close()
    return {"success": True, "topic": topic}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("topic"); parser.add_argument("--source", default="manual"); parser.add_argument("--heat", type=int, default=0)
    args = parser.parse_args()
    result = mark(args.topic, args.source, args.heat)
    print(f"✅ 标记成功: {args.topic}")