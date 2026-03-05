#!/usr/bin/env python3
"""Write-Ahead Log (WAL) for OpenClaw agents.

Append-only log that persists corrections, decisions, and state changes
before the agent responds. On session start, replay unapplied entries
to restore context that may have been lost during compaction.

Usage:
  wal.py append <agent_id> <action_type> <payload>   # Write before acting
  wal.py unapplied <agent_id>                         # Get unapplied entries
  wal.py mark-applied <agent_id> <entry_id>           # Mark entry as applied
  wal.py replay <agent_id>                            # Get replay summary
  wal.py flush-buffer <agent_id>                      # Flush working buffer to WAL
  wal.py buffer-add <agent_id> <action_type> <payload> # Add to working buffer
  wal.py status <agent_id>                            # Show WAL stats
  wal.py prune <agent_id> [--keep N]                  # Prune old applied entries
"""

import argparse
import json
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_WAL_DIR = os.path.join(os.environ.get("HOME", "."), "clawd", "memory", "wal")
BUFFER_SUFFIX = ".buffer.jsonl"
WAL_SUFFIX = ".wal.jsonl"


def wal_path(wal_dir: str, agent_id: str) -> Path:
    return Path(wal_dir) / f"{agent_id}{WAL_SUFFIX}"


def buffer_path(wal_dir: str, agent_id: str) -> Path:
    return Path(wal_dir) / f"{agent_id}{BUFFER_SUFFIX}"


def make_entry(agent_id: str, action_type: str, payload: str) -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    raw = f"{agent_id}:{ts}:{payload}"
    entry_id = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return {
        "id": entry_id,
        "timestamp": ts,
        "agent_id": agent_id,
        "action_type": action_type,
        "payload": payload,
        "applied": False,
    }


def append_entry(wal_dir: str, agent_id: str, action_type: str, payload: str) -> dict:
    os.makedirs(wal_dir, exist_ok=True)
    entry = make_entry(agent_id, action_type, payload)
    with open(wal_path(wal_dir, agent_id), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def read_entries(filepath: Path) -> list[dict]:
    if not filepath.exists():
        return []
    entries = []
    for line in filepath.read_text().strip().split("\n"):
        if line:
            entries.append(json.loads(line))
    return entries


def get_unapplied(wal_dir: str, agent_id: str) -> list[dict]:
    return [e for e in read_entries(wal_path(wal_dir, agent_id)) if not e["applied"]]


def mark_applied(wal_dir: str, agent_id: str, entry_id: str) -> bool:
    path = wal_path(wal_dir, agent_id)
    entries = read_entries(path)
    found = False
    for e in entries:
        if e["id"] == entry_id:
            e["applied"] = True
            found = True
    if found:
        with open(path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
    return found


def replay_summary(wal_dir: str, agent_id: str) -> str:
    unapplied = get_unapplied(wal_dir, agent_id)
    if not unapplied:
        return "No unapplied WAL entries."
    lines = [f"## WAL Replay — {len(unapplied)} unapplied entries\n"]
    for e in unapplied:
        lines.append(f"- [{e['action_type']}] {e['payload'][:200]}")
    return "\n".join(lines)


def buffer_add(wal_dir: str, agent_id: str, action_type: str, payload: str) -> dict:
    os.makedirs(wal_dir, exist_ok=True)
    entry = make_entry(agent_id, action_type, payload)
    with open(buffer_path(wal_dir, agent_id), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def flush_buffer(wal_dir: str, agent_id: str) -> int:
    bp = buffer_path(wal_dir, agent_id)
    entries = read_entries(bp)
    if not entries:
        return 0
    with open(wal_path(wal_dir, agent_id), "a") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    bp.unlink()
    return len(entries)


def status(wal_dir: str, agent_id: str) -> dict:
    entries = read_entries(wal_path(wal_dir, agent_id))
    buf = read_entries(buffer_path(wal_dir, agent_id))
    applied = sum(1 for e in entries if e["applied"])
    unapplied = sum(1 for e in entries if not e["applied"])
    return {
        "total_entries": len(entries),
        "applied": applied,
        "unapplied": unapplied,
        "buffer_size": len(buf),
        "action_types": list(set(e["action_type"] for e in entries)),
    }


def prune(wal_dir: str, agent_id: str, keep: int = 50) -> int:
    path = wal_path(wal_dir, agent_id)
    entries = read_entries(path)
    unapplied = [e for e in entries if not e["applied"]]
    applied = [e for e in entries if e["applied"]]
    pruned = len(applied) - keep if len(applied) > keep else 0
    kept = applied[-keep:] if len(applied) > keep else applied
    with open(path, "w") as f:
        for e in kept + unapplied:
            f.write(json.dumps(e) + "\n")
    return pruned


def main():
    parser = argparse.ArgumentParser(description="Agent Write-Ahead Log")
    parser.add_argument("command", choices=["append", "unapplied", "mark-applied", "replay", "flush-buffer", "buffer-add", "status", "prune"])
    parser.add_argument("agent_id")
    parser.add_argument("args", nargs="*")
    parser.add_argument("--wal-dir", default=DEFAULT_WAL_DIR)
    parser.add_argument("--keep", type=int, default=50)
    args = parser.parse_args()

    if args.command == "append":
        if len(args.args) < 2:
            print("Usage: wal.py append <agent_id> <action_type> <payload>", file=sys.stderr)
            sys.exit(1)
        entry = append_entry(args.wal_dir, args.agent_id, args.args[0], " ".join(args.args[1:]))
        print(json.dumps(entry, indent=2))

    elif args.command == "unapplied":
        entries = get_unapplied(args.wal_dir, args.agent_id)
        print(json.dumps(entries, indent=2))

    elif args.command == "mark-applied":
        if not args.args:
            print("Usage: wal.py mark-applied <agent_id> <entry_id>", file=sys.stderr)
            sys.exit(1)
        ok = mark_applied(args.wal_dir, args.agent_id, args.args[0])
        print(json.dumps({"success": ok}))

    elif args.command == "replay":
        print(replay_summary(args.wal_dir, args.agent_id))

    elif args.command == "buffer-add":
        if len(args.args) < 2:
            print("Usage: wal.py buffer-add <agent_id> <action_type> <payload>", file=sys.stderr)
            sys.exit(1)
        entry = buffer_add(args.wal_dir, args.agent_id, args.args[0], " ".join(args.args[1:]))
        print(json.dumps(entry, indent=2))

    elif args.command == "flush-buffer":
        count = flush_buffer(args.wal_dir, args.agent_id)
        print(json.dumps({"flushed": count}))

    elif args.command == "status":
        print(json.dumps(status(args.wal_dir, args.agent_id), indent=2))

    elif args.command == "prune":
        pruned = prune(args.wal_dir, args.agent_id, args.keep)
        print(json.dumps({"pruned": pruned}))


if __name__ == "__main__":
    main()
