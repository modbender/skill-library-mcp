#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) mentions — who's replying to and talking about you."""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tweepy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x_common import (
    DATA_DIR, USAGE_PATH, load_config, save_config, get_client,
    track_usage, budget_warning, check_budget,
    format_time, time_ago, format_number, handle_api_error,
)

MENTIONS_PATH = DATA_DIR / "mentions.json"

TWEET_FIELDS = [
    "created_at", "public_metrics", "text", "author_id",
    "conversation_id", "in_reply_to_user_id", "referenced_tweets",
]

USER_FIELDS = ["username", "name", "verified", "public_metrics"]


def load_store() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if MENTIONS_PATH.exists():
        return json.loads(MENTIONS_PATH.read_text())
    return {}


def save_store(store: dict):
    MENTIONS_PATH.write_text(json.dumps(store, indent=2))


def cmd_recent(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        cost = "$0.005" if not args.context else "$0.005-0.030"
        print(f"[DRY RUN] x_mentions.py recent")
        print(f"  Would cost: ~{cost} (1 tweet read{' + context lookups' if args.context else ''})")
        if args.context:
            print(f"  Tip: skip --context to save ~$0.025 — only adds parent tweet text")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    store = load_store()
    client = get_client(config)
    user_id = config["user_id"]

    kwargs = {
        "id": user_id,
        "max_results": min(args.max, 100),
        "tweet_fields": TWEET_FIELDS,
        "expansions": ["author_id"],
        "user_fields": USER_FIELDS,
        "user_auth": True,
    }

    if args.hours:
        kwargs["start_time"] = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    since_id = config.get("last_mention_id")
    if since_id and not args.hours and not args.no_cache:
        kwargs["since_id"] = since_id

    api_calls = 0
    try:
        resp = client.get_users_mentions(**kwargs)
        api_calls = 1
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(tweet_reads=api_calls)
    budget_warning(config, suppress=suppress)

    # Build author lookup from includes
    authors = {}
    if resp.includes and "users" in resp.includes:
        for user in resp.includes["users"]:
            authors[str(user.id)] = {
                "username": user.username,
                "name": user.name,
                "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
            }

    if not resp.data:
        if not args.no_cache and store:
            stored = sorted(store.values(), key=lambda t: t.get("created_at", ""), reverse=True)
            if args.hours:
                cutoff = (datetime.now(timezone.utc) - timedelta(hours=args.hours)).isoformat()
                stored = [t for t in stored if t.get("created_at", "") >= cutoff]
            stored = stored[:args.max]
            if stored:
                print(f"Your Mentions (from local store, {len(stored)})")
                print("=" * 50)
                for i, m in enumerate(stored, 1):
                    print_mention(m, i)
                print(f"---\n(Served from local store — 0 API calls)")
                print(f"Today's spend: ${day_usage['est_cost']:.3f}")
                return
        print("No new mentions found.")
        print(f"---\nEst. API cost: ~${api_calls * 0.005:.3f}")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")
        return

    # Store mentions
    mentions = []
    for tweet in resp.data:
        tid = str(tweet.id)
        author = authors.get(str(tweet.author_id), {})
        ref_type = "mention"
        if tweet.referenced_tweets:
            for ref in tweet.referenced_tweets:
                if ref.type == "replied_to":
                    ref_type = "reply"
                elif ref.type == "quoted":
                    ref_type = "quote"

        data = {
            "id": tid,
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
            "author_id": str(tweet.author_id),
            "author_username": author.get("username", "unknown"),
            "author_name": author.get("name", ""),
            "author_followers": author.get("followers", 0),
            "type": ref_type,
            "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
            "stored_at": datetime.now(timezone.utc).isoformat(),
        }
        store[tid] = data
        mentions.append(data)

    save_store(store)

    # Update since_id
    if mentions:
        max_id = max(m["id"] for m in mentions)
        if not since_id or int(max_id) > int(since_id):
            config["last_mention_id"] = max_id
            save_config(config)

    # Context fetching (optional)
    context_calls = 0
    if args.context:
        context_limit = 5
        for m in mentions[:context_limit]:
            if m["type"] == "reply" and m.get("metrics", {}).get("reply_count", 0) >= 0:
                # Try to get the tweet being replied to
                try:
                    for ref in resp.data:
                        if str(ref.id) == m["id"] and ref.referenced_tweets:
                            parent_id = ref.referenced_tweets[0].id
                            parent_resp = client.get_tweet(
                                id=parent_id,
                                tweet_fields=["text", "author_id", "created_at"],
                                user_auth=True,
                            )
                            context_calls += 1
                            if parent_resp.data:
                                m["context_text"] = parent_resp.data.text
                            break
                except Exception:
                    pass
        if context_calls:
            track_usage(tweet_reads=context_calls)
            day_usage = json.loads(USAGE_PATH.read_text()).get(
                datetime.now(timezone.utc).strftime("%Y-%m-%d"), {})

    # Display
    header = "Your Mentions"
    if args.hours:
        header += f" (last {args.hours}h)"
    print(f"{header} ({len(mentions)})")
    print("=" * 50)

    type_counts = {"reply": 0, "quote": 0, "mention": 0}
    for i, m in enumerate(mentions, 1):
        print_mention(m, i)
        type_counts[m.get("type", "mention")] += 1

    total_calls = api_calls + context_calls
    total_cost = total_calls * 0.005
    print(f"---")
    print(f"Summary: {len(mentions)} mentions | {type_counts['reply']} replies, {type_counts['quote']} quotes, {type_counts['mention']} direct")
    if total_cost > 0.02:
        print(f"Est. API cost: ~${total_cost:.3f} ({total_calls} tweet reads) [$$$ EXPENSIVE]")
        print(f"  Tip: skip --context next time to reduce cost")
    else:
        print(f"Est. API cost: ~${total_cost:.3f} ({total_calls} tweet reads)")
    print(f"Today's spend: ${day_usage.get('est_cost', 0):.3f}")


def print_mention(m: dict, index: int):
    """Print a single mention."""
    author = f"@{m.get('author_username', 'unknown')}"
    followers = m.get("author_followers", 0)
    mtype = m.get("type", "mention")

    text = m["text"]
    if len(text) > 200:
        text = text[:197] + "..."

    type_label = {"reply": "replied to your post", "quote": "quoted your post", "mention": "mentioned you"}
    print(f"{index}. {author} {type_label.get(mtype, 'mentioned you')}:")
    print(f"   \"{text}\"")
    print(f"   Posted: {format_time(m['created_at'])} ({time_ago(m['created_at'])})")
    print(f"   Their followers: {format_number(followers)}")

    if "context_text" in m:
        ctx = m["context_text"]
        if len(ctx) > 100:
            ctx = ctx[:97] + "..."
        print(f"   In reply to: \"{ctx}\"")

    print(f"   https://x.com/{m.get('author_username', 'i')}/status/{m['id']}")
    print()


def main():
    parser = argparse.ArgumentParser(description="X mentions — replies & mentions")
    parser.add_argument("--force", action="store_true", help="Override daily budget guard")
    parser.add_argument("--no-budget", action="store_true", help="Skip all budget checks and warnings")
    parser.add_argument("--no-cache", action="store_true", help="Skip local store")
    parser.add_argument("--dry-run", action="store_true", help="Show estimated cost without making API calls")
    subparsers = parser.add_subparsers(dest="command", required=True)

    recent_p = subparsers.add_parser("recent", help="Recent mentions")
    recent_p.add_argument("--max", type=int, default=100, help="Max mentions (default: 100)")
    recent_p.add_argument("--hours", type=int, help="Only mentions from last N hours")
    recent_p.add_argument("--context", action="store_true", help="Fetch parent tweet for replies (costs extra)")

    args = parser.parse_args()
    if args.command == "recent":
        cmd_recent(args)


if __name__ == "__main__":
    main()
