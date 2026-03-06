#!/usr/bin/env python3
"""
cal_editor.py — Natural language calendar editing.

Understands plain-English commands to move, find, clear, and summarise
calendar events without requiring exact IDs or dates.

Usage:
  python3 cal_editor.py --move "Sprint Review" "next Monday 2pm"
  python3 cal_editor.py --find-free "tomorrow" --duration 60
  python3 cal_editor.py --clear "this Friday afternoon"
  python3 cal_editor.py --read "this week"
  python3 cal_editor.py --reschedule-conflict    # auto-resolve first detected conflict
"""
from __future__ import annotations  # PEP 563 — required for Python 3.8 compat with datetime|None hints

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

DAYS_OF_WEEK = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SLOT_HOURS = {
    "morning": (8, 12),
    "afternoon": (13, 17),
    "evening": (18, 21),
    "early morning": (6, 9),
    "late afternoon": (15, 18),
    "midday": (11, 13),
    "noon": (12, 13),
    "night": (20, 23),
}


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


# ── Natural language date/time parser ─────────────────────────────────────────

def _resolve_weekday(name: str, base: datetime) -> datetime:
    """Return the next occurrence of weekday name after base (or today if same day)."""
    target = DAYS_OF_WEEK.index(name.lower())
    current = base.weekday()
    delta = (target - current) % 7
    if delta == 0:
        delta = 7  # "next monday" always means at least 1 week ahead for "next X"
    return base + timedelta(days=delta)


def parse_nl_datetime(text: str, base: datetime = None) -> datetime | None:
    """
    Parse natural language datetime expressions.
    Returns a timezone-aware datetime or None if unparseable.
    """
    if base is None:
        base = datetime.now(timezone.utc)
    text = text.strip().lower()

    # Time extractor: "at 2pm", "at 14:00", "9am", "3:30 pm"
    time_hour = None
    time_minute = 0
    time_match = re.search(
        r"\bat\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?|(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text)
    if time_match:
        if time_match.group(1):
            h = int(time_match.group(1))
            time_minute = int(time_match.group(2) or 0)
            meridiem = time_match.group(3)
        else:
            h = int(time_match.group(4))
            time_minute = int(time_match.group(5) or 0)
            meridiem = time_match.group(6)
        if meridiem == "pm" and h < 12:
            h += 12
        elif meridiem == "am" and h == 12:
            h = 0
        time_hour = h
        text = re.sub(
            r"\bat\s*\d{1,2}(?::\d{2})?\s*(?:am|pm)?|\d{1,2}(?::\d{2})?\s*(?:am|pm)\b",
            "", text).strip()

    def _apply_time(dt: datetime) -> datetime:
        h = time_hour if time_hour is not None else 9  # default 9am
        return dt.replace(hour=h, minute=time_minute, second=0, microsecond=0, tzinfo=timezone.utc)

    # Relative day keywords
    if "today" in text:
        return _apply_time(base)
    if "tomorrow" in text:
        return _apply_time(base + timedelta(days=1))
    if "yesterday" in text:
        return _apply_time(base - timedelta(days=1))
    if "day after tomorrow" in text:
        return _apply_time(base + timedelta(days=2))

    # "next <weekday>"
    next_match = re.search(r"\bnext\s+(" + "|".join(DAYS_OF_WEEK) + r")\b", text)
    if next_match:
        target_day = next_match.group(1)
        dt = _resolve_weekday(target_day, base)
        return _apply_time(dt)

    # "this <weekday>" — find nearest upcoming (today counts if after current time)
    this_match = re.search(r"\bthis\s+(" + "|".join(DAYS_OF_WEEK) + r")\b", text)
    if this_match:
        target_day = this_match.group(1)
        target_idx = DAYS_OF_WEEK.index(target_day)
        current_idx = base.weekday()
        delta = (target_idx - current_idx) % 7
        dt = base + timedelta(days=delta)
        return _apply_time(dt)

    # Plain "<weekday>" — nearest upcoming
    for day in DAYS_OF_WEEK:
        if re.search(rf"\b{day}\b", text):
            target_idx = DAYS_OF_WEEK.index(day)
            current_idx = base.weekday()
            delta = (target_idx - current_idx) % 7 or 7
            dt = base + timedelta(days=delta)
            return _apply_time(dt)

    # "in X days/hours"
    in_match = re.search(r"\bin\s+(\d+)\s+(day|hour|minute)s?\b", text)
    if in_match:
        n = int(in_match.group(1))
        unit = in_match.group(2)
        if unit == "day":
            return _apply_time(base + timedelta(days=n))
        elif unit == "hour":
            return (base + timedelta(hours=n)).replace(second=0, microsecond=0)
        elif unit == "minute":
            return (base + timedelta(minutes=n)).replace(second=0, microsecond=0)

    # ISO / YYYY-MM-DD HH:MM
    iso_match = re.search(r"(\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2})?)", text)
    if iso_match:
        try:
            raw = iso_match.group(1).replace(" ", "T")
            if "T" not in raw:
                raw += "T09:00"
            dt = datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)
            if time_hour is not None:
                dt = dt.replace(hour=time_hour, minute=time_minute)
            return dt
        except ValueError:
            pass

    return None


def parse_nl_window(text: str, base: datetime = None) -> tuple[datetime, datetime] | None:
    """
    Parse a window description like "this week", "tomorrow afternoon",
    "next Monday morning". Returns (start, end) datetimes or None.
    """
    if base is None:
        base = datetime.now(timezone.utc)
    text = text.strip().lower()

    # Named slots
    for slot_name, (sh, eh) in SLOT_HOURS.items():
        if slot_name in text:
            rest = text.replace(slot_name, "").strip()
            day_dt = parse_nl_datetime(rest or "today", base)
            if day_dt is None:
                day_dt = base
            start = day_dt.replace(hour=sh, minute=0, second=0, microsecond=0)
            end = day_dt.replace(hour=eh, minute=0, second=0, microsecond=0)
            return start, end

    # "this week"
    if "this week" in text:
        start = base.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        return start, end

    # "next week"
    if "next week" in text:
        days_until_monday = (7 - base.weekday()) % 7
        start = (base + timedelta(days=days_until_monday or 7)).replace(
            hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        return start, end

    # "today", "tomorrow", specific day
    dt = parse_nl_datetime(text, base)
    if dt:
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start, end

    return None


# ── Calendar operations ───────────────────────────────────────────────────────

def find_event_by_title(backend, title: str, days_ahead: int = 14) -> list[dict]:
    """Find events whose title matches (case-insensitive substring)."""
    from cal_backend import CalendarBackend
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)
    calendars = backend.list_user_calendars()
    matches = []
    title_lower = title.lower()
    for cal in calendars:
        try:
            events = backend.list_events(cal["id"], now, end)
            for e in events:
                if title_lower in (e.get("summary") or "").lower():
                    e["calendar_id"] = cal["id"]
                    matches.append(e)
        except Exception:
            continue
    return matches


def move_event(title: str, new_time_str: str) -> dict:
    """Move an event to a new datetime. Returns result dict."""
    from cal_backend import CalendarBackend
    backend = CalendarBackend()
    new_dt = parse_nl_datetime(new_time_str)
    if not new_dt:
        return {"status": "error", "message": f"Couldn't parse datetime: '{new_time_str}'"}

    matches = find_event_by_title(backend, title)
    if not matches:
        return {"status": "not_found", "message": f"No upcoming event found matching '{title}'"}
    if len(matches) > 1:
        return {
            "status": "ambiguous",
            "message": f"Found {len(matches)} events matching '{title}'. Please be more specific.",
            "matches": [{"title": e.get("summary"), "start": e.get("start", {}).get("dateTime", "")}
                        for e in matches[:5]],
        }

    event = matches[0]
    cal_id = event["calendar_id"]
    event_id = event["id"]

    # Compute original duration
    orig_start_str = event.get("start", {}).get("dateTime")
    orig_end_str = event.get("end", {}).get("dateTime")
    duration_minutes = 60  # default
    if orig_start_str and orig_end_str:
        try:
            os_ = datetime.fromisoformat(orig_start_str.replace("Z", "+00:00"))
            oe_ = datetime.fromisoformat(orig_end_str.replace("Z", "+00:00"))
            duration_minutes = max(15, int((oe_ - os_).total_seconds() / 60))
        except Exception:
            pass

    new_end = new_dt + timedelta(minutes=duration_minutes)
    try:
        result = backend.update_event(cal_id, event_id, {
            "start": {"dateTime": new_dt.isoformat()},
            "end": {"dateTime": new_end.isoformat()},
        })
        return {
            "status": "moved",
            "title": event.get("summary"),
            "new_start": new_dt.isoformat(),
            "new_end": new_end.isoformat(),
            "event_id": event_id,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def find_free_slots(window_str: str, duration_minutes: int = 60) -> dict:
    """Find free time slots within a window. Returns list of available blocks."""
    from cal_backend import CalendarBackend
    backend = CalendarBackend()
    base = datetime.now(timezone.utc)
    window = parse_nl_window(window_str, base)
    if not window:
        return {"status": "error", "message": f"Couldn't parse window: '{window_str}'"}

    win_start, win_end = window
    # Clamp to business hours (7am–10pm)
    calendars = backend.list_user_calendars()
    busy = []
    for cal in calendars:
        try:
            events = backend.list_events(cal["id"], win_start, win_end)
            for e in events:
                s = e.get("start", {}).get("dateTime")
                en = e.get("end", {}).get("dateTime")
                if s and en:
                    try:
                        bs = datetime.fromisoformat(s.replace("Z", "+00:00"))
                        be = datetime.fromisoformat(en.replace("Z", "+00:00"))
                        busy.append((bs, be))
                    except Exception:
                        pass
        except Exception:
            continue

    busy.sort(key=lambda x: x[0])

    # Merge overlapping busy blocks
    merged = []
    for bs, be in busy:
        if merged and bs < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], be))
        else:
            merged.append([bs, be])

    free_slots = []
    cursor = win_start
    # Clamp cursor to business start
    if cursor.hour < 7:
        cursor = cursor.replace(hour=7, minute=0, second=0, microsecond=0)

    for bs, be in merged:
        if cursor < bs:
            gap_mins = int((bs - cursor).total_seconds() / 60)
            if gap_mins >= duration_minutes:
                free_slots.append({
                    "start": cursor.isoformat(),
                    "end": (cursor + timedelta(minutes=duration_minutes)).isoformat(),
                    "gap_available_minutes": gap_mins,
                })
        cursor = max(cursor, be)
        # Respect business hours end (10pm)
        biz_end = cursor.replace(hour=22, minute=0, second=0, microsecond=0)
        if cursor >= biz_end:
            # Move to next day 7am
            next_day = (cursor + timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
            if next_day < win_end:
                cursor = next_day

    # One final gap after all busy
    if cursor < win_end:
        gap_mins = int((win_end - cursor).total_seconds() / 60)
        if gap_mins >= duration_minutes:
            free_slots.append({
                "start": cursor.isoformat(),
                "end": (cursor + timedelta(minutes=duration_minutes)).isoformat(),
                "gap_available_minutes": gap_mins,
            })

    return {
        "status": "ok",
        "window": {"start": win_start.isoformat(), "end": win_end.isoformat()},
        "duration_requested_minutes": duration_minutes,
        "free_slots": free_slots[:10],
        "total_found": len(free_slots),
    }


def clear_window(window_str: str, dry_run: bool = False) -> dict:
    """
    Cancel / delete all OpenClaw-managed events in a time window.
    Only touches events in the OpenClaw calendar (safety guard).
    """
    from cal_backend import CalendarBackend
    backend = CalendarBackend()
    config = load_config()
    openclaw_cal_id = config.get("openclaw_cal_id") or backend.get_openclaw_cal_id()

    if not openclaw_cal_id:
        return {"status": "error", "message": "OpenClaw calendar not found. Run setup.sh first."}

    window = parse_nl_window(window_str)
    if not window:
        return {"status": "error", "message": f"Couldn't parse window: '{window_str}'"}

    win_start, win_end = window
    try:
        events = backend.list_events(openclaw_cal_id, win_start, win_end)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    if not events:
        return {"status": "ok", "deleted": [], "count": 0,
                "message": "No OpenClaw events found in that window."}

    deleted = []
    skipped = []
    for e in events:
        title = e.get("summary", "Untitled")
        if dry_run:
            deleted.append({"title": title, "start": e.get("start", {}).get("dateTime", "")})
            continue
        try:
            backend.delete_event(openclaw_cal_id, e["id"])
            deleted.append({"title": title, "start": e.get("start", {}).get("dateTime", "")})
        except Exception as ex:
            skipped.append({"title": title, "error": str(ex)})

    return {
        "status": "ok" if not dry_run else "dry_run",
        "window": {"start": win_start.isoformat(), "end": win_end.isoformat()},
        "deleted": deleted,
        "skipped": skipped,
        "count": len(deleted),
    }


def read_calendar(window_str: str) -> dict:
    """Return a human-friendly summary of events in a time window."""
    from cal_backend import CalendarBackend
    backend = CalendarBackend()
    window = parse_nl_window(window_str)
    if not window:
        return {"status": "error", "message": f"Couldn't parse window: '{window_str}'"}

    win_start, win_end = window
    calendars = backend.list_user_calendars()
    all_events = []
    for cal in calendars:
        try:
            events = backend.list_events(cal["id"], win_start, win_end)
            for e in events:
                e["calendar_name"] = cal.get("summary", "")
                all_events.append(e)
        except Exception:
            continue

    all_events.sort(key=lambda e: e.get("start", {}).get("dateTime", "") or
                    e.get("start", {}).get("date", ""))

    summary_lines = []
    by_day = {}
    for e in all_events:
        s = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date", "")
        try:
            dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
            day_key = dt.strftime("%A %d %b")
            time_str = dt.strftime("%H:%M")
        except Exception:
            day_key = s[:10]
            time_str = ""
        by_day.setdefault(day_key, []).append(
            f"{time_str} — {e.get('summary', 'Untitled')}")

    for day, items in by_day.items():
        summary_lines.append(f"**{day}** ({len(items)} event{'s' if len(items) != 1 else ''})")
        for item in items:
            summary_lines.append(f"  • {item}")

    return {
        "status": "ok",
        "window": {"start": win_start.isoformat(), "end": win_end.isoformat()},
        "total_events": len(all_events),
        "summary": "\n".join(summary_lines) if summary_lines else "No events found.",
        "events": [
            {
                "title": e.get("summary", "Untitled"),
                "start": e.get("start", {}).get("dateTime") or e.get("start", {}).get("date", ""),
                "end": e.get("end", {}).get("dateTime") or e.get("end", {}).get("date", ""),
                "calendar": e.get("calendar_name", ""),
            }
            for e in all_events
        ],
    }


def reschedule_conflict() -> dict:
    """Detect the first overlap conflict and propose a move to nearest free slot."""
    import subprocess
    try:
        scan_result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts/scan_calendar.py"), "--force"],
            capture_output=True, text=True)
        conflicts_result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts/conflict_detector.py")],
            input=scan_result.stdout, capture_output=True, text=True)
        conflicts = json.loads(conflicts_result.stdout or "[]")
    except Exception as e:
        return {"status": "error", "message": str(e)}

    overlaps = [c for c in conflicts if c.get("type") == "overlap"]
    if not overlaps:
        return {"status": "ok", "message": "No overlap conflicts detected.", "conflicts": []}

    first = overlaps[0]
    event_titles = first.get("events", [])
    if len(event_titles) < 2:
        return {"status": "ok", "conflict": first,
                "message": "Conflict detected but couldn't extract event titles to auto-resolve."}

    # Find free slot for the second (less urgent) event
    free = find_free_slots("this week", duration_minutes=60)
    suggestion = None
    if free.get("free_slots"):
        suggestion = free["free_slots"][0]["start"]

    return {
        "status": "conflict_found",
        "conflict": first,
        "suggested_move": {
            "event": event_titles[-1] if event_titles else None,
            "to": suggestion,
            "note": "Confirm with user before moving.",
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--move", nargs=2, metavar=("TITLE", "NEW_TIME"))
    parser.add_argument("--find-free", metavar="WINDOW")
    parser.add_argument("--duration", type=int, default=60,
                        help="Duration in minutes for --find-free (default 60)")
    parser.add_argument("--clear", metavar="WINDOW")
    parser.add_argument("--dry-run", action="store_true",
                        help="With --clear: show what would be deleted without deleting")
    parser.add_argument("--read", metavar="WINDOW")
    parser.add_argument("--reschedule-conflict", action="store_true")
    parser.add_argument("--parse-datetime", metavar="TEXT",
                        help="Debug: parse a natural language datetime and print result")
    args = parser.parse_args()

    if args.parse_datetime:
        dt = parse_nl_datetime(args.parse_datetime)
        print(json.dumps({"input": args.parse_datetime,
                          "parsed": dt.isoformat() if dt else None}))
    elif args.move:
        print(json.dumps(move_event(args.move[0], args.move[1]), indent=2))
    elif args.find_free:
        print(json.dumps(find_free_slots(args.find_free, args.duration), indent=2))
    elif args.clear:
        print(json.dumps(clear_window(args.clear, dry_run=args.dry_run), indent=2))
    elif args.read:
        print(json.dumps(read_calendar(args.read), indent=2))
    elif args.reschedule_conflict:
        print(json.dumps(reschedule_conflict(), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
