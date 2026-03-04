#!/usr/bin/env python3
"""
Render subtitle-overlaid MP4 from static thumbnail + audio + srt.
Supports subtitle timing shift and custom fonts.
"""

import argparse
import re
import subprocess
from pathlib import Path


def srt_to_sec(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def sec_to_srt(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms >= 1000:
        s += 1
        ms = 0
    if s >= 60:
        m += 1
        s = 0
    if m >= 60:
        h += 1
        m = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def shift_srt(in_path: Path, out_path: Path, shift_ms: int):
    text = in_path.read_text(encoding="utf-8", errors="ignore")
    shift = shift_ms / 1000.0
    pat = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)")

    def repl(m):
        st = srt_to_sec(*m.groups()[:4]) + shift
        ed = srt_to_sec(*m.groups()[4:]) + shift
        if ed - st < 0.35:
            ed = st + 0.35
        return f"{sec_to_srt(st)} --> {sec_to_srt(ed)}"

    out_path.write_text(pat.sub(repl, text), encoding="utf-8")


def ff_escape(p: Path) -> str:
    s = str(p)
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    return s


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nokey=1:noprint_wrappers=1",
            str(path),
        ],
        text=True,
        timeout=60,
    ).strip()
    return float(out)


def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024 or u == units[-1]:
            return f"{size:.1f}{u}" if u != "B" else f"{int(size)}B"
        size /= 1024
    return f"{num_bytes}B"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--audio", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--fonts-dir", default="/home/tw2/.openclaw/workspace/archive/fonts")
    ap.add_argument("--font-name", default="Do Hyeon")
    ap.add_argument("--font-size", type=int, default=27)
    ap.add_argument("--margin-v", type=int, default=56)
    ap.add_argument("--shift-ms", type=int, default=0, help="negative = earlier")
    ap.add_argument("--crf", type=int, default=28)
    args = ap.parse_args()

    image = Path(args.image)
    audio = Path(args.audio)
    srt = Path(args.srt)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    srt_used = srt
    if args.shift_ms != 0:
        srt_used = output.with_suffix(".shifted.srt")
        shift_srt(srt, srt_used, shift_ms=args.shift_ms)

    style = (
        f"FontName={args.font_name},FontSize={args.font_size},"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00222222,BackColour=&H4A000000,"
        f"BorderStyle=3,Outline=1,Shadow=0,MarginV={args.margin_v},Alignment=2"
    )

    vf = (
        "scale=1280:720,"
        f"subtitles='{ff_escape(srt_used)}':"
        f"fontsdir='{ff_escape(Path(args.fonts_dir))}':"
        f"force_style='{style}'"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-framerate",
        "1",
        "-i",
        str(image),
        "-i",
        str(audio),
        "-vf",
        vf,
        "-r",
        "1",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        str(args.crf),
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "96k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output),
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)

    size = human_size(output.stat().st_size)
    dur = probe_duration(output)
    print(f"OUT={output.resolve()}")
    print(f"SIZE={size}")
    print(f"DURATION={dur:.3f}")


if __name__ == "__main__":
    main()
