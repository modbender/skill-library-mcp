#!/usr/bin/env python3
"""
action_planner.py — Plan actions from user calendar events into the Action Calendar.

The PLAN phase of the daemon:
  1. Ingest user events → upsert into link_store
  2. Detect missing events → pause linked actions
  3. Auto-relink moved events (fingerprint match)
  4. Create confirm_delete prompts after 2 misses
  5. Generate action calendar entries (prep, buffer, reminder, etc.) and link them

Usage:
  python3 action_planner.py --plan              # run one plan cycle
  python3 action_planner.py --plan --dry-run    # show what would be created
  python3 action_planner.py --status            # show planner state
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

MISSING_THRESHOLD = 2  # consecutive scans missing before prompting deletion


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _iso_to_ts(iso_str: str) -> int:
    """Convert ISO datetime string to Unix timestamp."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return 0


def _ts_to_iso(ts: int) -> str:
    """Convert Unix timestamp to ISO string."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def create_action_event_on_calendar(backend, action_cal_id: str,
                                     title: str, start_dt, end_dt,
                                     description: str, dry_run: bool = False) -> dict:
    """Create an event on the action calendar. Returns provider event dict."""
    if dry_run:
        return {"id": "dry-run", "summary": title, "start": start_dt.isoformat()}
    try:
        return backend.create_event(action_cal_id, title, start_dt, end_dt, description)
    except Exception as e:
        return {"error": str(e)}


def plan(config: dict = None, dry_run: bool = False) -> dict:
    """Run one plan cycle: ingest, detect missing, create actions."""
    if config is None:
        config = load_config()

    from link_store import (
        get_db, compute_user_event_uid, compute_fingerprint,
        upsert_user_event, mark_missing_and_pause, get_all_active_user_events,
        find_by_fingerprint, find_by_title_near, missing_candidates,
        is_suppressed, has_confirm_delete, create_action_event,
        link_action, get_linked_actions, cancel_linked_actions
    )
    from action_codec import encode_action_description, build_action_payload
    from scan_calendar import scan_user_events

    conn = get_db()
    now = datetime.now(timezone.utc)
    now_ts = int(now.timestamp())
    backend_name = config.get("calendar_backend", "google")

    # Get calendar backend
    backend = None
    action_cal_id = config.get("openclaw_cal_id", "")
    if not dry_run:
        try:
            from cal_backend import CalendarBackend
            backend = CalendarBackend()
            if not action_cal_id:
                action_cal_id = backend.get_openclaw_cal_id()
        except Exception as e:
            conn.close()
            return {"error": f"Calendar backend unavailable: {e}"}

    results = {
        "ingested": 0,
        "missing_detected": 0,
        "relinked": 0,
        "confirm_delete_created": 0,
        "actions_planned": 0,
        "dry_run": dry_run,
    }

    # ─── Step A: Ingest all seen user events ──────────────────────────────────
    user_events = scan_user_events(config, backend, now)
    seen_uids = set()

    for event in user_events:
        event_id = event.get("id", "")
        cal_id = event.get("_calendar_id", "")
        title = event.get("summary", "")
        start_raw = event.get("start", {}).get("dateTime") or event.get("start", {}).get("date", "")
        end_raw = event.get("end", {}).get("dateTime") or event.get("end", {}).get("date", "")

        if not event_id:
            continue

        start_ts = _iso_to_ts(start_raw)
        end_ts = _iso_to_ts(end_raw)
        attendees = ",".join(
            a.get("email", "") for a in (event.get("attendees") or [])
        )
        location = event.get("location", "")
        fp = compute_fingerprint(title, start_raw, end_raw, attendees, location)

        uid = upsert_user_event(
            conn, backend_name, cal_id, event_id,
            title, start_ts, end_ts, fp
        )
        seen_uids.add(uid)
        results["ingested"] += 1

    # ─── Step B: Find events previously known but not seen ────────────────────
    # Get all active events in DB that are within the scan window
    scan_days = config.get("scan_days_ahead", 7)
    window_end_ts = now_ts + (scan_days * 86400)

    active_events = conn.execute("""
        SELECT * FROM user_events
        WHERE state = 'active'
        AND start_ts >= ? AND start_ts <= ?
    """, (now_ts - 3600, window_end_ts)).fetchall()

    for row in active_events:
        uid = row["user_event_uid"]
        if uid not in seen_uids:
            # ─── Step C: Auto-relink check ────────────────────────────────
            fp = row["fingerprint"]
            relinked = False
            if fp:
                matches = find_by_fingerprint(conn, fp, exclude_uid=uid)
                if matches:
                    # Same fingerprint found — treat as move/recreate
                    results["relinked"] += 1
                    relinked = True
                    continue

                # Try title + near-time match
                title_matches = find_by_title_near(
                    conn, row["title"], row["start_ts"], tolerance_sec=300
                )
                if title_matches:
                    results["relinked"] += 1
                    relinked = True
                    continue

            if not relinked:
                mark_missing_and_pause(conn, uid)
                results["missing_detected"] += 1

    # ─── Step D: Create confirm_delete for events missing >= threshold ────────
    missing = missing_candidates(conn, MISSING_THRESHOLD)
    for event in missing:
        uid = event["user_event_uid"]
        if is_suppressed(conn, uid):
            continue
        if has_confirm_delete(conn, uid):
            continue

        # Create a confirm_delete action
        due = now + timedelta(minutes=1)
        due_ts = int(due.timestamp())

        payload = build_action_payload(
            action_event_uid="",  # will be set after creation
            action_type="confirm_delete",
            user_event_uid=uid,
            relationship="confirm_delete_for",
            due_ts=due_ts,
            status="pending"
        )
        desc = encode_action_description(
            f"Was '{event['title']}' deleted? Respond: --yes / --no / --dont-ask",
            payload
        )

        if not dry_run and backend and action_cal_id:
            cal_event = create_action_event_on_calendar(
                backend, action_cal_id,
                f"🦞 Confirm: '{event['title']}' missing",
                due, due + timedelta(minutes=5),
                desc
            )
            provider_id = cal_event.get("id", "")
        else:
            provider_id = "dry-run"

        action_uid = create_action_event(
            conn, backend_name, action_cal_id, provider_id,
            "confirm_delete", "pending", due_ts, due_ts,
            due_ts + 300
        )
        link_action(conn, uid, action_uid, "confirm_delete_for")

        # Also write to pending_nudges.json for UX
        _write_pending_nudge(
            f"Event '{event['title']}' seems to have been deleted. Was it? "
            f"Reply: --yes {uid} / --no {uid} / --dont-ask {uid}",
            uid
        )

        results["confirm_delete_created"] += 1

    # ─── Step E: Plan proactive actions for active user events ────────────────
    # Check which active events need actions planned
    active_needing_actions = conn.execute("""
        SELECT ue.* FROM user_events ue
        WHERE ue.state = 'active' AND ue.start_ts > ?
        AND NOT EXISTS (
            SELECT 1 FROM links l
            JOIN action_events ae ON ae.action_event_uid = l.action_event_uid
            WHERE l.user_event_uid = ue.user_event_uid
            AND ae.action_type = 'reminder'
            AND ae.status NOT IN ('canceled', 'done')
        )
    """, (now_ts,)).fetchall()

    for event in active_needing_actions:
        uid = event["user_event_uid"]
        title = event["title"]
        start_ts = event["start_ts"]
        end_ts = event["end_ts"]

        # Create a reminder action (due 1 hour before or 1 day for far events)
        hours_away = (start_ts - now_ts) / 3600
        if hours_away > 24:
            reminder_offset = timedelta(days=1)
        elif hours_away > 2:
            reminder_offset = timedelta(hours=1)
        else:
            reminder_offset = timedelta(minutes=15)

        reminder_dt = datetime.fromtimestamp(start_ts, tz=timezone.utc) - reminder_offset
        reminder_ts = int(reminder_dt.timestamp())

        if reminder_ts <= now_ts:
            continue  # too late for a reminder

        payload = build_action_payload(
            action_event_uid="",
            action_type="reminder",
            user_event_uid=uid,
            relationship="reminder_for",
            due_ts=reminder_ts,
        )
        desc = encode_action_description(
            f"Reminder: {title}",
            payload
        )

        if not dry_run and backend and action_cal_id:
            cal_event = create_action_event_on_calendar(
                backend, action_cal_id,
                f"🦞 Reminder: {title}",
                reminder_dt, reminder_dt + timedelta(minutes=5),
                desc
            )
            provider_id = cal_event.get("id", "")
        else:
            provider_id = "dry-run"

        action_uid = create_action_event(
            conn, backend_name, action_cal_id, provider_id,
            "reminder", "planned", reminder_ts,
            reminder_ts, reminder_ts + 300
        )
        link_action(conn, uid, action_uid, "reminder_for")
        results["actions_planned"] += 1

    # ─── Step E2: Policy-driven actions (prep, buffer, debrief) ───────────────
    if config.get("feature_policy_engine", True):
        try:
            from policy_engine import get_db as pe_db, get_active_policies
            pe_conn = pe_db()
            policies = get_active_policies(pe_conn)
            pe_conn.close()

            if policies:
                for event in active_needing_actions:
                    uid = event["user_event_uid"]
                    title = event["title"]
                    start_ts_val = event["start_ts"]

                    # Check if this event matches any policy
                    for policy in policies:
                        pj = policy["policy_json"]
                        if pj.get("trigger") != "event_scored":
                            continue
                        cond = pj.get("condition", {})
                        title_check = cond.get("title_contains", "")
                        if title_check and title_check not in title.lower():
                            continue

                        action_type_name = pj.get("action", "")
                        if action_type_name not in ("block_prep_time", "add_buffer", "block_debrief"):
                            continue

                        # Check if we already have this action type for this event
                        existing = conn.execute("""
                            SELECT 1 FROM links l
                            JOIN action_events ae ON ae.action_event_uid = l.action_event_uid
                            WHERE l.user_event_uid = ?
                            AND ae.action_type = ?
                            AND ae.status NOT IN ('canceled', 'done')
                            LIMIT 1
                        """, (uid, action_type_name.replace("block_", ""))).fetchone()
                        if existing:
                            continue

                        params = pj.get("params", {})
                        event_start_dt = datetime.fromtimestamp(start_ts_val, tz=timezone.utc)

                        if action_type_name == "block_prep_time":
                            offset_str = params.get("offset", "1 day")
                            duration = params.get("duration_minutes", 30)
                            parts = offset_str.split()
                            val, unit = (int(parts[0]), parts[1]) if len(parts) >= 2 else (1, "day")
                            if "day" in unit:
                                prep_start = event_start_dt - timedelta(days=val)
                            elif "hour" in unit:
                                prep_start = event_start_dt - timedelta(hours=val)
                            else:
                                prep_start = event_start_dt - timedelta(minutes=val)

                            if prep_start <= now:
                                continue

                            prep_end = prep_start + timedelta(minutes=duration)
                            a_type = "prep"
                            relationship = "prep_for"
                            a_title = f"🦞 Prep: {title}"
                            a_start, a_end = prep_start, prep_end

                        elif action_type_name == "add_buffer":
                            buf_min = params.get("buffer_minutes", 10)
                            event_end_dt = datetime.fromtimestamp(event["end_ts"], tz=timezone.utc)
                            a_start = event_end_dt
                            a_end = event_end_dt + timedelta(minutes=buf_min)
                            a_type = "buffer"
                            relationship = "buffer_after"
                            a_title = f"🦞 Buffer after {title}"

                        elif action_type_name == "block_debrief":
                            duration = params.get("duration_minutes", 15)
                            event_end_dt = datetime.fromtimestamp(event["end_ts"], tz=timezone.utc)
                            offset_str = params.get("offset_after", "15 minutes")
                            parts = offset_str.split()
                            offset_val = int(parts[0]) if parts else 15
                            a_start = event_end_dt + timedelta(minutes=offset_val)
                            a_end = a_start + timedelta(minutes=duration)
                            a_type = "debrief"
                            relationship = "debrief_for"
                            a_title = f"🦞 Debrief: {title}"

                        else:
                            continue

                        a_due_ts = int(a_start.timestamp())

                        payload = build_action_payload(
                            action_event_uid="",
                            action_type=a_type,
                            user_event_uid=uid,
                            relationship=relationship,
                            due_ts=a_due_ts,
                        )
                        desc = encode_action_description(a_title, payload)

                        autonomy = config.get("max_autonomy_level", "confirm")
                        if autonomy == "advisory":
                            continue  # don't create action events in advisory mode

                        if not dry_run and backend and action_cal_id:
                            cal_event = create_action_event_on_calendar(
                                backend, action_cal_id,
                                a_title, a_start, a_end, desc
                            )
                            provider_id = cal_event.get("id", "")
                        else:
                            provider_id = "dry-run"

                        action_uid = create_action_event(
                            conn, backend_name, action_cal_id, provider_id,
                            a_type, "planned", a_due_ts,
                            int(a_start.timestamp()), int(a_end.timestamp())
                        )
                        link_action(conn, uid, action_uid, relationship)
                        results["actions_planned"] += 1

        except Exception:
            pass

    conn.close()
    return results


def _write_pending_nudge(message: str, event_id: str):
    """Write a nudge to pending_nudges.json."""
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
    parser.add_argument("--plan", action="store_true", help="Run one plan cycle")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    parser.add_argument("--status", action="store_true", help="Show planner state")
    args = parser.parse_args()

    config = load_config()

    if args.plan or args.dry_run:
        result = plan(config, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
    elif args.status:
        from link_store import get_db, get_status_summary
        conn = get_db()
        print(json.dumps(get_status_summary(conn), indent=2))
        conn.close()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
