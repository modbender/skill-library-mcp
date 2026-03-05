#!/usr/bin/env python3
"""
Loxone State Watcher

Monitor real-time state changes from the Loxone Miniserver via WebSocket.
Outputs human-readable change events, optionally filtered by room or control.

Usage:
    # Watch everything (all rooms, all controls)
    python3 loxone_watch.py

    # Watch a specific room
    python3 loxone_watch.py --room "Office"

    # Watch a specific control
    python3 loxone_watch.py --control "Light in Office"

    # Watch multiple rooms
    python3 loxone_watch.py --room "Office" --room "Kids Room"

    # Limit duration (seconds, default=0=forever)
    python3 loxone_watch.py --room "Office" --duration 300

    # JSON output (for piping/processing)
    python3 loxone_watch.py --room "Office" --json

    # Filter by state key (e.g., only temperature changes)
    python3 loxone_watch.py --state-key "tempActual"

    # Quiet mode: only show changes, no initial state dump
    python3 loxone_watch.py --room "Office" --changes-only

Examples:
    # "Notify me when someone changes the office lights"
    python3 loxone_watch.py --control "Light in Office" --changes-only

    # "Monitor temperatures in the whole house"
    python3 loxone_watch.py --state-key "tempActual"

    # "Watch motion in the kids room"
    python3 loxone_watch.py --room "Kids Room" --state-key "active"

    # "Track all activity in Guest Room and Office"
    python3 loxone_watch.py --room "Guest Room" --room "Office"
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
import base64

from loxone_client import LoxoneClient

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))
from loxone_ws import LoxoneWS
from loxone_config import load_config_file


def load_config():
    """Load Loxone connection config (supports Cloud DNS shorthand)."""
    config_path = Path(__file__).parent.parent / "config.json"
    return load_config_file(str(config_path))


def download_structure(host: str, username: str, password: str, *, use_https: bool) -> str:
    """Download LoxAPP3.json from Miniserver, return path.

    Uses the same transport settings as the client (HTTPS by default).
    """
    cache = Path(__file__).parent.parent / ".cache"
    cache.mkdir(exist_ok=True)
    out = cache / "LoxAPP3.json"

    # Re-download if older than 1 hour
    if out.exists() and (time.time() - out.stat().st_mtime) < 3600:
        return str(out)

    client = LoxoneClient(host, username, password, use_https=use_https)
    client.fetch_structure(cache_file=str(out))
    return str(out)


# ── Mood name resolver ─────────────────────────────────────────

KNOWN_MOODS = {778: "Off"}


def resolve_mood(value, control_uuid: str, structure_path: str) -> str:
    """Try to resolve a mood ID to a name from the structure file."""
    mid = int(value)
    if mid in KNOWN_MOODS:
        return KNOWN_MOODS[mid]

    # Mood names aren't in LoxAPP3.json sadly, but IDs are sequential
    # For now return the numeric ID
    return str(mid)


# ── Output formatters ──────────────────────────────────────────

class HumanFormatter:
    def __init__(self, changes_only: bool = False):
        self.changes_only = changes_only

    def initial(self, uuid, name, value):
        if self.changes_only:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"📍 {ts} {name}: {value}")

    def changed(self, uuid, name, old, new):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"⚡ {ts} {name}: {old} → {new}")


class JsonFormatter:
    def __init__(self, changes_only: bool = False):
        self.changes_only = changes_only

    def initial(self, uuid, name, value):
        if self.changes_only:
            return
        print(json.dumps({
            "event": "initial",
            "ts": datetime.now().isoformat(),
            "uuid": uuid,
            "name": name,
            "value": value,
        }))

    def changed(self, uuid, name, old, new):
        print(json.dumps({
            "event": "change",
            "ts": datetime.now().isoformat(),
            "uuid": uuid,
            "name": name,
            "old": old,
            "new": new,
        }))


# ── State key filter wrapper ───────────────────────────────────

class StateKeyFilter:
    """Wraps a formatter and only passes through matching state keys."""

    def __init__(self, formatter, ws: LoxoneWS, state_keys: list):
        self.formatter = formatter
        self.ws = ws
        self.state_keys = [k.lower() for k in state_keys]

    def _matches(self, uuid):
        meta = self.ws.uuid_meta.get(uuid, {})
        sk = meta.get("state_key", "").lower()
        return any(k in sk for k in self.state_keys)

    def initial(self, uuid, name, value):
        if self._matches(uuid):
            self.formatter.initial(uuid, name, value)

    def changed(self, uuid, name, old, new):
        if self._matches(uuid):
            self.formatter.changed(uuid, name, old, new)


# ── Main ───────────────────────────────────────────────────────

async def run(args):
    sys.stdout.reconfigure(line_buffering=True)

    config = load_config()
    host = config["host"]
    user = config["username"]
    passwd = config["password"]

    use_https = bool(config.get("use_https", True))

    # Download/cache structure
    structure_path = download_structure(host, user, passwd, use_https=use_https)

    # Create WebSocket client
    ws = LoxoneWS(host, user, passwd, use_https=use_https)
    ws.load_structure(structure_path)

    # Apply filters
    if args.room:
        for room in args.room:
            ws.watch_room(room)
    if args.control:
        for ctrl in args.control:
            ws.watch_control(ctrl)

    # Setup formatter
    if args.json:
        fmt = JsonFormatter(changes_only=args.changes_only)
    else:
        fmt = HumanFormatter(changes_only=args.changes_only)

    # Wrap with state key filter if needed
    if args.state_key:
        fmt = StateKeyFilter(fmt, ws, args.state_key)

    # Wire callbacks
    ws.on_initial_state = lambda uuid, name, value: fmt.initial(uuid, name, value)
    ws.on_state_change = lambda uuid, name, old, new: fmt.changed(uuid, name, old, new)

    # Summary
    if not args.json:
        filters = []
        if args.room:
            filters.append(f"rooms: {', '.join(args.room)}")
        if args.control:
            filters.append(f"controls: {', '.join(args.control)}")
        if args.state_key:
            filters.append(f"states: {', '.join(args.state_key)}")
        filter_str = f" ({'; '.join(filters)})" if filters else " (all)"
        dur = f" for {args.duration}s" if args.duration else ""
        print(f"👁️ Watching Loxone{filter_str}{dur}")
        if ws._watch_uuids:
            print(f"   Monitoring {len(ws._watch_uuids)} state UUIDs")
        print()

    # Connect and listen
    await ws.connect()
    if not args.json:
        print("🔌 Connected\n")

    try:
        await ws.listen(duration=args.duration)
    except KeyboardInterrupt:
        pass
    finally:
        await ws.disconnect()
        if not args.json:
            print("\n🔌 Done")


def main():
    parser = argparse.ArgumentParser(
        description="Watch real-time Loxone state changes via WebSocket",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --room "Office"                    Watch all Office changes
  %(prog)s --control "Light in Office"        Watch office light only
  %(prog)s --state-key tempActual             All temperature changes
  %(prog)s --room "Office" --changes-only     Only show changes, skip initial
  %(prog)s --room "Office" --json             JSON output for processing
  %(prog)s --duration 60                      Watch for 60 seconds
        """,
    )
    parser.add_argument("--room", action="append", help="Filter by room name (repeatable)")
    parser.add_argument("--control", action="append", help="Filter by control name (repeatable)")
    parser.add_argument("--state-key", action="append", help="Filter by state key (repeatable)")
    parser.add_argument("--duration", type=float, default=0, help="Watch duration in seconds (0=forever)")
    parser.add_argument("--json", action="store_true", help="JSON output (one object per line)")
    parser.add_argument("--changes-only", action="store_true", help="Skip initial state dump")
    args = parser.parse_args()

    asyncio.run(run(args))


if __name__ == "__main__":
    main()
