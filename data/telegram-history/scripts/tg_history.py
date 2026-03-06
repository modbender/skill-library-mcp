#!/usr/bin/env python3
"""Fetch Telegram chat/topic message history via MTProto (Telethon)."""

import argparse
import asyncio
import json
import os
import sys

from telethon import TelegramClient
from telethon.tl.types import Message

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SESSION_PATH = os.path.join(SKILL_DIR, "session", "user")
API_ID_PATH = os.path.join(SKILL_DIR, "api_credentials.json")


def load_credentials():
    if not os.path.exists(API_ID_PATH):
        print(f"ERROR: No credentials file at {API_ID_PATH}", file=sys.stderr)
        print("Create it with: {\"api_id\": YOUR_ID, \"api_hash\": \"YOUR_HASH\"}", file=sys.stderr)
        sys.exit(1)
    with open(API_ID_PATH) as f:
        creds = json.load(f)
    return int(creds["api_id"]), creds["api_hash"]


async def main():
    parser = argparse.ArgumentParser(description="Fetch Telegram message history")
    sub = parser.add_subparsers(dest="command")

    # login
    sub.add_parser("login", help="Interactive login (run in TTY)")

    # history
    hist = sub.add_parser("history", help="Fetch message history")
    hist.add_argument("chat_id", help="Chat ID (numeric, with - prefix for groups)")
    hist.add_argument("--topic", type=int, help="Forum topic/thread ID")
    hist.add_argument("--limit", type=int, default=50, help="Number of messages (default 50)")
    hist.add_argument("--offset-id", type=int, default=0, help="Fetch messages before this ID")
    hist.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    api_id, api_hash = load_credentials()
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    client = TelegramClient(SESSION_PATH, api_id, api_hash)

    if args.command == "login":
        await client.start()
        me = await client.get_me()
        print(f"Logged in as {me.first_name} ({me.phone})")
        await client.disconnect()
        return

    if args.command == "history":
        await client.connect()
        if not await client.is_user_authorized():
            print("ERROR: Not logged in. Run with 'login' first.", file=sys.stderr)
            sys.exit(1)

        try:
            chat_id = int(args.chat_id)
        except ValueError:
            chat_id = args.chat_id

        # For forum topics, use reply_to parameter
        kwargs = {
            "entity": chat_id,
            "limit": args.limit,
            "offset_id": args.offset_id,
        }
        if args.topic:
            kwargs["reply_to"] = args.topic

        messages = []
        async for msg in client.iter_messages(**kwargs):
            if not isinstance(msg, Message):
                continue
            entry = {
                "id": msg.id,
                "date": msg.date.isoformat(),
                "sender_id": msg.sender_id,
                "text": msg.text or "",
                "reply_to_msg_id": msg.reply_to.reply_to_msg_id if msg.reply_to else None,
            }
            # Try to get sender name
            if msg.sender:
                name = getattr(msg.sender, "first_name", "") or ""
                last = getattr(msg.sender, "last_name", "") or ""
                username = getattr(msg.sender, "username", "") or ""
                entry["sender_name"] = f"{name} {last}".strip()
                entry["sender_username"] = username
            messages.append(entry)

        messages.reverse()  # chronological order

        if args.json:
            print(json.dumps(messages, indent=2, ensure_ascii=False))
        else:
            for m in messages:
                sender = m.get("sender_name", str(m["sender_id"]))
                reply = f" [reply to {m['reply_to_msg_id']}]" if m.get("reply_to_msg_id") else ""
                print(f"[{m['date']}] {sender}{reply}: {m['text']}")

        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
