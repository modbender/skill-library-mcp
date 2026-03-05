#!/usr/bin/env python3
"""Standalone evidence expiry checker for cron-driven alerts.

Designed to be called by OpenClaw cron in isolated sessions.
Checks for evidence expiring soon or already expired, and outputs
a formatted alert message suitable for delivery to messaging channels.

Usage:
    python3 evidence_expiry.py [--db-path PATH] [--days 30] [--format json|text]

Exit codes:
    0 = no alerts (all evidence current)
    1 = alerts present (expiring or expired evidence found)
    2 = error (DB not found, etc.)
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta


DEFAULT_DB = os.path.expanduser("~/.openclaw/grc/compliance.sqlite")


def get_db_connection(db_path):
    """Connect to the GRC database."""
    if not os.path.exists(db_path):
        print(json.dumps({
            "status": "error",
            "message": f"Database not found: {db_path}"
        }), file=sys.stderr)
        sys.exit(2)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def check_expiry(conn, days_threshold):
    """Check for expired and expiring evidence."""
    now = datetime.now()
    threshold_date = now + timedelta(days=days_threshold)

    # Expired evidence (valid_until < now)
    expired = conn.execute("""
        SELECT e.id, e.title, e.valid_until, e.status,
               GROUP_CONCAT(c.control_id, ', ') as linked_controls
        FROM evidence e
        LEFT JOIN evidence_controls ec ON e.id = ec.evidence_id
        LEFT JOIN controls c ON ec.control_id = c.id
        WHERE e.valid_until IS NOT NULL
          AND e.valid_until < ?
          AND e.status != 'expired'
        GROUP BY e.id
        ORDER BY e.valid_until ASC
    """, (now.strftime("%Y-%m-%d"),)).fetchall()

    # Expiring soon (now <= valid_until <= threshold)
    expiring = conn.execute("""
        SELECT e.id, e.title, e.valid_until, e.status,
               GROUP_CONCAT(c.control_id, ', ') as linked_controls
        FROM evidence e
        LEFT JOIN evidence_controls ec ON e.id = ec.evidence_id
        LEFT JOIN controls c ON ec.control_id = c.id
        WHERE e.valid_until IS NOT NULL
          AND e.valid_until >= ?
          AND e.valid_until <= ?
          AND e.status NOT IN ('expired', 'rejected')
        GROUP BY e.id
        ORDER BY e.valid_until ASC
    """, (now.strftime("%Y-%m-%d"), threshold_date.strftime("%Y-%m-%d"))).fetchall()

    return expired, expiring


def format_json(expired, expiring, days_threshold):
    """Format results as JSON."""
    result = {
        "status": "alerts" if (expired or expiring) else "ok",
        "checked_at": datetime.now().isoformat(),
        "threshold_days": days_threshold,
        "expired": [],
        "expiring_soon": []
    }

    for row in expired:
        days_past = (datetime.now() - datetime.strptime(row["valid_until"], "%Y-%m-%d")).days
        result["expired"].append({
            "id": row["id"],
            "title": row["title"],
            "valid_until": row["valid_until"],
            "days_overdue": days_past,
            "linked_controls": row["linked_controls"] or "none"
        })

    for row in expiring:
        days_left = (datetime.strptime(row["valid_until"], "%Y-%m-%d") - datetime.now()).days
        result["expiring_soon"].append({
            "id": row["id"],
            "title": row["title"],
            "valid_until": row["valid_until"],
            "days_remaining": max(0, days_left),
            "linked_controls": row["linked_controls"] or "none"
        })

    result["summary"] = {
        "expired_count": len(result["expired"]),
        "expiring_count": len(result["expiring_soon"]),
        "total_alerts": len(result["expired"]) + len(result["expiring_soon"])
    }

    return result


def format_text(expired, expiring, days_threshold):
    """Format results as human-readable text for messaging channels."""
    lines = []

    if not expired and not expiring:
        lines.append("All evidence is current. No expiry alerts.")
        return "\n".join(lines)

    lines.append(f"Evidence Expiry Alert ({datetime.now().strftime('%Y-%m-%d %H:%M')})")
    lines.append("=" * 50)

    if expired:
        lines.append(f"\nEXPIRED ({len(expired)} items):")
        for row in expired:
            days_past = (datetime.now() - datetime.strptime(row["valid_until"], "%Y-%m-%d")).days
            controls = row["linked_controls"] or "none"
            lines.append(f"  - {row['title']}")
            lines.append(f"    Expired: {row['valid_until']} ({days_past} days ago)")
            lines.append(f"    Controls: {controls}")

    if expiring:
        lines.append(f"\nEXPIRING SOON ({len(expiring)} items within {days_threshold} days):")
        for row in expiring:
            days_left = (datetime.strptime(row["valid_until"], "%Y-%m-%d") - datetime.now()).days
            controls = row["linked_controls"] or "none"
            urgency = "URGENT" if days_left <= 7 else "WARNING"
            lines.append(f"  [{urgency}] {row['title']}")
            lines.append(f"    Expires: {row['valid_until']} ({max(0, days_left)} days remaining)")
            lines.append(f"    Controls: {controls}")

    total = len(expired) + len(expiring)
    lines.append(f"\nTotal alerts: {total}")
    if expired:
        lines.append(f"Action required: {len(expired)} expired items need immediate renewal.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check for expiring/expired evidence")
    parser.add_argument("--db-path", default=DEFAULT_DB, help="Path to SQLite database")
    parser.add_argument("--days", type=int, default=30, help="Days threshold for expiring soon (default: 30)")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    args = parser.parse_args()

    conn = get_db_connection(args.db_path)

    try:
        expired, expiring = check_expiry(conn, args.days)

        if args.format == "json":
            result = format_json(expired, expiring, args.days)
            print(json.dumps(result, indent=2))
        else:
            print(format_text(expired, expiring, args.days))

        # Exit 1 if alerts found, 0 if clean
        if expired or expiring:
            sys.exit(1)
        else:
            sys.exit(0)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
