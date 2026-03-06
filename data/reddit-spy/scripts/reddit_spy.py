#!/usr/bin/env python3
"""Reddit Spy -- Stealth subreddit intelligence tool for Radar agent.

Usage:
    python3 reddit_spy.py <command> [options]

Commands:
    spy             Comprehensive single-subreddit intelligence scan
    deep-read       Full post + all comments deep dive
    bulk-scan       Multi-subreddit sweep
    strategy        Extract strategy patterns from a subreddit
    search          Search within a subreddit
    user-intel      Analyze a Reddit user's posting patterns
    health-check    Test which fetching layers are working
"""

import argparse
import json
import sys
from typing import Any, Dict

from lib import cascade_fetcher
from lib.deep_reader import deep_read, read_top_posts
from lib.strategy_extractor import extract_strategy
from lib.subreddit_scanner import scan_subreddit, bulk_scan


def _output(payload: Dict[str, Any]) -> int:
    print(json.dumps(payload, indent=2, default=str))
    return 0


def _error(code: str, message: str) -> int:
    print(json.dumps({"error": code, "message": message}, indent=2))
    return 1


def handle_spy(args: argparse.Namespace) -> int:
    try:
        result = scan_subreddit(args.subreddit, args.sort, args.timeframe, args.limit)
        return _output(result)
    except Exception as e:
        return _error("spy-failed", str(e))


def handle_deep_read(args: argparse.Namespace) -> int:
    try:
        result = deep_read(args.url, args.depth, args.comment_limit)
        return _output(result)
    except Exception as e:
        return _error("deep-read-failed", str(e))


def handle_bulk_scan(args: argparse.Namespace) -> int:
    subs = [s.strip() for s in args.subreddits.split(",") if s.strip()]
    if len(subs) < 1:
        return _error("no-subreddits", "Provide comma-separated subreddit names")
    try:
        result = bulk_scan(subs, args.sort, args.timeframe, args.limit)
        return _output(result)
    except Exception as e:
        return _error("bulk-scan-failed", str(e))


def handle_strategy(args: argparse.Namespace) -> int:
    try:
        posts = read_top_posts(args.subreddit, args.sort, args.timeframe, args.limit)
        result = extract_strategy(posts)
        result["subreddit"] = args.subreddit
        return _output(result)
    except Exception as e:
        return _error("strategy-failed", str(e))


def handle_search(args: argparse.Namespace) -> int:
    try:
        results = cascade_fetcher.search_posts(
            args.subreddit, args.query, args.sort, args.timeframe, args.limit,
        )
        return _output({"subreddit": args.subreddit, "query": args.query, "results": results})
    except Exception as e:
        return _error("search-failed", str(e))


def handle_user_intel(args: argparse.Namespace) -> int:
    try:
        posts = cascade_fetcher.fetch_user_posts(args.username, args.limit)
        strategy = extract_strategy(posts)
        subs = {}
        for p in posts:
            sub = p.get("subreddit", "unknown")
            subs[sub] = subs.get(sub, 0) + 1
        return _output({
            "username": args.username,
            "total_posts": len(posts),
            "subreddits": subs,
            "patterns": strategy,
        })
    except Exception as e:
        return _error("user-intel-failed", str(e))


def handle_health_check(args: argparse.Namespace) -> int:
    result = cascade_fetcher.health_check()
    test_sub = args.test_sub or "python"
    tests = [("oauth", _test_oauth), ("tor", _test_tor), ("stealth_http", _test_http), ("browser", _test_browser), ("pullpush", _test_pullpush)]
    for layer_name, fn in tests:
        result[layer_name]["test"] = fn(test_sub)
    return _output(result)


def _test_oauth(sub: str) -> str:
    from lib import reddit_auth
    if not reddit_auth.is_configured():
        return "skipped (not configured)"
    try:
        reddit_auth.fetch_about(sub)
        return "OK"
    except Exception as e:
        return f"FAIL: {e}"


def _test_tor(sub: str) -> str:
    from lib import tor_client
    if not tor_client.is_available():
        return "skipped (tor not running)"
    try:
        data = tor_client.fetch_about(sub)
        subs = data.get("subscribers", "?")
        return f"OK (subscribers: {subs})"
    except Exception as e:
        return f"FAIL: {e}"


def _test_http(sub: str) -> str:
    from lib import stealth_http
    try:
        stealth_http.fetch_about(sub)
        return "OK"
    except Exception as e:
        return f"FAIL: {e}"


def _test_browser(sub: str) -> str:
    from lib import browser_stealth
    if not browser_stealth.is_available():
        return "skipped (not installed)"
    try:
        browser_stealth.fetch_about(sub)
        return "OK"
    except Exception as e:
        return f"FAIL: {e}"


def _test_pullpush(sub: str) -> str:
    from lib import pullpush_client
    try:
        posts = pullpush_client.fetch_posts(sub, limit=1)
        return f"OK ({len(posts)} posts)"
    except Exception as e:
        return f"FAIL: {e}"


def _add_commands(subparsers: argparse._SubParsersAction) -> None:
    spy = subparsers.add_parser("spy", help="Comprehensive subreddit intelligence scan")
    spy.add_argument("--subreddit", required=True)
    spy.add_argument("--sort", default="top", choices=["hot", "new", "top", "rising"])
    spy.add_argument("--timeframe", default="week", choices=["hour", "day", "week", "month", "year", "all"])
    spy.add_argument("--limit", type=int, default=25)

    dr = subparsers.add_parser("deep-read", help="Full post + comments deep dive")
    dr.add_argument("--url", required=True)
    dr.add_argument("--depth", type=int, default=8)
    dr.add_argument("--comment-limit", type=int, default=200)

    bs = subparsers.add_parser("bulk-scan", help="Multi-subreddit intelligence sweep")
    bs.add_argument("--subreddits", required=True, help="Comma-separated names")
    bs.add_argument("--sort", default="top", choices=["hot", "new", "top", "rising"])
    bs.add_argument("--timeframe", default="week", choices=["hour", "day", "week", "month", "year", "all"])
    bs.add_argument("--limit", type=int, default=25)

    st = subparsers.add_parser("strategy", help="Extract strategy patterns")
    st.add_argument("--subreddit", required=True)
    st.add_argument("--sort", default="top", choices=["hot", "new", "top", "rising"])
    st.add_argument("--timeframe", default="week", choices=["hour", "day", "week", "month", "year", "all"])
    st.add_argument("--limit", type=int, default=50)

    sr = subparsers.add_parser("search", help="Search within a subreddit")
    sr.add_argument("--subreddit", required=True)
    sr.add_argument("--query", required=True)
    sr.add_argument("--sort", default="relevance", choices=["relevance", "top", "new", "comments"])
    sr.add_argument("--timeframe", default="all", choices=["hour", "day", "week", "month", "year", "all"])
    sr.add_argument("--limit", type=int, default=25)

    ui = subparsers.add_parser("user-intel", help="Analyze a Reddit user")
    ui.add_argument("--username", required=True)
    ui.add_argument("--limit", type=int, default=25)

    hc = subparsers.add_parser("health-check", help="Test fetching layers")
    hc.add_argument("--test-sub", default="python", help="Subreddit for testing")


HANDLERS = {
    "spy": handle_spy,
    "deep-read": handle_deep_read,
    "bulk-scan": handle_bulk_scan,
    "strategy": handle_strategy,
    "search": handle_search,
    "user-intel": handle_user_intel,
    "health-check": handle_health_check,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Reddit Spy -- Stealth subreddit intelligence")
    subs = parser.add_subparsers(dest="command", required=True)
    _add_commands(subs)
    args = parser.parse_args()
    handler = HANDLERS.get(args.command)
    if not handler:
        return _error("unknown-command", f"Unknown: {args.command}")
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
