#!/usr/bin/env python3
"""Staged Workflow Runner (v0.1.6-a)

Implements Seko-style state machine for story production:

- outline_confirmed → episode_plan_confirmed → storyboard_confirmed →
  storyboard_images_confirmed → render_approved
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Path to sibling scripts
SCRIPT_DIR = Path(__file__).resolve().parent


class RunStoryError(Exception):
    pass


@dataclass
class StageStatus:
    """Represents the status of a single stage."""
    stage: str
    confirmed: bool
    checkpoint_path: Optional[Path]
    timestamp: Optional[str]
    notes: str = ""


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_last_json(stdout: str) -> Dict[str, Any]:
    """Parse the last JSON object from mixed stdout logs."""
    text = (stdout or "").strip()
    if not text:
        return {}

    # Fast path: pure JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Robust path: find last balanced {...}
    for i in range(len(text) - 1, -1, -1):
        if text[i] != "{":
            continue
        candidate = text[i:]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    raise RunStoryError("Failed to parse JSON output from subprocess")


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def resolve_prepare_script() -> Path:
    """Find prepare_storyboard.py."""
    return SCRIPT_DIR / "prepare_storyboard.py"


def resolve_orchestrate_script() -> Path:
    """Find orchestrate_story.py."""
    return SCRIPT_DIR / "orchestrate_story.py"


def resolve_seedream_script() -> Path:
    """Find seedream_image.py."""
    return SCRIPT_DIR / "seedream_image.py"


def resolve_seedance_script() -> Path:
    """Find seedance.py from seedance-video-generation skill."""
    candidates = [
        Path.home() / ".openclaw" / "skills" / "seedance-video-generation" / "seedance.py",
        Path.cwd() / "skills" / "seedance-video-generation" / "seedance.py",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise RunStoryError("Cannot find seedance.py. Please install seedance-video-generation skill.")


def get_stage_checkpoint_path(project_dir: Path, stage: str) -> Path:
    """Get checkpoint file path for a stage."""
    return project_dir / f"checkpoint-{stage}.json"


def load_stage_status(project_dir: Path, stage: str) -> StageStatus:
    """Load stage status from checkpoint file."""
    checkpoint_path = get_stage_checkpoint_path(project_dir, stage)
    if not checkpoint_path.exists():
        return StageStatus(
            stage=stage,
            confirmed=False,
            checkpoint_path=None,
            timestamp=None,
        )

    data = load_json(checkpoint_path)
    return StageStatus(
        stage=stage,
        confirmed=data.get("confirmed", False),
        checkpoint_path=checkpoint_path,
        timestamp=data.get("timestamp"),
        notes=data.get("notes", ""),
    )


def save_stage_status(project_dir: Path, stage: str, confirmed: bool, notes: str = "") -> Path:
    """Save stage status to checkpoint file."""
    checkpoint_path = get_stage_checkpoint_path(project_dir, stage)
    data = {
        "stage": stage,
        "confirmed": confirmed,
        "timestamp": datetime.now().isoformat(),
        "notes": notes,
    }
    save_json(checkpoint_path, data)
    return checkpoint_path


def stage_outline(
    project_dir: Path,
    input_text: Optional[str],
    input_file: Optional[Path],
    project_id: str,
) -> StageStatus:
    """Stage 1: Generate outline."""
    print(f"\n=== Stage: outline ===")

    # Check if already confirmed
    current = load_stage_status(project_dir, "outline")
    if current.confirmed:
        print(f"[SKIP] Outline already confirmed at {current.timestamp}")
        print(f"  Checkpoint: {current.checkpoint_path}")
        return current

    # Run prepare_storyboard.py
    prepare_script = resolve_prepare_script()
    cmd = [
        "python3", str(prepare_script),
        "--project-id", project_id,
        "--output-dir", str(project_dir),
    ]
    if input_text:
        cmd.extend(["--input-text", input_text])
    elif input_file:
        cmd.extend(["--input-file", str(input_file)])
    else:
        raise RunStoryError("Either --input-text or --input-file is required for outline stage")

    print(f"[RUN] Generating outline...")
    print(f"  Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RunStoryError(f"Failed to generate outline:\n{result.stderr}")

    output = parse_last_json(result.stdout)
    plan_dir = Path(output.get("plan_dir"))

    # Outline artifact may be absent for free-form inputs; do not hard fail
    outline_path = plan_dir / "outline.v1.json"

    # Mark as pending confirmation
    checkpoint_path = save_stage_status(
        project_dir=project_dir,
        stage="outline",
        confirmed=False,
        notes=f"Generated at {plan_dir}, awaiting manual confirmation",
    )

    print(f"\n[DONE] Outline stage prepared")
    if outline_path.exists():
        print(f"  Outline artifact: {outline_path}")
    else:
        print("  Outline artifact: (not extracted; proceed with storyboard draft review)")
    print(f"  Plan directory: {plan_dir}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"\n[ACTION] Please review outline and run: python3 {__file__} confirm --stage outline")

    return load_stage_status(project_dir, "outline")


def stage_episode_plan(
    project_dir: Path,
    project_id: str,
) -> StageStatus:
    """Stage 2: Generate episode plan."""
    print(f"\n=== Stage: episode_plan ===")

    # Check if already confirmed
    current = load_stage_status(project_dir, "episode_plan")
    if current.confirmed:
        print(f"[SKIP] Episode plan already confirmed at {current.timestamp}")
        print(f"  Checkpoint: {current.checkpoint_path}")
        return current

    # Episode plan should already be generated by prepare_storyboard.py
    # Find the latest plan directory
    plan_dirs = sorted(project_dir.glob("plan-*"), reverse=True)
    if not plan_dirs:
        raise RunStoryError("No plan directory found. Run outline stage first.")

    latest_plan = plan_dirs[0]
    episode_path = latest_plan / "episode-plan.v1.json"
    if not episode_path.exists():
        raise RunStoryError(f"Episode plan artifact not found: {episode_path}")

    # Mark as pending confirmation
    checkpoint_path = save_stage_status(
        project_dir=project_dir,
        stage="episode_plan",
        confirmed=False,
        notes=f"Generated at {latest_plan}, awaiting manual confirmation",
    )

    print(f"\n[DONE] Episode plan ready")
    print(f"  Episode artifact: {episode_path}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"\n[ACTION] Please review episode plan and run: python3 {__file__} confirm --stage episode_plan")

    return load_stage_status(project_dir, "episode_plan")


def stage_storyboard(
    project_dir: Path,
    project_id: str,
) -> StageStatus:
    """Stage 3: Generate storyboard."""
    print(f"\n=== Stage: storyboard ===")

    # Check if already confirmed
    current = load_stage_status(project_dir, "storyboard")
    if current.confirmed:
        print(f"[SKIP] Storyboard already confirmed at {current.timestamp}")
        print(f"  Checkpoint: {current.checkpoint_path}")
        return current

    # Find the latest plan directory
    plan_dirs = sorted(project_dir.glob("plan-*"), reverse=True)
    if not plan_dirs:
        raise RunStoryError("No plan directory found. Run earlier stages first.")

    latest_plan = plan_dirs[0]
    storyboard_path = latest_plan / "storyboard.draft.v1.json"
    if not storyboard_path.exists():
        raise RunStoryError(f"Storyboard draft not found: {storyboard_path}")

    # Mark as pending confirmation
    checkpoint_path = save_stage_status(
        project_dir=project_dir,
        stage="storyboard",
        confirmed=False,
        notes=f"Generated at {latest_plan}, awaiting manual confirmation",
    )

    print(f"\n[DONE] Storyboard ready")
    print(f"  Storyboard draft: {storyboard_path}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"\n[ACTION] Please review storyboard and run: python3 {__file__} confirm --stage storyboard")

    return load_stage_status(project_dir, "storyboard")


def stage_storyboard_images(
    project_dir: Path,
    project_id: str,
    dry_run: bool,
) -> StageStatus:
    """Stage 4: Generate storyboard images."""
    print(f"\n=== Stage: storyboard_images ===")

    # Check if already confirmed
    current = load_stage_status(project_dir, "storyboard_images")
    if current.confirmed:
        print(f"[SKIP] Storyboard images already confirmed at {current.timestamp}")
        print(f"  Checkpoint: {current.checkpoint_path}")
        return current

    # Find storyboard
    plan_dirs = sorted(project_dir.glob("plan-*"), reverse=True)
    if not plan_dirs:
        raise RunStoryError("No plan directory found. Run earlier stages first.")

    latest_plan = plan_dirs[0]
    storyboard_path = latest_plan / "storyboard.draft.v1.json"
    if not storyboard_path.exists():
        raise RunStoryError(f"Storyboard not found: {storyboard_path}")

    # Run seedream_image.py
    seedream_script = resolve_seedream_script()
    cmd = [
        "python3", str(seedream_script),
        "storyboard",
        "--storyboard", str(storyboard_path),
        "--output-dir", str(project_dir / "images"),
    ]
    if dry_run:
        cmd.append("--dry-run")

    print(f"[RUN] Generating storyboard images...")
    print(f"  Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RunStoryError(f"Failed to generate storyboard images:\n{result.stderr}")

    output = parse_last_json(result.stdout)
    images_dir = Path(output.get("images_dir", ""))

    # Mark as pending confirmation
    checkpoint_path = save_stage_status(
        project_dir=project_dir,
        stage="storyboard_images",
        confirmed=False,
        notes=f"Generated to {images_dir}, awaiting manual confirmation",
    )

    print(f"\n[DONE] Storyboard images ready")
    print(f"  Images directory: {images_dir}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"\n[ACTION] Please review images and run: python3 {__file__} confirm --stage storyboard_images")

    return load_stage_status(project_dir, "storyboard_images")


def stage_render(
    project_dir: Path,
    project_id: str,
    dry_run: bool,
    continue_on_error: bool,
    auto_concat: bool = True,
) -> StageStatus:
    """Stage 5: Render videos and optionally concatenate."""
    print(f"\n=== Stage: render ===")

    # Check if already confirmed
    current = load_stage_status(project_dir, "render")
    if current.confirmed:
        print(f"[SKIP] Render already confirmed at {current.timestamp}")
        print(f"  Checkpoint: {current.checkpoint_path}")
        return current

    # Find storyboard
    plan_dirs = sorted(project_dir.glob("plan-*"), reverse=True)
    if not plan_dirs:
        raise RunStoryError("No plan directory found. Run earlier stages first.")

    latest_plan = plan_dirs[0]
    storyboard_path = latest_plan / "storyboard.draft.v1.json"
    if not storyboard_path.exists():
        raise RunStoryError(f"Storyboard not found: {storyboard_path}")

    # Run orchestrate_story.py
    orch_script = resolve_orchestrate_script()
    cmd = [
        "python3", str(orch_script),
        "run",
        "--storyboard", str(storyboard_path),
        "--output-dir", str(project_dir / "videos"),
    ]
    if dry_run:
        cmd.append("--dry-run")
    if continue_on_error:
        cmd.append("--continue-on-error")

    print(f"[RUN] Rendering videos...")
    print(f"  Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RunStoryError(f"Failed to render videos:\n{result.stderr}")

    output = parse_last_json(result.stdout)
    run_dir = Path(output.get("run_dir", ""))

    # Auto-concatenate videos if enabled and not dry-run
    final_video_path = None
    if auto_concat and not dry_run and run_dir.exists():
        print(f"\n[RUN] Concatenating videos into final video...")
        
        concat_script = SCRIPT_DIR / "concat_videos.py"
        concat_cmd = [
            "python3", str(concat_script),
            "--run-dir", str(run_dir),
            "--output", str(run_dir / "final-video.mp4"),
        ]
        
        concat_result = subprocess.run(concat_cmd, capture_output=True, text=True)
        if concat_result.returncode == 0:
            concat_output = parse_last_json(concat_result.stdout)
            final_video_path = concat_output.get("output_path", "")
            print(f"  Final video: {final_video_path}")
        else:
            print(f"  [WARN] Concatenation failed: {concat_result.stderr}")
            print(f"  You can manually run: python3 {concat_script} --run-dir {run_dir}")

    # Mark as pending confirmation
    notes = f"Rendered to {run_dir}"
    if final_video_path:
        notes += f", final video: {final_video_path}"
    
    checkpoint_path = save_stage_status(
        project_dir=project_dir,
        stage="render",
        confirmed=False,
        notes=notes,
    )

    print(f"\n[DONE] Render complete")
    print(f"  Run directory: {run_dir}")
    if final_video_path:
        print(f"  Final video: {final_video_path}")
    print(f"  Checkpoint: {checkpoint_path}")
    print(f"\n[ACTION] Please review videos and run: python3 {__file__} confirm --stage render")

    return load_stage_status(project_dir, "render")


def run_stages(
    project_dir: Path,
    project_id: str,
    input_text: Optional[str],
    input_file: Optional[Path],
    stage: str,
    dry_run: bool,
    continue_on_error: bool,
    auto_concat: bool = True,
) -> Dict[str, Any]:
    """Run stages up to the specified stage."""
    stages = ["outline", "episode_plan", "storyboard", "storyboard_images", "render"]

    if stage not in stages:
        raise RunStoryError(f"Invalid stage: {stage}. Must be one of: {', '.join(stages)}")

    # Run each stage in sequence
    results: Dict[str, StageStatus] = {}
    pending_confirmation_stage: Optional[str] = None

    for s in stages:
        if stages.index(s) > stages.index(stage):
            break

        existing = load_stage_status(project_dir, s)
        if existing.checkpoint_path and not existing.confirmed:
            results[s] = existing
            pending_confirmation_stage = s
            break

        if s == "outline":
            results[s] = stage_outline(
                project_dir=project_dir,
                input_text=input_text,
                input_file=input_file,
                project_id=project_id,
            )
        elif s == "episode_plan":
            results[s] = stage_episode_plan(
                project_dir=project_dir,
                project_id=project_id,
            )
        elif s == "storyboard":
            results[s] = stage_storyboard(
                project_dir=project_dir,
                project_id=project_id,
            )
        elif s == "storyboard_images":
            results[s] = stage_storyboard_images(
                project_dir=project_dir,
                project_id=project_id,
                dry_run=dry_run,
            )
        elif s == "render":
            results[s] = stage_render(
                project_dir=project_dir,
                project_id=project_id,
                dry_run=dry_run,
                continue_on_error=continue_on_error,
                auto_concat=auto_concat,
            )

        if not results[s].confirmed:
            pending_confirmation_stage = s
            break

    # Summarize results
    summary = {
        "project_dir": str(project_dir),
        "project_id": project_id,
        "stages_run": list(results.keys()),
        "pending_confirmation_stage": pending_confirmation_stage,
        "ready_to_continue": pending_confirmation_stage is None,
        "next_action": (
            f"python3 {__file__} confirm --project-dir {project_dir} --stage {pending_confirmation_stage}"
            if pending_confirmation_stage
            else "none"
        ),
        "stages_summary": [
            {
                "stage": s,
                "confirmed": results[s].confirmed,
                "timestamp": results[s].timestamp,
                "checkpoint": str(results[s].checkpoint_path) if results[s].checkpoint_path else None,
            }
            for s in results
        ],
    }

    return summary


def confirm_stage(project_dir: Path, stage: str, notes: str) -> Dict[str, Any]:
    """Confirm a stage."""
    checkpoint_path = save_stage_status(
        project_dir=project_dir,
        stage=stage,
        confirmed=True,
        notes=notes,
    )

    status = load_stage_status(project_dir, stage)

    return {
        "stage": stage,
        "confirmed": status.confirmed,
        "checkpoint": str(checkpoint_path),
        "timestamp": status.timestamp,
    }


def status_report(project_dir: Path) -> Dict[str, Any]:
    """Generate status report for all stages."""
    stages = ["outline", "episode_plan", "storyboard", "storyboard_images", "render"]
    results: List[Dict[str, Any]] = []

    for s in stages:
        status = load_stage_status(project_dir, s)
        results.append({
            "stage": s,
            "confirmed": status.confirmed,
            "timestamp": status.timestamp,
            "checkpoint": str(status.checkpoint_path) if status.checkpoint_path else None,
            "notes": status.notes,
        })

    return {
        "project_dir": str(project_dir),
        "stages": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Staged Story Workflow Runner (v0.1.6-a)")
    sub = parser.add_subparsers(dest="command", required=True)

    # Run command
    p_run = sub.add_parser("run", help="Run stages")
    p_run.add_argument("--project-dir", required=True, help="Project directory")
    p_run.add_argument("--project-id", help="Project ID")
    p_run.add_argument("--input-text", help="Input text (required for outline stage)")
    p_run.add_argument("--input-file", help="Input file (required for outline stage)")
    p_run.add_argument("--stage", default="render", help="Run up to this stage")
    p_run.add_argument("--dry-run", action="store_true", help="Dry run")
    p_run.add_argument("--continue-on-error", action="store_true", help="Continue on error")
    p_run.add_argument("--auto-concat", dest="auto_concat", action="store_true", default=True,
                       help="Auto-concatenate videos into final video (default: True)")
    p_run.add_argument("--no-auto-concat", dest="auto_concat", action="store_false",
                       help="Disable auto-concatenation")

    # Confirm command
    p_confirm = sub.add_parser("confirm", help="Confirm a stage")
    p_confirm.add_argument("--project-dir", required=True, help="Project directory")
    p_confirm.add_argument("--stage", required=True, help="Stage to confirm")
    p_confirm.add_argument("--notes", default="", help="Confirmation notes")

    # Status command
    p_status = sub.add_parser("status", help="Show status report")
    p_status.add_argument("--project-dir", required=True, help="Project directory")

    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser()
    project_dir.mkdir(parents=True, exist_ok=True)

    if args.command == "run":
        project_id = args.project_id or "project-001"
        summary = run_stages(
            project_dir=project_dir,
            project_id=project_id,
            input_text=args.input_text,
            input_file=Path(args.input_file).expanduser() if args.input_file else None,
            stage=args.stage,
            dry_run=args.dry_run,
            continue_on_error=args.continue_on_error,
            auto_concat=args.auto_concat,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.command == "confirm":
        result = confirm_stage(
            project_dir=project_dir,
            stage=args.stage,
            notes=args.notes,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == "status":
        report = status_report(project_dir=project_dir)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    try:
        main()
    except RunStoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
