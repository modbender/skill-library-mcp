#!/usr/bin/env python3
"""Archive old emails into dated folders (default monthly).

Scans a mailbox for messages older than N days and moves them to folders like
``Archive-YYYYMM`` (or ``Archive-YYYYMMDD``/``Archive-Wxxxx``) depending on
the configurable frequency, without creating empty folders.

Usage:
    python3 scripts/archive_mail.py --config config.yaml --days 90
    python3 scripts/archive_mail.py --config config.yaml --account work --folder INBOX --days 60
    python3 scripts/archive_mail.py --config config.yaml --days 30 --archive-root "Old Mail" --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive old emails to yearly folders")
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--account", default="", help="Account profile name")
    parser.add_argument("--folder", default="INBOX", help="Source folder to scan")
    parser.add_argument("--days", type=int, required=True,
                        help="Archive messages older than N days")
    parser.add_argument("--archive-root", default="Archive",
                        help="Archive folder prefix (default: Archive)")
    parser.add_argument("--frequency", choices=["daily", "weekly", "monthly", "yearly"],
                        default="monthly",
                        help="Frequency for archive folders (default: monthly)")
    parser.add_argument("--create-folders", action="store_true", default=True,
                        help="Create archive folders if they don't exist (default)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be archived without moving")
    parser.add_argument("--limit", type=int, default=500,
                        help="Max messages to scan")
    parser.add_argument("--format", choices=["json", "cli"], default="json")

    # Direct IMAP flags
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    cutoff = datetime.now() - timedelta(days=args.days)

    # Build client
    client: IMAPClient | None = None
    acct_name = args.account

    if args.imap_host:
        client = IMAPClient(
            host=args.imap_host, port=args.imap_port,
            username=args.imap_user, password=credential_store.resolve(args.imap_pass),
            use_ssl=not args.imap_no_ssl,
        )
        acct_name = acct_name or "direct"
    elif args.config:
        try:
            mgr = AccountManager.from_yaml(args.config)
        except Exception as exc:
            _error(f"Failed to load config: {exc}")
            return
        acct_name = acct_name or mgr.default_account
        client = mgr.get_imap_client(acct_name)
    else:
        _error("Provide --config or --imap-host")
        return

    try:
        client.connect()

        # Fetch messages using BEFORE date criteria
        date_str = cutoff.strftime("%d-%b-%Y")
        messages = client.search(
            mailbox=args.folder,
            criteria=f"(BEFORE {date_str})",
            limit=args.limit,
        )

        if not messages:
            result = {
                "account": acct_name,
                "folder": args.folder,
                "cutoff_date": cutoff.isoformat(),
                "scanned": 0,
                "archived": 0,
                "dry_run": args.dry_run,
                "details": [],
            }
            _output(result, args.format)
            return

        frequency = args.frequency
        groups: dict[str, list[EmailMessage]] = {}
        for msg in messages:
            folder_name = _archive_folder_name(
                msg.date, args.archive_root, frequency,
            )
            groups.setdefault(folder_name, []).append(msg)

        created_folders: set[str] = set()
        archived = 0
        move_details: list[dict] = []
        existing_folders = {f["name"] for f in client.list_folders()}

        for folder_name, msgs in sorted(groups.items()):
            if not msgs:
                continue

            if args.dry_run:
                for msg in msgs:
                    move_details.append({
                        "message_id": msg.message_id,
                        "subject": msg.subject,
                        "date": msg.date.isoformat() if msg.date else "",
                        "target": folder_name,
                        "status": "dry_run",
                    })
                    archived += 1
                continue

            if args.create_folders and folder_name not in existing_folders:
                ok = client.create_folder(folder_name)
                if ok:
                    existing_folders.add(folder_name)
                    created_folders.add(folder_name)
                else:
                    for msg in msgs:
                        move_details.append({
                            "message_id": msg.message_id,
                            "subject": msg.subject,
                            "date": msg.date.isoformat() if msg.date else "",
                            "target": folder_name,
                            "status": "error",
                            "error": f"Failed to create folder {folder_name}",
                        })
                    continue

            msg_ids = [m.message_id for m in msgs if m.message_id]
            if not msg_ids:
                for msg in msgs:
                    move_details.append({
                        "message_id": msg.message_id,
                        "subject": msg.subject,
                        "date": msg.date.isoformat() if msg.date else "",
                        "target": folder_name,
                        "status": "failed",
                        "error": "missing Message-ID",
                    })
                continue

            results = client.move_messages_batch(msg_ids, args.folder, folder_name)
            for msg in msgs:
                mid = msg.message_id
                ok = results.get(mid, False)
                move_details.append({
                    "message_id": mid,
                    "subject": msg.subject,
                    "date": msg.date.isoformat() if msg.date else "",
                    "target": folder_name,
                    "status": "moved" if ok else "failed",
                })
                if ok:
                    archived += 1

        result = {
            "account": acct_name,
            "folder": args.folder,
            "cutoff_date": cutoff.isoformat(),
            "cutoff_days": args.days,
            "frequency": frequency,
            "scanned": len(messages),
            "archived": archived,
            "dry_run": args.dry_run,
            "created_folders": sorted(created_folders),
            "details": move_details,
        }

        _output(result, args.format)

    finally:
        client.disconnect()


def _output(result: dict, fmt: str) -> None:
    if fmt == "cli":
        dr = " (DRY RUN)" if result.get("dry_run") else ""
        freq = result.get("frequency", "monthly")
        print(f"Archive[{freq}]{dr}: {result['archived']}/{result['scanned']} "
              f"messages from {result['folder']}")
        print(f"  Cutoff: {result.get('cutoff_days', '?')} days "
              f"({result['cutoff_date'][:10]})")
        created = result.get("created_folders", [])
        if created:
            print(f"  Created: {', '.join(created)}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


def _archive_folder_name(
    date: datetime | None,
    root: str,
    frequency: str,
) -> str:
    """Return the folder name for an archive period."""
    base = root.strip() or "Archive"
    dt = date or datetime.now()
    if frequency == "daily":
        suffix = dt.strftime("%Y%m%d")
    elif frequency == "weekly":
        iso_year, iso_week, _ = dt.isocalendar()
        suffix = f"{iso_year}W{iso_week:02d}"
    elif frequency == "yearly":
        suffix = dt.strftime("%Y")
    else:
        suffix = dt.strftime("%Y%m")
    return f"{base}-{suffix}"


if __name__ == "__main__":
    main()
