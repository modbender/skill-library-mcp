#!/usr/bin/env python3
"""
x-cli post — Post tweets, replies, and quotes on X/Twitter.

Usage:
  python x_post.py tweet "Hello world!"
  python x_post.py reply <tweet-id-or-url> "Nice analysis!"
  python x_post.py quote <tweet-id-or-url> "Adding context..."

Options:
  --json    Output posted tweet as JSON
  --dry-run Preview without posting
"""

import argparse
import json
import re

from x_utils import get_client, run


def extract_tweet_id(url_or_id: str) -> str:
    match = re.search(r"/status/(\d+)", url_or_id)
    return match.group(1) if match else url_or_id


async def cmd_tweet(args):
    client = await get_client()

    media_ids = args.media if hasattr(args, 'media') and args.media else None

    if args.dry_run:
        print(f"🔍 DRY RUN — would post:\n\n{args.text}\n\n({len(args.text)} chars)")
        if media_ids:
            print(f"📎 Media: {', '.join(media_ids)}")
        return

    result = await client.create_tweet(text=args.text, media_ids=media_ids)
    print(f"✅ Tweet posted: https://x.com/i/status/{result.id}" if not args.json
          else json.dumps({"id": result.id, "url": f"https://x.com/i/status/{result.id}"}))


async def cmd_reply(args):
    client = await get_client()
    tweet_id = extract_tweet_id(args.target)

    if args.dry_run:
        print(f"🔍 DRY RUN — would reply to {tweet_id}:\n\n{args.text}")
        return

    result = await client.create_tweet(text=args.text, reply_to=tweet_id)
    print(f"✅ Reply posted: https://x.com/i/status/{result.id}" if not args.json
          else json.dumps({"id": result.id, "reply_to": tweet_id}))


async def cmd_quote(args):
    client = await get_client()
    tweet_id = extract_tweet_id(args.target)
    tweet = await client.get_tweet_by_id(tweet_id)
    quote_url = f"https://x.com/{tweet.user.screen_name}/status/{tweet_id}"

    if args.dry_run:
        print(f"🔍 DRY RUN — would quote {quote_url}:\n\n{args.text}")
        return

    result = await client.create_tweet(text=args.text, attachment_url=quote_url)
    print(f"✅ Quote posted: https://x.com/i/status/{result.id}" if not args.json
          else json.dumps({"id": result.id, "quoted": tweet_id}))


def main():
    parser = argparse.ArgumentParser(description="x-cli post — Post to X/Twitter")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")

    sub = parser.add_subparsers(dest="command", required=True)

    p_tweet = sub.add_parser("tweet", help="Post a new tweet")
    p_tweet.add_argument("text", help="Tweet text")
    p_tweet.add_argument("--media", nargs="+", help="Media IDs (from x_extra.py upload)")

    p_reply = sub.add_parser("reply", help="Reply to a tweet")
    p_reply.add_argument("target", help="Tweet URL or ID to reply to")
    p_reply.add_argument("text", help="Reply text")

    p_quote = sub.add_parser("quote", help="Quote a tweet")
    p_quote.add_argument("target", help="Tweet URL or ID to quote")
    p_quote.add_argument("text", help="Quote text")

    args = parser.parse_args()

    if args.command == "tweet":
        run(cmd_tweet(args))
    elif args.command == "reply":
        run(cmd_reply(args))
    elif args.command == "quote":
        run(cmd_quote(args))


if __name__ == "__main__":
    main()
