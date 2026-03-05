"""
Shared wav2vec2 forced alignment for super-transcribe backends.
Refines word timestamps using MMS (Massively Multilingual Speech) model.
Works with any backend that produces word-level timestamps.
"""

from __future__ import annotations

import re
import sys
from typing import Any

Segment = dict[str, Any]

# Characters to strip before alignment (numbers, punctuation except apostrophe)
_ALIGN_CLEAN = re.compile(r"[^a-z'\u00e0-\u00ff]")  # keep letters, ', accented

_align_cache = {}  # reuse model across files in batch mode


def run_alignment(
    audio_path: str, segments: list[Segment], quiet: bool = False
) -> list[Segment]:
    """Refine word timestamps using wav2vec2 forced alignment (MMS model).

    Tokenises each word into character-level token groups, concatenates
    them, runs CTC forced alignment on the segment emission, then maps
    aligned spans back to words.  Falls back per-segment on failure.
    """
    global _align_cache

    try:
        import torch
        import torchaudio
    except ImportError:
        if not quiet:
            print(
                "⚠️  torchaudio not installed — skipping alignment refinement.\n"
                "   Install with: pip install torchaudio",
                file=sys.stderr,
            )
        return segments

    if not quiet:
        print("🎯 Refining word timestamps (wav2vec2)...", file=sys.stderr)

    # --- load / cache model ---------------------------------------------------
    if "model" not in _align_cache:
        bundle = torchaudio.pipelines.MMS_FA
        model = bundle.get_model()
        try:
            if torch.cuda.is_available():
                model = model.to("cuda")
                _align_cache["device"] = "cuda"
            else:
                _align_cache["device"] = "cpu"
        except (RuntimeError,):
            _align_cache["device"] = "cpu"

        _align_cache["model"] = model
        _align_cache["tokenizer"] = bundle.get_tokenizer()
        _align_cache["aligner"] = bundle.get_aligner()
        _align_cache["sample_rate"] = bundle.sample_rate

    model = _align_cache["model"]
    tokenizer = _align_cache["tokenizer"]
    aligner = _align_cache["aligner"]
    target_sr = _align_cache["sample_rate"]
    device = _align_cache["device"]

    # --- load audio -----------------------------------------------------------
    waveform, sr = torchaudio.load(audio_path)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)  # stereo → mono
    if sr != target_sr:
        waveform = torchaudio.functional.resample(waveform, sr, target_sr)
        sr = target_sr

    # --- emissions (one pass over full audio) ---------------------------------
    with torch.inference_mode():
        emission, _ = model(waveform.to(device))
    emission = emission[0].cpu()  # (num_frames, num_classes)

    num_samples = waveform.shape[1]
    num_frames = emission.shape[0]
    frame_dur = (num_samples / num_frames) / sr  # seconds per emission frame

    aligned_count = 0

    for seg in segments:
        words = seg.get("words")
        if not words:
            continue

        # tokenise each word → list of token groups [[t], [t], ...]
        word_map = []  # (index-in-words, group_count)
        all_groups = []
        for i, w in enumerate(words):
            raw = w["word"].strip().lower()
            cleaned = _ALIGN_CLEAN.sub("", raw)
            if not cleaned:
                continue
            try:
                groups = tokenizer(cleaned)  # [[t1], [t2], ...] per char
                if groups:
                    word_map.append((i, len(groups)))
                    all_groups.extend(groups)
            except (RuntimeError, ValueError):
                continue

        if not all_groups:
            continue

        # slice emission for this segment
        seg_start_frame = max(0, int(seg["start"] / frame_dur))
        seg_end_frame = min(num_frames, int(seg["end"] / frame_dur))
        seg_emission = emission[seg_start_frame:seg_end_frame]

        if seg_emission.shape[0] < len(all_groups):
            continue

        try:
            # aligner expects List[List[int]], returns List[List[TokenSpan]]
            all_spans = aligner(seg_emission, all_groups)
        except (RuntimeError, ValueError):
            continue

        if len(all_spans) != len(all_groups):
            continue

        # map spans back to words by group count
        grp_idx = 0
        for orig_idx, count in word_map:
            char_spans = all_spans[grp_idx : grp_idx + count]
            grp_idx += count

            # each char_spans[j] is [TokenSpan, ...] for one character
            first = char_spans[0] if char_spans else []
            last = char_spans[-1] if char_spans else []
            if not first or not last:
                continue

            start_t = round((seg_start_frame + first[0].start) * frame_dur, 3)
            end_t = round((seg_start_frame + last[-1].end) * frame_dur, 3)

            words[orig_idx]["start"] = start_t
            words[orig_idx]["end"] = end_t
            aligned_count += 1

        # tighten segment boundaries to aligned words
        valid = [w for w in words if w.get("start") is not None]
        if valid:
            seg["start"] = valid[0]["start"]
            seg["end"] = valid[-1]["end"]

    if not quiet:
        print(f"   Refined {aligned_count} word timestamps", file=sys.stderr)

    return segments
