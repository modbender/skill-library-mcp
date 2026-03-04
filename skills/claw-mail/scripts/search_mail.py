#!/usr/bin/env python3
"""Search emails on an IMAP server using flexible criteria.

Usage:
    python3 scripts/search_mail.py --config config.yaml --subject "invoice"
    python3 scripts/search_mail.py --config config.yaml --from "boss@company.com" --unseen
    python3 scripts/search_mail.py --config config.yaml --since 2025-01-01 --before 2025-06-01
    python3 scripts/search_mail.py --config config.yaml --criteria '(OR (FROM "a") (FROM "b"))'

Output: JSON (default) or CLI table to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient
from lib.models import EmailMessage


def _build_criteria(args) -> str:
    """Build an IMAP SEARCH criteria string from CLI flags."""
    if args.criteria:
        return args.criteria

    parts: list[str] = []

    if args.unseen:
        parts.append("UNSEEN")
    if args.flagged:
        parts.append("FLAGGED")
    if args.subject:
        parts.append(f'SUBJECT "{args.subject}"')
    if getattr(args, "from_addr", None):
        parts.append(f'FROM "{args.from_addr}"')
    if args.to:
        parts.append(f'TO "{args.to}"')
    if args.body:
        parts.append(f'BODY "{args.body}"')
    if args.since:
        try:
            dt = datetime.strptime(args.since, "%Y-%m-%d")
            parts.append(f'SINCE {dt.strftime("%d-%b-%Y")}')
        except ValueError:
            parts.append(f'SINCE {args.since}')
    if args.before:
        try:
            dt = datetime.strptime(args.before, "%Y-%m-%d")
            parts.append(f'BEFORE {dt.strftime("%d-%b-%Y")}')
        except ValueError:
            parts.append(f'BEFORE {args.before}')
    if args.text:
        parts.append(f'TEXT "{args.text}"')

    if not parts:
        parts.append("ALL")

    return "(" + " ".join(parts) + ")" if len(parts) > 1 else parts[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search emails via IMAP SEARCH")

    parser.add_argument("--account", default="", help="Account name")
    parser.add_argument("--folder", default="INBOX", help="Folder to search")
    parser.add_argument("--limit", type=int, default=50, help="Max results")
    parser.add_argument("--format", choices=["json", "cli"], default="json")

    # Search criteria flags
    parser.add_argument("--subject", default="", help="Search in subject")
    parser.add_argument("--from", dest="from_addr", default="", help="Search by sender")
    parser.add_argument("--to", default="", help="Search by recipient")
    parser.add_argument("--body", default="", help="Search in body text")
    parser.add_argument("--text", default="", help="Full-text search (subject + body)")
    parser.add_argument("--since", default="", help="Messages since date (YYYY-MM-DD)")
    parser.add_argument("--before", default="", help="Messages before date (YYYY-MM-DD)")
    parser.add_argument("--unseen", action="store_true", help="Unread messages only")
    parser.add_argument("--flagged", action="store_true", help="Flagged messages only")
    parser.add_argument("--criteria", default="",
                        help="Raw IMAP SEARCH criteria (overrides other flags)")

    # IMAP options
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    parser.add_argument("--config", default="", help="YAML config file")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    criteria = _build_criteria(args)

    # Build client
    if args.imap_host:
        client = IMAPClient(
            host=args.imap_host,
            port=args.imap_port,
            username=args.imap_user,
            password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
    elif args.config:
        mgr = _load_manager(args.config)
        acct_name = args.account or mgr.default_account
        client = mgr.get_imap_client(acct_name)
    else:
        _error("Either --config or --imap-host is required.")
        return

    try:
        client.connect()
        messages = client.search(
            mailbox=args.folder, criteria=criteria, limit=args.limit,
        )
    finally:
        client.disconnect()

    _output(messages, args.folder, args.format, args.account, criteria)


def _output(
    messages: list[EmailMessage], folder: str, fmt: str,
    account: str, criteria: str,
) -> None:
    if fmt == "cli":
        label = f"{account}:{folder}" if account else folder
        print(f"  Search: {criteria}")
        if not messages:
            print(f"  No results in {label}")
            return
        print(f"  {label} ({len(messages)} results)")
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
            "criteria": criteria,
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
        raise


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
