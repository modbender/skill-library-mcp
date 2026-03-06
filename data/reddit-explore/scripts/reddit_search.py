#!/usr/bin/env python3
"""Search Reddit via Apify's trudax/reddit-scraper-lite actor."""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Search Reddit via Apify")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max-items", type=int, default=30, help="Max results (default: 30)")
    parser.add_argument("--token", help="Apify API token (or set APIFY_TOKEN env var)")
    args = parser.parse_args()

    token = args.token or os.environ.get("APIFY_TOKEN")
    if not token:
        print("Error: APIFY_TOKEN not found. Set it as an environment variable or pass --token.", file=sys.stderr)
        sys.exit(1)

    try:
        from apify_client import ApifyClient
    except ImportError:
        print("Error: apify-client not installed. Run: pip3 install apify-client", file=sys.stderr)
        sys.exit(1)

    client = ApifyClient(token)

    run_input = {
        "searches": [args.query],
        "searchPosts": True,
        "searchComments": False,
        "skipComments": True,
        "sort": "relevance",
        "maxItems": args.max_items,
    }

    try:
        run = client.actor("trudax/reddit-scraper-lite").call(run_input=run_input)
    except Exception as e:
        print(f"Error: Apify API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())

    # Deduplicate by URL
    seen_urls = set()
    unique_posts = []
    for item in items:
        url = item.get("url", "")
        base_url = url.split("?")[0].rstrip("/")
        if base_url and base_url not in seen_urls:
            seen_urls.add(base_url)
            unique_posts.append(item)

    json.dump(unique_posts, sys.stdout, indent=2, default=str)


if __name__ == "__main__":
    main()
