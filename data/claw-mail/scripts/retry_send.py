#!/usr/bin/env python3
"""Retry sending messages sitting in the IMAP Outbox folder.

The Outbox is a temporary IMAP folder that holds messages while they
are being sent.  If a send fails, the message remains in the Outbox.
This script drains the Outbox by re-attempting delivery for each
message.  After all messages are sent, the Outbox folder is removed.

Usage:
    python3 scripts/retry_send.py --config config.yaml
    python3 scripts/retry_send.py --config config.yaml --account work
    python3 scripts/retry_send.py --config config.yaml --list
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.outbox import Outbox


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retry sending messages from the IMAP Outbox",
    )
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument(
        "--account", default="",
        help="Process only this account (default: all accounts)",
    )
    parser.add_argument(
        "--list", action="store_true", dest="list_outbox",
        help="List pending messages without sending",
    )
    parser.add_argument("--format", choices=["json", "cli"], default="json")
    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    if not args.config:
        _error("--config is required (or place config.yaml in skill root)")
        return

    try:
        mgr = AccountManager.from_yaml(args.config)
    except Exception as exc:
        _error(f"Failed to load config: {exc}")
        return

    if args.account:
        account_names = [args.account]
    else:
        account_names = mgr.list_accounts()

    if args.list_outbox:
        _do_list(mgr, account_names, args.format)
    else:
        _do_drain(mgr, account_names, args.format)


def _do_list(mgr: AccountManager, accounts: list[str], fmt: str) -> None:
    """List messages currently in each account's Outbox."""
    all_pending: list[dict] = []

    for acct_name in accounts:
        try:
            imap_client = mgr.get_imap_client(acct_name)
            imap_client.connect()
            try:
                outbox = Outbox(imap_client)
                messages = outbox.list_pending()
                for msg in messages:
                    all_pending.append({
                        "account": acct_name,
                        "message_id": msg.message_id,
                        "subject": msg.subject,
                        "recipients": [str(r) for r in msg.recipients],
                        "date": msg.date.isoformat() if msg.date else "",
                    })
            finally:
                imap_client.disconnect()
        except Exception as exc:
            if fmt == "cli":
                print(f"  [{acct_name}] Error checking Outbox: {exc}")

    if fmt == "cli":
        if not all_pending:
            print("No messages pending in any Outbox.")
        else:
            print(f"  {len(all_pending)} message(s) pending in Outbox:")
            print(f"  {'':->60}")
            for p in all_pending:
                recip = ", ".join(p["recipients"][:2])
                if len(recip) > 25:
                    recip = recip[:22] + "..."
                print(
                    f"    [{p['account']}] {p['subject']!r:30s}  to={recip}"
                )
            print()
    else:
        json.dump(
            {"pending_count": len(all_pending), "messages": all_pending},
            sys.stdout, indent=2,
        )
        print()


def _do_drain(mgr: AccountManager, accounts: list[str], fmt: str) -> None:
    """Drain the Outbox for each account, sending pending messages."""
    total_attempted = 0
    total_sent = 0
    total_failed = 0
    all_errors: list[dict] = []
    account_results: list[dict] = []

    for acct_name in accounts:
        try:
            result = mgr.drain_outbox(acct_name)
            account_results.append(result)
            total_attempted += result.get("attempted", 0)
            total_sent += result.get("sent", 0)
            total_failed += result.get("failed", 0)
            all_errors.extend(result.get("errors", []))
        except Exception as exc:
            all_errors.append({
                "account": acct_name,
                "error": str(exc),
            })

    if fmt == "cli":
        if total_attempted == 0:
            print("No messages pending in any Outbox.")
        else:
            print(
                f"Outbox drain: {total_attempted} attempted, "
                f"{total_sent} sent, {total_failed} failed"
            )
            for err in all_errors:
                acct = err.get("account", "?")
                subj = err.get("subject", "")
                emsg = err.get("error", "")
                print(f"  ERROR [{acct}] {subj!r}: {emsg}")
    else:
        json.dump(
            {
                "attempted": total_attempted,
                "sent": total_sent,
                "failed": total_failed,
                "errors": all_errors,
                "accounts": account_results,
            },
            sys.stdout, indent=2,
        )
        print()

    sys.exit(1 if total_failed > 0 else 0)


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
