#!/usr/bin/env python3
"""Fetch emails from an IMAP server.

Usage:
    python3 scripts/fetch_mail.py --config config.yaml
    python3 scripts/fetch_mail.py --config config.yaml --account work
    python3 scripts/fetch_mail.py --config config.yaml --format cli
    python3 scripts/fetch_mail.py --imap-host imap.example.com --imap-user me --imap-pass secret

Output: JSON (default) or CLI table to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient
from lib.models import EmailMessage


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch emails via IMAP")
    parser.add_argument("--account", default="", help="Account name (default: default account)")
    parser.add_argument("--folder", default="INBOX", help="Folder to fetch from")
    parser.add_argument("--limit", type=int, default=0, help="Max messages (0 = use config)")
    parser.add_argument("--unread-only", action="store_true", help="Only unread messages")
    parser.add_argument("--mark-read", action="store_true", help="Mark fetched messages as read")
    parser.add_argument("--format", choices=["json", "cli"], default="json",
                        help="Output format (default: json)")

    # Direct IMAP options (bypass AccountManager)
    parser.add_argument("--imap-host", default="", help="IMAP server")
    parser.add_argument("--imap-port", type=int, default=993, help="IMAP port")
    parser.add_argument("--imap-user", default="", help="IMAP username")
    parser.add_argument("--imap-pass", default="", help="IMAP password")
    parser.add_argument("--imap-no-ssl", action="store_true", help="Disable SSL")

    # Config / stdin
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--from-stdin", action="store_true",
                        help="Read JSON messages from stdin (skip IMAP)")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    # Read from stdin if piped in
    if args.from_stdin:
        data = json.load(sys.stdin)
        if isinstance(data, dict) and "messages" in data:
            msg_dicts = data["messages"]
        elif isinstance(data, list):
            msg_dicts = data
        else:
            _error("Expected JSON array or object with 'messages' key")
            return
        messages = [EmailMessage.from_dict(d) for d in msg_dicts]
        _output(messages, args.folder, args.format, args.account)
        return

    # Direct IMAP mode (no config file)
    if args.imap_host:
        client = IMAPClient(
            host=args.imap_host,
            port=args.imap_port,
            username=args.imap_user,
            password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
        limit = args.limit or 50
        try:
            client.connect()
            if args.unread_only:
                messages = client.fetch_unread(
                    mailbox=args.folder, limit=limit, mark_seen=args.mark_read,
                )
            else:
                messages = client.fetch_all(mailbox=args.folder, limit=limit)
        finally:
            client.disconnect()
        _output(messages, args.folder, args.format, "")
        return

    # Multi-account mode via config
    if not args.config:
        _error("Either --config or --imap-host is required.")

    mgr = _load_manager(args.config)
    acct_name = args.account or mgr.default_account
    limit = args.limit or mgr.get_fetch_limit(acct_name)

    client = mgr.get_imap_client(acct_name)
    try:
        client.connect()
        if args.unread_only:
            messages = client.fetch_unread(
                mailbox=args.folder, limit=limit, mark_seen=args.mark_read,
            )
        else:
            messages = client.fetch_all(mailbox=args.folder, limit=limit)
    finally:
        client.disconnect()

    _output(messages, args.folder, args.format, acct_name)


def _output(messages: list[EmailMessage], folder: str, fmt: str, account: str) -> None:
    if fmt == "cli":
        label = f"{account}:{folder}" if account else folder
        if not messages:
            print(f"  No messages in {label}")
            return
        print(f"  {label} ({len(messages)} messages)")
        print(f"  {'':->60}")
        for m in messages:
            sender = str(m.sender) if m.sender else "(unknown)"
            if len(sender) > 25:
                sender = sender[:22] + "..."
            date = m.date.strftime("%Y-%m-%d %H:%M") if m.date else ""
            subj = m.subject[:40] if m.subject else "(no subject)"
            read = " " if m.is_read else "*"
            att = "+" if m.has_attachments else " "
            print(f"  {read}{att} {date:16s}  {sender:25s}  {subj}")
        print()
    else:
        output = {
            "account": account,
            "folder": folder,
            "count": len(messages),
            "messages": [m.to_dict() for m in messages],
        }
        json.dump(output, sys.stdout, indent=2, default=str)
        print()


def _load_manager(path: str) -> AccountManager:
    try:
        return AccountManager.from_yaml(path)
    except Exception as exc:
        _error(f"Failed to load config: {exc}")
        raise  # unreachable, _error exits


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
