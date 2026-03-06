#!/usr/bin/env python3
"""Concatenate multiple video clips into a final video.

Uses FFmpeg for concatenation. Supports both copy mode (fast) and re-encode mode.

Usage:
    python3 scripts/concat_videos.py \
        --run-dir outputs/videos/run-20260224-223000 \
        --output final-video.mp4

    python3 scripts/concat_videos.py \
        --videos clip1.mp4 clip2.mp4 clip3.mp4 \
        --output final-video.mp4
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConcatError(Exception):
    pass


def find_ffmpeg() -> str:
    """Find ffmpeg executable."""
    # Try common locations
    candidates = [
        "ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
        "/opt/homebrew/bin/ffmpeg",
    ]
    
    for cmd in candidates:
        try:
            result = subprocess.run(
                [cmd, "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return cmd
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    raise ConcatError(
        "FFmpeg not found. Please install FFmpeg:\n"
        "  macOS: brew install ffmpeg\n"
        "  Ubuntu: sudo apt install ffmpeg\n"
        "  Windows: choco install ffmpeg"
    )


def get_video_files_from_run_dir(run_dir: Path) -> List[Path]:
    """Extract video file paths from run directory, sorted by shot order."""
    # Read run-summary.json to get correct order
    summary_path = run_dir / "run-summary.json"
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        
        results = summary.get("results", [])
        video_files = []
        for r in results:
            output_file = r.get("output_file", "")
            if output_file and Path(output_file).exists():
                video_files.append(Path(output_file))
        return video_files
    
    # Fallback: glob and sort by filename
    video_files = sorted(run_dir.glob("*.mp4"))
    return video_files


def get_video_duration(video_path: Path, ffmpeg_cmd: str) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        ffmpeg_cmd.replace("ffmpeg", "ffprobe"),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError):
        pass
    
    return 0.0


def concat_videos(
    video_files: List[Path],
    output_path: Path,
    ffmpeg_cmd: str,
    re_encode: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Concatenate video files using FFmpeg concat demuxer."""
    
    if not video_files:
        raise ConcatError("No video files to concatenate")
    
    # Verify all files exist
    missing = [str(v) for v in video_files if not v.exists()]
    if missing:
        raise ConcatError(f"Missing video files: {', '.join(missing)}")
    
    # Create file list for concat demuxer
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    filelist_path = output_path.parent / f"concat-filelist-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    
    with open(filelist_path, "w", encoding="utf-8") as f:
        for video in video_files:
            # Escape single quotes in path
            safe_path = str(video.resolve()).replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")
    
    # Build FFmpeg command
    if re_encode:
        # Re-encode for compatibility (slower but more reliable)
        cmd = [
            ffmpeg_cmd,
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-movflags", "+faststart",
            "-y",
            str(output_path),
        ]
    else:
        # Stream copy (fast, but requires same codec)
        cmd = [
            ffmpeg_cmd,
            "-f", "concat",
            "-safe", "0",
            "-i", str(filelist_path),
            "-c", "copy",
            "-movflags", "+faststart",
            "-y",
            str(output_path),
        ]
    
    if dry_run:
        # Calculate total duration
        total_duration = sum(get_video_duration(v, ffmpeg_cmd) for v in video_files)
        
        return {
            "dry_run": True,
            "command": " ".join(cmd),
            "video_count": len(video_files),
            "total_duration_seconds": total_duration,
            "output_path": str(output_path),
            "filelist_path": str(filelist_path),
        }
    
    # Run FFmpeg
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour max
        )
        
        if result.returncode != 0:
            raise ConcatError(f"FFmpeg failed:\n{result.stderr}")
        
    except subprocess.TimeoutExpired:
        raise ConcatError("FFmpeg timeout (exceeded 1 hour)")
    
    finally:
        # Clean up file list
        if filelist_path.exists():
            filelist_path.unlink()
    
    # Get output file info
    output_size = output_path.stat().st_size if output_path.exists() else 0
    output_duration = get_video_duration(output_path, ffmpeg_cmd)
    
    return {
        "ok": True,
        "output_path": str(output_path),
        "video_count": len(video_files),
        "output_size_bytes": output_size,
        "output_duration_seconds": output_duration,
        "re_encoded": re_encode,
    }


def concat_from_run_dir(
    run_dir: Path,
    output_path: Optional[Path],
    ffmpeg_cmd: str,
    re_encode: bool = False,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Concatenate videos from a run directory."""
    
    video_files = get_video_files_from_run_dir(run_dir)
    
    if not video_files:
        raise ConcatError(f"No video files found in: {run_dir}")
    
    # Default output path
    if not output_path:
        output_path = run_dir / "final-video.mp4"
    
    result = concat_videos(
        video_files=video_files,
        output_path=output_path,
        ffmpeg_cmd=ffmpeg_cmd,
        re_encode=re_encode,
        dry_run=dry_run,
    )
    
    result["run_dir"] = str(run_dir)
    result["source_videos"] = [str(v) for v in video_files]
    
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Concatenate video clips into final video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From run directory (auto-detects video order from run-summary.json)
  python3 scripts/concat_videos.py --run-dir outputs/videos/run-20260224-223000

  # From explicit video list
  python3 scripts/concat_videos.py --videos clip1.mp4 clip2.mp4 clip3.mp4 --output final.mp4

  # Re-encode for compatibility
  python3 scripts/concat_videos.py --run-dir outputs/videos/run-xxx --re-encode

  # Dry run
  python3 scripts/concat_videos.py --run-dir outputs/videos/run-xxx --dry-run
""",
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--run-dir",
        help="Run directory containing video clips and run-summary.json",
    )
    input_group.add_argument(
        "--videos",
        nargs="+",
        help="List of video files to concatenate (in order)",
    )
    
    # Output options
    parser.add_argument(
        "--output",
        help="Output video path (default: run-dir/final-video.mp4 or concat-output.mp4)",
    )
    parser.add_argument(
        "--re-encode",
        action="store_true",
        help="Re-encode videos for compatibility (slower but more reliable)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actually concatenating",
    )
    
    args = parser.parse_args()
    
    # Find FFmpeg
    ffmpeg_cmd = find_ffmpeg()
    
    if args.run_dir:
        run_dir = Path(args.run_dir).expanduser()
        if not run_dir.exists():
            raise ConcatError(f"Run directory not found: {run_dir}")
        
        output_path = Path(args.output).expanduser() if args.output else None
        
        result = concat_from_run_dir(
            run_dir=run_dir,
            output_path=output_path,
            ffmpeg_cmd=ffmpeg_cmd,
            re_encode=args.re_encode,
            dry_run=args.dry_run,
        )
    
    else:
        # Explicit video list
        video_files = [Path(v).expanduser() for v in args.videos]
        
        if args.output:
            output_path = Path(args.output).expanduser()
        else:
            output_path = Path.cwd() / "concat-output.mp4"
        
        result = concat_videos(
            video_files=video_files,
            output_path=output_path,
            ffmpeg_cmd=ffmpeg_cmd,
            re_encode=args.re_encode,
            dry_run=args.dry_run,
        )
        
        result["source_videos"] = [str(v) for v in video_files]
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except ConcatError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
