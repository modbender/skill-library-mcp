#!/usr/bin/env python3
"""Run a full email heartbeat cycle: fetch -> process -> execute actions.

Supports multiple accounts — iterates over all accounts (or a specific one)
and processes each account's mailboxes with per-account + global rules.

Usage:
    python3 scripts/heartbeat.py --config config.yaml
    python3 scripts/heartbeat.py --config config.yaml --account work
    python3 scripts/heartbeat.py --config config.yaml --state-file /tmp/email_state.json

Output: JSON cycle report to stdout.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

logger = logging.getLogger("clawMail.heartbeat")

sys.path.insert(0, os.path.dirname(__file__))

from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.models import EmailAddress, EmailMessage
from lib.imap_client import IMAPClient
from lib.smtp_client import SMTPClient
from lib.composer import EmailComposer
from lib.processor import EmailProcessor


def main() -> None:
    parser = argparse.ArgumentParser(description="Run email heartbeat cycle")
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--account", default="",
                        help="Process only this account (default: all accounts)")
    parser.add_argument("--state-file", default="",
                        help="Shared state file for multi-agent coordination")
    parser.add_argument("--format", choices=["json", "summary"], default="json")

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

    start = time.monotonic()
    now = datetime.now()
    errors: list[str] = []
    all_messages: list[EmailMessage] = []
    account_reports: list[dict] = []
    dedup_skipped = 0

    # Load previously-seen Message-IDs for deduplication
    seen_ids: set[str] = set()
    if args.state_file and os.path.exists(args.state_file):
        try:
            with open(args.state_file) as f:
                prev_state = json.load(f)
            seen_ids = set(prev_state.get("email_seen_ids", []))
        except Exception:
            pass

    # Determine which accounts to process
    if args.account:
        account_names = [args.account]
    else:
        account_names = mgr.list_accounts()

    # ── Drain Outbox for each account before fetching ──────────
    outbox_results: list[dict] = []
    for acct_name in account_names:
        try:
            drain = mgr.drain_outbox(acct_name)
            if drain.get("attempted", 0) > 0:
                outbox_results.append(drain)
                if drain.get("failed", 0) > 0:
                    for err in drain.get("errors", []):
                        errors.append(
                            f"[{acct_name}] Outbox send failed: "
                            f"{err.get('subject', '?')!r} — {err.get('error', '')}"
                        )
        except Exception as exc:
            errors.append(f"[{acct_name}] Outbox drain error: {exc}")

    # ── Fetch and process mail ───────────────────────────────────
    for acct_name in account_names:
        acct_messages: list[EmailMessage] = []
        mailboxes = mgr.get_mailboxes(acct_name)
        fetch_limit = mgr.get_fetch_limit(acct_name)

        # Fetch from each mailbox
        for mailbox in mailboxes:
            try:
                messages = _fetch(mgr, acct_name, mailbox, fetch_limit)
                acct_messages.extend(messages)
            except Exception as exc:
                errors.append(f"[{acct_name}] Fetch {mailbox}: {exc}")

        # Deduplicate: skip messages we've already processed
        if args.state_file and seen_ids:
            before = len(acct_messages)
            acct_messages = [
                m for m in acct_messages
                if m.message_id and m.message_id not in seen_ids
            ]
            dedup_skipped += before - len(acct_messages)

        # Process through per-account + global rules
        rules_config = mgr.get_rules(acct_name)
        if rules_config:
            processor = EmailProcessor.from_config(rules_config)
            results = processor.process_batch(acct_messages)
        else:
            results = []

        # Execute actions
        actions_executed = 0
        for result in results:
            try:
                actions_executed += _execute_actions(result, mgr, acct_name)
            except Exception as exc:
                errors.append(
                    f"[{acct_name}] Actions for '{result.message.subject}': {exc}"
                )

        # Record newly processed IDs
        for m in acct_messages:
            if m.message_id:
                seen_ids.add(m.message_id)

        account_reports.append({
            "account": acct_name,
            "mailboxes_checked": mailboxes,
            "messages_fetched": len(acct_messages),
            "rules_matched": sum(len(r.matched_rules) for r in results),
            "actions_executed": actions_executed,
        })
        all_messages.extend(acct_messages)

    duration = time.monotonic() - start

    # Build report
    report = {
        "timestamp": now.isoformat(),
        "accounts_processed": account_names,
        "total_messages_fetched": len(all_messages),
        "dedup_skipped": dedup_skipped,
        "outbox_drained": outbox_results,
        "duration_seconds": round(duration, 3),
        "errors": errors,
        "accounts": account_reports,
        "messages": [
            {
                "account": m.account,
                "message_id": m.message_id,
                "subject": m.subject,
                "sender": str(m.sender) if m.sender else "",
                "date": m.date.isoformat() if m.date else "",
            }
            for m in all_messages
        ],
    }

    # Write shared state
    if args.state_file:
        state = {}
        if os.path.exists(args.state_file):
            try:
                with open(args.state_file) as f:
                    state = json.load(f)
            except Exception:
                pass

        state["email_last_heartbeat"] = now.isoformat()
        state["email_unread_count"] = len(all_messages)
        state["email_accounts"] = {
            ar["account"]: {
                "fetched": ar["messages_fetched"],
                "rules_matched": ar["rules_matched"],
                "actions": ar["actions_executed"],
            }
            for ar in account_reports
        }
        state["email_messages"] = report["messages"]
        state["email_errors"] = errors

        # Persist seen Message-IDs for deduplication (cap at 10,000)
        seen_list = list(seen_ids)
        if len(seen_list) > 10000:
            seen_list = seen_list[-10000:]
        state["email_seen_ids"] = seen_list

        with open(args.state_file, "w") as f:
            json.dump(state, f, indent=2)

    if args.format == "summary":
        summary = {
            "status": "error" if errors else "ok",
            "accounts": len(account_names),
            "fetched": len(all_messages),
            "duration": f"{duration:.1f}s",
        }
        if errors:
            summary["errors"] = errors
        json.dump(summary, sys.stdout, indent=2)
    else:
        json.dump(report, sys.stdout, indent=2, default=str)

    print()
    sys.exit(1 if errors else 0)


def _fetch(
    mgr: AccountManager, acct_name: str, mailbox: str, limit: int,
) -> list[EmailMessage]:
    client = mgr.get_imap_client(acct_name)
    try:
        client.connect()
        return client.fetch_unread(mailbox=mailbox, limit=limit)
    finally:
        client.disconnect()


def _execute_actions(result, mgr: AccountManager, acct_name: str) -> int:
    count = 0
    message = result.message

    if result.should_mark_read:
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            client.mark_read(message.message_id, message.mailbox)
            count += 1
        finally:
            client.disconnect()

    if result.should_flag:
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            client.flag_message(message.message_id, message.mailbox)
            count += 1
        finally:
            client.disconnect()

    if result.move_to:
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            moved = client.move_message(
                message.message_id, message.mailbox, result.move_to,
            )
            if moved:
                count += 1
        finally:
            client.disconnect()

    if result.forward_to:
        composer = EmailComposer()
        sender = mgr.get_sender(acct_name)
        for addr in result.forward_to:
            fwd = composer.compose(
                to=addr,
                subject=f"Fwd: {message.subject}",
                body=message.body or message.body_plain,
                template="minimal",
                sender=str(sender) if sender else "",
            )
            mgr.send_with_fallback(fwd, acct_name)
            count += 1

    if result.reply_body:
        composer = EmailComposer()
        sender = mgr.get_sender(acct_name)
        reply = composer.compose_reply(
            original=message,
            body=result.reply_body,
            sender=str(sender) if sender else "",
        )
        mgr.send_with_fallback(reply, acct_name)
        count += 1

    if result.should_archive:
        archive_root = mgr.get_archive_root(acct_name)
        frequency = mgr.get_archive_frequency(acct_name)
        client = mgr.get_imap_client(acct_name)
        try:
            client.connect()
            if _archive_message(client, message, archive_root, frequency):
                count += 1
        finally:
            client.disconnect()

    return count


def _archive_message(
    client: IMAPClient,
    message: EmailMessage,
    archive_root: str,
    frequency: str,
) -> bool:
    if not message.message_id:
        logger.warning("Skipping archive: missing Message-ID for %s", message.subject)
        return False
    target_folder = _archive_folder_name(message.date, archive_root, frequency)
    existing = {f["name"] for f in client.list_folders()}
    if target_folder not in existing:
        if not client.create_folder(target_folder):
            logger.warning("Failed to create archive folder %s", target_folder)
            return False
        existing.add(target_folder)
    moved = client.move_message(message.message_id, message.mailbox, target_folder)
    if not moved:
        logger.warning(
            "Failed to archive message %s into %s", message.message_id, target_folder
        )
    return moved


def _archive_folder_name(
    date: datetime | None,
    root: str,
    frequency: str,
) -> str:
    base = root.strip() or "Archive"
    freq = frequency if frequency in {"daily", "weekly", "monthly", "yearly"} else "monthly"
    dt = date or datetime.now()
    if freq == "daily":
        suffix = dt.strftime("%Y%m%d")
    elif freq == "weekly":
        iso_year, iso_week, _ = dt.isocalendar()
        suffix = f"{iso_year}W{iso_week:02d}"
    elif freq == "yearly":
        suffix = dt.strftime("%Y")
    else:
        suffix = dt.strftime("%Y%m")
    return f"{base}-{suffix}"


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
