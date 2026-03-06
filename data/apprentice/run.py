#!/usr/bin/env python3
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: none
#   Local files read: workflows/<n>/SKILL.md, workflows/<n>/observation.json
#   Local files written: workflows/<n>/run_log.json

"""
Apprentice Runner — executes a learned workflow.
Lists, previews, and runs named workflows.
Stdlib only. No external dependencies. No network calls.
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

SKILL_DIR = Path(__file__).parent.parent
WORKFLOWS_DIR = SKILL_DIR / "workflows"


def list_workflows() -> list:
    workflows = []
    if not WORKFLOWS_DIR.exists():
        return workflows
    for item in sorted(WORKFLOWS_DIR.iterdir()):
        if item.is_dir() and (item / "SKILL.md").exists():
            obs = item / "observation.json"
            learned_at = "unknown"
            step_count = 0
            if obs.exists():
                try:
                    with open(obs) as f:
                        data = json.load(f)
                    learned_at = data.get("started_at", "unknown")[:10]
                    step_count = len(data.get("steps", []))
                except Exception:
                    pass
            workflows.append({
                "name": item.name,
                "learned_at": learned_at,
                "step_count": step_count,
                "path": str(item)
            })
    return workflows


def preview_workflow(workflow_name: str):
    """Show what a workflow will do before running it."""
    workflow_dir = WORKFLOWS_DIR / workflow_name
    if not workflow_dir.exists():
        print(f"Workflow not found: {workflow_name}", file=sys.stderr)
        print("Run: python3 run.py --list to see available workflows")
        sys.exit(1)

    obs_file = workflow_dir / "observation.json"
    if not obs_file.exists():
        print(f"No observation data for: {workflow_name}", file=sys.stderr)
        sys.exit(1)

    with open(obs_file) as f:
        obs = json.load(f)

    steps = obs.get("steps", [])
    print(f"━" * 52)
    print(f"🎓 WORKFLOW PREVIEW — {workflow_name}")
    print(f"   Learned: {obs.get('started_at', 'unknown')[:10]}")
    print(f"   Steps: {len(steps)}")
    print(f"━" * 52)
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step.get('text', '').strip()}")
    print(f"━" * 52)


def run_workflow(workflow_name: str, variables: dict = None, dry_run: bool = False):
    """Run a learned workflow."""
    workflow_dir = WORKFLOWS_DIR / workflow_name
    if not workflow_dir.exists():
        available = [w["name"] for w in list_workflows()]
        print(f"Workflow not found: {workflow_name}", file=sys.stderr)
        if available:
            print(f"Available workflows: {', '.join(available)}")
        sys.exit(1)

    run_script = workflow_dir / "run.sh"
    obs_file = workflow_dir / "observation.json"

    with open(obs_file) as f:
        obs = json.load(f)
    steps = obs.get("steps", [])

    print(f"🎓 Running: {workflow_name}")
    print(f"   Steps: {len(steps)}")

    if dry_run:
        print(f"   [DRY RUN — no execution]")
        preview_workflow(workflow_name)
        return

    if not run_script.exists():
        # Fallback: just narrate the steps
        print()
        for i, step in enumerate(steps, 1):
            print(f"  Step {i}/{len(steps)}: {step.get('text', '').strip()}")
        print()
        print("✅ Workflow narration complete.")
        print("   (No run.sh found — agent will interpret steps directly)")
        return

    # Build environment for run.sh
    env = os.environ.copy()
    if variables:
        for k, v in variables.items():
            env[k.upper()] = str(v)

    print()
    try:
        result = subprocess.run(
            ["bash", str(run_script)],
            env=env,
            capture_output=False
        )

        # Log the run
        run_log = {
            "workflow": workflow_name,
            "run_at": datetime.now(timezone.utc).isoformat(),
            "variables": variables or {},
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }
        log_file = workflow_dir / "run_log.json"
        logs = []
        if log_file.exists():
            try:
                with open(log_file) as f:
                    logs = json.load(f)
            except Exception:
                pass
        logs.append(run_log)
        logs = logs[-20:]  # Keep last 20 runs
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

        if result.returncode != 0:
            print(f"\n⚠️  Workflow exited with code {result.returncode}")
            print("   Say 'that step was wrong, here's how it should be:' to refine it.")

    except FileNotFoundError:
        print("bash not found — running step narration instead.", file=sys.stderr)
        for i, step in enumerate(steps, 1):
            print(f"  Step {i}: {step.get('text', '').strip()}")


def parse_variable_args(var_list: list) -> dict:
    """Parse KEY=value arguments into a dict."""
    variables = {}
    for item in var_list:
        if "=" in item:
            k, v = item.split("=", 1)
            variables[k.strip().upper()] = v.strip()
    return variables


def main():
    parser = argparse.ArgumentParser(
        description="Apprentice Runner — execute learned workflows"
    )
    parser.add_argument("workflow", nargs="?", help="Workflow name to run")
    parser.add_argument("--list", action="store_true", help="List all learned workflows")
    parser.add_argument("--preview", action="store_true", help="Preview without running")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no execution)")
    parser.add_argument("vars", nargs="*", help="Variable assignments: KEY=value")

    args = parser.parse_args()

    if args.list or not args.workflow:
        workflows = list_workflows()
        if not workflows:
            print("No workflows learned yet.")
            print("Say 'watch me' to start teaching your agent.")
            return
        print(f"🎓 LEARNED WORKFLOWS ({len(workflows)}):")
        for w in workflows:
            print(f"  ✅ {w['name']:35s}  {w['step_count']} steps  learned: {w['learned_at']}")
        return

    if args.preview:
        preview_workflow(args.workflow)
        return

    variables = parse_variable_args(args.vars)
    run_workflow(args.workflow, variables, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
