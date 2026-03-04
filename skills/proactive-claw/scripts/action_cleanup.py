#!/usr/bin/env python3
"""
action_cleanup.py — Soft-cancel policy and cleanup for the Action Calendar.

Since users may hide the action calendar:
  - Canceled actions: rename to "🦞 [Canceled] ..."
  - Paused actions: rename to "🦞 [Paused] ..."
  - Cleanup: delete canceled entries older than action_cleanup_days (default 30)

Run by daemon once daily.

Usage:
  python3 action_cleanup.py --cleanup              # run cleanup cycle
  python3 action_cleanup.py --cleanup --dry-run    # show what would be cleaned
  python3 action_cleanup.py --status               # show cleanup stats
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


def cleanup(config: dict = None, dry_run: bool = False) -> dict:
    """Run cleanup cycle: rename paused/canceled events, delete old canceled."""
    if config is None:
        config = load_config()

    from link_store import get_db
    from action_codec import decode_action_description, update_status_in_description

    conn = get_db()
    cleanup_days = config.get("action_cleanup_days", 30)
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=cleanup_days)).timestamp())

    results = {
        "renamed_paused": 0,
        "renamed_canceled": 0,
        "deleted_old": 0,
        "dry_run": dry_run,
    }

    # Get calendar backend
    backend = None
    action_cal_id = config.get("openclaw_cal_id", "")
    if not dry_run:
        try:
            from cal_backend import CalendarBackend
            backend = CalendarBackend()
            if not action_cal_id:
                action_cal_id = backend.get_openclaw_cal_id()
        except Exception:
            conn.close()
            return {"error": "Calendar backend unavailable"}

    # ─── Rename paused/canceled action events on calendar ─────────────────────
    status_actions = conn.execute("""
        SELECT * FROM action_events
        WHERE status IN ('paused', 'canceled')
        AND event_id != '' AND event_id != 'dry-run'
    """).fetchall()

    for action in status_actions:
        status = action["status"]
        event_id = action["event_id"]
        action_cal = action["action_calendar_id"]

        if not backend or not event_id:
            continue

        try:
            # Read current event from calendar
            cal_event = backend.get_event(action_cal, event_id)
            if not cal_event:
                continue

            title = cal_event.get("summary", "")

            # Only rename if not already prefixed
            prefix = f"🦞 [{status.capitalize()}] "
            if title.startswith(prefix):
                continue  # already renamed

            # Remove any existing status prefix
            for p in ("🦞 [Paused] ", "🦞 [Canceled] "):
                if title.startswith(p):
                    title = title[len(p):]

            new_title = f"{prefix}{title}"

            # Update description status marker too
            desc = cal_event.get("description", "")
            new_desc = update_status_in_description(desc, status)

            if not dry_run:
                backend.update_event(action_cal, event_id,
                                     summary=new_title, description=new_desc)

            key = f"renamed_{status}"
            results[key] = results.get(key, 0) + 1

        except Exception:
            pass

    # ─── Delete old canceled entries ──────────────────────────────────────────
    old_canceled = conn.execute("""
        SELECT * FROM action_events
        WHERE status = 'canceled' AND due_ts < ?
        AND event_id != '' AND event_id != 'dry-run'
    """, (cutoff_ts,)).fetchall()

    for action in old_canceled:
        event_id = action["event_id"]
        action_cal = action["action_calendar_id"]

        if not dry_run and backend and event_id:
            try:
                backend.delete_event(action_cal, event_id)
            except Exception:
                pass

        # Remove from DB
        if not dry_run:
            action_uid = action["action_event_uid"]
            conn.execute("DELETE FROM links WHERE action_event_uid = ?", (action_uid,))
            conn.execute("DELETE FROM action_events WHERE action_event_uid = ?", (action_uid,))

        results["deleted_old"] += 1

    if not dry_run:
        conn.commit()
    conn.close()

    # ─── Clean up old sent_actions entries ────────────────────────────────────
    if not dry_run:
        conn2 = get_db()
        conn2.execute("DELETE FROM sent_actions WHERE sent_ts < ?", (cutoff_ts,))
        conn2.commit()
        conn2.close()

    return results


def get_cleanup_status(config: dict = None) -> dict:
    """Show cleanup statistics."""
    if config is None:
        config = load_config()

    from link_store import get_db
    conn = get_db()

    cleanup_days = config.get("action_cleanup_days", 30)
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(days=cleanup_days)).timestamp())

    paused_count = conn.execute(
        "SELECT COUNT(*) FROM action_events WHERE status = 'paused'"
    ).fetchone()[0]
    canceled_count = conn.execute(
        "SELECT COUNT(*) FROM action_events WHERE status = 'canceled'"
    ).fetchone()[0]
    old_canceled = conn.execute(
        "SELECT COUNT(*) FROM action_events WHERE status = 'canceled' AND due_ts < ?",
        (cutoff_ts,)
    ).fetchone()[0]
    sent_total = conn.execute("SELECT COUNT(*) FROM sent_actions").fetchone()[0]

    conn.close()
    return {
        "paused_actions": paused_count,
        "canceled_actions": canceled_count,
        "old_canceled_eligible_for_cleanup": old_canceled,
        "sent_actions_log_size": sent_total,
        "cleanup_threshold_days": cleanup_days,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cleanup", action="store_true", help="Run cleanup cycle")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned")
    parser.add_argument("--status", action="store_true", help="Show cleanup stats")
    args = parser.parse_args()

    config = load_config()

    if args.cleanup or args.dry_run:
        result = cleanup(config, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.status:
        print(json.dumps(get_cleanup_status(config), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
