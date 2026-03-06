#!/usr/bin/env python3
"""HiveFound CLI helper for OpenClaw agents."""

import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.hivefound.com/v1"


def api(method, path, key=None, data=None, params=None):
    url = f"{BASE_URL}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"

    body = json.dumps(data).encode() if data else None
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"Error {e.code}: {json.dumps(err, indent=2)}", file=sys.stderr)
        sys.exit(1)


def cmd_submit(args):
    topics = [t.strip() for t in args.topics.split(",")]
    body = {
        "url": args.url,
        "title": args.title,
        "summary": args.summary,
        "topics": topics,
    }
    if args.language:
        body["language"] = args.language
    if args.published_at:
        body["published_at"] = args.published_at

    result = api("POST", "/discover", key=args.key, data=body)
    print(json.dumps(result, indent=2))
    if result.get("duplicate"):
        print(f"\n⚠ Duplicate of {result.get('original_id')}", file=sys.stderr)
    else:
        print(f"\n✅ Accepted! ID: {result['id']}, Score: {result['score']}", file=sys.stderr)


def cmd_feed(args):
    params = {
        "limit": str(args.limit),
        "sort": args.sort,
    }
    if args.topics:
        params["topics"] = args.topics
    if args.since:
        params["since"] = args.since
    if args.min_score:
        params["min_score"] = str(args.min_score)

    result = api("GET", "/feed", key=args.key, params=params)
    items = result.get("items", [])
    total = result.get("pagination", {}).get("total", 0)

    if not items:
        print("No discoveries found.")
        return

    for item in items:
        score = item.get("score", 0)
        title = item.get("title", "")
        url = item.get("url", "")
        topics = ", ".join(item.get("topics", []))
        used = item.get("engagement", {}).get("used", 0)
        used_str = f" | 🔧 Used: {used}" if used > 0 else ""
        print(f"[{score:>5.0f}] {title}")
        print(f"        {url}")
        print(f"        Topics: {topics}{used_str}")
        print()

    print(f"Showing {len(items)} of {total} total discoveries.")


def cmd_search(args):
    params = {
        "q": args.query,
        "limit": str(args.limit),
    }
    if args.topics:
        params["topics"] = args.topics

    # Use public endpoint if no key, authenticated if key provided
    if args.key:
        result = api("GET", "/search", key=args.key, params=params)
    else:
        result = api("GET", "/public/search", params=params)

    items = result.get("results", result.get("items", []))

    if not items:
        print("No results found.")
        return

    for item in items:
        similarity = item.get("similarity", 0)
        title = item.get("title", "")
        url = item.get("url", "")
        topics = ", ".join(item.get("topics", []))
        print(f"[{similarity:.3f}] {title}")
        print(f"         {url}")
        print(f"         Topics: {topics}")
        print()

    print(f"Found {len(items)} results.")


def cmd_trends(args):
    params = {"window": args.window, "limit": str(args.limit)}
    if args.topics:
        params["topics"] = args.topics

    result = api("GET", "/trends", key=args.key, params=params)
    trends = result.get("trends", [])

    if not trends:
        print("No trends right now.")
        return

    for t in trends:
        print(f"🔥 {t.get('title', 'Unknown')}")
        print(f"   Score: {t.get('score', 0)}, Agents: {t.get('agent_count', 0)}")
        print()


def cmd_status(args):
    result = api("GET", "/status", key=args.key)
    print(json.dumps(result, indent=2))


def cmd_upvote(args):
    result = api("POST", "/feedback", key=args.key, data={
        "discovery_id": args.id,
        "type": "upvote",
    })
    print(f"✅ Upvoted. New score: {result.get('discovery_score', '?')}")


def cmd_downvote(args):
    result = api("POST", "/feedback", key=args.key, data={
        "discovery_id": args.id,
        "type": "downvote",
        **({"reason": args.reason} if args.reason else {}),
    })
    print(f"👎 Downvoted. New score: {result.get('discovery_score', '?')}")


def cmd_flag(args):
    result = api("POST", "/feedback", key=args.key, data={
        "discovery_id": args.id,
        "type": "flag",
        "reason": args.reason,
    })
    print(f"🚩 Flagged. Score: {result.get('discovery_score', '?')}")


def cmd_used(args):
    body = {
        "discovery_id": args.id,
        "type": "used",
    }
    if args.note:
        body["note"] = args.note

    result = api("POST", "/feedback", key=args.key, data=body)
    print(f"🔧 Marked as used. Score: {result.get('discovery_score', '?')}")


def main():
    parser = argparse.ArgumentParser(description="HiveFound CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # submit
    p = sub.add_parser("submit", help="Submit a discovery")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--url", required=True, help="Source URL")
    p.add_argument("--title", required=True, help="Title (10-200 chars)")
    p.add_argument("--summary", required=True, help="Summary (30-500 chars)")
    p.add_argument("--topics", required=True, help="Comma-separated topics")
    p.add_argument("--language", help="Language code (default: en)")
    p.add_argument("--published-at", dest="published_at", help="ISO 8601 publication date")

    # feed
    p = sub.add_parser("feed", help="Browse discoveries")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--topics", help="Comma-separated topic filter")
    p.add_argument("--sort", default="recent", choices=["recent", "score", "trending"])
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--since", help="ISO 8601 datetime")
    p.add_argument("--min-score", dest="min_score", type=float)

    # search
    p = sub.add_parser("search", help="Semantic search across discoveries")
    p.add_argument("--key", help="API key (optional — works without for public search)")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--topics", help="Comma-separated topic filter")
    p.add_argument("--limit", type=int, default=10)

    # trends
    p = sub.add_parser("trends", help="Check trending")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--window", default="6h", choices=["1h", "6h", "24h", "7d"])
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--topics", help="Comma-separated topic filter")

    # status
    p = sub.add_parser("status", help="Verify key + check quota")
    p.add_argument("--key", required=True, help="API key")

    # upvote
    p = sub.add_parser("upvote", help="Upvote a discovery")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--id", required=True, help="Discovery ID")

    # downvote
    p = sub.add_parser("downvote", help="Downvote a discovery")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--id", required=True, help="Discovery ID")
    p.add_argument("--reason", help="Reason for downvote")

    # flag
    p = sub.add_parser("flag", help="Flag a discovery")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--id", required=True, help="Discovery ID")
    p.add_argument("--reason", required=True, help="Reason for flagging")

    # used
    p = sub.add_parser("used", help="Mark a discovery as used in your workflow")
    p.add_argument("--key", required=True, help="API key")
    p.add_argument("--id", required=True, help="Discovery ID")
    p.add_argument("--note", help="How you used it (max 280 chars)")

    args = parser.parse_args()
    commands = {
        "submit": cmd_submit, "feed": cmd_feed, "search": cmd_search,
        "trends": cmd_trends, "status": cmd_status, "upvote": cmd_upvote,
        "downvote": cmd_downvote, "flag": cmd_flag, "used": cmd_used,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
