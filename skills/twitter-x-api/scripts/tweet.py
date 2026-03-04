#!/usr/bin/env python3
"""
Twitter/X API CLI for reading, posting, replying, DMs, search, and analytics.
Uses Tweepy for X API v2 access.

Usage:
    tweet.py post "text" [--media FILE]
    tweet.py reply TWEET_ID "text"
    tweet.py thread "tweet1" "tweet2" ...
    tweet.py timeline [--count N]
    tweet.py mentions [--count N]
    tweet.py dms [--count N]
    tweet.py dm USERNAME "message"
    tweet.py search "query" [--count N]
    tweet.py user USERNAME
    tweet.py show TWEET_ID
    tweet.py analytics TWEET_ID
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import tweepy
except ImportError:
    print("Error: tweepy not installed. Run: pip install tweepy")
    sys.exit(1)


def load_credentials():
    """Load credentials from env vars or credentials file."""
    creds = {}

    # Try environment variables first
    env_keys = {
        "TWITTER_API_KEY": "api_key",
        "TWITTER_API_SECRET": "api_secret",
        "TWITTER_ACCESS_TOKEN": "access_token",
        "TWITTER_ACCESS_SECRET": "access_secret",
        "TWITTER_BEARER_TOKEN": "bearer_token",
    }
    for env_key, cred_key in env_keys.items():
        if os.environ.get(env_key):
            creds[cred_key] = os.environ[env_key]

    # Try credentials file
    cred_file = Path.home() / ".config" / "twitter" / "credentials.json"
    if cred_file.exists():
        with open(cred_file) as f:
            file_creds = json.load(f)
            creds.update({k: v for k, v in file_creds.items() if v})

    return creds


def get_client(creds, read_only=False):
    """Get Tweepy client for API v2."""
    if read_only and creds.get("bearer_token"):
        return tweepy.Client(bearer_token=creds["bearer_token"])

    if all(k in creds for k in ["api_key", "api_secret", "access_token", "access_secret"]):
        return tweepy.Client(
            consumer_key=creds["api_key"],
            consumer_secret=creds["api_secret"],
            access_token=creds["access_token"],
            access_token_secret=creds["access_secret"],
        )

    raise ValueError("Insufficient credentials. Need either bearer_token for read-only or all four OAuth keys for full access.")


def get_api_v1(creds):
    """Get Tweepy API v1.1 object for media uploads."""
    auth = tweepy.OAuth1UserHandler(
        creds["api_key"],
        creds["api_secret"],
        creds["access_token"],
        creds["access_secret"],
    )
    return tweepy.API(auth)


def format_tweet(tweet, include_user=True):
    """Format a tweet for display."""
    lines = []
    if include_user and hasattr(tweet, "author_id") or (isinstance(tweet, dict) and "author_id" in tweet):
        # Will show user separately if available
        pass

    text = tweet.text if hasattr(tweet, "text") else tweet.get("text", "")
    created_at = tweet.created_at if hasattr(tweet, "created_at") else tweet.get("created_at")
    tweet_id = tweet.id if hasattr(tweet, "id") else tweet.get("id")

    lines.append(f"Tweet ID: {tweet_id}")
    if created_at:
        if isinstance(created_at, str):
            lines.append(f"Time: {created_at}")
        else:
            lines.append(f"Time: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Text: {text}")
    lines.append("")

    return "\n".join(lines)


def cmd_post(args):
    """Post a new tweet."""
    creds = load_credentials()
    client = get_client(creds, read_only=False)

    media_ids = None
    if args.media:
        api = get_api_v1(creds)
        media_ids = []
        for media_path in args.media:
            print(f"Uploading {media_path}...")
            media = api.media_upload(filename=media_path)
            media_ids.append(media.media_id)

    response = client.create_tweet(text=args.text, media_ids=media_ids if media_ids else None)
    tweet_id = response.data["id"]
    print(f"Posted tweet: https://twitter.com/user/status/{tweet_id}")
    return tweet_id


def cmd_reply(args):
    """Reply to a tweet."""
    creds = load_credentials()
    client = get_client(creds, read_only=False)

    response = client.create_tweet(text=args.text, in_reply_to_tweet_id=args.tweet_id)
    tweet_id = response.data["id"]
    print(f"Posted reply: https://twitter.com/user/status/{tweet_id}")
    return tweet_id


def cmd_thread(args):
    """Post a thread of tweets."""
    creds = load_credentials()
    client = get_client(creds, read_only=False)

    if len(args.tweets) < 2:
        print("Error: Thread requires at least 2 tweets")
        sys.exit(1)

    previous_id = None
    tweet_ids = []

    for i, text in enumerate(args.tweets):
        if previous_id:
            response = client.create_tweet(text=text, in_reply_to_tweet_id=previous_id)
        else:
            response = client.create_tweet(text=text)

        tweet_id = response.data["id"]
        tweet_ids.append(tweet_id)
        previous_id = tweet_id
        print(f"Tweet {i+1}/{len(args.tweets)}: https://twitter.com/user/status/{tweet_id}")

        # Small delay to avoid rate limits
        if i < len(args.tweets) - 1:
            time.sleep(0.5)

    print(f"\nThread posted: {len(tweet_ids)} tweets")
    return tweet_ids


def cmd_timeline(args):
    """Get home timeline."""
    creds = load_credentials()
    client = get_client(creds, read_only=True)

    response = client.get_home_timeline(max_results=args.count, tweet_fields=["created_at", "author_id"])

    if not response.data:
        print("No tweets in timeline")
        return

    print(f"Timeline ({len(response.data)} tweets):\n")
    for tweet in response.data:
        print(format_tweet(tweet))


def cmd_mentions(args):
    """Get mentions timeline."""
    creds = load_credentials()
    client = get_client(creds, read_only=False)  # Requires user context

    # Get current user first
    me = client.get_me()
    if not me.data:
        print("Could not get user info")
        return

    response = client.get_users_mentions(
        id=me.data.id,
        max_results=args.count,
        tweet_fields=["created_at", "author_id"],
        expansions=["author_id"],
    )

    if not response.data:
        print("No mentions")
        return

    # Build user lookup
    users = {u.id: u.username for u in response.includes.get("users", [])} if response.includes else {}

    print(f"Mentions ({len(response.data)} tweets):\n")
    for tweet in response.data:
        username = users.get(tweet.author_id, "unknown")
        print(f"@{username}: {tweet.text}")
        print(f"  ID: {tweet.id} | Time: {tweet.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()


def cmd_dms(args):
    """Get recent DMs."""
    creds = load_credentials()
    client = get_client(creds, read_only=False)

    # Note: DM reading requires special access
    print("Note: DM reading may require elevated API access.")
    print("Attempting to fetch DMs...\n")

    try:
        # This endpoint may not be available on all tiers
        response = client.get_direct_message_events(
            max_results=args.count,
            dm_event_fields=["created_at", "sender_id"],
        )

        if not response.data:
            print("No DMs found")
            return

        print(f"Recent DMs:\n")
        for event in response.data:
            print(f"From: {event.sender_id}")
            print(f"Time: {event.created_at}")
            print(f"Message: {event.text}")
            print()
    except tweepy.errors.Forbidden:
        print("Error: DM access requires elevated API permissions (Basic tier or higher with DM access).")
    except AttributeError:
        print("Error: DM endpoint not available in this tweepy version or API tier.")


def cmd_dm(args):
    """Send a DM to a user."""
    creds = load_credentials()
    client = get_client(creds, read_only=False)

    # Get user ID from username
    user = client.get_user(username=args.username.lstrip("@"))
    if not user.data:
        print(f"Error: User @{args.username} not found")
        sys.exit(1)

    try:
        response = client.create_direct_message(participant_id=user.data.id, text=args.message)
        print(f"DM sent to @{args.username}")
    except tweepy.errors.Forbidden:
        print("Error: DM sending requires elevated API permissions.")


def cmd_search(args):
    """Search for tweets."""
    creds = load_credentials()
    client = get_client(creds, read_only=True)

    try:
        response = client.search_recent_tweets(
            query=args.query,
            max_results=args.count,
            tweet_fields=["created_at", "author_id", "public_metrics"],
            expansions=["author_id"],
        )

        if not response.data:
            print("No results found")
            return

        users = {u.id: u.username for u in response.includes.get("users", [])} if response.includes else {}

        print(f"Search results for '{args.query}' ({len(response.data)} tweets):\n")
        for tweet in response.data:
            username = users.get(tweet.author_id, "unknown")
            metrics = tweet.public_metrics if hasattr(tweet, "public_metrics") else {}
            print(f"@{username}: {tweet.text}")
            print(f"  ID: {tweet.id} | Likes: {metrics.get('like_count', '?')} | RTs: {metrics.get('retweet_count', '?')}")
            print()
    except tweepy.errors.Forbidden:
        print("Error: Search requires Basic API tier or higher.")


def cmd_user(args):
    """Get user information."""
    creds = load_credentials()
    client = get_client(creds, read_only=True)

    username = args.username.lstrip("@")
    response = client.get_user(
        username=username,
        user_fields=["created_at", "description", "public_metrics", "location", "verified"],
    )

    if not response.data:
        print(f"User @{username} not found")
        return

    user = response.data
    metrics = user.public_metrics if hasattr(user, "public_metrics") else {}

    print(f"User: @{user.username}")
    if hasattr(user, "name"):
        print(f"Name: {user.name}")
    if hasattr(user, "description") and user.description:
        print(f"Bio: {user.description}")
    if hasattr(user, "location") and user.location:
        print(f"Location: {user.location}")
    if hasattr(user, "verified"):
        print(f"Verified: {'Yes' if user.verified else 'No'}")
    if hasattr(user, "created_at"):
        print(f"Joined: {user.created_at.strftime('%Y-%m-%d')}")
    print(f"Followers: {metrics.get('followers_count', '?')}")
    print(f"Following: {metrics.get('following_count', '?')}")
    print(f"Tweets: {metrics.get('tweet_count', '?')}")


def cmd_show(args):
    """Show a specific tweet."""
    creds = load_credentials()
    client = get_client(creds, read_only=True)

    response = client.get_tweet(
        args.tweet_id,
        tweet_fields=["created_at", "author_id", "public_metrics"],
        expansions=["author_id"],
    )

    if not response.data:
        print(f"Tweet {args.tweet_id} not found")
        return

    tweet = response.data
    users = {u.id: u.username for u in response.includes.get("users", [])} if response.includes else {}
    username = users.get(tweet.author_id, "unknown")

    print(f"Tweet by @{username}")
    print(f"ID: {tweet.id}")
    print(f"Time: {tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n{tweet.text}")

    if hasattr(tweet, "public_metrics"):
        m = tweet.public_metrics
        print(f"\n📊 Likes: {m.get('like_count', 0)} | RTs: {m.get('retweet_count', 0)} | Replies: {m.get('reply_count', 0)} | Quotes: {m.get('quote_count', 0)}")


def cmd_analytics(args):
    """Get tweet analytics (public metrics)."""
    creds = load_credentials()
    client = get_client(creds, read_only=True)

    response = client.get_tweet(
        args.tweet_id,
        tweet_fields=["public_metrics", "created_at", "author_id"],
        expansions=["author_id"],
    )

    if not response.data:
        print(f"Tweet {args.tweet_id} not found")
        return

    tweet = response.data
    users = {u.id: u.username for u in response.includes.get("users", [])} if response.includes else {}
    username = users.get(tweet.author_id, "unknown")

    print(f"📊 Analytics for tweet by @{username}")
    print(f"Tweet ID: {tweet.id}")
    print(f"Posted: {tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nText: {tweet.text[:100]}{'...' if len(tweet.text) > 100 else ''}")

    if hasattr(tweet, "public_metrics"):
        m = tweet.public_metrics
        print(f"\n📈 Engagement:")
        print(f"  ❤️  Likes: {m.get('like_count', 0):,}")
        print(f"  🔄 Retweets: {m.get('retweet_count', 0):,}")
        print(f"  💬 Replies: {m.get('reply_count', 0):,}")
        print(f"  💭 Quotes: {m.get('quote_count', 0):,}")
        print(f"  👁️  Impressions: {m.get('impression_count', 'N/A')}")

        total = m.get('like_count', 0) + m.get('retweet_count', 0) + m.get('reply_count', 0) + m.get('quote_count', 0)
        print(f"\n  Total Engagements: {total:,}")


def main():
    parser = argparse.ArgumentParser(
        description="Twitter/X API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Post
    p_post = subparsers.add_parser("post", help="Post a new tweet")
    p_post.add_argument("text", help="Tweet text")
    p_post.add_argument("--media", action="append", help="Media file to attach (can be used multiple times)")

    # Reply
    p_reply = subparsers.add_parser("reply", help="Reply to a tweet")
    p_reply.add_argument("tweet_id", help="Tweet ID to reply to")
    p_reply.add_argument("text", help="Reply text")

    # Thread
    p_thread = subparsers.add_parser("thread", help="Post a thread")
    p_thread.add_argument("tweets", nargs="+", help="Tweets in order")

    # Timeline
    p_timeline = subparsers.add_parser("timeline", help="Get home timeline")
    p_timeline.add_argument("--count", type=int, default=20, help="Number of tweets (max 100)")

    # Mentions
    p_mentions = subparsers.add_parser("mentions", help="Get mentions")
    p_mentions.add_argument("--count", type=int, default=20, help="Number of tweets (max 100)")

    # DMs
    p_dms = subparsers.add_parser("dms", help="Get recent DMs")
    p_dms.add_argument("--count", type=int, default=20, help="Number of DMs")

    # Send DM
    p_dm = subparsers.add_parser("dm", help="Send a DM")
    p_dm.add_argument("username", help="Recipient username")
    p_dm.add_argument("message", help="Message text")

    # Search
    p_search = subparsers.add_parser("search", help="Search tweets")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--count", type=int, default=20, help="Number of results (max 100)")

    # User
    p_user = subparsers.add_parser("user", help="Get user info")
    p_user.add_argument("username", help="Username (with or without @)")

    # Show
    p_show = subparsers.add_parser("show", help="Show a specific tweet")
    p_show.add_argument("tweet_id", help="Tweet ID")

    # Analytics
    p_analytics = subparsers.add_parser("analytics", help="Get tweet analytics")
    p_analytics.add_argument("tweet_id", help="Tweet ID")

    args = parser.parse_args()

    commands = {
        "post": cmd_post,
        "reply": cmd_reply,
        "thread": cmd_thread,
        "timeline": cmd_timeline,
        "mentions": cmd_mentions,
        "dms": cmd_dms,
        "dm": cmd_dm,
        "search": cmd_search,
        "user": cmd_user,
        "show": cmd_show,
        "analytics": cmd_analytics,
    }

    try:
        commands[args.command](args)
    except tweepy.errors.TooManyRequests as e:
        print(f"Rate limit exceeded. Reset at: {e.response.headers.get('x-rate-limit-reset', 'unknown')}")
        sys.exit(1)
    except tweepy.errors.Forbidden as e:
        print(f"Forbidden: {e}")
        print("This operation may require a higher API tier.")
        sys.exit(1)
    except tweepy.errors.Unauthorized:
        print("Unauthorized: Check your credentials")
        sys.exit(1)
    except tweepy.errors.NotFound:
        print("Not found: Tweet or user may have been deleted")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()