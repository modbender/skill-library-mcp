#!/usr/bin/env python3
"""
OptionWhales Option Flow Intelligence — CLI Helper

A thin CLI wrapper for the OptionWhales Pro API. Designed for use by OpenClaw
agents and human developers alike.

Usage:
    python3 optionflow.py flow [--ticker AAPL] [--session 2025-06-02]
    python3 optionflow.py momentum [--top 10] [--ticker AAPL]
    python3 optionflow.py abnormal [--session 2025-06-02]
    python3 optionflow.py sessions
    python3 optionflow.py usage

Reads OPTIONWHALES_API_KEY from the environment.
Outputs JSON to stdout for piping through jq or agent parsing.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.optionwhales.io/v1"


def get_api_key() -> str:
    """Read API key from environment."""
    key = os.environ.get("OPTIONWHALES_API_KEY", "")
    if not key:
        print(
            json.dumps({"error": "OPTIONWHALES_API_KEY environment variable not set"}),
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def api_request(path: str, api_key: str) -> dict:
    """Make an authenticated GET request to the Pro API."""
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"X-API-Key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            err = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            err = {"detail": body or e.reason}
        print(
            json.dumps(
                {"error": f"HTTP {e.code}", "detail": err},
                indent=2,
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    except urllib.error.URLError as e:
        print(
            json.dumps({"error": "Connection failed", "detail": str(e.reason)}),
            file=sys.stderr,
        )
        sys.exit(1)


# ─── Subcommands ───────────────────────────────────────────────────────────


def cmd_flow(args, api_key: str):
    """Get intent flow rankings or ticker detail."""
    if args.session and args.ticker:
        path = f"/flow/{args.session}/{args.ticker}"
    elif args.session:
        path = f"/flow/{args.session}"
    elif args.ticker:
        path = f"/flow/current/{args.ticker}"
    else:
        path = "/flow/current"
    data = api_request(path, api_key)
    print(json.dumps(data, indent=2))


def cmd_momentum(args, api_key: str):
    """Get momentum rankings or ticker history."""
    if args.ticker:
        path = f"/momentum/{args.ticker}/history"
        if args.sessions:
            path += f"?sessions={args.sessions}"
        data = api_request(path, api_key)
    else:
        data = api_request("/momentum/rankings", api_key)
        # Optional: limit to top N
        if args.top and isinstance(data, dict) and "rankings" in data:
            data["rankings"] = data["rankings"][: args.top]
        elif args.top and isinstance(data, list):
            data = data[: args.top]
    print(json.dumps(data, indent=2))


def cmd_abnormal(args, api_key: str):
    """Get abnormal trades."""
    if args.session:
        path = f"/abnormal-trades/{args.session}"
    else:
        path = "/abnormal-trades/current"
    data = api_request(path, api_key)
    print(json.dumps(data, indent=2))


def cmd_sessions(args, api_key: str):
    """List available sessions."""
    data = api_request("/flow/sessions", api_key)
    print(json.dumps(data, indent=2))


def cmd_usage(args, api_key: str):
    """Show account usage stats."""
    data = api_request("/account/usage", api_key)
    print(json.dumps(data, indent=2))


# ─── Argument Parser ───────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="optionflow",
        description="Query OptionWhales Pro API for option flow intelligence",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # flow
    p_flow = sub.add_parser("flow", help="Intent flow rankings or ticker detail")
    p_flow.add_argument("--ticker", "-t", help="Ticker symbol (e.g. AAPL)")
    p_flow.add_argument("--session", "-s", help="Session date (YYYY-MM-DD)")

    # momentum
    p_mom = sub.add_parser("momentum", help="Momentum rankings or ticker history")
    p_mom.add_argument("--ticker", "-t", help="Ticker for history lookup")
    p_mom.add_argument("--top", type=int, help="Limit to top N tickers")
    p_mom.add_argument(
        "--sessions", type=int, help="Number of history sessions (1-30)"
    )

    # abnormal
    p_abn = sub.add_parser("abnormal", help="Abnormal / unusual option trades")
    p_abn.add_argument("--session", "-s", help="Session date (YYYY-MM-DD)")

    # sessions
    sub.add_parser("sessions", help="List available sessions")

    # usage
    sub.add_parser("usage", help="Show account usage stats")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    api_key = get_api_key()

    dispatch = {
        "flow": cmd_flow,
        "momentum": cmd_momentum,
        "abnormal": cmd_abnormal,
        "sessions": cmd_sessions,
        "usage": cmd_usage,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args, api_key)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
