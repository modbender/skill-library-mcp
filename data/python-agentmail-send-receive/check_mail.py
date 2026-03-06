#!/usr/bin/env python3
"""Batch-download unread emails from REPLACE_WITH_IDENTITY@agentmail.to as structured JSON files."""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone

from dotenv import load_dotenv
from agentmail import AgentMail

INBOX_ID = "REPLACE_WITH_IDENTITY@agentmail.to"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def to_filename_ts(ts):
    """Convert a datetime (or ISO-8601 string) to YYYYMMDDTHHmmss for filenames."""
    if isinstance(ts, str):
        ts = datetime.fromisoformat(ts)
    return ts.strftime("%Y%m%dT%H%M%S")


def message_to_dict(msg):
    """Extract relevant fields from a Message object into a plain dict."""
    return {
        "message_id": msg.message_id,
        "thread_id": msg.thread_id,
        "timestamp": msg.timestamp,
        "from": msg.from_,
        "to": list(msg.to) if msg.to else [],
        "cc": list(msg.cc) if msg.cc else None,
        "subject": msg.subject,
        "text": msg.text,
        "html": msg.html,
        "labels": list(msg.labels) if msg.labels else [],
        "in_reply_to": msg.in_reply_to,
        "attachments": list(msg.attachments) if msg.attachments else [],
    }


def write_atomic(filepath, data):
    """Write JSON data to filepath atomically via temp file + rename."""
    fd, tmp_path = tempfile.mkstemp(dir=SCRIPT_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
            f.write("\n")
        os.rename(tmp_path, filepath)
    except BaseException:
        os.unlink(tmp_path)
        raise


def fetch_all_unread(client):
    """Paginate through all unread messages, oldest first."""
    messages = []
    page_token = None
    while True:
        resp = client.inboxes.messages.list(
            INBOX_ID,
            labels=["unread"],
            ascending=True,
            limit=50,
            page_token=page_token,
        )
        messages.extend(resp.messages)
        if not resp.next_page_token:
            break
        page_token = resp.next_page_token
    return messages


def main():
    load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

    api_key = os.getenv("AGENTMAIL_API_KEY")
    if not api_key:
        print("Error: AGENTMAIL_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = AgentMail(api_key=api_key)

    try:
        unread = fetch_all_unread(client)
    except Exception as e:
        print(f"Error listing messages: {e}", file=sys.stderr)
        sys.exit(2)

    if not unread:
        print("No new mail.")
        sys.exit(0)

    saved = 0
    errors = 0

    for seq, item in enumerate(unread):
        mid = item.message_id
        try:
            msg = client.inboxes.messages.get(INBOX_ID, mid)

            data = message_to_dict(msg)
            ts = to_filename_ts(msg.timestamp)
            filename = f"MAIL.{ts}.{seq:03d}"
            filepath = os.path.join(SCRIPT_DIR, filename)

            write_atomic(filepath, data)

            client.inboxes.messages.update(
                INBOX_ID, mid,
                add_labels=["read"],
                remove_labels=["unread"],
            )

            subj = msg.subject or "(no subject)"
            print(f"  [{seq:03d}] {filename}  from={msg.from_}  subject={subj}")
            saved += 1

        except Exception as e:
            print(f"  [{seq:03d}] ERROR {mid}: {e}", file=sys.stderr)
            errors += 1

    print(f"\nDone: {saved} saved, {errors} errors, {len(unread)} total.")

    if saved == 0 and errors > 0:
        sys.exit(3)


if __name__ == "__main__":
    main()
