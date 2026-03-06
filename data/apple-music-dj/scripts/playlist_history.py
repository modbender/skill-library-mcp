#!/usr/bin/env python3
"""
playlist_history.py — Track created playlists to avoid recommending the same tracks.

Logs every playlist created by Apple Music DJ to ~/.apple-music-dj/playlist_history.json.
Provides utilities to check if tracks have been recently recommended.

Usage:
  python3 playlist_history.py log <name> <strategy> <track_ids_file>
  python3 playlist_history.py list [--limit N]
  python3 playlist_history.py check <track_id> [track_id ...]
  python3 playlist_history.py recent-tracks [--days N]

As a library:
  from playlist_history import log_playlist, get_recent_track_ids, load_history
"""

import sys

# Python version guard
if sys.version_info < (3, 9):
    sys.exit(
        f"ERROR: Python 3.9+ is required (you have "
        f"{sys.version_info.major}.{sys.version_info.minor}). Please upgrade."
    )

import argparse
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

HISTORY_FILE = Path.home() / ".apple-music-dj" / "playlist_history.json"


def load_history() -> list[dict]:
    """Load playlist history from disk."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_history(history: list[dict]) -> None:
    """Save playlist history to disk."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(HISTORY_FILE), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(history, f, indent=2)


def log_playlist(name: str, strategy: str, track_ids: list[str]) -> dict:
    """Log a newly created playlist to history. Returns the entry."""
    history = load_history()

    entry = {
        "name": name,
        "date": datetime.now(timezone.utc).isoformat(),
        "strategy": strategy,
        "track_ids": track_ids,
        "track_count": len(track_ids),
    }

    history.append(entry)

    # Keep last 200 entries to avoid unbounded growth
    if len(history) > 200:
        history = history[-200:]

    save_history(history)
    return entry


def get_recent_track_ids(days: int = 30) -> set[str]:
    """Get all track IDs used in playlists created in the last N days."""
    history = load_history()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    recent_ids: set[str] = set()

    for entry in history:
        try:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date >= cutoff:
                recent_ids.update(entry.get("track_ids", []))
        except (KeyError, ValueError):
            continue

    return recent_ids


def check_tracks(track_ids: list[str], days: int = 30) -> dict[str, bool]:
    """Check which track IDs were recently used. Returns {id: was_used}."""
    recent = get_recent_track_ids(days)
    return {tid: tid in recent for tid in track_ids}


# ── CLI ──────────────────────────────────────────────────────────

def cmd_log(args):
    """Log a playlist creation."""
    track_ids = []
    if args.track_ids_file:
        with open(args.track_ids_file, "r") as f:
            track_ids = [line.strip() for line in f if line.strip()]
    elif args.track_ids:
        track_ids = args.track_ids

    if not track_ids:
        print("ERROR: No track IDs provided.", file=sys.stderr)
        sys.exit(1)

    entry = log_playlist(args.name, args.strategy, track_ids)
    print(json.dumps(entry, indent=2))
    print(f"✅ Logged playlist '{args.name}' ({len(track_ids)} tracks).", file=sys.stderr)


def cmd_list(args):
    """List playlist history."""
    history = load_history()
    limit = args.limit or len(history)
    entries = history[-limit:]

    for entry in entries:
        date = entry.get("date", "?")[:10]
        name = entry.get("name", "?")
        strategy = entry.get("strategy", "?")
        count = entry.get("track_count", 0)
        print(f"  {date}  {strategy:15s}  {count:3d} tracks  {name}")

    print(f"\n{len(history)} total playlists logged.", file=sys.stderr)


def cmd_check(args):
    """Check if specific tracks were recently used."""
    results = check_tracks(args.track_ids, args.days)
    for tid, used in results.items():
        status = "♻️  recently used" if used else "✅ fresh"
        print(f"  {tid}  {status}")


def cmd_recent_tracks(args):
    """List all recently used track IDs."""
    recent = get_recent_track_ids(args.days)
    for tid in sorted(recent):
        print(tid)
    print(f"\n{len(recent)} unique tracks in last {args.days} days.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Apple Music DJ — Playlist History Tracker"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_log = sub.add_parser("log", help="Log a playlist creation")
    p_log.add_argument("name", help="Playlist name")
    p_log.add_argument("strategy", help="Strategy used (e.g., deep-cuts, mood, trend)")
    p_log.add_argument("track_ids_file", nargs="?", help="File with track IDs (one per line)")
    p_log.add_argument("--track-ids", nargs="*", help="Track IDs as arguments")
    p_log.set_defaults(func=cmd_log)

    p_list = sub.add_parser("list", help="List playlist history")
    p_list.add_argument("--limit", type=int, default=None, help="Show last N entries")
    p_list.set_defaults(func=cmd_list)

    p_check = sub.add_parser("check", help="Check if tracks were recently used")
    p_check.add_argument("track_ids", nargs="+", help="Track IDs to check")
    p_check.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")
    p_check.set_defaults(func=cmd_check)

    p_recent = sub.add_parser("recent-tracks", help="List all recently used track IDs")
    p_recent.add_argument("--days", type=int, default=30, help="Look back N days (default: 30)")
    p_recent.set_defaults(func=cmd_recent_tracks)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
