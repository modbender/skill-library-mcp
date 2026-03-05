#!/usr/bin/env python3
"""
Archive stale OpenClaw sessions from sessions.json to daily JSONL files.
Keeps sessions.json lean while preserving history for forensics.

Usage:
    python3 archive_sessions.py [--max-age-hours 48] [--archive-retention-days 30] [--sessions-path PATH] [--dry-run]
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path


def find_sessions_json():
    """Auto-detect sessions.json location."""
    candidates = [
        Path.home() / ".openclaw" / "agents" / "main" / "sessions" / "sessions.json",
        Path.home() / ".config" / "openclaw" / "agents" / "main" / "sessions" / "sessions.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def main():
    parser = argparse.ArgumentParser(description="Archive stale OpenClaw sessions")
    parser.add_argument("--max-age-hours", type=int, default=48, help="Archive sessions older than N hours (default: 48)")
    parser.add_argument("--archive-retention-days", type=int, default=30, help="Delete archive files older than N days (default: 30)")
    parser.add_argument("--sessions-path", type=str, default=None, help="Path to sessions.json (auto-detected if not set)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    args = parser.parse_args()

    # Find sessions.json
    if args.sessions_path:
        sessions_path = Path(args.sessions_path)
    else:
        sessions_path = find_sessions_json()

    if not sessions_path or not sessions_path.exists():
        print("ERROR: sessions.json not found. Use --sessions-path to specify location.")
        sys.exit(1)

    sessions_dir = sessions_path.parent
    archive_dir = sessions_dir / "sessions-archive"

    # Read sessions
    with open(sessions_path) as f:
        data = json.load(f)

    original_count = len(data)
    original_size = sessions_path.stat().st_size
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - (args.max_age_hours * 60 * 60 * 1000)

    # Partition into keep vs archive
    keep = {}
    archive = {}  # date_str -> list of (key, session)

    for key, sess in data.items():
        # Always keep main session
        if key == "agent:main:main":
            keep[key] = sess
            continue

        updated = sess.get("updatedAt", 0)
        if updated < cutoff_ms:
            # Archive this session, grouped by date
            if updated > 0:
                date_str = datetime.fromtimestamp(updated / 1000).strftime("%Y-%m-%d")
            else:
                date_str = "unknown"
            archive.setdefault(date_str, []).append((key, sess))
        else:
            keep[key] = sess

    archived_count = sum(len(v) for v in archive.values())

    if archived_count == 0:
        print("Nothing to archive.")
        return

    if args.dry_run:
        print(f"DRY RUN: Would archive {archived_count} sessions, keep {len(keep)}")
        for date_str, sessions in sorted(archive.items()):
            print(f"  {date_str}: {len(sessions)} sessions")
        return

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    # Write archive files
    for date_str, sessions in archive.items():
        archive_file = archive_dir / f"{date_str}.jsonl"
        with open(archive_file, "a") as f:
            for key, sess in sessions:
                entry = {"sessionKey": key, **sess}
                f.write(json.dumps(entry) + "\n")

    # Write cleaned sessions.json
    with open(sessions_path, "w") as f:
        json.dump(keep, f)

    new_size = sessions_path.stat().st_size

    # Rotate old archives
    retention_cutoff = datetime.now() - timedelta(days=args.archive_retention_days)
    rotated = 0
    if archive_dir.exists():
        for archive_file in archive_dir.glob("*.jsonl"):
            try:
                file_date = datetime.strptime(archive_file.stem, "%Y-%m-%d")
                if file_date < retention_cutoff:
                    archive_file.unlink()
                    rotated += 1
            except ValueError:
                continue

    # Report
    print(f"Archived: {archived_count} sessions")
    print(f"Remaining: {len(keep)} sessions")
    print(f"Size: {original_size / 1024 / 1024:.1f}MB → {new_size / 1024 / 1024:.1f}MB")
    if rotated:
        print(f"Rotated: {rotated} archive files older than {args.archive_retention_days} days")


if __name__ == "__main__":
    main()
