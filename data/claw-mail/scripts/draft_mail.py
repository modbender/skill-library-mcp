#!/usr/bin/env python3
"""Save a composed email to the IMAP Drafts folder, or resume a draft.

Usage:
    # Save a new draft
    python3 scripts/compose_mail.py ... | python3 scripts/draft_mail.py --action save --config config.yaml
    python3 scripts/draft_mail.py --action save --to "user@x.com" --subject "WIP" --body "..." --config config.yaml

    # List drafts
    python3 scripts/draft_mail.py --action list --config config.yaml

    # Resume (fetch) a draft by Message-ID
    python3 scripts/draft_mail.py --action resume --message-id "<id@x.com>" --config config.yaml

    # Send a draft (fetch + send + delete from Drafts)
    python3 scripts/draft_mail.py --action send --message-id "<id@x.com>" --config config.yaml

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
from lib.smtp_client import SMTPClient, build_mime


def main() -> None:
    parser = argparse.ArgumentParser(description="Save, list, resume, or send drafts")

    parser.add_argument("--account", default="", help="Account name")
    parser.add_argument("--action", required=True,
                        choices=["save", "list", "resume", "send"],
                        help="Action to perform")
    parser.add_argument("--drafts-folder", default="Drafts",
                        help="IMAP drafts folder name (default: Drafts)")
    parser.add_argument("--message-id", default="",
                        help="Message-ID for resume/send actions")
    parser.add_argument("--limit", type=int, default=20,
                        help="Max drafts to list")
    parser.add_argument("--format", choices=["json", "cli"], default="json")

    # Compose options (for --action save without stdin)
    parser.add_argument("--to", action="append", default=[])
    parser.add_argument("--cc", action="append", default=[])
    parser.add_argument("--subject", default="")
    parser.add_argument("--body", default="")
    parser.add_argument("--sender", default="")
    parser.add_argument("--template", default="minimal",
                        choices=["default", "minimal", "digest"])

    parser.add_argument("--from-stdin", action="store_true",
                        help="Read composed message JSON from stdin")
    parser.add_argument("--config", default="", help="YAML config file")

    # Direct IMAP options
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    if args.action == "save":
        _do_save(args)
    elif args.action == "list":
        _do_list(args)
    elif args.action == "resume":
        _do_resume(args)
    elif args.action == "send":
        _do_send(args)


def _get_client(args) -> IMAPClient:
    if args.imap_host:
        return IMAPClient(
            host=args.imap_host, port=args.imap_port,
            username=args.imap_user,
            password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
    if not args.config:
        _error("Either --config or --imap-host is required.")
    mgr = _load_manager(args.config)
    acct_name = args.account or mgr.default_account
    return mgr.get_imap_client(acct_name)


def _do_save(args) -> None:
    """Save a composed message to the Drafts folder."""
    if args.from_stdin or not sys.stdin.isatty():
        try:
            data = json.load(sys.stdin)
            message = EmailMessage.from_dict(data)
        except Exception as exc:
            _error(f"Failed to parse stdin: {exc}")
            return
    elif args.to and args.subject:
        sender = args.sender
        if not sender:
            try:
                mgr = _load_manager(args.config)
                acct_name = args.account or mgr.default_account
                addr = mgr.get_sender(acct_name)
                if addr:
                    sender = str(addr)
            except Exception:
                pass
        composer = EmailComposer()
        message = composer.compose(
            to=args.to, subject=args.subject, body=args.body,
            template=args.template, sender=sender or None,
            cc=args.cc or None,
        )
    else:
        _error("Provide --to and --subject, or pipe composed JSON via stdin")
        return

    # Build MIME and append to Drafts
    mime_msg = build_mime(message)
    raw_bytes = mime_msg.as_bytes()

    client = _get_client(args)
    try:
        client.connect()
        ok = client.append_message(raw_bytes, mailbox=args.drafts_folder)
    finally:
        client.disconnect()

    result = {
        "success": ok,
        "action": "save",
        "folder": args.drafts_folder,
        "subject": message.subject,
    }
    json.dump(result, sys.stdout, indent=2)
    print()
    if not ok:
        sys.exit(1)


def _do_list(args) -> None:
    """List messages in the Drafts folder."""
    client = _get_client(args)
    try:
        client.connect()
        messages = client.fetch_all(mailbox=args.drafts_folder, limit=args.limit)
    finally:
        client.disconnect()

    if args.format == "cli":
        if not messages:
            print(f"  No drafts in {args.drafts_folder}")
            return
        print(f"  {args.drafts_folder} ({len(messages)} drafts)")
        print(f"  {'':->60}")
        for m in messages:
            to_str = ", ".join(str(r) for r in m.recipients[:2]) if m.recipients else "(no recipient)"
            if len(to_str) > 25:
                to_str = to_str[:22] + "..."
            date = m.date.strftime("%Y-%m-%d %H:%M") if m.date else ""
            subj = m.subject[:40] if m.subject else "(no subject)"
            print(f"    {date:16s}  {to_str:25s}  {subj}")
        print()
    else:
        output = {
            "folder": args.drafts_folder,
            "count": len(messages),
            "drafts": [m.to_dict() for m in messages],
        }
        json.dump(output, sys.stdout, indent=2, default=str)
        print()


def _do_resume(args) -> None:
    """Fetch a draft by Message-ID and output as JSON for editing."""
    if not args.message_id:
        _error("--message-id is required for resume")
        return

    client = _get_client(args)
    try:
        client.connect()
        message = client.fetch_by_id(args.message_id, mailbox=args.drafts_folder)
    finally:
        client.disconnect()

    if message is None:
        _error(f"Draft not found: {args.message_id}")
        return

    json.dump(message.to_dict(), sys.stdout, indent=2, default=str)
    print()


def _do_send(args) -> None:
    """Fetch a draft, send it via SMTP, and delete from Drafts."""
    if not args.message_id:
        _error("--message-id is required for send")
        return

    client = _get_client(args)
    try:
        client.connect()
        message = client.fetch_by_id(args.message_id, mailbox=args.drafts_folder)
    finally:
        client.disconnect()

    if message is None:
        _error(f"Draft not found: {args.message_id}")
        return

    # Send
    mgr = _load_manager(args.config)
    acct_name = args.account or mgr.default_account
    if not message.sender:
        addr = mgr.get_sender(acct_name)
        if addr:
            message.sender = addr

    send_result = mgr.send_with_fallback(message, acct_name)
    if not send_result["success"]:
        result = {
            "success": False,
            "action": "send",
            "error": send_result.get("error", "Send failed"),
        }
        json.dump(result, sys.stdout, indent=2)
        print()
        sys.exit(1)

    # Delete draft after successful send
    client = _get_client(args)
    try:
        client.connect()
        client.delete_message(args.message_id, mailbox=args.drafts_folder)
    finally:
        client.disconnect()

    result = {
        "success": True,
        "action": "send",
        "subject": message.subject,
        "recipients": [str(r) for r in message.recipients],
        "draft_deleted": True,
    }
    json.dump(result, sys.stdout, indent=2)
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
