#!/usr/bin/env python3
"""ops-journal — Automated Ops Logging & Incident Timeline for OpenClaw.

A structured operational journal that captures deployments, incidents, changes,
and decisions. Creates a searchable ops log with incident timeline reconstruction
and automated postmortem generation.

No external dependencies — pure Python 3 stdlib.
"""

import argparse
import csv
import datetime
import io
import json
import os
import sqlite3
import sys
import textwrap

# --- Configuration ---

DEFAULT_BASE_DIR = os.path.expanduser("~/.openclaw/workspace/ops-journal")
DB_NAME = "journal.db"

CATEGORIES = ["deploy", "incident", "config", "maintenance", "security", "note"]
SEVERITIES = ["info", "warn", "high", "critical"]
INCIDENT_STATUSES = ["open", "resolved"]

CATEGORY_ICONS = {
    "deploy": "🚀",
    "incident": "🔥",
    "config": "⚙️",
    "maintenance": "🔧",
    "security": "🛡️",
    "note": "📝",
}

SEVERITY_COLORS = {
    "info": "\033[0;37m",      # white
    "warn": "\033[1;33m",      # yellow
    "high": "\033[0;31m",      # red
    "critical": "\033[1;31m",  # bright red
}

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


def get_base_dir():
    return os.environ.get("OPS_JOURNAL_DIR", DEFAULT_BASE_DIR)


def get_db_path():
    return os.path.join(get_base_dir(), DB_NAME)


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_since(since_str):
    """Parse relative time string like '7d', '2w', '1m' into a datetime."""
    if not since_str:
        return None
    unit = since_str[-1].lower()
    try:
        num = int(since_str[:-1])
    except ValueError:
        return None
    now = datetime.datetime.now(datetime.timezone.utc)
    if unit == "d":
        return now - datetime.timedelta(days=num)
    elif unit == "w":
        return now - datetime.timedelta(weeks=num)
    elif unit == "m":
        return now - datetime.timedelta(days=num * 30)
    return None


# --- Database ---

def init_db(db_path):
    """Create the journal database and tables."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'note',
            severity TEXT NOT NULL DEFAULT 'info',
            message TEXT NOT NULL,
            tags TEXT DEFAULT '',
            incident_id TEXT DEFAULT NULL,
            metadata TEXT DEFAULT '{}'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'high',
            status TEXT NOT NULL DEFAULT 'open',
            opened_at TEXT NOT NULL,
            resolved_at TEXT DEFAULT NULL,
            resolution TEXT DEFAULT NULL,
            duration_minutes INTEGER DEFAULT NULL,
            metadata TEXT DEFAULT '{}'
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_ts ON entries(timestamp)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_cat ON entries(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_sev ON entries(severity)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_incident ON entries(incident_id)")
    conn.commit()
    conn.close()


def get_conn():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        init_db(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def next_incident_id(conn):
    """Generate next incident ID like INC-001, INC-002, ..."""
    row = conn.execute("SELECT COUNT(*) as cnt FROM incidents").fetchone()
    num = (row["cnt"] or 0) + 1
    return f"INC-{num:03d}"


# --- Commands ---

def cmd_init(args):
    """Initialize journal database."""
    db_path = get_db_path()
    if os.path.exists(db_path) and not args.force:
        print(f"Journal already exists at {db_path}")
        print("Use --force to reinitialize (data is preserved).")
        return
    init_db(db_path)
    inc_dir = os.path.join(get_base_dir(), "incidents")
    os.makedirs(inc_dir, exist_ok=True)
    print(f"\033[0;32m✅\033[0m Journal initialized at {get_base_dir()}")


def cmd_log(args):
    """Create a journal entry."""
    if args.category and args.category not in CATEGORIES:
        print(f"Invalid category: {args.category}. Valid: {', '.join(CATEGORIES)}", file=sys.stderr)
        sys.exit(1)
    if args.severity and args.severity not in SEVERITIES:
        print(f"Invalid severity: {args.severity}. Valid: {', '.join(SEVERITIES)}", file=sys.stderr)
        sys.exit(1)

    category = args.category or "note"
    severity = args.severity or "info"
    tags = args.tags or ""
    message = " ".join(args.message)

    conn = get_conn()
    ts = now_iso()
    metadata = {}
    if args.incident:
        metadata["incident_ref"] = args.incident

    conn.execute(
        "INSERT INTO entries (timestamp, category, severity, message, tags, incident_id, metadata) VALUES (?,?,?,?,?,?,?)",
        (ts, category, severity, message, tags, args.incident, json.dumps(metadata))
    )
    conn.commit()
    entry_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    if args.json:
        print(json.dumps({
            "id": entry_id, "timestamp": ts, "category": category,
            "severity": severity, "message": message, "tags": tags,
        }))
    else:
        icon = CATEGORY_ICONS.get(category, "📋")
        color = SEVERITY_COLORS.get(severity, "")
        print(f"\033[0;32m✅\033[0m Logged #{entry_id}: {icon} {color}[{severity}]{RESET} {message}")


def cmd_incident(args):
    """Incident management."""
    sub = args.incident_action
    if sub == "open":
        cmd_incident_open(args)
    elif sub == "resolve":
        cmd_incident_resolve(args)
    elif sub == "list":
        cmd_incident_list(args)
    elif sub == "show":
        cmd_incident_show(args)
    else:
        print(f"Unknown incident action: {sub}", file=sys.stderr)
        sys.exit(1)


def cmd_incident_open(args):
    title = " ".join(args.title)
    severity = args.severity or "high"

    conn = get_conn()
    inc_id = next_incident_id(conn)
    ts = now_iso()

    conn.execute(
        "INSERT INTO incidents (id, title, severity, status, opened_at) VALUES (?,?,?,?,?)",
        (inc_id, title, severity, "open", ts)
    )
    # Auto-log the incident opening
    conn.execute(
        "INSERT INTO entries (timestamp, category, severity, message, tags, incident_id) VALUES (?,?,?,?,?,?)",
        (ts, "incident", severity, f"Incident opened: {title}", "incident-opened", inc_id)
    )
    conn.commit()

    # Write incident markdown file
    inc_dir = os.path.join(get_base_dir(), "incidents")
    os.makedirs(inc_dir, exist_ok=True)
    with open(os.path.join(inc_dir, f"{inc_id}.md"), "w") as f:
        f.write(f"# {inc_id} — {title}\n\n")
        f.write(f"- **Severity:** {severity}\n")
        f.write(f"- **Opened:** {ts}\n")
        f.write(f"- **Status:** OPEN\n\n")
        f.write("## Timeline\n\n")
        f.write(f"- `{ts}` — Incident opened\n")

    conn.close()

    if args.json:
        print(json.dumps({"id": inc_id, "title": title, "severity": severity, "opened_at": ts}))
    else:
        print(f"\033[0;31m🔥\033[0m Incident {BOLD}{inc_id}{RESET} opened: {title} [{severity}]")


def cmd_incident_resolve(args):
    inc_id = args.id.upper()
    resolution = " ".join(args.resolution) if args.resolution else "Resolved"

    conn = get_conn()
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (inc_id,)).fetchone()
    if not row:
        print(f"Incident {inc_id} not found.", file=sys.stderr)
        sys.exit(1)
    if row["status"] == "resolved":
        print(f"Incident {inc_id} is already resolved.", file=sys.stderr)
        sys.exit(1)

    ts = now_iso()
    opened = datetime.datetime.strptime(row["opened_at"], "%Y-%m-%dT%H:%M:%SZ")
    resolved = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
    duration = int((resolved - opened).total_seconds() / 60)

    conn.execute(
        "UPDATE incidents SET status='resolved', resolved_at=?, resolution=?, duration_minutes=? WHERE id=?",
        (ts, resolution, duration, inc_id)
    )
    conn.execute(
        "INSERT INTO entries (timestamp, category, severity, message, tags, incident_id) VALUES (?,?,?,?,?,?)",
        (ts, "incident", "info", f"Incident resolved: {resolution}", "incident-resolved", inc_id)
    )
    conn.commit()

    # Update incident markdown
    inc_file = os.path.join(get_base_dir(), "incidents", f"{inc_id}.md")
    if os.path.exists(inc_file):
        with open(inc_file, "a") as f:
            f.write(f"- `{ts}` — **Resolved:** {resolution}\n\n")
            f.write(f"## Resolution\n\n")
            f.write(f"- **Resolved at:** {ts}\n")
            f.write(f"- **Duration:** {duration} minutes\n")
            f.write(f"- **Root cause:** {resolution}\n")

    conn.close()

    if args.json:
        print(json.dumps({"id": inc_id, "resolved_at": ts, "duration_minutes": duration, "resolution": resolution}))
    else:
        print(f"\033[0;32m✅\033[0m Incident {BOLD}{inc_id}{RESET} resolved ({duration}m): {resolution}")


def cmd_incident_list(args):
    conn = get_conn()
    status_filter = args.status or "all"
    if status_filter == "all":
        rows = conn.execute("SELECT * FROM incidents ORDER BY opened_at DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM incidents WHERE status=? ORDER BY opened_at DESC", (status_filter,)).fetchall()
    conn.close()

    if not rows:
        print("No incidents found.")
        return

    if args.json:
        print(json.dumps([dict(r) for r in rows], indent=2))
        return

    print(f"\n{BOLD}═══ INCIDENTS ({len(rows)} total) ═══{RESET}\n")
    for r in rows:
        status_icon = "🔴" if r["status"] == "open" else "✅"
        sev_color = SEVERITY_COLORS.get(r["severity"], "")
        dur = f" ({r['duration_minutes']}m)" if r["duration_minutes"] else ""
        print(f"  {status_icon} {BOLD}{r['id']}{RESET} {sev_color}[{r['severity']}]{RESET} {r['title']}{dur}")
        print(f"     Opened: {r['opened_at']}  Status: {r['status']}")
        if r["resolution"]:
            print(f"     Resolution: {r['resolution']}")
        print()


def cmd_incident_show(args):
    inc_id = args.id.upper()
    conn = get_conn()
    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (inc_id,)).fetchone()
    if not row:
        print(f"Incident {inc_id} not found.", file=sys.stderr)
        sys.exit(1)

    entries = conn.execute(
        "SELECT * FROM entries WHERE incident_id = ? ORDER BY timestamp ASC", (inc_id,)
    ).fetchall()
    conn.close()

    if args.json:
        data = dict(row)
        data["timeline"] = [dict(e) for e in entries]
        print(json.dumps(data, indent=2))
        return

    sev_color = SEVERITY_COLORS.get(row["severity"], "")
    status_icon = "🔴 OPEN" if row["status"] == "open" else "✅ RESOLVED"
    print(f"\n{BOLD}═══ {row['id']} — {row['title']} ═══{RESET}")
    print(f"  Severity: {sev_color}{row['severity']}{RESET}")
    print(f"  Status:   {status_icon}")
    print(f"  Opened:   {row['opened_at']}")
    if row["resolved_at"]:
        print(f"  Resolved: {row['resolved_at']} ({row['duration_minutes']}m)")
    if row["resolution"]:
        print(f"  Resolution: {row['resolution']}")

    if entries:
        print(f"\n  {BOLD}Timeline:{RESET}")
        for e in entries:
            icon = CATEGORY_ICONS.get(e["category"], "📋")
            print(f"    {DIM}{e['timestamp']}{RESET} {icon} {e['message']}")
    print()


def cmd_search(args):
    """Search journal entries."""
    conn = get_conn()
    conditions = []
    params = []

    if args.query:
        query_str = " ".join(args.query)
        conditions.append("message LIKE ?")
        params.append(f"%{query_str}%")
    if args.category:
        conditions.append("category = ?")
        params.append(args.category)
    if args.severity:
        conditions.append("severity = ?")
        params.append(args.severity)
    if args.since:
        since_dt = parse_since(args.since)
        if since_dt:
            conditions.append("timestamp >= ?")
            params.append(since_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))

    where = " AND ".join(conditions) if conditions else "1=1"
    limit = args.limit or 50
    sql = f"SELECT * FROM entries WHERE {where} ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    if not rows:
        print("No entries found.")
        return

    if args.json:
        print(json.dumps([dict(r) for r in rows], indent=2))
        return

    print(f"\n{BOLD}═══ SEARCH RESULTS ({len(rows)} entries) ═══{RESET}\n")
    for r in rows:
        icon = CATEGORY_ICONS.get(r["category"], "📋")
        sev_color = SEVERITY_COLORS.get(r["severity"], "")
        tags = f" [{r['tags']}]" if r["tags"] else ""
        inc = f" → {r['incident_id']}" if r["incident_id"] else ""
        print(f"  {DIM}#{r['id']} {r['timestamp']}{RESET} {icon} {sev_color}[{r['severity']}]{RESET} {r['message']}{tags}{inc}")
    print()


def cmd_summary(args):
    """Generate period summary."""
    conn = get_conn()
    period = args.period or "day"

    now = datetime.datetime.now(datetime.timezone.utc)
    if period == "day":
        since = now - datetime.timedelta(days=1)
    elif period == "week":
        since = now - datetime.timedelta(weeks=1)
    elif period == "month":
        since = now - datetime.timedelta(days=30)
    else:
        since = now - datetime.timedelta(days=1)

    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Entry stats
    entries = conn.execute(
        "SELECT * FROM entries WHERE timestamp >= ? ORDER BY timestamp ASC", (since_str,)
    ).fetchall()

    cat_counts = {}
    sev_counts = {}
    for e in entries:
        cat_counts[e["category"]] = cat_counts.get(e["category"], 0) + 1
        sev_counts[e["severity"]] = sev_counts.get(e["severity"], 0) + 1

    # Incident stats
    incidents_opened = conn.execute(
        "SELECT COUNT(*) as cnt FROM incidents WHERE opened_at >= ?", (since_str,)
    ).fetchone()["cnt"]
    incidents_resolved = conn.execute(
        "SELECT COUNT(*) as cnt FROM incidents WHERE resolved_at >= ?", (since_str,)
    ).fetchone()["cnt"]
    incidents_open = conn.execute(
        "SELECT COUNT(*) as cnt FROM incidents WHERE status = 'open'"
    ).fetchone()["cnt"]

    avg_duration = conn.execute(
        "SELECT AVG(duration_minutes) as avg FROM incidents WHERE resolved_at >= ? AND duration_minutes IS NOT NULL",
        (since_str,)
    ).fetchone()["avg"]

    conn.close()

    summary = {
        "period": period,
        "since": since_str,
        "total_entries": len(entries),
        "by_category": cat_counts,
        "by_severity": sev_counts,
        "incidents_opened": incidents_opened,
        "incidents_resolved": incidents_resolved,
        "incidents_currently_open": incidents_open,
        "avg_resolution_minutes": round(avg_duration, 1) if avg_duration else None,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    print(f"\n{BOLD}═══ OPS JOURNAL — {period.upper()} SUMMARY ═══{RESET}")
    print(f"  Period: {since_str} → now")
    print(f"  Total entries: {BOLD}{len(entries)}{RESET}\n")

    if cat_counts:
        print(f"  {BOLD}By Category:{RESET}")
        for cat in CATEGORIES:
            if cat in cat_counts:
                icon = CATEGORY_ICONS.get(cat, "📋")
                print(f"    {icon} {cat}: {cat_counts[cat]}")
        print()

    if sev_counts:
        print(f"  {BOLD}By Severity:{RESET}")
        for sev in SEVERITIES:
            if sev in sev_counts:
                color = SEVERITY_COLORS.get(sev, "")
                print(f"    {color}{sev}{RESET}: {sev_counts[sev]}")
        print()

    print(f"  {BOLD}Incidents:{RESET}")
    print(f"    Opened:    {incidents_opened}")
    print(f"    Resolved:  {incidents_resolved}")
    print(f"    Currently open: {incidents_open}")
    if avg_duration:
        print(f"    Avg resolution: {avg_duration:.0f} minutes")
    print()

    # Recent notable entries (high/critical)
    notable = [e for e in entries if e["severity"] in ("high", "critical")]
    if notable:
        print(f"  {BOLD}Notable Events:{RESET}")
        for e in notable[-10:]:
            icon = CATEGORY_ICONS.get(e["category"], "📋")
            sev_color = SEVERITY_COLORS.get(e["severity"], "")
            print(f"    {DIM}{e['timestamp']}{RESET} {icon} {sev_color}[{e['severity']}]{RESET} {e['message']}")
        print()


def cmd_timeline(args):
    """Show incident timeline."""
    inc_id = args.id.upper()
    conn = get_conn()

    row = conn.execute("SELECT * FROM incidents WHERE id = ?", (inc_id,)).fetchone()
    if not row:
        print(f"Incident {inc_id} not found.", file=sys.stderr)
        sys.exit(1)

    entries = conn.execute(
        "SELECT * FROM entries WHERE incident_id = ? ORDER BY timestamp ASC", (inc_id,)
    ).fetchall()
    conn.close()

    if args.format == "json":
        data = dict(row)
        data["timeline"] = [dict(e) for e in entries]
        print(json.dumps(data, indent=2))
        return

    # Markdown format
    lines = []
    lines.append(f"# {row['id']} — {row['title']}")
    lines.append("")
    lines.append(f"| Field | Value |")
    lines.append(f"|-------|-------|")
    lines.append(f"| Severity | {row['severity']} |")
    lines.append(f"| Status | {row['status']} |")
    lines.append(f"| Opened | {row['opened_at']} |")
    if row["resolved_at"]:
        lines.append(f"| Resolved | {row['resolved_at']} |")
        lines.append(f"| Duration | {row['duration_minutes']} minutes |")
    if row["resolution"]:
        lines.append(f"| Resolution | {row['resolution']} |")
    lines.append("")
    lines.append("## Timeline")
    lines.append("")
    for e in entries:
        icon = CATEGORY_ICONS.get(e["category"], "📋")
        lines.append(f"- `{e['timestamp']}` {icon} **[{e['severity']}]** {e['message']}")
    lines.append("")

    output = "\n".join(lines)

    if args.format == "markdown":
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Timeline written to {args.output}")
        else:
            print(output)
    else:
        # Default: colored terminal
        sev_color = SEVERITY_COLORS.get(row["severity"], "")
        status_icon = "🔴 OPEN" if row["status"] == "open" else "✅ RESOLVED"
        print(f"\n{BOLD}═══ TIMELINE: {row['id']} — {row['title']} ═══{RESET}")
        print(f"  Severity: {sev_color}{row['severity']}{RESET} | Status: {status_icon}")
        print(f"  Opened: {row['opened_at']}")
        if row["resolved_at"]:
            print(f"  Resolved: {row['resolved_at']} ({row['duration_minutes']}m)")
        if row["resolution"]:
            print(f"  Resolution: {row['resolution']}")
        print(f"\n  {BOLD}Events:{RESET}")
        for e in entries:
            icon = CATEGORY_ICONS.get(e["category"], "📋")
            sev_c = SEVERITY_COLORS.get(e["severity"], "")
            print(f"    {DIM}{e['timestamp']}{RESET} {icon} {sev_c}[{e['severity']}]{RESET} {e['message']}")
        print()


def cmd_export(args):
    """Export journal entries."""
    conn = get_conn()
    conditions = []
    params = []

    if args.since:
        since_dt = parse_since(args.since)
        if since_dt:
            conditions.append("timestamp >= ?")
            params.append(since_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))

    where = " AND ".join(conditions) if conditions else "1=1"
    rows = conn.execute(f"SELECT * FROM entries WHERE {where} ORDER BY timestamp ASC", params).fetchall()
    conn.close()

    if not rows:
        print("No entries to export.")
        return

    fmt = args.format or "markdown"

    if fmt == "json":
        output = json.dumps([dict(r) for r in rows], indent=2)
    elif fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "timestamp", "category", "severity", "message", "tags", "incident_id"])
        for r in rows:
            writer.writerow([r["id"], r["timestamp"], r["category"], r["severity"], r["message"], r["tags"], r["incident_id"]])
        output = buf.getvalue()
    else:  # markdown
        lines = ["# Ops Journal Export", ""]
        lines.append(f"Entries: {len(rows)}")
        if args.since:
            lines.append(f"Since: {args.since}")
        lines.append("")
        lines.append("| # | Time | Cat | Sev | Message |")
        lines.append("|---|------|-----|-----|---------|")
        for r in rows:
            icon = CATEGORY_ICONS.get(r["category"], "📋")
            lines.append(f"| {r['id']} | {r['timestamp']} | {icon} {r['category']} | {r['severity']} | {r['message']} |")
        output = "\n".join(lines)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Exported {len(rows)} entries to {args.output}")
    else:
        print(output)


def cmd_stats(args):
    """Journal statistics."""
    conn = get_conn()

    total = conn.execute("SELECT COUNT(*) as cnt FROM entries").fetchone()["cnt"]
    total_incidents = conn.execute("SELECT COUNT(*) as cnt FROM incidents").fetchone()["cnt"]
    open_incidents = conn.execute("SELECT COUNT(*) as cnt FROM incidents WHERE status='open'").fetchone()["cnt"]

    first_entry = conn.execute("SELECT MIN(timestamp) as ts FROM entries").fetchone()["ts"]
    last_entry = conn.execute("SELECT MAX(timestamp) as ts FROM entries").fetchone()["ts"]

    cat_counts = {}
    for row in conn.execute("SELECT category, COUNT(*) as cnt FROM entries GROUP BY category"):
        cat_counts[row["category"]] = row["cnt"]

    sev_counts = {}
    for row in conn.execute("SELECT severity, COUNT(*) as cnt FROM entries GROUP BY severity"):
        sev_counts[row["severity"]] = row["cnt"]

    avg_dur = conn.execute(
        "SELECT AVG(duration_minutes) as avg FROM incidents WHERE duration_minutes IS NOT NULL"
    ).fetchone()["avg"]

    # Entries per day (last 30 days)
    thirty_days_ago = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent_count = conn.execute(
        "SELECT COUNT(*) as cnt FROM entries WHERE timestamp >= ?", (thirty_days_ago,)
    ).fetchone()["cnt"]
    daily_avg = recent_count / 30.0

    conn.close()

    if args.json:
        print(json.dumps({
            "total_entries": total,
            "total_incidents": total_incidents,
            "open_incidents": open_incidents,
            "first_entry": first_entry,
            "last_entry": last_entry,
            "by_category": cat_counts,
            "by_severity": sev_counts,
            "avg_resolution_minutes": round(avg_dur, 1) if avg_dur else None,
            "daily_average_30d": round(daily_avg, 1),
        }, indent=2))
        return

    print(f"\n{BOLD}═══ OPS JOURNAL STATISTICS ═══{RESET}\n")
    print(f"  Total entries:  {BOLD}{total}{RESET}")
    print(f"  Total incidents: {total_incidents} ({open_incidents} open)")
    print(f"  First entry:    {first_entry or 'N/A'}")
    print(f"  Last entry:     {last_entry or 'N/A'}")
    print(f"  Daily avg (30d): {daily_avg:.1f} entries/day")
    if avg_dur:
        print(f"  Avg resolution: {avg_dur:.0f} minutes")
    print()

    if cat_counts:
        print(f"  {BOLD}By Category:{RESET}")
        for cat in CATEGORIES:
            if cat in cat_counts:
                icon = CATEGORY_ICONS.get(cat, "📋")
                bar = "█" * min(cat_counts[cat], 40)
                print(f"    {icon} {cat:15s} {cat_counts[cat]:4d} {DIM}{bar}{RESET}")
        print()

    if sev_counts:
        print(f"  {BOLD}By Severity:{RESET}")
        for sev in SEVERITIES:
            if sev in sev_counts:
                color = SEVERITY_COLORS.get(sev, "")
                bar = "█" * min(sev_counts[sev], 40)
                print(f"    {color}{sev:10s}{RESET} {sev_counts[sev]:4d} {DIM}{bar}{RESET}")
        print()


# --- Argument Parser ---

def build_parser():
    parser = argparse.ArgumentParser(
        prog="journal.py",
        description="ops-journal — Automated Ops Logging & Incident Timeline for OpenClaw"
    )
    sub = parser.add_subparsers(dest="command", help="Command to run")

    # init
    p_init = sub.add_parser("init", help="Initialize journal database")
    p_init.add_argument("--force", action="store_true", help="Force reinitialize")

    # log
    p_log = sub.add_parser("log", help="Create a journal entry")
    p_log.add_argument("message", nargs="+", help="Log message")
    p_log.add_argument("-c", "--category", choices=CATEGORIES, help="Entry category")
    p_log.add_argument("-s", "--severity", choices=SEVERITIES, help="Severity level")
    p_log.add_argument("-t", "--tags", help="Comma-separated tags")
    p_log.add_argument("--incident", help="Link to incident ID")
    p_log.add_argument("--json", action="store_true", help="JSON output")

    # incident
    p_inc = sub.add_parser("incident", help="Incident management")
    inc_sub = p_inc.add_subparsers(dest="incident_action")

    p_inc_open = inc_sub.add_parser("open", help="Open a new incident")
    p_inc_open.add_argument("title", nargs="+", help="Incident title")
    p_inc_open.add_argument("-s", "--severity", choices=SEVERITIES, default="high", help="Severity")
    p_inc_open.add_argument("--json", action="store_true", help="JSON output")

    p_inc_resolve = inc_sub.add_parser("resolve", help="Resolve an incident")
    p_inc_resolve.add_argument("id", help="Incident ID (e.g. INC-001)")
    p_inc_resolve.add_argument("resolution", nargs="*", help="Resolution description")
    p_inc_resolve.add_argument("--json", action="store_true", help="JSON output")

    p_inc_list = inc_sub.add_parser("list", help="List incidents")
    p_inc_list.add_argument("--status", choices=["open", "resolved", "all"], default="all")
    p_inc_list.add_argument("--json", action="store_true", help="JSON output")

    p_inc_show = inc_sub.add_parser("show", help="Show incident details")
    p_inc_show.add_argument("id", help="Incident ID")
    p_inc_show.add_argument("--json", action="store_true", help="JSON output")

    # search
    p_search = sub.add_parser("search", help="Search journal entries")
    p_search.add_argument("query", nargs="*", help="Search text")
    p_search.add_argument("-c", "--category", choices=CATEGORIES, help="Filter by category")
    p_search.add_argument("-s", "--severity", choices=SEVERITIES, help="Filter by severity")
    p_search.add_argument("--since", help="Time window (e.g. 7d, 2w, 1m)")
    p_search.add_argument("--limit", type=int, default=50, help="Max results")
    p_search.add_argument("--json", action="store_true", help="JSON output")

    # summary
    p_summary = sub.add_parser("summary", help="Generate period summary")
    p_summary.add_argument("--period", choices=["day", "week", "month"], default="day")
    p_summary.add_argument("--json", action="store_true", help="JSON output")

    # timeline
    p_tl = sub.add_parser("timeline", help="Show incident timeline")
    p_tl.add_argument("id", help="Incident ID")
    p_tl.add_argument("--format", choices=["terminal", "markdown", "json"], default="terminal")
    p_tl.add_argument("--output", help="Output file path")

    # export
    p_export = sub.add_parser("export", help="Export journal entries")
    p_export.add_argument("--format", choices=["markdown", "json", "csv"], default="markdown")
    p_export.add_argument("--since", help="Time window (e.g. 7d, 2w, 1m)")
    p_export.add_argument("--output", help="Output file path")

    # stats
    p_stats = sub.add_parser("stats", help="Journal statistics")
    p_stats.add_argument("--period", choices=["week", "month", "all"], default="all")
    p_stats.add_argument("--json", action="store_true", help="JSON output")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmd_map = {
        "init": cmd_init,
        "log": cmd_log,
        "incident": cmd_incident,
        "search": cmd_search,
        "summary": cmd_summary,
        "timeline": cmd_timeline,
        "export": cmd_export,
        "stats": cmd_stats,
    }

    fn = cmd_map.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
