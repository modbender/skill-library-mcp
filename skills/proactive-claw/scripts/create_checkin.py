#!/usr/bin/env python3
"""
create_checkin.py — Create pre and post check-in events in the OpenClaw calendar.

Usage:
  python3 create_checkin.py \
    --title "Investor Demo" \
    --event-datetime "2025-03-15T14:00:00+01:00" \
    --event-duration 60 \
    --user-calendar "Work"
"""

import argparse
import json
import sys

# Python version guard
if sys.version_info < (3, 8):
    print(json.dumps({
        "error": "python_version_too_old",
        "detail": f"Python 3.8+ required. You have {sys.version}.",
        "fix": "Install Python 3.8+: https://www.python.org/downloads/"
    }))
    sys.exit(1)

from datetime import datetime, timedelta, timezone
from pathlib import Path

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def parse_offset(offset_str: str) -> timedelta:
    parts = offset_str.strip().lower().split()
    value = int(parts[0])
    unit = parts[1] if len(parts) > 1 else "hours"
    if "day" in unit:
        return timedelta(days=value)
    if "hour" in unit:
        return timedelta(hours=value)
    if "minute" in unit:
        return timedelta(minutes=value)
    return timedelta(hours=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--event-datetime", required=True,
                        help="ISO 8601 datetime, include timezone offset e.g. 2025-03-15T14:00:00+01:00")
    parser.add_argument("--event-duration", type=int, default=60)
    parser.add_argument("--user-calendar", default="")
    args = parser.parse_args()

    config = load_config()
    tz_str = config.get("timezone", "UTC")

    # Parse event start — preserve original timezone
    try:
        event_start = datetime.fromisoformat(args.event_datetime)
    except ValueError:
        print(json.dumps({"error": f"Invalid datetime format: {args.event_datetime}. Use ISO 8601."}))
        sys.exit(1)

    if event_start.tzinfo is None:
        # Assume user's configured timezone
        import zoneinfo
        try:
            tz = zoneinfo.ZoneInfo(tz_str)
            event_start = event_start.replace(tzinfo=tz)
        except Exception:
            event_start = event_start.replace(tzinfo=timezone.utc)

    event_end = event_start + timedelta(minutes=args.event_duration)

    # Determine pre check-in offset
    now = datetime.now(timezone.utc)
    same_day = event_start.astimezone(timezone.utc).date() == now.date()
    if same_day:
        pre_offset = parse_offset(config.get("pre_checkin_offset_same_day", "1 hour"))
    else:
        pre_offset = parse_offset(config.get("pre_checkin_offset_default", "1 day"))

    post_offset = parse_offset(config.get("post_checkin_offset", "30 minutes"))
    pre_start = event_start - pre_offset
    post_start = event_end + post_offset

    # Guard: don't create pre check-in in the past
    if pre_start.astimezone(timezone.utc) <= now:
        pre_start = now + timedelta(minutes=5)

    # Load backend
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
    except Exception as e:
        print(json.dumps({"error": "calendar_backend_unavailable", "detail": str(e)}))
        sys.exit(1)

    try:
        openclaw_cal_id = backend.get_openclaw_cal_id()
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    # Create pre check-in
    pre_title = f"🦞 Prep: {args.title}"
    pre_desc = (
        f"Prep check-in for: {args.title}\n\n"
        f"Suggested prompts:\n"
        f"• Do you need help preparing? Slides, talking points, research, practice run?\n"
        f"• What's the most important outcome you want from this?\n"
        f"• Any open questions or concerns to address beforehand?\n"
        f"• Who are the key people attending and what do they care about?"
    )

    # Create post check-in
    post_title = f"🦞 Follow-up: {args.title}"
    post_desc = (
        f"Follow-up check-in for: {args.title}\n\n"
        f"Suggested prompts:\n"
        f"• How did it go? What worked, what didn't?\n"
        f"• Any action items to capture?\n"
        f"• Notes or decisions to record?\n"
        f"• Anything to improve for next time?\n"
        f"• Any follow-up emails or messages to send?"
    )

    try:
        pre_event = backend.create_event(
            openclaw_cal_id, pre_title, pre_start,
            pre_start + timedelta(minutes=15), pre_desc
        )
        post_event = backend.create_event(
            openclaw_cal_id, post_title, post_start,
            post_start + timedelta(minutes=15), post_desc
        )
    except Exception as e:
        print(json.dumps({"error": "failed_to_create_events", "detail": str(e)}))
        sys.exit(1)

    # Friendly local time display (%-d removes leading zero on Linux/macOS)
    def fmt(dt):
        try:
            return dt.strftime("%A %b %-d at %-I:%M %p %Z")
        except ValueError:
            # Fallback for platforms that don't support %-d / %-I (e.g. some Windows builds)
            return dt.strftime("%A %b %d at %I:%M %p %Z").replace(" 0", " ")

    result = {
        "status": "created",
        "event_title": args.title,
        "pre_checkin": {
            "title": pre_title,
            "start": pre_start.isoformat(),
            "start_friendly": fmt(pre_start),
            "calendar": "OpenClaw",
            "event_id": pre_event.get("id"),
        },
        "post_checkin": {
            "title": post_title,
            "start": post_start.isoformat(),
            "start_friendly": fmt(post_start),
            "calendar": "OpenClaw",
            "event_id": post_event.get("id"),
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
