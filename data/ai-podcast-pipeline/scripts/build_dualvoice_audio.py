#!/usr/bin/env python3
"""
Build dual-speaker podcast audio from script with chunked Gemini TTS + merge.
Designed to avoid long-request timeout failures.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def chunk_lines(lines: list[str], chunk_size: int) -> list[list[str]]:
    out = []
    for i in range(0, len(lines), chunk_size):
        out.append(lines[i : i + chunk_size])
    return out


def run_cmd(cmd: list[str], timeout: int = 1800):
    subprocess.run(cmd, check=True, timeout=timeout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="dialogue script path")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--basename", default="podcast_dualvoice_full")
    ap.add_argument("--chunk-lines", type=int, default=6)
    ap.add_argument("--timeout-seconds", type=int, default=120)
    ap.add_argument("--retries", type=int, default=3)
    # voice controls (explicit for gender clarity)
    ap.add_argument("--female-name", default="Callie")
    ap.add_argument("--female-voice", default="Kore")
    ap.add_argument("--male-name", default="Nick")
    ap.add_argument("--male-voice", default="Puck")
    args = ap.parse_args()

    inp = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    lines = [ln.strip() for ln in inp.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
    if not lines:
        raise RuntimeError("Empty input script")

    chunks_dir = outdir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    chunks = chunk_lines(lines, args.chunk_lines)
    gemini_script = Path(__file__).with_name("gemini_multispeaker_tts.py")

    generated_mp3s = []
    for i, block in enumerate(chunks, 1):
        chunk_txt = chunks_dir / f"chunk_{i:02d}.txt"
        chunk_name = f"chunk_{i:02d}"
        chunk_txt.write_text("\n".join(block) + "\n", encoding="utf-8")

        cmd = [
            sys.executable,
            str(gemini_script),
            "--input-file",
            str(chunk_txt),
            "--outdir",
            str(outdir),
            "--basename",
            chunk_name,
            "--timeout-seconds",
            str(args.timeout_seconds),
            "--retries",
            str(args.retries),
            "--female-name",
            str(args.female_name),
            "--female-voice",
            str(args.female_voice),
            "--male-name",
            str(args.male_name),
            "--male-voice",
            str(args.male_voice),
        ]
        run_cmd(cmd)
        generated_mp3s.append(outdir / f"{chunk_name}.mp3")

    parts = outdir / "parts.txt"
    parts.write_text("\n".join([f"file '{p}'" for p in generated_mp3s]) + "\n", encoding="utf-8")

    final_mp3 = outdir / f"{args.basename}.mp3"

    # concat copy first, fallback to re-encode
    try:
        run_cmd([
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(parts),
            "-c",
            "copy",
            str(final_mp3),
        ])
    except Exception:
        run_cmd([
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(parts),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            str(final_mp3),
        ])

    print(f"CHUNKS={len(chunks)}")
    print(f"FINAL_MP3={final_mp3.resolve()}")


if __name__ == "__main__":
    main()
