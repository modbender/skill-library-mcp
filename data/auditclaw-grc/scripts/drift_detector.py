#!/usr/bin/env python3
"""Drift Detection Engine for auditclaw-grc.

Compares current evidence snapshots against previous snapshots to detect
configuration drift (regressions and improvements).

Usage:
    python3 drift_detector.py --db-path /path/to/compliance.sqlite --provider aws
    python3 drift_detector.py --db-path /path/to/compliance.sqlite --provider all
    python3 drift_detector.py --db-path /path/to/compliance.sqlite --provider aws --check iam
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime


SKILL_DIR = os.path.expanduser(os.environ.get("SKILL_DIR", "~/clawd/skills/auditclaw-grc"))
DB_QUERY_SCRIPT = os.path.join(SKILL_DIR, "scripts", "db_query.py")


def get_db_query_path():
    """Find db_query.py from auditclaw-grc."""
    candidates = [
        DB_QUERY_SCRIPT,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_query.py"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    return None


def get_latest_evidence(conn, provider, check=None):
    """Get the most recent evidence snapshot for a provider/check."""
    query = """
        SELECT id, title, description, filepath, metadata, source, uploaded_at
        FROM evidence
        WHERE source LIKE ? AND type = 'automated'
    """
    params = [f"%{provider}%"]

    if check:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{check}%", f"%{check}%"])

    query += " ORDER BY uploaded_at DESC LIMIT 50"
    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_previous_evidence(conn, provider, current_id, check=None):
    """Get the previous evidence snapshot before the current one."""
    query = """
        SELECT id, title, description, filepath, metadata, source, uploaded_at
        FROM evidence
        WHERE source LIKE ? AND type = 'automated' AND id < ?
    """
    params = [f"%{provider}%", current_id]

    if check:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{check}%", f"%{check}%"])

    query += " ORDER BY uploaded_at DESC LIMIT 1"
    row = conn.execute(query, params).fetchone()
    return dict(row) if row else None


def _load_evidence_data(evidence):
    """Load evidence data from filepath or metadata."""
    # Try filepath first (file-based evidence)
    filepath = evidence.get("filepath")
    if filepath:
        expanded = os.path.expanduser(filepath)
        # Validate filepath is within expected directory
        real_path = os.path.realpath(expanded)
        allowed_base = os.path.realpath(os.path.expanduser("~/.openclaw/grc"))
        if not real_path.startswith(allowed_base):
            return {}  # skip files outside the GRC directory
        if os.path.exists(expanded):
            try:
                with open(expanded) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
    # Fall back to metadata field
    meta = evidence.get("metadata")
    if meta:
        try:
            return json.loads(meta) if isinstance(meta, str) else meta
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


def _extract_score(data):
    """Extract a numeric score/grade from evidence data for comparison."""
    # Check for score/grade keys commonly used by evidence scripts
    if "score" in data:
        return {"passed": data.get("score", 0), "failed": 0, "total": 1}
    if "grade" in data:
        grade_map = {"A+": 100, "A": 95, "B": 80, "C": 60, "D": 40, "F": 20}
        score = grade_map.get(data["grade"], 50)
        return {"passed": score, "failed": 100 - score, "total": 100}
    if "passed" in data:
        return {"passed": data.get("passed", 0), "failed": data.get("failed", 0),
                "total": data.get("total", 0)}
    # For header checks: count True/False values
    if "headers" in data and isinstance(data["headers"], dict):
        total = len(data["headers"])
        passed = sum(1 for v in data["headers"].values() if v)
        return {"passed": passed, "failed": total - passed, "total": total}
    # For SSL checks
    if "chain_valid" in data:
        passed = 1 if data["chain_valid"] else 0
        return {"passed": passed, "failed": 1 - passed, "total": 1}
    return {"passed": 0, "failed": 0, "total": 0}


def compare_snapshots(current, previous):
    """Compare two evidence snapshots and classify drift."""
    if not previous:
        return {"type": "initial", "detail": "First evidence snapshot \u2014 no previous data to compare"}

    try:
        curr_data = _load_evidence_data(current)
        prev_data = _load_evidence_data(previous)
    except Exception:
        return {"type": "error", "detail": "Could not parse evidence data"}

    if not curr_data and not prev_data:
        return {"type": "unchanged", "detail": "No parseable evidence data in either snapshot"}

    curr_scores = _extract_score(curr_data)
    prev_scores = _extract_score(prev_data)

    curr_passed = curr_scores["passed"]
    curr_failed = curr_scores["failed"]
    curr_total = curr_scores["total"]
    prev_passed = prev_scores["passed"]
    prev_failed = prev_scores["failed"]
    prev_total = prev_scores["total"]

    # Classify drift
    if curr_failed > prev_failed:
        drift_type = "regression"
        severity = "critical" if curr_failed - prev_failed >= 3 else "warning"
    elif curr_failed < prev_failed:
        drift_type = "improvement"
        severity = "info"
    elif curr_total != prev_total:
        drift_type = "scope_change"
        severity = "info"
    else:
        drift_type = "unchanged"
        severity = "info"

    return {
        "type": drift_type,
        "severity": severity,
        "current": {"passed": curr_passed, "failed": curr_failed, "total": curr_total},
        "previous": {"passed": prev_passed, "failed": prev_failed, "total": prev_total},
        "delta_passed": curr_passed - prev_passed,
        "delta_failed": curr_failed - prev_failed,
        "detail": _format_drift_detail(drift_type, curr_failed, prev_failed, curr_passed, prev_passed),
    }


def _format_drift_detail(drift_type, curr_failed, prev_failed, curr_passed, prev_passed):
    if drift_type == "regression":
        return f"REGRESSION: failures increased from {prev_failed} to {curr_failed} (+{curr_failed - prev_failed})"
    elif drift_type == "improvement":
        return f"IMPROVEMENT: failures decreased from {prev_failed} to {curr_failed} (-{prev_failed - curr_failed})"
    elif drift_type == "scope_change":
        return f"Scope changed: checks count different, passed {prev_passed}->{curr_passed}"
    else:
        return "No drift detected"


def create_drift_alert(db_path, provider, check_name, drift_result):
    """Create an alert for drift events (regressions and improvements)."""
    if drift_result["type"] in ("unchanged", "initial", "error"):
        return None

    db_query = get_db_query_path()
    if not db_query:
        return _create_alert_direct(db_path, provider, check_name, drift_result)

    title = f"Drift: {provider}/{check_name} \u2014 {drift_result['type']}"
    severity = drift_result.get("severity", "info")

    cmd = [
        sys.executable, db_query,
        "--db-path", db_path,
        "--action", "add-alert",
        "--type", "drift_detected",
        "--title", title,
        "--severity", severity,
        "--description", drift_result["detail"],
        "--resource-type", provider,
        "--resource-id", check_name,
        "--drift-details", json.dumps(drift_result, default=str),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        try:
            return json.loads(proc.stdout)
        except (json.JSONDecodeError, ValueError):
            return {"status": "created"}
    return _create_alert_direct(db_path, provider, check_name, drift_result)


def _create_alert_direct(db_path, provider, check_name, drift_result):
    """Direct DB insert for drift alert."""
    conn = sqlite3.connect(db_path)
    now = datetime.now().isoformat(timespec="seconds")
    cursor = conn.execute(
        """INSERT INTO alerts (type, title, severity, message, resource_type, resource_id, drift_details)
           VALUES ('drift_detected', ?, ?, ?, ?, ?, ?)""",
        (f"Drift: {provider}/{check_name} \u2014 {drift_result['type']}",
         drift_result.get("severity", "info"),
         drift_result["detail"],
         provider,
         check_name,
         json.dumps(drift_result, default=str))
    )
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return {"status": "created", "id": alert_id}


def check_drift(db_path, provider, check=None):
    """Run drift detection for a provider/check."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    providers = [provider] if provider != "all" else ["aws", "github", "check_headers", "check_ssl"]
    drifts = []
    total_checks = 0
    regressions = 0
    improvements = 0
    unchanged = 0

    for prov in providers:
        latest = get_latest_evidence(conn, prov, check)
        if not latest:
            continue

        # Group by source script or title
        checks_seen = {}
        for ev in latest:
            source = ev.get("source", "")
            title = ev.get("title", "")
            # Use source as check name, fall back to title
            if source:
                check_name = source.replace(".py", "").replace("_", "-")
            elif title:
                check_name = title.split(" - ")[0].lower().replace(" ", "-")
            else:
                check_name = "unknown"

            if check_name in checks_seen:
                continue
            checks_seen[check_name] = ev

        for check_name, current_ev in checks_seen.items():
            total_checks += 1
            previous = get_previous_evidence(conn, prov, current_ev["id"], check_name)
            drift = compare_snapshots(current_ev, previous)
            drift["provider"] = prov
            drift["check"] = check_name
            drift["evidence_id"] = current_ev["id"]
            drift["timestamp"] = current_ev["uploaded_at"]
            drifts.append(drift)

            if drift["type"] == "regression":
                regressions += 1
                create_drift_alert(db_path, prov, check_name, drift)
            elif drift["type"] == "improvement":
                improvements += 1
                create_drift_alert(db_path, prov, check_name, drift)
            else:
                unchanged += 1

    conn.close()
    return {
        "status": "ok",
        "total_checks": total_checks,
        "drifted": regressions + improvements,
        "regressions": regressions,
        "improvements": improvements,
        "unchanged": unchanged,
        "drifts": drifts,
    }


def drift_history(db_path, provider=None, days=30, severity=None):
    """Get drift history from alerts table."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    query = "SELECT * FROM alerts WHERE type = 'drift_detected'"
    params = []

    if provider:
        query += " AND resource_type = ?"
        params.append(provider)
    if days:
        query += " AND triggered_at >= datetime('now', ?)"
        params.append(f"-{days} days")
    if severity == "regression":
        query += " AND severity IN ('critical', 'warning')"
    elif severity == "improvement":
        query += " AND severity = 'info'"

    query += " ORDER BY triggered_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()

    alerts = [dict(r) for r in rows]
    regressions = sum(1 for a in alerts if a["severity"] in ("critical", "warning"))
    improvements = sum(1 for a in alerts if a["severity"] == "info")

    return {
        "status": "ok",
        "total": len(alerts),
        "regressions": regressions,
        "improvements": improvements,
        "drifts": alerts,
    }


def main():
    parser = argparse.ArgumentParser(description="Drift Detection for auditclaw-grc")
    parser.add_argument("--db-path", required=True, help="Path to compliance.sqlite")
    parser.add_argument("--action", choices=["check-drift", "drift-history"], default="check-drift")
    parser.add_argument("--provider", default="all", help="Provider to check (aws/github/all)")
    parser.add_argument("--check", help="Specific check name")
    parser.add_argument("--days", type=int, default=30, help="Days of history")
    parser.add_argument("--severity", choices=["regression", "improvement", "all"], help="Filter drift type")

    args = parser.parse_args()

    if args.action == "check-drift":
        result = check_drift(args.db_path, args.provider, args.check)
    else:
        result = drift_history(args.db_path, args.provider, args.days, args.severity)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
