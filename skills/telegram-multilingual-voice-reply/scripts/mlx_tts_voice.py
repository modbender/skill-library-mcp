#!/usr/bin/env python3
"""Generate a Telegram-friendly voice note file from text using mlx_audio.

Why this exists:
- OpenClaw's `tts` tool may send voice/audio as a separate message and may not
  support attaching a caption in the same Telegram voice message.
- Telegram UX often expects: a *single voice message* with text shown under it.

This script generates an audio file you can send via the OpenClaw `message` tool
with `asVoice: true` and `caption: <same text>`.

It uses the mlx_audio CLI entrypoint (works with `uv tool install mlx-audio`).
Then it converts to OGG/OPUS (Telegram voice note friendly) via ffmpeg.

Example:
  python3 scripts/mlx_tts_voice.py --text "你好" --out voice.ogg
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate voice note audio (ogg/opus) from text using mlx_audio TTS.")
    ap.add_argument("--text", required=True, help="Text to speak")
    ap.add_argument(
        "--model",
        default="mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16",
        help="TTS model id (HuggingFace).",
    )
    ap.add_argument("--voice", default="Chelsie", help="Voice name (model-dependent).")
    ap.add_argument("--language", default=None, help="Optional language hint, e.g. English/Chinese (model-dependent).")
    ap.add_argument("--speed", default="1.0", help="Speed multiplier (string/float, model-dependent).")
    ap.add_argument("--out", required=True, help="Output path (.ogg recommended)")

    args = ap.parse_args()

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Locate mlx_audio CLI entrypoint
    cli = "mlx_audio.tts.generate"
    fallback = Path.home() / ".local" / "bin" / "mlx_audio.tts.generate"
    if fallback.exists():
        cli = str(fallback)

    tmpdir = Path(tempfile.mkdtemp(prefix="mlx_tts_"))
    mp3_path = tmpdir / "reply.mp3"

    cmd = [
        cli,
        "--model",
        args.model,
        "--text",
        args.text,
        "--voice",
        args.voice,
        "--speed",
        str(args.speed),
        "--output_path",
        str(tmpdir),
        "--file_prefix",
        "reply",
        "--audio_format",
        "mp3",
        "--join_audio",
    ]
    # language arg differs across models; the CLI supports --lang_code and some models accept --language.
    # We avoid guessing; only pass if user supplied it.
    if args.language:
        cmd += ["--language", args.language]

    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        print("ERROR: mlx_audio.tts.generate failed", file=sys.stderr)
        print(p.stderr or p.stdout, file=sys.stderr)
        return 3

    if not mp3_path.exists() or mp3_path.stat().st_size == 0:
        print(f"ERROR: TTS output missing/empty: {mp3_path}", file=sys.stderr)
        return 4

    # Convert to ogg/opus for Telegram voice notes
    ff = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3_path),
            "-c:a",
            "libopus",
            "-b:a",
            "24k",
            "-vbr",
            "on",
            "-application",
            "voip",
            str(out_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ff.returncode != 0 or not out_path.exists() or out_path.stat().st_size == 0:
        print("ERROR: ffmpeg opus conversion failed", file=sys.stderr)
        return 5

    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
