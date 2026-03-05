#!/usr/bin/env python3
"""
Automated tests for agent-step-sequencer check and runner.
Uses echo/false as agent commands for deterministic behavior.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Add scripts to path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
CHECK = SCRIPTS_DIR / "step-sequencer-check.py"
RUNNER = SCRIPTS_DIR / "step-sequencer-runner.py"


def run_check(state_path: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    env = env or os.environ.copy()
    return subprocess.run(
        [sys.executable, str(CHECK), str(state_path)],
        cwd=state_path.parent,
        env=env,
        capture_output=True,
        text=True,
    )


def load_state(state_path: Path) -> dict:
    with open(state_path) as f:
        return json.load(f)


def test_basic_flow_two_steps():
    """Check invokes runner; with auto-advance, one run_check can complete both steps."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {
                "steps": {
                    "step-1": {"title": "First", "instruction": "one"},
                    "step-2": {"title": "Second", "instruction": "two"},
                }
            },
            "stepQueue": ["step-1", "step-2"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "echo"

        # Run 1: runner does step 1 -> DONE -> invokes check -> advance -> runner step 2 -> DONE -> check -> advance
        run_check(state_path, env)
        s = load_state(state_path)
        assert s["stepRuns"]["step-1"]["status"] == "DONE"
        assert s["stepRuns"]["step-2"]["status"] == "DONE"
        assert s["currentStep"] == 2

        # Run 2: check sees currentStep >= len(stepQueue), sets status DONE
        run_check(state_path, env)
        s = load_state(state_path)
        assert s["status"] == "DONE"

    print("test_basic_flow_two_steps: OK")


def test_failure_marks_failed():
    """Agent returns non-zero -> step marked FAILED, error stored."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {"step-1": {"title": "Fail", "instruction": "x"}}},
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "false"  # always fails

        run_check(state_path, env)
        s = load_state(state_path)
        assert s["stepRuns"]["step-1"]["status"] == "FAILED"
        assert "error" in s["stepRuns"]["step-1"]

    print("test_failure_marks_failed: OK")


def test_retry_stops_at_max_retries():
    """On FAILED, retries until STEP_MAX_RETRIES, then adds to blockers."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {"step-1": {"title": "Fail", "instruction": "x"}}},
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "false"
        env["STEP_MAX_RETRIES"] = "2"

        run_check(state_path, env)
        s = load_state(state_path)
        assert s["stepRuns"]["step-1"]["status"] == "FAILED"
        assert s["stepRuns"]["step-1"]["tries"] >= 2
        assert "blockers" in s
        assert any("step-1" in b for b in s["blockers"])

    print("test_retry_stops_at_max_retries: OK")


def test_recovery_mid_flow():
    """State with step 1 DONE, step 2 PENDING -> one run_check advances and runs step 2."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {
                "steps": {
                    "step-1": {"title": "Done", "instruction": "a"},
                    "step-2": {"title": "Next", "instruction": "b"},
                }
            },
            "stepQueue": ["step-1", "step-2"],
            "currentStep": 0,
            "stepRuns": {"step-1": {"status": "DONE", "tries": 1, "lastRunIso": "2025-01-01T00:00:00Z"}},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "echo"

        run_check(state_path, env)
        s = load_state(state_path)
        assert s["currentStep"] == 2
        assert s["stepRuns"]["step-2"]["status"] == "DONE"

        run_check(state_path, env)  # set status DONE
        s = load_state(state_path)
        assert s["status"] == "DONE"

    print("test_recovery_mid_flow: OK")


def test_no_state_does_nothing():
    """No state file -> check exits 0, does nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "nonexistent.json"
        r = run_check(state_path)
        assert r.returncode == 0

    print("test_no_state_does_nothing: OK")


def test_step_agent_cmd_blocked():
    """STEP_AGENT_CMD=bash -c is rejected (command injection prevention)."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {"step-1": {"title": "X", "instruction": "hello"}}},
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "bash -c"

        r = subprocess.run(
            [sys.executable, str(RUNNER), str(state_path)],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 2
        assert "bash" in r.stderr or "shell" in r.stderr.lower()

    print("test_step_agent_cmd_blocked: OK")


def run_runner(state_path: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    env = env or os.environ.copy()
    return subprocess.run(
        [sys.executable, str(RUNNER), str(state_path)],
        cwd=state_path.parent,
        env=env,
        capture_output=True,
        text=True,
    )


def test_required_outputs_missing_fails():
    """Agent exits 0 but requiredOutputs files missing -> step FAILED."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {
                "steps": {
                    "step-1": {
                        "title": "Produce file",
                        "instruction": "write out",
                        "requiredOutputs": ["out.md"],
                    }
                }
            },
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "echo"  # exits 0 but no out.md

        run_runner(state_path, env)
        s = load_state(state_path)
        assert s["stepRuns"]["step-1"]["status"] == "FAILED"
        assert "Missing required outputs" in s["stepRuns"]["step-1"].get("error", "")

    print("test_required_outputs_missing_fails: OK")


def test_required_outputs_present_succeeds():
    """Agent exits 0 and requiredOutputs exist -> step DONE."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        (Path(tmp) / "artifacts").mkdir(exist_ok=True)
        (Path(tmp) / "artifacts" / "report.md").write_text("done")
        state = {
            "plan": {
                "steps": {
                    "step-1": {
                        "title": "Produce report",
                        "instruction": "write report",
                        "requiredOutputs": ["artifacts/report.md"],
                    }
                }
            },
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "echo"

        run_runner(state_path, env)
        s = load_state(state_path)
        assert s["stepRuns"]["step-1"]["status"] == "DONE"

    print("test_required_outputs_present_succeeds: OK")


def test_done_state_does_nothing():
    """status=DONE -> check does nothing."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {}},
            "stepQueue": [],
            "currentStep": 0,
            "stepRuns": {},
            "status": "DONE",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        run_check(state_path)
        s = load_state(state_path)
        assert s["status"] == "DONE"

    print("test_done_state_does_nothing: OK")


def test_step_agent_cmd_unset():
    """STEP_AGENT_CMD unset -> runner exits 2 with clear error."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {"step-1": {"title": "X", "instruction": "hello"}}},
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env.pop("STEP_AGENT_CMD", None)

        r = subprocess.run(
            [sys.executable, str(RUNNER), str(state_path)],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 2, f"Expected exit 2, got {r.returncode}"
        assert "STEP_AGENT_CMD" in r.stderr

    print("test_step_agent_cmd_unset: OK")


def test_step_agent_cmd_binary_not_found():
    """STEP_AGENT_CMD points to nonexistent binary -> runner exits 2."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {"step-1": {"title": "X", "instruction": "hello"}}},
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "nonexistent-binary-xyz --message"

        r = subprocess.run(
            [sys.executable, str(RUNNER), str(state_path)],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
        )
        assert r.returncode == 2, f"Expected exit 2, got {r.returncode}"
        assert "not found on PATH" in r.stderr

    print("test_step_agent_cmd_binary_not_found: OK")


def test_stdout_captured_on_success():
    """Agent stdout is stored in stepRuns on success."""
    with tempfile.TemporaryDirectory() as tmp:
        state_path = Path(tmp) / "state.json"
        state = {
            "plan": {"steps": {"step-1": {"title": "Echo", "instruction": "hello world"}}},
            "stepQueue": ["step-1"],
            "currentStep": 0,
            "stepRuns": {},
            "stepDelayMinutes": 0,
            "status": "IN_PROGRESS",
        }
        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

        env = os.environ.copy()
        env["STEP_AGENT_CMD"] = "echo"

        run_runner(state_path, env)
        s = load_state(state_path)
        assert s["stepRuns"]["step-1"]["status"] == "DONE"
        assert "stdout" in s["stepRuns"]["step-1"]
        assert "hello world" in s["stepRuns"]["step-1"]["stdout"]

    print("test_stdout_captured_on_success: OK")


def main():
    tests = [
        test_no_state_does_nothing,
        test_step_agent_cmd_blocked,
        test_step_agent_cmd_unset,
        test_step_agent_cmd_binary_not_found,
        test_done_state_does_nothing,
        test_basic_flow_two_steps,
        test_failure_marks_failed,
        test_retry_stops_at_max_retries,
        test_recovery_mid_flow,
        test_required_outputs_missing_fails,
        test_required_outputs_present_succeeds,
        test_stdout_captured_on_success,
    ]
    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            failed.append((t.__name__, e))
            print(f"{t.__name__}: FAIL - {e}")

    if failed:
        print(f"\n{len(failed)}/{len(tests)} tests failed")
        sys.exit(1)
    print(f"\nAll {len(tests)} tests passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
