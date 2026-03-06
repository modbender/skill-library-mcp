#!/usr/bin/env python3
"""
action_executor.py — Execute due actions from the Action Calendar.

The EXECUTE phase of the daemon:
  1. Read action calendar events due in [now, now+lookahead]
  2. Decode PC_ACTION metadata
  3. Check DB status (not paused/canceled)
  4. Idempotency check (skip if already sent)
  5. Send notification via configured channels
  6. Record sent

Usage:
  python3 action_executor.py --execute              # execute due actions
  python3 action_executor.py --execute --dry-run    # show what would fire
  python3 action_executor.py --due                  # list due actions
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

# Lookahead must be >= daemon interval to not miss actions
DEFAULT_LOOKAHEAD_SEC = 1200  # 20 minutes


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _build_notification_message(action: dict, user_event: dict = None) -> str:
    """Build a human-readable notification message for an action."""
    action_type = action.get("action_type", "")
    title = ""
    if user_event:
        title = user_event.get("title", "")

    messages = {
        "reminder": f"*{title}* is coming up. Want to prep?",
        "prep": f"🦞 Prep time for *{title}* is starting.",
        "buffer": f"🦞 Buffer time after *{title}*. Take a breath.",
        "debrief": f"🦞 Time to debrief: *{title}*. How did it go?",
        "followup": f"🦞 Follow-up reminder for *{title}*.",
        "checkin": f"🦞 Check-in: How was *{title}*?",
        "confirm_delete": (
            f"Event '*{title}*' seems to have been deleted from your calendar. "
            f"Was it removed intentionally?"
        ),
    }

    return messages.get(action_type, f"🦞 Action: {action_type} for {title}")


def execute_due(config: dict = None, dry_run: bool = False,
                lookahead_sec: int = DEFAULT_LOOKAHEAD_SEC) -> dict:
    """Execute actions that are due now."""
    if config is None:
        config = load_config()

    from link_store import (
        get_db, get_due_actions, was_sent, record_sent,
        update_action_status
    )
    from action_codec import decode_action_description

    conn = get_db()
    now = datetime.now(timezone.utc)
    now_ts = int(now.timestamp())

    results = {
        "executed": 0,
        "skipped_already_sent": 0,
        "skipped_paused": 0,
        "skipped_canceled": 0,
        "dry_run": dry_run,
        "actions": [],
    }

    # Get due actions from DB
    due_actions = get_due_actions(conn, now_ts, lookahead_sec)

    # Also try to read action calendar directly for any DB-missed entries
    try:
        if not dry_run:
            from cal_backend import CalendarBackend
            backend = CalendarBackend()
            action_cal_id = config.get("openclaw_cal_id", "")
            if action_cal_id:
                cal_events = backend.list_events(
                    action_cal_id, now,
                    now + timedelta(seconds=lookahead_sec)
                )
                # Cross-reference with DB actions via PC_ACTION metadata
                for cal_event in cal_events:
                    desc = cal_event.get("description", "")
                    payload = decode_action_description(desc)
                    if payload and payload.get("action_event_uid"):
                        # Already in due_actions from DB query? Skip if so
                        uid = payload["action_event_uid"]
                        if not any(a.get("action_event_uid") == uid for a in due_actions):
                            # Found a calendar action not in DB — add it
                            due_actions.append({
                                "action_event_uid": uid,
                                "action_type": payload.get("action_type", ""),
                                "user_event_uid": payload.get("user_event_uid", ""),
                                "status": payload.get("status", "planned"),
                                "due_ts": payload.get("due_ts", now_ts),
                                "relationship": payload.get("relationship", ""),
                                "_from_calendar": True,
                            })
    except Exception:
        pass

    for action in due_actions:
        action_uid = action.get("action_event_uid", "")
        action_type = action.get("action_type", "")
        user_event_uid = action.get("user_event_uid", "")
        status = action.get("status", "")
        due_ts = action.get("due_ts", 0)

        # Skip paused/canceled
        if status in ("paused", "canceled", "done"):
            key = "skipped_paused" if status == "paused" else "skipped_canceled"
            results[key] = results.get(key, 0) + 1
            continue

        # Idempotency check
        idemp_key = f"{action_uid}:{due_ts}"
        if was_sent(conn, idemp_key):
            results["skipped_already_sent"] += 1
            continue

        # Get user event details for the message
        user_event = None
        if user_event_uid:
            row = conn.execute(
                "SELECT * FROM user_events WHERE user_event_uid = ?",
                (user_event_uid,)
            ).fetchone()
            if row:
                user_event = dict(row)

        # Check user event state — don't fire for missing/deleted
        if user_event and user_event.get("state") in ("deleted_confirmed", "suppressed"):
            results["skipped_canceled"] += 1
            continue

        msg = _build_notification_message(action, user_event)

        action_record = {
            "action_uid": action_uid,
            "action_type": action_type,
            "user_event_title": user_event.get("title", "") if user_event else "",
            "message": msg,
            "fired": not dry_run,
        }

        if not dry_run:
            # Send notification
            try:
                from daemon import send_notification
                send_notification(config, msg, user_event_uid)
            except Exception:
                # Fallback: write to pending_nudges.json
                _write_pending_nudge(msg, user_event_uid)

            # Record sent + update status
            record_sent(conn, idemp_key)
            update_action_status(conn, action_uid, "fired")

        results["actions"].append(action_record)
        results["executed"] += 1

    conn.close()
    return results


def list_due(config: dict = None,
             lookahead_sec: int = DEFAULT_LOOKAHEAD_SEC) -> dict:
    """List actions that are currently due."""
    if config is None:
        config = load_config()
    from link_store import get_db, get_due_actions
    conn = get_db()
    now_ts = int(datetime.now(timezone.utc).timestamp())
    actions = get_due_actions(conn, now_ts, lookahead_sec)
    conn.close()
    return {
        "due_actions": actions,
        "count": len(actions),
        "window": f"{now_ts} to {now_ts + lookahead_sec}",
    }


def _write_pending_nudge(message: str, event_id: str):
    """Fallback: write nudge to pending_nudges.json."""
    nudges_file = SKILL_DIR / "pending_nudges.json"
    nudges = []
    if nudges_file.exists():
        try:
            nudges = json.loads(nudges_file.read_text())
        except Exception:
            nudges = []
    nudges.append({
        "message": message,
        "event_id": event_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "shown": False,
    })
    nudges_file.write_text(json.dumps(nudges, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Execute due actions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would fire")
    parser.add_argument("--due", action="store_true", help="List due actions")
    parser.add_argument("--lookahead", type=int, default=DEFAULT_LOOKAHEAD_SEC,
                        help="Lookahead in seconds")
    args = parser.parse_args()

    config = load_config()

    if args.execute or args.dry_run:
        result = execute_due(config, dry_run=args.dry_run,
                            lookahead_sec=args.lookahead)
        print(json.dumps(result, indent=2))
    elif args.due:
        print(json.dumps(list_due(config, args.lookahead), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
