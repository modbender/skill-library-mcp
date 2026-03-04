#!/usr/bin/env python3
"""
confirm_delete.py — Handle user responses to deletion confirmation prompts.

When a user event disappears from the calendar for 2+ scans, the planner
creates a confirm_delete action. This script processes the user's response.

Usage:
  python3 confirm_delete.py --yes <user_event_uid>
  python3 confirm_delete.py --no <user_event_uid>
  python3 confirm_delete.py --dont-ask <user_event_uid>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def handle_yes(user_event_uid: str) -> dict:
    """User confirms deletion: cancel linked actions, mark as deleted."""
    from link_store import (
        get_db, set_deleted_confirmed, cancel_linked_actions,
        get_linked_actions
    )
    conn = get_db()

    # Cancel linked actions
    actions = get_linked_actions(conn, user_event_uid)
    cancel_linked_actions(conn, user_event_uid)
    set_deleted_confirmed(conn, user_event_uid)

    # Mark any confirm_delete actions as done
    conn.execute("""
        UPDATE action_events SET status = 'done'
        WHERE action_event_uid IN (
            SELECT action_event_uid FROM links
            WHERE user_event_uid = ?
        ) AND action_type = 'confirm_delete'
    """, (user_event_uid,))
    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "action": "deleted_confirmed",
        "user_event_uid": user_event_uid,
        "actions_canceled": len(actions),
    }


def handle_no(user_event_uid: str) -> dict:
    """User says event NOT deleted: run recovery scan, keep actions paused, cooldown."""
    from link_store import get_db
    conn = get_db()

    # Keep actions paused — don't resume them
    # Set a cooldown: don't prompt again for 24 hours
    cooldown_until = int((datetime.now(timezone.utc) + timedelta(hours=24)).timestamp())
    conn.execute("""
        INSERT OR REPLACE INTO suppression (scope, key, created_ts)
        VALUES ('cooldown', ?, ?)
    """, (user_event_uid, cooldown_until))
    conn.commit()

    # Run expanded recovery scan (wider horizon)
    recovery_result = _run_recovery_scan(user_event_uid)

    conn.close()
    return {
        "status": "ok",
        "action": "recovery_scan",
        "user_event_uid": user_event_uid,
        "cooldown_until": datetime.fromtimestamp(
            cooldown_until, tz=timezone.utc
        ).isoformat(),
        "recovery": recovery_result,
    }


def handle_dont_ask(user_event_uid: str) -> dict:
    """User says don't ask again: suppress event permanently, cancel actions."""
    from link_store import (
        get_db, suppress_event, cancel_linked_actions,
        get_linked_actions
    )
    conn = get_db()

    actions = get_linked_actions(conn, user_event_uid)
    cancel_linked_actions(conn, user_event_uid)
    suppress_event(conn, user_event_uid)

    conn.close()
    return {
        "status": "ok",
        "action": "suppressed",
        "user_event_uid": user_event_uid,
        "actions_canceled": len(actions),
        "message": "Event suppressed. Will never prompt about it again.",
    }


def _run_recovery_scan(user_event_uid: str) -> dict:
    """Run an expanded scan to try to find the event in a wider window."""
    try:
        config = load_config()
        from scan_calendar import scan_user_events
        from link_store import get_db

        conn = get_db()
        event_row = conn.execute(
            "SELECT * FROM user_events WHERE user_event_uid = ?",
            (user_event_uid,)
        ).fetchone()

        if not event_row:
            conn.close()
            return {"found": False, "detail": "Event not found in link store."}

        title = event_row["title"]

        # Scan wider horizon (180 days)
        config_expanded = dict(config)
        config_expanded["scan_days_ahead"] = 180
        events = scan_user_events(config_expanded)

        # Search for matching title
        matches = [e for e in events
                   if (e.get("summary") or "").lower() == title.lower()]

        conn.close()
        if matches:
            return {
                "found": True,
                "matches": len(matches),
                "detail": f"Found {len(matches)} event(s) matching '{title}' in expanded scan.",
            }
        else:
            return {
                "found": False,
                "detail": f"No events matching '{title}' found in 180-day window.",
            }
    except Exception as e:
        return {"found": False, "detail": f"Recovery scan failed: {e}"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--yes", metavar="USER_EVENT_UID",
                        help="Confirm event was deleted")
    parser.add_argument("--no", metavar="USER_EVENT_UID",
                        help="Event was NOT deleted — run recovery")
    parser.add_argument("--dont-ask", metavar="USER_EVENT_UID",
                        help="Suppress: never ask about this event again")
    args = parser.parse_args()

    if args.yes:
        print(json.dumps(handle_yes(args.yes), indent=2))
    elif args.no:
        print(json.dumps(handle_no(args.no), indent=2))
    elif args.dont_ask:
        print(json.dumps(handle_dont_ask(args.dont_ask), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
