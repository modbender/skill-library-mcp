#!/usr/bin/env python3
"""
Display bot trading history.

Usage:
    # Show trade history for a bot
    python history.py my_bot

    # Show summary statistics
    python history.py my_bot --summary
"""

import argparse
import asyncio
import json
import sys
import os
import urllib.request
import urllib.error
import base64

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import get_config, print_table


def api_request(endpoint: str) -> dict:
    """Make authenticated GET request to API."""
    url_base, username, password = get_config()
    url = f"{url_base}{endpoint}"
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {credentials}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"HTTP {e.code}: {error_body}")


async def get_bot_history(bot_name: str, show_summary: bool = False):
    """Get trade history for a bot."""
    try:
        result = api_request(f"/bot-orchestration/{bot_name}/history")
        history = result.get("response", result)

        if isinstance(history, dict) and history.get("success") is False:
            print(f"Bot '{bot_name}' not found")
            return
    except Exception as e:
        print(f"Could not get history for '{bot_name}': {e}")
        return

        if not history:
            print(f"No history found for bot '{bot_name}'")
            return

        # Handle different response formats
        if isinstance(history, dict):
            if "response" in history:
                history = history["response"]
            elif "data" in history:
                history = history["data"]

        if show_summary:
            show_trade_summary(history, bot_name)
            return

        # Display history
        print(f"Trade History: {bot_name}")
        print("=" * 80)

        if isinstance(history, dict):
            # Print key-value pairs
            for key, value in history.items():
                if isinstance(value, (list, dict)):
                    print(f"\n{key}:")
                    if isinstance(value, list):
                        for item in value[:20]:  # Limit display
                            print(f"  {item}")
                    else:
                        for k, v in value.items():
                            print(f"  {k}: {v}")
                else:
                    print(f"{key}: {value}")
        elif isinstance(history, list):
            # Print as table if list of dicts
            if history and isinstance(history[0], dict):
                rows = []
                for trade in history[:50]:  # Limit to 50 trades
                    rows.append({
                        "time": str(trade.get("timestamp", trade.get("time", "")))[:19],
                        "pair": trade.get("trading_pair", trade.get("symbol", "")),
                        "side": trade.get("side", trade.get("trade_type", "")),
                        "price": f"{float(trade.get('price', 0)):,.4f}",
                        "amount": f"{float(trade.get('amount', 0)):,.6f}",
                    })
                print_table(rows, ["time", "pair", "side", "price", "amount"])
                print(f"\nShowing {len(rows)} of {len(history)} trades")
            else:
                for item in history:
                    print(item)
        else:
            print(history)


def show_trade_summary(history, bot_name: str):
    """Show summary statistics for trades."""
    print(f"Trade Summary: {bot_name}")
    print("=" * 50)

    if isinstance(history, dict):
        # Print summary fields
        for key in ["total_trades", "pnl", "volume", "win_rate"]:
            if key in history:
                print(f"{key}: {history[key]}")
        return

    if not isinstance(history, list):
        print("No trade data to summarize")
        return

    total_trades = len(history)
    print(f"Total Trades: {total_trades}")

    # Count buys and sells
    buys = sum(1 for t in history if str(t.get("side", t.get("trade_type", ""))).lower() == "buy")
    sells = sum(1 for t in history if str(t.get("side", t.get("trade_type", ""))).lower() == "sell")
    print(f"Buys: {buys}, Sells: {sells}")


def main():
    parser = argparse.ArgumentParser(description="Display bot trading history")
    parser.add_argument("bot_name", help="Bot name")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics")
    args = parser.parse_args()

    try:
        asyncio.run(get_bot_history(args.bot_name, show_summary=args.summary))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
