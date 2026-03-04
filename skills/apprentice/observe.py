#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: workflows/ directory
#   Local files written: workflows/<name>/observation.json, .observation_active.json

"""
Apprentice Observer — manages observation sessions.
Records user actions, narrations, and intent during "watch me" mode.
Stdlib only. No external dependencies. No network calls.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

SKILL_DIR = Path(__file__).parent.parent
WORKFLOWS_DIR = SKILL_DIR / "workflows"
ACTIVE_SESSION_FILE = SKILL_DIR / ".observation_active.json"
WORKFLOWS_DIR.mkdir(exist_ok=True)


def load_active_session() -> dict | None:
    if not ACTIVE_SESSION_FILE.exists():
        return None
    try:
        with open(ACTIVE_SESSION_FILE) as f:
            return json.load(f)
    except Exception:
        return None


def save_active_session(session: dict):
    with open(ACTIVE_SESSION_FILE, "w") as f:
        json.dump(session, f, indent=2)


def clear_active_session():
    if ACTIVE_SESSION_FILE.exists():
        ACTIVE_SESSION_FILE.unlink()


def start_observation(hint: str = ""):
    """Start a new observation session."""
    existing = load_active_session()
    if existing:
        print(f"⚠️  Already in observation mode (started: {existing.get('started_at', 'unknown')})")
        print("   Say 'done' or run: python3 observe.py --stop")
        sys.exit(1)

    session = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "hint": hint,
        "steps": [],
        "raw_narration": []
    }
    save_active_session(session)
    print("🎓 APPRENTICE — OBSERVATION MODE ACTIVE")
    print()
    if hint:
        print(f"   Learning: {hint}")
    print("   Do your task naturally. Talk out loud if it helps.")
    print("   Tell me what you're doing, why, and what changes each time.")
    print("   When you're done, say 'done' or 'stop watching'.")
    print()
    print("   I'm watching. Go ahead.")


def record_step(text: str):
    """Record a step/narration during active observation."""
    session = load_active_session()
    if not session:
        print("Not in observation mode. Say 'watch me' to start.", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).isoformat()
    step = {
        "timestamp": timestamp,
        "text": text.strip()
    }

    session["steps"].append(step)
    session["raw_narration"].append(f"[{timestamp}] {text.strip()}")
    save_active_session(session)

    step_num = len(session["steps"])
    print(f"   📝 Step {step_num} recorded.")


def stop_observation() -> dict:
    """Stop observation and return the completed session."""
    session = load_active_session()
    if not session:
        print("No active observation session.", file=sys.stderr)
        sys.exit(1)

    session["ended_at"] = datetime.now(timezone.utc).isoformat()
    clear_active_session()

    print(f"🎓 Observation complete. {len(session['steps'])} steps recorded.")
    return session


def save_raw_observation(session: dict, workflow_name: str) -> Path:
    """Save raw observation to the workflow directory."""
    # Sanitize workflow name
    safe_name = "".join(
        c if c.isalnum() or c in "-_" else "-"
        for c in workflow_name.lower().replace(" ", "-")
    ).strip("-")

    workflow_dir = WORKFLOWS_DIR / safe_name
    workflow_dir.mkdir(exist_ok=True)

    obs_file = workflow_dir / "observation.json"
    with open(obs_file, "w") as f:
        json.dump(session, f, indent=2)

    return workflow_dir


def list_workflows() -> list:
    """List all learned workflows."""
    workflows = []
    for item in sorted(WORKFLOWS_DIR.iterdir()):
        if item.is_dir():
            skill_md = item / "SKILL.md"
            obs = item / "observation.json"
            status = "✅" if skill_md.exists() else "⚙️ "

            learned_at = "unknown"
            if obs.exists():
                try:
                    with open(obs) as f:
                        data = json.load(f)
                    learned_at = data.get("started_at", "unknown")[:10]
                except Exception:
                    pass

            workflows.append({
                "name": item.name,
                "status": status,
                "learned_at": learned_at,
                "has_skill": skill_md.exists()
            })
    return workflows


def status():
    """Show current observation status."""
    session = load_active_session()
    workflows = list_workflows()

    if session:
        print(f"🔴 OBSERVATION IN PROGRESS")
        print(f"   Started: {session.get('started_at', 'unknown')[:19].replace('T', ' ')} UTC")
        print(f"   Steps recorded: {len(session.get('steps', []))}")
        if session.get('hint'):
            print(f"   Learning: {session['hint']}")
    else:
        print("⚪ Not currently observing.")

    print()
    if workflows:
        print(f"🎓 LEARNED WORKFLOWS ({len(workflows)}):")
        for w in workflows:
            print(f"   {w['status']} {w['name']:30s}  learned: {w['learned_at']}")
    else:
        print("🎓 No workflows learned yet.")
        print("   Say 'watch me' to start teaching your agent.")


def main():
    parser = argparse.ArgumentParser(
        description="Apprentice Observer — manage observation sessions"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Start
    start_p = subparsers.add_parser("start", help="Start observation session")
    start_p.add_argument("hint", nargs="*", help="What you're teaching (optional)")

    # Record
    record_p = subparsers.add_parser("record", help="Record a step during observation")
    record_p.add_argument("text", nargs="+", help="What you're doing/narrating")

    # Stop
    subparsers.add_parser("stop", help="Stop observation and return raw session")

    # Status
    subparsers.add_parser("status", help="Show observation status and workflow library")

    # List
    subparsers.add_parser("list", help="List all learned workflows")

    args = parser.parse_args()

    if args.command == "start":
        hint = " ".join(args.hint) if args.hint else ""
        start_observation(hint)

    elif args.command == "record":
        text = " ".join(args.text)
        record_step(text)

    elif args.command == "stop":
        session = stop_observation()
        # Output JSON for synthesize.py to consume
        print(json.dumps(session))

    elif args.command == "status":
        status()

    elif args.command == "list":
        workflows = list_workflows()
        if not workflows:
            print("No workflows learned yet.")
        else:
            for w in workflows:
                print(f"{w['status']} {w['name']}")

    else:
        # Default: show status
        status()


if __name__ == "__main__":
    main()
