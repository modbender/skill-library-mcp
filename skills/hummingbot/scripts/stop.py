#!/usr/bin/env python3
"""
Stop a running bot.

Usage:
    # Stop a bot by name
    python stop.py my_bot

    # Stop all running bots
    python stop.py --all
"""

import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client


async def stop_bot(bot_name: str):
    """Stop a specific bot."""
    async with client() as c:
        await c.bot_orchestration.stop_bot(bot_name=bot_name)
        print(f"Stopped bot '{bot_name}'")


async def stop_all_bots():
    """Stop all running bots."""
    async with client() as c:
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
            return

        stopped = 0
        for bot in bots:
            name = bot.get("bot_name", bot.get("instance_name"))
            if name:
                try:
                    await c.bot_orchestration.stop_bot(bot_name=name)
                    print(f"Stopped: {name}")
                    stopped += 1
                except Exception as e:
                    print(f"Failed to stop {name}: {e}")

        print(f"\nStopped {stopped} bot(s)")


def main():
    parser = argparse.ArgumentParser(description="Stop a bot")
    parser.add_argument("bot_name", nargs="?", help="Bot name")
    parser.add_argument("--all", action="store_true", help="Stop all running bots")
    args = parser.parse_args()

    try:
        if args.all:
            asyncio.run(stop_all_bots())
        elif args.bot_name:
            asyncio.run(stop_bot(args.bot_name))
        else:
            parser.print_help()
            print("\nExamples:")
            print("  python stop.py my_bot")
            print("  python stop.py --all")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
