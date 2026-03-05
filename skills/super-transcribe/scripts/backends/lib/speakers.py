"""
Shared speaker-related functions for super-transcribe backends.
Includes: speaker name mapping, speaker audio export.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .formatters import format_duration

Segment = dict[str, Any]


# ---------------------------------------------------------------------------
# Speaker name mapping
# ---------------------------------------------------------------------------


def apply_speaker_names(segments: list[Segment], names_str: str) -> list[Segment]:
    """Replace SPEAKER_1, SPEAKER_2, … with real names from a comma-separated list."""
    names = [n.strip() for n in names_str.split(",") if n.strip()]
    mapping = {}
    for seg in segments:
        raw = seg.get("speaker", "")
        if raw and raw.startswith("SPEAKER_"):
            if raw not in mapping:
                try:
                    idx = int(raw.split("_", 1)[1]) - 1
                    mapping[raw] = names[idx] if 0 <= idx < len(names) else raw
                except (ValueError, IndexError):
                    mapping[raw] = raw
            seg["speaker"] = mapping[raw]
            if seg.get("words"):
                for w in seg["words"]:
                    if w.get("speaker") == raw:
                        w["speaker"] = mapping[raw]
    return segments


# ---------------------------------------------------------------------------
# Speaker audio export
# ---------------------------------------------------------------------------


def export_speakers_audio(
    audio_path: str, segments: list[Segment], output_dir: str, quiet: bool = False
) -> None:
    """Export each speaker's audio as a separate WAV file."""
    if not shutil.which("ffmpeg"):
        print("⚠️  --export-speakers requires ffmpeg in PATH", file=sys.stderr)
        return

    speaker_ranges = {}
    for seg in segments:
        sp = seg.get("speaker")
        if not sp:
            continue
        speaker_ranges.setdefault(sp, []).append((seg["start"], seg["end"]))

    if not speaker_ranges:
        print(
            "⚠️  No speaker-labeled segments found — diarization produced no speakers.",
            file=sys.stderr,
        )
        return

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for speaker, ranges in sorted(speaker_ranges.items()):
        out_file = out_dir / f"{speaker}.wav"

        select_expr = "+".join(f"between(t,{start:.3f},{end:.3f})" for start, end in ranges)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            audio_path,
            "-af",
            f"aselect='{select_expr}',asetpts=N/SR/TB",
            str(out_file),
        ]

        total_dur = sum(e - s for s, e in ranges)
        if not quiet:
            print(
                f"🎤 Exporting {speaker}: {len(ranges)} segment(s), "
                f"{format_duration(total_dur)}...",
                file=sys.stderr,
            )

        try:
            subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL if quiet else None)
            if not quiet:
                print(f"   💾 {out_file}", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to export {speaker}: {e}", file=sys.stderr)

    if not quiet:
        print(f"✅ Speaker audio saved to: {out_dir}", file=sys.stderr)
