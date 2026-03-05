#!/usr/bin/env python3
"""
Display bot status and performance metrics.

Usage:
    # List all bots with status
    python status.py

    # Get detailed status for a specific bot
    python status.py my_bot

    # Get status with performance metrics
    python status.py my_bot --performance
"""

import argparse
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, get_config


async def list_all_bots():
    """List all bots with their status."""
    url, _, _ = get_config()

    # Check API connectivity first
    try:
        async with client() as c:
            print(f"API: {url}")
            print("-" * 60)

            result = await c.bot_orchestration.get_active_bots_status()
            # Handle response - may be dict with 'data' key containing bot dict
            if isinstance(result, dict):
                data = result.get("data", result)
                if isinstance(data, dict):
                    bots = list(data.values())
                else:
                    bots = data if data else []
            else:
                bots = result if result else []

            if not bots:
                print("No bots running")
                print("\nStart a bot with: python start.py <bot_name> --controller <config>")
                return

            print(f"{'BOT NAME':20} {'STATUS':12} {'CONFIG/SCRIPT':25}")
            print("-" * 60)

            for bot in bots:
                name = bot.get("bot_name", bot.get("instance_name", "unknown"))
                status = bot.get("status", "unknown")
                config = bot.get("controller_config") or bot.get("script") or "-"
                print(f"{name:20} {status:12} {config:25}")

            print(f"\nTotal: {len(bots)} bot(s)")

    except Exception as e:
        print(f"Cannot connect to API at {url}")
        print(f"Error: {e}")
        print("\nRun: cd ./hummingbot-api && make deploy")
        sys.exit(1)


async def get_bot_status(bot_name: str, show_performance: bool = False):
    """Get detailed status for a specific bot."""
    async with client() as c:
        # Get bot info
        try:
            result = await c.bot_orchestration.get_bot_status(bot_name)
            # Handle response format
            if isinstance(result, dict):
                bot = result.get("data", result)
            else:
                bot = result

            if not bot:
                print(f"Bot '{bot_name}' not found")
                print("\nList running bots with: python status.py")
                return
        except Exception as e:
            print(f"Error: {e}")
            return

        print(f"Bot: {bot_name}")
        print("=" * 50)

        status = bot.get("status", "unknown")
        print(f"Status: {status}")

        config = bot.get("controller_config") or bot.get("script")
        if config:
            print(f"Config: {config}")

        start_time = bot.get("start_time")
        if start_time:
            try:
                start_dt = datetime.fromisoformat(str(start_time).replace("Z", "+00:00"))
                uptime = datetime.now(start_dt.tzinfo) - start_dt
                hours = int(uptime.total_seconds() // 3600)
                minutes = int((uptime.total_seconds() % 3600) // 60)
                print(f"Uptime: {hours}h {minutes}m")
            except Exception:
                print(f"Started: {start_time}")

        if show_performance:
            print("\nPerformance:")
            print("-" * 30)

            # Get performance metrics
            try:
                perf = await c.bot_orchestration.get_bot_performance(bot_name)

                total_trades = perf.get("total_trades", 0)
                print(f"Total Trades: {total_trades}")

                pnl = perf.get("pnl", 0)
                pnl_pct = perf.get("pnl_percent", 0)
                print(f"PnL: ${pnl:,.2f} ({pnl_pct:+.2f}%)")

                volume = perf.get("volume", 0)
                print(f"Volume: ${volume:,.2f}")

            except Exception:
                print("Performance data not available")


def main():
    parser = argparse.ArgumentParser(description="Display bot status")
    parser.add_argument("bot_name", nargs="?", help="Bot name")
    parser.add_argument("--performance", action="store_true", help="Show performance metrics")
    args = parser.parse_args()

    try:
        if args.bot_name:
            asyncio.run(get_bot_status(args.bot_name, args.performance))
        else:
            asyncio.run(list_all_bots())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
