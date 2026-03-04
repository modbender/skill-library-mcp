"""
Recipe: Hacker News Thread Tracker
===================================
Track a list of HN threads and get notified when comment counts change.
Great for monitoring Show HN / Ask HN posts you've submitted or commented on.

Usage:
    # Track a thread
    python3 recipes/hn_tracker.py track 47147183

    # Check for new replies
    python3 recipes/hn_tracker.py check

    # See all tracked threads
    python3 recipes/hn_tracker.py list
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from undersheet import load_adapter, load_state, save_state, track_thread, get_unread_threads

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    adapter = load_adapter("hackernews")
    state   = load_state("hackernews")

    if cmd == "track":
        if len(sys.argv) < 3:
            print("Usage: hn_tracker.py track <item_id>")
            sys.exit(1)
        item_id = sys.argv[2]
        threads = adapter.get_threads([item_id])
        if not threads:
            print(f"Could not fetch item {item_id}")
            sys.exit(1)
        t = threads[0]
        track_thread(state, item_id, t["comment_count"], title=t["title"], url=t["url"])
        save_state("hackernews", state)
        print(f"Tracking: {t['title']}")
        print(f"  {t['comment_count']} comments — {t['url']}")

    elif cmd == "check":
        unread = get_unread_threads(adapter, state)
        save_state("hackernews", state)
        if unread:
            for t in unread:
                print(f"+{t['new_replies']} new comments — {t['title']}")
                print(f"  {t['url']}")
        else:
            print("No new comments on tracked threads.")

    elif cmd == "list":
        threads = state.get("threads", {})
        if not threads:
            print("No tracked threads. Use: hn_tracker.py track <item_id>")
        for tid, meta in threads.items():
            print(f"  [{meta.get('comment_count',0)}💬] {meta.get('title', tid)}")
            print(f"       {meta.get('url','')}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
