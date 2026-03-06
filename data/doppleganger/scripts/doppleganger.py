#!/usr/bin/env python3
"""
Doppleganger — Prevent duplicate subagent sessions.

Stops the "multiple Spidermen pointing at each other" problem: same task
spawned multiple times = token overspend and lag. Run before sessions_spawn
to block duplicates.

Usage:
  python3 doppleganger.py check "<task string>" [--json]
  python3 doppleganger.py guard --task "<task>" [--json]   # alias for check, same output
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", Path.home() / ".openclaw"))
TRACKER_SCRIPT = OPENCLAW_HOME / "workspace" / "skills" / "subagent-tracker" / "scripts" / "subagent_tracker.py"


def _find_tracker():
    if TRACKER_SCRIPT.exists():
        return str(TRACKER_SCRIPT)
    fallback = SKILL_DIR.parent / "subagent-tracker" / "scripts" / "subagent_tracker.py"
    if fallback.exists():
        return str(fallback)
    return None


def check_duplicate(task: str, json_out: bool) -> dict:
    """Check if task is already running. Returns result dict."""
    tracker = _find_tracker()
    if not tracker:
        return {"duplicate": False, "error": "subagent_tracker not found", "doppleganger_ok": False}
    cmd = [sys.executable, tracker, "check-duplicate", "--task", task, "--json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out = result.stdout.strip()
        if not out:
            return {"duplicate": False, "error": result.stderr or "no output", "doppleganger_ok": False}
        data = json.loads(out)
        data["doppleganger_ok"] = True
        return data
    except subprocess.TimeoutExpired:
        return {"duplicate": False, "error": "timeout", "doppleganger_ok": False}
    except json.JSONDecodeError as e:
        return {"duplicate": False, "error": str(e), "doppleganger_ok": False}


def main():
    parser = argparse.ArgumentParser(
        description="Doppleganger: prevent duplicate subagent sessions (same task = one agent)."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    check_p = sub.add_parser("check", help="Check if this task is already running")
    check_p.add_argument("task", nargs="?", default="", help="Task string (same as for sessions_spawn)")
    check_p.add_argument("--json", action="store_true", help="JSON output")
    guard_p = sub.add_parser("guard", help="Guard: same as check (for 'run doppleganger guard before spawn')")
    guard_p.add_argument("--task", required=True, help="Task string")
    guard_p.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()
    task = (getattr(args, "task", None) or "").strip()
    json_out = getattr(args, "json", False)

    result = check_duplicate(task, json_out)
    if json_out:
        print(json.dumps(result))
    else:
        if result.get("duplicate"):
            print(f"Doppleganger: duplicate detected (already running). sessionId={result.get('sessionId', '?')}")
            sys.exit(2)
        if result.get("error"):
            print(f"Doppleganger: check failed — {result['error']}")
            sys.exit(1)
        print("Doppleganger: no duplicate; safe to spawn.")
    sys.exit(0)


if __name__ == "__main__":
    main()
