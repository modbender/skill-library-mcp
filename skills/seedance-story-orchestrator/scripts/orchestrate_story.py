#!/usr/bin/env python3
"""Seedance Story Orchestrator (v0.1.1)

Orchestrate multi-shot generation by delegating per-shot execution to
seedance-video-generation's seedance.py.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_MODEL = "doubao-seedance-1-5-pro-251215"
ALLOWED_RATIOS = {"16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"}
ALLOWED_RES = {"480p", "720p", "1080p"}


class OrchestratorError(Exception):
    pass


@dataclass
class ShotResult:
    shot_id: str
    task_id: str
    status: str
    video_url: str = ""
    last_frame_url: str = ""
    output_file: str = ""
    retries_used: int = 0
    error: str = ""
    skipped: bool = False
    resumed_from_run_id: str = ""


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_seedance_script(explicit: Optional[str]) -> Path:
    candidates: List[Path] = []
    if explicit:
        candidates.append(Path(explicit).expanduser())

    env_path = os.environ.get("SEEDANCE_SCRIPT")
    if env_path:
        candidates.append(Path(env_path).expanduser())

    home = Path.home()
    candidates.extend([
        home / ".openclaw" / "skills" / "seedance-video-generation" / "seedance.py",
        Path.cwd() / "skills" / "seedance-video-generation" / "seedance.py",
        Path(__file__).resolve().parent.parent / "seedance-video-generation" / "seedance.py",
    ])

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    raise OrchestratorError(
        "Cannot find seedance.py. Set --seedance-script or SEEDANCE_SCRIPT, "
        "or install seedance-video-generation under ~/.openclaw/skills."
    )


def validate_storyboard(data: Dict[str, Any]) -> None:
    if data.get("version") != "storyboard.v1":
        raise OrchestratorError("storyboard.version must be 'storyboard.v1'.")

    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        raise OrchestratorError("storyboard.shots must be a non-empty array.")

    seen_ids = set()
    for i, shot in enumerate(shots):
        sid = shot.get("id")
        if not sid:
            raise OrchestratorError(f"shots[{i}] missing required field: id")
        if sid in seen_ids:
            raise OrchestratorError(f"Duplicate shot id: {sid}")
        seen_ids.add(sid)

        ratio = shot.get("ratio")
        if ratio and ratio not in ALLOWED_RATIOS:
            raise OrchestratorError(f"shots[{i}].ratio unsupported: {ratio}")

        resolution = shot.get("resolution")
        if resolution and resolution not in ALLOWED_RES:
            raise OrchestratorError(f"shots[{i}].resolution unsupported: {resolution}")

    global_cfg = data.get("global", {})
    if isinstance(global_cfg, dict):
        ratio = global_cfg.get("ratio")
        if ratio and ratio not in ALLOWED_RATIOS:
            raise OrchestratorError(f"global.ratio unsupported: {ratio}")
        resolution = global_cfg.get("resolution")
        if resolution and resolution not in ALLOWED_RES:
            raise OrchestratorError(f"global.resolution unsupported: {resolution}")


def run_json_command(cmd: List[str]) -> Dict[str, Any]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise OrchestratorError(
            f"Command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr.strip()}"
        )

    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise OrchestratorError(
            f"Non-JSON output from command: {' '.join(cmd)}\n"
            f"stdout:\n{stdout[:1200]}"
        ) from exc


def bool_str(v: bool) -> str:
    return "true" if v else "false"


def pick_value(shot: Dict[str, Any], global_cfg: Dict[str, Any], key: str, default: Any = None) -> Any:
    if key in shot:
        return shot.get(key)
    if key in global_cfg:
        return global_cfg.get(key)
    return default


def build_create_command(
    seedance_script: Path,
    shot: Dict[str, Any],
    global_cfg: Dict[str, Any],
    injected_first_frame: Optional[str],
) -> List[str]:
    cmd: List[str] = [
        "python3",
        str(seedance_script),
        "create",
    ]

    prompt = shot.get("prompt")
    if prompt:
        cmd.extend(["--prompt", prompt])

    image = shot.get("first_frame") or shot.get("image") or injected_first_frame
    if image:
        cmd.extend(["--image", image])

    last_frame = shot.get("last_frame")
    if last_frame:
        cmd.extend(["--last-frame", last_frame])

    ref_images = shot.get("ref_images")
    if ref_images:
        cmd.append("--ref-images")
        cmd.extend(ref_images)

    model = pick_value(shot, global_cfg, "model", DEFAULT_MODEL)
    if model:
        cmd.extend(["--model", str(model)])

    ratio = pick_value(shot, global_cfg, "ratio")
    if ratio:
        cmd.extend(["--ratio", str(ratio)])

    duration = pick_value(shot, global_cfg, "duration")
    if duration is not None:
        cmd.extend(["--duration", str(duration)])

    resolution = pick_value(shot, global_cfg, "resolution")
    if resolution:
        cmd.extend(["--resolution", str(resolution)])

    seed = pick_value(shot, global_cfg, "seed")
    if seed is not None:
        cmd.extend(["--seed", str(seed)])

    for key, flag in [
        ("camera_fixed", "--camera-fixed"),
        ("watermark", "--watermark"),
        ("generate_audio", "--generate-audio"),
        ("draft", "--draft"),
        ("return_last_frame", "--return-last-frame"),
    ]:
        val = pick_value(shot, global_cfg, key)
        if val is not None:
            cmd.extend([flag, bool_str(bool(val))])

    service_tier = pick_value(shot, global_cfg, "service_tier")
    if service_tier:
        cmd.extend(["--service-tier", str(service_tier)])

    return cmd


def wait_task_status(
    seedance_script: Path,
    task_id: str,
    poll_interval: int,
) -> Dict[str, Any]:
    while True:
        status_json = run_json_command([
            "python3", str(seedance_script), "status", task_id
        ])

        status = status_json.get("status")
        if status in {"succeeded", "failed", "expired", "cancelled"}:
            return status_json

        time.sleep(poll_interval)


def download_video(video_url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(video_url, output_path)


def load_resume_success_map(resume_summary: Optional[Path]) -> Tuple[str, Dict[str, ShotResult]]:
    if not resume_summary:
        return "", {}

    data = load_json(resume_summary)
    run_id = str(data.get("run_id", ""))
    results = data.get("results", [])
    if not isinstance(results, list):
        raise OrchestratorError("resume summary format invalid: results must be an array")

    success_map: Dict[str, ShotResult] = {}
    for item in results:
        if not isinstance(item, dict):
            continue
        shot_id = item.get("shot_id")
        if not shot_id:
            continue
        if item.get("status") != "succeeded":
            continue

        success_map[shot_id] = ShotResult(
            shot_id=shot_id,
            task_id=str(item.get("task_id", "")),
            status="succeeded",
            video_url=str(item.get("video_url", "")),
            last_frame_url=str(item.get("last_frame_url", "")),
            output_file=str(item.get("output_file", "")),
            retries_used=int(item.get("retries_used", 0) or 0),
            skipped=True,
            resumed_from_run_id=run_id,
        )

    return run_id, success_map


def write_result_index(run_dir: Path, run_id: str, project_id: str, results: List[ShotResult]) -> Tuple[Path, Path]:
    by_shot = {
        r.shot_id: {
            "status": r.status,
            "task_id": r.task_id,
            "output_file": r.output_file,
            "output_exists": bool(r.output_file and Path(r.output_file).exists()),
            "video_url": r.video_url,
            "last_frame_url": r.last_frame_url,
            "retries_used": r.retries_used,
            "skipped": r.skipped,
            "resumed_from_run_id": r.resumed_from_run_id,
            "error": r.error,
        }
        for r in results
    }

    index_json = {
        "version": "result-index.v1",
        "run_id": run_id,
        "project_id": project_id,
        "shots_total": len(results),
        "by_shot": by_shot,
    }

    json_path = run_dir / "result-index.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(index_json, f, ensure_ascii=False, indent=2)

    md_path = run_dir / "result-index.md"
    lines = [
        "# Result Index",
        "",
        "| shot_id | status | task_id | output_file | retries | skipped |",
        "|---|---|---|---|---:|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.shot_id} | {r.status} | {r.task_id or '-'} | {r.output_file or '-'} | {r.retries_used} | {'yes' if r.skipped else 'no'} |"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return json_path, md_path


def run_story(
    storyboard_path: Path,
    output_dir: Path,
    seedance_script: Path,
    poll_interval: int,
    max_retries: int,
    retry_backoff_seconds: int,
    retry_backoff_multiplier: float,
    dry_run: bool,
    resume_summary: Optional[Path],
    force_rerun_existing: bool,
    continue_on_error: bool,
) -> Dict[str, Any]:
    data = load_json(storyboard_path)
    validate_storyboard(data)

    global_cfg = data.get("global", {}) if isinstance(data.get("global"), dict) else {}
    continuity = data.get("continuity", {}) if isinstance(data.get("continuity"), dict) else {}
    chain_last_frame = bool(continuity.get("chain_last_frame", False))

    resumed_from_run_id, resume_success_map = load_resume_success_map(resume_summary)

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_dir / f"run-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results: List[ShotResult] = []
    previous_last_frame: Optional[str] = None

    shots: List[Dict[str, Any]] = data["shots"]

    for idx, shot in enumerate(shots, start=1):
        shot_id = shot["id"]

        if not force_rerun_existing and shot_id in resume_success_map:
            reused = resume_success_map[shot_id]
            results.append(reused)
            if reused.last_frame_url:
                previous_last_frame = reused.last_frame_url
            print(f"[RESUME] Shot {idx}/{len(shots)} ({shot_id}) -> reused from run {reused.resumed_from_run_id or 'unknown'}")
            continue

        injected_first_frame = None
        if chain_last_frame and not shot.get("first_frame") and not shot.get("image"):
            injected_first_frame = previous_last_frame

        create_cmd = build_create_command(seedance_script, shot, global_cfg, injected_first_frame)

        if dry_run:
            print(f"[DRY-RUN] Shot {idx}/{len(shots)} ({shot_id})")
            print("  Command:", " ".join(create_cmd))
            results.append(ShotResult(shot_id=shot_id, task_id="DRY_RUN", status="planned"))
            continue

        shot_success = False
        last_error = ""

        for attempt in range(max_retries + 1):
            try:
                print(f"[RUN] Shot {idx}/{len(shots)} ({shot_id}) attempt {attempt + 1}/{max_retries + 1}")

                create_json = run_json_command(create_cmd)
                task_id = create_json.get("task_id") or create_json.get("id")
                if not task_id:
                    raise OrchestratorError(f"Shot {shot_id}: missing task_id in create response")

                status_json = wait_task_status(seedance_script, task_id, poll_interval)
                status = status_json.get("status", "unknown")

                if status != "succeeded":
                    raise OrchestratorError(
                        f"Shot {shot_id}: task {task_id} ended with status={status}"
                    )

                content = status_json.get("content", {})
                video_url = content.get("video_url", "")
                last_frame_url = content.get("last_frame_url", "")

                output_file = ""
                if video_url:
                    filename = f"{idx:02d}-{shot_id}-{task_id}.mp4"
                    output_path = run_dir / filename
                    download_video(video_url, output_path)
                    output_file = str(output_path)

                results.append(
                    ShotResult(
                        shot_id=shot_id,
                        task_id=task_id,
                        status=status,
                        video_url=video_url,
                        last_frame_url=last_frame_url,
                        output_file=output_file,
                        retries_used=attempt,
                    )
                )

                if last_frame_url:
                    previous_last_frame = last_frame_url

                shot_success = True
                break

            except Exception as exc:
                last_error = str(exc)
                if attempt < max_retries:
                    delay = int(retry_backoff_seconds * (retry_backoff_multiplier ** attempt))
                    delay = max(1, delay)
                    print(f"[WARN] Shot {shot_id} failed on attempt {attempt + 1}: {last_error}")
                    print(f"[RETRY] Waiting {delay}s before next attempt...")
                    time.sleep(delay)
                    continue

                results.append(
                    ShotResult(
                        shot_id=shot_id,
                        task_id="",
                        status="failed",
                        retries_used=attempt,
                        error=last_error,
                    )
                )
                print(f"[ERROR] Shot {shot_id} failed after {attempt + 1} attempts")
                break

        if not shot_success and not continue_on_error:
            break

    all_done = len(results) == len(shots)
    all_success = all(r.status in {"succeeded", "planned"} for r in results)
    overall_status = "succeeded" if results and all_done and all_success else "failed"

    index_json_path, index_md_path = write_result_index(
        run_dir=run_dir,
        run_id=run_id,
        project_id=str(data.get("project_id", "")),
        results=results,
    )

    summary = {
        "version": "orchestrator-run.v1",
        "run_id": run_id,
        "project_id": data.get("project_id", ""),
        "storyboard": str(storyboard_path.resolve()),
        "seedance_script": str(seedance_script),
        "overall_status": overall_status,
        "chain_last_frame": chain_last_frame,
        "shots_total": len(shots),
        "shots_done": len(results),
        "resume_summary": str(resume_summary.resolve()) if resume_summary else "",
        "resumed_from_run_id": resumed_from_run_id,
        "index_json": str(index_json_path),
        "index_md": str(index_md_path),
        "results": [r.__dict__ for r in results],
    }

    summary_path = run_dir / "run-summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "run_dir": str(run_dir),
        "summary": str(summary_path),
        "index_json": str(index_json_path),
        "index_md": str(index_md_path),
        "overall_status": overall_status,
    }, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Seedance Story Orchestrator")
    sub = parser.add_subparsers(dest="command")

    p_run = sub.add_parser("run", help="Run storyboard generation")
    p_run.add_argument("--storyboard", required=True, help="Path to storyboard.v1 json")
    p_run.add_argument("--output-dir", default="./outputs", help="Output directory")
    p_run.add_argument("--seedance-script", help="Path to seedance.py")
    p_run.add_argument("--poll-interval", type=int, default=15, help="Poll interval seconds")
    p_run.add_argument("--max-retries", type=int, default=1, help="Retries per shot")
    p_run.add_argument("--retry-backoff-seconds", type=int, default=5, help="Base retry backoff seconds")
    p_run.add_argument("--retry-backoff-multiplier", type=float, default=2.0, help="Retry backoff multiplier")
    p_run.add_argument("--resume-summary", help="Path to previous run-summary.json for resume")
    p_run.add_argument("--force-rerun-existing", action="store_true", help="Ignore resume cache and rerun all shots")
    p_run.add_argument("--continue-on-error", action="store_true", help="Continue remaining shots even if one shot fails")
    p_run.add_argument("--dry-run", action="store_true", help="Print plan only")

    p_validate = sub.add_parser("validate", help="Validate storyboard json")
    p_validate.add_argument("--storyboard", required=True, help="Path to storyboard.v1 json")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "validate":
        data = load_json(Path(args.storyboard).expanduser())
        validate_storyboard(data)
        print(json.dumps({"ok": True, "storyboard": str(Path(args.storyboard).resolve())}, ensure_ascii=False))
        return

    if args.command == "run":
        seedance_script = resolve_seedance_script(args.seedance_script)
        run_story(
            storyboard_path=Path(args.storyboard).expanduser(),
            output_dir=Path(args.output_dir).expanduser(),
            seedance_script=seedance_script,
            poll_interval=max(2, args.poll_interval),
            max_retries=max(0, args.max_retries),
            retry_backoff_seconds=max(1, args.retry_backoff_seconds),
            retry_backoff_multiplier=max(1.0, args.retry_backoff_multiplier),
            dry_run=args.dry_run,
            resume_summary=Path(args.resume_summary).expanduser() if args.resume_summary else None,
            force_rerun_existing=args.force_rerun_existing,
            continue_on_error=args.continue_on_error,
        )
        return


if __name__ == "__main__":
    try:
        main()
    except OrchestratorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
