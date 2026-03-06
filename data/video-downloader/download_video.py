#!/usr/bin/env python3
"""Download a single online video using yt-dlp with safe defaults."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def ensure_yt_dlp() -> bool:
    """Return True when yt-dlp is available in PATH."""
    try:
        subprocess.run(
            ["yt-dlp", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def format_selector(quality: str) -> str:
    """Build yt-dlp format selector from quality choice."""
    if quality == "best":
        return "bestvideo+bestaudio/best"
    if quality == "worst":
        return "worstvideo+worstaudio/worst"

    max_height = quality.replace("p", "")
    return f"bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]"


def inspect_video(url: str) -> dict:
    """Fetch metadata without downloading."""
    result = subprocess.run(
        ["yt-dlp", "--dump-single-json", "--no-playlist", url],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def build_command(args: argparse.Namespace) -> list[str]:
    """Build the yt-dlp command from parsed arguments."""
    output_dir = Path(args.output).expanduser()
    output_template = str(output_dir / "%(title)s [%(id)s].%(ext)s")

    cmd = ["yt-dlp", "--no-playlist", "--no-progress"]

    if args.audio_only:
        cmd.extend(["-x", "--audio-format", "mp3", "--audio-quality", "0"])
    else:
        cmd.extend(["-f", format_selector(args.quality), "--merge-output-format", args.format])

    if args.restrict_filenames:
        cmd.append("--restrict-filenames")

    cmd.extend(["-o", output_template, args.url])
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download one online video with quality and format controls."
    )
    parser.add_argument("url", help="Direct video page URL")
    parser.add_argument(
        "-q",
        "--quality",
        default="best",
        choices=["best", "2160p", "1440p", "1080p", "720p", "480p", "360p", "worst"],
        help="Maximum video quality (default: best)",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="mp4",
        choices=["mp4", "webm", "mkv"],
        help="Container format for video mode (default: mp4)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="~/Downloads",
        help="Output directory (default: ~/Downloads)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Extract audio only as MP3",
    )
    parser.add_argument(
        "--print-info",
        action="store_true",
        help="Print metadata only and skip download",
    )
    parser.add_argument(
        "--restrict-filenames",
        action="store_true",
        help="Use ASCII-safe filenames",
    )
    args = parser.parse_args()

    if not ensure_yt_dlp():
        print("Error: yt-dlp is not installed or not in PATH.", file=sys.stderr)
        print("Install it first, then run this command again.", file=sys.stderr)
        return 2

    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        info = inspect_video(args.url)
    except subprocess.CalledProcessError as err:
        print("Error: failed to fetch metadata.", file=sys.stderr)
        print(err.stderr.strip(), file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print("Error: metadata response was not valid JSON.", file=sys.stderr)
        return 1

    summary = {
        "id": info.get("id"),
        "title": info.get("title"),
        "duration_seconds": info.get("duration"),
        "uploader": info.get("uploader"),
    }
    print(json.dumps(summary, indent=2))

    if args.print_info:
        return 0

    command = build_command(args)
    print("Running:", " ".join(command))

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as err:
        print(f"Error: download failed with code {err.returncode}.", file=sys.stderr)
        return err.returncode

    print("Download complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
