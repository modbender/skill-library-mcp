#!/usr/bin/env python3
"""TechPulse - мониторинг трендов"""

import json
import urllib.request
from datetime import datetime

CATEGORIES = {
    "iot": {"subreddits": ["homeautomation", "IOT"], "icon": "🏠"},
    "ev": {"subreddits": ["electricvehicles", "teslamotors"], "icon": "⚡"},
    "games": {"subreddits": ["gaming", "gamedev"], "icon": "🎮"},
    "diy": {"subreddits": ["arduino", "raspberry_pi"], "icon": "🔧"},
    "tech": {"subreddits": ["technology", "artificial"], "icon": "🚀"}
}

def fetch_reddit(subreddit, limit=5):
    """Получает посты из Reddit"""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "TechPulse/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["data"]["children"]
    except:
        return []

def analyze_category(category):
    """Анализирует категорию"""
    cat = CATEGORIES.get(category, CATEGORIES["tech"])
    posts = []
    
    for sub in cat["subreddits"]:
        for p in fetch_reddit(sub, 3):
            post = p["data"]
            posts.append({
                "title": post["title"][:80],
                "score": post["score"],
                "url": f"https://reddit.com{post['permalink']}"
            })
    
    posts.sort(key=lambda x: x["score"], reverse=True)
    return posts[:3]

def generate_report(category="all"):
    """Генерирует отчёт"""
    lines = [f"📊 TECHPULSE — {datetime.now().strftime('%d.%m.%Y')}", ""]
    
    cats = [category] if category in CATEGORIES else list(CATEGORIES.keys())
    
    for cat in cats:
        info = CATEGORIES[cat]
        posts = analyze_category(cat)
        
        lines.append(f"{info['icon']} {cat.upper()}")
        for p in posts:
            lines.append(f"  • {p['title']} ({p['score']}↑)")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    cat = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(generate_report(cat))
