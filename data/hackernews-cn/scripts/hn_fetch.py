#!/usr/bin/env python3
"""
Hacker News 获取脚本
Hacker News Fetcher
"""

import json
import sys
from datetime import datetime

def get_hn_top(limit=10):
    """获取 HN Top Stories（使用模拟数据）"""
    mock_stories = [
        {"rank": 1, "title": "AI Agents Are Getting Scary Good", "points": 892, "comments": 456, "url": "https://example.com/ai-agents", "user": "pg"},
        {"rank": 2, "title": "Show HN: I Built a Markdown Editor in Rust", "points": 654, "comments": 234, "url": "https://example.com/md-editor", "user": "rustdev"},
        {"rank": 3, "title": "The State of Rust 2026", "points": 543, "comments": 189, "url": "https://example.com/rust-2026", "user": "steveklabnik"},
        {"rank": 4, "title": "Why I Left Big Tech for a Startup", "points": 487, "comments": 312, "url": "https://example.com/why-left", "user": "exgoogler"},
        {"rank": 5, "title": "Ask HN: What's Your Favorite CLI Tool?", "points": 421, "comments": 567, "url": "", "user": "curious_dev"},
        {"rank": 6, "title": "OpenAI Announces GPT-5", "points": 1205, "comments": 892, "url": "https://example.com/gpt5", "user": "sama"},
        {"rank": 7, "title": "A Deep Dive into Linux Memory Management", "points": 356, "comments": 145, "url": "https://example.com/linux-mm", "user": "kernel_hacker"},
        {"rank": 8, "title": "Launch HN: New Developer Tool (YC W26)", "points": 298, "comments": 167, "url": "https://example.com/launch", "user": "ycombinator"},
        {"rank": 9, "title": "The Future of Remote Work", "points": 276, "comments": 423, "url": "https://example.com/remote", "user": "remote_worker"},
        {"rank": 10, "title": "PostgreSQL 17 Released", "points": 234, "comments": 98, "url": "https://example.com/pg17", "user": "postgres_fan"},
    ]
    return mock_stories[:limit]

def format_output(data):
    output = "🄪 Hacker News Top Stories\n\n"
    for item in data:
        url_hint = f"\n   {item['url']}" if item['url'] else ""
        output += f"{item['rank']}. {item['title']}\n"
        output += f"   👍 {item['points']} points | 💬 {item['comments']} comments | by {item['user']}{url_hint}\n\n"
    return output

def main():
    limit = 10
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
    
    data = get_hn_top(limit=limit)
    
    if "--json" in sys.argv or "-j" in sys.argv:
        print(json.dumps({"data": data}, ensure_ascii=False, indent=2))
    else:
        print(format_output(data))

if __name__ == "__main__":
    main()
