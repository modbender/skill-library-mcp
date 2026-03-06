#!/usr/bin/env python3
"""
policy_conflict_detector.py — Detect contradictory calendar policies.

Warns when policies would conflict (e.g., "block prep before all meetings"
+ "no events before 10am").

Usage:
  python3 policy_conflict_detector.py --check-all
  python3 policy_conflict_detector.py --check-new <policy_json>
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
DB_FILE = SKILL_DIR / "memory.db"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

CONFLICT_SCHEMA = """
CREATE TABLE IF NOT EXISTS policy_conflicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_a_id INTEGER NOT NULL,
    policy_b_id INTEGER NOT NULL,
    conflict_type TEXT NOT NULL,
    description TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    resolved INTEGER DEFAULT 0
);
"""


def get_db() -> sqlite3.Connection:
    from memory import get_db as mem_db
    conn = mem_db()
    conn.executescript(CONFLICT_SCHEMA)
    conn.commit()
    return conn


def _conditions_overlap(cond_a: dict, cond_b: dict) -> bool:
    """Check if two policy conditions could match the same events."""
    # If either has no conditions, it matches everything
    if not cond_a or not cond_b:
        return True

    # Check event_type overlap
    et_a = set(cond_a.get("event_type", []))
    et_b = set(cond_b.get("event_type", []))
    if et_a and et_b and not et_a & et_b:
        return False

    # Check title overlap (both have title_contains)
    tc_a = cond_a.get("title_contains", "")
    tc_b = cond_b.get("title_contains", "")
    if tc_a and tc_b and tc_a != tc_b:
        # Partial overlap possible if one contains the other
        if tc_a not in tc_b and tc_b not in tc_a:
            return False

    return True


def _actions_conflict(action_a: str, action_b: str, params_a: dict, params_b: dict) -> str:
    """Check if two actions would conflict. Returns conflict description or empty string."""
    # Prep + block_focus at same time
    if {action_a, action_b} == {"block_prep_time", "block_focus_time"}:
        return "prep time and focus time may overlap on same window"

    # Same action with very different parameters
    if action_a == action_b:
        if action_a == "block_prep_time":
            off_a = params_a.get("offset", "")
            off_b = params_b.get("offset", "")
            if off_a != off_b:
                return f"duplicate prep policies with different offsets ({off_a} vs {off_b})"

    # warn_and_confirm + autonomous action
    if action_a == "warn_and_confirm" or action_b == "warn_and_confirm":
        other = action_b if action_a == "warn_and_confirm" else action_a
        if other in ("block_prep_time", "block_debrief", "add_buffer", "block_focus_time"):
            return f"one policy warns while another auto-acts ({other}) for overlapping events"

    return ""


def detect_conflicts(policies: list) -> list:
    """Compare all active policies pairwise for contradictions."""
    conflicts = []

    for i, pa in enumerate(policies):
        for pb in policies[i + 1:]:
            pj_a = pa.get("policy_json", {})
            pj_b = pb.get("policy_json", {})

            cond_a = pj_a.get("condition", {})
            cond_b = pj_b.get("condition", {})

            if not _conditions_overlap(cond_a, cond_b):
                continue

            action_a = pj_a.get("action", "")
            action_b = pj_b.get("action", "")
            params_a = pj_a.get("params", {})
            params_b = pj_b.get("params", {})

            conflict_desc = _actions_conflict(action_a, action_b, params_a, params_b)
            if conflict_desc:
                conflicts.append({
                    "policy_a": {"id": pa["id"], "text": pa["policy_text"]},
                    "policy_b": {"id": pb["id"], "text": pb["policy_text"]},
                    "conflict_type": "action_conflict",
                    "description": conflict_desc,
                })

            # Autonomy mismatch
            auto_a = pj_a.get("autonomous", False)
            auto_b = pj_b.get("autonomous", False)
            if auto_a != auto_b and action_a == action_b:
                conflicts.append({
                    "policy_a": {"id": pa["id"], "text": pa["policy_text"]},
                    "policy_b": {"id": pb["id"], "text": pb["policy_text"]},
                    "conflict_type": "autonomy_mismatch",
                    "description": f"same action ({action_a}) but different autonomy levels",
                })

    return conflicts


def check_new_policy(new_policy_json: dict, existing_policies: list) -> list:
    """Check if a proposed new policy conflicts with existing ones."""
    fake_policy = {
        "id": -1,
        "policy_text": new_policy_json.get("source_text", "(new policy)"),
        "policy_json": new_policy_json,
    }
    all_policies = existing_policies + [fake_policy]
    conflicts = detect_conflicts(all_policies)
    return [c for c in conflicts
            if c["policy_a"]["id"] == -1 or c["policy_b"]["id"] == -1]


def save_conflicts(conn: sqlite3.Connection, conflicts: list):
    """Persist detected conflicts to DB."""
    now = datetime.now(timezone.utc).isoformat()
    for c in conflicts:
        conn.execute("""
            INSERT INTO policy_conflicts (policy_a_id, policy_b_id, conflict_type, description, detected_at)
            VALUES (?, ?, ?, ?, ?)
        """, (c["policy_a"]["id"], c["policy_b"]["id"],
              c["conflict_type"], c["description"], now))
    conn.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-all", action="store_true",
                        help="Check all active policies for conflicts")
    parser.add_argument("--check-new", metavar="POLICY_JSON",
                        help="Check a new policy JSON against existing policies")
    args = parser.parse_args()

    conn = get_db()

    from policy_engine import get_active_policies
    policies = get_active_policies(conn)

    if args.check_all:
        conflicts = detect_conflicts(policies)
        if conflicts:
            save_conflicts(conn, conflicts)
        print(json.dumps({
            "policies_checked": len(policies),
            "conflicts_found": len(conflicts),
            "conflicts": conflicts,
        }, indent=2))

    elif args.check_new:
        new_pj = json.loads(args.check_new)
        conflicts = check_new_policy(new_pj, policies)
        print(json.dumps({
            "conflicts_with_new": len(conflicts),
            "conflicts": conflicts,
        }, indent=2))

    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
