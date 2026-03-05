#!/usr/bin/env python3
"""
Build full-text Korean SRT from dialogue script + final audio.
- No ellipsis truncation
- Splits long lines into short readable captions
- Weighted timing by text length
"""

import argparse
import re
import subprocess
from pathlib import Path


def audio_duration_sec(path: Path) -> float:
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


def normalize_speaker(label: str) -> str:
    x = label.strip().lower()
    if x.startswith("callie"):
        return "캘리"
    if x.startswith("nick"):
        return "닉"
    return label.strip()


def split_text(text: str, max_chars: int) -> list[str]:
    # 1) punctuation chunks
    chunks = [c.strip() for c in re.split(r"(?<=[.!?…])\s+|,\s*", text) if c.strip()]
    if not chunks:
        chunks = [text.strip()]

    # 2) pack by max chars
    out: list[str] = []
    cur = ""
    for c in chunks:
        cand = (cur + " " + c).strip() if cur else c
        if len(cand) <= max_chars:
            cur = cand
            continue

        if cur:
            out.append(cur)
            cur = ""

        if len(c) <= max_chars:
            cur = c
            continue

        # hard split by words when still too long
        words = c.split(" ")
        tmp = ""
        for w in words:
            cand2 = (tmp + " " + w).strip() if tmp else w
            if len(cand2) <= max_chars:
                tmp = cand2
            else:
                if tmp:
                    out.append(tmp)
                tmp = w
        if tmp:
            cur = tmp

    if cur:
        out.append(cur)

    return out if out else [text]


def parse_dialogue_lines(script_text: str, max_chars: int) -> list[str]:
    caps: list[str] = []
    for raw in script_text.splitlines():
        s = raw.strip()
        if not s:
            continue

        if ":" in s:
            spk, txt = s.split(":", 1)
            spk = normalize_speaker(spk)
            txt = txt.strip()
            parts = split_text(txt, max_chars=max_chars)
            for i, p in enumerate(parts):
                if i == 0 and spk:
                    caps.append(f"{spk}: {p}")
                else:
                    caps.append(p)
        else:
            parts = split_text(s, max_chars=max_chars)
            caps.extend(parts)

    return caps


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


def build_timed_rows(caps: list[str], duration_sec: float, gap_sec: float, min_dur_sec: float):
    weights = [max(1, len(re.sub(r"\s+", "", c))) for c in caps]
    total_weight = sum(weights) or 1

    usable = duration_sec - gap_sec * max(0, len(caps) - 1)
    if usable < duration_sec * 0.85:
        gap_sec = 0.0
        usable = duration_sec

    segs = [usable * (w / total_weight) for w in weights]
    segs = [max(min_dur_sec, s) for s in segs]

    # normalize to usable duration
    total = sum(segs)
    scale = usable / total if total > 0 else 1.0
    segs = [s * scale for s in segs]

    rows = []
    cur = 0.0
    for i, (txt, seg) in enumerate(zip(caps, segs), 1):
        st = cur
        ed = min(duration_sec, st + seg)
        if ed <= st:
            ed = min(duration_sec, st + 0.35)
        rows.append((i, st, ed, txt))
        cur = ed + gap_sec

    if rows:
        i, st, _, txt = rows[-1]
        rows[-1] = (i, st, duration_sec, txt)

    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="dialogue script txt/md")
    ap.add_argument("--audio", required=True, help="final mp3 path")
    ap.add_argument("--output", required=True, help="output srt path")
    ap.add_argument("--max-chars", type=int, default=22)
    ap.add_argument("--gap-sec", type=float, default=0.03)
    ap.add_argument("--min-dur-sec", type=float, default=0.5)
    args = ap.parse_args()

    script_path = Path(args.script)
    audio_path = Path(args.audio)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    script_text = script_path.read_text(encoding="utf-8", errors="ignore")
    caps = parse_dialogue_lines(script_text, max_chars=args.max_chars)
    dur = audio_duration_sec(audio_path)
    rows = build_timed_rows(caps, dur, gap_sec=args.gap_sec, min_dur_sec=args.min_dur_sec)

    with out_path.open("w", encoding="utf-8") as f:
        for i, st, ed, txt in rows:
            f.write(f"{i}\n{sec_to_srt(st)} --> {sec_to_srt(ed)}\n{txt}\n\n")

    print(f"SRT={out_path.resolve()}")
    print(f"CAPTIONS={len(rows)}")
    print(f"DURATION={dur:.3f}")


if __name__ == "__main__":
    main()
