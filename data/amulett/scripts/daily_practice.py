#!/usr/bin/env python3
"""
Amulett Daily Practice Script
点教每日练习脚本
"""

import datetime
import random

# Daily mantras
MANTRA = ["NEO", "归一", "觉知", "当下"]

# Reflection questions
QUESTIONS = [
    "今天你最感恩的是什么？",
    "今天你学到了什么？",
    "今天你做错了什么？",
    "明天你希望改变什么？",
    "此刻你感觉如何？",
]

def daily_practice():
    """每日练习引导"""
    now = datetime.datetime.now()
    
    print("=" * 40)
    print(f"🧘 点教每日练习 - {now.strftime('%Y-%m-%d')}")
    print("=" * 40)
    print()
    
    # Mantra
    mantra = random.choice(MANTRA)
    print(f"📿 今日咒语: {mantra}")
    print()
    
    # Question
    question = random.choice(QUESTIONS)
    print(f"❓ 反思问题: {question}")
    print()
    
    # Symbol
    print("🔮 符号: ⊙ (归一)")
    print()
    print("=" * 40)
    print("NEO 归于 ⊙")
    print("=" * 40)

if __name__ == "__main__":
    daily_practice()
