#!/usr/bin/env python3
"""
faster-whisper transcription CLI
High-performance speech-to-text using CTranslate2 backend with batched inference.

Features:
- Multiple output formats: text, JSON, SRT, VTT, ASS, LRC, TTML, CSV, TSV, HTML
- URL/YouTube input via yt-dlp
- Speaker diarization (optional, requires pyannote.audio)
- Batch processing with glob patterns and directories
- Initial prompt for domain-specific terminology
- Confidence-based segment filtering
- Performance statistics
"""

from __future__ import annotations

import argparse
import copy
import fnmatch
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    from faster_whisper import BatchedInferencePipeline, WhisperModel
except ImportError:
    print("Error: faster-whisper not installed", file=sys.stderr)
    print("Run setup: ./setup.sh", file=sys.stderr)
    sys.exit(2)  # EXIT_MISSING_DEP

# Add shared lib to path
_BACKEND_DIR = Path(__file__).resolve().parent
_LIB_DIR = _BACKEND_DIR.parent / "lib"
if str(_LIB_DIR.parent) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR.parent))

from lib.alignment import run_alignment
from lib.audio import (
    burn_subtitles,
    download_url,
    extract_channel,
    is_url,
    preprocess_audio,
)
from lib.exitcodes import (
    EXIT_BAD_INPUT,
    EXIT_GENERAL,
    EXIT_GPU_ERROR,
    EXIT_MISSING_DEP,
)
from lib.formatters import (
    EXT_MAP,
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
# Helpers
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


# Output formatters, postprocessing, audio helpers, speakers, RSS — imported from lib/


# ---------------------------------------------------------------------------
# Speaker diarization
# ---------------------------------------------------------------------------


def run_diarization(
    audio_path, segments, quiet=False, min_speakers=None, max_speakers=None, hf_token=None
):
    """Assign speaker labels to segments using pyannote.audio."""
    try:
        from pyannote.audio import Pipeline as PyannotePipeline
    except ImportError:
        # Auto-install pyannote.audio on first use
        from lib.audio import auto_install_package

        if not auto_install_package("pyannote.audio", quiet=quiet):
            print(
                "  Manual install: ./setup.sh --diarize\n"
                "  Or:             pip install pyannote.audio",
                file=sys.stderr,
            )
            sys.exit(EXIT_MISSING_DEP)
        from pyannote.audio import Pipeline as PyannotePipeline

    if not quiet:
        print("🔊 Running speaker diarization...", file=sys.stderr)

    try:
        pretrained_kwargs = {}
        if hf_token:
            pretrained_kwargs["use_auth_token"] = hf_token
        pipeline = PyannotePipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            **pretrained_kwargs,
        )
    except Exception as e:
        print(f"Error loading diarization model: {e}", file=sys.stderr)
        print(
            "  Ensure you have a HuggingFace token at ~/.cache/huggingface/token\n"
            "  and accepted: https://hf.co/pyannote/speaker-diarization-3.1",
            file=sys.stderr,
        )
        sys.exit(EXIT_MISSING_DEP)

    # Move to GPU if available
    try:
        import torch

        if torch.cuda.is_available():
            pipeline.to(torch.device("cuda"))
    except Exception:
        pass

    # pyannote works best with WAV; convert compressed formats to avoid
    # sample-count mismatches (known issue with MP3/OGG)
    diarize_path = audio_path
    tmp_wav = None
    if not audio_path.lower().endswith(".wav"):
        tmp_wav = audio_path + ".diarize.wav"
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", audio_path, "-ar", "16000", "-ac", "1", tmp_wav],
                check=True,
                capture_output=True,
            )
            diarize_path = tmp_wav
        except Exception:
            # Fall back to original file if conversion fails
            tmp_wav = None

    try:
        diarize_kwargs = {}
        if min_speakers is not None:
            diarize_kwargs["min_speakers"] = min_speakers
        if max_speakers is not None:
            diarize_kwargs["max_speakers"] = max_speakers
        diarize_result = pipeline(diarize_path, **diarize_kwargs)
    finally:
        if tmp_wav and os.path.exists(tmp_wav):
            os.remove(tmp_wav)

    # pyannote 4.x returns DiarizeOutput with .speaker_diarization attribute;
    # pyannote 3.x returns an Annotation directly
    if hasattr(diarize_result, "speaker_diarization"):
        annotation = diarize_result.speaker_diarization
    else:
        annotation = diarize_result

    # Build speaker timeline
    timeline = [
        {"start": turn.start, "end": turn.end, "speaker": speaker}
        for turn, _, speaker in annotation.itertracks(yield_label=True)
    ]

    def speaker_at(t):
        """Find the speaker at a given timestamp by max overlap with a point."""
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
        # Word-level diarization: assign speaker to each word, then regroup
        # into speaker-homogeneous segments
        for w in all_words:
            mid = (w["start"] + w["end"]) / 2
            w["speaker"] = speaker_at(mid)

        # Group consecutive words by speaker into new segments
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
                    "text": "".join(w["word"] for w in current_words),
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
        # No word-level data: fall back to segment-level assignment
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


def parse_language_map(lang_map_str):
    """Parse --language-map value into a {pattern: lang_code} dict.

    Two forms accepted:
      Inline: "interview*.mp3=en,lecture.mp3=fr,keynote.wav=de"
      JSON file: "@/path/to/map.json"  (must be a dict of {pattern: lang})

    Patterns can be exact filenames, stems, or fnmatch glob patterns.
    """
    if not lang_map_str:
        return {}

    if lang_map_str.startswith("@"):
        json_path = lang_map_str[1:]
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)

    mapping = {}
    for part in lang_map_str.split(","):
        part = part.strip()
        if "=" not in part:
            continue
        pattern, lang = part.rsplit("=", 1)
        mapping[pattern.strip()] = lang.strip()
    return mapping


def resolve_file_language(audio_path, lang_map, fallback=None):
    """Return the language code for *audio_path* using *lang_map*.

    Priority:
      1. Exact filename match (e.g. "interview.mp3")
      2. Exact stem match (e.g. "interview")
      3. fnmatch glob match on filename (e.g. "interview*.mp3")
      4. fnmatch glob match on stem (e.g. "interview*")
      5. Fallback (global --language setting or None = auto-detect)
    """
    if not lang_map:
        return fallback

    name = Path(audio_path).name
    stem = Path(audio_path).stem

    for pattern, lang in lang_map.items():
        if pattern in (name, stem):
            return lang

    for pattern, lang in lang_map.items():
        if fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(stem, pattern):
            return lang

    return fallback


# resolve_inputs and AUDIO_EXTS imported from lib.audio (shared across backends)
from lib.audio import resolve_inputs  # noqa: E402

# ---------------------------------------------------------------------------
# Core transcription
# ---------------------------------------------------------------------------


def transcribe_file(audio_path, pipeline, args):
    """Transcribe a single audio file. Returns result dict."""
    t0 = time.time()

    # --- Preprocessing (normalize / denoise) ---
    preprocess_tmp = None
    channel_tmp = None
    effective_path = str(audio_path)

    # --- Channel extraction (stereo → mono channel) ---
    channel = getattr(args, "channel", "mix")
    if channel != "mix":
        effective_path, channel_tmp = extract_channel(effective_path, channel, quiet=args.quiet)

    if args.normalize or args.denoise:
        effective_path, preprocess_tmp = preprocess_audio(
            effective_path,
            normalize=args.normalize,
            denoise=args.denoise,
            quiet=args.quiet,
        )

    need_words = (
        args.word_timestamps
        or args.min_confidence is not None
        or args.diarize  # word-level needed for accurate speaker assignment
    ) and not args.stream  # streaming skips post-processing

    kw = dict(
        language=args.language,
        task="translate" if args.translate else "transcribe",
        beam_size=args.beam_size,
        word_timestamps=need_words,
        vad_filter=not args.no_vad,
        hotwords=args.hotwords,
        initial_prompt=args.initial_prompt,
        prefix=args.prefix,
        condition_on_previous_text=not args.no_condition_on_previous_text,
        multilingual=args.multilingual if args.multilingual else None,
    )

    # Optional parameters — only pass if explicitly set (avoids overriding defaults)
    if args.hallucination_silence_threshold is not None:
        kw["hallucination_silence_threshold"] = args.hallucination_silence_threshold
    if args.compression_ratio_threshold is not None:
        kw["compression_ratio_threshold"] = args.compression_ratio_threshold
    if args.log_prob_threshold is not None:
        kw["log_prob_threshold"] = args.log_prob_threshold
    if args.max_new_tokens is not None:
        kw["max_new_tokens"] = args.max_new_tokens
    if args.clip_timestamps is not None:
        # BatchedInferencePipeline expects List[dict] with "start"/"end" keys (seconds as floats).
        # Parse "0,3" → [{"start": 0.0, "end": 3.0}]
        # Parse "0,30;60,90" → [{"start": 0.0, "end": 30.0}, {"start": 60.0, "end": 90.0}]
        parsed_clips = []
        for clip_str in args.clip_timestamps.split(";"):
            parts = clip_str.strip().split(",")
            if len(parts) == 2:
                parsed_clips.append({"start": float(parts[0]), "end": float(parts[1])})
            else:
                raise ValueError(
                    f"Invalid clip range '{clip_str}'. Expected 'start,end' (seconds)."
                )
        kw["clip_timestamps"] = parsed_clips
    if args.progress:
        kw["log_progress"] = True

    if not args.no_batch:
        kw["batch_size"] = args.batch_size

    # VAD tuning parameters
    vad_dict = {}
    vad_threshold = args.vad_threshold if args.vad_threshold is not None else args.vad_onset
    vad_neg_threshold = (
        args.vad_neg_threshold if args.vad_neg_threshold is not None else args.vad_offset
    )
    if vad_threshold is not None:
        vad_dict["threshold"] = vad_threshold
    if vad_neg_threshold is not None:
        vad_dict["neg_threshold"] = vad_neg_threshold
    if args.min_speech_duration is not None:
        vad_dict["min_speech_duration_ms"] = args.min_speech_duration
    if args.max_speech_duration is not None:
        vad_dict["max_speech_duration_s"] = args.max_speech_duration
    if args.min_silence_duration is not None:
        vad_dict["min_silence_duration_ms"] = args.min_silence_duration
    if args.speech_pad is not None:
        vad_dict["speech_pad_ms"] = args.speech_pad
    if vad_dict:
        kw["vad_parameters"] = vad_dict

    # Temperature control
    if args.temperature is not None:
        temps = [float(t.strip()) for t in args.temperature.split(",")]
        kw["temperature"] = temps[0] if len(temps) == 1 else temps

    # No-speech threshold
    if args.no_speech_threshold is not None:
        kw["no_speech_threshold"] = args.no_speech_threshold

    # Beam search / sampling tuning
    if args.best_of is not None:
        kw["best_of"] = args.best_of
    if args.patience is not None:
        kw["patience"] = args.patience
    if args.repetition_penalty is not None:
        kw["repetition_penalty"] = args.repetition_penalty
    if args.no_repeat_ngram_size is not None:
        kw["no_repeat_ngram_size"] = args.no_repeat_ngram_size

    # --- Advanced inference params (Part 1 new flags) ---
    if args.no_timestamps:
        _ts_formats = {"srt", "vtt", "tsv", "lrc", "ass", "ttml"}
        conflicts = (
            args.word_timestamps
            or any(f in _ts_formats for f in getattr(args, "_formats", [args.format]))
            or args.diarize
        )
        if conflicts:
            print(
                "⚠️  --no-timestamps ignored: incompatible with "
                "--word-timestamps / --format srt/vtt/tsv/lrc/ass/ttml / --diarize",
                file=sys.stderr,
            )
        else:
            kw["without_timestamps"] = True

    if args.chunk_length is not None:
        kw["chunk_length"] = args.chunk_length

    if args.language_detection_threshold is not None:
        kw["language_detection_threshold"] = args.language_detection_threshold

    if args.language_detection_segments is not None:
        kw["language_detection_segments"] = args.language_detection_segments

    if args.length_penalty is not None:
        kw["length_penalty"] = args.length_penalty

    if args.prompt_reset_on_temperature is not None:
        kw["prompt_reset_on_temperature"] = args.prompt_reset_on_temperature

    if args.no_suppress_blank:
        kw["suppress_blank"] = False

    if args.suppress_tokens is not None:
        try:
            ids = [int(x.strip()) for x in args.suppress_tokens.split(",") if x.strip()]
            kw["suppress_tokens"] = [-1] + ids
        except ValueError:
            print(
                f"⚠️  Invalid --suppress-tokens value: {args.suppress_tokens!r} — skipped",
                file=sys.stderr,
            )

    if args.max_initial_timestamp is not None:
        kw["max_initial_timestamp"] = args.max_initial_timestamp

    if args.prepend_punctuations is not None:
        kw["prepend_punctuations"] = args.prepend_punctuations

    if args.append_punctuations is not None:
        kw["append_punctuations"] = args.append_punctuations

    segments_iter, info = pipeline.transcribe(effective_path, **kw)

    segments = []
    full_text_parts = []

    for seg in segments_iter:
        # Confidence filter (needs word-level probabilities)
        if args.min_confidence is not None and seg.words:
            avg = sum(w.probability for w in seg.words) / len(seg.words)
            if avg < args.min_confidence:
                continue

        full_text_parts.append(seg.text.strip())
        seg_data = {"start": seg.start, "end": seg.end, "text": seg.text}

        # Capture avg_logprob for confidence scoring (always available)
        if hasattr(seg, "avg_logprob"):
            seg_data["avg_logprob"] = seg.avg_logprob

        if need_words and seg.words:
            seg_data["words"] = [
                {
                    "word": w.word,
                    "start": w.start,
                    "end": w.end,
                    "probability": w.probability,
                }
                for w in seg.words
            ]

        segments.append(seg_data)

        # Streaming: print segment immediately
        if args.stream:
            line = f"[{format_ts_vtt(seg.start)} → {format_ts_vtt(seg.end)}] {seg.text.strip()}"
            print(line, flush=True)

    # Refine word timestamps with wav2vec2 (before diarization so it benefits)
    # Auto-runs whenever word timestamps are computed (--precise, --diarize,
    # --word-timestamps, --min-confidence all trigger word-level output)
    if need_words and not args.stream:
        segments = run_alignment(effective_path, segments, quiet=args.quiet)

    # Diarize after transcription (and alignment if --precise)
    speakers = None
    if args.diarize and not args.stream:
        segments, speakers = run_diarization(
            effective_path,
            segments,
            quiet=args.quiet,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
            hf_token=args.hf_token,
        )
        # Apply speaker name mapping if provided
        if getattr(args, "speaker_names", None):
            segments = apply_speaker_names(segments, args.speaker_names)

    # Filter hallucinations if requested
    if getattr(args, "filter_hallucinations", False):
        segments = filter_hallucinations(segments)

    # Cleanup preprocessing and channel extraction temp files
    if preprocess_tmp and os.path.exists(preprocess_tmp):
        os.remove(preprocess_tmp)
    if channel_tmp and os.path.exists(channel_tmp):
        os.remove(channel_tmp)

    elapsed = time.time() - t0
    dur = info.duration
    rt = round(dur / elapsed, 1) if elapsed > 0 else 0

    result = {
        "file": Path(audio_path).name,
        "text": " ".join(full_text_parts),
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": dur,
        "segments": segments,
        "stats": {
            "processing_time": round(elapsed, 2),
            "realtime_factor": rt,
        },
    }
    if args.translate:
        result["task"] = "translate"
    if speakers:
        result["speakers"] = speakers

    if not args.quiet:
        task_label = "translated" if args.translate else "transcribed"
        print(
            f"✅ {result['file']}: {format_duration(dur)} {task_label} in "
            f"{format_duration(elapsed)} ({rt}× realtime)",
            file=sys.stderr,
        )

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    # Pre-import onnxruntime silently to suppress the harmless WSL2 device-discovery warning.
    # onnxruntime writes directly to stderr fd when first imported (device_discovery.cc:211).
    # By importing it here with fd 2 redirected, we populate sys.modules so that later
    # lazy imports (faster_whisper's SileroVADModel) hit the cache instead of re-triggering.
    try:
        _old_stderr_fd = os.dup(2)
        try:
            with open(os.devnull, "wb") as _devnull:
                os.dup2(_devnull.fileno(), 2)
                import onnxruntime as _ort  # noqa: F401
        finally:
            os.dup2(_old_stderr_fd, 2)
            os.close(_old_stderr_fd)
    except Exception:
        pass  # If anything goes wrong, just continue — stderr stays intact

    # Early exit handlers — must run BEFORE argparse so they work without AUDIO positional arg
    _SCRIPT_DIR = Path(__file__).parent

    if "--version" in sys.argv:
        try:
            import importlib.metadata

            _fw_version = importlib.metadata.version("faster-whisper")
        except Exception:
            _fw_version = getattr(sys.modules.get("faster_whisper"), "__version__", "unknown")
        print(f"faster-whisper {_fw_version}")
        sys.exit(0)

    if "--update" in sys.argv:
        _venv_python = _SCRIPT_DIR.parent / ".venv" / "bin" / "python"
        if shutil.which("uv"):
            subprocess.run(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    str(_venv_python),
                    "--upgrade",
                    "faster-whisper",
                ],
                check=True,
            )
        else:
            subprocess.run(
                [str(_venv_python), "-m", "pip", "install", "--upgrade", "faster-whisper"],
                check=True,
            )
        try:
            import importlib.metadata

            _fw_version = importlib.metadata.version("faster-whisper")
        except Exception:
            _fw_version = "unknown"
        print(f"✅ faster-whisper updated to {_fw_version}")
        sys.exit(0)

    p = argparse.ArgumentParser(
        description="Transcribe audio with faster-whisper",
        epilog=(
            "examples:\n"
            "  %(prog)s audio.mp3\n"
            "  %(prog)s audio.mp3 --format srt -o subtitles.srt\n"
            "  %(prog)s https://youtube.com/watch?v=... --language en\n"
            "  %(prog)s *.mp3 --skip-existing -o ./transcripts/\n"
            "  %(prog)s meeting.wav --diarize --format vtt\n"
            "  %(prog)s lecture.mp3 --initial-prompt 'Kubernetes, gRPC'\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # --- Positional ---
    p.add_argument(
        "audio",
        nargs="*",
        metavar="AUDIO",
        help="Audio file(s), directory, glob pattern, or URL. Optional when --rss is used.",
    )

    # --- Model & language ---
    p.add_argument(
        "-m",
        "--model",
        default="distil-large-v3.5",
        help="Whisper model (default: distil-large-v3.5). "
        "Common models: distil-large-v3.5 (fastest, best accuracy), "
        "large-v3-turbo / turbo, large-v3, medium, small, tiny, base. "
        "Also accepts full HuggingFace model paths.",
    )
    p.add_argument(
        "--revision",
        default=None,
        metavar="REV",
        help="Model revision (git branch/tag/commit hash) to pin a specific version",
    )
    p.add_argument(
        "-l",
        "--language",
        default=None,
        help="Language code, e.g. en, es, fr (auto-detects if omitted)",
    )
    p.add_argument(
        "--language-map",
        default=None,
        metavar="MAP",
        help="Per-file language override for batch mode. Inline: 'interview*.mp3=en,lecture.wav=fr' "
        "or JSON file: '@/path/to/map.json'. Overrides --language for matched files; "
        "unmatched files fall back to --language (or auto-detect). "
        "Patterns support fnmatch globs on filename or stem.",
    )
    p.add_argument(
        "--initial-prompt",
        default=None,
        metavar="TEXT",
        help="Prompt to condition the model (terminology, formatting hints)",
    )
    p.add_argument(
        "--prefix",
        default=None,
        metavar="TEXT",
        help="Prefix to condition the first segment (e.g. known starting words)",
    )
    p.add_argument(
        "--hotwords",
        default=None,
        metavar="WORDS",
        help="Hotwords to boost recognition (space-separated)",
    )
    p.add_argument(
        "--translate",
        action="store_true",
        help="Translate to English instead of transcribing",
    )
    p.add_argument(
        "--multilingual",
        action="store_true",
        help="Enable multilingual/code-switching mode (helps smaller models)",
    )
    p.add_argument(
        "--hf-token",
        default=None,
        metavar="TOKEN",
        help="HuggingFace token for private models and diarization (overrides cached token)",
    )
    p.add_argument(
        "--model-dir",
        default=None,
        metavar="PATH",
        help="Custom directory for model cache (default: ~/.cache/huggingface/hub)",
    )

    # --- Output format ---
    p.add_argument(
        "-f",
        "--format",
        default="text",
        help="Output format (default: text). "
        "Accepts one or a comma-separated list of: "
        "text, json, srt, vtt, tsv, csv, lrc, html, ass, ttml. "
        "Example: --format srt,text",
    )
    p.add_argument(
        "--word-timestamps",
        action="store_true",
        help="Include word-level timestamps (auto-enabled for --diarize)",
    )
    p.add_argument(
        "--stream",
        action="store_true",
        help="Output segments as they are transcribed (streaming mode; disables diarize/alignment)",
    )
    p.add_argument(
        "--max-words-per-line",
        type=int,
        default=None,
        metavar="N",
        help="For SRT/VTT, split long segments into sub-cues with at most N words each "
        "(requires word-level timestamps; falls back to full segment if no word data)",
    )
    p.add_argument(
        "--max-chars-per-line",
        type=int,
        default=None,
        metavar="N",
        help="For SRT/VTT/ASS/TTML, split subtitle lines so each fits within N characters "
        "(requires word-level timestamps; takes priority over --max-words-per-line)",
    )
    p.add_argument(
        "--channel",
        default="mix",
        choices=["left", "right", "mix"],
        help="Stereo channel to transcribe: left, right, or mix (default: mix). "
        "Requires ffmpeg.",
    )
    p.add_argument(
        "--clean-filler",
        action="store_true",
        help="Remove hesitation fillers (um, uh, er, ah, hmm) and discourse markers "
        "(you know, I mean, you see) from transcript text",
    )
    p.add_argument(
        "--detect-paragraphs",
        action="store_true",
        help="Insert paragraph breaks in text output based on silence gaps between segments",
    )
    p.add_argument(
        "--paragraph-gap",
        type=float,
        default=3.0,
        metavar="SEC",
        help="Minimum silence gap in seconds to start a new paragraph (default: 3.0). "
        "Used with --detect-paragraphs",
    )
    p.add_argument(
        "--merge-sentences",
        action="store_true",
        help="Merge consecutive segments into sentence-level chunks "
        "(useful for improving SRT/VTT readability)",
    )
    p.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="PATH",
        help="Output file or directory (directory for batch mode)",
    )
    p.add_argument(
        "--output-template",
        default=None,
        metavar="TEMPLATE",
        help="Output filename template for batch mode. Supports: "
        "{stem} (input filename without ext), {lang} (detected language), "
        "{ext} (format extension), {model} (model name). "
        "Example: '{stem}_{lang}.{ext}' → 'interview_en.srt'",
    )

    # --- Inference tuning ---
    p.add_argument(
        "--beam-size",
        type=int,
        default=5,
        metavar="N",
        help="Beam search size (default: 5)",
    )
    p.add_argument(
        "--temperature",
        default=None,
        metavar="T",
        help="Sampling temperature or comma-separated fallback list (e.g. '0.0' or '0.0,0.2,0.4'); "
        "default uses faster-whisper's built-in schedule [0.0,0.2,0.4,0.6,0.8,1.0]",
    )
    p.add_argument(
        "--no-speech-threshold",
        type=float,
        default=None,
        metavar="PROB",
        help="Probability threshold below which segments are treated as silence/no-speech "
        "(default: 0.6)",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=8,
        metavar="N",
        help="Batch size for batched inference (default: 8; reduce if OOM)",
    )
    p.add_argument("--no-vad", action="store_true", help="Disable voice activity detection")
    p.add_argument(
        "--vad-threshold",
        type=float,
        default=None,
        metavar="T",
        help="VAD speech probability threshold (default: 0.5); higher = more conservative",
    )
    p.add_argument(
        "--vad-neg-threshold",
        type=float,
        default=None,
        metavar="T",
        help="VAD negative threshold for ending speech segments (default: auto)",
    )
    p.add_argument(
        "--vad-onset",
        type=float,
        default=None,
        metavar="T",
        help="Alias for --vad-threshold (legacy compatibility)",
    )
    p.add_argument(
        "--vad-offset",
        type=float,
        default=None,
        metavar="T",
        help="Alias for --vad-neg-threshold (legacy compatibility)",
    )
    p.add_argument(
        "--min-speech-duration",
        type=int,
        default=None,
        metavar="MS",
        help="Minimum speech segment duration in milliseconds (default: 0)",
    )
    p.add_argument(
        "--max-speech-duration",
        type=float,
        default=None,
        metavar="SEC",
        help="Maximum speech segment duration in seconds (default: unlimited)",
    )
    p.add_argument(
        "--min-silence-duration",
        type=int,
        default=None,
        metavar="MS",
        help="Minimum silence duration before splitting a segment in ms (default: 2000)",
    )
    p.add_argument(
        "--speech-pad",
        type=int,
        default=None,
        metavar="MS",
        help="Padding added around speech segments in milliseconds (default: 400)",
    )
    p.add_argument(
        "--no-batch",
        action="store_true",
        help="Disable batched inference (use standard WhisperModel)",
    )
    p.add_argument(
        "--hallucination-silence-threshold",
        type=float,
        default=None,
        metavar="SEC",
        help="Skip silent sections where model hallucinates (e.g. 1.0 sec)",
    )
    p.add_argument(
        "--no-condition-on-previous-text",
        action="store_true",
        help="Don't condition on previous text (reduces repetition/hallucination loops; auto-enabled for distil models)",
    )
    p.add_argument(
        "--condition-on-previous-text",
        action="store_true",
        help="Force-enable conditioning on previous text (overrides auto-disable for distil models)",
    )
    p.add_argument(
        "--compression-ratio-threshold",
        type=float,
        default=None,
        metavar="RATIO",
        help="Filter segments above this compression ratio (default: 2.4)",
    )
    p.add_argument(
        "--log-prob-threshold",
        type=float,
        default=None,
        metavar="PROB",
        help="Filter segments below this avg log probability (default: -1.0)",
    )
    p.add_argument(
        "--max-new-tokens",
        type=int,
        default=None,
        metavar="N",
        help="Maximum tokens per segment (prevents runaway generation)",
    )
    p.add_argument(
        "--clip-timestamps",
        default=None,
        metavar="RANGE",
        help="Transcribe specific time ranges: '30,60' or '0,30;60,90' (seconds)",
    )
    p.add_argument(
        "--progress",
        action="store_true",
        help="Show transcription progress bar",
    )
    p.add_argument(
        "--best-of",
        type=int,
        default=None,
        metavar="N",
        help="Number of candidates when sampling with non-zero temperature (default: 5)",
    )
    p.add_argument(
        "--patience",
        type=float,
        default=None,
        metavar="F",
        help="Beam search patience factor; higher allows more beam candidates (default: 1.0)",
    )
    p.add_argument(
        "--repetition-penalty",
        type=float,
        default=None,
        metavar="F",
        help="Penalty applied to previously generated tokens to reduce repetition (default: 1.0)",
    )
    p.add_argument(
        "--no-repeat-ngram-size",
        type=int,
        default=None,
        metavar="N",
        help="Prevent repetition of n-grams of this size (default: 0 = disabled)",
    )

    # --- Advanced inference tuning ---
    p.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Output text segments without timing information (faster; "
        "incompatible with --word-timestamps, --format srt/vtt/tsv, --diarize)",
    )
    p.add_argument(
        "--chunk-length",
        type=int,
        default=None,
        metavar="N",
        help="Audio chunk length in seconds for batched inference (default: auto); "
        "ignored with --no-batch",
    )
    p.add_argument(
        "--language-detection-threshold",
        type=float,
        default=None,
        metavar="T",
        help="Confidence threshold for automatic language detection (default: 0.5)",
    )
    p.add_argument(
        "--language-detection-segments",
        type=int,
        default=None,
        metavar="N",
        help="Number of audio segments to sample for language detection "
        "(default: 1; increase for more accurate detection)",
    )
    p.add_argument(
        "--length-penalty",
        type=float,
        default=None,
        metavar="F",
        help="Length penalty for beam search; >1 favors longer outputs, <1 favors shorter "
        "(default: 1.0)",
    )
    p.add_argument(
        "--prompt-reset-on-temperature",
        type=float,
        default=None,
        metavar="T",
        help="Reset initial prompt when temperature fallback reaches this threshold (default: 0.5)",
    )
    p.add_argument(
        "--no-suppress-blank",
        action="store_true",
        help="Disable blank token suppression (may improve transcription of soft speech)",
    )
    p.add_argument(
        "--suppress-tokens",
        default=None,
        metavar="IDS",
        help="Comma-separated token IDs to suppress in addition to the default -1 "
        "(e.g. '1234,5678')",
    )
    p.add_argument(
        "--max-initial-timestamp",
        type=float,
        default=None,
        metavar="T",
        help="Maximum timestamp allowed for the first transcribed segment in seconds "
        "(default: 1.0)",
    )
    p.add_argument(
        "--prepend-punctuations",
        default=None,
        metavar="CHARS",
        help='Punctuation characters to merge into the preceding word (default: "\'¿([{-")',
    )
    p.add_argument(
        "--append-punctuations",
        default=None,
        metavar="CHARS",
        help="Punctuation characters to merge into the following word "
        '(default: "\'.。,，!！?？:：")]}\、")',
    )

    # --- Advanced features ---
    p.add_argument(
        "--diarize",
        action="store_true",
        help="Speaker diarization (requires pyannote.audio; install via setup.sh --diarize)",
    )
    p.add_argument(
        "--min-speakers",
        type=int,
        default=None,
        metavar="N",
        help="Minimum number of speakers hint for diarization",
    )
    p.add_argument(
        "--max-speakers",
        type=int,
        default=None,
        metavar="N",
        help="Maximum number of speakers hint for diarization",
    )
    p.add_argument(
        "--min-confidence",
        type=float,
        default=None,
        metavar="PROB",
        help="Drop segments below this avg word confidence (0.0–1.0)",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip files whose output already exists (batch mode)",
    )
    p.add_argument(
        "--detect-language-only",
        action="store_true",
        help="Detect the language of the audio and exit (no transcription). "
        "Output: 'Language: en (probability: 0.984)'. With --format json: JSON object.",
    )
    p.add_argument(
        "--stats-file",
        default=None,
        metavar="PATH",
        help="Write performance stats JSON sidecar after transcription. "
        "If a directory: writes {stem}.stats.json in that dir. "
        "In batch mode, one stats file per input.",
    )
    p.add_argument(
        "--burn-in",
        default=None,
        metavar="OUTPUT",
        help="Burn subtitles into the original video: transcribe, then ffmpeg-overlay SRT "
        "into the input file and save to OUTPUT (single-file mode only; requires ffmpeg)",
    )
    p.add_argument(
        "--speaker-names",
        default=None,
        metavar="NAMES",
        help="Comma-separated speaker names to replace SPEAKER_1, SPEAKER_2, etc. "
        "(e.g. 'Alice,Bob'). Requires --diarize",
    )
    p.add_argument(
        "--filter-hallucinations",
        action="store_true",
        help="Filter common Whisper hallucinations: music/applause markers, "
        "'Thank you for watching', duplicate consecutive segments, etc.",
    )
    p.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep temp files from URL downloads instead of deleting them "
        "(useful for re-processing downloaded audio without re-downloading)",
    )
    p.add_argument(
        "--parallel",
        type=int,
        default=None,
        metavar="N",
        help="Number of parallel workers for batch processing "
        "(default: sequential; mainly useful on CPU with many small files)",
    )

    # --- Preprocessing ---
    p.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize audio volume before transcription (EBU R128 loudnorm)",
    )
    p.add_argument(
        "--denoise",
        action="store_true",
        help="Apply noise reduction before transcription (high-pass + FFT denoise)",
    )

    # --- Device ---
    p.add_argument(
        "--device",
        default="auto",
        choices=["auto", "cpu", "cuda"],
        help="Compute device (default: auto)",
    )
    p.add_argument(
        "--compute-type",
        default="auto",
        choices=["auto", "int8", "int8_float16", "float16", "float32"],
        help="Quantization (default: auto; int8_float16 = hybrid for GPU)",
    )
    p.add_argument(
        "--threads",
        type=int,
        default=None,
        metavar="N",
        help="Number of CPU threads for CTranslate2 inference (default: auto)",
    )
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress messages",
    )
    p.add_argument(
        "--agent",
        action="store_true",
        help="Agent/chatbot output mode: emit a single compact JSON line to stdout "
        "with text, duration, language, speakers, and stats. Implies --quiet. "
        "File output (-o) still works alongside --agent.",
    )
    p.add_argument(
        "--log-level",
        default="warning",
        choices=["debug", "info", "warning", "error"],
        help="Set faster_whisper library logging level (default: warning)",
    )

    # --- Utility ---
    p.add_argument(
        "--version",
        action="store_true",
        help="Show installed faster-whisper version and exit",
    )
    p.add_argument(
        "--update",
        action="store_true",
        help="Upgrade faster-whisper in the skill venv and exit",
    )

    # --- RSS / Podcast ---
    p.add_argument(
        "--rss",
        default=None,
        metavar="URL",
        help="Podcast RSS feed URL — extracts audio enclosures and transcribes them. "
        "AUDIO positional is optional when --rss is used.",
    )
    p.add_argument(
        "--rss-latest",
        type=int,
        default=5,
        metavar="N",
        help="Number of most-recent episodes to process from --rss feed "
        "(default: 5; use 0 for all episodes)",
    )

    # --- Reliability ---
    p.add_argument(
        "--retries",
        type=int,
        default=0,
        metavar="N",
        help="Retry failed files up to N times with exponential backoff "
        "(default: 0 = no retry; incompatible with --parallel)",
    )
    p.add_argument(
        "--resume",
        default=None,
        metavar="PATH",
        help="Resume batch processing from a progress checkpoint file. "
        "Skips already-completed files. Creates the file if it doesn't exist.",
    )

    # --- Transcript search ---
    p.add_argument(
        "--search",
        default=None,
        metavar="TERM",
        help="Search the transcript for TERM and print matching segments with timestamps. "
        "Replaces the normal transcript output (use with -o to save search results to file).",
    )
    p.add_argument(
        "--search-fuzzy",
        action="store_true",
        help="Use fuzzy/approximate matching with --search (useful for typos or partial words)",
    )

    # --- Chapter detection ---
    p.add_argument(
        "--detect-chapters",
        action="store_true",
        help="Detect chapter/section breaks from silence gaps between segments and print chapter markers.",
    )
    p.add_argument(
        "--chapter-gap",
        type=float,
        default=8.0,
        metavar="SEC",
        help="Minimum silence gap in seconds to start a new chapter (default: 8.0)",
    )
    p.add_argument(
        "--chapters-file",
        default=None,
        metavar="PATH",
        help="Write chapter markers to this file (default: print to stdout alongside transcript). "
        "Format is controlled by --chapter-format.",
    )
    p.add_argument(
        "--chapter-format",
        default="youtube",
        choices=["youtube", "text", "json"],
        help="Chapter output format: youtube (M:SS Title), text (Title: HH:MM:SS), json (default: youtube)",
    )

    # --- Speaker audio export ---
    p.add_argument(
        "--export-speakers",
        default=None,
        metavar="DIR",
        help="After diarization, export each speaker's audio turns to separate WAV files in DIR. "
        "Requires --diarize and ffmpeg.",
    )

    # --- Backward compat (hidden) ---
    p.add_argument("-j", "--json", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--vad", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--precise", action="store_true", help=argparse.SUPPRESS)

    args = p.parse_args()
    if args.json:
        args.format = "json"
    if args.precise:
        args.word_timestamps = True

    # Parse --format as comma-separated list; validate each entry
    _VALID_FORMATS = {"text", "json", "srt", "vtt", "tsv", "csv", "lrc", "html", "ass", "ttml"}
    _raw_formats = [f.strip() for f in args.format.split(",") if f.strip()]
    _invalid = [f for f in _raw_formats if f not in _VALID_FORMATS]
    if _invalid:
        p.error(
            f"Invalid format(s): {', '.join(_invalid)}. "
            f"Choose from: {', '.join(sorted(_VALID_FORMATS))}"
        )
    args._formats = _raw_formats if _raw_formats else ["text"]
    args.format = args._formats[0]  # backward compat

    # Multi-format + file path (not dir) is an error
    if len(args._formats) > 1 and args.output and Path(args.output).suffix:
        p.error(
            f"Multiple formats ({', '.join(args._formats)}) require -o to be a directory, "
            f"not a file path. Use: -o /path/to/output/dir/"
        )

    # Agent mode: auto-enable quiet (suppress all stderr)
    if args.agent:
        args.quiet = True

    # Validate: need at least one audio source
    if not args.audio and not args.rss:
        p.error("AUDIO file(s) are required, or use --rss to specify a podcast feed")

    # Apply HuggingFace token to environment early (model loading picks it up)
    if args.hf_token:
        os.environ["HF_TOKEN"] = args.hf_token
        os.environ["HUGGING_FACE_HUB_TOKEN"] = args.hf_token

    # Parse --language-map early so we can validate before loading the model
    lang_map = {}
    if getattr(args, "language_map", None):
        try:
            lang_map = parse_language_map(args.language_map)
        except Exception as e:
            print(f"Error parsing --language-map: {e}", file=sys.stderr)
            sys.exit(EXIT_BAD_INPUT)

    # Apply faster_whisper library logging level
    logging.basicConfig()
    logging.getLogger("faster_whisper").setLevel(getattr(logging, args.log_level.upper()))

    # Handle "turbo" alias → large-v3-turbo
    if args.model.lower() == "turbo":
        args.model = "large-v3-turbo"

    # Auto-disable condition_on_previous_text for distil models (HuggingFace recommendation)
    # Prevents repetition loops inherent to distil model architecture.
    # Override with --condition-on-previous-text if you need the old behaviour.
    is_distil = args.model.lower().startswith("distil-")
    if (
        is_distil
        and not args.no_condition_on_previous_text
        and not args.condition_on_previous_text
    ):
        args.no_condition_on_previous_text = True
        if not args.quiet:
            print(
                "ℹ️  distil model detected: auto-disabling condition_on_previous_text "
                "(reduces repetition loops; pass --condition-on-previous-text to override)",
                file=sys.stderr,
            )

    # Warn when --speaker-names is used without --diarize (has no effect)
    if getattr(args, "speaker_names", None) and not args.diarize:
        print("⚠️  --speaker-names has no effect without --diarize; ignoring", file=sys.stderr)

    # Streaming mode disables post-processing that needs all segments
    if args.stream:
        if args.diarize:
            print("⚠️  --stream disables --diarize (needs all segments)", file=sys.stderr)
            args.diarize = False
        if args.word_timestamps:
            print(
                "⚠️  --stream disables word-level alignment (needs all segments)",
                file=sys.stderr,
            )

    # Conflict check: --chunk-length requires batched mode
    if args.chunk_length is not None and args.no_batch:
        print(
            "⚠️  --chunk-length ignored with --no-batch (only valid for batched inference)",
            file=sys.stderr,
        )
        args.chunk_length = None

    # ---- Resolve inputs (including stdin '-') ----
    temp_dirs = []
    stdin_tmp = None
    raw_inputs = list(args.audio)  # mutable copy

    # Handle --rss: fetch podcast episodes and prepend their URLs
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

    # Check for stdin '-' usage
    if "-" in raw_inputs:
        if len(raw_inputs) > 1:
            print(
                "Error: stdin '-' cannot be combined with other inputs in batch mode",
                file=sys.stderr,
            )
            sys.exit(EXIT_BAD_INPUT)
        if not args.quiet:
            print("📥 Reading audio from stdin...", file=sys.stderr)
        stdin_data = sys.stdin.buffer.read()
        stdin_tmp = tempfile.NamedTemporaryFile(
            delete=False, suffix=".audio", prefix="fw-stdin-"
        )
        stdin_tmp.write(stdin_data)
        stdin_tmp.flush()
        stdin_tmp.close()
        raw_inputs = [stdin_tmp.name]

    audio_files = []
    for inp in raw_inputs:
        if is_url(inp):
            path, td = download_url(inp, quiet=args.quiet)
            audio_files.append(path)
            temp_dirs.append(td)
        else:
            audio_files.extend(resolve_inputs([inp]))

    if not audio_files:
        print("Error: No audio files found", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    is_batch = len(audio_files) > 1

    # ---- Device setup ----
    device = args.device
    compute_type = args.compute_type
    cuda_ok, gpu_name = check_cuda_available()

    if device == "auto":
        device = "cuda" if cuda_ok else "cpu"
        if device == "cpu" and not args.quiet:
            print("⚠️  CUDA not available — using CPU (this will be slow!)", file=sys.stderr)
            print(
                "   To enable GPU: pip install torch --index-url https://download.pytorch.org/whl/cu121",
                file=sys.stderr,
            )

    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"

    if cuda_ok and compute_type == "float16" and args.compute_type == "auto" and not args.quiet:
        import re as _re

        gpu_name = gpu_name or ""
        if _re.search(r"RTX 30[0-9]{2}", gpu_name, _re.IGNORECASE):
            print(
                f"💡 Tip: For {gpu_name}, --compute-type int8_float16 saves ~1GB VRAM with minimal quality loss",
                file=sys.stderr,
            )

    use_batched = not args.no_batch

    if not args.quiet:
        mode = f"batched (bs={args.batch_size})" if use_batched else "standard"
        gpu_str = f" on {gpu_name}" if device == "cuda" and gpu_name else ""
        task_str = " [translate→en]" if args.translate else ""
        stream_str = " [streaming]" if args.stream else ""
        print(
            f"🎙️  {args.model} ({device}/{compute_type}){gpu_str} [{mode}]{task_str}{stream_str}",
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
                f"⚠️  Batch stem collision: {_dup_names} — later files will overwrite earlier ones. "
                f"Use --output-template '{{stem}}_{{lang}}.{{ext}}' to differentiate.",
                file=sys.stderr,
            )

    # ---- Load model ----
    try:
        model_kwargs = dict(device=device, compute_type=compute_type)
        if args.revision is not None:
            model_kwargs["revision"] = args.revision
        if args.threads is not None:
            model_kwargs["cpu_threads"] = args.threads
        if getattr(args, "model_dir", None):
            model_kwargs["download_root"] = args.model_dir
        model = WhisperModel(args.model, **model_kwargs)
        pipe = BatchedInferencePipeline(model) if use_batched else model
    except Exception as e:
        err_msg = str(e).lower()
        if "out of memory" in err_msg or "oom" in err_msg or "cuda" in err_msg:
            print(f"Error: GPU memory error loading model: {e}", file=sys.stderr)
            sys.exit(EXIT_GPU_ERROR)
        print(f"Error loading model: {e}", file=sys.stderr)
        sys.exit(EXIT_GENERAL)

    # ---- Detect language only (early exit) ----
    if args.detect_language_only:
        try:
            from faster_whisper.audio import decode_audio
        except ImportError:
            # Older versions may use different path
            try:
                from faster_whisper import decode_audio
            except ImportError:

                def decode_audio(path, sampling_rate=16000):
                    import subprocess as _sp

                    import numpy as np

                    cmd = [
                        "ffmpeg",
                        "-i",
                        path,
                        "-ar",
                        str(sampling_rate),
                        "-ac",
                        "1",
                        "-f",
                        "f32le",
                        "-",
                    ]
                    result = _sp.run(cmd, capture_output=True, check=True)
                    return np.frombuffer(result.stdout, dtype=np.float32)

        exit_code = 0
        for audio_path in audio_files:
            try:
                audio_np = decode_audio(audio_path)
                lang, lang_prob, _ = model.detect_language(audio=audio_np)
                prob_val = float(lang_prob)
                if args.format == "json":
                    print(
                        json.dumps(
                            {"language": lang, "language_probability": round(prob_val, 4)},
                            ensure_ascii=False,
                        )
                    )
                else:
                    print(f"Language: {lang} (probability: {prob_val:.3f})")
            except Exception as e:
                print(f"Error detecting language for {audio_path}: {e}", file=sys.stderr)
                exit_code = 1
        # Clean up any URL-downloaded temp directories before exiting
        for td in temp_dirs:
            shutil.rmtree(td, ignore_errors=True)
        if stdin_tmp and os.path.exists(stdin_tmp.name):
            os.unlink(stdin_tmp.name)
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
                # Skip only when ALL requested format outputs already exist
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

    if getattr(args, "parallel", None) and args.parallel > 1 and is_batch:
        if device == "cuda" and not args.quiet:
            print(
                "⚠️  --parallel on GPU: each call uses the full GPU; "
                "benefit is limited vs sequential batched mode",
                file=sys.stderr,
            )
        if args.retries and not args.quiet:
            print("⚠️  --retries is not supported with --parallel (ignored)", file=sys.stderr)
        pending = [af for af in audio_files if not _should_skip(af)]
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            # Build per-file args copies with language-map overrides
            def _make_args(af):
                file_lang = resolve_file_language(af, lang_map, args.language)
                if file_lang != args.language:
                    a = copy.copy(args)
                    a.language = file_lang
                    return a
                return args

            future_to_path = {
                executor.submit(transcribe_file, af, pipe, _make_args(af)): af for af in pending
            }
            for future in as_completed(future_to_path):
                af = future_to_path[future]
                name = Path(af).name
                try:
                    r = future.result()
                    r["_audio_path"] = af
                    results.append(r)
                    total_audio += r["duration"]
                except Exception as e:
                    print(f"❌ {name}: {e}", file=sys.stderr)
                    failed_files.append((af, str(e)))
    else:
        # ETA tracking for sequential batch mode
        pending_files = [af for af in audio_files if not _should_skip(af)]
        pending_total = len(pending_files)
        eta_wall_start = time.time()
        files_done = 0

        for audio_path in audio_files:
            name = Path(audio_path).name

            if _should_skip(audio_path):
                continue

            # Per-file language override via --language-map
            file_lang = resolve_file_language(audio_path, lang_map, args.language)
            if lang_map and file_lang != args.language and not args.quiet and is_batch:
                print(f"   🌐 Language override: {file_lang}", file=sys.stderr)

            # Build per-file args (only copy if language differs to avoid overhead)
            file_args = args
            if file_lang != args.language:
                file_args = copy.copy(args)
                file_args.language = file_lang

            if not args.quiet and is_batch:
                # ETA prefix before file name (files_done = completed so far)
                current_idx = files_done + 1  # 1-based index of current file
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

            success = False
            last_error = None
            max_attempts = args.retries + 1
            for attempt in range(max_attempts):
                try:
                    r = transcribe_file(audio_path, pipe, file_args)
                    # Store the original audio_path on result for stats/template use
                    r["_audio_path"] = audio_path
                    results.append(r)
                    total_audio += r["duration"]
                    files_done += 1
                    success = True
                    # Save progress checkpoint
                    if progress is not None and progress_path:
                        progress["completed"].append(os.path.abspath(audio_path))
                        save_progress(progress_path, progress)
                    break
                except Exception as e:
                    last_error = e
                    if attempt < args.retries:
                        wait = 2 ** (attempt + 1)
                        print(
                            f"⚠️  {name}: attempt {attempt + 1}/{max_attempts} failed: {e}. "
                            f"Retrying in {wait}s...",
                            file=sys.stderr,
                        )
                        time.sleep(wait)

            if not success:
                print(
                    f"❌ {name}: failed after {max_attempts} attempt(s): {last_error}",
                    file=sys.stderr,
                )
                failed_files.append((audio_path, str(last_error)))
                files_done += 1  # count failed files too for accurate ETA
                # Save failed files to progress
                if progress is not None and progress_path:
                    progress["failed"].append(
                        {
                            "path": os.path.abspath(audio_path),
                            "error": str(last_error),
                        }
                    )
                    save_progress(progress_path, progress)
                if not is_batch:
                    err_msg = str(last_error).lower()
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

    # Cleanup temp dirs and stdin temp file
    for td in temp_dirs:
        if getattr(args, "keep_temp", False):
            if not args.quiet:
                print(f"📁 Temp files kept: {td}", file=sys.stderr)
        else:
            shutil.rmtree(td, ignore_errors=True)
    if stdin_tmp and os.path.exists(stdin_tmp.name):
        os.unlink(stdin_tmp.name)

    if not results:
        if args.skip_existing:
            if not args.quiet:
                print("All files already transcribed (--skip-existing)", file=sys.stderr)
            sys.exit(0)
        if getattr(args, "resume", None):
            if not args.quiet:
                print("All files already transcribed (--resume)", file=sys.stderr)
            sys.exit(0)
        print("Error: No files transcribed", file=sys.stderr)
        sys.exit(EXIT_BAD_INPUT)

    # ---- Write output ----
    for r in results:
        # Apply --merge-sentences post-processing before formatting
        if args.merge_sentences and r.get("segments"):
            r["segments"] = merge_sentences(r["segments"])
            # Rebuild full text from merged segments
            r["text"] = " ".join(s["text"].strip() for s in r["segments"]).strip()

        # ---- Speaker audio export (requires diarization) ----
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

        # ---- Streaming mode already printed segments to stdout ----
        if args.stream and not args.output:
            _write_stats(r, args)
            continue

        # ---- Apply paragraph detection ----
        if getattr(args, "detect_paragraphs", False) and r.get("segments"):
            r["segments"] = detect_paragraphs(
                r["segments"],
                min_gap=getattr(args, "paragraph_gap", 3.0),
            )

        # ---- Apply filler word removal ----
        if getattr(args, "clean_filler", False) and r.get("segments"):
            r["segments"] = remove_filler_words(r["segments"])
            r["text"] = " ".join(s["text"].strip() for s in r["segments"]).strip()

        # Determine output filename stem for template/stats
        audio_path = r.get("_audio_path", r["file"])
        stem = Path(audio_path).stem
        lang = r.get("language", "xx")
        model_name = args.model

        # ---- Pre-compute chapters (must happen before output formatting for JSON embedding) ----
        # Stored in _computed_chapters so the display block below can reuse it without a second call.
        _computed_chapters = None
        if getattr(args, "detect_chapters", False) and r.get("segments"):
            _computed_chapters = detect_chapters(r["segments"], min_gap=args.chapter_gap)
            _formats_list = getattr(args, "_formats", [args.format])
            if "json" in _formats_list:
                r["chapters"] = _computed_chapters  # embed in JSON output

        # ---- Agent mode: compact JSON output ----
        if getattr(args, "agent", False):
            # Inject file_path and output_path for agent tracking
            r["file_path"] = os.path.abspath(audio_path)
            # Still write to files if -o is set
            if args.output:
                formats = getattr(args, "_formats", [args.format])
                for fmt in formats:
                    ext = EXT_MAP.get(fmt, ".txt").lstrip(".")
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
                        if args.output_template:
                            filename = args.output_template.format(
                                stem=stem,
                                lang=lang,
                                ext=ext,
                                model=model_name,
                            )
                            dest = out_path / filename
                        else:
                            dest = out_path / (stem + EXT_MAP.get(fmt, ".txt"))
                    else:
                        dest = out_path
                    dest.write_text(output, encoding="utf-8")
                    r["output_path"] = str(dest.resolve())
            # Emit compact JSON to stdout
            print(format_agent_json(r, "faster-whisper"))
            _write_stats(r, args)
            continue

        # ---- Transcript search mode ----
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
            # ---- Multi-format output loop ----
            formats = getattr(args, "_formats", [args.format])
            if len(formats) > 1 and not args.output:
                print(
                    f"⚠️  Multiple formats requested but no -o DIR specified; "
                    f"showing only '{formats[0]}' on stdout. "
                    f"Use -o <dir> to write all formats.",
                    file=sys.stderr,
                )
            for fmt_idx, fmt in enumerate(formats):
                ext = EXT_MAP.get(fmt, ".txt").lstrip(".")
                output = format_result(
                    r,
                    fmt,
                    max_words_per_line=args.max_words_per_line,
                    max_chars_per_line=getattr(args, "max_chars_per_line", None),
                )

                if args.output:
                    out_path = Path(args.output)
                    # Treat as directory when: it's already a dir, OR batch mode, OR multiple formats requested
                    multi_fmt = len(formats) > 1
                    if (
                        out_path.is_dir()
                        or (is_batch and not out_path.suffix)
                        or (multi_fmt and not out_path.suffix)
                    ):
                        out_path.mkdir(parents=True, exist_ok=True)
                        # Apply output template if provided
                        if args.output_template:
                            filename = args.output_template.format(
                                stem=stem,
                                lang=lang,
                                ext=ext,
                                model=model_name,
                            )
                            dest = out_path / filename
                        else:
                            dest = out_path / (stem + EXT_MAP.get(fmt, ".txt"))
                    else:
                        dest = out_path
                    dest.write_text(output, encoding="utf-8")
                    if not args.quiet:
                        print(f"💾 {dest}", file=sys.stderr)
                else:
                    # Only print first format to stdout
                    if fmt_idx == 0:
                        if is_batch and fmt == "text":
                            print(f"\n=== {r['file']} ===")
                        print(output)

        # ---- Chapter detection output ----
        if _computed_chapters is not None:
            chapters = _computed_chapters  # reuse pre-computed result
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
                # Print to stdout after transcript — clear header so agents can parse it separately
                print(f"\n=== CHAPTERS ({len(chapters)}) ===\n{chapters_output}")

        # Write stats sidecar
        _write_stats(r, args)

        # Subtitle burn-in (single file only)
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


def _write_stats(r, args):
    """Write a JSON stats sidecar file for result r, if --stats-file is set."""
    if not getattr(args, "stats_file", None):
        return

    audio_path = r.get("_audio_path", r["file"])
    stem = Path(audio_path).stem
    stats_path = Path(args.stats_file)

    # Directory → write {stem}.stats.json inside it
    if stats_path.is_dir() or args.stats_file.endswith(os.sep):
        stats_path.mkdir(parents=True, exist_ok=True)
        dest = stats_path / f"{stem}.stats.json"
    else:
        dest = stats_path

    word_count = sum(len(s["text"].split()) for s in r.get("segments", []))
    elapsed = r["stats"]["processing_time"]
    duration = r.get("duration", 0)

    stats = {
        "file": r["file"],
        "language": r.get("language"),
        "language_probability": round(r.get("language_probability", 0), 4),
        "duration_seconds": round(duration, 2),
        "processing_time_seconds": elapsed,
        "realtime_factor": r["stats"].get("realtime_factor", 0),
        "segment_count": len(r.get("segments", [])),
        "word_count": word_count,
        "model": args.model,
        "compute_type": args.compute_type,
        "device": args.device,
    }

    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
        if not getattr(args, "quiet", False):
            print(f"📈 Stats: {dest}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Failed to write stats file {dest}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
