#!/usr/bin/env python3
"""Compose rich HTML emails and output as JSON (for piping to send_mail.py).

Usage:
    python3 scripts/compose_mail.py [options]
    python3 scripts/compose_mail.py ... | python3 scripts/send_mail.py --from-stdin

Output: JSON message object to stdout.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lib.composer import EmailComposer
from lib.models import EmailAttachment


def main() -> None:
    parser = argparse.ArgumentParser(description="Compose rich HTML emails")

    parser.add_argument("--to", action="append", default=[], help="Recipient (repeatable)")
    parser.add_argument("--cc", action="append", default=[], help="CC recipient")
    parser.add_argument("--bcc", action="append", default=[], help="BCC recipient")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--body", default="", help="Email body (HTML or plain)")
    parser.add_argument("--sender", default="", help="Sender address")
    parser.add_argument("--template", default="default",
                        choices=["default", "minimal", "digest"],
                        help="Email template")

    # Template variables
    parser.add_argument("--greeting", default="", help="Greeting line")
    parser.add_argument("--sign-off", default="", help="Sign-off line")
    parser.add_argument("--header-text", default="", help="Header text")
    parser.add_argument("--header-color", default="#2d3748", help="Header bg color")
    parser.add_argument("--footer-text", default="", help="Footer text")
    parser.add_argument("--action-url", default="", help="CTA button URL")
    parser.add_argument("--action-text", default="View Details", help="CTA button text")
    parser.add_argument("--action-color", default="#4299e1", help="CTA button color")

    # Digest-specific
    parser.add_argument("--items", default="", help="JSON array of row dicts for digest")
    parser.add_argument("--columns", default="", help="JSON array of column names")
    parser.add_argument("--summary", default="", help="Summary text for digest")

    # Reply
    parser.add_argument("--reply-to", default="", help="In-Reply-To message ID")

    # Attachments
    parser.add_argument("--attach", action="append", default=[],
                        help="File path to attach (repeatable)")

    args = parser.parse_args()

    if not args.to:
        json.dump({"error": "At least one --to recipient is required"}, sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)

    items = None
    columns = None
    if args.items:
        try:
            items = json.loads(args.items)
        except json.JSONDecodeError as exc:
            json.dump({"error": f"Invalid --items JSON: {exc}"}, sys.stderr)
            print(file=sys.stderr)
            sys.exit(1)
    if args.columns:
        try:
            columns = json.loads(args.columns)
        except json.JSONDecodeError as exc:
            json.dump({"error": f"Invalid --columns JSON: {exc}"}, sys.stderr)
            print(file=sys.stderr)
            sys.exit(1)

    composer = EmailComposer()
    message = composer.compose(
        to=args.to,
        subject=args.subject,
        body=args.body,
        template=args.template,
        sender=args.sender or None,
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
        items=items,
        columns=columns,
        summary=args.summary,
    )

    # Attach files from disk
    for filepath in args.attach:
        if not os.path.isfile(filepath):
            json.dump({"error": f"Attachment not found: {filepath}"}, sys.stderr)
            print(file=sys.stderr)
            sys.exit(1)
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

    json.dump(message.to_dict(), sys.stdout, indent=2, default=str)
    print()


if __name__ == "__main__":
    main()
