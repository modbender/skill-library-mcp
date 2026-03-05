#!/usr/bin/env python3
"""Move emails between IMAP folders.

Usage:
    python3 scripts/move_mail.py --message-id "<id@example.com>" --from INBOX --to Archive --config config.yaml
    python3 scripts/move_mail.py --account work --from-stdin --to Projects --config config.yaml

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
from lib.defaults import resolve_config_path
from lib.imap_client import IMAPClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Move emails between IMAP folders")
    parser.add_argument("--account", default="", help="Account name (default: default account)")
    parser.add_argument("--message-id", action="append", default=[],
                        help="Message-ID to move (repeatable)")
    parser.add_argument("--from", dest="from_folder", default="INBOX",
                        help="Source folder (default: INBOX)")
    parser.add_argument("--to", dest="to_folder", required=True,
                        help="Destination folder")
    parser.add_argument("--create-folder", action="store_true",
                        help="Create destination folder if it doesn't exist")
    parser.add_argument("--format", choices=["json", "cli"], default="json",
                        help="Output format (default: json)")

    # Direct IMAP options
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    parser.add_argument("--config", default="", help="YAML config file")

    # Stdin input
    parser.add_argument("--from-stdin", action="store_true",
                        help="Read message IDs from stdin JSON")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    # Collect message IDs
    msg_ids = list(args.message_id)
    if args.from_stdin:
        data = json.load(sys.stdin)
        if isinstance(data, dict) and "messages" in data:
            for m in data["messages"]:
                mid = m.get("message_id", "")
                if mid:
                    msg_ids.append(mid)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    msg_ids.append(item)
                elif isinstance(item, dict):
                    mid = item.get("message_id", "")
                    if mid:
                        msg_ids.append(mid)

    if not msg_ids:
        _error("No message IDs provided. Use --message-id or --from-stdin.")

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
        _error("IMAP host required. Use --imap-host or --config.")
        return

    results = []
    try:
        client.connect()

        if args.create_folder:
            folders = [f["name"] for f in client.list_folders()]
            if args.to_folder not in folders:
                client.create_folder(args.to_folder)

        # Use batch move for efficiency
        batch_results = client.move_messages_batch(
            msg_ids, args.from_folder, args.to_folder,
        )
        for mid, ok in batch_results.items():
            results.append({"message_id": mid, "success": ok})
    finally:
        client.disconnect()

    moved = sum(1 for r in results if r["success"])
    failed = len(results) - moved

    if args.format == "cli":
        print(f"  Moved {moved}/{len(results)} messages"
              f" from '{args.from_folder}' to '{args.to_folder}'")
        if failed:
            for r in results:
                if not r["success"]:
                    print(f"    FAILED: {r['message_id']}")
        print()
    else:
        output = {
            "account": args.account,
            "from": args.from_folder,
            "to": args.to_folder,
            "moved": moved,
            "failed": failed,
            "results": results,
        }
        json.dump(output, sys.stdout, indent=2)
        print()

    if failed:
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
