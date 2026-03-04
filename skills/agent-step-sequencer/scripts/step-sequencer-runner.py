#!/usr/bin/env python3
"""
Step-sequencer runner. Invoked by check script or after failure.
Reads state, gets current step instruction, invokes agent, marks DONE/FAILED.
On FAILED: invokes check script immediately for retry.
"""

import json
import os
import shutil
import subprocess
import sys
import time
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


# Blocked to prevent command injection: instruction is appended and must not be executed by a shell
_BLOCKED_BASES = frozenset({"bash", "sh", "dash", "zsh", "ksh", "eval", "exec"})
_BLOCKED_ARGS = frozenset({"-c", "-e"})


def _validate_agent_cmd(tokens: list[str]) -> None:
    """Reject STEP_AGENT_CMD values that could execute instruction as shell code."""
    if not tokens:
        return
    base = Path(tokens[0]).name.lower()
    if base in _BLOCKED_BASES:
        raise ValueError(
            f"STEP_AGENT_CMD cannot use shell interpreter '{tokens[0]}'. "
            "Use your agent binary (e.g. openclaw agent --message)."
        )
    if any(a in _BLOCKED_ARGS for a in tokens[1:]):
        raise ValueError(
            "STEP_AGENT_CMD cannot include -c or -e (shell command flags). "
            "Use your agent binary (e.g. openclaw agent --message)."
        )


def get_agent_cmd() -> list[str]:
    """How to invoke the agent. Env STEP_AGENT_CMD (space-separated). Required."""
    cmd = os.environ.get("STEP_AGENT_CMD", "").strip()
    if not cmd:
        raise ValueError(
            "STEP_AGENT_CMD is not set. Set it to your agent command "
            "(e.g. export STEP_AGENT_CMD='openclaw agent --message')."
        )
    tokens = cmd.split()
    _validate_agent_cmd(tokens)
    binary = tokens[0]
    if not shutil.which(binary):
        raise ValueError(
            f"STEP_AGENT_CMD binary '{binary}' not found on PATH. "
            "Ensure it is installed and accessible."
        )
    return tokens


def get_check_script_path(scripts_dir: Path) -> Path:
    return scripts_dir / "step-sequencer-check.py"


def _check_required_outputs(step_def: dict, workspace_root: Path) -> tuple[bool, list[str]]:
    """If step has requiredOutputs, verify each path exists under workspace_root. Return (all_exist, missing_list)."""
    required = step_def.get("requiredOutputs") or step_def.get("required_outputs")
    if not required or not isinstance(required, list):
        return True, []
    root = workspace_root.resolve()
    missing = []
    for rel in required:
        if not isinstance(rel, str):
            continue
        full = (root / rel).resolve()
        try:
            if root not in full.parents and full != root:
                missing.append(rel)  # path escape
            elif not full.is_file() and not full.is_dir():
                missing.append(rel)
        except (OSError, ValueError):
            missing.append(rel)
    return (len(missing) == 0, missing)


def run(state_path: Path) -> int:
    """
    Run current step. Returns 0 on success, 1 on failure.
    1. Read state
    2. Get current step instruction from plan.steps
    3. If stepDelayMinutes > 0 and not first run of step, sleep
    4. Invoke agent (configurable via STEP_AGENT_CMD)
    5. Mark DONE or FAILED in stepRuns
    6. If FAILED: invoke check script immediately
    """
    state = load_state(state_path)
    if state is None:
        return 0

    plan = state.get("plan", {})
    steps = plan.get("steps", {})
    step_queue = state.get("stepQueue", [])
    current_step = state.get("currentStep", 0)
    step_runs = state.get("stepRuns", {})
    step_delay = state.get("stepDelayMinutes", 0)
    scripts_dir = Path(__file__).resolve().parent

    if not step_queue or current_step >= len(step_queue):
        return 0

    step_id = step_queue[current_step]
    step_def = steps.get(step_id, {})
    instruction = step_def.get("instruction", "")
    step_info = step_runs.get(step_id, {"status": "PENDING", "tries": 0})
    tries = step_info.get("tries", 0)

    # Troubleshoot prompt on retry (tries > 0 means we've failed before)
    if tries > 0 and step_info.get("error"):
        error = step_info.get("error", "unknown")
        prompt = (
            f"Step {step_id} failed (tries: {tries}). "
            f"Previous run ended with: {error}. "
            f"Please troubleshoot and retry: {instruction}"
        )
    else:
        prompt = instruction

    # Apply delay: between steps (not the very first step) or on retries
    is_retry = tries > 0 and step_info.get("lastRunIso")
    is_subsequent_step = current_step > 0 and tries == 0
    if step_delay > 0 and (is_retry or is_subsequent_step):
        time.sleep(step_delay * 60)

    now = datetime.now(timezone.utc).isoformat()
    step_runs[step_id] = {
        "status": "IN_PROGRESS",
        "tries": tries + 1,
        "lastRunIso": now,
    }
    state["stepRuns"] = step_runs
    save_state(state_path, state)

    agent_cmd = get_agent_cmd() + [prompt]
    try:
        result = subprocess.run(
            agent_cmd,
            capture_output=True,
            text=True,
            timeout=3600,
            shell=False,
        )
        success = result.returncode == 0
    except subprocess.TimeoutExpired:
        success = False
        result = type("Result", (), {"stderr": "Timeout"})()

    if success and step_def:
        all_present, missing = _check_required_outputs(step_def, state_path.parent)
        if not all_present:
            success = False
            result = type("Result", (), {"stderr": f"Missing required outputs: {', '.join(missing)}"})()

    step_runs[step_id]["status"] = "DONE" if success else "FAILED"
    step_runs[step_id]["lastRunIso"] = datetime.now(timezone.utc).isoformat()
    stdout = getattr(result, "stdout", "") or ""
    if stdout:
        step_runs[step_id]["stdout"] = stdout[:500]
    if not success:
        step_runs[step_id]["error"] = getattr(result, "stderr", str(result))[:500]
    state["stepRuns"] = step_runs
    save_state(state_path, state)

    if not success:
        check_script = get_check_script_path(scripts_dir)
        if check_script.exists():
            subprocess.run(
                [sys.executable, str(check_script), str(state_path)],
                cwd=state_path.parent,
            )
        return 1

    # Advance to next step immediately: invoke check script so it bumps currentStep and runs runner again
    check_script = get_check_script_path(scripts_dir)
    if check_script.exists():
        subprocess.run(
            [sys.executable, str(check_script), str(state_path)],
            cwd=state_path.parent,
        )
    return 0


def main() -> int:
    try:
        state_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("state.json")
        if not state_path.is_absolute():
            state_path = Path.cwd() / state_path
        return run(state_path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
