#!/usr/bin/env python3
"""
x-cli dm — Send and read Direct Messages.

Usage:
  python x_dm.py send <username> "message text"
  python x_dm.py inbox [--count N]
"""

import argparse

from x_utils import get_client, run


async def cmd_send(args):
    client = await get_client()
    user = await client.get_user_by_screen_name(args.username.lstrip("@"))
    await client.send_dm(user.id, args.text)
    print(f"✅ DM sent to @{user.screen_name}: {args.text[:50]}...")


async def cmd_inbox(args):
    client = await get_client()
    conversations = await client.get_dm_history()
    count = 0
    for conv in conversations:
        if count >= args.count:
            break
        if hasattr(conv, "messages") and conv.messages:
            for msg in conv.messages[:1]:
                sender = msg.sender_id if hasattr(msg, "sender_id") else "?"
                text = msg.text if hasattr(msg, "text") else str(msg)
                print(f"💬 {sender}: {text}")
                if not args.json:
                    print("─" * 40)
                count += 1


def main():
    parser = argparse.ArgumentParser(description="x-cli dm — Direct Messages")
    parser.add_argument("--json", action="store_true", help="JSON output")

    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send", help="Send a DM")
    p_send.add_argument("username", help="Recipient username")
    p_send.add_argument("text", help="Message text")

    p_inbox = sub.add_parser("inbox", help="Read DM inbox")
    p_inbox.add_argument("--count", type=int, default=10)

    args = parser.parse_args()

    if args.command == "send":
        run(cmd_send(args))
    elif args.command == "inbox":
        run(cmd_inbox(args))


if __name__ == "__main__":
    main()
