#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pillow>=10.0.0",
# ]
# ///
"""
TikTok Overlay Engine v3
========================
Adds animated pill-style captions + optional logo watermark to an MP4 using ffmpeg.

Usage:
  uv run tiktok_overlay_engine_v3.py \
    --input base.mp4 \
    --output overlayed.mp4 \
    --captions "Hook line!|Feature 1|Feature 2|CTA here" \
    [--logo /path/to/logo.png] \
    [--lang EN|AR] \
    [--font-size 52] \
    [--pill-color "#000000AA"] \
    [--text-color white]

Captions are split by | and timed evenly across the video duration.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def get_video_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", path],
        capture_output=True, text=True
    )
    import json
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def build_drawtext_filter(captions: list[str], duration: float, font_size: int,
                           text_color: str, pill_color: str, lang: str) -> str:
    """Build ffmpeg drawtext filter chain with timed captions."""
    segment = duration / len(captions)
    filters = []

    # For AR we flip alignment; default LTR for EN
    align_x = "w/2" if lang == "AR" else "w/2"

    for i, caption in enumerate(captions):
        start = i * segment
        end = start + segment
        # Escape special chars for ffmpeg
        safe = (caption
                .replace("'", "\\'")
                .replace(":", "\\:")
                .replace(",", "\\,"))
        f = (
            f"drawtext=text='{safe}'"
            f":fontsize={font_size}"
            f":fontcolor={text_color}"
            f":x=(w-text_w)/2"
            f":y=h*0.75"
            f":box=1:boxcolor={pill_color}:boxborderw=20"
            f":enable='between(t,{start:.2f},{end:.2f})'"
            f":alpha='if(lt(t-{start:.2f},0.3),(t-{start:.2f})/0.3,if(gt(t,{end:.2f}-0.3),(({end:.2f}-t)/0.3),1))'"
        )
        filters.append(f)

    return ",".join(filters)


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok Overlay Engine v3")
    parser.add_argument("--input", required=True, help="Input MP4 path")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--captions", required=True,
                        help="Caption lines separated by |")
    parser.add_argument("--logo", default=None, help="Optional logo PNG path")
    parser.add_argument("--lang", default="EN", choices=["EN", "AR"],
                        help="Language (affects text direction)")
    parser.add_argument("--font-size", type=int, default=52)
    parser.add_argument("--pill-color", default="black@0.65",
                        help="Box/pill background color (ffmpeg color format)")
    parser.add_argument("--text-color", default="white")
    args = parser.parse_args()

    inp = Path(args.input)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not inp.exists():
        print(f"ERROR: input file not found: {inp}", file=sys.stderr)
        sys.exit(1)

    captions = [c.strip() for c in args.captions.split("|") if c.strip()]
    if not captions:
        print("ERROR: no captions provided", file=sys.stderr)
        sys.exit(1)

    duration = get_video_duration(inp)
    print(f"Video duration: {duration:.2f}s, {len(captions)} captions")

    drawtext = build_drawtext_filter(
        captions, duration, args.font_size,
        args.text_color, args.pill_color, args.lang
    )

    # Build filter_complex
    if args.logo and Path(args.logo).exists():
        # Overlay logo top-right at 10% width
        filter_complex = (
            f"[0:v]{drawtext}[captioned];"
            f"[1:v]scale=w*0.10:-1[logo];"
            f"[captioned][logo]overlay=W-w-20:20[out]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(inp),
            "-i", args.logo,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-map", "0:a?",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            str(out)
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(inp),
            "-vf", drawtext,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k",
            str(out)
        ]

    print(f"Running ffmpeg overlay...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR:\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)

    print(f"✅ Overlay done → {out}")
    print(f"MEDIA:{out}")


if __name__ == "__main__":
    main()
