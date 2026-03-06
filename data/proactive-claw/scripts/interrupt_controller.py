#!/usr/bin/env python3
"""
interrupt_controller.py — Interruption governance layer.

Enforces nudge limits, cooldowns, quiet hours, focus block suppression,
and priority-based nudge hierarchy.

Called by daemon.py between scoring and notification to filter which
events actually get surfaced to the user.

Usage:
  python3 interrupt_controller.py --filter <scan_json_file>
  python3 interrupt_controller.py --status
  python3 interrupt_controller.py --record-dismissal <event_id>
  python3 interrupt_controller.py --quiet-hours-check
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
DB_FILE = SKILL_DIR / "memory.db"

sys.path.insert(0, str(SKILL_DIR / "scripts"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS nudge_log (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id         TEXT DEFAULT '',
    nudge_type       TEXT DEFAULT '',
    priority_tier    INTEGER DEFAULT 5,
    sent_at          TEXT DEFAULT '',
    dismissed_at     TEXT DEFAULT NULL,
    cooldown_until   TEXT DEFAULT NULL,
    suppressed       INTEGER DEFAULT 0,
    suppressed_reason TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_nl_sent ON nudge_log(sent_at);
CREATE INDEX IF NOT EXISTS idx_nl_event ON nudge_log(event_id);
"""

# Priority tiers — lower number = higher priority
PRIORITY_TIERS = {
    "safety": 0,            # P0: conflicts, double-books
    "high_stakes_prep": 1,  # P1: high-stakes prep < 24h
    "policy_action": 2,     # P2: policy-triggered actions
    "follow_up": 3,         # P3: follow-up reminders
    "routine_checkin": 4,   # P4: routine check-ins
    "informational": 5,     # P5: digests, stats
}

# Max nudges per session based on proactivity mode
MODE_TOP_N = {
    "low": 3,
    "balanced": 6,
    "executive": 12,
}


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def classify_nudge_priority(event: dict, nudge_source: str = "daemon") -> int:
    """Determine priority tier for a nudge based on event properties and source."""
    if nudge_source == "conflict_detector":
        return PRIORITY_TIERS["safety"]

    event_type = event.get("event_type", "")
    hours_away = event.get("hours_away")

    # P1: high-stakes within 24h
    if event_type in ("one_off_high_stakes", "routine_high_stakes"):
        if hours_away is not None and hours_away <= 24:
            return PRIORITY_TIERS["high_stakes_prep"]

    if nudge_source == "policy_engine":
        return PRIORITY_TIERS["policy_action"]

    if nudge_source in ("follow_up", "intelligence_loop"):
        return PRIORITY_TIERS["follow_up"]

    if nudge_source in ("digest", "stats", "behaviour_report"):
        return PRIORITY_TIERS["informational"]

    # Default: routine check-in for regular events, high-stakes prep for important ones
    if event_type in ("one_off_high_stakes", "routine_high_stakes"):
        return PRIORITY_TIERS["high_stakes_prep"]
    if event_type == "routine_low_stakes":
        return PRIORITY_TIERS["routine_checkin"]

    return PRIORITY_TIERS["routine_checkin"]


def is_quiet_hours(config: dict) -> bool:
    """Check if current time falls within configured quiet_hours."""
    quiet = config.get("quiet_hours", {})
    if not quiet:
        return False

    now = datetime.now()
    is_weekend = now.weekday() >= 5
    window_key = "weekends" if is_weekend else "weekdays"
    window = quiet.get(window_key, "")
    if not window or "-" not in window:
        return False

    try:
        start_str, end_str = window.split("-")
        start_parts = start_str.strip().split(":")
        end_parts = end_str.strip().split(":")
        start_hour, start_min = int(start_parts[0]), int(start_parts[1])
        end_hour, end_min = int(end_parts[0]), int(end_parts[1])

        current_minutes = now.hour * 60 + now.minute
        start_minutes = start_hour * 60 + start_min
        end_minutes = end_hour * 60 + end_min

        # Handle overnight windows (e.g., 22:00-07:00)
        if start_minutes > end_minutes:
            return current_minutes >= start_minutes or current_minutes < end_minutes
        return start_minutes <= current_minutes < end_minutes
    except Exception:
        return False


def is_in_focus_block(config: dict) -> bool:
    """Check if there's an active focus block right now on the calendar."""
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
        openclaw_cal_id = backend.get_openclaw_cal_id()
        now = datetime.now(timezone.utc)
        near = now + timedelta(minutes=1)
        events = backend.list_events(openclaw_cal_id, now, near)
        for event in events:
            title = (event.get("summary") or "").lower()
            if "focus" in title or "prep" in title:
                return True
        return False
    except Exception:
        return False


def get_nudges_today(conn: sqlite3.Connection) -> int:
    """Count nudges sent today from nudge_log."""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    ).isoformat()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM nudge_log WHERE sent_at >= ? AND suppressed = 0",
        (today_start,)
    ).fetchone()
    return row["cnt"] if row else 0


def get_cooldown_active(conn: sqlite3.Connection, event_id: str,
                        cooldown_minutes: int) -> bool:
    """Check if a recent dismissal makes this event on cooldown."""
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=cooldown_minutes)).isoformat()
    row = conn.execute(
        "SELECT 1 FROM nudge_log WHERE event_id = ? AND dismissed_at IS NOT NULL "
        "AND dismissed_at >= ? LIMIT 1",
        (event_id, cutoff)
    ).fetchone()
    return row is not None


def record_nudge(conn: sqlite3.Connection, event_id: str, nudge_type: str,
                 priority: int) -> int:
    """Log a sent nudge to nudge_log. Returns the log row ID."""
    cur = conn.execute("""
        INSERT INTO nudge_log (event_id, nudge_type, priority_tier, sent_at)
        VALUES (?, ?, ?, ?)
    """, (event_id, nudge_type, priority, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    return cur.lastrowid


def record_suppression(conn: sqlite3.Connection, event_id: str, nudge_type: str,
                       priority: int, reason: str) -> int:
    """Log a suppressed nudge."""
    cur = conn.execute("""
        INSERT INTO nudge_log (event_id, nudge_type, priority_tier, sent_at,
                               suppressed, suppressed_reason)
        VALUES (?, ?, ?, ?, 1, ?)
    """, (event_id, nudge_type, priority, datetime.now(timezone.utc).isoformat(), reason))
    conn.commit()
    return cur.lastrowid


def record_dismissal(conn: sqlite3.Connection, event_id: str,
                     cooldown_minutes: int = 30):
    """Log a dismissal and set cooldown."""
    now_iso = datetime.now(timezone.utc).isoformat()
    cooldown_until = (datetime.now(timezone.utc) + timedelta(minutes=cooldown_minutes)).isoformat()
    conn.execute("""
        UPDATE nudge_log SET dismissed_at = ?, cooldown_until = ?
        WHERE event_id = ? AND dismissed_at IS NULL
        ORDER BY sent_at DESC LIMIT 1
    """, (now_iso, cooldown_until, event_id))
    conn.commit()


def filter_nudges(events: list, config: dict, state: dict = None) -> list:
    """Main filter function. Returns events that should actually be notified.

    Checks:
    1. max_nudges_per_day
    2. cooldown after dismissals
    3. quiet hours (suppress non-P0)
    4. focus block suppression (suppress non-P0)
    5. Priority sort + top-N by proactivity_mode
    """
    if not events:
        return []

    conn = get_db()
    mode = config.get("proactivity_mode", "balanced")
    max_per_day = config.get("max_nudges_per_day", 12)
    cooldown_min = config.get("nudge_cooldown_minutes", 30)
    top_n = MODE_TOP_N.get(mode, 6)

    nudges_today = get_nudges_today(conn)
    quiet = is_quiet_hours(config)

    # Try to detect focus block (expensive, skip if not needed)
    in_focus = False
    if not quiet:
        try:
            in_focus = is_in_focus_block(config)
        except Exception:
            pass

    # Classify and filter each event
    candidates = []
    for event in events:
        event_id = event.get("id", "")
        priority = classify_nudge_priority(event)

        # P0 (safety) always passes
        if priority > PRIORITY_TIERS["safety"]:
            # Check quiet hours
            if quiet:
                record_suppression(conn, event_id, "event_nudge", priority, "quiet_hours")
                continue

            # Check focus block
            if in_focus:
                record_suppression(conn, event_id, "event_nudge", priority, "focus_block")
                continue

            # Check daily limit
            if nudges_today >= max_per_day:
                record_suppression(conn, event_id, "event_nudge", priority, "daily_limit")
                continue

            # Check cooldown
            if event_id and get_cooldown_active(conn, event_id, cooldown_min):
                record_suppression(conn, event_id, "event_nudge", priority, "cooldown")
                continue

        candidates.append((priority, event.get("score", 0), event))

    conn.close()

    # Sort by priority (ascending), then score (descending)
    candidates.sort(key=lambda x: (x[0], -x[1]))

    # Take top-N
    filtered = [event for _, _, event in candidates[:top_n]]
    return filtered


def get_status(config: dict = None) -> dict:
    """Return current interrupt controller status."""
    if config is None:
        config = load_config()
    conn = get_db()
    nudges_today = get_nudges_today(conn)
    max_per_day = config.get("max_nudges_per_day", 12)
    mode = config.get("proactivity_mode", "balanced")
    quiet = is_quiet_hours(config)

    # Recent suppressions
    recent_suppressions = conn.execute("""
        SELECT suppressed_reason, COUNT(*) as cnt
        FROM nudge_log
        WHERE suppressed = 1 AND sent_at >= ?
        GROUP BY suppressed_reason
    """, ((datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),)).fetchall()

    suppression_summary = {r["suppressed_reason"]: r["cnt"] for r in recent_suppressions}

    conn.close()
    return {
        "status": "ok",
        "proactivity_mode": mode,
        "nudges_today": nudges_today,
        "max_per_day": max_per_day,
        "remaining_budget": max(0, max_per_day - nudges_today),
        "quiet_hours_active": quiet,
        "quiet_hours_config": config.get("quiet_hours", {}),
        "top_n_limit": MODE_TOP_N.get(mode, 6),
        "suppressions_24h": suppression_summary,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", metavar="SCAN_JSON_FILE",
                        help="Filter events from a scored scan JSON file")
    parser.add_argument("--status", action="store_true",
                        help="Show current interrupt controller status")
    parser.add_argument("--record-dismissal", metavar="EVENT_ID",
                        help="Record that a nudge was dismissed")
    parser.add_argument("--quiet-hours-check", action="store_true",
                        help="Check if quiet hours are currently active")
    args = parser.parse_args()

    config = load_config()

    if args.filter:
        scan = json.loads(Path(args.filter).read_text())
        events = scan.get("actionable", scan.get("events", []))
        filtered = filter_nudges(events, config)
        print(json.dumps({
            "input_count": len(events),
            "output_count": len(filtered),
            "mode": config.get("proactivity_mode", "balanced"),
            "events": [
                {"title": e.get("title"), "score": e.get("score"),
                 "event_type": e.get("event_type")}
                for e in filtered
            ],
        }, indent=2))

    elif args.status:
        print(json.dumps(get_status(config), indent=2))

    elif args.record_dismissal:
        conn = get_db()
        cooldown = config.get("nudge_cooldown_minutes", 30)
        record_dismissal(conn, args.record_dismissal, cooldown)
        conn.close()
        print(json.dumps({
            "status": "ok",
            "event_id": args.record_dismissal,
            "cooldown_minutes": cooldown,
        }))

    elif args.quiet_hours_check:
        print(json.dumps({
            "quiet_hours_active": is_quiet_hours(config),
            "config": config.get("quiet_hours", {}),
        }, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
