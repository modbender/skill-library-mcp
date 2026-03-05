#!/usr/bin/env python3
"""Calculate compliance scores for GRC frameworks.

Implements weighted scoring methodology matching AuditClaw SaaS:
- Control health: HEALTHY (1.0), AT_RISK (0.5), CRITICAL (0.0)
- Priority weights: P5=2.0, P4=1.5, P3=1.0, P2=0.75, P1=0.5
- Score = (Total Weighted Health / Total Weight) * 100

Usage:
    python3 compliance_score.py [--framework <slug>] [--store] [--db-path /path/to/db]

Output: JSON with score, breakdown, trend, label.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta

DEFAULT_DB_PATH = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")

# Priority weight multipliers (from AuditClaw scoring engine)
PRIORITY_WEIGHTS = {
    5: 2.0,
    4: 1.5,
    3: 1.0,
    2: 0.75,
    1: 0.5,
}

# Score labels
SCORE_LABELS = [
    (90, "Excellent"),
    (75, "Good"),
    (60, "Fair"),
    (50, "Needs Attention"),
    (0, "Critical"),
]

# Drift thresholds
DRIFT_CRITICAL = 10  # >10pt drop = critical drift
DRIFT_WARNING = 5    # >5pt drop = warning drift


def get_score_label(score):
    """Map numeric score to human-readable label."""
    for threshold, label in SCORE_LABELS:
        if score >= threshold:
            return label
    return "Critical"


def determine_health(control, evidence_list):
    """Determine control health using priority-ordered rules.

    Evaluates top-to-bottom, first match wins (from AuditClaw ComplianceScoreServiceTest).

    Returns: ("HEALTHY"|"AT_RISK"|"CRITICAL", weight)
    """
    status = control.get("status", "not_started")
    now = datetime.now()

    # Rule 1: not_started → CRITICAL
    if status == "not_started":
        return "CRITICAL", 0.0

    # Rule 2: any expired evidence → CRITICAL
    for ev in evidence_list:
        if ev.get("status") == "expired":
            return "CRITICAL", 0.0

    # Rule 3: rejected → AT_RISK
    if status == "rejected":
        return "AT_RISK", 0.5

    # Rule 4: in_progress → AT_RISK
    if status == "in_progress":
        return "AT_RISK", 0.5

    # Rule 5: complete but no evidence linked → AT_RISK
    if status == "complete" and len(evidence_list) == 0:
        return "AT_RISK", 0.5

    # Rule 6: complete but evidence expiring within 30 days → AT_RISK
    if status == "complete":
        for ev in evidence_list:
            if ev.get("valid_until") and ev.get("status") == "active":
                try:
                    expiry = datetime.fromisoformat(ev["valid_until"])
                    if expiry <= now + timedelta(days=30):
                        return "AT_RISK", 0.5
                except (ValueError, TypeError):
                    pass

    # Rule 7: review overdue → AT_RISK
    review_date = control.get("review_date")
    if review_date:
        try:
            rd = datetime.fromisoformat(review_date)
            if rd < now:
                return "AT_RISK", 0.5
        except (ValueError, TypeError):
            pass

    # Rule 8: awaiting_review → AT_RISK
    if status == "awaiting_review":
        return "AT_RISK", 0.5

    # Rule 9: complete with current evidence → HEALTHY
    if status == "complete" and len(evidence_list) > 0:
        return "HEALTHY", 1.0

    # Default fallback
    return "AT_RISK", 0.5


def calculate_score(db_path, framework_slug=None):
    """Calculate compliance score for all or specific framework."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get frameworks to score
    if framework_slug:
        frameworks = conn.execute(
            "SELECT id, name, slug FROM frameworks WHERE slug = ? AND status = 'active'",
            (framework_slug,)
        ).fetchall()
        if not frameworks:
            conn.close()
            return {"status": "error", "message": f"Framework '{framework_slug}' not found or inactive"}
    else:
        frameworks = conn.execute(
            "SELECT id, name, slug FROM frameworks WHERE status = 'active'"
        ).fetchall()

    if not frameworks:
        conn.close()
        return {
            "status": "ok",
            "score": 0.0,
            "label": "Critical",
            "frameworks": [],
            "message": "No active frameworks found"
        }

    framework_scores = []
    total_weighted_health = 0.0
    total_weight = 0.0
    all_health_counts = {"HEALTHY": 0, "AT_RISK": 0, "CRITICAL": 0}

    for fw in frameworks:
        controls = conn.execute(
            "SELECT * FROM controls WHERE framework_id = ?", (fw["id"],)
        ).fetchall()

        if not controls:
            framework_scores.append({
                "framework": fw["slug"],
                "name": fw["name"],
                "score": 0.0,
                "label": "Critical",
                "total_controls": 0,
                "health_distribution": {"HEALTHY": 0, "AT_RISK": 0, "CRITICAL": 0},
            })
            continue

        fw_weighted_health = 0.0
        fw_total_weight = 0.0
        health_counts = {"HEALTHY": 0, "AT_RISK": 0, "CRITICAL": 0}

        for control in controls:
            control_dict = dict(control)
            priority = control_dict.get("priority", 3)
            weight = PRIORITY_WEIGHTS.get(priority, 1.0)

            # Get linked evidence for this control
            evidence = conn.execute(
                """SELECT e.* FROM evidence e
                   JOIN evidence_controls ec ON e.id = ec.evidence_id
                   WHERE ec.control_id = ?""",
                (control_dict["id"],)
            ).fetchall()
            evidence_list = [dict(e) for e in evidence]

            health, health_value = determine_health(control_dict, evidence_list)
            health_counts[health] += 1
            all_health_counts[health] += 1

            fw_weighted_health += health_value * weight
            fw_total_weight += weight

            total_weighted_health += health_value * weight
            total_weight += weight

        fw_score = round((fw_weighted_health / fw_total_weight * 100) if fw_total_weight > 0 else 0.0, 2)

        framework_scores.append({
            "framework": fw["slug"],
            "name": fw["name"],
            "score": fw_score,
            "label": get_score_label(fw_score),
            "total_controls": len(controls),
            "health_distribution": health_counts,
        })

    overall_score = round((total_weighted_health / total_weight * 100) if total_weight > 0 else 0.0, 2)

    # Get baseline for drift detection
    baseline_row = conn.execute(
        "SELECT score FROM compliance_scores WHERE framework_slug IS NULL ORDER BY calculated_at DESC LIMIT 1"
    ).fetchone()
    baseline = baseline_row["score"] if baseline_row else None

    drift = None
    trend = "unknown"
    if baseline is not None:
        delta = overall_score - baseline
        if delta < -DRIFT_CRITICAL:
            drift = "critical"
        elif delta < -DRIFT_WARNING:
            drift = "warning"
        elif abs(delta) <= 2:
            trend = "stable"
        elif delta > 2:
            trend = "improving"
        else:
            trend = "declining"

        if drift:
            trend = "declining"

    conn.close()

    return {
        "status": "ok",
        "score": overall_score,
        "label": get_score_label(overall_score),
        "health_distribution": all_health_counts,
        "frameworks": framework_scores,
        "trend": trend,
        "drift": drift,
        "baseline": baseline,
    }


def store_score(db_path, result, framework_slug=None):
    """Store score in compliance_scores table for history."""
    conn = sqlite3.connect(db_path)
    # Store overall score
    conn.execute(
        """INSERT INTO compliance_scores (framework_slug, score, total_controls,
           healthy_controls, at_risk_controls, critical_controls, metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            framework_slug,
            result["score"],
            sum(f["total_controls"] for f in result.get("frameworks", [])),
            result.get("health_distribution", {}).get("HEALTHY", 0),
            result.get("health_distribution", {}).get("AT_RISK", 0),
            result.get("health_distribution", {}).get("CRITICAL", 0),
            json.dumps({"frameworks": [f["framework"] for f in result.get("frameworks", [])]})
        )
    )
    # When storing overall score, also store per-framework scores
    if not framework_slug:
        for fw in result.get("frameworks", []):
            hd = fw.get("health_distribution", {})
            conn.execute(
                """INSERT INTO compliance_scores (framework_slug, score, total_controls,
                   healthy_controls, at_risk_controls, critical_controls, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    fw["framework"],
                    fw["score"],
                    fw["total_controls"],
                    hd.get("HEALTHY", 0),
                    hd.get("AT_RISK", 0),
                    hd.get("CRITICAL", 0),
                    json.dumps({"framework": fw["framework"]})
                )
            )
    conn.commit()
    conn.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="Calculate GRC compliance score")
    parser.add_argument("--framework", help="Framework slug (or all if omitted)")
    parser.add_argument("--store", action="store_true", help="Store score in history")
    parser.add_argument("--db-path", help="Path to SQLite database")
    args = parser.parse_args()

    db_path = args.db_path or os.environ.get("GRC_DB_PATH", DEFAULT_DB_PATH)

    if not os.path.exists(db_path):
        print(json.dumps({"status": "error", "message": f"Database not found at {db_path}. Run init_db.py first."}),
              file=sys.stderr)
        sys.exit(1)

    try:
        result = calculate_score(db_path, args.framework)

        if result.get("status") == "error":
            print(json.dumps(result), file=sys.stderr)
            sys.exit(1)

        if args.store:
            store_score(db_path, result, args.framework)
            result["stored"] = True

        print(json.dumps(result, indent=2, default=str))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
