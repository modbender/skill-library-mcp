#!/usr/bin/env python3
"""Read and render a specific email by Message-ID.

Usage:
    python3 scripts/read_mail.py --message-id "<id@example.com>" --config config.yaml
    python3 scripts/read_mail.py --message-id "<id@example.com>" --account work --format cli
    echo '{"message_id":"<id>", ...}' | python3 scripts/read_mail.py --from-stdin --format cli

Output: JSON message object (default) or CLI-rendered email.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient
from lib.models import EmailMessage


def main() -> None:
    parser = argparse.ArgumentParser(description="Read/render an email by Message-ID")
    parser.add_argument("--account", default="", help="Account name (default: default account)")
    parser.add_argument("--message-id", default="", help="Message-ID header value")
    parser.add_argument("--folder", default="INBOX", help="Folder to search in")
    parser.add_argument("--format", choices=["json", "cli"], default="json",
                        help="Output format (default: json)")

    # Direct IMAP options
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")

    # Attachments
    parser.add_argument("--save-attachments", default="",
                        help="Directory to save attachments to")

    # Config / stdin
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--from-stdin", action="store_true",
                        help="Read message JSON from stdin instead of IMAP")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    if args.from_stdin:
        data = json.load(sys.stdin)
        if isinstance(data, dict) and "messages" in data:
            if not data["messages"]:
                _error("No messages in input")
                return
            message = EmailMessage.from_dict(data["messages"][0])
        elif isinstance(data, dict):
            message = EmailMessage.from_dict(data)
        else:
            _error("Expected JSON message object")
            return
    elif args.imap_host:
        if not args.message_id:
            _error("--message-id is required (or use --from-stdin)")
            return
        client = IMAPClient(
            host=args.imap_host,
            port=args.imap_port,
            username=args.imap_user,
            password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
        try:
            client.connect()
            message = client.fetch_by_id(args.message_id, mailbox=args.folder)
        finally:
            client.disconnect()
        if message is None:
            _error(f"Message not found: {args.message_id}")
            return
    else:
        if not args.message_id:
            _error("--message-id is required (or use --from-stdin)")
            return
        if not args.config:
            _error("--config or --imap-host is required")
            return

        mgr = _load_manager(args.config)
        acct_name = args.account or mgr.default_account
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            message = client.fetch_by_id(args.message_id, mailbox=args.folder)
        finally:
            client.disconnect()
        if message is None:
            _error(f"Message not found: {args.message_id}")
            return

    # Save attachments if requested
    if args.save_attachments:
        _save_attachments(message, args.save_attachments)

    _output(message, args.format)


def _save_attachments(message: EmailMessage, dest_dir: str) -> None:
    """Save all attachments from a message to the given directory."""
    if not message.attachments:
        return
    os.makedirs(dest_dir, exist_ok=True)
    for att in message.attachments:
        safe_name = os.path.basename(att.filename) or "attachment"
        dest_path = os.path.join(dest_dir, safe_name)
        # Avoid overwriting: add suffix if file exists
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = f"{base}_{counter}{ext}"
            counter += 1
        with open(dest_path, "wb") as f:
            f.write(att.data)
        print(f"  Saved: {dest_path} ({att.size} bytes)", file=sys.stderr)


def _output(message: EmailMessage, fmt: str) -> None:
    if fmt == "cli":
        _render_cli(message)
    else:
        json.dump(message.to_dict(), sys.stdout, indent=2, default=str)
        print()


def _render_cli(msg: EmailMessage) -> None:
    """Render an email for terminal display."""
    w = 72
    print("=" * w)
    if msg.account:
        print(f"  Account: {msg.account}")
    print(f"  From:    {msg.sender or '(unknown)'}")
    if msg.recipients:
        print(f"  To:      {', '.join(str(r) for r in msg.recipients)}")
    if msg.cc:
        print(f"  Cc:      {', '.join(str(r) for r in msg.cc)}")
    print(f"  Subject: {msg.subject}")
    print(f"  Date:    {msg.date.strftime('%Y-%m-%d %H:%M %Z') if msg.date else '(unknown)'}")
    if msg.message_id:
        print(f"  ID:      {msg.message_id}")
    if msg.has_attachments:
        att_names = ", ".join(a.filename for a in msg.attachments)
        print(f"  Attach:  {att_names}")
    print("-" * w)

    # Prefer plain text for CLI; fall back to stripped HTML
    body = msg.body_plain
    if not body and msg.body_html:
        body = re.sub(r"<head[\s>].*?</head>", "", msg.body_html,
                       flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r"<style[\s>].*?</style>", "", body,
                       flags=re.DOTALL | re.IGNORECASE)
        body = re.sub(r"<br\s*/?>", "\n", body, flags=re.IGNORECASE)
        body = re.sub(r"</p>", "\n\n", body, flags=re.IGNORECASE)
        body = re.sub(r"<[^>]+>", "", body)
        body = re.sub(r"\n{3,}", "\n\n", body)

    if body:
        for line in body.strip().splitlines():
            print(f"  {line}")
    else:
        print("  (empty body)")

    print("=" * w)
    print()


def _load_manager(path: str) -> AccountManager:
    try:
        return AccountManager.from_yaml(path)
    except Exception as exc:
        _error(f"Failed to load config: {exc}")
        raise


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
