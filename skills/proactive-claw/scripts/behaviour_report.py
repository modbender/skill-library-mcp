#!/usr/bin/env python3
"""
behaviour_report.py — Drift monitoring and monthly reports.

Tracks how proactivity changes over time: dismiss rates, energy pattern
shifts, policy effectiveness. Detects if the system is becoming less useful.

Usage:
  python3 behaviour_report.py --monthly
  python3 behaviour_report.py --snapshot
  python3 behaviour_report.py --compare "2025-01" "2025-02"
  python3 behaviour_report.py --drift-alert
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
DB_FILE = SKILL_DIR / "memory.db"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

SNAPSHOT_SCHEMA = """
CREATE TABLE IF NOT EXISTS behaviour_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bs_period ON behaviour_snapshots(period_start);
"""


def get_db() -> sqlite3.Connection:
    from memory import get_db as mem_db
    conn = mem_db()
    conn.executescript(SNAPSHOT_SCHEMA)
    conn.commit()
    return conn


def _compute_period_metrics(conn: sqlite3.Connection,
                            start: str, end: str) -> dict:
    """Compute metrics for a date range."""
    metrics = {}

    # Outcomes
    try:
        outcomes = conn.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END) as positive,
                   SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END) as negative,
                   SUM(CASE WHEN prep_done=1 THEN 1 ELSE 0 END) as prepped,
                   AVG(CASE WHEN follow_up_needed=1 THEN 1.0 ELSE 0.0 END) as followup_rate
            FROM outcomes
            WHERE event_datetime >= ? AND event_datetime < ?
        """, (start, end)).fetchone()
        if outcomes and outcomes["total"]:
            metrics["outcomes"] = {
                "total": outcomes["total"],
                "positive_rate": round((outcomes["positive"] or 0) / outcomes["total"], 2),
                "negative_rate": round((outcomes["negative"] or 0) / outcomes["total"], 2),
                "prep_rate": round((outcomes["prepped"] or 0) / outcomes["total"], 2),
                "followup_rate": round(outcomes["followup_rate"] or 0, 2),
            }
        else:
            metrics["outcomes"] = {"total": 0}
    except Exception:
        metrics["outcomes"] = {"total": 0, "note": "table not found"}

    # Nudge log (if exists)
    try:
        nudges = conn.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN suppressed=1 THEN 1 ELSE 0 END) as suppressed,
                   SUM(CASE WHEN dismissed_at IS NOT NULL THEN 1 ELSE 0 END) as dismissed
            FROM nudge_log
            WHERE sent_at >= ? AND sent_at < ?
        """, (start, end)).fetchone()
        if nudges and nudges["total"]:
            metrics["nudges"] = {
                "total": nudges["total"],
                "suppressed": nudges["suppressed"] or 0,
                "dismissed": nudges["dismissed"] or 0,
                "dismiss_rate": round((nudges["dismissed"] or 0) / max(nudges["total"], 1), 2),
            }
        else:
            metrics["nudges"] = {"total": 0}
    except Exception:
        metrics["nudges"] = {"total": 0, "note": "table not found"}

    # Proactivity scores (if exists)
    try:
        scores = conn.execute("""
            SELECT AVG(final_score) as avg_score,
                   MIN(final_score) as min_score,
                   MAX(final_score) as max_score,
                   COUNT(*) as count
            FROM proactivity_scores
            WHERE computed_at >= ? AND computed_at < ?
        """, (start, end)).fetchone()
        if scores and scores["count"]:
            metrics["proactivity"] = {
                "avg_score": round(scores["avg_score"] or 0, 1),
                "min_score": round(scores["min_score"] or 0, 1),
                "max_score": round(scores["max_score"] or 0, 1),
                "events_scored": scores["count"],
            }
        else:
            metrics["proactivity"] = {"events_scored": 0}
    except Exception:
        metrics["proactivity"] = {"events_scored": 0, "note": "table not found"}

    # Policies fired
    try:
        policies = conn.execute("""
            SELECT SUM(times_fired) as total_fires,
                   COUNT(*) as active_policies
            FROM policies WHERE active=1
        """).fetchone()
        if policies:
            metrics["policies"] = {
                "active": policies["active_policies"] or 0,
                "total_fires": policies["total_fires"] or 0,
            }
    except Exception:
        metrics["policies"] = {"note": "table not found"}

    return metrics


def monthly_report(conn: sqlite3.Connection, months_back: int = 1) -> dict:
    """Generate report for last N months."""
    now = datetime.now(timezone.utc)
    periods = []

    for i in range(months_back + 1):
        if i == 0:
            end = now
        else:
            end = now.replace(day=1) - timedelta(days=1) * (30 * (i - 1))
        start = (end.replace(day=1)).replace(hour=0, minute=0, second=0)
        end_str = end.isoformat()
        start_str = start.isoformat()
        label = start.strftime("%Y-%m")

        metrics = _compute_period_metrics(conn, start_str, end_str)
        periods.append({"period": label, "start": start_str, "end": end_str, "metrics": metrics})

    # Detect drift between last two periods
    drift_alerts = []
    if len(periods) >= 2:
        current = periods[0]["metrics"]
        previous = periods[1]["metrics"]

        # Dismiss rate increasing
        curr_dismiss = current.get("nudges", {}).get("dismiss_rate", 0)
        prev_dismiss = previous.get("nudges", {}).get("dismiss_rate", 0)
        if curr_dismiss > prev_dismiss + 0.2:
            drift_alerts.append(
                f"Dismiss rate increased from {prev_dismiss:.0%} to {curr_dismiss:.0%}"
            )

        # Prep rate declining
        curr_prep = current.get("outcomes", {}).get("prep_rate", 0)
        prev_prep = previous.get("outcomes", {}).get("prep_rate", 0)
        if prev_prep > 0 and curr_prep < prev_prep - 0.15:
            drift_alerts.append(
                f"Prep rate dropped from {prev_prep:.0%} to {curr_prep:.0%}"
            )

        # Negative sentiment rising
        curr_neg = current.get("outcomes", {}).get("negative_rate", 0)
        prev_neg = previous.get("outcomes", {}).get("negative_rate", 0)
        if curr_neg > prev_neg + 0.15:
            drift_alerts.append(
                f"Negative outcomes rose from {prev_neg:.0%} to {curr_neg:.0%}"
            )

    return {
        "status": "ok",
        "periods": periods,
        "drift_alerts": drift_alerts,
        "generated_at": now.isoformat(),
    }


def snapshot_metrics(conn: sqlite3.Connection) -> dict:
    """Take a current snapshot and save to DB."""
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=30)).isoformat()
    end = now.isoformat()
    metrics = _compute_period_metrics(conn, start, end)

    conn.execute("""
        INSERT INTO behaviour_snapshots (period_start, period_end, metrics_json, created_at)
        VALUES (?, ?, ?, ?)
    """, (start, end, json.dumps(metrics), now.isoformat()))
    conn.commit()

    return {
        "status": "ok",
        "period": f"{start[:10]} to {end[:10]}",
        "metrics": metrics,
    }


def compare_periods(conn: sqlite3.Connection,
                    period_a: str, period_b: str) -> dict:
    """Compare two monthly periods."""
    start_a = f"{period_a}-01T00:00:00"
    start_b = f"{period_b}-01T00:00:00"

    # Parse end dates
    import calendar as cal_mod
    ya, ma = int(period_a[:4]), int(period_a[5:7])
    yb, mb = int(period_b[:4]), int(period_b[5:7])
    end_a = f"{period_a}-{cal_mod.monthrange(ya, ma)[1]}T23:59:59"
    end_b = f"{period_b}-{cal_mod.monthrange(yb, mb)[1]}T23:59:59"

    metrics_a = _compute_period_metrics(conn, start_a, end_a)
    metrics_b = _compute_period_metrics(conn, start_b, end_b)

    return {
        "period_a": {"label": period_a, "metrics": metrics_a},
        "period_b": {"label": period_b, "metrics": metrics_b},
    }


def drift_alert(conn: sqlite3.Connection) -> dict:
    """Quick check for concerning drift patterns."""
    report = monthly_report(conn, months_back=1)
    alerts = report.get("drift_alerts", [])
    return {
        "status": "warning" if alerts else "ok",
        "alerts": alerts,
        "message": "System behaviour is drifting — consider reviewing config." if alerts else "No drift detected.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--monthly", action="store_true",
                        help="Generate monthly behaviour report")
    parser.add_argument("--months", type=int, default=1,
                        help="How many months back to compare (default: 1)")
    parser.add_argument("--snapshot", action="store_true",
                        help="Take a metrics snapshot")
    parser.add_argument("--compare", nargs=2, metavar=("PERIOD_A", "PERIOD_B"),
                        help="Compare two periods (e.g. 2025-01 2025-02)")
    parser.add_argument("--drift-alert", action="store_true",
                        help="Quick drift detection")
    args = parser.parse_args()

    conn = get_db()

    if args.monthly:
        print(json.dumps(monthly_report(conn, args.months), indent=2))
    elif args.snapshot:
        print(json.dumps(snapshot_metrics(conn), indent=2))
    elif args.compare:
        print(json.dumps(compare_periods(conn, args.compare[0], args.compare[1]), indent=2))
    elif args.drift_alert:
        print(json.dumps(drift_alert(conn), indent=2))
    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
