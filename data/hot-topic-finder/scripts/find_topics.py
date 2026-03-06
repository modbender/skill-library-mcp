#!/usr/bin/env python3
"""Hot Topic Finder - 热点话题发现脚本"""
import argparse, sqlite3, os
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/.openclaw/data/topic_history.db")

TOPICS = [
    ("房价下跌趋势", 560000, "财经"),
    ("AI替代人类工作", 480000, "科技"),
    ("二手房交易量暴跌", 450000, "财经"),
    ("职场35岁危机", 420000, "职场"),
    ("年轻人不婚不育", 380000, "社会"),
    ("新能源车价格战", 350000, "科技"),
    ("考研分数线变化", 320000, "教育"),
    ("谷爱凌斯坦福牛津双学霸", 310000, "娱乐"),
    ("中年女人显年轻的特点", 280000, "生活"),
    ("春季养生指南", 190000, "健康"),
]

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS topic_history (
        id INTEGER PRIMARY KEY, topic TEXT UNIQUE, source TEXT, heat INTEGER,
        first_used DATE, last_used DATE, use_count INTEGER DEFAULT 0, tags TEXT)""")
    conn.commit(); conn.close()

def get_used():
    if not os.path.exists(DB_PATH): return {}
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT topic, use_count FROM topic_history WHERE last_used >= ?",
        ((datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),))
    return {r[0]: r[1] for r in cursor.fetchall()}

def find_topics(count=10, min_heat=100000):
    init_db()
    used = get_used()
    result = []
    for topic, heat, cat in TOPICS:
        if heat < min_heat: continue
        is_used = topic in used
        result.append({"topic": topic, "heat": heat, "category": cat, "is_used": is_used, "use_count": used.get(topic, 0)})
    result.sort(key=lambda x: (-x["heat"], not x["is_used"]))
    return result[:count]

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--min-heat", type=int, default=100000)
    args = parser.parse_args()
    
    topics = find_topics(args.count, args.min_heat)
    print(f"\n🔥 热点话题推荐（共 {len(topics)} 个）\n" + "-" * 50)
    for i, t in enumerate(topics, 1):
        status = "✅" if not t["is_used"] else f"⚠️ 已用{t['use_count']}次"
        print(f"{i}. [{t['heat']//10000}万热度] {t['topic']} {status}")