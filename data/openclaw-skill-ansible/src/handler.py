#!/usr/bin/env python3
"""Secure task dispatcher for openclaw-skill-ansible."""

import json
import os
import subprocess
import sys
from pathlib import Path

ACTIONS_DIR = Path(__file__).resolve().parents[1] / "actions"

HIGH_RISK_ACTIONS = {"run-cmd", "deploy-skill"}


def load_task(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _allowed_callers() -> set[str]:
    raw = os.environ.get("OPENCLAW_ALLOWED_CALLERS", "architect,chief-of-staff")
    out = set()
    for part in raw.split(","):
        v = part.strip()
        if v:
            out.add(v)
    return out


def authorize(task: dict) -> tuple[bool, str]:
    action = str(task.get("action", "")).strip()
    caller = str(task.get("caller", "")).strip()
    if not caller:
        return False, "missing caller"

    allowed = _allowed_callers()
    if caller not in allowed:
        return False, f"caller '{caller}' not authorized"

    if action in HIGH_RISK_ACTIONS:
        allow_high_risk = os.environ.get("OPENCLAW_ALLOW_HIGH_RISK", "0") == "1"
        if not allow_high_risk:
            return False, f"action '{action}' blocked (set OPENCLAW_ALLOW_HIGH_RISK=1 to enable)"

    return True, "ok"


def dispatch(task: dict, task_path: str) -> int:
    action = str(task.get("action", "")).strip()
    if not action:
        print("Missing action", file=sys.stderr)
        return 2

    script = ACTIONS_DIR / f"{action}.sh"
    if not script.exists():
        print(f"Unknown action: {action}", file=sys.stderr)
        return 2

    # Run script directly with argv, never shell interpolation.
    result = subprocess.run(["/bin/bash", str(script), task_path], check=False)
    return int(result.returncode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: handler.py /path/to/task.json", file=sys.stderr)
        sys.exit(1)

    task_path = sys.argv[1]
    task = load_task(task_path)

    ok, reason = authorize(task)
    if not ok:
        print(f"Authorization failed: {reason}", file=sys.stderr)
        sys.exit(3)

    rc = dispatch(task, task_path)
    sys.exit(rc)
