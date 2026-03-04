#!/usr/bin/env python3
"""
x-cli read — Read tweets, timelines, threads, mentions, replies, and user search.

Usage:
  python x_read.py tweet <url-or-id>              Read a single tweet
  python x_read.py user <username> [--count N]     Read user's latest tweets
  python x_read.py timeline [--count N]            Read home timeline (Following)
  python x_read.py foryou [--count N]              Read For You timeline
  python x_read.py thread <url-or-id>              Read a thread
  python x_read.py replies <url-or-id> [--count N] Read replies to a tweet
  python x_read.py mentions [--count N]            Read your mentions
  python x_read.py highlights <username> [--count]  Read user's highlights
  python x_read.py search-user <query> [--count N] Search for users

Options:
  --count N    Number of results (default: 5)
  --json       Output as JSON
"""

import argparse
import json
import re
import sys

from x_utils import load_config, get_client, format_tweet, run


def extract_tweet_id(url_or_id: str) -> str:
    match = re.search(r"/status/(\d+)", url_or_id)
    return match.group(1) if match else url_or_id


def format_user(user, json_mode=False) -> str:
    data = {
        "id": user.id,
        "username": user.screen_name,
        "name": user.name,
        "bio": getattr(user, "description", ""),
        "followers": getattr(user, "followers_count", 0),
    }
    if json_mode:
        return json.dumps(data, ensure_ascii=False)
    return f"@{data['username']} ({data['name']}) — {data['followers']} followers\n  {data['bio'][:100]}"


async def cmd_tweet(args):
    client = await get_client()
    tweet_id = extract_tweet_id(args.target)
    tweet = await client.get_tweet_by_id(tweet_id)
    print(format_tweet(tweet, args.json))


async def cmd_user(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.target.lstrip("@"))
    tweets = await client.get_user_tweets(user.id, "Tweets", count=args.count)
    separator = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(t, args.json) for t in tweets[:args.count]]
    print(separator.join(output))


async def cmd_timeline(args):
    client = await get_client()
    tweets = await client.get_latest_timeline(count=args.count)
    separator = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(t, args.json) for t in tweets[:args.count]]
    print(separator.join(output))


async def cmd_foryou(args):
    client = await get_client()
    tweets = await client.get_timeline(count=args.count)
    separator = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(t, args.json) for t in tweets[:args.count]]
    print(separator.join(output))


async def cmd_thread(args):
    client = await get_client()
    tweet_id = extract_tweet_id(args.target)
    tweet = await client.get_tweet_by_id(tweet_id)
    print(format_tweet(tweet, args.json))
    if not args.json:
        print("\n" + "─" * 50)
    try:
        replies = await client.get_tweet_replies(tweet_id)
        for reply in replies:
            if reply.user and reply.user.screen_name == tweet.user.screen_name:
                if not args.json:
                    print()
                print(format_tweet(reply, args.json))
    except Exception:
        pass


async def cmd_replies(args):
    client = await get_client()
    tweet_id = extract_tweet_id(args.target)
    replies = await client.get_tweet_replies(tweet_id)
    separator = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(r, args.json) for r in replies[:args.count]]
    print(separator.join(output) if output else "No replies found.")


async def cmd_mentions(args):
    client = await get_client()
    notifs = await client.get_notifications("Mentions")
    count = 0
    for n in notifs:
        if count >= args.count:
            break
        if hasattr(n, "tweet") and n.tweet:
            print(format_tweet(n.tweet, args.json))
        else:
            print(f"🔔 {n}")
        if not args.json:
            print("─" * 50)
        count += 1
    if count == 0:
        print("No mentions found.")


async def cmd_highlights(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.target.lstrip("@"))
    tweets = await client.get_user_highlights_tweets(user.id, count=args.count)
    separator = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(t, args.json) for t in tweets[:args.count]]
    print(separator.join(output) if output else "No highlights found.")


async def cmd_search_user(args):
    client = await get_client()
    users = await client.search_user(args.query, count=args.count)
    separator = "\n" if args.json else "\n" + "─" * 30 + "\n"
    output = [format_user(u, args.json) for u in users[:args.count]]
    print(separator.join(output) if output else "No users found.")


def main():
    parser = argparse.ArgumentParser(description="x-cli read — Read from X/Twitter")
    parser.add_argument("--json", action="store_true", help="JSON output")

    sub = parser.add_subparsers(dest="command", required=True)

    p_tweet = sub.add_parser("tweet", help="Read a single tweet")
    p_tweet.add_argument("target", help="Tweet URL or ID")

    p_user = sub.add_parser("user", help="Read user's latest tweets")
    p_user.add_argument("target", help="Username")
    p_user.add_argument("--count", type=int, default=5)

    p_tl = sub.add_parser("timeline", help="Read home timeline (Following)")
    p_tl.add_argument("--count", type=int, default=20)

    p_fy = sub.add_parser("foryou", help="Read For You timeline")
    p_fy.add_argument("--count", type=int, default=20)

    p_thread = sub.add_parser("thread", help="Read a thread")
    p_thread.add_argument("target", help="Tweet URL or ID")

    p_replies = sub.add_parser("replies", help="Read replies to a tweet")
    p_replies.add_argument("target", help="Tweet URL or ID")
    p_replies.add_argument("--count", type=int, default=20)

    p_mentions = sub.add_parser("mentions", help="Read your mentions")
    p_mentions.add_argument("--count", type=int, default=10)

    p_hl = sub.add_parser("highlights", help="Read user's highlights")
    p_hl.add_argument("target", help="Username")
    p_hl.add_argument("--count", type=int, default=10)

    p_su = sub.add_parser("search-user", help="Search for users")
    p_su.add_argument("query", help="Search query")
    p_su.add_argument("--count", type=int, default=10)

    args = parser.parse_args()

    cmd_map = {
        "tweet": cmd_tweet, "user": cmd_user,
        "timeline": cmd_timeline, "foryou": cmd_foryou,
        "thread": cmd_thread, "replies": cmd_replies,
        "mentions": cmd_mentions, "highlights": cmd_highlights,
        "search-user": cmd_search_user,
    }
    run(cmd_map[args.command](args))


if __name__ == "__main__":
    main()
