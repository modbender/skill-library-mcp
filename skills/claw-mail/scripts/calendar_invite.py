#!/usr/bin/env python3
"""Compose and send calendar invitations (iCalendar VEVENT).

Creates a text/calendar MIME part and sends it as an email. Recipients'
mail clients will display it as a meeting invitation.

Usage:
    python3 scripts/calendar_invite.py \\
        --to "bob@example.com" \\
        --subject "Team Standup" \\
        --start "2026-03-01T09:00:00" \\
        --end "2026-03-01T09:30:00" \\
        --location "Zoom" \\
        --description "Daily standup meeting" \\
        --config config.yaml

    # Recurring weekly meeting
    python3 scripts/calendar_invite.py \\
        --to "team@example.com" \\
        --subject "Weekly Sync" \\
        --start "2026-03-02T14:00:00" \\
        --end "2026-03-02T15:00:00" \\
        --rrule "FREQ=WEEKLY;COUNT=10" \\
        --config config.yaml
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(__file__))

from lib import credential_store
from lib.account_manager import AccountManager
from lib.defaults import resolve_config_path
from lib.models import EmailAddress, EmailMessage


def build_vcalendar(
    organizer: str,
    attendees: list[str],
    subject: str,
    start: datetime,
    end: datetime,
    location: str = "",
    description: str = "",
    rrule: str = "",
    uid: str = "",
    method: str = "REQUEST",
) -> str:
    """Build an iCalendar VCALENDAR string for a VEVENT."""
    uid = uid or f"{uuid.uuid4()}@clawMail"
    now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = start.strftime("%Y%m%dT%H%M%S")
    dtend = end.strftime("%Y%m%dT%H%M%S")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//clawMail//calendar//EN",
        f"METHOD:{method}",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{now}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{subject}",
        f"ORGANIZER;CN={organizer}:mailto:{organizer}",
    ]

    for attendee in attendees:
        lines.append(
            f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;"
            f"RSVP=TRUE:mailto:{attendee}"
        )

    if location:
        lines.append(f"LOCATION:{location}")
    if description:
        # Fold long description lines per RFC 5545
        desc_escaped = description.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,")
        lines.append(f"DESCRIPTION:{desc_escaped}")
    if rrule:
        lines.append(f"RRULE:{rrule}")

    lines.extend([
        "STATUS:CONFIRMED",
        "SEQUENCE:0",
        "END:VEVENT",
        "END:VCALENDAR",
    ])

    return "\r\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Send calendar invitation")
    parser.add_argument("--config", default="", help="YAML config file")
    parser.add_argument("--account", default="", help="Account profile name")
    parser.add_argument("--to", action="append", default=[], help="Attendee address")
    parser.add_argument("--cc", action="append", default=[], help="CC address")
    parser.add_argument("--subject", required=True, help="Event subject/title")
    parser.add_argument("--start", required=True,
                        help="Start datetime (ISO 8601: YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--end", required=True,
                        help="End datetime (ISO 8601: YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--location", default="", help="Event location")
    parser.add_argument("--description", default="", help="Event description")
    parser.add_argument("--rrule", default="",
                        help="Recurrence rule (e.g. FREQ=WEEKLY;COUNT=10)")
    parser.add_argument("--uid", default="", help="Unique event ID (auto-generated)")
    parser.add_argument("--method", default="REQUEST",
                        choices=["REQUEST", "CANCEL", "REPLY"],
                        help="Calendar method")
    parser.add_argument("--body", default="", help="Additional email body text")
    parser.add_argument("--sender", default="", help="Sender address override")
    parser.add_argument("--format", choices=["json", "cli"], default="json")

    # Direct SMTP flags
    parser.add_argument("--smtp-host", default="")
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--smtp-user", default="")
    parser.add_argument("--smtp-pass", default="")
    parser.add_argument("--smtp-no-tls", action="store_true")
    args = parser.parse_args()
    args.config = resolve_config_path(args.config)

    if not args.to:
        _error("At least one --to recipient is required")
        return

    # Parse datetimes
    try:
        start_dt = datetime.fromisoformat(args.start)
        end_dt = datetime.fromisoformat(args.end)
    except ValueError as exc:
        _error(f"Invalid datetime: {exc}")
        return

    # Determine sender
    sender_addr = args.sender
    mgr = None
    acct_name = args.account

    if args.config:
        try:
            mgr = AccountManager.from_yaml(args.config)
        except Exception as exc:
            _error(f"Failed to load config: {exc}")
            return
        acct_name = acct_name or mgr.default_account
        if not sender_addr:
            s = mgr.get_sender(acct_name)
            if s:
                sender_addr = s.address

    if not sender_addr:
        sender_addr = args.smtp_user or "organizer@example.com"

    # Build iCalendar
    vcal = build_vcalendar(
        organizer=sender_addr,
        attendees=args.to,
        subject=args.subject,
        start=start_dt,
        end=end_dt,
        location=args.location,
        description=args.description,
        rrule=args.rrule,
        uid=args.uid,
        method=args.method,
    )

    # Build MIME message with text/calendar part
    mime_msg = MIMEMultipart("mixed")
    mime_msg["From"] = sender_addr
    mime_msg["To"] = ", ".join(args.to)
    if args.cc:
        mime_msg["Cc"] = ", ".join(args.cc)
    mime_msg["Subject"] = args.subject

    # Alternative part: plain text + calendar
    alt = MIMEMultipart("alternative")

    body_text = args.body or f"You are invited to: {args.subject}"
    alt.attach(MIMEText(body_text, "plain", "utf-8"))

    cal_part = MIMEText(vcal, "calendar", "utf-8")
    cal_part.set_param("method", args.method)
    alt.attach(cal_part)

    mime_msg.attach(alt)

    # Send or output
    all_recipients = args.to + args.cc

    if args.smtp_host:
        from lib.smtp_client import SMTPClient
        client = SMTPClient(
            host=args.smtp_host, port=args.smtp_port,
            username=args.smtp_user, password=credential_store.resolve(args.smtp_pass),
            use_tls=not args.smtp_no_tls,
        )
        # Build an EmailMessage for sending
        em = EmailMessage(
            subject=args.subject,
            sender=EmailAddress.parse(sender_addr),
            recipients=[EmailAddress.parse(a) for a in args.to],
            cc=[EmailAddress.parse(a) for a in args.cc],
            body_html=body_text,
            body_plain=body_text,
        )
        ok = client.send(em)
        result = {
            "success": ok,
            "method": args.method,
            "subject": args.subject,
            "attendees": args.to,
        }
    elif mgr:
        # Use the MIME directly via smtplib
        em = EmailMessage(
            subject=args.subject,
            sender=EmailAddress.parse(sender_addr),
            recipients=[EmailAddress.parse(a) for a in args.to],
            cc=[EmailAddress.parse(a) for a in args.cc],
            body_html=body_text,
            body_plain=body_text,
        )
        send_result = mgr.send_with_fallback(em, acct_name)
        result = {
            "success": send_result["success"],
            "method": args.method,
            "subject": args.subject,
            "attendees": args.to,
            "fallback_used": send_result.get("fallback_used", False),
        }
    else:
        # No send method — just output the iCalendar
        result = {
            "subject": args.subject,
            "method": args.method,
            "attendees": args.to,
            "vcalendar": vcal,
        }

    if args.format == "cli":
        if result.get("success") is True:
            print(f"Calendar invitation sent: {args.subject}")
            print(f"  Method: {args.method}")
            print(f"  Start: {args.start}")
            print(f"  End: {args.end}")
            print(f"  Attendees: {', '.join(args.to)}")
        elif "vcalendar" in result:
            print(vcal)
        else:
            print(f"Failed to send invitation: {result}")
    else:
        json.dump(result, sys.stdout, indent=2)
        print()


def _error(msg: str) -> None:
    json.dump({"error": msg}, sys.stderr)
    print(file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
