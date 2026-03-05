#!/usr/bin/env python3
"""
x-cli search — Search tweets on X/Twitter.

Usage:
  python x_search.py "query" [--count N] [--json]

Advanced queries:
  python x_search.py "from:zerohedge gold"
  python x_search.py "CPI inflation lang:en"
  python x_search.py "#Bitcoin min_faves:100"
"""

import argparse
import json

from x_utils import get_client, format_tweet, run


async def cmd_search(args):
    client = await get_client()
    tweets = await client.search_tweet(args.query, product="Latest", count=args.count)
    separator = "\n" if args.json else "\n" + "─" * 50 + "\n"
    output = []
    for tweet in tweets[:args.count]:
        output.append(format_tweet(tweet, args.json))

    if not output:
        print("No results found." if not args.json else json.dumps({"results": []}))
        return

    print(separator.join(output))


def main():
    parser = argparse.ArgumentParser(description="x-cli search — Search X/Twitter")
    parser.add_argument("query", help="Search query (supports X advanced search syntax)")
    parser.add_argument("--count", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    run(cmd_search(args))


if __name__ == "__main__":
    main()
