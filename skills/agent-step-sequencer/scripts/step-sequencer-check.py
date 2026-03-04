#!/usr/bin/env python3
"""
Step-sequencer heartbeat check. Invoked by heartbeat cycle or agent.
Reads state.json, invokes runner when work exists. Does NOT execute work—invokes runner.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_state(state_path: Path) -> dict | None:
    if not state_path.exists():
        return None
    with open(state_path) as f:
        return json.load(f)


def save_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def get_runner_path(scripts_dir: Path) -> Path:
    return Path(os.environ.get("STEP_RUNNER", str(scripts_dir / "step-sequencer-runner.py")))


def invoke_runner(state_path: Path, scripts_dir: Path) -> None:
    runner = get_runner_path(scripts_dir)
    if runner.exists():
        subprocess.run(
            [sys.executable, str(runner), str(state_path)],
            cwd=state_path.parent,
        )


def check(state_path: Path) -> int:
    """
    Run heartbeat check. Returns 0 on success.
    1. Read state.json
    2. If no state or status=DONE → do nothing
    3. If step FAILED → bump tries, reset to PENDING, invoke runner
    4. If step DONE → advance currentStep, invoke runner
    5. If step PENDING or IN_PROGRESS → invoke runner
    6. Update lastHeartbeatIso
    """
    state = load_state(state_path)
    if state is None:
        return 0

    now = datetime.now(timezone.utc).isoformat()
    state["lastHeartbeatIso"] = now

    status = state.get("status", "IN_PROGRESS")
    if status == "DONE":
        save_state(state_path, state)
        return 0

    step_queue = state.get("stepQueue", [])
    current_step = state.get("currentStep", 0)
    step_runs = state.get("stepRuns", {})
    scripts_dir = Path(__file__).resolve().parent

    if not step_queue:
        state["status"] = "DONE"
        save_state(state_path, state)
        return 0

    if current_step >= len(step_queue):
        state["status"] = "DONE"
        save_state(state_path, state)
        return 0

    step_id = step_queue[current_step]
    step_info = step_runs.get(step_id, {"status": "PENDING", "tries": 0})
    step_status = step_info.get("status")

    if step_status == "DONE":
        state["currentStep"] = current_step + 1
        save_state(state_path, state)
        invoke_runner(state_path, scripts_dir)
        return 0

    if step_status == "FAILED":
        tries = step_info.get("tries", 0)
        max_retries = int(os.environ.get("STEP_MAX_RETRIES", "3"))
        if tries >= max_retries:
            state.setdefault("blockers", []).append(f"{step_id}: max retries ({tries}) exceeded")
            save_state(state_path, state)
            return 0
        step_runs[step_id] = {
            "status": "PENDING",
            "tries": tries,
            "error": step_info.get("error", "unknown"),
            "lastRunIso": step_info.get("lastRunIso", now),
        }
        state["stepRuns"] = step_runs
        save_state(state_path, state)
        invoke_runner(state_path, scripts_dir)
        return 0

    # PENDING or IN_PROGRESS: invoke runner
    save_state(state_path, state)
    invoke_runner(state_path, scripts_dir)
    return 0


def main() -> int:
    state_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("state.json")
    if not state_path.is_absolute():
        state_path = Path.cwd() / state_path
    return check(state_path)


if __name__ == "__main__":
    sys.exit(main())
