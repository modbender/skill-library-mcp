#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) briefing — combined morning summary of posts, mentions, and profile."""

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
    format_number, handle_api_error,
)

TWEETS_PATH = DATA_DIR / "tweets.json"
MENTIONS_PATH = DATA_DIR / "mentions.json"

TWEET_FIELDS = [
    "created_at", "public_metrics", "text", "author_id",
    "conversation_id", "in_reply_to_user_id", "referenced_tweets",
]

USER_FIELDS = ["username", "name", "verified", "public_metrics"]

PROFILE_FIELDS = [
    "created_at", "description", "location", "public_metrics",
    "profile_image_url", "url", "verified", "verified_type",
]

HIGH_FOLLOWER_THRESHOLD = 10_000


def load_tweet_store() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if TWEETS_PATH.exists():
        return json.loads(TWEETS_PATH.read_text())
    return {}


def save_tweet_store(store: dict):
    TWEETS_PATH.write_text(json.dumps(store, indent=2))


def load_mention_store() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if MENTIONS_PATH.exists():
        return json.loads(MENTIONS_PATH.read_text())
    return {}


def save_mention_store(store: dict):
    MENTIONS_PATH.write_text(json.dumps(store, indent=2))


def cmd_briefing(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget
    hours = args.hours

    if args.dry_run:
        print(f"[DRY RUN] x_briefing.py (last {hours}h)")
        print(f"  Would cost: ~$0.020 (2 tweet reads + 1 user read)")
        print(f"  Breakdown: timeline $0.005 + mentions $0.005 + profile $0.010")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    user_id = config["user_id"]
    handle = config["handle"]
    budget_mode = config.get("budget_mode", "guarded")
    auto_paginate = budget_mode in ("relaxed", "unlimited") or args.no_budget
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    api_calls_tweet = 0
    api_calls_user = 0

    tweet_store = load_tweet_store()
    mention_store = load_mention_store()

    # === 1. YOUR POSTS ===
    posts = []
    try:
        pagination_token = None
        while True:
            kwargs = dict(
                id=user_id,
                max_results=100,
                tweet_fields=TWEET_FIELDS,
                exclude=["retweets"],
                start_time=start_time,
                user_auth=True,
            )
            if pagination_token:
                kwargs["pagination_token"] = pagination_token
            resp = client.get_users_tweets(**kwargs)
            api_calls_tweet += 1
            if resp.data:
                for tweet in resp.data:
                    tid = str(tweet.id)
                    data = {
                        "id": tid,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
                        "stored_at": datetime.now(timezone.utc).isoformat(),
                    }
                    tweet_store[tid] = data
                    posts.append(data)
                save_tweet_store(tweet_store)
            # Paginate if more results exist
            if resp.meta and resp.meta.get("next_token"):
                if auto_paginate:
                    pagination_token = resp.meta["next_token"]
                else:
                    print(f"  ⚠️  More than {len(posts)} posts in the last {hours}h — use relaxed/unlimited mode or --no-budget to fetch all")
                    break
            else:
                break
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)

    # === 2. MENTIONS ===
    mentions = []
    authors = {}
    try:
        pagination_token = None
        while True:
            kwargs = dict(
                id=user_id,
                max_results=100,
                tweet_fields=TWEET_FIELDS,
                expansions=["author_id"],
                user_fields=USER_FIELDS,
                start_time=start_time,
                user_auth=True,
            )
            if pagination_token:
                kwargs["pagination_token"] = pagination_token
            resp = client.get_users_mentions(**kwargs)
            api_calls_tweet += 1

            if resp.includes and "users" in resp.includes:
                for user in resp.includes["users"]:
                    authors[str(user.id)] = {
                    "username": user.username,
                    "name": user.name,
                    "followers": user.public_metrics["followers_count"] if user.public_metrics else 0,
                }

            if resp.data:
                for tweet in resp.data:
                    tid = str(tweet.id)
                    author = authors.get(str(tweet.author_id), {})
                    data = {
                        "id": tid,
                        "text": tweet.text,
                        "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                        "author_id": str(tweet.author_id),
                        "author_username": author.get("username", "unknown"),
                        "author_name": author.get("name", ""),
                        "author_followers": author.get("followers", 0),
                        "metrics": dict(tweet.public_metrics) if tweet.public_metrics else {},
                        "stored_at": datetime.now(timezone.utc).isoformat(),
                    }
                    mention_store[tid] = data
                    mentions.append(data)
                save_mention_store(mention_store)
            # Paginate if more results exist
            if resp.meta and resp.meta.get("next_token"):
                if auto_paginate:
                    pagination_token = resp.meta["next_token"]
                else:
                    print(f"  ⚠️  More than {len(mentions)} mentions in the last {hours}h — use relaxed/unlimited mode or --no-budget to fetch all")
                    break
            else:
                break
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)

    # === 3. PROFILE ===
    profile = None
    try:
        resp = client.get_me(user_fields=PROFILE_FIELDS, user_auth=True)
        api_calls_user += 1
        if resp.data:
            profile = resp.data
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)

    # Track usage
    day_usage = track_usage(tweet_reads=api_calls_tweet, user_reads=api_calls_user)
    total_cost = api_calls_tweet * 0.005 + api_calls_user * 0.01

    # === OUTPUT ===
    print(f"X BRIEFING — Last {hours} hours")
    print("=" * 50)

    # Posts section
    print(f"\nYOUR POSTS ({len(posts)} posts)")
    if posts:
        # Find top performer
        top_post = None
        top_impressions = 0
        for p in posts:
            text = p["text"]
            if len(text) > 60:
                text = text[:57] + "..."
            pm = p.get("metrics", {})
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

            metrics_str = "  ".join(metrics_parts) if metrics_parts else "no metrics yet"
            print(f"  \"{text}\" — {metrics_str}")

            if impressions > top_impressions:
                top_impressions = impressions
                top_post = p

        if top_post and len(posts) > 1:
            top_text = top_post["text"]
            if len(top_text) > 50:
                top_text = top_text[:47] + "..."
            print(f"  Top performer: \"{top_text}\" ({format_number(top_impressions)} impressions)")
    else:
        print("  No posts in this period.")

    # Mentions section
    print(f"\nMENTIONS ({len(mentions)} new)")
    if mentions:
        for m in mentions:
            username = m.get("author_username", "unknown")
            followers = m.get("author_followers", 0)
            text = m.get("text", "")
            if len(text) > 80:
                text = text[:77] + "..."

            flag = " [HIGH-PROFILE]" if followers >= HIGH_FOLLOWER_THRESHOLD else ""
            marker = "  *" if followers >= HIGH_FOLLOWER_THRESHOLD else "  "
            print(f"{marker}@{username} ({format_number(followers)} followers): \"{text}\"{flag}")
    else:
        print("  No new mentions.")

    # Profile section
    if profile:
        pm = profile.public_metrics
        followers = pm["followers_count"]
        following = pm["following_count"]

        # Follower delta
        delta_str = ""
        history = config.get("follower_history", [])
        if history:
            last = history[-1]
            diff = followers - last["followers"]
            if diff > 0:
                delta_str = f" (+{diff} since {last['date']})"
            elif diff < 0:
                delta_str = f" ({diff} since {last['date']})"

        print(f"\nPROFILE")
        print(f"  Followers: {format_number(followers)}{delta_str}")
        print(f"  Following: {format_number(following)}")

        # Track follower history
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if not history or history[-1]["date"] != today:
            history.append({
                "date": today,
                "followers": followers,
                "following": following,
                "posts": pm["tweet_count"],
            })
            config["follower_history"] = history[-90:]
            save_config(config)

    # Footer
    budget = config.get("daily_budget", 0.10)
    remaining = max(0, budget - day_usage.get("est_cost", 0))
    print(f"\nBriefing cost: ${total_cost:.2f} | Today's total: ${day_usage['est_cost']:.3f} | Budget: ${remaining:.2f} remaining")
    budget_warning(config, suppress=suppress)


def main():
    parser = argparse.ArgumentParser(description="X briefing — morning summary")
    parser.add_argument("--hours", type=int, default=24, help="Lookback period in hours (default: 24)")
    parser.add_argument("--force", action="store_true", help="Override daily budget guard")
    parser.add_argument("--no-budget", action="store_true", help="Skip all budget checks and warnings")
    parser.add_argument("--dry-run", action="store_true", help="Show estimated cost without making API calls")
    args = parser.parse_args()
    cmd_briefing(args)


if __name__ == "__main__":
    main()
