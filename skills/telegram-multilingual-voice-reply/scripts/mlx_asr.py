#!/usr/bin/env python3
"""Local wrapper for mlx_audio (default Qwen3-ASR) used by telegram-voice-smart-reply.

Goal: provide a stable, scriptable entrypoint for STT (and optional forced alignment)
that works with either:
- Python import install: `pip install mlx-audio` (importable as `mlx_audio`), OR
- uv tool install: `uv tool install mlx-audio` (CLI entrypoints exist but import may not).

Outputs:
- text: prints transcript
- json: prints a structured payload
- srt/vtt: requires Python API (segments).

Telegram voice notes are often .ogg/.opus; if CLI fallback is used, we best-effort
convert to 16k mono wav with ffmpeg.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


def _segments_to_srt(segments: List[Dict[str, Any]]) -> str:
    def fmt_ts(sec: float) -> str:
        ms = int(round(sec * 1000))
        s = ms // 1000
        ms = ms % 1000
        hh = s // 3600
        mm = (s % 3600) // 60
        ss = s % 60
        return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"

    out: List[str] = []
    for i, seg in enumerate(segments, start=1):
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 0.0))
        text = str(seg.get("text", "")).strip()
        if not text:
            continue
        out.append(str(i))
        out.append(f"{fmt_ts(start)} --> {fmt_ts(end)}")
        out.append(text)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _segments_to_vtt(segments: List[Dict[str, Any]]) -> str:
    def fmt_ts(sec: float) -> str:
        ms = int(round(sec * 1000))
        s = ms // 1000
        ms = ms % 1000
        hh = s // 3600
        mm = (s % 3600) // 60
        ss = s % 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}.{ms:03d}"

    out: List[str] = ["WEBVTT", ""]
    for seg in segments:
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 0.0))
        text = str(seg.get("text", "")).strip()
        if not text:
            continue
        out.append(f"{fmt_ts(start)} --> {fmt_ts(end)}")
        out.append(text)
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _ffmpeg_to_wav(src: Path) -> Path:
    """Convert audio to 16k mono wav using ffmpeg (best-effort)."""
    import subprocess
    import tempfile

    out = Path(tempfile.mkstemp(prefix="mlx_asr_", suffix=".wav")[1])
    cmd = ["ffmpeg", "-y", "-i", str(src), "-ac", "1", "-ar", "16000", str(out)]
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if p.returncode != 0 or not out.exists():
        raise RuntimeError("ffmpeg conversion failed")
    return out


def _run_cli(model_id: str, audio_file: Path, language: str | None, want_format: str) -> Dict[str, Any]:
    """Run mlx_audio CLI (uv-tool style) and return a payload."""
    import subprocess
    import tempfile

    cli = "mlx_audio.stt.generate"
    fallback = Path.home() / ".local" / "bin" / "mlx_audio.stt.generate"
    if fallback.exists():
        cli = str(fallback)

    # mlx_audio CLI treats --output-path as a FILE PREFIX and appends .txt/.json
    out_prefix = Path(tempfile.mkdtemp(prefix="mlx_asr_out_")) / "out"

    fmt = "txt" if want_format in ("text", "srt", "vtt") else "json"

    cmd = [
        cli,
        "--model",
        model_id,
        "--audio",
        str(audio_file),
        "--output-path",
        str(out_prefix),
        "--format",
        fmt,
    ]
    if language:
        cmd += ["--language", language]

    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "mlx_audio CLI failed")

    txt_path = Path(str(out_prefix) + ".txt")
    json_path = Path(str(out_prefix) + ".json")
    if txt_path.exists():
        text = txt_path.read_text(encoding="utf-8", errors="replace").strip()
        return {"kind": "asr", "model": model_id, "audio": str(audio_file), "language": language, "text": text, "segments": None}
    if json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
        payload.setdefault("kind", "asr")
        payload.setdefault("model", model_id)
        payload.setdefault("audio", str(audio_file))
        payload.setdefault("language", language)
        return payload

    return {"kind": "asr", "model": model_id, "audio": str(audio_file), "language": language, "text": (p.stdout or "").strip(), "segments": None}


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcribe audio with mlx_audio (Qwen3-ASR) or do forced alignment.")
    ap.add_argument("--audio", required=True, help="Path to audio file (wav/mp3/m4a/ogg/opus/...) ")
    ap.add_argument("--model", default="mlx-community/Qwen3-ASR-0.6B-8bit", help="ASR model id (HuggingFace).")
    ap.add_argument("--language", default=None, help='Language name like "English" / "Chinese". If omitted, model may auto-detect.')
    ap.add_argument("--format", default="text", choices=["text", "json", "srt", "vtt"], help="Output format for ASR. (Forced alignment always outputs JSON.)")
    ap.add_argument("--text", default=None, help="If provided, run forced alignment for this transcript instead of ASR.")
    ap.add_argument("--align-model", default="mlx-community/Qwen3-ForcedAligner-0.6B-8bit", help="Forced aligner model id.")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")

    args = ap.parse_args()

    audio_path = Path(args.audio).expanduser()
    if not audio_path.exists():
        print(f"ERROR: audio file not found: {audio_path}", file=sys.stderr)
        return 2

    # Try Python API
    load = None
    try:
        from mlx_audio.stt import load as _load  # type: ignore

        load = _load
    except Exception:
        load = None

    if load is not None:
        if args.text is not None:
            model = load(args.align_model)
            result = model.generate(audio=str(audio_path), text=args.text, language=args.language)

            items = []
            for item in getattr(result, "items", result):
                items.append(
                    {
                        "text": getattr(item, "text", None),
                        "start_time": float(getattr(item, "start_time", 0.0)),
                        "end_time": float(getattr(item, "end_time", 0.0)),
                    }
                )

            payload = {"kind": "forced_alignment", "model": args.align_model, "audio": str(audio_path), "language": args.language, "items": items}
            if args.pretty:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(payload, ensure_ascii=False))
            return 0

        # ASR
        model = load(args.model)
        result = model.generate(str(audio_path), language=args.language)

        text = getattr(result, "text", "")
        segments = getattr(result, "segments", None)

        if args.format == "text":
            sys.stdout.write(text.rstrip() + "\n")
            return 0

        payload = {
            "kind": "asr",
            "model": args.model,
            "audio": str(audio_path),
            "language": args.language,
            "text": text,
            "segments": segments,
            "stats": {
                "prompt_tokens": getattr(result, "prompt_tokens", None),
                "generation_tokens": getattr(result, "generation_tokens", None),
                "total_tokens": getattr(result, "total_tokens", None),
                "total_time": getattr(result, "total_time", None),
                "prompt_tps": getattr(result, "prompt_tps", None),
                "generation_tps": getattr(result, "generation_tps", None),
            },
        }

        if args.format == "json":
            if args.pretty:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(payload, ensure_ascii=False))
            return 0

        if not isinstance(segments, list):
            print("ERROR: model output did not include segments; cannot render srt/vtt.", file=sys.stderr)
            return 4

        if args.format == "srt":
            sys.stdout.write(_segments_to_srt(segments))
            return 0

        if args.format == "vtt":
            sys.stdout.write(_segments_to_vtt(segments))
            return 0

        print("ERROR: unreachable", file=sys.stderr)
        return 5

    # CLI fallback
    if args.text is not None:
        print("ERROR: forced alignment requires mlx_audio importable in this python interpreter.", file=sys.stderr)
        return 3

    try:
        audio_for_cli = audio_path
        if audio_for_cli.suffix.lower() in {".ogg", ".opus"}:
            audio_for_cli = _ffmpeg_to_wav(audio_for_cli)
        payload = _run_cli(args.model, audio_for_cli, args.language, args.format)
    except Exception as e:
        print(f"ERROR: mlx_audio import unavailable and CLI fallback failed: {e}", file=sys.stderr)
        return 3

    if args.format == "text":
        sys.stdout.write(str(payload.get("text", "")).rstrip() + "\n")
        return 0

    if args.format == "json":
        if args.pretty:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(payload, ensure_ascii=False))
        return 0

    print("ERROR: srt/vtt output requires mlx_audio importable in this python interpreter.", file=sys.stderr)
    return 4


if __name__ == "__main__":
    raise SystemExit(main())
