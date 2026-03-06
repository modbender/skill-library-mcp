#!/usr/bin/env python3
"""
policy_engine.py — Autonomous calendar management via user-defined policies.

Policies let the agent act without per-event confirmation, within defined rules.
Policies are stored in memory.db and evaluated by the daemon on every scan.

Usage:
  python3 policy_engine.py --add "Always block prep time for high-stakes events"
  python3 policy_engine.py --list
  python3 policy_engine.py --delete <policy_id>
  python3 policy_engine.py --evaluate <scan_json_file>   # evaluate policies against scan output
  python3 policy_engine.py --dry-run <scan_json_file>    # show what would be done without acting
"""

import argparse
import json
import re
import sqlite3
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

# ─── Policy Schema ─────────────────────────────────────────────────────────────

POLICY_SCHEMA = """
CREATE TABLE IF NOT EXISTS policies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_text TEXT NOT NULL,
    policy_json TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    active      INTEGER DEFAULT 1,
    times_fired INTEGER DEFAULT 0,
    last_fired  TEXT DEFAULT NULL
);
"""

# ─── Policy Patterns ──────────────────────────────────────────────────────────

POLICY_PATTERNS = [
    # "Always block prep time for high-stakes events"
    (r"always\s+block\s+prep\s+(?:time\s+)?for\s+(high.?stakes|important|external|investor|board|demo|interview)",
     lambda m, text: {
         "trigger": "event_scored",
         "condition": {"event_type": ["one_off_high_stakes", "routine_high_stakes"]},
         "action": "block_prep_time",
         "params": {"offset": "1 day", "duration_minutes": 30},
         "autonomous": True,
         "description": f"Auto-block 30min prep for high-stakes events",
     }),

    # "Always block prep N hours/days before anything with word X"
    (r"always\s+block\s+(?:prep\s+)?(\d+)\s+(hour|day)[s]?\s+before\s+.{0,30}?(?:word\s+)?['\"]?(\w+)['\"]?",
     lambda m, text: {
         "trigger": "event_scored",
         "condition": {"title_contains": m.group(3).lower()},
         "action": "block_prep_time",
         "params": {"offset": f"{m.group(1)} {m.group(2)}s", "duration_minutes": 30},
         "autonomous": True,
         "description": f"Auto-block prep {m.group(1)} {m.group(2)}s before '{m.group(3)}' events",
     }),

    # "Protect Friday afternoons / Monday mornings from meetings"
    (r"protect\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(morning|afternoon|evening)",
     lambda m, text: {
         "trigger": "daily_scan",
         "condition": {"day_of_week": m.group(1).capitalize(), "time_of_day": m.group(2)},
         "action": "block_focus_time",
         "params": {"title": f"🦞 Focus time ({m.group(1).capitalize()} {m.group(2)})",
                    "duration_hours": 2},
         "autonomous": True,
         "description": f"Block focus time on {m.group(1).capitalize()} {m.group(2)}s",
     }),

    # "Always add N min buffer after meetings longer than X min"
    (r"always\s+add\s+(\d+)\s+min\s+buffer\s+after\s+(?:meetings?\s+)?(?:longer|more)\s+than\s+(\d+)\s+min",
     lambda m, text: {
         "trigger": "event_scored",
         "condition": {"duration_minutes_gt": int(m.group(2))},
         "action": "add_buffer",
         "params": {"buffer_minutes": int(m.group(1))},
         "autonomous": True,
         "description": f"Add {m.group(1)}min buffer after meetings longer than {m.group(2)}min",
     }),

    # "Always block debrief after board/investor/demo"
    (r"always\s+(?:block|add|schedule)\s+(?:a\s+)?debrief\s+after\s+.{0,30}?(?:word\s+)?['\"]?(\w+)['\"]?",
     lambda m, text: {
         "trigger": "event_scored",
         "condition": {"title_contains": m.group(1).lower()},
         "action": "block_debrief",
         "params": {"offset_after": "15 minutes", "duration_minutes": 15},
         "autonomous": True,
         "description": f"Auto-block debrief after '{m.group(1)}' events",
     }),

    # "Never schedule meetings before N am"
    (r"never\s+(?:schedule|add|create)\s+meetings?\s+before\s+(\d+)\s*(?:am|AM)?",
     lambda m, text: {
         "trigger": "create_event",
         "condition": {"start_hour_lt": int(m.group(1))},
         "action": "warn_and_confirm",
         "params": {"message": f"This is before your {m.group(1)}am start preference. Schedule anyway?"},
         "autonomous": False,
         "description": f"Warn before scheduling events before {m.group(1)}am",
     }),
]


def parse_policy(text: str) -> dict:
    text_lower = text.lower().strip()
    for pattern, parser in POLICY_PATTERNS:
        m = re.search(pattern, text_lower)
        if m:
            try:
                policy_json = parser(m, text_lower)
                policy_json["source_text"] = text
                return {"parsed": True, "policy_json": policy_json,
                        "description": policy_json.get("description", text),
                        "autonomous": policy_json.get("autonomous", False)}
            except Exception:
                continue
    return {
        "parsed": False,
        "policy_json": None,
        "suggestion": (
            "Couldn't parse that policy. Try:\n"
            "  • 'Always block prep time for high-stakes events'\n"
            "  • 'Always block prep 2 hours before anything with the word board'\n"
            "  • 'Protect Friday afternoons from meetings'\n"
            "  • 'Always add 10 min buffer after meetings longer than 60 min'\n"
            "  • 'Always block debrief after demo'"
        )
    }


def get_db():
    from memory import get_db as mem_db
    conn = mem_db()
    conn.executescript(POLICY_SCHEMA)
    conn.commit()
    return conn


def save_policy(conn, text: str, policy_json: dict) -> int:
    cur = conn.execute(
        "INSERT INTO policies (policy_text, policy_json, created_at) VALUES (?,?,?)",
        (text, json.dumps(policy_json), datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    return cur.lastrowid


def get_active_policies(conn) -> list:
    rows = conn.execute("SELECT * FROM policies WHERE active=1").fetchall()
    return [{"id": r["id"], "policy_text": r["policy_text"],
             "policy_json": json.loads(r["policy_json"]),
             "times_fired": r["times_fired"]} for r in rows]


def evaluate_policies(policies: list, events: list, dry_run: bool = False,
                      config: dict = None) -> list:
    """Evaluate all autonomous policies against scanned events. Return list of actions taken.

    The optional config parameter enables max_autonomy_level enforcement:
    - advisory: never execute, return suggestion only
    - confirm: never execute, mark as needs_confirmation
    - autonomous: execute as configured (explicit opt-in)
    """
    actions = []
    now = datetime.now(timezone.utc)
    autonomy = "confirm"
    if config:
        autonomy = config.get("max_autonomy_level", "confirm")

    for event in events:
        score = event.get("score", 0)
        if score < 5:
            continue

        for policy in policies:
            pj = policy["policy_json"]
            if not pj.get("autonomous", False):
                continue
            if pj.get("trigger") != "event_scored":
                continue

            cond = pj.get("condition", {})
            # Check event_type condition
            if "event_type" in cond:
                if event.get("event_type") not in cond["event_type"]:
                    continue
            # Check title_contains condition
            if "title_contains" in cond:
                if cond["title_contains"] not in (event.get("title") or "").lower():
                    continue
            # Check duration condition
            if "duration_minutes_gt" in cond:
                if event.get("duration_minutes", 0) <= cond["duration_minutes_gt"]:
                    continue

            # Policy matches — determine action
            action_type = pj.get("action")
            params = pj.get("params", {})
            event_title = event.get("title", "")
            event_start = event.get("start", "")

            action_record = {
                "policy_id": policy["id"],
                "policy_text": policy["policy_text"],
                "event_title": event_title,
                "action_type": action_type,
                "dry_run": dry_run,
                "autonomy_level": autonomy,
                "executed": False,
                "result": None,
            }

            # Enforce max_autonomy_level
            if autonomy == "advisory":
                action_record["result"] = {
                    "advisory": f"Would {action_type} for '{event_title}'",
                    "params": params,
                }
            elif autonomy == "confirm":
                action_record["result"] = {
                    "needs_confirmation": True,
                    "action": action_type,
                    "event_title": event_title,
                    "params": params,
                }
            elif not dry_run and event_start:
                try:
                    result = _execute_action(action_type, params, event_title,
                                              event_start, event.get("duration_minutes", 60))
                    action_record["executed"] = True
                    action_record["result"] = result
                except Exception as e:
                    action_record["result"] = {"error": str(e)}
            else:
                action_record["result"] = {"would_do": f"{action_type} for '{event_title}'",
                                            "params": params}

            actions.append(action_record)

    return actions


def _execute_action(action_type: str, params: dict,
                    event_title: str, event_start: str, event_duration: int) -> dict:
    """Execute a policy action by calling create_checkin.py or cal_backend.py."""
    from cal_backend import CalendarBackend
    import zoneinfo

    config = json.loads((SKILL_DIR / "config.json").read_text())
    tz_str = config.get("timezone", "UTC")
    backend = CalendarBackend()
    openclaw_cal_id = backend.get_openclaw_cal_id()

    try:
        start_dt = datetime.fromisoformat(event_start.replace("Z", "+00:00"))
    except Exception:
        return {"error": f"Could not parse event start: {event_start}"}

    if action_type == "block_prep_time":
        offset_str = params.get("offset", "1 day")
        duration = params.get("duration_minutes", 30)
        parts = offset_str.split()
        val, unit = (int(parts[0]), parts[1]) if len(parts) >= 2 else (1, "day")
        if "day" in unit:
            prep_start = start_dt - timedelta(days=val)
        elif "hour" in unit:
            prep_start = start_dt - timedelta(hours=val)
        else:
            prep_start = start_dt - timedelta(minutes=val)
        # Don't create if in the past
        if prep_start <= datetime.now(timezone.utc):
            return {"skipped": "prep time is in the past"}
        prep_end = prep_start + timedelta(minutes=duration)
        event = backend.create_event(
            openclaw_cal_id,
            f"🦞 Prep: {event_title}",
            prep_start, prep_end,
            f"Auto-blocked by policy: prep for {event_title}"
        )
        return {"created": f"Prep block at {prep_start.isoformat()}", "event_id": event.get("id")}

    elif action_type == "block_debrief":
        offset_str = params.get("offset_after", "15 minutes")
        duration = params.get("duration_minutes", 15)
        parts = offset_str.split()
        val, unit = (int(parts[0]), parts[1]) if len(parts) >= 2 else (15, "minutes")
        event_end = start_dt + timedelta(minutes=event_duration)
        if "minute" in unit:
            debrief_start = event_end + timedelta(minutes=val)
        elif "hour" in unit:
            debrief_start = event_end + timedelta(hours=val)
        else:
            debrief_start = event_end + timedelta(minutes=15)
        debrief_end = debrief_start + timedelta(minutes=duration)
        event = backend.create_event(
            openclaw_cal_id,
            f"🦞 Debrief: {event_title}",
            debrief_start, debrief_end,
            f"Auto-blocked by policy: debrief after {event_title}"
        )
        return {"created": f"Debrief block at {debrief_start.isoformat()}", "event_id": event.get("id")}

    elif action_type == "block_focus_time":
        return {"skipped": "focus_time blocking handled by daily_scan trigger"}

    elif action_type == "add_buffer":
        buffer_min = params.get("buffer_minutes", 10)
        event_end = start_dt + timedelta(minutes=event_duration)
        buffer_end = event_end + timedelta(minutes=buffer_min)
        event = backend.create_event(
            openclaw_cal_id,
            f"🦞 Buffer after {event_title}",
            event_end, buffer_end,
            f"Auto-blocked buffer by policy"
        )
        return {"created": f"Buffer at {event_end.isoformat()}", "event_id": event.get("id")}

    return {"error": f"Unknown action_type: {action_type}"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", metavar="POLICY_TEXT")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--delete", type=int, metavar="POLICY_ID")
    parser.add_argument("--evaluate", metavar="SCAN_JSON_FILE")
    parser.add_argument("--dry-run", metavar="SCAN_JSON_FILE")
    args = parser.parse_args()

    conn = get_db()

    if args.add:
        result = parse_policy(args.add)
        if not result["parsed"]:
            print(json.dumps(result, indent=2))
            return
        pid = save_policy(conn, args.add, result["policy_json"])
        auto = "autonomous" if result["autonomous"] else "requires confirmation"
        print(json.dumps({
            "status": "saved", "policy_id": pid,
            "description": result["description"],
            "mode": auto,
        }, indent=2))

    elif args.list:
        policies = get_active_policies(conn)
        print(json.dumps({"policies": policies}, indent=2))

    elif args.delete:
        conn.execute("UPDATE policies SET active=0 WHERE id=?", (args.delete,))
        conn.commit()
        print(json.dumps({"status": "deleted", "policy_id": args.delete}))

    elif args.evaluate or args.dry_run:
        scan_file = args.evaluate or args.dry_run
        dry = bool(args.dry_run)
        scan = json.loads(Path(scan_file).read_text())
        policies = get_active_policies(conn)
        actions = evaluate_policies(policies, scan.get("events", []), dry_run=dry)
        print(json.dumps({"dry_run": dry, "actions_taken": len(actions), "actions": actions}, indent=2))

    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
