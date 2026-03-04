#!/usr/bin/env python3
"""Board management via Youmind HTTP APIs (API-only)."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api_client import AuthError, YoumindApiClient


def _print(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Youmind boards via API")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all boards")

    p_find = sub.add_parser("find", help="Find boards by keyword (name/id)")
    p_find.add_argument("--query", required=True)

    p_get = sub.add_parser("get", help="Get board detail by id")
    p_get.add_argument("--id", required=True)

    p_create = sub.add_parser("create", help="Create a new board")
    p_create.add_argument("--name", required=True, help="Board name")
    p_create.add_argument("--prompt", help="Optional first prompt to bootstrap board")
    p_create.add_argument("--description", default="")
    p_create.add_argument("--icon-name", default="Game")
    p_create.add_argument("--icon-color", default="--function-red")

    args = parser.parse_args()

    try:
        client = YoumindApiClient()

        if args.command == "list":
            _print(client.list_boards())
            return 0

        if args.command == "find":
            _print(client.find_boards(args.query))
            return 0

        if args.command == "get":
            _print(client.get_board_detail(args.id))
            return 0

        if args.command == "create":
            _print(
                client.create_board(
                    name=args.name,
                    prompt=args.prompt,
                    description=args.description,
                    icon_name=args.icon_name,
                    icon_color=args.icon_color,
                )
            )
            return 0

        parser.print_help()
        return 1

    except AuthError as exc:
        print(f"❌ Auth error: {exc}")
        print("Run: python scripts/run.py auth_manager.py setup")
        return 1
    except Exception as exc:
        print(f"❌ Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
