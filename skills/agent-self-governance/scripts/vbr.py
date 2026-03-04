#!/usr/bin/env python3
"""Verify Before Reporting (VBR) — Don't claim "done" until verified.

Tracks verification tasks and their outcomes. Before reporting completion,
run the appropriate verification check.

Usage:
  vbr.py check <task_id> <task_type> <target>    # Run verification
  vbr.py log <agent_id> <task_id> <passed> <details>  # Log result
  vbr.py history <agent_id> [--limit N]           # View verification history
  vbr.py stats <agent_id>                         # Pass/fail rates
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DIR = os.path.join(os.environ.get("HOME", "."), "clawd", "memory", "governance")
VBR_FILE = "vbr-history.jsonl"


def vbr_path(gov_dir: str) -> Path:
    return Path(gov_dir) / VBR_FILE


def check_file_exists(target: str) -> tuple[bool, str]:
    exists = os.path.exists(target)
    return exists, f"File {'exists' if exists else 'NOT FOUND'}: {target}"


def check_file_changed(target: str) -> tuple[bool, str]:
    """Check if file was modified in last 5 minutes."""
    if not os.path.exists(target):
        return False, f"File not found: {target}"
    mtime = os.path.getmtime(target)
    age = datetime.now().timestamp() - mtime
    changed = age < 300
    return changed, f"File modified {int(age)}s ago {'(recent)' if changed else '(stale)'}"


def check_command(target: str) -> tuple[bool, str]:
    """Run a shell command and check exit code."""
    try:
        result = subprocess.run(target, shell=True, capture_output=True, text=True, timeout=30)
        passed = result.returncode == 0
        output = (result.stdout + result.stderr).strip()[:200]
        return passed, f"Exit {result.returncode}: {output}"
    except subprocess.TimeoutExpired:
        return False, "Command timed out (30s)"
    except Exception as e:
        return False, f"Error: {e}"


def check_git_pushed(target: str) -> tuple[bool, str]:
    """Check if local branch is up to date with remote."""
    try:
        result = subprocess.run(
            f"cd {target} && git status -sb",
            shell=True, capture_output=True, text=True, timeout=10
        )
        behind = "behind" in result.stdout or "ahead" in result.stdout
        return not behind, f"Git status: {result.stdout.strip()[:100]}"
    except Exception as e:
        return False, f"Error: {e}"


CHECKS = {
    "file_exists": check_file_exists,
    "file_changed": check_file_changed,
    "command": check_command,
    "git_pushed": check_git_pushed,
}


def run_check(task_type: str, target: str) -> tuple[bool, str]:
    if task_type in CHECKS:
        return CHECKS[task_type](target)
    return False, f"Unknown check type: {task_type}. Available: {list(CHECKS.keys())}"


def log_result(gov_dir: str, agent_id: str, task_id: str, passed: bool, details: str):
    os.makedirs(gov_dir, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": agent_id,
        "task_id": task_id,
        "passed": passed,
        "details": details,
    }
    with open(vbr_path(gov_dir), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def get_history(gov_dir: str, agent_id: str, limit: int = 20) -> list[dict]:
    path = vbr_path(gov_dir)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().strip().split("\n"):
        if line:
            e = json.loads(line)
            if e["agent_id"] == agent_id:
                entries.append(e)
    return entries[-limit:]


def get_stats(gov_dir: str, agent_id: str) -> dict:
    path = vbr_path(gov_dir)
    if not path.exists():
        return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0}
    entries = []
    for line in path.read_text().strip().split("\n"):
        if line:
            e = json.loads(line)
            if e["agent_id"] == agent_id:
                entries.append(e)
    passed = sum(1 for e in entries if e["passed"])
    total = len(entries)
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": round(passed / total, 2) if total > 0 else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Verify Before Reporting")
    parser.add_argument("command", choices=["check", "log", "history", "stats"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--dir", default=DEFAULT_DIR)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if args.command == "check":
        if len(args.args) < 3:
            print("Usage: vbr.py check <task_id> <task_type> <target>", file=sys.stderr)
            sys.exit(1)
        task_id, task_type, target = args.args[0], args.args[1], " ".join(args.args[2:])
        passed, details = run_check(task_type, target)
        result = {"task_id": task_id, "task_type": task_type, "passed": passed, "details": details}
        print(json.dumps(result, indent=2))

    elif args.command == "log":
        if len(args.args) < 4:
            print("Usage: vbr.py log <agent_id> <task_id> <passed> <details>", file=sys.stderr)
            sys.exit(1)
        passed = args.args[2].lower() in ("true", "1", "yes")
        entry = log_result(args.dir, args.args[0], args.args[1], passed, " ".join(args.args[3:]))
        print(json.dumps(entry, indent=2))

    elif args.command == "history":
        if not args.args:
            print("Usage: vbr.py history <agent_id>", file=sys.stderr)
            sys.exit(1)
        entries = get_history(args.dir, args.args[0], args.limit)
        print(json.dumps(entries, indent=2))

    elif args.command == "stats":
        if not args.args:
            print("Usage: vbr.py stats <agent_id>", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(get_stats(args.dir, args.args[0]), indent=2))


if __name__ == "__main__":
    main()
