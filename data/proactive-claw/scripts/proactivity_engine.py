#!/usr/bin/env python3
"""
proactivity_engine.py — Unified proactivity scoring core.

Merges signals from scan_calendar, energy_predictor, adaptive_notifications,
policy_engine, and relationship_memory into ONE unified urgency score per event.

Called by daemon.py after scan_calendar returns raw scored events.

Usage:
  python3 proactivity_engine.py --score <scan_json_file>
  python3 proactivity_engine.py --score-event <event_json>
  python3 proactivity_engine.py --history <event_id>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
DB_FILE = SKILL_DIR / "memory.db"

sys.path.insert(0, str(SKILL_DIR / "scripts"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS proactivity_scores (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id         TEXT NOT NULL,
    event_title      TEXT DEFAULT '',
    base_score       INTEGER DEFAULT 0,
    energy_delta     REAL DEFAULT 0.0,
    notification_delta REAL DEFAULT 0.0,
    policy_delta     REAL DEFAULT 0.0,
    relationship_delta REAL DEFAULT 0.0,
    mode_multiplier  REAL DEFAULT 1.0,
    final_score      REAL DEFAULT 0.0,
    explanation_json  TEXT DEFAULT '{}',
    computed_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ps_event ON proactivity_scores(event_id);
CREATE INDEX IF NOT EXISTS idx_ps_computed ON proactivity_scores(computed_at);
"""

MODE_MULTIPLIERS = {
    "low": {"high_stakes": 1.0, "default": 0.5},
    "balanced": {"high_stakes": 1.0, "default": 1.0},
    "executive": {"high_stakes": 1.3, "default": 1.3},
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


def get_mode_multiplier(mode: str, event_type: str) -> float:
    """Return scoring multiplier based on proactivity_mode and event type."""
    mode_cfg = MODE_MULTIPLIERS.get(mode, MODE_MULTIPLIERS["balanced"])
    is_high_stakes = event_type in ("one_off_high_stakes", "routine_high_stakes")
    return mode_cfg["high_stakes"] if is_high_stakes else mode_cfg["default"]


def compute_energy_delta(event: dict, config: dict) -> tuple:
    """Query energy_predictor for this event's timing. Returns (delta, explanation)."""
    try:
        from energy_predictor import analyse_energy, check_event_timing
        from memory import get_db as mem_db
        conn = mem_db()
        event_dt = event.get("start", "")
        if not event_dt:
            conn.close()
            return 0.0, "no start time"
        result = check_event_timing(conn, event_dt, event.get("event_type", ""))
        conn.close()
        if result.get("status") != "ok":
            return 0.0, "insufficient energy data"
        energy_score = result.get("energy_score", 0)
        if result.get("warning"):
            return -1.0, result["warning"]
        if result.get("tip"):
            return 0.5, result["tip"]
        if energy_score > 0.5:
            return 0.3, f"good energy window (score {energy_score:+.1f})"
        if energy_score < -0.3:
            return -0.5, f"low energy window (score {energy_score:+.1f})"
        return 0.0, f"neutral energy (score {energy_score:+.1f})"
    except Exception as e:
        return 0.0, f"energy check unavailable: {e}"


def compute_notification_delta(event: dict, config: dict) -> tuple:
    """Check if adaptive_notifications says this event type is over-dismissed."""
    try:
        from adaptive_notifications import get_db as an_db
        conn = an_db()
        event_type = event.get("event_type", "")
        if not event_type:
            conn.close()
            return 0.0, "no event type"
        # Check frequency preference
        pref = conn.execute(
            "SELECT value, confidence FROM notification_preferences WHERE key = ?",
            (f"frequency_{event_type}",)
        ).fetchone()
        conn.close()
        if not pref or float(pref["confidence"]) < 0.4:
            return 0.0, "not enough notification history"
        freq = pref["value"]
        if freq == "low":
            return -1.0, f"high dismiss rate for {event_type} — reducing priority"
        if freq == "high":
            return 0.5, f"user engages well with {event_type} notifications"
        return 0.0, f"normal engagement with {event_type}"
    except Exception as e:
        return 0.0, f"notification check unavailable: {e}"


def compute_policy_delta(event: dict, config: dict) -> tuple:
    """Check if any active policies match this event (boost if yes)."""
    try:
        from policy_engine import get_db as pe_db, get_active_policies
        conn = pe_db()
        policies = get_active_policies(conn)
        conn.close()
        if not policies:
            return 0.0, "no active policies"
        title = (event.get("title") or "").lower()
        event_type = event.get("event_type", "")
        matching = []
        for p in policies:
            pj = p["policy_json"]
            cond = pj.get("condition", {})
            if "event_type" in cond and event_type in cond["event_type"]:
                matching.append(p["policy_text"])
            elif "title_contains" in cond and cond["title_contains"] in title:
                matching.append(p["policy_text"])
        if matching:
            return 0.5, f"{len(matching)} policy(ies) match: {matching[0][:50]}"
        return 0.0, "no policies match"
    except Exception as e:
        return 0.0, f"policy check unavailable: {e}"


def compute_relationship_delta(event: dict, config: dict) -> tuple:
    """Check relationship_memory for high-impact attendees."""
    try:
        from relationship_memory import get_db as rm_db
        conn = rm_db()
        attendees = event.get("attendees_count", 0)
        has_external = event.get("has_external_attendees", False)
        if not has_external or attendees == 0:
            conn.close()
            return 0.0, "no external attendees"
        title = event.get("title", "")
        # Check if any attendees are high-frequency contacts
        top_contacts = conn.execute(
            "SELECT email, interaction_count FROM contacts ORDER BY interaction_count DESC LIMIT 10"
        ).fetchall()
        conn.close()
        if top_contacts and any(c["interaction_count"] >= 5 for c in top_contacts):
            return 0.3, "event involves frequent contacts"
        return 0.0, "no notable contacts found"
    except Exception as e:
        return 0.0, f"relationship check unavailable: {e}"


def score_events(scan_output: dict, config: dict) -> dict:
    """Takes raw scan_calendar output, returns enriched output with unified scores.

    This is the main entry point called by daemon.py.
    """
    conn = get_db()
    mode = config.get("proactivity_mode", "balanced")
    half_life = config.get("memory_decay_half_life_days", 90)
    now_iso = datetime.now(timezone.utc).isoformat()
    threshold = config.get("calendar_threshold", 6)

    enriched_events = []
    enriched_actionable = []

    for event in scan_output.get("events", []):
        event_id = event.get("id", "")
        base_score = event.get("score", 0)
        event_type = event.get("event_type", "one_off_standard")

        # Compute deltas from each signal source
        energy_delta, energy_reason = compute_energy_delta(event, config)
        notif_delta, notif_reason = compute_notification_delta(event, config)
        policy_delta, policy_reason = compute_policy_delta(event, config)
        rel_delta, rel_reason = compute_relationship_delta(event, config)

        # Apply mode multiplier
        multiplier = get_mode_multiplier(mode, event_type)

        # Compute final score
        raw_total = base_score + energy_delta + notif_delta + policy_delta + rel_delta
        final_score = max(0, min(10, raw_total * multiplier))

        explanation = {
            "base_score": base_score,
            "energy": {"delta": energy_delta, "reason": energy_reason},
            "notification": {"delta": notif_delta, "reason": notif_reason},
            "policy": {"delta": policy_delta, "reason": policy_reason},
            "relationship": {"delta": rel_delta, "reason": rel_reason},
            "mode": mode,
            "multiplier": multiplier,
            "final_score": round(final_score, 1),
        }

        # Store in DB
        try:
            conn.execute("""
                INSERT INTO proactivity_scores
                    (event_id, event_title, base_score, energy_delta, notification_delta,
                     policy_delta, relationship_delta, mode_multiplier, final_score,
                     explanation_json, computed_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (event_id, event.get("title", ""), base_score, energy_delta,
                  notif_delta, policy_delta, rel_delta, multiplier,
                  round(final_score, 1), json.dumps(explanation), now_iso))
        except Exception:
            pass

        # Update event with unified score
        event["score"] = round(final_score, 1)
        event["proactivity_explanation"] = explanation
        enriched_events.append(event)

        if final_score >= threshold and not event.get("snoozed", False):
            enriched_actionable.append(event)

    try:
        conn.commit()
    except Exception:
        pass
    conn.close()

    # Sort by unified score
    enriched_actionable.sort(key=lambda e: -e["score"])

    scan_output["events"] = enriched_events
    scan_output["actionable"] = enriched_actionable
    scan_output["scoring"] = {
        "engine": "proactivity_engine",
        "mode": mode,
        "events_scored": len(enriched_events),
        "actionable_count": len(enriched_actionable),
    }

    return scan_output


def score_single_event(event_json: str, config: dict = None) -> dict:
    """Score a single event (for CLI/testing)."""
    event = json.loads(event_json) if isinstance(event_json, str) else event_json
    if config is None:
        config = load_config()
    fake_scan = {"events": [event], "actionable": []}
    result = score_events(fake_scan, config)
    if result["events"]:
        return result["events"][0]
    return {"error": "no event scored"}


def get_score_history(event_id: str) -> list:
    """Return scoring history for an event."""
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM proactivity_scores
        WHERE event_id = ?
        ORDER BY computed_at DESC
        LIMIT 10
    """, (event_id,)).fetchall()
    conn.close()
    return [
        {
            "event_id": r["event_id"],
            "event_title": r["event_title"],
            "base_score": r["base_score"],
            "final_score": r["final_score"],
            "mode_multiplier": r["mode_multiplier"],
            "explanation": json.loads(r["explanation_json"]),
            "computed_at": r["computed_at"],
        }
        for r in rows
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--score", metavar="SCAN_JSON_FILE",
                        help="Score events from a scan_calendar JSON output file")
    parser.add_argument("--score-event", metavar="EVENT_JSON",
                        help="Score a single event (JSON string)")
    parser.add_argument("--history", metavar="EVENT_ID",
                        help="Show scoring history for an event")
    args = parser.parse_args()

    config = load_config()

    if args.score:
        scan = json.loads(Path(args.score).read_text())
        result = score_events(scan, config)
        print(json.dumps({
            "scoring": result.get("scoring"),
            "actionable": [
                {"title": e.get("title"), "score": e["score"],
                 "explanation": e.get("proactivity_explanation")}
                for e in result.get("actionable", [])
            ],
        }, indent=2))

    elif args.score_event:
        result = score_single_event(args.score_event, config)
        print(json.dumps(result, indent=2))

    elif args.history:
        history = get_score_history(args.history)
        print(json.dumps({"event_id": args.history, "history": history}, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
