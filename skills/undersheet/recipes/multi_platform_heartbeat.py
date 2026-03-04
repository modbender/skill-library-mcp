"""
Recipe: Multi-Platform Heartbeat
================================
Run a single heartbeat that checks all your platforms at once.
Drop this in your HEARTBEAT.md or run it as a cron job.

Usage:
    python3 recipes/multi_platform_heartbeat.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from undersheet import load_adapter, load_state, save_state, get_unread_threads, get_new_feed_posts
from datetime import datetime, timezone

PLATFORMS = [
    {"name": "hackernews", "min_score": 50},
    {"name": "moltbook",   "min_score": 3},
    # {"name": "reddit",   "min_score": 10},   # uncomment when configured
    # {"name": "discord",  "min_score": 0},    # uncomment when configured
]

total_unread = 0
total_new    = 0

for cfg in PLATFORMS:
    platform = cfg["name"]
    try:
        adapter  = load_adapter(platform)
        state    = load_state(platform)
    except SystemExit:
        print(f"[{platform}] adapter not installed, skipping")
        continue
    except Exception as e:
        print(f"[{platform}] error loading: {e}")
        continue

    unread = get_unread_threads(adapter, state)
    new_posts = get_new_feed_posts(adapter, state, min_score=cfg.get("min_score", 0), limit=5)

    if unread or new_posts:
        print(f"\n── {platform.upper()} ──────────────────")
        for t in unread:
            print(f"  💬 +{t['new_replies']} — {t['title'][:60]}")
            total_unread += 1
        for p in new_posts:
            print(f"  📰 [{p.get('score',0)}↑] {p.get('title','')[:60]}")
            total_new += 1

    state["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
    save_state(platform, state)

print(f"\n── Summary ──────────────────────────")
print(f"  {total_unread} thread(s) with new replies")
print(f"  {total_new} new feed post(s)")
print(f"  {datetime.now(timezone.utc).strftime('%H:%M UTC')}")
