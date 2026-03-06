#!/usr/bin/env python3
"""Mail merge — batch personalised sends from a template + data source.

Reads a CSV or JSON data file where each row represents one recipient.
For each row, the template subject/body placeholders are filled in and
the message is sent via SMTP.

Placeholder syntax: ``{{field_name}}`` in subject and body.

Usage:
    # CSV data source
    python3 scripts/mail_merge.py \\
        --data contacts.csv \\
        --subject "Hello {{name}}" \\
        --body "<p>Dear {{name}}, your code is {{code}}.</p>" \\
        --to-field email \\
        --config config.yaml

    # JSON data source
    python3 scripts/mail_merge.py \\
        --data contacts.json \\
        --subject "Invoice #{{invoice_id}}" \\
        --body "<p>Amount: {{amount}}</p>" \\
        --to-field email \\
        --config config.yaml

    # Dry run (compose without sending)
    python3 scripts/mail_merge.py \\
        --data contacts.csv \\
        --subject "Hi {{name}}" \\
        --body "Test" \\
        --to-field email \\
        --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from lib.account_manager import AccountManager
from lib.composer import EmailComposer
from lib.defaults import resolve_config_path
from lib.models import EmailAddress


def _load_data(path: str) -> list[dict[str, str]]:
    """Load rows from a CSV or JSON file."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        raise ValueError("JSON data must be an array of objects")
    else:
        # Default: CSV
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return list(reader)


def _fill_template(template: str, row: dict[str, str]) -> str:
    """Replace ``{{key}}`` placeholders with values from *row*."""
    def replacer(match):
        key = match.group(1).strip()
        return row.get(key, match.group(0))
    return re.sub(r"\{\{(\w+)\}\}", replacer, template)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mail merge — batch personalised sends")
    parser.add_argument("--data", required=True,
                        help="CSV or JSON file with recipient data")
    parser.add_argument("--subject", required=True,
                        help="Subject template (use {{field}} for placeholders)")
    parser.add_argument("--body", required=True,
                        help="Body template (HTML, use {{field}} for placeholders)")
    parser.add_argument("--to-field", required=True,
                        help="Column/key name containing recipient email address")
    parser.add_argument("--name-field", default="",
                        help="Column/key for recipient display name (optional)")
    parser.add_argument("--template", default="default",
                        choices=["default", "minimal", "digest"],
                        help="Email template")
    parser.add_argument("--sender", default="", help="Sender address override")
    parser.add_argument("--greeting", default="", help="Greeting template")
    parser.add_argument("--sign-off", default="", help="Sign-off template")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Delay in seconds between sends (default: 0.5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compose messages without sending")
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--account", default="", help="Account profile name")
    parser.add_argument("--attach", action="append", default=[],
                        help="File to attach (same for all recipients)")
    parser.add_argument("--format", choices=["json", "cli"], default="json")
    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    # Load data
    try:
        rows = _load_data(args.data)
    except Exception as exc:
        _error(f"Failed to load data: {exc}")
        return

    if not rows:
        _error("Data file is empty")
        return

    # Validate to-field exists
    if args.to_field not in rows[0]:
        _error(f"Field '{args.to_field}' not found in data. "
               f"Available: {', '.join(rows[0].keys())}")
        return

    # Setup
    mgr = None
    acct_name = args.account
    if args.config:
        try:
            mgr = AccountManager.from_yaml(args.config)
        except Exception as exc:
            _error(f"Failed to load config: {exc}")
            return
        acct_name = acct_name or mgr.default_account

    sender = args.sender
    if not sender and mgr:
        s = mgr.get_sender(acct_name)
        if s:
            sender = str(s)

    composer = EmailComposer()

    # Load attachments once
    from lib.models import EmailAttachment
    import mimetypes
    attachments = []
    for fpath in args.attach:
        if not os.path.isfile(fpath):
            _error(f"Attachment not found: {fpath}")
            return
        ct = mimetypes.guess_type(fpath)[0] or "application/octet-stream"
        with open(fpath, "rb") as f:
            data = f.read()
        attachments.append(EmailAttachment(
            filename=os.path.basename(fpath), content_type=ct, data=data,
        ))

    results = []
    sent = 0
    failed = 0

    for i, row in enumerate(rows):
        to_addr = row.get(args.to_field, "").strip()
        if not to_addr:
            results.append({"row": i, "error": f"Empty {args.to_field}"})
            failed += 1
            continue

        subject = _fill_template(args.subject, row)
        body = _fill_template(args.body, row)
        greeting = _fill_template(args.greeting, row) if args.greeting else ""
        sign_off = _fill_template(args.sign_off, row) if args.sign_off else ""

        message = composer.compose(
            to=to_addr,
            subject=subject,
            body=body,
            template=args.template,
            sender=sender,
            greeting=greeting,
            sign_off=sign_off,
        )
        message.attachments = list(attachments)

        row_result: dict = {
            "row": i,
            "to": to_addr,
            "subject": subject,
        }

        if args.dry_run:
            row_result["status"] = "dry_run"
            results.append(row_result)
            sent += 1
        elif mgr:
            send_result = mgr.send_with_fallback(message, acct_name)
            if send_result["success"]:
                row_result["status"] = "sent"
                row_result["fallback_used"] = send_result.get("fallback_used", False)
                sent += 1
            else:
                row_result["status"] = "failed"
                row_result["error"] = send_result.get("error", "unknown")
                failed += 1
            results.append(row_result)
            if args.delay and i < len(rows) - 1:
                time.sleep(args.delay)
        else:
            row_result["status"] = "no_config"
            row_result["message"] = message.to_dict()
            results.append(row_result)
            sent += 1

    report = {
        "total": len(rows),
        "sent": sent,
        "failed": failed,
        "dry_run": args.dry_run,
        "results": results,
    }

    if args.format == "cli":
        print(f"Mail merge: {sent}/{len(rows)} sent, {failed} failed"
              + (" (dry run)" if args.dry_run else ""))
        for r in results:
            status = r.get("status", "?")
            to = r.get("to", "?")
            subj = r.get("subject", "?")
            err = r.get("error", "")
            print(f"  [{status}] {to}: {subj}" + (f" ({err})" if err else ""))
    else:
        json.dump(report, sys.stdout, indent=2)
        print()


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
