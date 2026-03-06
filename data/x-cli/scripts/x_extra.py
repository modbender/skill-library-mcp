#!/usr/bin/env python3
"""
x-cli extra — Trends, bookmarks, notifications, user info, media, lists, polls.

Usage:
  python x_extra.py trends                            Trending topics
  python x_extra.py bookmarks [--count N]             List bookmarks
  python x_extra.py notifications [--count N]         Notifications
  python x_extra.py user-info <username>              User profile
  python x_extra.py followers <username> [--count N]  List followers
  python x_extra.py following <username> [--count N]  List following
  python x_extra.py upload <file-path>                Upload media
  python x_extra.py schedule <timestamp> "text"       Schedule tweet
  python x_extra.py poll "A" "B" "C" [--duration M]   Create poll
  python x_extra.py list-create <name>                Create list
  python x_extra.py list-add <list-id> <username>     Add to list
  python x_extra.py list-remove <list-id> <username>  Remove from list
  python x_extra.py list-tweets <list-id> [--count N] List tweets
"""

import argparse
import json
import sys
import time

from x_utils import load_config, get_client, format_tweet, run


async def cmd_trends(args):
    client = await get_client()
    category = getattr(args, "category", "trending") or "trending"
    trends = await client.get_trends(category)
    for i, trend in enumerate(trends[:20], 1):
        name = trend.name if hasattr(trend, "name") else str(trend)
        count = getattr(trend, "tweet_count", "")
        print(f"{i}. {name}" + (f" ({count})" if count else ""))


async def cmd_bookmarks(args):
    client = await get_client()
    bookmarks = await client.get_bookmarks(count=args.count)
    sep = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(t, args.json) for t in bookmarks[:args.count]]
    print(sep.join(output) if output else "No bookmarks found.")


async def cmd_notifications(args):
    client = await get_client()
    notifs = await client.get_notifications("All")
    count = 0
    for n in notifs:
        if count >= args.count:
            break
        print(f"🔔 {n}")
        count += 1


async def cmd_user_info(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.username.lstrip("@"))
    data = {
        "id": user.id, "username": user.screen_name, "name": user.name,
        "bio": getattr(user, "description", ""),
        "followers": getattr(user, "followers_count", 0),
        "following": getattr(user, "following_count", 0),
        "tweets": getattr(user, "statuses_count", 0),
        "verified": getattr(user, "is_blue_verified", False),
        "created": str(getattr(user, "created_at", "")),
        "location": getattr(user, "location", ""),
    }
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"@{data['username']} ({data['name']})")
        print(f"📝 {data['bio']}")
        print(f"👥 {data['followers']} followers | {data['following']} following | {data['tweets']} tweets")
        if data["verified"]:
            print("✅ Verified")
        if data["location"]:
            print(f"📍 {data['location']}")


async def cmd_followers(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.username.lstrip("@"))
    followers = await client.get_user_followers(user.id, count=args.count)
    for f in followers[:args.count]:
        print(f"@{f.screen_name} ({f.name}) — {getattr(f, 'followers_count', '?')} followers")


async def cmd_following(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.username.lstrip("@"))
    following = await client.get_user_following(user.id, count=args.count)
    for f in following[:args.count]:
        print(f"@{f.screen_name} ({f.name})")


async def cmd_upload(args):
    client = await get_client()
    media_id = await client.upload_media(args.filepath, wait_for_completion=True)
    print(f"✅ Media uploaded: {media_id}")
    print(f"Use with: python x_post.py tweet \"text\" --media {media_id}")


async def cmd_schedule(args):
    client = await get_client()
    scheduled_id = await client.create_scheduled_tweet(
        scheduled_at=args.timestamp, text=args.text
    )
    t = time.strftime("%Y-%m-%d %H:%M", time.localtime(args.timestamp))
    print(f"⏰ Tweet scheduled for {t} (ID: {scheduled_id})")


async def cmd_poll(args):
    client = await get_client()
    card_uri = await client.create_poll(
        choices=args.choices, duration_minutes=args.duration
    )
    print(f"📊 Poll created: {card_uri}")
    print(f"Use with: python x_post.py tweet \"question?\" --poll-uri {card_uri}")


async def cmd_list_create(args):
    client = await get_client()
    lst = await client.create_list(
        name=args.name, description=args.description or "",
        is_private=args.private
    )
    print(f"📋 List created: {lst.id} — {args.name}")


async def cmd_list_add(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.username.lstrip("@"))
    await client.add_list_member(args.list_id, user.id)
    print(f"✅ Added @{user.screen_name} to list {args.list_id}")


async def cmd_list_remove(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.username.lstrip("@"))
    await client.remove_list_member(args.list_id, user.id)
    print(f"👋 Removed @{user.screen_name} from list {args.list_id}")


async def cmd_list_tweets(args):
    client = await get_client()
    tweets = await client.get_list_tweets(args.list_id, count=args.count)
    sep = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = [format_tweet(t, args.json) for t in tweets[:args.count]]
    print(sep.join(output) if output else "No tweets in this list.")


def main():
    parser = argparse.ArgumentParser(description="x-cli extra — Additional X/Twitter features")
    parser.add_argument("--json", action="store_true", help="JSON output")

    sub = parser.add_subparsers(dest="command", required=True)

    p_trends = sub.add_parser("trends", help="Trending topics")
    p_trends.add_argument("--category", choices=["trending", "for-you", "news", "sports", "entertainment"], default="trending")

    p_bm = sub.add_parser("bookmarks", help="List bookmarked tweets")
    p_bm.add_argument("--count", type=int, default=10)

    p_notif = sub.add_parser("notifications", help="Get notifications")
    p_notif.add_argument("--count", type=int, default=10)

    p_info = sub.add_parser("user-info", help="User profile info")
    p_info.add_argument("username")

    p_followers = sub.add_parser("followers", help="List followers")
    p_followers.add_argument("username")
    p_followers.add_argument("--count", type=int, default=20)

    p_following = sub.add_parser("following", help="List following")
    p_following.add_argument("username")
    p_following.add_argument("--count", type=int, default=20)

    p_upload = sub.add_parser("upload", help="Upload media file")
    p_upload.add_argument("filepath", help="Path to image/video/gif")

    p_sched = sub.add_parser("schedule", help="Schedule a tweet")
    p_sched.add_argument("timestamp", type=int, help="Unix timestamp")
    p_sched.add_argument("text", help="Tweet text")

    p_poll = sub.add_parser("poll", help="Create a poll")
    p_poll.add_argument("choices", nargs="+", help="Poll choices (2-4)")
    p_poll.add_argument("--duration", type=int, default=1440, help="Minutes (default: 24h)")

    p_lc = sub.add_parser("list-create", help="Create a list")
    p_lc.add_argument("name", help="List name")
    p_lc.add_argument("--description", default="")
    p_lc.add_argument("--private", action="store_true")

    p_la = sub.add_parser("list-add", help="Add user to list")
    p_la.add_argument("list_id")
    p_la.add_argument("username")

    p_lr = sub.add_parser("list-remove", help="Remove user from list")
    p_lr.add_argument("list_id")
    p_lr.add_argument("username")

    p_lt = sub.add_parser("list-tweets", help="Tweets from a list")
    p_lt.add_argument("list_id")
    p_lt.add_argument("--count", type=int, default=20)

    args = parser.parse_args()

    cmd_map = {
        "trends": cmd_trends, "bookmarks": cmd_bookmarks,
        "notifications": cmd_notifications, "user-info": cmd_user_info,
        "followers": cmd_followers, "following": cmd_following,
        "upload": cmd_upload, "schedule": cmd_schedule,
        "poll": cmd_poll, "list-create": cmd_list_create,
        "list-add": cmd_list_add, "list-remove": cmd_list_remove,
        "list-tweets": cmd_list_tweets,
    }
    run(cmd_map[args.command](args))


if __name__ == "__main__":
    main()
