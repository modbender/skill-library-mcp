#!/usr/bin/env python3
"""
explain.py — Decision explainability mode.

Central CLI for tracing why any proactive decision was made:
nudges, policies, energy decisions.

Usage:
  python3 explain.py --explain-nudge <event_id>
  python3 explain.py --explain-policy <policy_id>
  python3 explain.py --explain-energy-decision <event_id>
  python3 explain.py --trace <event_id>
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


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    return conn


def explain_nudge(event_id: str) -> dict:
    """Trace why a nudge was sent for an event."""
    conn = get_db()
    trace = {"event_id": event_id, "sections": []}

    # 1. Proactivity score
    score_row = conn.execute("""
        SELECT * FROM proactivity_scores WHERE event_id = ?
        ORDER BY computed_at DESC LIMIT 1
    """, (event_id,)).fetchone()

    if score_row:
        explanation = json.loads(score_row["explanation_json"])
        trace["sections"].append({
            "section": "proactivity_score",
            "base_score": score_row["base_score"],
            "final_score": score_row["final_score"],
            "mode_multiplier": score_row["mode_multiplier"],
            "breakdown": explanation,
            "computed_at": score_row["computed_at"],
        })
    else:
        trace["sections"].append({
            "section": "proactivity_score",
            "note": "No proactivity score found — event may have used raw scan scoring.",
        })

    # 2. Nudge log
    nudge_rows = conn.execute("""
        SELECT * FROM nudge_log WHERE event_id = ?
        ORDER BY sent_at DESC LIMIT 5
    """, (event_id,)).fetchall()

    nudge_history = []
    for r in nudge_rows:
        entry = {
            "sent_at": r["sent_at"],
            "nudge_type": r["nudge_type"],
            "priority_tier": r["priority_tier"],
            "suppressed": bool(r["suppressed"]),
        }
        if r["suppressed"]:
            entry["suppressed_reason"] = r["suppressed_reason"]
        if r["dismissed_at"]:
            entry["dismissed_at"] = r["dismissed_at"]
            entry["cooldown_until"] = r["cooldown_until"]
        nudge_history.append(entry)

    if nudge_history:
        trace["sections"].append({
            "section": "nudge_history",
            "entries": nudge_history,
        })
    else:
        trace["sections"].append({
            "section": "nudge_history",
            "note": "No nudge log entries found for this event.",
        })

    conn.close()

    # 3. Human-readable summary
    summary_lines = []
    if score_row:
        summary_lines.append(
            f"Event scored {score_row['final_score']}/10 "
            f"(base {score_row['base_score']}, "
            f"mode multiplier {score_row['mode_multiplier']}x)."
        )
        exp = json.loads(score_row["explanation_json"])
        for key in ("energy", "notification", "policy", "relationship"):
            if key in exp and exp[key].get("delta", 0) != 0:
                summary_lines.append(
                    f"  {key}: {exp[key]['delta']:+.1f} — {exp[key]['reason']}"
                )
    sent_count = sum(1 for n in nudge_history if not n["suppressed"])
    suppressed_count = sum(1 for n in nudge_history if n["suppressed"])
    if sent_count or suppressed_count:
        summary_lines.append(
            f"Nudges: {sent_count} sent, {suppressed_count} suppressed."
        )

    trace["summary"] = "\n".join(summary_lines) if summary_lines else "No trace data available."
    return trace


def explain_policy(policy_id: int) -> dict:
    """Explain a policy: what it matches, how many times fired."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM policies WHERE id = ?", (policy_id,)
    ).fetchone()

    if not row:
        conn.close()
        return {"error": f"Policy {policy_id} not found."}

    policy_json = json.loads(row["policy_json"])
    result = {
        "policy_id": policy_id,
        "text": row["policy_text"],
        "active": bool(row["active"]),
        "times_fired": row["times_fired"],
        "last_fired": row["last_fired"],
        "created_at": row["created_at"],
        "trigger": policy_json.get("trigger", ""),
        "condition": policy_json.get("condition", {}),
        "action": policy_json.get("action", ""),
        "params": policy_json.get("params", {}),
        "autonomous": policy_json.get("autonomous", False),
    }

    # Human-readable explanation
    cond = policy_json.get("condition", {})
    cond_parts = []
    if "event_type" in cond:
        cond_parts.append(f"event type in {cond['event_type']}")
    if "title_contains" in cond:
        cond_parts.append(f"title contains '{cond['title_contains']}'")
    if "duration_minutes_gt" in cond:
        cond_parts.append(f"duration > {cond['duration_minutes_gt']} min")
    if "day_of_week" in cond:
        cond_parts.append(f"on {cond['day_of_week']}")

    result["explanation"] = (
        f"When {policy_json.get('trigger', '?')}: "
        f"if {' AND '.join(cond_parts) if cond_parts else 'always'}, "
        f"then {policy_json.get('action', '?')}. "
        f"{'Runs autonomously.' if policy_json.get('autonomous') else 'Requires confirmation.'}"
    )

    conn.close()
    return result


def explain_energy_decision(event_id: str) -> dict:
    """Explain energy scoring for an event."""
    conn = get_db()

    # Get the proactivity score for energy details
    score_row = conn.execute("""
        SELECT explanation_json, computed_at FROM proactivity_scores
        WHERE event_id = ? ORDER BY computed_at DESC LIMIT 1
    """, (event_id,)).fetchone()

    if not score_row:
        conn.close()
        return {"event_id": event_id, "note": "No proactivity score found for this event."}

    explanation = json.loads(score_row["explanation_json"])
    energy = explanation.get("energy", {})

    # Get current energy analysis
    try:
        from energy_predictor import analyse_energy
        from memory import get_db as mem_db
        mem_conn = mem_db()
        analysis = analyse_energy(mem_conn)
        mem_conn.close()
    except Exception:
        analysis = {"status": "unavailable"}

    result = {
        "event_id": event_id,
        "energy_delta": energy.get("delta", 0),
        "energy_reason": energy.get("reason", "unknown"),
        "computed_at": score_row["computed_at"],
    }

    if analysis.get("status") == "ok":
        result["best_times"] = analysis.get("best_times", [])[:3]
        result["worst_times"] = analysis.get("worst_times", [])[:3]
        result["outcomes_analysed"] = analysis.get("outcomes_analysed", 0)

    conn.close()
    return result


def full_trace(event_id: str) -> dict:
    """Full decision trace combining nudge, policy, and energy explanations."""
    nudge = explain_nudge(event_id)
    energy = explain_energy_decision(event_id)
    return {
        "event_id": event_id,
        "nudge_trace": nudge,
        "energy_trace": energy,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Explain proactive decisions — trace why nudges, policies, or energy decisions were made."
    )
    parser.add_argument("--explain-nudge", metavar="EVENT_ID",
                        help="Explain why a nudge was sent for an event")
    parser.add_argument("--explain-policy", type=int, metavar="POLICY_ID",
                        help="Explain a policy's conditions and history")
    parser.add_argument("--explain-energy-decision", metavar="EVENT_ID",
                        help="Explain energy scoring for an event")
    parser.add_argument("--trace", metavar="EVENT_ID",
                        help="Full decision trace for an event")
    args = parser.parse_args()

    if args.explain_nudge:
        print(json.dumps(explain_nudge(args.explain_nudge), indent=2))
    elif args.explain_policy is not None:
        print(json.dumps(explain_policy(args.explain_policy), indent=2))
    elif args.explain_energy_decision:
        print(json.dumps(explain_energy_decision(args.explain_energy_decision), indent=2))
    elif args.trace:
        print(json.dumps(full_trace(args.trace), indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
