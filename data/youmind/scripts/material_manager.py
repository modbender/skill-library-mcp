#!/usr/bin/env python3
"""Material operations via Youmind HTTP APIs (API-only)."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api_client import AuthError, YoumindApiClient


def _print(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _resolve_board_id(client: YoumindApiClient, board_id: str | None, board_url: str | None) -> str:
    if board_id:
        return board_id
    if board_url:
        return client.board_id_from_url(board_url)
    raise ValueError("Provide --board-id or --board-url")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage board materials via API")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add_link = sub.add_parser("add-link", help="Add a URL to board")
    p_add_link.add_argument("--board-id")
    p_add_link.add_argument("--board-url")
    p_add_link.add_argument("--url", required=True)

    p_upload = sub.add_parser("upload-file", help="Upload a local file to board")
    p_upload.add_argument("--board-id")
    p_upload.add_argument("--board-url")
    p_upload.add_argument("--file", required=True)

    p_snips = sub.add_parser("get-snips", help="Get snips by ids")
    p_snips.add_argument("--ids", required=True, help="Comma-separated snip ids")

    p_picks = sub.add_parser("list-picks", help="List picks by board id")
    p_picks.add_argument("--board-id")
    p_picks.add_argument("--board-url")

    args = parser.parse_args()

    try:
        client = YoumindApiClient()

        if args.command == "add-link":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(client.add_link(board_id=bid, url=args.url))
            return 0

        if args.command == "upload-file":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(client.upload_file(board_id=bid, file_path=args.file))
            return 0

        if args.command == "get-snips":
            ids = [x.strip() for x in args.ids.split(",") if x.strip()]
            _print(client.get_snips(ids))
            return 0

        if args.command == "list-picks":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(client.list_picks(bid))
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
