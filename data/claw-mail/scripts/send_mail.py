#!/usr/bin/env python3
"""Send rich HTML emails via SMTP.

Usage:
    python3 scripts/send_mail.py --config config.yaml [options]
    python3 scripts/send_mail.py --config config.yaml --account personal [options]
    python3 scripts/compose_mail.py ... | python3 scripts/send_mail.py --from-stdin --config config.yaml

Output: JSON result to stdout.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.models import EmailAttachment, EmailMessage
from lib.smtp_client import SMTPClient
from lib.composer import EmailComposer


def main() -> None:
    parser = argparse.ArgumentParser(description="Send rich HTML emails via SMTP")

    # Account
    parser.add_argument("--account", default="", help="Account name (default: default account)")

    # Message options
    parser.add_argument("--to", action="append", default=[], help="Recipient (repeatable)")
    parser.add_argument("--cc", action="append", default=[], help="CC recipient")
    parser.add_argument("--bcc", action="append", default=[], help="BCC recipient")
    parser.add_argument("--subject", default="", help="Email subject")
    parser.add_argument("--body", default="", help="Email body (HTML or plain)")
    parser.add_argument("--sender", default="", help="Sender address")

    # Template options
    parser.add_argument("--template", default="default",
                        choices=["default", "minimal", "digest"],
                        help="Email template")
    parser.add_argument("--greeting", default="", help="Greeting line")
    parser.add_argument("--sign-off", default="", help="Sign-off line")
    parser.add_argument("--header-text", default="", help="Header text")
    parser.add_argument("--header-color", default="#2d3748", help="Header bg color")
    parser.add_argument("--footer-text", default="", help="Footer text")
    parser.add_argument("--action-url", default="", help="CTA button URL")
    parser.add_argument("--action-text", default="View Details", help="CTA button text")
    parser.add_argument("--action-color", default="#4299e1", help="CTA button color")

    # Reply threading
    parser.add_argument("--reply-to", default="", help="In-Reply-To message ID")

    # Attachments
    parser.add_argument("--attach", action="append", default=[],
                        help="File path to attach (repeatable)")

    # Direct SMTP options (bypass AccountManager)
    parser.add_argument("--smtp-host", default="", help="SMTP hostname")
    parser.add_argument("--smtp-port", type=int, default=587, help="SMTP port")
    parser.add_argument("--smtp-user", default="", help="SMTP username")
    parser.add_argument("--smtp-pass", default="", help="SMTP password")
    parser.add_argument("--smtp-no-tls", action="store_true", help="Disable SMTP TLS")

    # Pipe input
    parser.add_argument("--from-stdin", action="store_true",
                        help="Read composed message JSON from stdin")

    # Config
    parser.add_argument("--config", default="", help="YAML config file")

    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    # Build or read message
    if args.from_stdin:
        try:
            data = json.load(sys.stdin)
            message = EmailMessage.from_dict(data)
        except Exception as exc:
            _error(f"Failed to parse stdin message: {exc}")
            return
    else:
        if not args.to:
            _error("At least one --to recipient is required")
        if not args.subject:
            _error("--subject is required")

        # Resolve sender from account config if not explicit
        sender_addr = args.sender
        if not sender_addr and args.config:
            try:
                mgr = AccountManager.from_yaml(args.config)
                acct_name = args.account or mgr.default_account
                sender = mgr.get_sender(acct_name)
                if sender:
                    sender_addr = str(sender)
            except Exception:
                pass

        composer = EmailComposer()
        message = composer.compose(
            to=args.to,
            subject=args.subject,
            body=args.body or "",
            template=args.template,
            sender=sender_addr or None,
            cc=args.cc or None,
            bcc=args.bcc or None,
            reply_to=args.reply_to,
            greeting=args.greeting,
            sign_off=args.sign_off,
            header_text=args.header_text,
            header_color=args.header_color,
            footer_text=args.footer_text,
            action_url=args.action_url,
            action_text=args.action_text,
            action_color=args.action_color,
        )

    # Attach files from disk
    for filepath in args.attach:
        if not os.path.isfile(filepath):
            _error(f"Attachment not found: {filepath}")
        content_type, _ = mimetypes.guess_type(filepath)
        if not content_type:
            content_type = "application/octet-stream"
        with open(filepath, "rb") as fh:
            data = fh.read()
        message.attachments.append(EmailAttachment(
            filename=os.path.basename(filepath),
            content_type=content_type,
            data=data,
        ))

    # Direct SMTP mode
    if args.smtp_host:
        client = SMTPClient(
            host=args.smtp_host,
            port=args.smtp_port,
            username=args.smtp_user,
            password=credential_store.resolve(args.smtp_pass),
            use_tls=not args.smtp_no_tls,
        )
        success = client.send(message)
        result = {
            "success": success,
            "transport": "smtp",
            "subject": message.subject,
            "recipients": [str(r) for r in message.recipients],
        }
        if not success:
            result["error"] = "Failed to send email"
            json.dump(result, sys.stdout, indent=2)
            print()
            sys.exit(1)
        json.dump(result, sys.stdout, indent=2)
        print()
        return

    # Multi-account mode with Outbox + SMTP fallback
    if not args.config:
        _error("Either --config or --smtp-host is required.")

    mgr = _load_manager(args.config)
    acct_name = args.account or mgr.default_account

    # Set sender from account if not already set on message
    if not message.sender:
        sender = mgr.get_sender(acct_name)
        if sender:
            message.sender = sender

    # Use the Outbox pattern: stage → send → cleanup
    send_result = mgr.send_via_outbox(message, acct_name)

    result = {
        "success": send_result["success"],
        "transport": "smtp",
        "account": send_result["account"],
        "fallback_used": send_result.get("fallback_used", False),
        "staged_in_outbox": send_result.get("staged", False),
        "subject": message.subject,
        "recipients": [str(r) for r in message.recipients],
    }

    stage_error = send_result.get("stage_error")
    if stage_error:
        result["stage_error"] = stage_error
        if "error" not in result or not result["error"]:
            result["error"] = stage_error

    if not send_result["success"]:
        result["error"] = send_result.get("error", "Failed to send email")
        if send_result.get("staged"):
            result["note"] = "Message is staged in Outbox for retry"
        json.dump(result, sys.stdout, indent=2)
        print()
        sys.exit(1)

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
