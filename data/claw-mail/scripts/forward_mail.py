#!/usr/bin/env python3
"""Forward an existing email to new recipients.

Usage:
    python3 scripts/forward_mail.py --message-id "<id@example.com>" --to "user@other.com" --config config.yaml
    python3 scripts/forward_mail.py --from-stdin --to "user@other.com" --config config.yaml
    python3 scripts/forward_mail.py --from-stdin --to "user@other.com" --body "FYI" --config config.yaml

Output: JSON result to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.composer import EmailComposer
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient
from lib.models import EmailMessage
from lib.smtp_client import SMTPClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Forward an email to new recipients")

    parser.add_argument("--account", default="", help="Account name")
    parser.add_argument("--message-id", default="", help="Message-ID to forward")
    parser.add_argument("--folder", default="INBOX", help="Folder to find message in")
    parser.add_argument("--to", action="append", default=[], required=True,
                        help="Forward recipient (repeatable)")
    parser.add_argument("--body", default="", help="Additional message body")
    parser.add_argument("--sender", default="", help="Sender address override")
    parser.add_argument("--include-attachments", action="store_true",
                        help="Include original attachments in the forward")

    # IMAP / SMTP options
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    parser.add_argument("--smtp-host", default="")
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--smtp-user", default="")
    parser.add_argument("--smtp-pass", default="")
    parser.add_argument("--smtp-no-tls", action="store_true")

    parser.add_argument("--from-stdin", action="store_true",
                        help="Read original message JSON from stdin")
    parser.add_argument("--config", default="", help="YAML config file")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    # Get the original message
    if args.from_stdin:
        try:
            data = json.load(sys.stdin)
            if isinstance(data, dict) and "messages" in data:
                if not data["messages"]:
                    _error("No messages in input")
                    return
                original = EmailMessage.from_dict(data["messages"][0])
            elif isinstance(data, dict):
                original = EmailMessage.from_dict(data)
            else:
                _error("Expected JSON message object")
                return
        except Exception as exc:
            _error(f"Failed to parse stdin: {exc}")
            return
    elif args.imap_host:
        if not args.message_id:
            _error("--message-id is required when using IMAP")
            return
        client = IMAPClient(
            host=args.imap_host, port=args.imap_port,
            username=args.imap_user, password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
        try:
            client.connect()
            original = client.fetch_by_id(args.message_id, mailbox=args.folder)
        finally:
            client.disconnect()
        if original is None:
            _error(f"Message not found: {args.message_id}")
            return
    elif args.config:
        if not args.message_id:
            _error("--message-id is required when using config")
            return
        mgr = _load_manager(args.config)
        acct_name = args.account or mgr.default_account
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            original = client.fetch_by_id(args.message_id, mailbox=args.folder)
        finally:
            client.disconnect()
        if original is None:
            _error(f"Message not found: {args.message_id}")
            return
    else:
        _error("--from-stdin, --imap-host, or --config is required")
        return

    # Resolve sender
    sender = args.sender
    if not sender and args.config:
        try:
            mgr = _load_manager(args.config)
            acct_name = args.account or mgr.default_account
            addr = mgr.get_sender(acct_name)
            if addr:
                sender = str(addr)
        except Exception:
            pass

    # Compose forward
    composer = EmailComposer()
    fwd_message = composer.compose_forward(
        original=original,
        to=args.to,
        body=args.body,
        sender=sender or None,
        attach_original=args.include_attachments,
    )

    # Send
    if args.smtp_host:
        smtp = SMTPClient(
            host=args.smtp_host, port=args.smtp_port,
            username=args.smtp_user, password=credential_store.resolve(args.smtp_pass),
            use_tls=not args.smtp_no_tls,
        )
        success = smtp.send(fwd_message)
        result = {
            "success": success,
            "transport": "smtp",
            "subject": fwd_message.subject,
            "recipients": [str(r) for r in fwd_message.recipients],
            "original_message_id": original.message_id,
        }
        if not success:
            result["error"] = "Failed to send forward"
    elif args.config:
        mgr = _load_manager(args.config)
        acct_name = args.account or mgr.default_account
        if not fwd_message.sender:
            addr = mgr.get_sender(acct_name)
            if addr:
                fwd_message.sender = addr
        send_result = mgr.send_with_fallback(fwd_message, acct_name)
        result = {
            "success": send_result["success"],
            "transport": "smtp",
            "account": send_result["account"],
            "fallback_used": send_result["fallback_used"],
            "subject": fwd_message.subject,
            "recipients": [str(r) for r in fwd_message.recipients],
            "original_message_id": original.message_id,
        }
        if not send_result["success"]:
            result["error"] = send_result.get("error", "Failed to send")
    else:
        # No send mechanism — output composed message for piping
        json.dump(fwd_message.to_dict(), sys.stdout, indent=2, default=str)
        print()
        return

    json.dump(result, sys.stdout, indent=2)
    print()
    if not result.get("success"):
        sys.exit(1)


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
