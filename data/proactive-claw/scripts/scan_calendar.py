#!/usr/bin/env python3
"""
scan_calendar.py — Fetch upcoming events, score them, apply pattern learning.

Usage:
  python3 scan_calendar.py                          # scan (uses cache if < 30 min old)
  python3 scan_calendar.py --force                  # bypass cache
  python3 scan_calendar.py --patterns <recurring_id>
  python3 scan_calendar.py --snooze <event_id> <hours>
  python3 scan_calendar.py --dismiss <event_id>
"""

import argparse
import json
import sys

# Python version guard — must be first executable code
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
OUTCOMES_DIR = SKILL_DIR / "outcomes"
CACHE_FILE = SKILL_DIR / "last_scan.json"
SNOOZE_FILE = SKILL_DIR / "snoozed.json"

HIGH_STAKES_KEYWORDS = {
    "demo", "presentation", "interview", "workshop", "conference",
    "launch", "review", "deadline", "board", "investor", "pitch",
    "keynote", "summit", "offsite", "performance", "appraisal", "evaluation"
}
ROUTINE_KEYWORDS = {"standup", "stand-up", "sync", "check-in", "scrum", "huddle"}


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_outcomes(recurring_id=None) -> list:
    outcomes = []
    if not OUTCOMES_DIR.exists():
        return outcomes
    for f in sorted(OUTCOMES_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            if recurring_id is None or data.get("recurring_id") == recurring_id:
                outcomes.append(data)
        except Exception:
            pass
    return outcomes


def load_snoozed() -> dict:
    """Load snoozed entries, auto-purging expired (non-dismissed) ones."""
    if not SNOOZE_FILE.exists():
        return {}
    try:
        data = json.loads(SNOOZE_FILE.read_text())
    except Exception:
        return {}
    now = datetime.now(timezone.utc)
    cleaned = {}
    for event_id, entry in data.items():
        if entry.get("dismissed"):
            cleaned[event_id] = entry  # dismissed = keep forever
            continue
        until = entry.get("until")
        if until:
            try:
                until_dt = datetime.fromisoformat(until)
                if until_dt.tzinfo is None:
                    until_dt = until_dt.replace(tzinfo=timezone.utc)
                if now < until_dt:
                    cleaned[event_id] = entry  # still active snooze
                # else: expired — drop it
            except Exception:
                pass  # malformed entry — drop it
    if len(cleaned) != len(data):
        # Write back cleaned version
        try:
            SNOOZE_FILE.write_text(json.dumps(cleaned, indent=2))
        except Exception:
            pass
    return cleaned


def save_snoozed(snoozed: dict):
    SNOOZE_FILE.write_text(json.dumps(snoozed, indent=2))


def is_snoozed(event_id: str, snoozed: dict) -> bool:
    entry = snoozed.get(event_id)
    if not entry:
        return False
    if entry.get("dismissed"):
        return True
    until = entry.get("until")
    if until:
        try:
            until_dt = datetime.fromisoformat(until)
            if datetime.now(timezone.utc) < until_dt:
                return True
            # Snooze expired — remove it
        except Exception:
            pass
    return False


def get_user_timezone(config: dict) -> str:
    return config.get("timezone", "UTC")


def to_utc(dt_str: str) -> datetime:
    """Parse an ISO datetime string and return UTC-aware datetime."""
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def score_event(event: dict, config: dict, outcomes: list, openclaw_event_titles: list,
                snoozed: dict) -> dict:
    score = 0
    title = (event.get("summary") or "").lower()
    description = event.get("description") or ""
    attendees = event.get("attendees") or []
    recurring_id = event.get("recurringEventId") or event.get("recurring_id") or ""
    event_id = event.get("id", "")

    # All-day event — lower relevance
    start_raw = event["start"].get("dateTime") or event["start"].get("date", "")
    end_raw = event["end"].get("dateTime") or event["end"].get("date", "")
    is_all_day = "T" not in start_raw

    if is_all_day:
        score -= 1

    # Duration
    try:
        s = to_utc(start_raw) if not is_all_day else None
        e = to_utc(end_raw) if not is_all_day else None
        duration_min = int((e - s).total_seconds() // 60) if s and e else 0
        if duration_min > 60:
            score += 2
    except Exception:
        duration_min = 0

    # Declined events — skip entirely
    for att in attendees:
        if att.get("self") and att.get("responseStatus") == "declined":
            return None

    # High-stakes keywords
    if any(kw in title for kw in HIGH_STAKES_KEYWORDS):
        score += 1

    # Routine keywords — reduce base score
    if any(kw in title for kw in ROUTINE_KEYWORDS):
        score -= 1

    # External attendees
    user_email = config.get("user_email", "")
    user_domain = user_email.split("@")[-1] if "@" in user_email else None
    has_external = False
    if user_domain:
        for att in attendees:
            email = att.get("email", "")
            if "@" in email and email.split("@")[-1] != user_domain and not att.get("self"):
                has_external = True
                break
    if has_external:
        score += 2

    # No description/agenda
    if not description.strip():
        score += 2

    # Timing
    now = datetime.now(timezone.utc)
    hours_away = None
    try:
        if not is_all_day:
            event_start = to_utc(start_raw)
            hours_away = (event_start - now).total_seconds() / 3600
            if 0 < hours_away <= 24:
                score += 2
    except Exception:
        pass

    # Check if OpenClaw check-in already exists
    slug = title[:30]
    already_has_checkin = any(slug in (t or "").lower() for t in openclaw_event_titles)
    if already_has_checkin:
        score -= 5

    # Pattern-based adjustments
    if recurring_id and outcomes:
        recent = outcomes[-4:]
        avg_items = sum(len(o.get("action_items", [])) for o in recent) / len(recent)
        if avg_items == 0:
            score -= 3
        elif avg_items >= 3:
            score += 2

    score = max(0, min(10, score))
    event_type = classify_event(recurring_id, duration_min, attendees, has_external, outcomes)

    return {
        "id": event_id,
        "summary": event.get("summary") or "(no title)",
        "title": event.get("summary") or "(no title)",  # alias kept for compatibility
        "start": start_raw,
        "end": end_raw,
        "is_all_day": is_all_day,
        "duration_minutes": duration_min,
        "recurring_id": recurring_id,
        "has_description": bool(description.strip()),
        "attendee_count": len(attendees),
        "has_external_attendees": has_external,
        "hours_away": round(hours_away, 1) if hours_away is not None else None,
        "already_has_checkin": already_has_checkin,
        "snoozed": is_snoozed(event_id, snoozed),
        "score": score,
        "past_outcomes": len(outcomes),
        "event_type": event_type,
        "calendar": event.get("_calendar_name") or event.get("calendar", ""),
    }


def classify_event(recurring_id, duration_min, attendees, has_external, outcomes) -> str:
    is_recurring = bool(recurring_id)
    avg_items = 0
    if outcomes:
        recent = outcomes[-4:]
        avg_items = sum(len(o.get("action_items", [])) for o in recent) / len(recent)
    if is_recurring and not has_external and avg_items < 1:
        return "routine_low_stakes"
    if is_recurring and (has_external or avg_items >= 2):
        return "routine_high_stakes"
    if not is_recurring and duration_min < 60 and not has_external:
        return "one_off_standard"
    return "one_off_high_stakes"


def is_cache_valid(config: dict) -> bool:
    if not CACHE_FILE.exists():
        return False
    try:
        data = json.loads(CACHE_FILE.read_text())
        scanned_at = datetime.fromisoformat(data["scanned_at"])
        if scanned_at.tzinfo is None:
            scanned_at = scanned_at.replace(tzinfo=timezone.utc)
        age_minutes = (datetime.now(timezone.utc) - scanned_at).total_seconds() / 60
        cache_ttl = config.get("scan_cache_ttl_minutes", 30)
        return age_minutes < cache_ttl
    except Exception:
        return False


def scan_user_events(config: dict = None, backend=None, now=None, time_max=None) -> list:
    """Library function: scan user calendars and return raw event dicts.

    Excludes the action calendar (openclaw_cal_id). Respects watched_calendars
    and ignored_calendars config keys.

    Returns list of dicts, each with original provider fields plus _calendar_name.
    """
    if config is None:
        config = load_config()
    if now is None:
        now = datetime.now(timezone.utc)
    days_ahead = config.get("scan_days_ahead", 7)
    if time_max is None:
        time_max = now + timedelta(days=days_ahead)

    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    if backend is None:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()

    openclaw_cal_id = config.get("openclaw_cal_id", "")
    watched = config.get("watched_calendars", [])
    ignored = config.get("ignored_calendars", [])

    try:
        calendars = backend.list_user_calendars()
    except Exception as e:
        return []

    all_events = []
    for cal in calendars:
        cal_id = cal["id"]
        # Skip action calendar
        if cal_id == openclaw_cal_id:
            continue
        # Skip ignored
        if cal_id in ignored:
            continue
        # If watched list is non-empty, only include those
        if watched and cal_id not in watched:
            continue
        try:
            events = backend.list_events(cal_id, now, time_max)
            for event in events:
                event["_calendar_name"] = cal.get("summary", "")
                event["_calendar_id"] = cal_id
                all_events.append(event)
        except Exception:
            pass

    return all_events


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Bypass scan cache")
    parser.add_argument("--patterns", help="Get pattern data for a recurring_id")
    parser.add_argument("--snooze", nargs=2, metavar=("EVENT_ID", "HOURS"),
                        help="Snooze an event for N hours")
    parser.add_argument("--dismiss", metavar="EVENT_ID",
                        help="Permanently dismiss an event from check-in")
    args = parser.parse_args()

    config = load_config()

    # Pattern lookup
    if args.patterns:
        outcomes = load_outcomes(args.patterns)
        print(json.dumps({
            "recurring_id": args.patterns,
            "total_outcomes": len(outcomes),
            "outcomes": outcomes[-5:]
        }, indent=2))
        return

    # Snooze
    if args.snooze:
        event_id, hours = args.snooze[0], float(args.snooze[1])
        snoozed = load_snoozed()
        until = (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()
        snoozed[event_id] = {"until": until, "dismissed": False}
        save_snoozed(snoozed)
        print(json.dumps({"status": "snoozed", "event_id": event_id, "until": until}))
        return

    # Dismiss
    if args.dismiss:
        snoozed = load_snoozed()
        snoozed[args.dismiss] = {"dismissed": True}
        save_snoozed(snoozed)
        print(json.dumps({"status": "dismissed", "event_id": args.dismiss}))
        return

    # Return cache if valid
    if not args.force and is_cache_valid(config):
        print(CACHE_FILE.read_text())
        return

    # Live scan
    try:
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
    except Exception as e:
        print(json.dumps({"error": "calendar_backend_unavailable", "detail": str(e),
                          "fallback": "Check setup.sh has been run and credentials are valid."}))
        sys.exit(1)

    now = datetime.now(timezone.utc)
    days_ahead = config.get("scan_days_ahead", 7)
    time_max = now + timedelta(days=days_ahead)
    snoozed = load_snoozed()

    # Get OpenClaw events for dedup check
    openclaw_event_titles = []
    try:
        openclaw_cal_id = backend.get_openclaw_cal_id()
        openclaw_events = backend.list_events(openclaw_cal_id, now, time_max)
        openclaw_event_titles = [(e.get("summary") or "").lower() for e in openclaw_events]
    except Exception:
        pass

    # Fetch all user calendars
    try:
        calendars = backend.list_user_calendars()
    except Exception as e:
        print(json.dumps({"error": "failed_to_list_calendars", "detail": str(e)}))
        sys.exit(1)

    openclaw_cal_id_safe = config.get("openclaw_cal_id", "")
    all_events = []

    for cal in calendars:
        cal_id = cal["id"]
        if cal_id == openclaw_cal_id_safe:
            continue
        try:
            events = backend.list_events(cal_id, now, time_max)
            for event in events:
                event["_calendar_name"] = cal.get("summary", "")
                all_events.append(event)
        except Exception:
            pass  # Skip unreadable calendars silently

    # Score events
    scored = []
    for event in all_events:
        recurring_id = event.get("recurringEventId") or event.get("recurring_id") or ""
        outcomes = load_outcomes(recurring_id) if recurring_id else []
        result = score_event(event, config, outcomes, openclaw_event_titles, snoozed)
        if result is not None:
            scored.append(result)

    scored.sort(key=lambda e: (-e["score"], e["start"] or ""))

    output = {
        "scanned_at": now.isoformat(),
        "days_ahead": days_ahead,
        "timezone": get_user_timezone(config),
        "total_events": len(scored),
        "actionable": [e for e in scored if e["score"] >= config.get("calendar_threshold", 6) and not e["snoozed"]],
        "events": scored,
    }

    # Write cache
    try:
        CACHE_FILE.write_text(json.dumps(output, indent=2))
    except Exception:
        pass

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
