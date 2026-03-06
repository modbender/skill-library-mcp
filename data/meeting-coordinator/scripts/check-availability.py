#!/usr/bin/env python3
"""
Check calendar availability and find free time slots.

Usage:
  python3 check-availability.py --calendar shawn.vo@gmail.com --date 2026-02-19 --duration 90
  python3 check-availability.py --calendar shawn.vo@gmail.com --date 2026-02-19 --duration 60 --start-hour 10 --end-hour 17 --tz America/New_York
"""

import argparse
import subprocess
import json
from datetime import datetime, timedelta, date as date_type
from zoneinfo import ZoneInfo
import sys


def get_events(calendar_id: str, date_str: str, tz: ZoneInfo):
    """Fetch events for a date from gog calendar."""
    try:
        result = subprocess.run(
            ["gog", "calendar", "events", calendar_id,
             "--from", f"{date_str}T00:00:00",
             "--to", f"{date_str}T23:59:59"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error fetching calendar: {e}", file=sys.stderr)
        return []

    events = []
    for line in result.stdout.strip().split("\n"):
        if not line.strip() or line.startswith("ID"):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        events.append({
            "id": parts[0],
            "start": parts[1],
            "end": parts[2],
            "summary": " ".join(parts[3:]),
        })
    return events


def parse_dt(s: str, tz: ZoneInfo) -> datetime:
    """Parse an ISO datetime string into a tz-aware datetime."""
    s = s.replace("Z", "+00:00")
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


def find_free_slots(calendar_id: str, date_str: str, duration: int,
                    start_hour: int, end_hour: int, tz: ZoneInfo):
    """Return free slots of at least `duration` minutes within the work window."""
    d = date_type.fromisoformat(date_str)
    window_start = datetime(d.year, d.month, d.day, start_hour, tzinfo=tz)
    window_end = datetime(d.year, d.month, d.day, end_hour, tzinfo=tz)

    raw_events = get_events(calendar_id, date_str, tz)

    # Parse and sort busy periods
    busy = []
    for ev in raw_events:
        try:
            s = parse_dt(ev["start"], tz)
            e = parse_dt(ev["end"], tz)
            busy.append((s, e, ev["summary"], ev["id"]))
        except Exception as exc:
            print(f"Warning: skipping event {ev}: {exc}", file=sys.stderr)

    busy.sort(key=lambda x: x[0])

    # Walk the window
    cursor = window_start
    free = []
    for b_start, b_end, _, _ in busy:
        # Skip events entirely outside the window
        if b_end <= window_start or b_start >= window_end:
            continue
        gap_end = min(b_start, window_end)
        if cursor < gap_end:
            mins = (gap_end - cursor).total_seconds() / 60
            if mins >= duration:
                free.append({
                    "start": cursor.isoformat(),
                    "end": gap_end.isoformat(),
                    "duration_minutes": int(mins),
                })
        cursor = max(cursor, b_end)
        if cursor >= window_end:
            break

    # Trailing gap
    if cursor < window_end:
        mins = (window_end - cursor).total_seconds() / 60
        if mins >= duration:
            free.append({
                "start": cursor.isoformat(),
                "end": window_end.isoformat(),
                "duration_minutes": int(mins),
            })

    return {
        "date": date_str,
        "window": f"{start_hour:02d}:00–{end_hour:02d}:00",
        "timezone": str(tz),
        "events": [
            {"summary": ev["summary"], "start": ev["start"], "end": ev["end"], "id": ev["id"]}
            for ev in raw_events
        ],
        "free_slots": free,
    }


def main():
    p = argparse.ArgumentParser(description="Check calendar availability")
    p.add_argument("--calendar", required=True, help="Google Calendar ID")
    p.add_argument("--date", required=True, help="Date to check (YYYY-MM-DD)")
    p.add_argument("--duration", type=int, default=30, help="Minimum free slot in minutes")
    p.add_argument("--start-hour", type=int, default=12, help="Window start (24h)")
    p.add_argument("--end-hour", type=int, default=17, help="Window end (24h)")
    p.add_argument("--tz", default="America/New_York", help="IANA timezone")
    args = p.parse_args()

    tz = ZoneInfo(args.tz)
    result = find_free_slots(args.calendar, args.date, args.duration,
                             args.start_hour, args.end_hour, tz)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
