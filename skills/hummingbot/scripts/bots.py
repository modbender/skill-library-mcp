#!/usr/bin/env python3
"""
Bot lifecycle management via Hummingbot API.

Usage:
    python scripts/bots.py list
    python scripts/bots.py deploy <bot_name> --controller <config_name>
    python scripts/bots.py deploy <bot_name> --script <script_name> [--config <config_name>]
    python scripts/bots.py stop <bot_name>
    python scripts/bots.py status <bot_name>
    python scripts/bots.py logs <bot_name> [--lines 50]
    python scripts/bots.py controllers
    python scripts/bots.py scripts
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def cmd_list(args):
    async with client() as c:
        bots = await c.bots.get_active_bots()
        if not bots:
            print("No active bots.")
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


async def cmd_deploy(args):
    async with client() as c:
        if args.controller:
            result = await c.bots.deploy_v2_controllers(
                name=args.bot_name,
                controllers=[args.controller],
            )
        elif args.script:
            result = await c.bots.deploy_v2_script(
                name=args.bot_name,
                script=args.script,
                config=args.config,
            )
        else:
            print("Error: specify --controller or --script")
            sys.exit(1)
        print(f"✓ Bot '{args.bot_name}' deployed")
        if isinstance(result, dict):
            for k, v in result.items():
                print(f"  {k}: {v}")


async def cmd_stop(args):
    async with client() as c:
        await c.bots.stop_bot(args.bot_name)
        print(f"✓ Bot '{args.bot_name}' stopped")


async def cmd_status(args):
    async with client() as c:
        status = await c.bots.get_bot_status(args.bot_name)
        if isinstance(status, dict):
            for k, v in status.items():
                print(f"  {k}: {v}")
        else:
            print(status)


async def cmd_logs(args):
    async with client() as c:
        logs = await c.bots.get_bot_logs(args.bot_name)
        lines = logs if isinstance(logs, list) else str(logs).splitlines()
        for line in lines[-args.lines:]:
            print(line)


async def cmd_controllers(args):
    async with client() as c:
        result = await c.controllers.list_controller_configs()
        if not result:
            print("No controller configs found.")
            return
        if isinstance(result, list):
            for item in result:
                name = item if isinstance(item, str) else item.get("name", str(item))
                print(f"  {name}")
        else:
            print(result)


async def cmd_scripts(args):
    async with client() as c:
        result = await c.scripts.list_scripts()
        if not result:
            print("No scripts found.")
            return
        if isinstance(result, list):
            for item in result:
                name = item if isinstance(item, str) else item.get("name", str(item))
                print(f"  {name}")
        else:
            print(result)


COMMANDS = {
    "list": cmd_list,
    "deploy": cmd_deploy,
    "stop": cmd_stop,
    "status": cmd_status,
    "logs": cmd_logs,
    "controllers": cmd_controllers,
    "scripts": cmd_scripts,
}


def main():
    parser = argparse.ArgumentParser(description="Bot management")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List active bots")

    p_deploy = sub.add_parser("deploy", help="Deploy a bot")
    p_deploy.add_argument("bot_name", help="Bot instance name")
    p_deploy.add_argument("--controller", help="Controller config name")
    p_deploy.add_argument("--script", help="Script name")
    p_deploy.add_argument("--config", help="Script config name")

    p_stop = sub.add_parser("stop", help="Stop a bot")
    p_stop.add_argument("bot_name")

    p_status = sub.add_parser("status", help="Get bot status")
    p_status.add_argument("bot_name")

    p_logs = sub.add_parser("logs", help="Get bot logs")
    p_logs.add_argument("bot_name")
    p_logs.add_argument("--lines", type=int, default=50)

    sub.add_parser("controllers", help="List available controller configs")
    sub.add_parser("scripts", help="List available scripts")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    asyncio.run(COMMANDS[args.command](args))


if __name__ == "__main__":
    main()
