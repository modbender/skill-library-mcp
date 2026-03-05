#!/usr/bin/env python3
"""
Desearch X (Twitter) Search CLI - Real-time X/Twitter search and monitoring.

Usage:
    desearch <command> <query> [options]

Commands:
    x, x_post, x_urls, x_user, x_timeline,
    x_retweeters, x_replies, x_post_replies

Environment:
    DESEARCH_API_KEY - Required API key from desearch.ai
"""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DESEARCH_BASE = "https://api.desearch.ai"

COMMANDS = [
    "x",
    "x_post",
    "x_urls",
    "x_user",
    "x_timeline",
    "x_retweeters",
    "x_replies",
    "x_post_replies",
]


def get_api_key() -> str:
    key = os.environ.get("DESEARCH_API_KEY")
    if not key:
        print("Error: DESEARCH_API_KEY environment variable not set", file=sys.stderr)
        print("Get your key at https://console.desearch.ai", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(
    method: str, path: str, params: dict = None, body: dict = None
) -> dict | str:
    api_key = get_api_key()
    url = f"{DESEARCH_BASE}{path}"

    if method == "GET" and params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url = f"{url}?{urlencode(filtered, doseq=True)}"

    headers = {
        "Authorization": f"{api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Desearch-Clawdbot/1.0",
    }

    data = None
    if method == "POST" and body:
        data = json.dumps(body).encode()

    try:
        req = Request(url, data=data, headers=headers, method=method)
        with urlopen(req, timeout=60) as response:
            raw = response.read().decode()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        try:
            return json.loads(error_body)
        except (json.JSONDecodeError, Exception):
            return {"error": f"HTTP {e.code}: {e.reason}", "details": error_body}
    except URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def cmd_x(args):
    params = {
        "query": args.query,
        "sort": args.sort,
        "user": args.user,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "lang": args.lang,
        "count": args.count,
    }
    if args.verified:
        params["verified"] = "true"
    if args.blue_verified:
        params["blue_verified"] = "true"
    if args.is_quote:
        params["is_quote"] = "true"
    if args.is_video:
        params["is_video"] = "true"
    if args.is_image:
        params["is_image"] = "true"
    if args.min_retweets is not None:
        params["min_retweets"] = args.min_retweets
    if args.min_replies is not None:
        params["min_replies"] = args.min_replies
    if args.min_likes is not None:
        params["min_likes"] = args.min_likes
    return api_request("GET", "/twitter", params=params)


def cmd_x_post(args):
    return api_request("GET", "/twitter/post", params={"id": args.query})


def cmd_x_urls(args):
    params = {"urls": args.urls}
    return api_request("GET", "/twitter/urls", params=params)


def cmd_x_user(args):
    params = {
        "user": args.query,
        "query": args.extra_query or "",
        "count": args.count,
    }
    return api_request("GET", "/twitter/post/user", params=params)


def cmd_x_timeline(args):
    params = {
        "username": args.query,
        "count": args.count,
    }
    return api_request("GET", "/twitter/user/posts", params=params)


def cmd_x_retweeters(args):
    params = {
        "id": args.query,
    }
    if args.cursor:
        params["cursor"] = args.cursor
    return api_request("GET", "/twitter/post/retweeters", params=params)


def cmd_x_replies(args):
    params = {
        "user": args.query,
        "count": args.count,
        "query": args.extra_query or "",
    }
    return api_request("GET", "/twitter/replies", params=params)


def cmd_x_post_replies(args):
    params = {
        "post_id": args.query,
        "count": args.count,
        "query": args.extra_query or "",
    }
    return api_request("GET", "/twitter/replies/post", params=params)


COMMAND_HANDLERS = {
    "x": cmd_x,
    "x_post": cmd_x_post,
    "x_urls": cmd_x_urls,
    "x_user": cmd_x_user,
    "x_timeline": cmd_x_timeline,
    "x_retweeters": cmd_x_retweeters,
    "x_replies": cmd_x_replies,
    "x_post_replies": cmd_x_post_replies,
}


def format_tweets(data):
    lines = []
    if isinstance(data, str):
        return data
    if isinstance(data, dict) and "error" in data:
        return f"Error: {data['error']}"

    tweets = (
        data if isinstance(data, list) else data.get("tweets", data.get("results", []))
    )
    if not isinstance(tweets, list):
        tweets = [data] if isinstance(data, dict) else []

    for t in tweets[:20]:
        user = t.get("user", {})
        username = user.get("username", user.get("screen_name", "unknown"))
        name = user.get("name", username)
        text = t.get("text", t.get("full_text", ""))
        likes = t.get("like_count", t.get("favorite_count", 0))
        retweets = t.get("retweet_count", 0)
        date = t.get("created_at", "")

        lines.append(f"\n@{username} ({name}) - {date}")
        lines.append(f"  {text[:280]}")
        lines.append(f"  Likes: {likes} | Retweets: {retweets}")

        tweet_id = t.get("id", t.get("id_str", ""))
        if tweet_id:
            lines.append(f"  https://x.com/{username}/status/{tweet_id}")

    return "\n".join(lines) if lines else "No tweets found."


TEXT_FORMATTERS = {
    "x": format_tweets,
    "x_post": format_tweets,
    "x_urls": format_tweets,
    "x_user": format_tweets,
    "x_timeline": format_tweets,
    "x_retweeters": lambda d: json.dumps(d, indent=2),
    "x_replies": format_tweets,
    "x_post_replies": format_tweets,
}


def main():
    parser = argparse.ArgumentParser(
        description="Desearch X (Twitter) Search CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("command", choices=COMMANDS, help="Command to execute")
    parser.add_argument(
        "query", help="Search query, post ID, username, or URL (depending on command)"
    )
    parser.add_argument(
        "urls", nargs="*", help="Additional URLs (for x_urls command)"
    )

    parser.add_argument(
        "--count", "-n", type=int, default=None, help="Number of results"
    )

    # X search options
    parser.add_argument(
        "--sort",
        choices=["Top", "Latest"],
        default="Top",
        help="Sort order for X search",
    )
    parser.add_argument("--user", "-u", help="X/Twitter username filter")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--lang", help="Language code (e.g., en, es)")
    parser.add_argument("--verified", action="store_true", help="Filter verified users")
    parser.add_argument(
        "--blue-verified", action="store_true", help="Filter blue verified users"
    )
    parser.add_argument(
        "--is-quote", action="store_true", help="Only tweets with quotes"
    )
    parser.add_argument(
        "--is-video", action="store_true", help="Only tweets with videos"
    )
    parser.add_argument(
        "--is-image", action="store_true", help="Only tweets with images"
    )
    parser.add_argument("--min-retweets", type=int, help="Minimum retweets")
    parser.add_argument("--min-replies", type=int, help="Minimum replies")
    parser.add_argument("--min-likes", type=int, help="Minimum likes")
    parser.add_argument("--cursor", help="Pagination cursor (for retweeters)")
    parser.add_argument(
        "--query", "-q", dest="extra_query", help="Additional query filter"
    )

    args = parser.parse_args()

    if args.command == "x_urls":
        args.urls = [args.query] + (args.urls or [])

    handler = COMMAND_HANDLERS[args.command]
    results = handler(args)

    if isinstance(results, str):
        print(results)
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
