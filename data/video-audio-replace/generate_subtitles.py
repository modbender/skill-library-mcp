#!/usr/bin/env python3
"""
Generate subtitles from video using Whisper
"""

import os
import sys
import argparse
import srt
from datetime import timedelta

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Error: faster-whisper not installed.")
    print("Install with: sudo pip3 install faster-whisper --break-system-packages")
    sys.exit(1)


def format_time(seconds):
    """Format seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    ms = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def main():
    parser = argparse.ArgumentParser(description="Generate subtitles from video using Whisper")
    parser.add_argument("video", help="Input video file")
    parser.add_argument("-o", "--output", help="Output SRT file (default: video.srt)")
    parser.add_argument("-m", "--model", default="base", help="Whisper model size (tiny, base, small, medium, large)")
    parser.add_argument("-l", "--language", default="auto", help="Language code (auto for detection)")
    parser.add_argument("--device", default="cpu", help="Device: cpu, cuda")
    parser.add_argument("--compute", default="int8", help="Compute type: int8, float16")
    args = parser.parse_args()

    # Default output
    if not args.output:
        args.output = os.path.splitext(args.video)[0] + ".srt"

    print(f"Loading Whisper model: {args.model} ({args.device})...")
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute)

    print(f"Transcribing: {args.video}")
    segments, info = model.transcribe(args.video, language=args.language)

    print(f"Detected language: {info.language} ({info.language_probability:.2f})")

    # Generate SRT
    print("Generating SRT...")
    srt_content = ""
    for i, seg in enumerate(segments, 1):
        start = format_time(seg.start)
        end = format_time(seg.end)
        text = seg.text.strip()
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"✅ Subtitles saved to: {args.output}")


if __name__ == "__main__":
    main()
