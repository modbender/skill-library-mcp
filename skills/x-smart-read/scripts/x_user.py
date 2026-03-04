#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "tweepy>=4.14.0",
# ]
# ///
"""X (Twitter) user profile info and follower tracking."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import tweepy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from x_common import (
    load_config, save_config, get_client,
    track_usage, budget_warning, check_budget,
    format_number, handle_api_error,
)

USER_FIELDS = [
    "created_at", "description", "location", "public_metrics",
    "profile_image_url", "url", "verified", "verified_type",
]


def cmd_me(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        print("[DRY RUN] x_user.py me")
        print(f"  Would cost: ~$0.010 (1 user read)")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    try:
        resp = client.get_me(user_fields=USER_FIELDS, user_auth=True)
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(user_reads=1)
    budget_warning(config, suppress=suppress)

    if not resp.data:
        print("Error: Could not retrieve profile.")
        return

    u = resp.data
    pm = u.public_metrics

    print(f"Profile: {u.name} (@{u.username})")
    print("=" * 40)
    if u.description:
        print(f"Bio: {u.description}")
    if u.location:
        print(f"Location: {u.location}")
    if u.created_at:
        print(f"Joined: {u.created_at.strftime('%B %Y')}")
    if u.url:
        print(f"URL: {u.url}")
    print()

    followers = pm["followers_count"]
    following = pm["following_count"]
    tweets = pm["tweet_count"]
    listed = pm["listed_count"]

    # Follower delta tracking
    delta_str = ""
    history = config.get("follower_history", [])
    if history:
        last = history[-1]
        diff = followers - last["followers"]
        if diff > 0:
            delta_str = f"  (+{diff} since {last['date']})"
        elif diff < 0:
            delta_str = f"  ({diff} since {last['date']})"

    print(f"Followers:  {format_number(followers)}{delta_str}")
    print(f"Following:  {format_number(following)}")
    print(f"Posts:      {format_number(tweets)}")
    print(f"Listed:     {format_number(listed)}")
    print()
    print(f"https://x.com/{u.username}")

    # Track follower history if --track
    if args.track:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        # Don't duplicate same-day entries
        if not history or history[-1]["date"] != today:
            history.append({
                "date": today,
                "followers": followers,
                "following": following,
                "posts": tweets,
            })
            # Keep last 90 entries
            config["follower_history"] = history[-90:]
            save_config(config)
            print("\n(Follower history updated)")

    print(f"\n---\nEst. API cost: ~$0.010 (1 user read)")
    print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def cmd_lookup(args):
    config = load_config()
    if not config:
        return

    force = args.force or args.no_budget
    suppress = args.no_budget

    if args.dry_run:
        print(f"[DRY RUN] x_user.py lookup {args.username}")
        print(f"  Would cost: ~$0.010 (1 user read)")
        budget_warning(config, suppress=suppress)
        return

    if not check_budget(config, force):
        return

    client = get_client(config)
    username = args.username.lstrip("@")

    try:
        resp = client.get_user(username=username, user_fields=USER_FIELDS)
    except tweepy.errors.TweepyException as e:
        handle_api_error(e)
        return

    day_usage = track_usage(user_reads=1)
    budget_warning(config, suppress=suppress)

    if not resp.data:
        print(f"Error: User @{username} not found.")
        return

    u = resp.data
    pm = u.public_metrics

    print(f"Profile: {u.name} (@{u.username})")
    print("=" * 40)
    if u.description:
        print(f"Bio: {u.description}")
    if u.location:
        print(f"Location: {u.location}")
    if u.created_at:
        print(f"Joined: {u.created_at.strftime('%B %Y')}")
    if u.url:
        print(f"URL: {u.url}")
    print()
    print(f"Followers:  {format_number(pm['followers_count'])}")
    print(f"Following:  {format_number(pm['following_count'])}")
    print(f"Posts:      {format_number(pm['tweet_count'])}")
    print(f"Listed:     {format_number(pm['listed_count'])}")
    print()
    print(f"https://x.com/{u.username}")
    print(f"\n---\nEst. API cost: ~$0.010 (1 user read)")
    print(f"Today's spend: ${day_usage['est_cost']:.3f}")


def main():
    parser = argparse.ArgumentParser(description="X user profile info")
    parser.add_argument("--force", action="store_true", help="Override daily budget guard")
    parser.add_argument("--no-budget", action="store_true", help="Skip all budget checks and warnings")
    parser.add_argument("--dry-run", action="store_true", help="Show estimated cost without making API calls")
    subparsers = parser.add_subparsers(dest="command", required=True)

    me_parser = subparsers.add_parser("me", help="Your profile stats")
    me_parser.add_argument("--track", action="store_true", help="Save follower count for delta tracking")

    lookup_parser = subparsers.add_parser("lookup", help="Look up any user")
    lookup_parser.add_argument("username", help="X handle (with or without @)")

    args = parser.parse_args()
    if args.command == "me":
        cmd_me(args)
    elif args.command == "lookup":
        cmd_lookup(args)


if __name__ == "__main__":
    main()
