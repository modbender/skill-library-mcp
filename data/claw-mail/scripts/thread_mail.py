#!/usr/bin/env python3
"""Group emails into conversation threads by References / In-Reply-To.

Fetches messages from a folder and groups them into threads using the
Message-ID, In-Reply-To, and References headers (RFC 5256 / JWZ algorithm
simplified).

Usage:
    python3 scripts/thread_mail.py --config config.yaml
    python3 scripts/thread_mail.py --config config.yaml --account work --folder INBOX
    python3 scripts/thread_mail.py --config config.yaml --limit 200 --format cli
    python3 scripts/thread_mail.py --from-stdin < messages.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.models import EmailMessage


def build_threads(messages: list[EmailMessage]) -> list[dict]:
    """Group messages into conversation threads.

    Returns a list of thread dicts, each containing:
    - ``thread_id``: The Message-ID of the thread root
    - ``subject``: Subject of the root message
    - ``message_count``: Number of messages in the thread
    - ``participants``: Unique sender addresses
    - ``latest_date``: ISO date of the most recent message
    - ``messages``: List of message summaries in chronological order
    """
    # Index messages by Message-ID
    by_id: dict[str, EmailMessage] = {}
    for msg in messages:
        if msg.message_id:
            by_id[msg.message_id] = msg

    # Build parent map: message_id -> parent_message_id
    parent_of: dict[str, str] = {}
    children_of: dict[str, list[str]] = defaultdict(list)

    for msg in messages:
        mid = msg.message_id
        if not mid:
            continue

        parent = None
        if msg.in_reply_to and msg.in_reply_to in by_id:
            parent = msg.in_reply_to
        elif msg.references:
            # Walk references from most recent to oldest
            for ref in reversed(msg.references):
                if ref in by_id:
                    parent = ref
                    break

        if parent and parent != mid:
            parent_of[mid] = parent
            children_of[parent].append(mid)

    # Find roots (messages with no parent)
    roots = set()
    for msg in messages:
        mid = msg.message_id
        if not mid:
            continue
        # Walk up to root
        current = mid
        visited = set()
        while current in parent_of and current not in visited:
            visited.add(current)
            current = parent_of[current]
        roots.add(current)

    # Build thread for each root
    threads = []
    seen_in_thread = set()

    for root_id in roots:
        if root_id in seen_in_thread:
            continue

        # Collect all messages in this thread via BFS
        thread_ids = []
        queue = [root_id]
        while queue:
            current = queue.pop(0)
            if current in seen_in_thread:
                continue
            seen_in_thread.add(current)
            if current in by_id:
                thread_ids.append(current)
            queue.extend(children_of.get(current, []))

        if not thread_ids:
            continue

        # Sort by date
        thread_msgs = [by_id[mid] for mid in thread_ids if mid in by_id]
        thread_msgs.sort(key=lambda m: m.date or m.date.__class__(1970, 1, 1) if m.date else "", reverse=False)

        # Handle sorting with None dates
        def sort_key(m):
            if m.date:
                return m.date.isoformat()
            return ""
        thread_msgs.sort(key=sort_key)

        participants = set()
        for m in thread_msgs:
            if m.sender:
                participants.add(m.sender.address)

        latest = max(
            (m.date for m in thread_msgs if m.date),
            default=None,
        )

        root_msg = by_id.get(root_id)
        subject = root_msg.subject if root_msg else thread_msgs[0].subject if thread_msgs else ""

        threads.append({
            "thread_id": root_id,
            "subject": subject,
            "message_count": len(thread_msgs),
            "participants": sorted(participants),
            "latest_date": latest.isoformat() if latest else "",
            "messages": [
                {
                    "message_id": m.message_id,
                    "subject": m.subject,
                    "sender": str(m.sender) if m.sender else "",
                    "date": m.date.isoformat() if m.date else "",
                    "in_reply_to": m.in_reply_to,
                }
                for m in thread_msgs
            ],
        })

    # Sort threads by latest_date descending
    threads.sort(key=lambda t: t.get("latest_date", ""), reverse=True)
    return threads


def main() -> None:
    parser = argparse.ArgumentParser(description="Thread emails by conversation")
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--account", default="", help="Account profile name")
    parser.add_argument("--folder", default="INBOX", help="Folder to thread")
    parser.add_argument("--limit", type=int, default=100, help="Max messages to fetch")
    parser.add_argument("--from-stdin", action="store_true",
                        help="Read messages JSON from stdin")
    parser.add_argument("--format", choices=["json", "cli"], default="json")

    # Direct IMAP flags
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    messages: list[EmailMessage] = []

    if args.from_stdin:
        try:
            data = json.load(sys.stdin)
            raw_msgs = data if isinstance(data, list) else data.get("messages", [])
            messages = [EmailMessage.from_dict(m) for m in raw_msgs]
        except Exception as exc:
            _error(f"Failed to parse stdin: {exc}")
            return
    elif args.imap_host:
        from lib.imap_client import IMAPClient
        client = IMAPClient(
            host=args.imap_host, port=args.imap_port,
            username=args.imap_user, password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
        try:
            client.connect()
            messages = client.fetch_all(mailbox=args.folder, limit=args.limit)
        finally:
            client.disconnect()
    elif args.config:
        try:
            mgr = AccountManager.from_yaml(args.config)
        except Exception as exc:
            _error(f"Failed to load config: {exc}")
            return
        acct_name = args.account or mgr.default_account
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            messages = client.fetch_all(mailbox=args.folder, limit=args.limit)
        finally:
            client.disconnect()
    else:
        _error("Provide --config, --imap-host, or --from-stdin")
        return

    threads = build_threads(messages)

    if args.format == "cli":
        print(f"Found {len(threads)} conversation thread(s) "
              f"from {len(messages)} message(s):\n")
        for t in threads:
            count = t["message_count"]
            subj = t["subject"] or "(no subject)"
            parts = ", ".join(t["participants"][:3])
            if len(t["participants"]) > 3:
                parts += f" +{len(t['participants']) - 3} more"
            print(f"  [{count} msg] {subj}")
            print(f"         Participants: {parts}")
            print(f"         Latest: {t['latest_date']}")
            print()
    else:
        result = {
            "total_messages": len(messages),
            "thread_count": len(threads),
            "threads": threads,
        }
        json.dump(result, sys.stdout, indent=2)
        print()


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
