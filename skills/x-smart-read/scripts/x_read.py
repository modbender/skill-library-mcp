#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) read — fetch any tweet or thread by URL or ID."""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import tweepy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x_common import (
    DATA_DIR, load_config, save_config, get_client,
    track_usage, budget_warning, check_budget,
    format_time, time_ago, format_number, handle_api_error,
)

TWEETS_PATH = DATA_DIR / "tweets.json"

TWEET_FIELDS = [
    "created_at", "public_metrics", "text", "conversation_id",
    "in_reply_to_user_id", "referenced_tweets", "author_id",
    "note_tweet",
]

USER_FIELDS = ["username", "name", "public_metrics"]

EXPANSIONS = [
    "author_id",
    "referenced_tweets.id",
    "referenced_tweets.id.author_id",
]


def parse_tweet_id(url_or_id: str) -> str | None:
    """Extract tweet ID from URL or bare ID."""
    # Bare numeric ID
    if url_or_id.strip().isdigit():
        return url_or_id.strip()
    # URL patterns: x.com/user/status/ID or twitter.com/user/status/ID
    match = re.search(r'(?:x\.com|twitter\.com)/\w+/status/(\d+)', url_or_id)
    if match:
        return match.group(1)
    return None


def load_store() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if TWEETS_PATH.exists():
        return json.loads(TWEETS_PATH.read_text())
    return {}


def save_store(store: dict):
    TWEETS_PATH.write_text(json.dumps(store, indent=2))


def format_tweet_display(tweet_data: dict, authors: dict, indent: str = "") -> str:
    """Format a tweet for display with author info."""
    author_id = tweet_data.get("author_id", "")
    author = authors.get(author_id, {})
    handle = author.get("username", "unknown")
    created = tweet_data.get("created_at", "")

    lines = []
    # Header
    date_str = ""
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            date_str = dt.strftime("%b %d, %Y")
        except (ValueError, TypeError):
            date_str = created
    lines.append(f"{indent}@{handle} · {date_str}")

    # Text — use note_tweet for long-form posts (>280 chars)
    note = tweet_data.get("note_tweet", {})
    text = note.get("text", "") if note else ""
    if not text:
        text = tweet_data.get("text", "")
    for text_line in text.split("\n"):
        lines.append(f"{indent}{text_line}")

    # Metrics
    pm = tweet_data.get("metrics", {})
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
        metrics_parts.append(f"📊 {format_number(impressions)} views")
    if metrics_parts:
        lines.append(f"{indent}{'  '.join(metrics_parts)}")

    # URL
    tweet_id = tweet_data.get("id", "")
    lines.append(f"{indent}https://x.com/{handle}/status/{tweet_id}")

    return "\n".join(lines)


def cmd_read(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    tweet_id = parse_tweet_id(args.tweet)
    if not tweet_id:
        print(f"Error: Could not parse tweet ID from '{args.tweet}'")
        print("Expected: tweet URL (https://x.com/user/status/ID) or bare ID")
        return

    if args.dry_run:
        cost = "$0.005" if not args.thread else "$0.005-0.010"
        print(f"[DRY RUN] x_read.py {tweet_id}")
        if args.thread:
            print(f"  Would cost: ~{cost} (1-2 tweet reads for thread)")
        else:
            print(f"  Would cost: ~{cost} (1 tweet read)")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    store = load_store()
    api_calls = 0

    # Fetch the target tweet
    try:
        resp = client.get_tweet(
            id=tweet_id,
            tweet_fields=TWEET_FIELDS,
            expansions=EXPANSIONS,
            user_fields=USER_FIELDS,
            user_auth=True,
        )
        api_calls += 1
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    if not resp.data:
        day_usage = track_usage(tweet_reads=api_calls)
        budget_warning(config, suppress=suppress)
        print(f"Tweet {tweet_id} not found.")
        print(f"\n---\nEst. API cost: ~${api_calls * 0.005:.3f}")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")
        return

    tweet = resp.data

    # Build author lookup from includes
    authors = {}
    if resp.includes and "users" in resp.includes:
        for user in resp.includes["users"]:
            authors[str(user.id)] = {
                "username": user.username,
                "name": user.name,
                "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
            }

    # Build referenced tweets lookup from includes
    ref_tweets = {}
    if resp.includes and "tweets" in resp.includes:
        for rt in resp.includes["tweets"]:
            rt_note = getattr(rt, "note_tweet", None)
            ref_tweets[str(rt.id)] = {
                "id": str(rt.id),
                "text": rt.text,
                "created_at": rt.created_at.isoformat() if rt.created_at else None,
                "author_id": str(rt.author_id) if rt.author_id else "",
                "metrics": dict(rt.public_metrics) if rt.public_metrics else {},
                **({"note_tweet": rt_note} if rt_note else {}),
            }

    # Store the tweet
    note_tweet = getattr(tweet, "note_tweet", None)
    tweet_data = {
        "id": str(tweet.id),
        "text": tweet.text,
        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
        "author_id": str(tweet.author_id) if tweet.author_id else "",
        "conversation_id": str(tweet.conversation_id) if tweet.conversation_id else None,
        "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
        **({"note_tweet": note_tweet} if note_tweet else {}),
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    store[str(tweet.id)] = tweet_data
    save_store(store)

    if args.thread:
        # Thread mode — fetch all tweets in the conversation
        thread_tweets = fetch_thread(client, tweet, tweet_data, authors, ref_tweets, store)
        api_calls += thread_tweets["api_calls"]

        day_usage = track_usage(tweet_reads=api_calls)
        budget_warning(config, suppress=suppress)

        print(f"Thread ({len(thread_tweets['tweets'])} posts)")
        print("=" * 50)
        for i, t in enumerate(thread_tweets["tweets"], 1):
            print(format_tweet_display(t, authors))
            if i < len(thread_tweets["tweets"]):
                print("  |")
        print(f"\n---\nEst. API cost: ~${api_calls * 0.005:.3f} ({api_calls} tweet reads)")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")
    else:
        day_usage = track_usage(tweet_reads=api_calls)
        budget_warning(config, suppress=suppress)

        # Single tweet display
        print(format_tweet_display(tweet_data, authors))

        # Show parent if this is a reply (from expansion, no extra cost)
        if tweet.referenced_tweets:
            for ref in tweet.referenced_tweets:
                ref_id = str(ref.id)
                if ref.type == "replied_to" and ref_id in ref_tweets:
                    parent = ref_tweets[ref_id]
                    parent_author = authors.get(parent.get("author_id", ""), {})
                    parent_handle = parent_author.get("username", "unknown")
                    parent_text = parent.get("text", "")
                    if len(parent_text) > 280:
                        parent_text = parent_text[:277] + "..."
                    print(f"\n↩️ Replying to @{parent_handle}: {parent_text}")
                elif ref.type == "quoted" and ref_id in ref_tweets:
                    quoted = ref_tweets[ref_id]
                    print(f"\n📎 Quoting:")
                    print(format_tweet_display(quoted, authors, indent="  "))

        print(f"\n---\nEst. API cost: ~${api_calls * 0.005:.3f} ({api_calls} tweet read)")
        print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def fetch_thread(client, tweet, tweet_data, authors, ref_tweets, store) -> dict:
    """Fetch all tweets in a thread/conversation."""
    conv_id = str(tweet.conversation_id) if tweet.conversation_id else str(tweet.id)
    author_id = str(tweet.author_id) if tweet.author_id else ""
    author_info = authors.get(author_id, {})
    author_username = author_info.get("username", "")

    extra_calls = 0
    thread_tweets = [tweet_data]

    # Check if tweet is within 7 days (can use search)
    tweet_dt = tweet.created_at if tweet.created_at else None
    within_7_days = False
    if tweet_dt:
        within_7_days = (datetime.now(timezone.utc) - tweet_dt).days < 7

    if within_7_days and author_username:
        # Use search for recent threads — one call gets all parts
        try:
            query = f"conversation_id:{conv_id} from:{author_username}"
            search_resp = client.search_recent_tweets(
                query=query,
                tweet_fields=TWEET_FIELDS,
                expansions=EXPANSIONS,
                user_fields=USER_FIELDS,
                max_results=100,
            )
            extra_calls += 1

            # Add authors from search includes
            if search_resp.includes and "users" in search_resp.includes:
                for user in search_resp.includes["users"]:
                    authors[str(user.id)] = {
                        "username": user.username,
                        "name": user.name,
                        "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
                    }

            if search_resp.data:
                for t in search_resp.data:
                    tid = str(t.id)
                    if tid == str(tweet.id):
                        continue  # Skip the original tweet
                    t_data = {
                        "id": tid,
                        "text": t.text,
                        "created_at": t.created_at.isoformat() if t.created_at else None,
                        "author_id": str(t.author_id) if t.author_id else "",
                        "conversation_id": str(t.conversation_id) if t.conversation_id else None,
                        "metrics": dict(t.public_metrics) if t.public_metrics else {},
                        "stored_at": datetime.now(timezone.utc).isoformat(),
                    }
                    store[tid] = t_data
                    thread_tweets.append(t_data)

        except tweepy.errors.TweepyException as e:
            handle_api_error(e)

        # If the original tweet isn't the root, fetch the root too
        if str(tweet.id) != conv_id and conv_id not in {t["id"] for t in thread_tweets}:
            try:
                root_resp = client.get_tweet(
                    id=conv_id,
                    tweet_fields=TWEET_FIELDS,
                    expansions=EXPANSIONS,
                    user_fields=USER_FIELDS,
                    user_auth=True,
                )
                extra_calls += 1
                if root_resp.data:
                    if root_resp.includes and "users" in root_resp.includes:
                        for user in root_resp.includes["users"]:
                            authors[str(user.id)] = {
                                "username": user.username,
                                "name": user.name,
                                "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
                            }
                    root_data = {
                        "id": str(root_resp.data.id),
                        "text": root_resp.data.text,
                        "created_at": root_resp.data.created_at.isoformat() if root_resp.data.created_at else None,
                        "author_id": str(root_resp.data.author_id) if root_resp.data.author_id else "",
                        "conversation_id": conv_id,
                        "metrics": dict(root_resp.data.public_metrics) if root_resp.data.public_metrics else {},
                        "stored_at": datetime.now(timezone.utc).isoformat(),
                    }
                    store[conv_id] = root_data
                    thread_tweets.append(root_data)
            except tweepy.errors.TweepyException:
                pass
    else:
        # Older thread — follow referenced_tweets chain upward, batch fetch
        chain_ids = set()
        # Collect IDs from referenced tweets
        if tweet.referenced_tweets:
            for ref in tweet.referenced_tweets:
                if ref.type == "replied_to":
                    chain_ids.add(str(ref.id))
        # Add any referenced tweets we already have
        for ref_id, ref_data in ref_tweets.items():
            chain_ids.add(ref_id)
            if ref_id not in {t["id"] for t in thread_tweets}:
                thread_tweets.append(ref_data)

        # Batch fetch any chain IDs we don't have yet
        missing_ids = [cid for cid in chain_ids if cid not in {t["id"] for t in thread_tweets}]
        if missing_ids:
            # Batch up to 100 IDs per call
            for batch_start in range(0, len(missing_ids), 100):
                batch = missing_ids[batch_start:batch_start + 100]
                try:
                    batch_resp = client.get_tweets(
                        ids=batch,
                        tweet_fields=TWEET_FIELDS,
                        expansions=EXPANSIONS,
                        user_fields=USER_FIELDS,
                        user_auth=True,
                    )
                    extra_calls += 1
                    if batch_resp.includes and "users" in batch_resp.includes:
                        for user in batch_resp.includes["users"]:
                            authors[str(user.id)] = {
                                "username": user.username,
                                "name": user.name,
                                "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
                            }
                    if batch_resp.data:
                        for t in batch_resp.data:
                            t_data = {
                                "id": str(t.id),
                                "text": t.text,
                                "created_at": t.created_at.isoformat() if t.created_at else None,
                                "author_id": str(t.author_id) if t.author_id else "",
                                "metrics": dict(t.public_metrics) if t.public_metrics else {},
                                "stored_at": datetime.now(timezone.utc).isoformat(),
                            }
                            store[str(t.id)] = t_data
                            thread_tweets.append(t_data)
                except tweepy.errors.TweepyException as e:
                    handle_api_error(e)

    save_store(store)

    # Sort by created_at ascending for reading order
    thread_tweets.sort(key=lambda t: t.get("created_at", "") or "")

    return {"tweets": thread_tweets, "api_calls": extra_calls}


def main():
    parser = argparse.ArgumentParser(description="X read — fetch any tweet or thread")
    parser.add_argument("tweet", help="Tweet URL or ID")
    parser.add_argument("--thread", action="store_true", help="Fetch full thread/conversation")
    parser.add_argument("--force", action="store_true", help="Override daily budget guard")
    parser.add_argument("--no-budget", action="store_true", help="Skip all budget checks and warnings")
    parser.add_argument("--dry-run", action="store_true", help="Show estimated cost without making API calls")
    args = parser.parse_args()
    cmd_read(args)


if __name__ == "__main__":
    main()
