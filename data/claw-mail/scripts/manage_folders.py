#!/usr/bin/env python3
"""List, create, delete, rename, and move IMAP folders.

Usage:
    python3 scripts/manage_folders.py --action list --config config.yaml
    python3 scripts/manage_folders.py --action list --account work --format cli --config config.yaml
    python3 scripts/manage_folders.py --action create --folder Projects --config config.yaml
    python3 scripts/manage_folders.py --action move --folder Projects --new-parent Archive --config config.yaml

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


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage IMAP folders")
    parser.add_argument("--account", default="", help="Account name (default: default account)")
    parser.add_argument("--action", required=True,
                        choices=["list", "create", "delete", "rename", "move"],
                        help="Action to perform")
    parser.add_argument("--folder", default="", help="Folder name (for create/delete/rename/move)")
    parser.add_argument("--new-name", default="", help="New name (for rename)")
    parser.add_argument("--new-parent", default="", help="New parent folder (for move)")
    parser.add_argument("--format", choices=["json", "cli"], default="json",
                        help="Output format (default: json)")

    # Direct IMAP options
    parser.add_argument("--imap-host", default="")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--imap-user", default="")
    parser.add_argument("--imap-pass", default="")
    parser.add_argument("--imap-no-ssl", action="store_true")
    parser.add_argument("--config", default="", help="YAML config file")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

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

    try:
        client.connect()

        if args.action == "list":
            _list_folders(client, args.format, args.account)
        elif args.action == "create":
            if not args.folder:
                _error("--folder is required for create")
            _create_folder(client, args.folder, args.format)
        elif args.action == "delete":
            if not args.folder:
                _error("--folder is required for delete")
            _delete_folder(client, args.folder, args.format)
        elif args.action == "rename":
            if not args.folder or not args.new_name:
                _error("--folder and --new-name are required for rename")
            _rename_folder(client, args.folder, args.new_name, args.format)
        elif args.action == "move":
            if not args.folder or not args.new_parent:
                _error("--folder and --new-parent are required for move")
            _move_folder(client, args.folder, args.new_parent, args.format)
    finally:
        client.disconnect()


def _list_folders(client: IMAPClient, fmt: str, account: str) -> None:
    folders = client.list_folders()
    enriched = []
    for f in folders:
        try:
            status = client.folder_status(f["name"])
            f.update(status)
        except Exception:
            f.update({"messages": 0, "unseen": 0, "recent": 0})
        enriched.append(f)

    if fmt == "cli":
        if not enriched:
            print("  No folders found")
            return
        label = f"  [{account}] " if account else "  "
        print(f"{label}{'Folder':<30s}  {'Total':>6s}  {'Unread':>6s}  {'Recent':>6s}")
        print(f"  {'':-<30s}  {'':->6s}  {'':->6s}  {'':->6s}")
        for f in enriched:
            print(f"  {f['name']:<30s}  {f.get('messages', 0):>6d}"
                  f"  {f.get('unseen', 0):>6d}  {f.get('recent', 0):>6d}")
        print()
    else:
        output = {"account": account, "folders": enriched}
        json.dump(output, sys.stdout, indent=2)
        print()


def _create_folder(client: IMAPClient, folder: str, fmt: str) -> None:
    ok = client.create_folder(folder)
    result = {"action": "create", "folder": folder, "success": ok}
    if fmt == "cli":
        status = "created" if ok else "FAILED"
        print(f"  Folder '{folder}': {status}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    if not ok:
        sys.exit(1)


def _delete_folder(client: IMAPClient, folder: str, fmt: str) -> None:
    ok = client.delete_folder(folder)
    result = {"action": "delete", "folder": folder, "success": ok}
    if fmt == "cli":
        status = "deleted" if ok else "FAILED"
        print(f"  Folder '{folder}': {status}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    if not ok:
        sys.exit(1)


def _rename_folder(client: IMAPClient, old: str, new: str, fmt: str) -> None:
    ok = client.rename_folder(old, new)
    result = {"action": "rename", "old_name": old, "new_name": new, "success": ok}
    if fmt == "cli":
        status = f"renamed to '{new}'" if ok else "FAILED"
        print(f"  Folder '{old}': {status}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    if not ok:
        sys.exit(1)


def _move_folder(client: IMAPClient, folder: str, new_parent: str, fmt: str) -> None:
    ok = client.move_folder(folder, new_parent)
    result = {"action": "move", "folder": folder, "new_parent": new_parent, "success": ok}
    if fmt == "cli":
        status = f"moved under '{new_parent}'" if ok else "FAILED"
        print(f"  Folder '{folder}': {status}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()
    if not ok:
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
