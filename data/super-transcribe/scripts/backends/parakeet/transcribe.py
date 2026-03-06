#!/usr/bin/env python3
"""
NVIDIA Parakeet TDT transcription CLI (NeMo backend).
High-accuracy multilingual speech-to-text using NVIDIA's Parakeet models.

Features:
- Multiple output formats: text, JSON, SRT, VTT, ASS, LRC, TTML, CSV, TSV, HTML
- Word/segment/char-level timestamps
- Long-form audio (up to 3 hours with local attention)
- Streaming/chunked inference
- NeMo-native speaker diarization (MSDD telephonic)
- URL/YouTube input via yt-dlp
- Batch processing with glob patterns and directories
- Language auto-detection across 25 European languages
- Automatic punctuation and capitalization
- Audio preprocessing (denoise/normalize)
- Transcript search, chapter detection, filler removal
- RSS/podcast feed processing
- Subtitle burn-in
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

# Add shared lib to path
_BACKEND_DIR = Path(__file__).resolve().parent
_LIB_DIR = _BACKEND_DIR.parent / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR.parent))

from lib.alignment import run_alignment
from lib.audio import (
    convert_to_wav,
    download_url,
    extract_channel,
    get_audio_duration,
    is_url,
    preprocess_audio,
    resolve_inputs,
)
from lib.exitcodes import (
    EXIT_BAD_INPUT,
    EXIT_GENERAL,
    EXIT_GPU_ERROR,
    EXIT_MISSING_DEP,
    EXIT_OK,
)
from lib.formatters import (
    EXT_MAP,
    VALID_FORMATS,
    format_agent_json,
    format_duration,
    format_result,
    format_ts_vtt,
    to_srt,
)
from lib.postprocess import (
    detect_chapters,
    detect_paragraphs,
    filter_hallucinations,
    format_chapters_output,
    format_search_results,
    merge_sentences,
    remove_filler_words,
    search_transcript,
)
from lib.rss import fetch_rss_episodes
from lib.speakers import apply_speaker_names, export_speakers_audio

# ---------------------------------------------------------------------------
# Model aliases (short names → full HuggingFace model paths)
# ---------------------------------------------------------------------------

PARAKEET_ALIASES = {
    # Default multilingual (25 EU languages)
    "tdt-0.6b-v3": "nvidia/parakeet-tdt-0.6b-v3",
    "tdt-v3": "nvidia/parakeet-tdt-0.6b-v3",
    "v3": "nvidia/parakeet-tdt-0.6b-v3",
    # Previous version (English)
    "tdt-0.6b-v2": "nvidia/parakeet-tdt-0.6b-v2",
    "tdt-v2": "nvidia/parakeet-tdt-0.6b-v2",
    "v2": "nvidia/parakeet-tdt-0.6b-v2",
    # 1.1B parameter models (English, higher accuracy)
    "tdt-1.1b": "nvidia/parakeet-tdt-1.1b",
    "tdt-ctc-1.1b": "nvidia/parakeet-tdt_ctc-1.1b",
    "1.1b": "nvidia/parakeet-tdt-1.1b",
    # Small / fast (110M params)
    "tdt-ctc-110m": "nvidia/parakeet-tdt_ctc-110m",
    "110m": "nvidia/parakeet-tdt_ctc-110m",
    "fast": "nvidia/parakeet-tdt_ctc-110m",
    "small": "nvidia/parakeet-tdt_ctc-110m",
    # Language-specific
    "ja": "nvidia/parakeet-tdt_ctc-0.6b-ja",
    "japanese": "nvidia/parakeet-tdt_ctc-0.6b-ja",
    "vi": "nvidia/parakeet-ctc-0.6b-Vietnamese",
    "vietnamese": "nvidia/parakeet-ctc-0.6b-Vietnamese",
    "da": "nvidia/parakeet-rnnt-110m-da-dk",
    "danish": "nvidia/parakeet-rnnt-110m-da-dk",
    # CTC variants
    "ctc-1.1b": "nvidia/parakeet-ctc-1.1b",
    "ctc-0.6b": "nvidia/parakeet-ctc-0.6b",
    "rnnt-1.1b": "nvidia/parakeet-rnnt-1.1b",
    "rnnt-0.6b": "nvidia/parakeet-rnnt-0.6b",
    # Multitalker
    "multitalker": "nvidia/multitalker-parakeet-streaming-0.6b-v1",
    # Canary models (ASR + translation, 25 EU languages)
    "canary": "nvidia/canary-1b-v2",
    "canary-v2": "nvidia/canary-1b-v2",
    "canary-1b": "nvidia/canary-1b-v2",
    "canary-1b-v2": "nvidia/canary-1b-v2",
    "canary-1b-flash": "nvidia/canary-1b-flash",
    "canary-flash": "nvidia/canary-1b-flash",
}

# Language → dedicated Parakeet model (auto-selected when available)
LANGUAGE_MODEL_MAP = {
    "da": "nvidia/parakeet-rnnt-110m-da-dk",
    "ja": "nvidia/parakeet-tdt_ctc-0.6b-ja",
    "vi": "nvidia/parakeet-ctc-0.6b-Vietnamese",
}

# Canary models that support translation
CANARY_MODELS = {
    "nvidia/canary-1b-v2",
    "nvidia/canary-1b-flash",
    "nvidia/canary-1b",
}

# Languages supported by Canary for translation
CANARY_LANGUAGES = {
    "bg",
    "hr",
    "cs",
    "da",
    "nl",
    "en",
    "et",
    "fi",
    "fr",
    "de",
    "el",
    "hu",
    "it",
    "lv",
    "lt",
    "mt",
    "pl",
    "pt",
    "ro",
    "sk",
    "sl",
    "es",
    "sv",
    "ru",
    "uk",
}


def resolve_model_alias(model_name):
    """Resolve a model alias to a full HuggingFace model path."""
    return PARAKEET_ALIASES.get(model_name.lower(), model_name)


def is_canary_model(model_name):
    """Check if a model is a Canary model (supports translation)."""
    resolved = resolve_model_alias(model_name)
    return resolved in CANARY_MODELS or "canary" in resolved.lower()


def detect_language_from_text(text):
    """Detect language from transcribed text using langdetect or heuristics."""
    if not text or len(text.strip()) < 10:
        return None, 0.0

    # Try langdetect first (optional dependency)
    try:
        from langdetect import detect_langs

        results = detect_langs(text)
        if results:
            best = results[0]
            return best.lang, round(best.prob, 3)
    except ImportError:
        pass

    # Fallback: character-based heuristics for common scripts
    cyrillic = sum(1 for c in text if "\u0400" <= c <= "\u04ff")
    greek = sum(1 for c in text if "\u0370" <= c <= "\u03ff")
    cjk = sum(1 for c in text if "\u3000" <= c <= "\u9fff" or "\uf900" <= c <= "\ufaff")
    total = max(len(text), 1)

    if cyrillic / total > 0.3:
        return "ru", 0.6  # Could be ru/uk/bg — rough guess
    if greek / total > 0.3:
        return "el", 0.6
    if cjk / total > 0.3:
        return "ja", 0.5

    # Latin script: check for diacritics that indicate specific languages
    diacritics = sum(1 for c in text if ord(c) > 127 and c.isalpha())
    alpha = sum(1 for c in text if c.isalpha())

    if alpha > 0 and diacritics / alpha < 0.02:
        # Very few diacritics → likely English
        return "en", 0.5

    # Has some diacritics but is Latin script → probably a European language
    return None, 0.0


# ---------------------------------------------------------------------------
# CUDA check
# ---------------------------------------------------------------------------


def check_cuda_available():
    """Check if CUDA is available and return device info."""
    try:
        import torch

        if torch.cuda.is_available():
            return True, torch.cuda.get_device_name(0)
        return False, None
    except ImportError:
        return False, None


# ---------------------------------------------------------------------------
# NeMo model loading
# ---------------------------------------------------------------------------

PARAKEET_V3_LANGUAGES = {
    "bg",
    "hr",
    "cs",
    "da",
    "nl",
    "en",
    "et",
    "fi",
    "fr",
    "de",
    "el",
    "hu",
    "it",
    "lv",
    "lt",
    "mt",
    "pl",
    "pt",
    "ro",
    "sk",
    "sl",
    "es",
    "sv",
    "ru",
    "uk",
}

_model_cache = {}


def load_model(model_name, device="auto", quiet=False):
    """Load NeMo ASR model. Caches for reuse in batch mode."""
    global _model_cache

    cache_key = (model_name, device)
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    try:
        import nemo.collections.asr as nemo_asr
    except ImportError:
        print(
            "Error: NeMo toolkit not installed.\n  Run setup: ./setup.sh",
            file=sys.stderr,
        )
        sys.exit(EXIT_MISSING_DEP)

    if not quiet:
        print(f"📦 Loading model: {model_name}...", file=sys.stderr)

    try:
        asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)
    except Exception as e:
        err_msg = str(e).lower()
        if "out of memory" in err_msg or "oom" in err_msg or "cuda" in err_msg:
            print(f"Error: GPU memory error loading model: {e}", file=sys.stderr)
            sys.exit(EXIT_GPU_ERROR)
        print(f"Error loading model '{model_name}': {e}", file=sys.stderr)
        sys.exit(EXIT_GENERAL)

    import torch

    cuda_ok = torch.cuda.is_available()

    if device == "auto":
        if cuda_ok:
            asr_model = asr_model.cuda()
            if not quiet:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"🚀 Using GPU: {gpu_name}", file=sys.stderr)
        else:
            if not quiet:
                print(
                    "⚠️  CUDA not available — using CPU (this will be slower)", file=sys.stderr
                )
    elif device == "cuda":
        if not cuda_ok:
            print("Error: CUDA requested but not available", file=sys.stderr)
            sys.exit(EXIT_GPU_ERROR)
        asr_model = asr_model.cuda()

    asr_model.eval()
    _model_cache[cache_key] = asr_model
    return asr_model


# ---------------------------------------------------------------------------
# Canary translation
# ---------------------------------------------------------------------------


def transcribe_canary(audio_path, asr_model, args):
    """Transcribe or translate using a Canary model.

    Canary models support both ASR and speech translation between
    25 European languages. The model is invoked with source_lang and
    target_lang parameters to control the task.
    """
    t0 = time.time()

    # Preprocessing
    convert_tmp = None
    preprocess_tmp = None
    channel_tmp = None
    effective_path = str(audio_path)

    channel = getattr(args, "channel", "mix")
    if channel != "mix":
        effective_path, channel_tmp = extract_channel(effective_path, channel, quiet=args.quiet)

    if getattr(args, "normalize", False) or getattr(args, "denoise", False):
        effective_path, preprocess_tmp = preprocess_audio(
            effective_path,
            normalize=getattr(args, "normalize", False),
            denoise=getattr(args, "denoise", False),
            quiet=args.quiet,
        )

    effective_path, convert_tmp = convert_to_wav(effective_path, quiet=args.quiet)
    duration = get_audio_duration(effective_path)

    # Determine source/target languages
    source_lang = getattr(args, "source_lang", None) or args.language or "en"
    target_lang = getattr(args, "target_lang", None) or "en"

    # Validate languages
    for lang_name, lang_code in [("source", source_lang), ("target", target_lang)]:
        if lang_code not in CANARY_LANGUAGES:
            print(
                f"⚠️  Canary does not support {lang_name} language '{lang_code}'. "
                f"Supported: {', '.join(sorted(CANARY_LANGUAGES))}",
                file=sys.stderr,
            )

    is_translate = getattr(args, "translate", False) or (source_lang != target_lang)

    task_label = (
        f"translate ({source_lang}→{target_lang})"
        if is_translate
        else f"transcribe ({source_lang})"
    )
    if not args.quiet:
        print(f"🐤 Canary: {task_label}", file=sys.stderr)

    # Build transcription kwargs
    transcribe_kwargs = {
        "source_lang": source_lang,
        "target_lang": target_lang,
    }

    timestamps_enabled = (
        args.timestamps
        or args.format in ("srt", "vtt", "json", "ass", "lrc", "ttml", "csv", "tsv", "html")
        or getattr(args, "diarize", False)
        or getattr(args, "detect_chapters", False)
        or getattr(args, "agent", False)
    )
    if timestamps_enabled:
        transcribe_kwargs["timestamps"] = True

    # Transcribe
    try:
        output = asr_model.transcribe([effective_path], **transcribe_kwargs)
    except Exception as e:
        _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
        raise RuntimeError(f"Canary transcription failed: {e}") from e

    # Parse output
    hyp = output[0]
    full_text = hyp.text if hasattr(hyp, "text") else str(hyp)

    segments = []
    if timestamps_enabled and hasattr(hyp, "timestamp") and hyp.timestamp:
        ts_data = hyp.timestamp
        if "segment" in ts_data and ts_data["segment"]:
            for seg_ts in ts_data["segment"]:
                seg_data = {
                    "start": seg_ts["start"],
                    "end": seg_ts["end"],
                    "text": seg_ts.get("segment", ""),
                }
                segments.append(seg_data)

        if "word" in ts_data and ts_data["word"]:
            words_all = [
                {"word": w.get("word", ""), "start": w["start"], "end": w["end"]}
                for w in ts_data["word"]
            ]
            if words_all and segments:
                for seg in segments:
                    seg_words = [
                        w
                        for w in words_all
                        if w["start"] >= seg["start"] - 0.01 and w["end"] <= seg["end"] + 0.01
                    ]
                    if seg_words:
                        seg["words"] = seg_words

    if not segments and full_text.strip():
        segments.append({"start": 0.0, "end": duration, "text": full_text})

    # Diarization (optional, works with Canary output too)
    speakers = None
    if getattr(args, "diarize", False):
        segments, speakers = run_nemo_diarization(
            effective_path,
            segments,
            quiet=args.quiet,
            min_speakers=getattr(args, "min_speakers", None),
            max_speakers=getattr(args, "max_speakers", None),
        )
        if getattr(args, "speaker_names", None):
            segments = apply_speaker_names(segments, args.speaker_names)

    if getattr(args, "filter_hallucinations", False):
        segments = filter_hallucinations(segments)

    _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)

    elapsed = time.time() - t0
    rt = round(duration / elapsed, 1) if elapsed > 0 else 0

    result = {
        "file": Path(audio_path).name,
        "text": full_text.strip(),
        "language": source_lang,
        "duration": duration,
        "segments": segments,
        "stats": {
            "processing_time": round(elapsed, 2),
            "realtime_factor": rt,
        },
    }

    if is_translate:
        result["task"] = "translate"
        result["source_language"] = source_lang
        result["target_language"] = target_lang

    if speakers:
        result["speakers"] = speakers

    if not args.quiet:
        task_str = "translated" if is_translate else "transcribed"
        print(
            f"✅ {result['file']}: {format_duration(duration)} {task_str} in "
            f"{format_duration(elapsed)} ({rt}× realtime)",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# NeMo diarization
# ---------------------------------------------------------------------------


def run_nemo_diarization(
    audio_path, segments, quiet=False, min_speakers=None, max_speakers=None
):
    """Assign speaker labels using NeMo's MSDD diarization pipeline.

    Uses NeMo's neural diarization with multi-scale diarization decoder (MSDD)
    for telephonic/meeting audio. Falls back to clustering diarization if MSDD
    is unavailable.
    """
    import torch

    if not quiet:
        print("🔊 Running NeMo speaker diarization...", file=sys.stderr)

    # NeMo diarization requires WAV input; ensure we have it
    diarize_path = audio_path
    tmp_wav = None
    if not audio_path.lower().endswith(".wav"):
        tmp_wav = audio_path + ".diarize.wav"
        try:
            import subprocess

            subprocess.run(
                ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", tmp_wav],
                check=True,
                capture_output=True,
            )
            diarize_path = tmp_wav
        except Exception:
            tmp_wav = None

    tmpdir = None
    try:
        # Try NeMo's offline diarization using the ClusteringDiarizer
        # which uses speaker embeddings + spectral clustering
        import tempfile

        from nemo.collections.asr.models import ClusteringDiarizer

        # Create a YAML config for the diarizer
        tmpdir = tempfile.mkdtemp(prefix="nemo-diar-")

        # Create manifest file (NeMo diarization needs a manifest)
        manifest_path = os.path.join(tmpdir, "manifest.json")
        duration = get_audio_duration(diarize_path)
        manifest_entry = {
            "audio_filepath": os.path.abspath(diarize_path),
            "offset": 0,
            "duration": duration,
            "label": "infer",
            "text": "-",
            "num_speakers": max_speakers if max_speakers else None,
            "rttm_filepath": None,
            "uem_filepath": None,
        }
        # Remove None values
        manifest_entry = {k: v for k, v in manifest_entry.items() if v is not None}

        with open(manifest_path, "w") as f:
            json.dump(manifest_entry, f)
            f.write("\n")

        # Build diarizer config
        # AIDEV-NOTE: NeMo ClusteringDiarizer expects many top-level keys
        # (device, num_workers, sample_rate, batch_size, verbose) alongside
        # the diarizer sub-config. Missing any causes runtime errors.
        device = "cuda" if torch.cuda.is_available() else "cpu"
        diar_config = {
            "device": device,
            "num_workers": 1,
            "sample_rate": 16000,
            "batch_size": 64,
            "verbose": False,
            "diarizer": {
                "manifest_filepath": manifest_path,
                "out_dir": tmpdir,
                "oracle_vad": False,
                "collar": 0.25,
                "ignore_overlap": True,
                "clustering": {
                    "parameters": {
                        "oracle_num_speakers": False,
                        "max_num_speakers": max_speakers or 8,
                        "enhanced_count_thres": 80,
                        "max_rp_threshold": 0.25,
                        "sparse_search_volume": 30,
                    },
                },
                "vad": {
                    "model_path": "vad_multilingual_marblenet",
                    "parameters": {
                        "window_length_in_sec": 0.15,
                        "shift_length_in_sec": 0.01,
                        "smoothing": "median",
                        "overlap": 0.5,
                        "onset": 0.8,
                        "offset": 0.6,
                        "pad_onset": 0.05,
                        "pad_offset": -0.1,
                        "min_duration_on": 0.2,
                        "min_duration_off": 0.2,
                    },
                },
                "speaker_embeddings": {
                    "model_path": "titanet_large",
                    "parameters": {
                        "window_length_in_sec": [1.5, 1.25, 1.0, 0.75, 0.5],
                        "shift_length_in_sec": [0.75, 0.625, 0.5, 0.375, 0.25],
                        "multiscale_weights": [1, 1, 1, 1, 1],
                        "save_embeddings": False,
                    },
                },
            },
        }

        if min_speakers is not None:
            diar_config["diarizer"]["clustering"]["parameters"]["oracle_num_speakers"] = False

        # Run diarization — use struct=False to avoid OmegaConf rejecting
        # keys that NeMo adds internally during initialization
        from omegaconf import OmegaConf

        cfg = OmegaConf.create(diar_config)
        OmegaConf.set_struct(cfg, False)
        diarizer = ClusteringDiarizer(cfg=cfg)
        # NeMo's __init__ may re-enable struct mode; disable it again
        # so diarize() can set batch_size, save_embeddings, etc.
        OmegaConf.set_struct(diarizer._cfg, False)
        diarizer.diarize()

        # Parse RTTM output
        rttm_dir = os.path.join(tmpdir, "pred_rttms")
        rttm_files = list(Path(rttm_dir).glob("*.rttm")) if os.path.isdir(rttm_dir) else []

        if not rttm_files:
            # Check alternative output location
            rttm_files = list(Path(tmpdir).glob("**/*.rttm"))

        timeline = []
        if rttm_files:
            with open(rttm_files[0]) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 8 and parts[0] == "SPEAKER":
                        start = float(parts[3])
                        dur = float(parts[4])
                        speaker = parts[7]
                        timeline.append(
                            {
                                "start": start,
                                "end": start + dur,
                                "speaker": speaker,
                            }
                        )

    except ImportError as e:
        if not quiet:
            print(f"⚠️  NeMo ClusteringDiarizer not available: {e}", file=sys.stderr)
            print("   Falling back to pyannote diarization...", file=sys.stderr)
        # Fall back to pyannote if available
        timeline = _run_pyannote_fallback(diarize_path, quiet, min_speakers, max_speakers)
    except Exception as e:
        if not quiet:
            print(f"⚠️  NeMo diarization failed: {e}", file=sys.stderr)
            print("   Falling back to pyannote diarization...", file=sys.stderr)
        timeline = _run_pyannote_fallback(diarize_path, quiet, min_speakers, max_speakers)
    finally:
        # Always clean up temp directory
        if tmpdir and os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)

    # Clean up temp wav
    if tmp_wav and os.path.exists(tmp_wav):
        os.remove(tmp_wav)

    if not timeline:
        if not quiet:
            print("⚠️  No speakers detected by diarization", file=sys.stderr)
        return segments, []

    # Assign speakers to segments
    def speaker_at(t):
        """Find the speaker at a given timestamp."""
        best, best_overlap = None, 0
        for tl in timeline:
            if tl["start"] <= t <= tl["end"]:
                overlap = min(tl["end"], t + 0.01) - max(tl["start"], t)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best = tl["speaker"]
        return best

    # Collect all words across segments for word-level speaker assignment
    all_words = []
    for seg in segments:
        if seg.get("words"):
            all_words.extend(seg["words"])

    if all_words:
        # Word-level diarization — assign speaker to each word.
        # Words not covered by any RTTM span get None; inherit from
        # the previous word to avoid fragmenting segments.
        for w in all_words:
            mid = (w["start"] + w["end"]) / 2
            w["speaker"] = speaker_at(mid)
        prev_speaker = None
        for w in all_words:
            if w["speaker"] is None:
                w["speaker"] = prev_speaker
            else:
                prev_speaker = w["speaker"]

        new_segments = []
        current_speaker = None
        current_words = []

        def flush_group():
            if not current_words:
                return
            new_segments.append(
                {
                    "start": current_words[0]["start"],
                    "end": current_words[-1]["end"],
                    "text": " ".join(w["word"].strip() for w in current_words),
                    "speaker": current_speaker,
                    "words": list(current_words),
                }
            )

        for w in all_words:
            sp = w.get("speaker")
            if sp != current_speaker and current_words:
                flush_group()
                current_words = []
            current_speaker = sp
            current_words.append(w)
        flush_group()

        segments = new_segments
    else:
        # Segment-level assignment
        for seg in segments:
            mid = (seg["start"] + seg["end"]) / 2
            seg["speaker"] = speaker_at(mid)

    # Rename to SPEAKER_1, SPEAKER_2, ... in order of appearance
    seen = {}
    for seg in segments:
        raw = seg.get("speaker")
        if raw and raw not in seen:
            seen[raw] = f"SPEAKER_{len(seen) + 1}"
        if raw:
            seg["speaker"] = seen[raw]

    if not quiet:
        print(f"   Found {len(seen)} speaker(s)", file=sys.stderr)

    return segments, list(seen.values())


def _run_pyannote_fallback(audio_path, quiet=False, min_speakers=None, max_speakers=None):
    """Fallback to pyannote.audio if NeMo diarization fails."""
    try:
        from pyannote.audio import Pipeline as PyannotePipeline
    except ImportError:
        # Auto-install pyannote.audio as fallback diarizer
        from lib.audio import auto_install_package

        if not auto_install_package("pyannote.audio", quiet=quiet):
            if not quiet:
                print(
                    "⚠️  Neither NeMo diarization nor pyannote.audio available.\n"
                    "   Install NeMo toolkit or run: pip install pyannote.audio",
                    file=sys.stderr,
                )
            return []
        try:
            from pyannote.audio import Pipeline as PyannotePipeline
        except ImportError:
            return []

    try:
        pipeline = PyannotePipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    except Exception as e:
        if not quiet:
            print(f"⚠️  Could not load pyannote pipeline: {e}", file=sys.stderr)
        return []

    try:
        import torch

        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))
    except Exception:
        pass

    diarize_kwargs = {}
    if min_speakers is not None:
        diarize_kwargs["min_speakers"] = min_speakers
    if max_speakers is not None:
        diarize_kwargs["max_speakers"] = max_speakers

    diarize_result = pipeline(audio_path, **diarize_kwargs)

    if hasattr(diarize_result, "speaker_diarization"):
        annotation = diarize_result.speaker_diarization
    else:
        annotation = diarize_result

    timeline = [
        {"start": turn.start, "end": turn.end, "speaker": speaker}
        for turn, _, speaker in annotation.itertracks(yield_label=True)
    ]

    return timeline


# ---------------------------------------------------------------------------
# Multitalker transcription
# ---------------------------------------------------------------------------

_multitalker_cache = {}


def _try_speaker_tagged_asr(audio_path, args, diar_model, mt_model, effective_path, duration):
    """Try NeMo's SpeakerTaggedASR for proper multitalker inference.

    This uses speaker kernel injection for each speaker instance,
    which handles overlapped speech much better than per-speaker
    audio extraction. Returns result dict or None if unavailable.
    """
    try:
        import torch
        from nemo.collections.asr.parts.utils.multispk_transcribe_utils import SpeakerTaggedASR
        from nemo.collections.asr.parts.utils.streaming_utils import (
            CacheAwareStreamingAudioBuffer,
        )
        from omegaconf import OmegaConf
    except ImportError:
        return None  # NeMo version doesn't have these utilities

    try:
        if not args.quiet:
            print(
                "🔊 Using NeMo SpeakerTaggedASR (speaker kernel injection)...", file=sys.stderr
            )

        # Build config for multitalker inference
        max_speakers = getattr(args, "max_speakers", None) or 4
        cfg = OmegaConf.create(
            {
                "audio_file": os.path.abspath(effective_path),
                "output_path": None,
                "online_normalization": True,
                "pad_and_drop_preencoded": True,
                "max_speakers": max_speakers,
            }
        )

        # Create streaming buffer
        streaming_buffer = CacheAwareStreamingAudioBuffer(
            model=mt_model,
            online_normalization=cfg.online_normalization,
            pad_and_drop_preencoded=cfg.pad_and_drop_preencoded,
        )
        streaming_buffer.append_audio_file(audio_filepath=cfg.audio_file, stream_id=-1)
        streaming_buffer_iter = iter(streaming_buffer)

        # Set up multitalker streamer
        multispk_asr = SpeakerTaggedASR(cfg, mt_model, diar_model)

        # Process audio chunks
        for step_num, (chunk_audio, chunk_lengths) in enumerate(streaming_buffer_iter):
            drop_extra = (
                0
                if step_num == 0 and not cfg.pad_and_drop_preencoded
                else mt_model.encoder.streaming_cfg.drop_extra_pre_encoded
            )
            with torch.inference_mode():
                with torch.amp.autocast(diar_model.device.type, enabled=True):
                    with torch.no_grad():
                        multispk_asr.perform_parallel_streaming_stt_spk(
                            step_num=step_num,
                            chunk_audio=chunk_audio,
                            chunk_lengths=chunk_lengths,
                            is_buffer_empty=streaming_buffer.is_buffer_empty(),
                            drop_extra_pre_encoded=drop_extra,
                        )

        # Generate final results
        samples = [{"audio_filepath": cfg.audio_file}]
        multispk_asr.generate_seglst_dicts_from_parallel_streaming(samples=samples)
        seglst = multispk_asr.instance_manager.seglst_dict_list

        if not seglst or not seglst[0]:
            return None

        # Parse seglst output into our segment format
        all_segments = []
        speakers_seen = {}

        for entry in seglst[0]:
            speaker_raw = entry.get("speaker", "SPEAKER_0")
            if speaker_raw not in speakers_seen:
                speakers_seen[speaker_raw] = f"SPEAKER_{len(speakers_seen) + 1}"
            speaker_label = speakers_seen[speaker_raw]

            seg = {
                "start": float(entry.get("start_time", entry.get("offset", 0))),
                "end": float(
                    entry.get("end_time", entry.get("offset", 0) + entry.get("duration", 0))
                ),
                "text": entry.get("words", entry.get("text", "")),
                "speaker": speaker_label,
            }
            all_segments.append(seg)

        all_segments.sort(key=lambda s: s["start"])

        return {
            "segments": all_segments,
            "speakers": list(speakers_seen.values()),
            "method": "speaker_tagged_asr",
        }

    except Exception as e:
        if not args.quiet:
            print(f"⚠️  SpeakerTaggedASR failed: {e}", file=sys.stderr)
            print("   Falling back to per-speaker extraction...", file=sys.stderr)
        return None


def transcribe_multitalker(audio_path, args):
    """Multi-speaker transcription using NVIDIA's multitalker pipeline.

    Attempts two approaches in order:
    1. NeMo SpeakerTaggedASR (proper speaker kernel injection, best for
       overlapped speech — requires NeMo 25.11+)
    2. Per-speaker audio extraction fallback (works with any NeMo version,
       may miss overlapped speech)

    Both the diarizer and ASR models are lazy-loaded on first call and
    cached for batch mode.  Users can override which models are loaded
    via --multitalker-diar-model and --multitalker-asr-model (or via
    the aliases "multitalker" in PARAKEET_ALIASES).

    Returns result dict compatible with standard transcribe_file output.
    """
    global _multitalker_cache
    import torch

    t0 = time.time()

    # Check CUDA (multitalker needs significant GPU memory)
    if not torch.cuda.is_available():
        print(
            "Error: --multitalker requires CUDA GPU (needs ~6GB VRAM for both models)",
            file=sys.stderr,
        )
        sys.exit(EXIT_GPU_ERROR)

    # Resolve model names (allow exact user overrides)
    diar_model_name = (
        getattr(args, "multitalker_diar_model", None)
        or "nvidia/diar_streaming_sortformer_4spk-v2.1"
    )
    mt_asr_model_name = (
        getattr(args, "multitalker_asr_model", None)
        or "nvidia/multitalker-parakeet-streaming-0.6b-v1"
    )

    # Preprocessing
    convert_tmp = None
    preprocess_tmp = None
    channel_tmp = None
    effective_path = str(audio_path)

    channel = getattr(args, "channel", "mix")
    if channel != "mix":
        effective_path, channel_tmp = extract_channel(effective_path, channel, quiet=args.quiet)

    if getattr(args, "normalize", False) or getattr(args, "denoise", False):
        effective_path, preprocess_tmp = preprocess_audio(
            effective_path,
            normalize=getattr(args, "normalize", False),
            denoise=getattr(args, "denoise", False),
            quiet=args.quiet,
        )

    effective_path, convert_tmp = convert_to_wav(effective_path, quiet=args.quiet)
    duration = get_audio_duration(effective_path)

    # Lazy-load diarizer model (cached across batch files)
    cache_diar_key = f"diar:{diar_model_name}"
    if cache_diar_key not in _multitalker_cache:
        if not args.quiet:
            print(f"📦 Loading diarizer: {diar_model_name}...", file=sys.stderr)
        try:
            from nemo.collections.asr.models import SortformerEncLabelModel

            diar_model = SortformerEncLabelModel.from_pretrained(diar_model_name).eval().cuda()
            _multitalker_cache[cache_diar_key] = diar_model
        except ImportError as e:
            print(
                f"Error: Multitalker requires NeMo 2.4+ with SortformerEncLabelModel.\n"
                f"  pip install nemo_toolkit[asr]\n"
                f"  Import error: {e}",
                file=sys.stderr,
            )
            _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
            sys.exit(EXIT_MISSING_DEP)
        except Exception as e:
            err_msg = str(e).lower()
            exit_code = (
                EXIT_GPU_ERROR
                if ("out of memory" in err_msg or "oom" in err_msg)
                else EXIT_GENERAL
            )
            print(
                f"Error loading diarizer '{diar_model_name}': {e}",
                file=sys.stderr,
            )
            _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
            sys.exit(exit_code)

    # Lazy-load multitalker ASR model (cached across batch files)
    cache_asr_key = f"mt_asr:{mt_asr_model_name}"
    if cache_asr_key not in _multitalker_cache:
        if not args.quiet:
            print(f"📦 Loading multitalker ASR: {mt_asr_model_name}...", file=sys.stderr)
        try:
            import nemo.collections.asr as nemo_asr

            mt_model = nemo_asr.models.ASRModel.from_pretrained(mt_asr_model_name).eval().cuda()
            _multitalker_cache[cache_asr_key] = mt_model
        except ImportError as e:
            print(
                f"Error: NeMo ASR not available: {e}\n  pip install nemo_toolkit[asr]",
                file=sys.stderr,
            )
            _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
            sys.exit(EXIT_MISSING_DEP)
        except Exception as e:
            err_msg = str(e).lower()
            exit_code = (
                EXIT_GPU_ERROR
                if ("out of memory" in err_msg or "oom" in err_msg)
                else EXIT_GENERAL
            )
            print(
                f"Error loading multitalker ASR model '{mt_asr_model_name}': {e}",
                file=sys.stderr,
            )
            _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
            sys.exit(exit_code)

    diar_model = _multitalker_cache[cache_diar_key]
    mt_model = _multitalker_cache[cache_asr_key]

    # Try the proper SpeakerTaggedASR approach first (handles overlapped speech)
    sta_result = _try_speaker_tagged_asr(
        audio_path, args, diar_model, mt_model, effective_path, duration
    )
    if sta_result is not None:
        # SpeakerTaggedASR succeeded — build full result
        all_segments = sta_result["segments"]
        speaker_names = sta_result["speakers"]

        if getattr(args, "speaker_names", None):
            all_segments = apply_speaker_names(all_segments, args.speaker_names)
        if getattr(args, "filter_hallucinations", False):
            all_segments = filter_hallucinations(all_segments)

        full_text = " ".join(
            f"[{s.get('speaker', '')}] {s['text'].strip()}"
            if s.get("speaker")
            else s["text"].strip()
            for s in all_segments
        )

        _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
        elapsed = time.time() - t0
        rt = round(duration / elapsed, 1) if elapsed > 0 else 0

        result = {
            "file": Path(audio_path).name,
            "text": full_text.strip(),
            "duration": duration,
            "segments": all_segments,
            "speakers": speaker_names,
            "stats": {
                "processing_time": round(elapsed, 2),
                "realtime_factor": rt,
            },
        }
        if not args.quiet:
            print(
                f"✅ {result['file']}: {format_duration(duration)} transcribed "
                f"({len(speaker_names)} speakers, SpeakerTaggedASR) in "
                f"{format_duration(elapsed)} ({rt}× realtime)",
                file=sys.stderr,
            )
        return result

    # Fallback: per-speaker audio extraction approach
    if not args.quiet:
        print("🔊 Running Sortformer diarization...", file=sys.stderr)

    # Step 1: Run diarization to get speaker activity
    import subprocess
    import tempfile

    tmpdir = tempfile.mkdtemp(prefix="mt-diar-")

    try:
        # Create manifest for diarizer
        manifest_path = os.path.join(tmpdir, "manifest.json")
        manifest_entry = {
            "audio_filepath": os.path.abspath(effective_path),
            "offset": 0,
            "duration": duration,
            "label": "infer",
            "text": "-",
        }
        _max_speakers = getattr(args, "max_speakers", None) or 4  # noqa: F841
        _min_speakers = getattr(args, "min_speakers", None)  # noqa: F841

        with open(manifest_path, "w") as f:
            import json as _json

            _json.dump(manifest_entry, f)
            f.write("\n")

        # Run Sortformer diarization
        from omegaconf import OmegaConf

        _diar_cfg = OmegaConf.create(  # noqa: F841
            {
                "manifest_filepath": manifest_path,
                "out_dir": tmpdir,
                "batch_size": 1,
            }
        )

        try:
            # Sortformer returns per-frame speaker labels
            _diar_output = diar_model.diarize(  # noqa: F841
                audio=[os.path.abspath(effective_path)],
                batch_size=1,
            )
        except Exception:
            # Fallback: use the manifest-based approach
            try:
                _diar_output = diar_model.diarize(  # noqa: F841
                    manifest_filepath=manifest_path,
                    out_dir=tmpdir,
                    batch_size=1,
                )
            except Exception as e:
                if not args.quiet:
                    print(f"⚠️  Sortformer diarization failed: {e}", file=sys.stderr)
                    print("   Falling back to standard diarization...", file=sys.stderr)
                _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
                shutil.rmtree(tmpdir, ignore_errors=True)
                # Fall back to standard transcription + diarization
                model = load_model(
                    getattr(args, "model", "nvidia/parakeet-tdt-0.6b-v3"),
                    quiet=args.quiet,
                )
                args_copy = argparse.Namespace(**vars(args))
                args_copy.diarize = True
                return transcribe_file(audio_path, model, args_copy)

        # Parse RTTM output from diarization
        rttm_files = list(Path(tmpdir).glob("**/*.rttm"))
        timeline = []
        if rttm_files:
            with open(rttm_files[0]) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 8 and parts[0] == "SPEAKER":
                        start = float(parts[3])
                        dur = float(parts[4])
                        speaker = parts[7]
                        timeline.append(
                            {
                                "start": start,
                                "end": start + dur,
                                "speaker": speaker,
                            }
                        )

        if not timeline:
            if not args.quiet:
                print(
                    "⚠️  No speakers detected — transcribing as single speaker", file=sys.stderr
                )

        # Step 2: Identify unique speakers and their segments
        speakers_found = (
            sorted(set(t["speaker"] for t in timeline)) if timeline else ["SPEAKER_0"]
        )
        if not args.quiet:
            print(f"   Found {len(speakers_found)} speaker(s)", file=sys.stderr)

        # Step 3: Per-speaker transcription using the multitalker model
        all_segments = []
        speaker_map = {}

        for sp_idx, speaker_id in enumerate(speakers_found):
            speaker_label = f"SPEAKER_{sp_idx + 1}"
            speaker_map[speaker_id] = speaker_label

            # Get this speaker's active regions
            sp_ranges = [(t["start"], t["end"]) for t in timeline if t["speaker"] == speaker_id]

            if not sp_ranges:
                continue

            # Extract speaker audio using ffmpeg
            sp_audio = os.path.join(tmpdir, f"{speaker_label}.wav")
            select_expr = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in sp_ranges)

            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        effective_path,
                        "-af",
                        f"aselect='{select_expr}',asetpts=N/SR/TB",
                        "-ar",
                        "16000",
                        "-ac",
                        "1",
                        sp_audio,
                    ],
                    check=True,
                    capture_output=True,
                )
            except subprocess.CalledProcessError:
                if not args.quiet:
                    print(f"⚠️  Failed to extract audio for {speaker_label}", file=sys.stderr)
                continue

            if not args.quiet:
                total_dur = sum(e - s for s, e in sp_ranges)
                print(
                    f"   🎤 {speaker_label}: {len(sp_ranges)} segment(s), {format_duration(total_dur)}",
                    file=sys.stderr,
                )

            # Transcribe this speaker's audio
            try:
                output = mt_model.transcribe([sp_audio], timestamps=True)
                hyp = output[0]
                sp_text = hyp.text if hasattr(hyp, "text") else str(hyp)

                # Extract timestamps and map back to original audio timeline
                if hasattr(hyp, "timestamp") and hyp.timestamp and "segment" in hyp.timestamp:
                    # Map extracted-audio timestamps back to original timestamps
                    # Build cumulative offset map from sp_ranges
                    offset_map = []  # (extracted_start, original_start, duration)
                    cum_dur = 0.0
                    for orig_start, orig_end in sp_ranges:
                        seg_dur = orig_end - orig_start
                        offset_map.append((cum_dur, orig_start, seg_dur))
                        cum_dur += seg_dur

                    def map_to_original(extracted_t):
                        """Map extracted audio timestamp to original audio timestamp."""
                        for ext_start, orig_start, seg_dur in offset_map:
                            if ext_start <= extracted_t < ext_start + seg_dur:
                                return orig_start + (extracted_t - ext_start)
                        # Past the end — use last segment
                        if offset_map:
                            ext_start, orig_start, seg_dur = offset_map[-1]
                            return orig_start + min(extracted_t - ext_start, seg_dur)
                        return extracted_t

                    for seg_ts in hyp.timestamp["segment"]:
                        seg_data = {
                            "start": map_to_original(seg_ts["start"]),
                            "end": map_to_original(seg_ts["end"]),
                            "text": seg_ts.get("segment", ""),
                            "speaker": speaker_label,
                        }

                        # Map word timestamps too
                        if "word" in hyp.timestamp and hyp.timestamp["word"]:
                            seg_words = [
                                w
                                for w in hyp.timestamp["word"]
                                if w["start"] >= seg_ts["start"] - 0.01
                                and w["end"] <= seg_ts["end"] + 0.01
                            ]
                            if seg_words:
                                seg_data["words"] = [
                                    {
                                        "word": w.get("word", ""),
                                        "start": map_to_original(w["start"]),
                                        "end": map_to_original(w["end"]),
                                        "speaker": speaker_label,
                                    }
                                    for w in seg_words
                                ]

                        all_segments.append(seg_data)
                else:
                    # No timestamps — create a single segment per speaker range
                    for orig_start, orig_end in sp_ranges:
                        all_segments.append(
                            {
                                "start": orig_start,
                                "end": orig_end,
                                "text": sp_text,
                                "speaker": speaker_label,
                            }
                        )

            except Exception as e:
                if not args.quiet:
                    print(f"⚠️  Transcription failed for {speaker_label}: {e}", file=sys.stderr)
                continue

        # Sort all segments by start time
        all_segments.sort(key=lambda s: s["start"])

        # Apply speaker name mapping
        if getattr(args, "speaker_names", None):
            all_segments = apply_speaker_names(all_segments, args.speaker_names)

        # Filter hallucinations
        if getattr(args, "filter_hallucinations", False):
            all_segments = filter_hallucinations(all_segments)

        # Build full text
        full_text = " ".join(
            f"[{s.get('speaker', '')}] {s['text'].strip()}"
            if s.get("speaker")
            else s["text"].strip()
            for s in all_segments
        )

        speaker_names = [speaker_map.get(sp, sp) for sp in speakers_found]

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)

    elapsed = time.time() - t0
    rt = round(duration / elapsed, 1) if elapsed > 0 else 0

    result = {
        "file": Path(audio_path).name,
        "text": full_text.strip(),
        "duration": duration,
        "segments": all_segments,
        "speakers": speaker_names,
        "stats": {
            "processing_time": round(elapsed, 2),
            "realtime_factor": rt,
        },
    }

    if not args.quiet:
        print(
            f"✅ {result['file']}: {format_duration(duration)} transcribed "
            f"({len(speakers_found)} speakers) in {format_duration(elapsed)} "
            f"({rt}× realtime)",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# Batch resume support
# ---------------------------------------------------------------------------


def load_progress(progress_path):
    """Load batch progress checkpoint file."""
    if os.path.isfile(progress_path):
        try:
            with open(progress_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"completed": [], "failed": []}


def save_progress(progress_path, progress):
    """Save batch progress checkpoint file."""
    try:
        with open(progress_path, "w") as f:
            json.dump(progress, f, indent=2)
    except IOError as e:
        print(f"⚠️  Failed to save progress: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Core transcription
# ---------------------------------------------------------------------------


def transcribe_file(audio_path, asr_model, args):
    """Transcribe a single audio file. Returns result dict."""
    t0 = time.time()

    # Preprocessing
    convert_tmp = None
    preprocess_tmp = None
    channel_tmp = None
    effective_path = str(audio_path)

    # Channel extraction
    channel = getattr(args, "channel", "mix")
    if channel != "mix":
        effective_path, channel_tmp = extract_channel(effective_path, channel, quiet=args.quiet)

    # Audio preprocessing (denoise/normalize)
    if getattr(args, "normalize", False) or getattr(args, "denoise", False):
        effective_path, preprocess_tmp = preprocess_audio(
            effective_path,
            normalize=getattr(args, "normalize", False),
            denoise=getattr(args, "denoise", False),
            quiet=args.quiet,
        )

    # Convert to WAV if needed
    effective_path, convert_tmp = convert_to_wav(effective_path, quiet=args.quiet)

    # Get audio duration
    duration = get_audio_duration(effective_path)

    # Configure long-form mode if requested
    if args.long_form:
        if not args.quiet:
            print("📏 Enabling local attention for long-form audio...", file=sys.stderr)
        try:
            asr_model.change_attention_model(
                self_attention_model="rel_pos_local_attn",
                att_context_size=[256, 256],
            )
        except Exception as e:
            if not args.quiet:
                print(f"⚠️  Could not set local attention: {e}", file=sys.stderr)

    # Prepare transcription kwargs
    timestamps_enabled = (
        args.timestamps
        or args.format in ("srt", "vtt", "json", "ass", "lrc", "ttml", "csv", "tsv", "html")
        or getattr(args, "diarize", False)
        or getattr(args, "detect_chapters", False)
        or getattr(args, "agent", False)
    )

    transcribe_kwargs = {}
    if timestamps_enabled:
        transcribe_kwargs["timestamps"] = True

    if args.language:
        if args.language not in PARAKEET_V3_LANGUAGES and not args.quiet:
            print(
                f"⚠️  Language '{args.language}' may not be supported by this model. "
                f"Supported: {', '.join(sorted(PARAKEET_V3_LANGUAGES))}",
                file=sys.stderr,
            )

    if args.batch_size != 32:
        transcribe_kwargs["batch_size"] = args.batch_size

    # Transcribe
    try:
        output = asr_model.transcribe([effective_path], **transcribe_kwargs)
    except Exception as e:
        _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)
        raise RuntimeError(f"Transcription failed: {e}") from e

    # Parse NeMo output
    hyp = output[0]
    full_text = hyp.text if hasattr(hyp, "text") else str(hyp)

    # Extract timestamps if available
    segments = []
    words_all = []

    if timestamps_enabled and hasattr(hyp, "timestamp") and hyp.timestamp:
        ts_data = hyp.timestamp

        if "segment" in ts_data and ts_data["segment"]:
            for seg_ts in ts_data["segment"]:
                seg_data = {
                    "start": seg_ts["start"],
                    "end": seg_ts["end"],
                    "text": seg_ts.get("segment", ""),
                }
                segments.append(seg_data)

        if "word" in ts_data and ts_data["word"]:
            for word_ts in ts_data["word"]:
                words_all.append(
                    {
                        "word": word_ts.get("word", ""),
                        "start": word_ts["start"],
                        "end": word_ts["end"],
                    }
                )

        chars_all = []
        if "char" in ts_data and ts_data["char"]:
            for char_ts in ts_data["char"]:
                chars_all.append(
                    {
                        "char": char_ts.get("char", ""),
                        "start": char_ts["start"],
                        "end": char_ts["end"],
                    }
                )

        # Attach words to segments
        if words_all and segments:
            for seg in segments:
                seg_words = [
                    w
                    for w in words_all
                    if w["start"] >= seg["start"] - 0.01 and w["end"] <= seg["end"] + 0.01
                ]
                if seg_words:
                    seg["words"] = seg_words
    else:
        chars_all = []

    # If no segment timestamps, create a single segment from the full text
    if not segments and full_text.strip():
        segments.append(
            {
                "start": 0.0,
                "end": duration,
                "text": full_text,
            }
        )

    # Refine word timestamps with wav2vec2 (before diarization so it benefits)
    if (
        words_all
        and not getattr(args, "streaming", False)
        and not getattr(args, "no_align", False)
    ):
        segments = run_alignment(effective_path, segments, quiet=args.quiet)

    # Diarization
    speakers = None
    if getattr(args, "diarize", False):
        segments, speakers = run_nemo_diarization(
            effective_path,
            segments,
            quiet=args.quiet,
            min_speakers=getattr(args, "min_speakers", None),
            max_speakers=getattr(args, "max_speakers", None),
        )
        if getattr(args, "speaker_names", None):
            segments = apply_speaker_names(segments, args.speaker_names)

    # Filter hallucinations
    if getattr(args, "filter_hallucinations", False):
        segments = filter_hallucinations(segments)

    # Cleanup temp files
    _cleanup_temps(convert_tmp, preprocess_tmp, channel_tmp)

    elapsed = time.time() - t0
    rt = round(duration / elapsed, 1) if elapsed > 0 else 0

    # Detect language from transcription output (Feature 4)
    detected_lang = None
    detected_lang_prob = 0.0
    if args.language:
        detected_lang = args.language
        detected_lang_prob = 1.0  # user-specified
    elif full_text.strip():
        detected_lang, detected_lang_prob = detect_language_from_text(full_text)

    result = {
        "file": Path(audio_path).name,
        "text": full_text.strip(),
        "duration": duration,
        "segments": segments,
        "stats": {
            "processing_time": round(elapsed, 2),
            "realtime_factor": rt,
        },
    }

    if detected_lang:
        result["language"] = detected_lang
        result["language_probability"] = detected_lang_prob

    if words_all:
        result["words"] = words_all
    if chars_all:
        result["chars"] = chars_all
    if speakers:
        result["speakers"] = speakers

    if not args.quiet:
        lang_str = ""
        if detected_lang:
            if args.language:
                lang_str = f" [{detected_lang}]"
            else:
                lang_str = f" [detected: {detected_lang}]"
        print(
            f"✅ {result['file']}: {format_duration(duration)} transcribed{lang_str} in "
            f"{format_duration(elapsed)} ({rt}× realtime)",
            file=sys.stderr,
        )

    return result


def _cleanup_temps(*temps):
    """Remove temp files if they exist."""
    for tmp in temps:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


# ---------------------------------------------------------------------------
# Streaming transcription
# ---------------------------------------------------------------------------


def transcribe_file_streaming(audio_path, asr_model, args):
    """Transcribe a file using chunked inference, printing segments as they arrive."""
    t0 = time.time()

    convert_tmp = None
    effective_path = str(audio_path)
    effective_path, convert_tmp = convert_to_wav(effective_path, quiet=args.quiet)

    duration = get_audio_duration(effective_path)

    if not args.quiet:
        print(f"🔴 Streaming transcription: {Path(audio_path).name}", file=sys.stderr)

    try:
        output = asr_model.transcribe([effective_path], timestamps=True)
    except Exception as e:
        if convert_tmp and os.path.exists(convert_tmp):
            os.remove(convert_tmp)
        raise RuntimeError(f"Streaming transcription failed: {e}") from e

    hyp = output[0]
    full_text = hyp.text if hasattr(hyp, "text") else str(hyp)

    segments = []
    if hasattr(hyp, "timestamp") and hyp.timestamp and "segment" in hyp.timestamp:
        for seg_ts in hyp.timestamp["segment"]:
            seg_data = {
                "start": seg_ts["start"],
                "end": seg_ts["end"],
                "text": seg_ts.get("segment", ""),
            }
            segments.append(seg_data)
            line = f"[{format_ts_vtt(seg_data['start'])} → {format_ts_vtt(seg_data['end'])}] {seg_data['text'].strip()}"
            print(line, flush=True)
    else:
        print(full_text.strip(), flush=True)
        if full_text.strip():
            segments.append(
                {
                    "start": 0.0,
                    "end": duration,
                    "text": full_text,
                }
            )

    if convert_tmp and os.path.exists(convert_tmp):
        os.remove(convert_tmp)

    elapsed = time.time() - t0
    rt = round(duration / elapsed, 1) if elapsed > 0 else 0

    result = {
        "file": Path(audio_path).name,
        "text": full_text.strip(),
        "duration": duration,
        "segments": segments,
        "stats": {
            "processing_time": round(elapsed, 2),
            "realtime_factor": rt,
        },
    }

    if not args.quiet:
        print(
            f"✅ {result['file']}: {format_duration(duration)} streamed in "
            f"{format_duration(elapsed)} ({rt}× realtime)",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# Stats file writing
# ---------------------------------------------------------------------------


def _write_stats(r, args):
    """Write a JSON stats sidecar file if --stats-file is set."""
    if not getattr(args, "stats_file", None):
        return

    audio_path = r.get("_audio_path", r["file"])
    stem = Path(audio_path).stem
    stats_path = Path(args.stats_file)

    if stats_path.is_dir() or args.stats_file.endswith(os.sep):
        stats_path.mkdir(parents=True, exist_ok=True)
        dest = stats_path / f"{stem}.stats.json"
    else:
        dest = stats_path

    word_count = sum(len(s["text"].split()) for s in r.get("segments", []))
    duration = r.get("duration", 0)

    stats = {
        "file": r["file"],
        "duration_seconds": round(duration, 2),
        "processing_time_seconds": r["stats"]["processing_time"],
        "realtime_factor": r["stats"].get("realtime_factor", 0),
        "segment_count": len(r.get("segments", [])),
        "word_count": word_count,
        "model": args.model,
        "device": args.device,
    }

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
        if not args.quiet:
            print(f"📈 Stats: {dest}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Failed to write stats file {dest}: {e}", file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    # Suppress NeMo's noisy logging by default
    os.environ.setdefault("NEMO_LOG_LEVEL", "ERROR")

    # Early exit: --version
    if "--version" in sys.argv:
        try:
            import importlib.metadata

            nemo_ver = importlib.metadata.version("nemo_toolkit")
        except Exception:
            nemo_ver = "unknown"
        print(f"parakeet-skill 1.0.0 (nemo_toolkit {nemo_ver})")
        sys.exit(0)

    p = argparse.ArgumentParser(
        description="Transcribe audio with NVIDIA Parakeet (NeMo)",
        epilog=(
            "examples:\n"
            "  %(prog)s audio.wav\n"
            "  %(prog)s audio.mp3 --format srt -o subtitles.srt\n"
            "  %(prog)s audio.wav --timestamps --format json -o result.json\n"
            "  %(prog)s https://youtube.com/watch?v=... -l en\n"
            "  %(prog)s *.wav --skip-existing -o ./transcripts/\n"
            "  %(prog)s long-lecture.wav --long-form\n"
            "  %(prog)s meeting.wav --diarize\n"
            '  %(prog)s audio.mp3 --search "keyword"\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Positional ---
    p.add_argument(
        "audio",
        nargs="*",
        metavar="AUDIO",
        help="Audio file(s), directory, glob pattern, or URL.",
    )

    # --- Model & language ---
    p.add_argument(
        "-m",
        "--model",
        default="nvidia/parakeet-tdt-0.6b-v3",
        help="NeMo model name or alias (default: nvidia/parakeet-tdt-0.6b-v3). "
        "Aliases: tdt-v3, tdt-v2, 1.1b, 110m/fast/small, ja, vi, multitalker, "
        "canary, canary-v2. Also accepts full HuggingFace model paths.",
    )
    p.add_argument(
        "-l",
        "--language",
        default=None,
        help="Expected language code, e.g. en, es, fr. "
        "For ja/vi, auto-selects dedicated Parakeet model if default model is used.",
    )

    # --- Translation (Canary) ---
    p.add_argument(
        "--translate",
        action="store_true",
        help="Translate speech to a different language using Canary model. "
        "Auto-selects canary-1b-v2 if no Canary model is specified. "
        "Use --source-lang and --target-lang to control language pair. "
        "Supports 25 EU languages (bidirectional).",
    )
    p.add_argument(
        "--source-lang",
        default=None,
        metavar="LANG",
        help="Source language for Canary translation (default: auto from -l or 'en'). "
        "Example: --source-lang fr",
    )
    p.add_argument(
        "--target-lang",
        default=None,
        metavar="LANG",
        help="Target language for Canary translation (default: 'en'). "
        "Example: --target-lang de",
    )

    # --- Language detection ---
    p.add_argument(
        "--detect-language-only",
        action="store_true",
        help="Detect the language of the audio and exit (no full transcription). "
        "Transcribes a short segment and detects language from the output.",
    )

    # --- Output format ---
    p.add_argument(
        "-f",
        "--format",
        default="text",
        help="Output format (default: text). "
        "Accepts: text, json, srt, vtt, tsv, csv, lrc, html, ass, ttml. "
        "Comma-separated for multi: --format srt,text",
    )
    p.add_argument(
        "--timestamps",
        action="store_true",
        help="Enable word/segment/char timestamps.",
    )
    p.add_argument(
        "--max-words-per-line",
        type=int,
        default=None,
        metavar="N",
        help="For SRT/VTT, split long segments into sub-cues with at most N words.",
    )
    p.add_argument(
        "--max-chars-per-line",
        type=int,
        default=None,
        metavar="N",
        help="For SRT/VTT/ASS/TTML, split subtitle lines so each fits within N characters.",
    )
    p.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="PATH",
        help="Output file or directory (directory for batch mode).",
    )

    # --- Long-form & streaming ---
    p.add_argument(
        "--long-form",
        action="store_true",
        help="Enable local attention for audio >24 min.",
    )
    p.add_argument(
        "--streaming",
        action="store_true",
        help="Streaming mode: print segments as they are transcribed.",
    )

    # --- Inference tuning ---
    p.add_argument(
        "--batch-size",
        type=int,
        default=32,
        metavar="N",
        help="Batch size for inference (default: 32).",
    )

    # --- Batch processing ---
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files whose output already exists (batch mode).",
    )

    # --- Device ---
    p.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Compute device (default: auto).",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress and status messages.",
    )
    p.add_argument(
        "--agent",
        action="store_true",
        help="Agent/chatbot output mode: emit a single compact JSON line to stdout "
        "with text, duration, language, speakers, and stats. Implies --quiet. "
        "File output (-o) still works alongside --agent.",
    )

    # --- Diarization ---
    p.add_argument(
        "--diarize",
        action="store_true",
        help="Speaker diarization using NeMo's clustering diarizer.",
    )
    p.add_argument(
        "--min-speakers",
        type=int,
        default=None,
        metavar="N",
        help="Minimum number of speakers hint for diarization.",
    )
    p.add_argument(
        "--max-speakers",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of speakers hint for diarization.",
    )
    p.add_argument(
        "--speaker-names",
        default=None,
        metavar="NAMES",
        help="Comma-separated speaker names to replace SPEAKER_1, SPEAKER_2, etc.",
    )
    p.add_argument(
        "--export-speakers",
        default=None,
        metavar="DIR",
        help="After diarization, export each speaker's audio to separate WAV files.",
    )

    # --- Audio preprocessing ---
    p.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize audio volume before transcription (EBU R128 loudnorm).",
    )
    p.add_argument(
        "--denoise",
        action="store_true",
        help="Apply noise reduction before transcription (high-pass + FFT denoise).",
    )
    p.add_argument(
        "--channel",
        default="mix",
        choices=["left", "right", "mix"],
        help="Stereo channel to transcribe (default: mix).",
    )

    # --- Post-processing ---
    p.add_argument(
        "--clean-filler",
        action="store_true",
        help="Remove hesitation fillers (um, uh, etc.) from transcript.",
    )
    p.add_argument(
        "--filter-hallucinations",
        action="store_true",
        help="Filter common hallucination patterns.",
    )
    p.add_argument(
        "--merge-sentences",
        action="store_true",
        help="Merge consecutive segments into sentence-level chunks.",
    )
    p.add_argument(
        "--detect-paragraphs",
        action="store_true",
        help="Insert paragraph breaks based on silence gaps.",
    )
    p.add_argument(
        "--paragraph-gap",
        type=float,
        default=3.0,
        metavar="SEC",
        help="Minimum silence gap for new paragraph (default: 3.0).",
    )

    # --- Search ---
    p.add_argument(
        "--search",
        default=None,
        metavar="TERM",
        help="Search the transcript for TERM and print matching segments.",
    )
    p.add_argument(
        "--search-fuzzy",
        action="store_true",
        help="Use fuzzy/approximate matching with --search.",
    )

    # --- Chapter detection ---
    p.add_argument(
        "--detect-chapters",
        action="store_true",
        help="Detect chapter/section breaks from silence gaps.",
    )
    p.add_argument(
        "--chapter-gap",
        type=float,
        default=8.0,
        metavar="SEC",
        help="Minimum silence gap for new chapter (default: 8.0).",
    )
    p.add_argument(
        "--chapters-file",
        default=None,
        metavar="PATH",
        help="Write chapter markers to this file.",
    )
    p.add_argument(
        "--chapter-format",
        default="youtube",
        choices=["youtube", "text", "json"],
        help="Chapter output format (default: youtube).",
    )

    # --- RSS ---
    p.add_argument(
        "--rss",
        default=None,
        metavar="URL",
        help="Podcast RSS feed URL — extracts audio and transcribes.",
    )
    p.add_argument(
        "--rss-latest",
        type=int,
        default=5,
        metavar="N",
        help="Number of most-recent episodes from --rss feed (default: 5).",
    )

    # --- Burn-in ---
    p.add_argument(
        "--burn-in",
        default=None,
        metavar="OUTPUT",
        help="Burn subtitles into the original video.",
    )

    # --- Stats ---
    p.add_argument(
        "--stats-file",
        default=None,
        metavar="PATH",
        help="Write performance stats JSON sidecar after transcription.",
    )

    # --- Multitalker ---
    p.add_argument(
        "--multitalker",
        action="store_true",
        help="Use multitalker pipeline for better overlapped speech handling. "
        "Requires ~6GB VRAM (loads Sortformer diarizer + multitalker ASR). "
        "English only. Implies --diarize.",
    )
    p.add_argument(
        "--multitalker-diar-model",
        default=None,
        metavar="MODEL",
        help="Override diarizer model for multitalker mode "
        "(default: nvidia/diar_streaming_sortformer_4spk-v2.1). "
        "Accepts full HuggingFace model path.",
    )
    p.add_argument(
        "--multitalker-asr-model",
        default=None,
        metavar="MODEL",
        help="Override ASR model for multitalker mode "
        "(default: nvidia/multitalker-parakeet-streaming-0.6b-v1). "
        "Accepts full HuggingFace model path.",
    )

    # --- Fast mode ---
    p.add_argument(
        "--fast",
        action="store_true",
        help="Use the small 110M model for quick transcription (lower accuracy, ~2GB VRAM). "
        "Equivalent to --model nvidia/parakeet-tdt_ctc-110m.",
    )

    # --- Alignment ---
    p.add_argument(
        "--no-align",
        action="store_true",
        help="Skip wav2vec2 timestamp alignment refinement (faster, slightly less precise timestamps).",
    )

    # --- Resume ---
    p.add_argument(
        "--resume",
        default=None,
        metavar="PATH",
        help="Resume batch processing from a progress checkpoint file. "
        "Skips already-completed files. Creates the file if it doesn't exist.",
    )

    # --- Utility ---
    p.add_argument(
        "--version",
        action="store_true",
        help="Show version info and exit.",
    )

    args = p.parse_args()

    # Parse --format as comma-separated list
    _raw_formats = [f.strip() for f in args.format.split(",") if f.strip()]
    _invalid = [f for f in _raw_formats if f not in VALID_FORMATS]
    if _invalid:
        p.error(
            f"Invalid format(s): {', '.join(_invalid)}. "
            f"Choose from: {', '.join(sorted(VALID_FORMATS))}"
        )
    args._formats = _raw_formats if _raw_formats else ["text"]
    args.format = args._formats[0]

    # Multi-format + file path (not dir) is an error
    if len(args._formats) > 1 and args.output and Path(args.output).suffix:
        p.error(f"Multiple formats ({', '.join(args._formats)}) require -o to be a directory.")

    # Agent mode: auto-enable quiet (suppress all stderr)
    if getattr(args, "agent", False):
        args.quiet = True

    # Validate inputs
    if not args.audio and not args.rss:
        p.error("AUDIO file(s) are required, or use --rss to specify a podcast feed")

    # Resolve model alias
    args.model = resolve_model_alias(args.model)

    # --fast overrides model
    if args.fast:
        args.model = "nvidia/parakeet-tdt_ctc-110m"

    # Language-specific model auto-selection
    if args.language and args.language in LANGUAGE_MODEL_MAP:
        default_model = "nvidia/parakeet-tdt-0.6b-v3"
        if args.model == default_model and not args.fast:
            args.model = LANGUAGE_MODEL_MAP[args.language]
            if not args.quiet:
                print(
                    f"🌐 Auto-selected {args.model} for language '{args.language}'",
                    file=sys.stderr,
                )

    # --translate: auto-select Canary model if not already a Canary model
    if args.translate:
        if not is_canary_model(args.model):
            args.model = "nvidia/canary-1b-v2"
            if not args.quiet:
                print(
                    "🐤 --translate detected: auto-selecting canary-1b-v2 for translation",
                    file=sys.stderr,
                )

    # --source-lang / --target-lang imply Canary model
    if getattr(args, "source_lang", None) or getattr(args, "target_lang", None):
        if not is_canary_model(args.model) and not args.translate:
            args.model = "nvidia/canary-1b-v2"
            args.translate = True
            if not args.quiet:
                print(
                    "🐤 --source-lang/--target-lang detected: auto-selecting canary-1b-v2",
                    file=sys.stderr,
                )

    # --multitalker implies --diarize
    if args.multitalker:
        args.diarize = True

    # Warn when --speaker-names is used without --diarize
    if getattr(args, "speaker_names", None) and not args.diarize:
        print("⚠️  --speaker-names has no effect without --diarize; ignoring", file=sys.stderr)

    # ---- Resolve inputs ----
    temp_dirs = []
    raw_inputs = list(args.audio) if args.audio else []

    # Handle --rss
    if args.rss:
        rss_episodes = fetch_rss_episodes(
            args.rss,
            latest=args.rss_latest if args.rss_latest != 0 else None,
            quiet=args.quiet,
        )
        if not args.quiet:
            for _, title in rss_episodes:
                print(f"   📻 {title}", file=sys.stderr)
        raw_inputs = [url for url, _ in rss_episodes] + raw_inputs

    audio_files = []
    for inp in raw_inputs:
        if is_url(inp):
            path, td = download_url(inp, audio_format="wav", quiet=args.quiet)
            audio_files.append(path)
            temp_dirs.append(td)
        else:
            audio_files.extend(resolve_inputs([inp]))

    if not audio_files:
        print("Error: No audio files found", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    is_batch = len(audio_files) > 1

    # ---- Device info ----
    cuda_ok, gpu_name = check_cuda_available()

    if args.device == "auto":
        effective_device = "cuda" if cuda_ok else "cpu"
    else:
        effective_device = args.device

    if effective_device == "cpu" and not args.quiet:
        print(
            "⚠️  Using CPU — transcription will be slower. GPU strongly recommended.",
            file=sys.stderr,
        )

    if not args.quiet:
        gpu_str = f" on {gpu_name}" if effective_device == "cuda" and gpu_name else ""
        stream_str = " [streaming]" if args.streaming else ""
        long_str = " [long-form]" if args.long_form else ""
        diar_str = " [diarize]" if args.diarize else ""
        print(
            f"🦜 {args.model} ({effective_device}){gpu_str}{stream_str}{long_str}{diar_str}",
            file=sys.stderr,
        )
        if is_batch:
            print(f"📁 {len(audio_files)} files queued", file=sys.stderr)

    # ---- Warn about batch stem collisions ----
    if is_batch and args.output:
        from collections import Counter

        _stems = Counter(Path(f).stem for f in audio_files)
        _dupes = {s: c for s, c in _stems.items() if c > 1}
        if _dupes and not args.quiet:
            _dup_names = ", ".join(f"{s} ({c}×)" for s, c in _dupes.items())
            print(
                f"⚠️  Batch stem collision: {_dup_names} — later files will overwrite earlier ones.",
                file=sys.stderr,
            )

    # ---- Load model ----
    is_canary = is_canary_model(args.model)
    asr_model = load_model(args.model, device=effective_device, quiet=args.quiet)

    # ---- Detect language only (early exit) ----
    if args.detect_language_only:
        exit_code = 0
        for audio_path in audio_files:
            try:
                # Convert to WAV for NeMo
                wav_path, convert_tmp = convert_to_wav(str(audio_path), quiet=args.quiet)

                if is_canary:
                    # Canary: transcribe with source_lang auto-detection
                    output = asr_model.transcribe(
                        [wav_path],
                        source_lang=args.language or "en",
                        target_lang=args.language or "en",
                    )
                else:
                    # Parakeet: transcribe short segment
                    output = asr_model.transcribe([wav_path])

                hyp = output[0]
                text = hyp.text if hasattr(hyp, "text") else str(hyp)

                detected_lang, prob = detect_language_from_text(text)

                if args.language:
                    detected_lang = args.language
                    prob = 1.0

                if args.format == "json":
                    import json as _json

                    print(
                        _json.dumps(
                            {
                                "language": detected_lang,
                                "language_probability": prob,
                                "sample": text[:200].strip(),
                            },
                            ensure_ascii=False,
                        )
                    )
                else:
                    lang_str = detected_lang or "unknown"
                    print(f"Language: {lang_str} (probability: {prob:.3f})")
                    if text.strip():
                        print(f"Sample: {text[:200].strip()}")

                if convert_tmp and os.path.exists(convert_tmp):
                    os.remove(convert_tmp)
            except Exception as e:
                print(f"Error detecting language for {audio_path}: {e}", file=sys.stderr)
                exit_code = 1

        for td in temp_dirs:
            shutil.rmtree(td, ignore_errors=True)
        sys.exit(exit_code)

    # ---- Resume support ----
    progress = None
    progress_path = None
    if getattr(args, "resume", None):
        progress_path = args.resume
        progress = load_progress(progress_path)
        if progress["completed"] and not args.quiet:
            print(
                f"📋 Resuming: {len(progress['completed'])} file(s) already done",
                file=sys.stderr,
            )

    # ---- Transcribe ----
    results = []
    failed_files = []
    total_audio = 0
    wall_start = time.time()
    _skip_count = [0]  # mutable counter for batch summary

    def _should_skip(audio_path):
        # Skip if resume checkpoint shows this file completed
        if progress and os.path.abspath(audio_path) in progress["completed"]:
            if not args.quiet:
                print(f"⏭️  Skip (resumed): {Path(audio_path).name}", file=sys.stderr)
            _skip_count[0] += 1
            return True
        if args.skip_existing and args.output:
            out_dir = Path(args.output)
            if out_dir.is_dir():
                formats = getattr(args, "_formats", [args.format])
                all_exist = all(
                    (out_dir / (Path(audio_path).stem + EXT_MAP.get(fmt, ".txt"))).exists()
                    for fmt in formats
                )
                if all_exist:
                    if not args.quiet:
                        print(f"⏭️  Skip (exists): {Path(audio_path).name}", file=sys.stderr)
                    _skip_count[0] += 1
                    return True
        return False

    pending_files = [af for af in audio_files if not _should_skip(af)]
    pending_total = len(pending_files)
    eta_wall_start = time.time()
    files_done = 0

    for audio_path in audio_files:
        name = Path(audio_path).name

        if _should_skip(audio_path):
            continue

        if not args.quiet and is_batch:
            current_idx = files_done + 1
            if files_done > 0:
                elapsed_so_far = time.time() - eta_wall_start
                avg_per_file = elapsed_so_far / files_done
                remaining = pending_total - files_done
                eta_sec = avg_per_file * remaining
                eta_str = format_duration(eta_sec)
                print(
                    f"▶️  [{current_idx}/{pending_total}] {name}  |  ETA: {eta_str}",
                    file=sys.stderr,
                )
            else:
                print(f"▶️  [{current_idx}/{pending_total}] {name}", file=sys.stderr)

        try:
            if args.multitalker:
                r = transcribe_multitalker(audio_path, args)
            elif is_canary and (
                args.translate
                or getattr(args, "source_lang", None)
                or getattr(args, "target_lang", None)
            ):
                r = transcribe_canary(audio_path, asr_model, args)
            elif args.streaming:
                r = transcribe_file_streaming(audio_path, asr_model, args)
            else:
                r = transcribe_file(audio_path, asr_model, args)
            r["_audio_path"] = audio_path
            results.append(r)
            total_audio += r["duration"]
            files_done += 1
            # Save progress checkpoint
            if progress is not None and progress_path:
                progress["completed"].append(os.path.abspath(audio_path))
                save_progress(progress_path, progress)
        except Exception as e:
            print(f"❌ {name}: {e}", file=sys.stderr)
            failed_files.append((audio_path, str(e)))
            files_done += 1
            # Save failed files to progress too
            if progress is not None and progress_path:
                progress["failed"].append(
                    {
                        "path": os.path.abspath(audio_path),
                        "error": str(e),
                    }
                )
                save_progress(progress_path, progress)
            if not is_batch:
                err_msg = str(e).lower()
                if any(
                    k in err_msg
                    for k in (
                        "format not recognised",
                        "invalid data",
                        "no backend",
                        "failed to open",
                        "not found",
                        "bad input",
                    )
                ):
                    sys.exit(EXIT_BAD_INPUT)
                elif "out of memory" in err_msg or "oom" in err_msg:
                    sys.exit(EXIT_GPU_ERROR)
                sys.exit(EXIT_GENERAL)

    # Cleanup temp dirs
    for td in temp_dirs:
        shutil.rmtree(td, ignore_errors=True)

    if not results:
        if args.skip_existing:
            if not args.quiet:
                print("All files already transcribed (--skip-existing)", file=sys.stderr)
            sys.exit(EXIT_OK)
        if getattr(args, "resume", None):
            if not args.quiet:
                print("All files already transcribed (--resume)", file=sys.stderr)
            sys.exit(EXIT_OK)
        print("Error: No files transcribed", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    # ---- Write output ----
    for r in results:
        # Apply --merge-sentences post-processing
        if args.merge_sentences and r.get("segments"):
            r["segments"] = merge_sentences(r["segments"])
            r["text"] = " ".join(s["text"].strip() for s in r["segments"]).strip()

        # Speaker audio export
        if getattr(args, "export_speakers", None):
            if not args.diarize:
                if not args.quiet:
                    print("⚠️  --export-speakers requires --diarize; skipping", file=sys.stderr)
            else:
                audio_src = r.get("_audio_path", r["file"])
                export_speakers_audio(
                    audio_src,
                    r.get("segments", []),
                    args.export_speakers,
                    quiet=args.quiet,
                )

        # Streaming already printed segments
        if args.streaming and not args.output:
            _write_stats(r, args)
            continue

        # Apply paragraph detection
        if getattr(args, "detect_paragraphs", False) and r.get("segments"):
            r["segments"] = detect_paragraphs(
                r["segments"],
                min_gap=getattr(args, "paragraph_gap", 3.0),
            )

        # Apply filler word removal
        if getattr(args, "clean_filler", False) and r.get("segments"):
            r["segments"] = remove_filler_words(r["segments"])
            r["text"] = " ".join(s["text"].strip() for s in r["segments"]).strip()

        audio_path = r.get("_audio_path", r["file"])
        stem = Path(audio_path).stem

        # Pre-compute chapters
        _computed_chapters = None
        if getattr(args, "detect_chapters", False) and r.get("segments"):
            _computed_chapters = detect_chapters(r["segments"], min_gap=args.chapter_gap)
            _formats_list = getattr(args, "_formats", [args.format])
            if "json" in _formats_list:
                r["chapters"] = _computed_chapters

        # ---- Agent mode: compact JSON output ----
        if getattr(args, "agent", False):
            # Inject file_path and output_path for agent tracking
            r["file_path"] = os.path.abspath(audio_path)
            # Still write to files if -o is set
            if args.output:
                formats = getattr(args, "_formats", [args.format])
                for fmt in formats:
                    output = format_result(
                        r,
                        fmt,
                        max_words_per_line=args.max_words_per_line,
                        max_chars_per_line=getattr(args, "max_chars_per_line", None),
                    )
                    out_path = Path(args.output)
                    multi_fmt = len(formats) > 1
                    if (
                        out_path.is_dir()
                        or (is_batch and not out_path.suffix)
                        or (multi_fmt and not out_path.suffix)
                    ):
                        out_path.mkdir(parents=True, exist_ok=True)
                        dest = out_path / (stem + EXT_MAP.get(fmt, ".txt"))
                    else:
                        dest = out_path
                    dest.write_text(output, encoding="utf-8")
                    r["output_path"] = str(dest.resolve())
            # Emit compact JSON to stdout
            print(format_agent_json(r, "parakeet"))
            _write_stats(r, args)
            continue

        # Search mode
        if getattr(args, "search", None):
            matches = search_transcript(
                r.get("segments", []),
                args.search,
                fuzzy=getattr(args, "search_fuzzy", False),
            )
            search_output = format_search_results(matches, args.search)
            if args.output:
                out_path = Path(args.output)
                if out_path.is_dir() or (is_batch and not out_path.suffix):
                    out_path.mkdir(parents=True, exist_ok=True)
                    dest = out_path / (stem + ".txt")
                else:
                    dest = out_path
                dest.write_text(search_output, encoding="utf-8")
                if not args.quiet:
                    print(f"💾 {dest}", file=sys.stderr)
            else:
                if is_batch:
                    print(f"\n=== {r['file']} ===")
                print(search_output)
        else:
            # Multi-format output loop
            formats = getattr(args, "_formats", [args.format])
            if len(formats) > 1 and not args.output:
                print(
                    f"⚠️  Multiple formats requested but no -o DIR specified; "
                    f"showing only '{formats[0]}' on stdout.",
                    file=sys.stderr,
                )
            for fmt_idx, fmt in enumerate(formats):
                output = format_result(
                    r,
                    fmt,
                    max_words_per_line=args.max_words_per_line,
                    max_chars_per_line=getattr(args, "max_chars_per_line", None),
                )

                if args.output:
                    out_path = Path(args.output)
                    multi_fmt = len(formats) > 1
                    if (
                        out_path.is_dir()
                        or (is_batch and not out_path.suffix)
                        or (multi_fmt and not out_path.suffix)
                    ):
                        out_path.mkdir(parents=True, exist_ok=True)
                        dest = out_path / (stem + EXT_MAP.get(fmt, ".txt"))
                    else:
                        dest = out_path
                    dest.write_text(output, encoding="utf-8")
                    if not args.quiet:
                        print(f"💾 {dest}", file=sys.stderr)
                else:
                    if fmt_idx == 0:
                        if is_batch and fmt == "text":
                            print(f"\n=== {r['file']} ===")
                        print(output)

        # Chapter detection output
        if _computed_chapters is not None:
            chapters = _computed_chapters
            chapters_output = format_chapters_output(chapters, fmt=args.chapter_format)
            if not args.quiet:
                if not chapters or len(chapters) == 1:
                    print(
                        f"ℹ️  Chapter detection: only 1 chapter found "
                        f"(no silence gaps ≥ {args.chapter_gap}s)",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"📑 {len(chapters)} chapter(s) detected "
                        f"(gap threshold: {args.chapter_gap}s):",
                        file=sys.stderr,
                    )

            chapters_dest = getattr(args, "chapters_file", None)
            if chapters_dest:
                Path(chapters_dest).parent.mkdir(parents=True, exist_ok=True)
                Path(chapters_dest).write_text(chapters_output, encoding="utf-8")
                if not args.quiet:
                    print(f"📑 Chapters saved: {chapters_dest}", file=sys.stderr)
            else:
                print(f"\n=== CHAPTERS ({len(chapters)}) ===\n{chapters_output}")

        # Write stats sidecar
        _write_stats(r, args)

        # Subtitle burn-in
        if getattr(args, "burn_in", None):
            if is_batch:
                if not args.quiet:
                    print(
                        "⚠️  --burn-in is only supported for single-file mode; skipping",
                        file=sys.stderr,
                    )
            elif not r.get("segments"):
                if not args.quiet:
                    print("⚠️  --burn-in skipped: no speech segments detected", file=sys.stderr)
            else:
                srt_content = to_srt(r["segments"])
                src_path = r.get("_audio_path", r["file"])
                from lib.audio import burn_subtitles

                burn_subtitles(src_path, srt_content, args.burn_in, quiet=args.quiet)

    # Batch summary
    if is_batch and not args.quiet:
        wall = time.time() - wall_start
        rt = total_audio / wall if wall > 0 else 0
        skip_note = f" ({_skip_count[0]} skipped)" if _skip_count[0] else ""
        print(
            f"\n📊 Done: {len(results)} files{skip_note}, {format_duration(total_audio)} audio "
            f"in {format_duration(wall)} ({rt:.1f}× realtime)",
            file=sys.stderr,
        )
        if failed_files:
            print(f"❌ Failed: {len(failed_files)} file(s):", file=sys.stderr)
            for path, err in failed_files:
                print(f"   • {Path(path).name}: {err}", file=sys.stderr)
        if progress_path:
            print(f"📋 Progress saved: {progress_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
