#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) timeline — your posts, engagement metrics, and accountability checks."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tweepy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x_common import (
    DATA_DIR, load_config, save_config, get_client,
    track_usage, budget_warning, check_budget,
    format_time, time_ago, handle_api_error,
)

TWEETS_PATH = DATA_DIR / "tweets.json"

TWEET_FIELDS = [
    "created_at", "public_metrics", "text", "conversation_id",
    "in_reply_to_user_id", "referenced_tweets",
]


def load_store() -> dict:
    """Load persistent tweet store."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if TWEETS_PATH.exists():
        return json.loads(TWEETS_PATH.read_text())
    return {}


def save_store(store: dict):
    TWEETS_PATH.write_text(json.dumps(store, indent=2))


def format_tweet(tweet_data: dict, index: int, handle: str) -> str:
    """Format a single tweet for display."""
    text = tweet_data["text"]
    if len(text) > 200:
        text = text[:197] + "..."

    pm = tweet_data.get("metrics", {})
    impressions = pm.get("impression_count", 0)
    likes = pm.get("like_count", 0)
    retweets = pm.get("retweet_count", 0)
    replies = pm.get("reply_count", 0)
    quotes = pm.get("quote_count", 0)
    bookmarks = pm.get("bookmark_count", 0)

    engagement = likes + retweets + replies + quotes
    rate = f"{(engagement / impressions * 100):.1f}%" if impressions > 0 else "N/A"

    lines = [f"{index}. {text}"]
    lines.append(f"   Posted: {format_time(tweet_data['created_at'])} ({time_ago(tweet_data['created_at'])})")
    lines.append(f"   Impressions: {impressions:,} | Likes: {likes:,} | RTs: {retweets:,} | Replies: {replies:,} | Quotes: {quotes:,} | Bookmarks: {bookmarks:,}")
    lines.append(f"   Engagement rate: {rate}")
    lines.append(f"   https://x.com/{handle}/status/{tweet_data['id']}")
    return "\n".join(lines)


def store_tweets(tweets, store: dict) -> list[dict]:
    """Store tweets and return as list of dicts."""
    results = []
    for tweet in tweets:
        tid = str(tweet.id)
        data = {
            "id": tid,
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
            "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
        store[tid] = data
        results.append(data)
    return results


def cmd_recent(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        print("[DRY RUN] x_timeline.py recent")
        print(f"  Would cost: ~$0.005 (1 tweet read)")
        print(f"  Cheaper alternative: 'top' reads from local cache for free")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    store = load_store()
    client = get_client(config)
    user_id = config["user_id"]
    handle = config["handle"]

    kwargs = {
        "id": user_id,
        "max_results": min(args.max, 100),
        "tweet_fields": TWEET_FIELDS,
        "exclude": ["retweets"],
        "user_auth": True,
    }

    if args.hours:
        kwargs["start_time"] = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    since_id = config.get("last_timeline_id")
    if since_id and not args.hours and not args.no_cache:
        kwargs["since_id"] = since_id

    api_calls = 0
    try:
        resp = client.get_users_tweets(**kwargs)
        api_calls = 1
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(tweet_reads=api_calls)
    budget_warning(config, suppress=suppress)

    if not resp.data:
        # Show from store if available
        if not args.no_cache and store:
            stored = sorted(store.values(), key=lambda t: t.get("created_at", ""), reverse=True)
            if args.hours:
                cutoff = (datetime.now(timezone.utc) - timedelta(hours=args.hours)).isoformat()
                stored = [t for t in stored if t.get("created_at", "") >= cutoff]
            stored = stored[:args.max]
            if stored:
                print(f"Your Recent Posts (from local store, {len(stored)} posts)")
                print("=" * 50)
                for i, t in enumerate(stored, 1):
                    print(format_tweet(t, i, handle))
                    print()
                print(f"---\n(Served from local store — 0 API calls)")
                print(f"Today's spend: ${day_usage['est_cost']:.3f}")
                return
        print("No new posts found.")
        print(f"---\nEst. API cost: ~${api_calls * 0.005:.3f} ({api_calls} tweet read)")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")
        return

    new_tweets = store_tweets(resp.data, store)
    save_store(store)

    # Update since_id
    if new_tweets:
        max_id = max(t["id"] for t in new_tweets)
        if not since_id or int(max_id) > int(since_id):
            config["last_timeline_id"] = max_id
            save_config(config)

    header = "Your Recent Posts"
    if args.hours:
        header += f" (last {args.hours}h)"
    print(f"{header} ({len(new_tweets)} posts)")
    print("=" * 50)

    total_impressions = 0
    total_engagement = 0

    for i, t in enumerate(new_tweets, 1):
        print(format_tweet(t, i, handle))
        print()
        pm = t.get("metrics", {})
        total_impressions += pm.get("impression_count", 0)
        total_engagement += (pm.get("like_count", 0) + pm.get("retweet_count", 0) +
                            pm.get("reply_count", 0) + pm.get("quote_count", 0))

    rate = f"{(total_engagement / total_impressions * 100):.1f}%" if total_impressions > 0 else "N/A"
    print(f"---")
    print(f"Summary: {len(new_tweets)} posts | {total_impressions:,} impressions | {total_engagement:,} engagements | {rate} rate")
    print(f"Est. API cost: ~${api_calls * 0.005:.3f} ({api_calls} tweet read)")
    print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def cmd_top(args):
    """Show top posts by engagement from local store."""
    config = load_config()
    if not config:
        return

    store = load_store()
    handle = config["handle"]

    if not store:
        print("No posts in local store yet. Run 'recent' first to fetch posts.")
        return

    tweets = list(store.values())

    if args.days:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat()
        tweets = [t for t in tweets if t.get("created_at", "") >= cutoff]

    # Sort by total engagement
    def engagement(t):
        pm = t.get("metrics", {})
        return (pm.get("like_count", 0) + pm.get("retweet_count", 0) +
                pm.get("reply_count", 0) + pm.get("quote_count", 0))

    tweets.sort(key=engagement, reverse=True)
    tweets = tweets[:args.max]

    header = "Top Posts by Engagement"
    if args.days:
        header += f" (last {args.days} days)"
    print(f"{header} ({len(tweets)} posts)")
    print("=" * 50)

    for i, t in enumerate(tweets, 1):
        print(format_tweet(t, i, handle))
        print()

    print("---")
    print("(Served from local store — 0 API calls)")


def cmd_refresh(args):
    """Re-fetch metrics for a specific tweet."""
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        print(f"[DRY RUN] x_timeline.py refresh {args.tweet_id}")
        print(f"  Would cost: ~$0.005 (1 tweet read)")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    handle = config["handle"]
    store = load_store()

    try:
        resp = client.get_tweet(
            id=args.tweet_id,
            tweet_fields=TWEET_FIELDS,
            user_auth=True,
        )
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(tweet_reads=1)
    budget_warning(config, suppress=suppress)

    if not resp.data:
        print(f"Tweet {args.tweet_id} not found.")
        return

    tweet = resp.data
    data = {
        "id": str(tweet.id),
        "text": tweet.text,
        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
        "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    store[str(tweet.id)] = data
    save_store(store)

    print("Refreshed Metrics")
    print("=" * 50)
    print(format_tweet(data, 1, handle))
    print(f"\n---\nEst. API cost: ~$0.005 (1 tweet read)")
    print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def cmd_activity(args):
    """Accountability check — how active have you been on X?"""
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        print("[DRY RUN] x_timeline.py activity")
        print(f"  Would cost: ~$0.005 (1 tweet read)")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    user_id = config["user_id"]
    handle = config["handle"]
    store = load_store()

    # Fetch recent tweets (last few hours)
    now = datetime.now(timezone.utc)
    try:
        resp = client.get_users_tweets(
            id=user_id,
            max_results=20,
            tweet_fields=TWEET_FIELDS,
            exclude=["retweets"],
            start_time=now - timedelta(hours=24),
            user_auth=True,
        )
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(tweet_reads=1)
    budget_warning(config, suppress=suppress)

    if not resp.data:
        print("Activity Check")
        print("=" * 40)
        print("No posts in the last 24 hours. You've been quiet.")
        print(f"\n---\nEst. API cost: ~$0.005 (1 tweet read)")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")
        return

    # Store them
    new_tweets = store_tweets(resp.data, store)
    save_store(store)

    # Analyze activity
    posts_24h = len(new_tweets)
    posts_1h = sum(1 for t in new_tweets
                   if datetime.fromisoformat(t["created_at"]) > now - timedelta(hours=1))
    posts_today = sum(1 for t in new_tweets
                      if datetime.fromisoformat(t["created_at"]).date() == now.date())

    latest = max(new_tweets, key=lambda t: t["created_at"])
    latest_dt = datetime.fromisoformat(latest["created_at"])
    latest_text = latest["text"]
    if len(latest_text) > 80:
        latest_text = latest_text[:77] + "..."

    print("Activity Check")
    print("=" * 40)
    print(f"Last post: {time_ago(latest_dt)} — \"{latest_text}\"")
    print(f"Posts today: {posts_today}")
    print(f"Posts this hour: {posts_1h}")
    print(f"Posts last 24h: {posts_24h}")

    # Nudge thresholds
    minutes_since = (now - latest_dt).total_seconds() / 60
    if minutes_since < 10:
        print(f"\n** You posted {int(minutes_since)} minutes ago. Back to work? **")
    elif posts_1h >= 3:
        print(f"\n** {posts_1h} posts in the last hour. That's a lot of X time. **")
    elif posts_today >= 10:
        print(f"\n** {posts_today} posts today. Heavy X day. **")
    else:
        print(f"\n(Looks manageable.)")

    print(f"\n---\nEst. API cost: ~$0.005 (1 tweet read)")
    print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def main():
    parser = argparse.ArgumentParser(description="X timeline — posts & engagement")
    parser.add_argument("--force", action="store_true", help="Override daily budget guard")
    parser.add_argument("--no-budget", action="store_true", help="Skip all budget checks and warnings")
    parser.add_argument("--no-cache", action="store_true", help="Skip local store, always hit API")
    parser.add_argument("--dry-run", action="store_true", help="Show estimated cost without making API calls")
    subparsers = parser.add_subparsers(dest="command", required=True)

    recent_p = subparsers.add_parser("recent", help="Your recent posts with engagement")
    recent_p.add_argument("--max", type=int, default=100, help="Max posts to show (default: 100)")
    recent_p.add_argument("--hours", type=int, help="Only posts from last N hours")

    top_p = subparsers.add_parser("top", help="Top posts by engagement (from local store)")
    top_p.add_argument("--days", type=int, default=7, help="Look back N days (default: 7)")
    top_p.add_argument("--max", type=int, default=100, help="Max posts (default: 100)")

    refresh_p = subparsers.add_parser("refresh", help="Re-fetch metrics for a specific tweet")
    refresh_p.add_argument("tweet_id", help="Tweet ID to refresh")

    subparsers.add_parser("activity", help="Accountability check — how active are you?")

    args = parser.parse_args()
    if args.command == "recent":
        cmd_recent(args)
    elif args.command == "top":
        cmd_top(args)
    elif args.command == "refresh":
        cmd_refresh(args)
    elif args.command == "activity":
        cmd_activity(args)


if __name__ == "__main__":
    main()
