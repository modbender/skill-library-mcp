#!/usr/bin/env python3
"""
intelligence_loop.py — Post-event intelligence and periodic summaries.

Closes the loop on outcomes:
  - Detects open action items from past events, creates follow-up calendar events
  - Generates weekly/quarterly summaries with insights
  - Detects stale action items and nudges the user

Usage:
  python3 intelligence_loop.py --check-followups     # find open action items needing follow-up
  python3 intelligence_loop.py --create-followups    # create calendar events for open action items
  python3 intelligence_loop.py --summary [--days 90] # generate period summary
  python3 intelligence_loop.py --weekly-digest       # compact weekly summary for conversation open
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": f"Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def check_followups(conn) -> list:
    """Return open action items older than 3 days that haven't been scheduled yet."""
    from memory import get_open_actions
    open_items = get_open_actions(conn)
    now = datetime.now(timezone.utc)
    stale = []
    for item in open_items:
        event_date_str = item.get("event_date", "")
        if not event_date_str:
            continue
        try:
            event_date = datetime.fromisoformat(event_date_str)
            if event_date.tzinfo is None:
                event_date = event_date.replace(tzinfo=timezone.utc)
            days_old = (now - event_date).days
            if days_old >= 3:
                item["days_old"] = days_old
                stale.append(item)
        except Exception:
            pass
    return stale


def create_followup_events(stale_items: list, config: dict) -> list:
    """Create calendar events for stale action items."""
    created = []
    for item in stale_items:
        title = f"🦞 Action: {item['text'][:50]}"
        # Schedule for tomorrow at 9am user timezone
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        try:
            result = subprocess.run(
                [sys.executable, str(SKILL_DIR / "scripts/create_checkin.py"),
                 "--title", item["text"][:80],
                 "--event-datetime", tomorrow.isoformat(),
                 "--event-duration", "30",
                 "--user-calendar", config.get("default_user_calendar", "")],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                created.append({"action": item["text"], "scheduled": tomorrow.isoformat()})
        except Exception as e:
            created.append({"action": item["text"], "error": str(e)})

    return created


def weekly_digest(conn, config: dict) -> dict:
    """Compact digest for surfacing at start of Monday conversation."""
    from memory import get_summary, get_open_actions
    summary = get_summary(conn, days=7)
    open_actions = get_open_actions(conn)

    # Upcoming high-stakes events this week
    upcoming = []
    try:
        result = subprocess.run(
            [sys.executable, str(SKILL_DIR / "scripts/scan_calendar.py"), "--force"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            scan = json.loads(result.stdout)
            upcoming = [e for e in scan.get("actionable", []) if (e.get("hours_away") or 999) <= 168]
    except Exception:
        pass

    lines = []
    if summary.get("total_events", 0) > 0:
        lines.append(f"📊 Last week: {summary['total_events']} events, "
                     f"{summary.get('total_action_items_captured', 0)} action items captured")
    if open_actions:
        lines.append(f"⚠️  {len(open_actions)} open action item(s) from past events")
    if upcoming:
        top = upcoming[0]
        lines.append(f"📅 Coming up: *{top['title']}* "
                     f"({int((top.get('hours_away') or 0) / 24)} days away, score {top['score']}/10)")

    return {
        "digest": "\n".join(lines) if lines else "",
        "has_content": bool(lines),
        "open_action_count": len(open_actions),
        "upcoming_count": len(upcoming),
        "last_week_summary": summary,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-followups", action="store_true")
    parser.add_argument("--create-followups", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--weekly-digest", action="store_true")
    args = parser.parse_args()

    from memory import get_db, get_summary
    conn = get_db()
    config = load_config()

    if args.check_followups:
        stale = check_followups(conn)
        print(json.dumps({"stale_action_items": stale, "count": len(stale)}, indent=2))

    elif args.create_followups:
        stale = check_followups(conn)
        if not stale:
            print(json.dumps({"status": "nothing_to_schedule"}))
        else:
            created = create_followup_events(stale, config)
            print(json.dumps({"scheduled": created, "count": len(created)}, indent=2))

    elif args.summary:
        print(json.dumps(get_summary(conn, args.days), indent=2))

    elif args.weekly_digest:
        print(json.dumps(weekly_digest(conn, config), indent=2))

    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
