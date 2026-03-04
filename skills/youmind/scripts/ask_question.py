#!/usr/bin/env python3
"""Backward-compatible question entrypoint implemented with API-only chat calls."""

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
    parser = argparse.ArgumentParser(description="Ask Youmind board via API")
    parser.add_argument("--question", required=True)
    parser.add_argument("--board-id")
    parser.add_argument("--board-url")
    parser.add_argument("--chat-id", help="If provided, send to existing chat; otherwise create new chat")
    parser.add_argument("--message-mode", default="agent")
    parser.add_argument("--max-mode", action="store_true")
    args = parser.parse_args()

    try:
        client = YoumindApiClient()
        bid = _resolve_board_id(client, args.board_id, args.board_url)

        if args.chat_id:
            result = client.send_message(
                chat_id=args.chat_id,
                board_id=bid,
                message=args.question,
                message_mode=args.message_mode,
                max_mode=args.max_mode,
            )
        else:
            result = client.create_chat(
                board_id=bid,
                message=args.question,
                message_mode=args.message_mode,
                max_mode=args.max_mode,
            )

        _print(result)
        return 0

    except AuthError as exc:
        print(f"❌ Auth error: {exc}")
        print("Run: python scripts/run.py auth_manager.py setup")
        return 1
    except Exception as exc:
        print(f"❌ Error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
