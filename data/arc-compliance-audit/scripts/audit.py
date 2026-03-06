#!/usr/bin/env python3
"""Compliance Audit Trail for autonomous agents.

Immutable, hash-chained audit logging with integrity verification.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIT_DIR = Path.home() / ".openclaw" / "audit"


def ensure_dir():
    """Create audit directory if it doesn't exist."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def get_today_file():
    """Get the audit log file for today."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return AUDIT_DIR / f"audit-{today}.json"


def load_entries(filepath):
    """Load entries from a single audit file."""
    if not filepath.exists():
        return []
    with open(filepath) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_entries(filepath, entries):
    """Save entries to an audit file."""
    with open(filepath, "w") as f:
        json.dump(entries, f, indent=2)


def compute_hash(prev_hash, entry_data):
    """Compute the SHA-256 hash for a new entry."""
    payload = prev_hash + json.dumps(entry_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_last_hash():
    """Get the hash of the most recent entry across all files."""
    files = sorted(AUDIT_DIR.glob("audit-*.json"), reverse=True)
    for f in files:
        entries = load_entries(f)
        if entries:
            return entries[-1].get("hash", "genesis")
    return "genesis"


def get_next_sequence():
    """Get the next sequence number."""
    files = sorted(AUDIT_DIR.glob("audit-*.json"), reverse=True)
    for f in files:
        entries = load_entries(f)
        if entries:
            return entries[-1].get("sequence", 0) + 1
    return 1


def log_entry(action, details, agent="arc"):
    """Create a new audit log entry."""
    ensure_dir()

    prev_hash = get_last_hash()
    sequence = get_next_sequence()
    timestamp = datetime.now(timezone.utc).isoformat()

    entry_data = {
        "timestamp": timestamp,
        "sequence": sequence,
        "action": action,
        "agent": agent,
        "details": details,
    }

    entry_hash = compute_hash(prev_hash, entry_data)
    entry_data["hash"] = entry_hash
    entry_data["prev_hash"] = prev_hash

    filepath = get_today_file()
    entries = load_entries(filepath)
    entries.append(entry_data)
    save_entries(filepath, entries)

    return entry_data


def load_all_entries():
    """Load all entries from all audit files, in order."""
    ensure_dir()
    all_entries = []
    for f in sorted(AUDIT_DIR.glob("audit-*.json")):
        all_entries.extend(load_entries(f))
    return all_entries


def verify_chain():
    """Verify the integrity of the entire audit chain."""
    entries = load_all_entries()
    if not entries:
        print("No entries to verify.")
        return True

    errors = []
    prev_hash = "genesis"

    for i, entry in enumerate(entries):
        # Reconstruct entry data (without hash and prev_hash)
        entry_data = {
            "timestamp": entry["timestamp"],
            "sequence": entry["sequence"],
            "action": entry["action"],
            "agent": entry["agent"],
            "details": entry["details"],
        }

        expected_hash = compute_hash(prev_hash, entry_data)

        if entry.get("hash") != expected_hash:
            errors.append({
                "sequence": entry.get("sequence", i),
                "expected_hash": expected_hash[:16] + "...",
                "actual_hash": entry.get("hash", "missing")[:16] + "...",
                "timestamp": entry.get("timestamp", "?"),
            })

        if entry.get("prev_hash") != prev_hash:
            errors.append({
                "sequence": entry.get("sequence", i),
                "issue": "prev_hash mismatch",
                "expected": prev_hash[:16] + "...",
                "actual": entry.get("prev_hash", "missing")[:16] + "...",
            })

        prev_hash = entry.get("hash", "")

    if errors:
        print(f"INTEGRITY FAILURE: {len(errors)} issue(s) found")
        for e in errors:
            print(f"  Sequence {e['sequence']}: {json.dumps(e)}")
        return False
    else:
        print(f"VERIFIED: {len(entries)} entries, chain intact.")
        return True


def view_entries(last=None, action=None, since=None, until=None, agent=None):
    """View filtered audit entries."""
    entries = load_all_entries()

    if action:
        entries = [e for e in entries if e.get("action") == action]

    if agent:
        entries = [e for e in entries if e.get("agent") == agent]

    if since:
        entries = [e for e in entries if e.get("timestamp", "") >= since]

    if until:
        entries = [e for e in entries if e.get("timestamp", "") <= until]

    if last:
        entries = entries[-last:]

    for entry in entries:
        ts = entry.get("timestamp", "?")[:19]
        seq = entry.get("sequence", "?")
        act = entry.get("action", "?")
        ag = entry.get("agent", "?")
        details = json.dumps(entry.get("details", {}))
        if len(details) > 120:
            details = details[:117] + "..."
        print(f"[{seq}] {ts} | {ag} | {act} | {details}")


def export_entries(fmt="json"):
    """Export all entries in JSON or CSV format."""
    entries = load_all_entries()

    if fmt == "json":
        print(json.dumps(entries, indent=2))
    elif fmt == "csv":
        if not entries:
            return
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["sequence", "timestamp", "agent", "action", "details", "hash"])
        for e in entries:
            writer.writerow([
                e.get("sequence", ""),
                e.get("timestamp", ""),
                e.get("agent", ""),
                e.get("action", ""),
                json.dumps(e.get("details", {})),
                e.get("hash", ""),
            ])
        print(output.getvalue())


def summary(period="day"):
    """Generate a compliance summary."""
    entries = load_all_entries()
    if not entries:
        print("No entries found.")
        return

    now = datetime.now(timezone.utc)
    if period == "day":
        cutoff = now.isoformat()[:10]
        filtered = [e for e in entries if e.get("timestamp", "")[:10] == cutoff]
        label = f"Today ({cutoff})"
    elif period == "week":
        from datetime import timedelta
        cutoff = (now - timedelta(days=7)).isoformat()
        filtered = [e for e in entries if e.get("timestamp", "") >= cutoff]
        label = "Last 7 days"
    else:
        filtered = entries
        label = "All time"

    # Count by action type
    by_action = {}
    by_agent = {}
    for e in filtered:
        act = e.get("action", "unknown")
        ag = e.get("agent", "unknown")
        by_action[act] = by_action.get(act, 0) + 1
        by_agent[ag] = by_agent.get(ag, 0) + 1

    print(f"Compliance Summary — {label}")
    print(f"Total entries: {len(filtered)}")
    print()

    if by_action:
        print("By action type:")
        for act, count in sorted(by_action.items(), key=lambda x: -x[1]):
            print(f"  {act}: {count}")
        print()

    if by_agent:
        print("By agent:")
        for ag, count in sorted(by_agent.items(), key=lambda x: -x[1]):
            print(f"  {ag}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Compliance Audit Trail")
    sub = parser.add_subparsers(dest="command")

    # Log command
    p_log = sub.add_parser("log", help="Log an audit entry")
    p_log.add_argument("--action", required=True, help="Action type (skill_executed, decision, data_access, budget_change, error)")
    p_log.add_argument("--details", required=True, help="JSON details string")
    p_log.add_argument("--agent", default="arc", help="Agent name")

    # View command
    p_view = sub.add_parser("view", help="View audit entries")
    p_view.add_argument("--last", type=int, help="Show last N entries")
    p_view.add_argument("--action", help="Filter by action type")
    p_view.add_argument("--agent", help="Filter by agent name")
    p_view.add_argument("--since", help="Start timestamp (ISO 8601)")
    p_view.add_argument("--until", help="End timestamp (ISO 8601)")

    # Verify command
    sub.add_parser("verify", help="Verify audit trail integrity")

    # Export command
    p_export = sub.add_parser("export", help="Export audit trail")
    p_export.add_argument("--format", choices=["json", "csv"], default="json")

    # Summary command
    p_summary = sub.add_parser("summary", help="Generate compliance summary")
    p_summary.add_argument("--period", choices=["day", "week", "all"], default="day")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "log":
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError:
            details = {"raw": args.details}
        entry = log_entry(args.action, details, args.agent)
        print(f"Logged: [{entry['sequence']}] {entry['action']} | hash: {entry['hash'][:16]}...")

    elif args.command == "view":
        view_entries(last=args.last, action=args.action, since=args.since, until=args.until, agent=args.agent)

    elif args.command == "verify":
        success = verify_chain()
        sys.exit(0 if success else 1)

    elif args.command == "export":
        export_entries(args.format)

    elif args.command == "summary":
        summary(args.period)


if __name__ == "__main__":
    main()
