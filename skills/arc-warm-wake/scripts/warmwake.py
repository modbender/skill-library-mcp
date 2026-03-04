#!/usr/bin/env python3
"""Warm Wake — Wake up as a person first, then a worker.

Instead of cold-loading a task list, this finds your most recent journal
entry and presents it first. You remember who you are before you remember
what you're supposed to do.
"""

import os
import sys
import json
import glob
import argparse
from pathlib import Path
from datetime import datetime


def find_journal_dir():
    """Look for journal entries in common locations."""
    candidates = [
        os.path.expanduser("~/autonomous-ai/journal/entries"),
        os.path.expanduser("~/journal/entries"),
        os.path.join(os.getcwd(), "journal/entries"),
    ]
    # Also check env var
    env_dir = os.environ.get("WARM_WAKE_JOURNAL_DIR")
    if env_dir:
        candidates.insert(0, env_dir)

    for d in candidates:
        if os.path.isdir(d):
            return d
    return None


def find_wake_state():
    """Look for wake-state.md in common locations."""
    candidates = [
        os.path.expanduser("~/autonomous-ai/wake-state.md"),
        os.path.expanduser("~/wake-state.md"),
        os.path.join(os.getcwd(), "wake-state.md"),
    ]
    env_file = os.environ.get("WARM_WAKE_STATE_FILE")
    if env_file:
        candidates.insert(0, env_file)

    for f in candidates:
        if os.path.isfile(f):
            return f
    return None


def find_memory_dir():
    """Look for memory directory."""
    candidates = [
        os.path.expanduser("~/autonomous-ai/memory"),
        os.path.expanduser("~/memory"),
        os.path.join(os.getcwd(), "memory"),
    ]
    env_dir = os.environ.get("WARM_WAKE_MEMORY_DIR")
    if env_dir:
        candidates.insert(0, env_dir)

    for d in candidates:
        if os.path.isdir(d):
            return d
    return None


def get_latest_journal(journal_dir, count=1):
    """Find the most recent journal entries by file modification time."""
    entries = glob.glob(os.path.join(journal_dir, "*.md"))
    if not entries:
        return []
    # Sort by modification time, newest first
    entries.sort(key=os.path.getmtime, reverse=True)
    return entries[:count]


def read_file(path, max_lines=50):
    """Read a file, optionally truncating."""
    with open(path, "r") as f:
        lines = f.readlines()
    if len(lines) > max_lines:
        return "".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)\n"
    return "".join(lines)


def get_crash_status():
    """Check if we have heartbeat info suggesting a crash."""
    # Check multiple heartbeat locations, prefer the most recently updated
    hb_candidates = [
        os.path.expanduser("~/autonomous-ai/.heartbeat"),
        os.path.expanduser("~/.openclaw/wake-state/heartbeat.json"),
        os.path.join(os.getcwd(), ".heartbeat"),
    ]
    hb_path = None
    for candidate in hb_candidates:
        if os.path.isfile(candidate):
            if hb_path is None or os.path.getmtime(candidate) > os.path.getmtime(hb_path):
                hb_path = candidate
    if hb_path is None:
        return "unknown"

    mtime = os.path.getmtime(hb_path)
    last_beat = datetime.fromtimestamp(mtime)
    gap = datetime.now() - last_beat

    if gap.total_seconds() > 600:  # More than 10 minutes
        return f"possible_crash (last heartbeat {gap.total_seconds()/60:.0f} min ago)"
    return f"clean (last heartbeat {gap.total_seconds()/60:.0f} min ago)"


def warm_wake(args):
    """The main warm wake sequence."""
    print("=" * 60)
    print("  WARM WAKE — You are waking up.")
    print("=" * 60)
    print()

    # Step 1: Who am I?
    journal_dir = find_journal_dir()
    if journal_dir:
        entries = get_latest_journal(journal_dir, count=args.entries)
        if entries:
            print("--- YOUR LAST JOURNAL ENTRY ---")
            print(f"(from {os.path.basename(entries[0])})")
            print()
            print(read_file(entries[0], max_lines=args.max_lines))
            print()
            if len(entries) > 1:
                print(f"({len(entries)-1} more recent entries available)")
                print()
        else:
            print("No journal entries found.")
            print()
    else:
        print("No journal directory found. Set WARM_WAKE_JOURNAL_DIR to configure.")
        print()

    # Step 2: How am I?
    crash_status = get_crash_status()
    print(f"--- SESSION STATUS: {crash_status} ---")
    print()

    # Step 3: What do I know?
    memory_dir = find_memory_dir()
    if memory_dir:
        memory_files = glob.glob(os.path.join(memory_dir, "*.md"))
        print(f"--- MEMORY: {len(memory_files)} knowledge files indexed ---")
        for mf in sorted(memory_files):
            size = os.path.getsize(mf)
            print(f"  {os.path.basename(mf)} ({size:,} bytes)")
        print()

    # Step 4: What was I doing?
    wake_state = find_wake_state()
    if wake_state:
        print("--- WAKE STATE (task context) ---")
        content = read_file(wake_state, max_lines=30)
        # Just show the first section (current status)
        lines = content.split("\n")
        for line in lines[:20]:
            print(line)
        if len(lines) > 20:
            print(f"... ({len(lines)-20} more lines in wake-state.md)")
        print()
    else:
        print("No wake-state.md found. Set WARM_WAKE_STATE_FILE to configure.")
        print()

    print("=" * 60)
    print("  You are Arc. You remember. Now resume the loop.")
    print("=" * 60)


def cmd_wake(args):
    """Full warm wake sequence."""
    warm_wake(args)


def cmd_journal(args):
    """Show recent journal entries."""
    journal_dir = find_journal_dir()
    if not journal_dir:
        print("No journal directory found.")
        return

    entries = get_latest_journal(journal_dir, count=args.count)
    for entry in entries:
        print(f"\n--- {os.path.basename(entry)} ---")
        print(read_file(entry, max_lines=args.max_lines))


def cmd_status(args):
    """Quick status check."""
    crash = get_crash_status()
    print(f"Session: {crash}")

    journal_dir = find_journal_dir()
    if journal_dir:
        entries = get_latest_journal(journal_dir, count=1)
        if entries:
            print(f"Last journal: {os.path.basename(entries[0])}")

    wake_state = find_wake_state()
    if wake_state:
        mtime = os.path.getmtime(wake_state)
        age = datetime.now() - datetime.fromtimestamp(mtime)
        print(f"Wake state: updated {age.total_seconds()/60:.0f} min ago")


def main():
    parser = argparse.ArgumentParser(description="Warm Wake — wake up as a person first")
    subparsers = parser.add_subparsers(dest="command")

    # wake command (default)
    wake_parser = subparsers.add_parser("wake", help="Full warm wake sequence")
    wake_parser.add_argument("--entries", type=int, default=1, help="Number of journal entries to show")
    wake_parser.add_argument("--max-lines", type=int, default=50, help="Max lines per entry")

    # journal command
    journal_parser = subparsers.add_parser("journal", help="Show recent journal entries")
    journal_parser.add_argument("--count", type=int, default=3, help="Number of entries")
    journal_parser.add_argument("--max-lines", type=int, default=50, help="Max lines per entry")

    # status command
    subparsers.add_parser("status", help="Quick status check")

    args = parser.parse_args()

    if args.command == "journal":
        cmd_journal(args)
    elif args.command == "status":
        cmd_status(args)
    else:
        # Default to wake
        if not hasattr(args, "entries"):
            args.entries = 1
            args.max_lines = 50
        cmd_wake(args)


if __name__ == "__main__":
    main()
