#!/usr/bin/env python3
"""Fallback web search for Weibo content via Brave Search API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search weibo.com using Brave Search API (fallback when Weibo API is unavailable)."
    )
    parser.add_argument("keyword", help="Search keyword or phrase.")
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of results to return (default: 10).",
    )
    parser.add_argument(
        "--freshness",
        default="pd",
        choices=["pd", "pw", "pm", "py"],
        help="Result freshness: pd/day, pw/week, pm/month, py/year (default: pd).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit compact JSON only.",
    )
    return parser.parse_args()


def perform_search(keyword: str, count: int, freshness: str) -> dict[str, Any]:
    api_key = os.getenv("BRAVE_SEARCH_API")
    if not api_key:
        raise RuntimeError("Missing BRAVE_SEARCH_API environment variable.")

    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": api_key},
        params={
            "q": f"site:weibo.com {keyword}",
            "count": count,
            "freshness": freshness,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    args = parse_args()
    try:
        payload = perform_search(args.keyword, args.count, args.freshness)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    results = payload.get("web", {}).get("results", [])
    if args.json:
        print(json.dumps(results, ensure_ascii=False))
        return 0

    if not results:
        print("No results.")
        return 0

    for item in results:
        print(f"Title: {item.get('title', '')}")
        print(f"URL: {item.get('url', '')}")
        print(f"Description: {item.get('description', '')}")
        print("---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
