#!/usr/bin/env python3
"""
Start a bot with a configuration.

Note: Only V2 strategies are supported in Hummingbot API.
      V1 strategies must use the traditional Hummingbot client.

Usage:
    # Interactive mode - prompts for bot type
    python start.py my_bot

    # Start a bot with a controller config
    python start.py my_bot --controller my_config

    # Start a bot with a script
    python start.py my_bot --script v2_with_controllers --config my_config

    # List running bots
    python start.py --list
"""

import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def list_available_configs():
    """List available controller configs and scripts."""
    async with client() as c:
        configs = await c.controllers.list_controller_configs()
        scripts = await c.scripts.list_scripts()
        return configs, scripts


async def start_bot_interactive(bot_name: str):
    """Interactive mode to start a bot."""
    print(f"\nStarting bot: {bot_name}")
    print("=" * 50)
    print("\nHummingbot API supports V2 strategies only:")
    print("  1. V2 Controller - Use a controller config")
    print("  2. V2 Script     - Use a script with optional config")
    print()

    choice = input("Select strategy type [1/2]: ").strip()

    if choice == "1":
        # V2 Controller
        async with client() as c:
            configs = await c.controllers.list_controller_configs()

        if configs:
            print("\nAvailable controller configs:")
            for i, cfg in enumerate(configs, 1):
                name = cfg.get("id", cfg.get("name", str(cfg))) if isinstance(cfg, dict) else cfg
                print(f"  {i}. {name}")
            print()

        controller = input("Enter controller config name: ").strip()
        if not controller:
            print("Error: Controller config name is required")
            return

        await start_bot(bot_name, controller=controller)

    elif choice == "2":
        # V2 Script
        async with client() as c:
            scripts = await c.scripts.list_scripts()

        if scripts:
            print("\nAvailable scripts:")
            for script in scripts:
                name = script.get("name", str(script)) if isinstance(script, dict) else script
                print(f"  - {name}")
            print()

        script = input("Enter script name (default: v2_with_controllers): ").strip()
        if not script:
            script = "v2_with_controllers"

        config = input("Enter script config name (optional): ").strip()
        if not config:
            config = None

        await start_bot(bot_name, script=script, config=config)

    else:
        print("Invalid choice. Use 1 for Controller or 2 for Script.")


async def start_bot(bot_name: str, controller: str = None, script: str = None, config: str = None):
    """Start a bot."""
    async with client() as c:
        if controller:
            # Deploy with V2 controllers
            result = await c.bot_orchestration.deploy_v2_controllers(
                instance_name=bot_name,
                controllers_config=[controller],
            )
            print(f"Started bot '{bot_name}' with controller config '{controller}'")
        elif script:
            # Deploy with script
            result = await c.bot_orchestration.deploy_v2_script(
                instance_name=bot_name,
                script=script,
                script_config=config,
            )
            if config:
                print(f"Started bot '{bot_name}' with script '{script}' and config '{config}'")
            else:
                print(f"Started bot '{bot_name}' with script '{script}'")
        else:
            # No options specified - go interactive
            await start_bot_interactive(bot_name)
            return

        # Show result
        if isinstance(result, dict):
            for k, v in result.items():
                if k not in ["status", "success"]:
                    print(f"  {k}: {v}")


async def list_bots():
    """List all bots."""
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
            print("\nStart a bot with: python start.py <bot_name>")
            return

        rows = [
            {
                "name": b.get("bot_name", b.get("instance_name", "?")),
                "status": b.get("status", "?"),
                "script": b.get("script", b.get("strategy", "?")),
                "started": b.get("start_time", "?"),
            }
            for b in bots
        ]
        print_table(rows, ["name", "status", "script", "started"])


def main():
    parser = argparse.ArgumentParser(
        description="Start a bot (V2 strategies only)",
        epilog="Note: V1 strategies are not supported in Hummingbot API"
    )
    parser.add_argument("bot_name", nargs="?", help="Bot name")
    parser.add_argument("--controller", help="V2 Controller config name")
    parser.add_argument("--script", help="V2 Script name")
    parser.add_argument("--config", help="Script config name (used with --script)")
    parser.add_argument("--list", action="store_true", help="List running bots")
    args = parser.parse_args()

    try:
        if args.list:
            asyncio.run(list_bots())
        elif args.bot_name:
            if args.controller or args.script:
                asyncio.run(start_bot(
                    args.bot_name,
                    controller=args.controller,
                    script=args.script,
                    config=args.config
                ))
            else:
                # Interactive mode
                asyncio.run(start_bot_interactive(args.bot_name))
        else:
            parser.print_help()
            print("\nV2 Strategy Types:")
            print("  --controller  Deploy a V2 controller config")
            print("  --script      Deploy a V2 script")
            print("\nExamples:")
            print("  python start.py my_bot                           # Interactive mode")
            print("  python start.py my_bot --controller my_mm_config")
            print("  python start.py my_bot --script v2_with_controllers --config my_config")
            print("  python start.py --list")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
