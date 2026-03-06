#!/usr/bin/env python3
"""Chat operations via Youmind HTTP APIs (API-only)."""

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
    parser = argparse.ArgumentParser(description="Chat with Youmind boards via API")
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create", help="Create a new chat with first message")
    p_create.add_argument("--board-id")
    p_create.add_argument("--board-url")
    p_create.add_argument("--message", required=True)
    p_create.add_argument("--message-mode", default="agent")
    p_create.add_argument("--max-mode", action="store_true")

    p_send = sub.add_parser("send", help="Send message to existing chat")
    p_send.add_argument("--board-id")
    p_send.add_argument("--board-url")
    p_send.add_argument("--chat-id", required=True)
    p_send.add_argument("--message", required=True)
    p_send.add_argument("--message-mode", default="agent")
    p_send.add_argument("--max-mode", action="store_true")

    p_history = sub.add_parser("history", help="List chat history by board")
    p_history.add_argument("--board-id")
    p_history.add_argument("--board-url")

    p_origin = sub.add_parser("detail-by-origin", help="Get chat detail by board origin")
    p_origin.add_argument("--board-id")
    p_origin.add_argument("--board-url")

    p_detail = sub.add_parser("detail", help="Get chat detail by chat id")
    p_detail.add_argument("--chat-id", required=True)

    p_mark = sub.add_parser("mark-read", help="Mark chat as read")
    p_mark.add_argument("--chat-id", required=True)

    p_img = sub.add_parser("generate-image", help="Create image via chat")
    p_img.add_argument("--board-id")
    p_img.add_argument("--board-url")
    p_img.add_argument("--prompt", required=True)

    p_slides = sub.add_parser("generate-slides", help="Create slides via chat")
    p_slides.add_argument("--board-id")
    p_slides.add_argument("--board-url")
    p_slides.add_argument("--prompt", required=True)

    args = parser.parse_args()

    try:
        client = YoumindApiClient()

        if args.command == "create":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(
                client.create_chat(
                    board_id=bid,
                    message=args.message,
                    message_mode=args.message_mode,
                    max_mode=args.max_mode,
                )
            )
            return 0

        if args.command == "send":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(
                client.send_message(
                    chat_id=args.chat_id,
                    board_id=bid,
                    message=args.message,
                    message_mode=args.message_mode,
                    max_mode=args.max_mode,
                )
            )
            return 0

        if args.command == "history":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(client.list_chat_history(bid))
            return 0

        if args.command == "detail-by-origin":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            _print(client.get_chat_detail_by_origin(bid))
            return 0

        if args.command == "detail":
            _print(client.get_chat_detail(args.chat_id))
            return 0

        if args.command == "mark-read":
            _print(client.mark_chat_as_read(args.chat_id))
            return 0

        if args.command == "generate-image":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            message = f"生成一张图片：{args.prompt}"
            _print(client.create_chat(board_id=bid, message=message, message_mode="agent", max_mode=False))
            return 0

        if args.command == "generate-slides":
            bid = _resolve_board_id(client, args.board_id, args.board_url)
            message = f"创建 Slides：{args.prompt}"
            _print(client.create_chat(board_id=bid, message=message, message_mode="agent", max_mode=False))
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
