#!/usr/bin/env python3
"""Diarize an audio file with pyannote and export one concatenated WAV per speaker.

This variant *forces* the pyannote pipeline onto a specified torch device
(default: MPS) and errors if the device is unavailable.

Exports into outdir:
- diarization.rttm
- segments.jsonl
- meta.json
- <prefix>_speaker<N>.wav (concatenated segments)

Example:
  python diarize_and_slice_mps.py --input vocals.wav --outdir out --token $HF_TOKEN --prefix MyShow

Notes:
- Converts input to 16kHz mono WAV for pyannote.
- If you want to prevent silent CPU fallback for unsupported MPS ops, run with:
    PYTORCH_ENABLE_MPS_FALLBACK=0
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict

from pydub import AudioSegment


def ffmpeg_convert_to_wav_mono_16k(src: str, dst: str) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        src,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        dst,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _ensure_torchaudio_compat_shim() -> None:
    """Keep older deps happy on newer torchaudio."""
    try:
        import torchaudio  # type: ignore

        if not hasattr(torchaudio, "list_audio_backends"):

            def _list_audio_backends() -> list[str]:
                return ["ffmpeg"]

            torchaudio.list_audio_backends = _list_audio_backends  # type: ignore[attr-defined]
    except Exception:
        pass


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Input audio file (wav preferred)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--token", default=os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN"))
    ap.add_argument("--prefix", default=None, help="Prefix for exported files (e.g., Podcast)")
    ap.add_argument("--min-speakers", type=int, default=None)
    ap.add_argument("--max-speakers", type=int, default=None)
    ap.add_argument("--pad-ms", type=int, default=80, help="Pad each segment on both sides (ms)")
    ap.add_argument("--device", default="mps", help="Torch device to run on (default: mps)")
    args = ap.parse_args()

    if not args.token:
        raise SystemExit("Missing HF token. Provide --token or set HF_TOKEN.")

    os.makedirs(args.outdir, exist_ok=True)

    base = os.path.splitext(os.path.basename(args.input))[0]
    prefix = args.prefix or base

    wav16 = os.path.join(args.outdir, f"{prefix}_vocals_16k_mono.wav")
    ffmpeg_convert_to_wav_mono_16k(args.input, wav16)

    _ensure_torchaudio_compat_shim()

    import torch
    from pyannote.audio import Pipeline

    device = torch.device(args.device)
    if device.type == "mps":
        if not torch.backends.mps.is_built() or not torch.backends.mps.is_available():
            raise SystemExit("MPS requested but torch.backends.mps.is_available() is False")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=args.token,
    )

    # Move pipeline to requested device.
    try:
        pipeline.to(device)
    except Exception as e:
        raise SystemExit(f"Failed to move pyannote pipeline to device={device}: {e}")

    diarize_output = pipeline(
        {"audio": wav16},
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
    )

    # pyannote.audio 3.1 returns a `DiarizeOutput` that contains
    # `speaker_diarization` (pyannote.core.Annotation).
    annotation = (
        getattr(diarize_output, "speaker_diarization", None)
        or getattr(diarize_output, "exclusive_speaker_diarization", None)
        or diarize_output
    )

    # Save RTTM
    rttm_path = os.path.join(args.outdir, "diarization.rttm")
    with open(rttm_path, "w", encoding="utf-8") as f:
        for segment, track, speaker in annotation.itertracks(yield_label=True):
            f.write(
                f"SPEAKER {prefix} 1 {segment.start:.3f} {segment.duration:.3f} <NA> <NA> {speaker} <NA> <NA>\n"
            )

    # Save segments JSONL
    seg_path = os.path.join(args.outdir, "segments.jsonl")
    speakers = []
    segments_by_speaker = defaultdict(list)
    with open(seg_path, "w", encoding="utf-8") as f:
        for segment, _, speaker in annotation.itertracks(yield_label=True):
            speakers.append(speaker)
            rec = {
                "speaker": speaker,
                "start": float(segment.start),
                "end": float(segment.end),
                "duration": float(segment.end - segment.start),
            }
            segments_by_speaker[speaker].append(rec)
            f.write(json.dumps(rec) + "\n")

    unique_speakers = sorted(set(speakers))
    speaker_to_index = {spk: i + 1 for i, spk in enumerate(unique_speakers)}

    # Concatenate segments per speaker.
    audio = AudioSegment.from_wav(wav16)
    for spk in unique_speakers:
        out = AudioSegment.silent(duration=0, frame_rate=audio.frame_rate)
        for rec in segments_by_speaker[spk]:
            s = max(0, int(rec["start"] * 1000) - args.pad_ms)
            e = min(len(audio), int(rec["end"] * 1000) + args.pad_ms)
            out += audio[s:e]
        out_path = os.path.join(args.outdir, f"{prefix}_speaker{speaker_to_index[spk]}.wav")
        out.export(out_path, format="wav")

    meta_path = os.path.join(args.outdir, "meta.json")
    meta = {
        "input": args.input,
        "converted": wav16,
        "pipeline": "pyannote/speaker-diarization-3.1",
        "torch": getattr(torch, "__version__", None),
        "device": str(device),
        "mps_available": bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()),
        "num_speakers": len(unique_speakers),
        "speakers": unique_speakers,
        "speaker_index": speaker_to_index,
        "rttm": rttm_path,
        "segments": seg_path,
        "pad_ms": args.pad_ms,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(json.dumps({"num_speakers": len(unique_speakers), "outdir": args.outdir}, indent=2))


if __name__ == "__main__":
    main()
