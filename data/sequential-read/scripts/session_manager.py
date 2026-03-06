#!/usr/bin/env python3
"""
Manage sequential_read sessions — create, list, get, update.
All session data lives under <workspace>/memory/sequential_read/<session-id>/.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_workspace():
    """Resolve the workspace root directory."""
    ws = os.environ.get("OPENCLAW_WORKSPACE")
    if ws:
        return Path(ws)
    return Path.home() / ".openclaw" / "workspace"


def get_sessions_root():
    return get_workspace() / "memory" / "sequential_read"


def make_session_id(source_file):
    """Generate a session-id from the source filename + current date."""
    name = Path(source_file).stem
    # Sanitise: lowercase, replace non-alphanum with hyphens, collapse runs
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"{slug}-{date}"


def find_existing_session(source_file):
    """Find an existing session for the same source filename (basename match)."""
    root = get_sessions_root()
    if not root.exists():
        return None
    target_name = Path(source_file).name
    for session_dir in sorted(root.iterdir(), reverse=True):
        meta_path = session_dir / "session.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                existing_name = Path(meta.get("source_file", "")).name
                if existing_name == target_name and meta.get("status") != "complete":
                    return meta["session_id"]
            except (json.JSONDecodeError, KeyError):
                continue
    return None


# ── Subcommands ──────────────────────────────────────────────────────

def cmd_create(args):
    source = Path(args.source_file)
    if not source.exists():
        print(f"Error: source file not found: {source}", file=sys.stderr)
        sys.exit(1)
    if not source.is_file():
        print(f"Error: not a regular file: {source}", file=sys.stderr)
        sys.exit(1)

    # Check for resumable session
    existing = find_existing_session(str(source))
    if existing:
        sess_dir = get_sessions_root() / existing
        meta = json.loads((sess_dir / "session.json").read_text(encoding="utf-8"))
        print(f"Existing session found: {existing} (status: {meta['status']})")
        print(str(sess_dir))
        return

    session_id = make_session_id(str(source))

    # Handle collision (same file re-read on same day)
    root = get_sessions_root()
    candidate = session_id
    counter = 2
    while (root / candidate).exists():
        candidate = f"{session_id}-{counter}"
        counter += 1
    session_id = candidate

    sess_dir = root / session_id
    for sub in ("chunks", "reflections", "annotations", "output"):
        (sess_dir / sub).mkdir(parents=True, exist_ok=True)

    meta = {
        "session_id": session_id,
        "source_file": str(source.resolve()),
        "source_filename": source.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lens": args.lens or None,
        "status": "preread",
        "current_chunk": 0,
        "total_chunks": 0,
    }
    (sess_dir / "session.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print(session_id)
    print(str(sess_dir))


def cmd_list(args):
    root = get_sessions_root()
    if not root.exists():
        print("No sessions found.")
        return
    sessions = []
    for d in sorted(root.iterdir()):
        mp = d / "session.json"
        if mp.exists():
            try:
                m = json.loads(mp.read_text(encoding="utf-8"))
                sessions.append(m)
            except json.JSONDecodeError:
                continue
    if not sessions:
        print("No sessions found.")
        return
    # Header
    print(f"{'SESSION ID':<40} {'STATUS':<12} {'PROGRESS':<12} {'SOURCE'}")
    print("-" * 100)
    for s in sessions:
        cur = s.get("current_chunk", 0)
        tot = s.get("total_chunks", 0)
        prog = f"{cur}/{tot}" if tot else "—"
        src = Path(s.get("source_file", "?")).name
        print(f"{s['session_id']:<40} {s.get('status','?'):<12} {prog:<12} {src}")


def cmd_get(args):
    sess_dir = get_sessions_root() / args.session_id
    mp = sess_dir / "session.json"
    if not mp.exists():
        print(f"Error: session not found: {args.session_id}", file=sys.stderr)
        sys.exit(1)
    print(mp.read_text(encoding="utf-8"), end="")


def cmd_update(args):
    sess_dir = get_sessions_root() / args.session_id
    mp = sess_dir / "session.json"
    if not mp.exists():
        print(f"Error: session not found: {args.session_id}", file=sys.stderr)
        sys.exit(1)
    meta = json.loads(mp.read_text(encoding="utf-8"))

    for kv in args.set:
        if "=" not in kv:
            print(f"Error: --set expects key=value, got: {kv}", file=sys.stderr)
            sys.exit(1)
        key, val = kv.split("=", 1)
        # Auto-coerce integers
        try:
            val = int(val)
        except ValueError:
            pass
        meta[key] = val

    mp.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {args.session_id}")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Manage sequential_read sessions"
    )
    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Create a new reading session")
    p_create.add_argument("source_file", help="Path to the source text file")
    p_create.add_argument("--lens", help="Optional reading lens/persona")

    sub.add_parser("list", help="List all reading sessions")

    p_get = sub.add_parser("get", help="Show session metadata")
    p_get.add_argument("session_id")

    p_update = sub.add_parser("update", help="Update session fields")
    p_update.add_argument("session_id")
    p_update.add_argument(
        "--set",
        nargs="+",
        required=True,
        metavar="key=value",
        help="Fields to update (e.g. --set status=chunked total_chunks=12)",
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"create": cmd_create, "list": cmd_list, "get": cmd_get, "update": cmd_update}[
        args.command
    ](args)


if __name__ == "__main__":
    main()
