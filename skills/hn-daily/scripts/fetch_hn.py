#!/usr/bin/env python3
"""
Hacker News Top Stories Fetcher
抓取 HN Top Stories，支持关键词过滤和缓存
"""

import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

# 从环境变量读取代理，支持 HTTP_PROXY / HTTPS_PROXY / ALL_PROXY
def get_proxies():
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('HTTP_PROXY') or os.environ.get('ALL_PROXY')
    if proxy:
        return {"http": proxy, "https": proxy}
    return None

DEFAULT_CONFIG = {
    "limit": 10,
    "min_score": 50,
    "filter_keywords": [
        "ai", "artificial intelligence", "llm", "gpt", "claude", "openai", "anthropic",
        "programming", "python", "javascript", "rust", "go", "typescript",
        "startup", "entrepreneur", "business", "productivity",
        "machine learning", "deep learning", "neural",
        "open source", "github", "developer", "coding"
    ],
    "cache_duration_hours": 4
}

def get_cache_path():
    cache_dir = Path.home() / ".cache" / "hn-daily"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "hn_cache.json"

def load_cache():
    cache_path = get_cache_path()
    if not cache_path.exists():
        return None
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        cached_time = cache.get('timestamp', 0)
        if time.time() - cached_time > DEFAULT_CONFIG['cache_duration_hours'] * 3600:
            return None
        return cache.get('stories', [])
    except Exception:
        return None

def save_cache(stories):
    try:
        with open(get_cache_path(), 'w', encoding='utf-8') as f:
            json.dump({'timestamp': time.time(), 'stories': stories}, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def fetch_top_stories(limit=50):
    try:
        resp = requests.get(f"{HN_API_BASE}/topstories.json", timeout=10, proxies=get_proxies())
        resp.raise_for_status()
        return resp.json()[:limit]
    except Exception as e:
        print(f"[HN] 获取 Top Stories 失败: {e}")
        return []

def fetch_story_details(story_id):
    try:
        resp = requests.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10, proxies=get_proxies())
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None

def matches_keywords(story, keywords):
    text = (story.get('title', '') + ' ' + story.get('text', '')[:200]).lower()
    for kw in keywords:
        if kw.lower() in text:
            return True, kw
    return False, None

def filter_stories(stories, config=None):
    config = config or DEFAULT_CONFIG
    filtered = []
    for story in stories:
        if not story or story.get('score', 0) < config['min_score']:
            continue
        matches, kw = matches_keywords(story, config['filter_keywords'])
        filtered.append({
            'id': story.get('id'),
            'title': story.get('title'),
            'url': story.get('url'),
            'score': story.get('score', 0),
            'by': story.get('by'),
            'time': story.get('time'),
            'descendants': story.get('descendants', 0),
            'matched_keyword': kw if matches else None,
            'is_tech_related': matches
        })
    filtered.sort(key=lambda x: x['score'], reverse=True)
    tech = [s for s in filtered if s['is_tech_related']]
    other = [s for s in filtered if not s['is_tech_related']][:3]
    return (tech + other)[:config['limit']]

def format_output(stories, format='text'):
    if not stories:
        return "📰 今日 HN：暂无匹配的技术新闻"
    
    if format == 'json':
        return json.dumps(stories, ensure_ascii=False, indent=2)
    
    lines = ["📰 Hacker News 精选\n"]
    for i, s in enumerate(stories[:10], 1):
        tag = f"[{s['matched_keyword'].upper()}] " if s.get('matched_keyword') else ""
        lines.append(f"{i}. {tag}{s['title']}")
        if s.get('url'):
            lines.append(f"   🔗 {s['url']}")
        lines.append(f"   👍 {s['score']} 分 | 💬 {s.get('descendants', 0)} 评论\n")
    return "\n".join(lines)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch Hacker News top stories')
    parser.add_argument('--limit', type=int, default=10, help='Number of stories to return')
    parser.add_argument('--min-score', type=int, default=50, help='Minimum score filter')
    parser.add_argument('--no-cache', action='store_true', help='Skip cache')
    parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')
    args = parser.parse_args()

    config = {**DEFAULT_CONFIG, 'limit': args.limit, 'min_score': args.min_score}

    if not args.no_cache:
        cached = load_cache()
        if cached:
            print(format_output(cached[:args.limit], args.format))
            return

    story_ids = fetch_top_stories(50)
    if not story_ids:
        print("[HN] 获取失败")
        return

    stories = [fetch_story_details(sid) for sid in story_ids]
    stories = [s for s in stories if s]
    filtered = filter_stories(stories, config)
    save_cache(filtered)
    print(format_output(filtered, args.format))

if __name__ == "__main__":
    main()
