#!/usr/bin/env python3
"""Generate ICS invite files from confirmed showing JSON."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4


def to_dt(value: str) -> datetime:
    # Expect ISO 8601 like 2026-02-20T14:00:00-05:00
    return datetime.fromisoformat(value)


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return cleaned or "showing"


def format_ics_time(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_ics(event: dict) -> str:
    start = to_dt(event["start_time"])
    end = to_dt(event.get("end_time")) if event.get("end_time") else start + timedelta(minutes=30)
    uid = f"{uuid4()}@show-booking"
    created = datetime.now(timezone.utc)
    summary = f"Showing: {event['address']}"
    desc = event.get("notes", "Real estate showing booked by AI calling workflow.")
    location = event["address"]

    return "\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//show-booking//EN",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{format_ics_time(created)}",
            f"DTSTART:{format_ics_time(start)}",
            f"DTEND:{format_ics_time(end)}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{desc}",
            f"LOCATION:{location}",
            "END:VEVENT",
            "END:VCALENDAR",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create ICS files from confirmed showings JSON.")
    parser.add_argument("--input", required=True, help="JSON array with confirmed showings.")
    parser.add_argument("--output-dir", required=True, help="Directory for .ics files.")
    args = parser.parse_args()

    events = json.loads(Path(args.input).read_text())
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for idx, event in enumerate(events, start=1):
        filename = f"{idx:02d}-{slug(event['address'])}.ics"
        file_path = output_dir / filename
        file_path.write_text(build_ics(event))
        print(str(file_path))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
