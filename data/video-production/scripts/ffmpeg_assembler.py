#!/usr/bin/env python3
"""
ffmpeg_assembler.py — Stitch approved clips into a final 15s video

Reads storyboard.json for scene order. Reads feedback.json for which
scenes are approved. Chains clips with optional crossfade transitions.

Usage:
  python3 scripts/ffmpeg_assembler.py --storyboard my_project/storyboard.json
  python3 scripts/ffmpeg_assembler.py --storyboard my_project/storyboard.json --feedback my_project/feedback.json
  python3 scripts/ffmpeg_assembler.py --storyboard my_project/storyboard.json --transition crossfade
"""

import json
import sys
import shutil
import argparse
import subprocess
from pathlib import Path


def check_ffmpeg():
    if not shutil.which("ffmpeg"):
        print("✗ ffmpeg not found. Install: brew install ffmpeg")
        sys.exit(1)


def get_clip_duration(path: Path) -> float:
    """Get actual clip duration via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 5.0  # fallback


def assemble_cut(clips: list[Path], output: Path):
    """Simple cut assembly — no transitions, just concat."""
    # Write concat file
    concat_file = output.parent / "_concat.txt"
    with open(concat_file, "w") as f:
        for clip in clips:
            f.write(f"file '{clip.resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output)
    ]

    print(f"⚙  Assembling with cut transitions…")
    result = subprocess.run(cmd, capture_output=True, text=True)
    concat_file.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"✗ ffmpeg error:\n{result.stderr}")
        return False
    return True


def assemble_crossfade(clips: list[Path], output: Path, fade_dur: float = 0.5):
    """Crossfade assembly — smooth dissolve at each clip boundary."""
    print(f"⚙  Assembling with {fade_dur}s crossfade transitions…")

    if len(clips) == 1:
        # Single clip, just copy
        shutil.copy(clips[0], output)
        return True

    # Build complex filtergraph for crossfade
    # Each clip needs to be trimmed to account for overlap
    durations = [get_clip_duration(c) for c in clips]

    inputs = []
    for clip in clips:
        inputs += ["-i", str(clip)]

    # Build xfade filter chain
    # xfade expects: duration of each clip, offset = cumulative duration - fade_dur
    filter_parts = []
    n = len(clips)

    prev = f"[0:v]"
    offset = durations[0] - fade_dur

    for i in range(1, n):
        out = f"[v{i}]" if i < n - 1 else "[vout]"
        filter_parts.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade_dur}:offset={offset:.3f}{out}")
        prev = out
        if i < n - 1:
            offset += durations[i] - fade_dur

    filtergraph = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filtergraph,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-an",  # no audio for now (add music layer separately)
        "-movflags", "+faststart",
        str(output)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"✗ ffmpeg xfade error:\n{result.stderr[-800:]}")
        print("  Falling back to cut assembly…")
        return assemble_cut(clips, output)
    return True


def main():
    parser = argparse.ArgumentParser(description="Assemble approved clips into final video")
    parser.add_argument("--storyboard", "-s", required=True, help="Path to storyboard.json")
    parser.add_argument("--feedback", "-f", help="Path to feedback.json (optional — uses all clips if omitted)")
    parser.add_argument("--transition", "-t", default="cut",
                        choices=["cut", "crossfade"], help="Transition style (default: cut)")
    parser.add_argument("--fade-dur", type=float, default=0.4,
                        help="Crossfade duration in seconds (default: 0.4)")
    parser.add_argument("--output", "-o", help="Output filename (default: final.mp4 in project dir)")
    args = parser.parse_args()

    check_ffmpeg()

    storyboard_path = Path(args.storyboard)
    if not storyboard_path.exists():
        print(f"✗ Storyboard not found: {storyboard_path}")
        sys.exit(1)

    with open(storyboard_path) as f:
        sb = json.load(f)

    project_dir = storyboard_path.parent
    clips_dir = project_dir / sb.get("output_dir", "clips")

    # Load feedback if provided
    approved_ids = None
    if args.feedback:
        feedback_path = Path(args.feedback)
        if feedback_path.exists():
            with open(feedback_path) as f:
                fb = json.load(f)
            approved_ids = {s["id"] for s in fb["scenes"] if s.get("action") == "approve"}
            revise_ids = {s["id"] for s in fb["scenes"] if s.get("action") == "revise"}
            if revise_ids:
                print(f"⚠  Scenes still marked for revision: {', '.join(revise_ids)}")
                print("   Run apply_feedback.py first, or proceed with current clips.\n")

    # Collect clips in storyboard order
    clips = []
    missing = []

    for scene in sorted(sb["scenes"], key=lambda s: s.get("order", 0)):
        if approved_ids and scene["id"] not in approved_ids:
            print(f"⏭  [{scene['id']}] {scene['label']} — skipped (not approved)")
            continue

        clip_path = clips_dir / f"{scene['id']}.mp4"
        if not clip_path.exists():
            missing.append(scene["id"])
            print(f"✗  [{scene['id']}] {scene['label']} — clip missing!")
        else:
            clips.append(clip_path)
            dur = get_clip_duration(clip_path)
            print(f"✓  [{scene['id']}] {scene['label']} — {dur:.1f}s")

    if missing:
        print(f"\n✗ Cannot assemble — missing clips: {', '.join(missing)}")
        print("  Run batch_generate.py first.")
        sys.exit(1)

    if not clips:
        print("✗ No clips to assemble.")
        sys.exit(1)

    # Output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_name = sb.get("final_output", "final.mp4")
        output_path = project_dir / output_name

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🎬 Assembling {len(clips)} clips → {output_path.name}")
    print(f"   Transition: {args.transition}")

    if args.transition == "crossfade":
        success = assemble_crossfade(clips, output_path, fade_dur=args.fade_dur)
    else:
        success = assemble_cut(clips, output_path)

    if success:
        total_size = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Final video: {output_path}")
        print(f"   Size: {total_size:.1f} MB")

        # Get final duration
        final_dur = get_clip_duration(output_path)
        print(f"   Duration: {final_dur:.1f}s")

        # Auto-open
        import subprocess as sp
        sp.run(["open", str(output_path)], check=False)
    else:
        print("✗ Assembly failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
