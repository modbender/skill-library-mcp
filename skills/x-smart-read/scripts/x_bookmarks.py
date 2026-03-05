#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) bookmarks — save, list, and manage bookmarked posts."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import tweepy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x_common import (
    DATA_DIR, load_config, get_client,
    track_usage, budget_warning, check_budget,
    format_time, time_ago, format_number, handle_api_error,
)

BOOKMARKS_PATH = DATA_DIR / "bookmarks.json"

TWEET_FIELDS = [
    "created_at", "public_metrics", "text", "author_id",
    "conversation_id", "referenced_tweets",
]

USER_FIELDS = ["username", "name", "public_metrics"]


def load_store() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if BOOKMARKS_PATH.exists():
        return json.loads(BOOKMARKS_PATH.read_text())
    return {}


def save_store(store: dict):
    BOOKMARKS_PATH.write_text(json.dumps(store, indent=2))


def cmd_list(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        print("[DRY RUN] x_bookmarks.py list")
        print(f"  Would cost: ~$0.005 (1 tweet read)")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    store = load_store()

    try:
        resp = client.get_bookmarks(
            max_results=min(args.max, 100),
            tweet_fields=TWEET_FIELDS,
            expansions=["author_id"],
            user_fields=USER_FIELDS,
            user_auth=True,
        )
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(tweet_reads=1)
    budget_warning(config, suppress=suppress)

    # Build author lookup
    authors = {}
    if resp.includes and "users" in resp.includes:
        for user in resp.includes["users"]:
            authors[str(user.id)] = {
                "username": user.username,
                "name": user.name,
                "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
            }

    if not resp.data:
        print("No bookmarks found.")
        print(f"\n---\nEst. API cost: ~$0.005 (1 tweet read)")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")
        return

    # Store and display
    for tweet in resp.data:
        tid = str(tweet.id)
        author = authors.get(str(tweet.author_id), {})
        store[tid] = {
            "id": tid,
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
            "author_id": str(tweet.author_id) if tweet.author_id else "",
            "author_username": author.get("username", "unknown"),
            "author_name": author.get("name", ""),
            "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
    save_store(store)

    print(f"Your Bookmarks ({len(resp.data)} saved)")
    print("=" * 50)

    for i, tweet in enumerate(resp.data, 1):
        tid = str(tweet.id)
        b = store[tid]
        author_handle = b.get("author_username", "unknown")
        created = b.get("created_at", "")

        date_str = ""
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                date_str = dt.strftime("%b %d, %Y")
            except (ValueError, TypeError):
                date_str = created

        text = b.get("text", "")
        if len(text) > 200:
            text = text[:197] + "..."

        pm = b.get("metrics", {})
        likes = pm.get("like_count", 0)
        retweets = pm.get("retweet_count", 0)
        replies = pm.get("reply_count", 0)
        impressions = pm.get("impression_count", 0)

        metrics_parts = []
        if likes:
            metrics_parts.append(f"♥ {format_number(likes)}")
        if retweets:
            metrics_parts.append(f"🔁 {format_number(retweets)}")
        if replies:
            metrics_parts.append(f"💬 {format_number(replies)}")
        if impressions:
            metrics_parts.append(f"📊 {format_number(impressions)}")

        print(f"{i}. @{author_handle} · {date_str}")
        print(f"   \"{text}\"")
        if metrics_parts:
            print(f"   {'  '.join(metrics_parts)}")
        print(f"   https://x.com/{author_handle}/status/{tid}")
        print()

    print(f"---\nEst. API cost: ~$0.005 (1 tweet read)")
    print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def cmd_add(args):
    config = load_config()
    if not config:
        return

    suppress = args.no_budget

    if args.dry_run:
        print(f"[DRY RUN] x_bookmarks.py add {args.tweet_id}")
        print(f"  Would cost: $0 (bookmark is a free write action)")
        return

    client = get_client(config)

    try:
        client.bookmark(args.tweet_id, user_auth=True)
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    track_usage()  # Free action, but log it
    budget_warning(config, suppress=suppress)
    print(f"Bookmarked: https://x.com/i/status/{args.tweet_id}")


def cmd_remove(args):
    config = load_config()
    if not config:
        return

    suppress = args.no_budget

    if args.dry_run:
        print(f"[DRY RUN] x_bookmarks.py remove {args.tweet_id}")
        print(f"  Would cost: $0 (remove bookmark is a free write action)")
        return

    client = get_client(config)

    try:
        client.remove_bookmark(args.tweet_id, user_auth=True)
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    # Remove from local store too
    store = load_store()
    if args.tweet_id in store:
        del store[args.tweet_id]
        save_store(store)

    track_usage()  # Free action, but log it
    budget_warning(config, suppress=suppress)
    print(f"Removed bookmark: {args.tweet_id}")


def main():
    parser = argparse.ArgumentParser(description="X bookmarks — save and manage bookmarked posts")
    parser.add_argument("--force", action="store_true", help="Override daily budget guard")
    parser.add_argument("--no-budget", action="store_true", help="Skip all budget checks and warnings")
    parser.add_argument("--dry-run", action="store_true", help="Show estimated cost without making API calls")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_p = subparsers.add_parser("list", help="List your bookmarks")
    list_p.add_argument("--max", type=int, default=20, help="Max bookmarks to show (default: 20)")

    add_p = subparsers.add_parser("add", help="Bookmark a post")
    add_p.add_argument("tweet_id", help="Tweet ID to bookmark")

    remove_p = subparsers.add_parser("remove", help="Remove a bookmark")
    remove_p.add_argument("tweet_id", help="Tweet ID to remove from bookmarks")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "remove":
        cmd_remove(args)


if __name__ == "__main__":
    main()
