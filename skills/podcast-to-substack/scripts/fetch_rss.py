#!/usr/bin/env python3
"""Fetch recent podcast episodes from an RSS feed."""

import sys
import json
import re
from datetime import datetime, timedelta, timezone

try:
    import feedparser
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser", "-q"])
    import feedparser


def extract_episode_number(title: str) -> str:
    """Extract episode number from title like 'Episode 123: ...' or '123 - ...'."""
    m = re.match(r"(?:Episode\s+)?#?(\d+)", title, re.IGNORECASE)
    return m.group(1) if m else ""


def fetch_episodes(rss_url: str, days_back: int = 7) -> list:
    feed = feedparser.parse(rss_url)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    episodes = []

    for entry in feed.entries:
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

        if published and published < cutoff:
            continue

        title = entry.get("title", "")
        episodes.append({
            "title": title,
            "episode_number": extract_episode_number(title),
            "published": published.isoformat() if published else "",
            "link": entry.get("link", ""),
            "description": entry.get("summary", entry.get("description", "")),
        })

    return episodes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: fetch_rss.py <RSS_URL> [days_back]", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 7

    result = fetch_episodes(url, days)
    print(json.dumps(result, indent=2))
