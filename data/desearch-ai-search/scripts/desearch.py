#!/usr/bin/env python3
"""
Desearch AI Search CLI - AI-powered multi-source search with summarized results.

Usage:
    desearch ai_search "<query>" [options]
    desearch ai_web "<query>" [options]
    desearch ai_x "<query>" [options]

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

COMMANDS = ["ai_search", "ai_web", "ai_x"]

WEB_TOOLS = ["web", "hackernews", "reddit", "wikipedia", "youtube", "arxiv"]

DATE_FILTERS = [
    "PAST_24_HOURS",
    "PAST_2_DAYS",
    "PAST_WEEK",
    "PAST_2_WEEKS",
    "PAST_MONTH",
    "PAST_2_MONTHS",
    "PAST_YEAR",
    "PAST_2_YEARS",
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


def cmd_ai_search(args):
    body = {"prompt": args.query, "streaming": False}
    if args.tools:
        body["tools"] = args.tools.split(",")
    else:
        body["tools"] = ["twitter", "web"]

    if args.count:
        body["result_count"] = args.count
    if args.date_filter:
        body["date_filter"] = args.date_filter
    return api_request("POST", "/desearch/ai/search", body=body)


def cmd_ai_web(args):
    tools = args.tools.split(",") if args.tools else ["web"]
    body = {
        "prompt": args.query,
        "tools": tools,
    }
    if args.count:
        body["count"] = args.count
    return api_request("POST", "/desearch/ai/search/links/web", body=body)


def cmd_ai_x(args):
    body = {"prompt": args.query}
    if args.count:
        body["count"] = args.count
    return api_request("POST", "/desearch/ai/search/links/twitter", body=body)


COMMAND_HANDLERS = {
    "ai_search": cmd_ai_search,
    "ai_web": cmd_ai_web,
    "ai_x": cmd_ai_x,
}


def format_ai_search(data):
    lines = []
    if isinstance(data, str):
        return data
    if "error" in data:
        return f"Error: {data['error']}"

    for key in (
        "search",
        "hacker_news_search",
        "reddit_search",
        "youtube_search",
        "tweets",
    ):
        results = data.get(key)
        if not results:
            continue
        label = key.replace("_", " ").title()
        lines.append(f"\n=== {label} ===")
        for r in results[:10]:
            lines.append(f"\n  {r.get('title', 'No title')}")
            lines.append(f"  {r.get('link', '')}")
            snippet = r.get("snippet", "")
            if snippet:
                lines.append(f"  {snippet[:200]}")

    return "\n".join(lines) if lines else "No results found."


def format_web_links(data):
    lines = []
    if isinstance(data, str):
        return data
    if "error" in data:
        return f"Error: {data['error']}"

    results = (
        data if isinstance(data, list) else data.get("results", data.get("data", []))
    )
    if isinstance(results, dict):
        for source, items in results.items():
            if not isinstance(items, list):
                continue
            lines.append(f"\n=== {source} ===")
            for r in items[:10]:
                lines.append(f"\n  {r.get('title', 'No title')}")
                lines.append(f"  {r.get('link', r.get('url', ''))}")
    elif isinstance(results, list):
        for r in results[:10]:
            lines.append(f"\n  {r.get('title', 'No title')}")
            lines.append(f"  {r.get('link', r.get('url', ''))}")

    return "\n".join(lines) if lines else "No results found."


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
    "ai_search": format_ai_search,
    "ai_web": format_web_links,
    "ai_x": format_tweets,
}


def main():
    parser = argparse.ArgumentParser(
        description="Desearch AI Search CLI - AI-powered multi-source search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("command", choices=COMMANDS, help="Command to execute")
    parser.add_argument("query", help="Search query")

    parser.add_argument(
        "--count", "-n", type=int, default=None, help="Number of results"
    )
    parser.add_argument(
        "--tools",
        "-t",
        help="Comma-separated list of tools: web,hackernews,reddit,wikipedia,youtube,arxiv,twitter",
    )
    parser.add_argument(
        "--date-filter", choices=DATE_FILTERS, help="Date filter for AI search"
    )

    args = parser.parse_args()

    handler = COMMAND_HANDLERS[args.command]
    results = handler(args)

    if isinstance(results, str):
        print(results)
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
