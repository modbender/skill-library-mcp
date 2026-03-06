#!/usr/bin/env python3
"""Recommend topics"""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from find_topics import find_topics, init_db

if __name__ == "__main__":
    init_db()
    topics = find_topics(5)
    print(f"\n🎯 智能推荐\n" + "="*50)
    for i, t in enumerate(topics, 1):
        stars = "⭐⭐⭐⭐⭐" if not t["is_used"] else "⭐"
        print(f"{i}. {t['topic']} [{t['heat']//10000}万] {stars}")