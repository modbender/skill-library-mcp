#!/usr/bin/env python3
"""
Audit logger for email sanitization checks.

Appends JSONL entries to audit-log.jsonl with monthly rotation.
"""

import json
import os
import sys
from datetime import datetime, timezone

LOG_DIR = os.path.dirname(os.path.abspath(__file__))


def _log_path() -> str:
    """Return current month's log file path."""
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return os.path.join(LOG_DIR, f"audit-log-{month}.jsonl")


def log_check(
    emails_checked: int = 0,
    suspicious_count: int = 0,
    flags_found: list[str] | None = None,
    actions_taken: str = "none",
    check_type: str = "email",
    items_checked: int = 0,
) -> None:
    """Append an audit entry. Works for both email and calendar checks."""
    count = items_checked or emails_checked
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "check_type": check_type,
        "items_checked": count,
        "suspicious_count": suspicious_count,
        "flags_found": flags_found or [],
        "actions_taken": actions_taken,
    }
    path = _log_path()
    with open(path, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    """CLI: pipe sanitizer JSON output to log summary."""
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Invalid JSON", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, dict):
        data = [data]

    total = len(data)
    suspicious = sum(1 for e in data if e.get("suspicious"))
    all_flags = []
    for e in data:
        all_flags.extend(e.get("flags", []))

    log_check(total, suspicious, list(set(all_flags)))
    print(f"Logged: {total} emails, {suspicious} suspicious", file=sys.stderr)


if __name__ == "__main__":
    main()
