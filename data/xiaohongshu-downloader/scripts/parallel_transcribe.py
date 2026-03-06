#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "faster-whisper>=1.0.0",
# ]
# ///
"""
Parallel Whisper Transcription Script

Splits audio at silence boundaries using ffmpeg, then transcribes segments
in parallel using faster-whisper. Outputs WebVTT subtitles and plain text.

Usage:
    uv run parallel_transcribe.py audio.mp3 -o output_dir/
    python parallel_transcribe.py audio.mp3 -o output_dir/ --model base
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


def detect_silence(audio_path, min_silence_len=0.5, silence_thresh=-35):
    """Detect silence points in audio using ffmpeg silencedetect.

    Args:
        audio_path: Path to audio file.
        min_silence_len: Minimum silence duration in seconds.
        silence_thresh: Silence threshold in dB.

    Returns:
        List of (start, end) tuples for silence regions.
    """
    cmd = [
        "ffmpeg", "-i", audio_path,
        "-af", f"silencedetect=noise={silence_thresh}dB:d={min_silence_len}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    silences = []
    starts = re.findall(r'silence_start: ([\d.]+)', stderr)
    ends = re.findall(r'silence_end: ([\d.]+)', stderr)

    for s, e in zip(starts, ends):
        silences.append((float(s), float(e)))

    return silences


def get_audio_duration(audio_path):
    """Get audio duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-show_entries", "format=duration",
        "-of", "json",
        audio_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def split_audio_at_silence(audio_path, silences, total_duration,
                           max_segment=300, min_segment=10):
    """Split audio into segments at silence boundaries.

    Args:
        audio_path: Path to audio file.
        silences: List of (start, end) silence regions.
        total_duration: Total audio duration in seconds.
        max_segment: Maximum segment duration in seconds.
        min_segment: Minimum segment duration in seconds.

    Returns:
        List of (segment_path, start_time) tuples.
    """
    # Calculate split points at the midpoint of each silence region
    split_points = []
    for s, e in silences:
        mid = (s + e) / 2
        if mid > min_segment and mid < total_duration - min_segment:
            split_points.append(mid)

    # If no good silence points or audio is short, don't split
    if not split_points or total_duration <= max_segment:
        return [(audio_path, 0.0)]

    # Filter split points to ensure segments aren't too small or too large
    filtered = [0.0]
    for pt in sorted(split_points):
        if pt - filtered[-1] >= min_segment:
            filtered.append(pt)
    if total_duration - filtered[-1] < min_segment and len(filtered) > 1:
        filtered.pop()

    # Create segment files
    tmpdir = tempfile.mkdtemp(prefix="whisper_segments_")
    segments = []

    for i in range(len(filtered)):
        start = filtered[i]
        end = filtered[i + 1] if i + 1 < len(filtered) else total_duration
        segment_path = os.path.join(tmpdir, f"segment_{i:04d}.wav")

        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-ss", str(start),
            "-to", str(end),
            "-ar", "16000",   # Whisper expects 16kHz
            "-ac", "1",       # mono
            "-f", "wav",
            segment_path,
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        segments.append((segment_path, start))

    return segments


def transcribe_segment(segment_path, model_size="base", language=None):
    """Transcribe a single audio segment using faster-whisper.

    Args:
        segment_path: Path to audio segment.
        model_size: Whisper model size.
        language: Language code (None for auto-detect).

    Returns:
        List of (start, end, text) tuples with timestamps relative to segment.
    """
    from faster_whisper import WhisperModel

    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments_iter, info = model.transcribe(
        segment_path,
        language=language,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=300),
    )

    results = []
    for seg in segments_iter:
        results.append((seg.start, seg.end, seg.text.strip()))

    return results


def _transcribe_worker(args):
    """Worker function for parallel transcription."""
    segment_path, offset, model_size, language = args
    try:
        results = transcribe_segment(segment_path, model_size, language)
        # Adjust timestamps by the segment's offset in the original audio
        adjusted = [(s + offset, e + offset, text) for s, e, text in results]
        return adjusted
    except Exception as e:
        print(f"Error transcribing {segment_path}: {e}", file=sys.stderr)
        return []


def format_vtt_time(seconds):
    """Format seconds as VTT timestamp HH:MM:SS.mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def write_vtt(segments, output_path):
    """Write transcription results as WebVTT.

    Args:
        segments: List of (start, end, text) tuples.
        output_path: Path to write the VTT file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for i, (start, end, text) in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_vtt_time(start)} --> {format_vtt_time(end)}\n")
            f.write(f"{text}\n\n")


def write_txt(segments, output_path):
    """Write transcription results as plain text.

    Args:
        segments: List of (start, end, text) tuples.
        output_path: Path to write the text file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for _, _, text in segments:
            if text:
                f.write(text + "\n")


def parallel_transcribe(audio_path, output_dir, model_size="base",
                        language=None, max_workers=None):
    """Main transcription pipeline: split → parallel transcribe → merge.

    Args:
        audio_path: Path to audio file.
        output_dir: Directory for output files.
        model_size: Whisper model size (tiny/base/small/medium/large-v3).
        language: Language code or None for auto-detect.
        max_workers: Max parallel workers (defaults to CPU count).

    Returns:
        Tuple of (vtt_path, txt_path) or (None, None) on failure.
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"Audio: {audio_path}")
    print(f"Model: {model_size}")
    print(f"Language: {language or 'auto-detect'}")

    # Get duration
    total_duration = get_audio_duration(audio_path)
    print(f"Duration: {total_duration:.1f}s")

    # Detect silence and split
    print("Detecting silence boundaries...")
    silences = detect_silence(audio_path)
    print(f"Found {len(silences)} silence regions")

    segments = split_audio_at_silence(audio_path, silences, total_duration)
    print(f"Split into {len(segments)} segment(s)")

    # Transcribe in parallel
    all_results = []

    if len(segments) == 1:
        # Single segment — no need for multiprocessing
        print("Transcribing...")
        results = transcribe_segment(segments[0][0], model_size, language)
        offset = segments[0][1]
        all_results = [(s + offset, e + offset, text) for s, e, text in results]
    else:
        workers = max_workers or min(len(segments), os.cpu_count() or 4)
        print(f"Transcribing with {workers} parallel workers...")

        work_items = [
            (seg_path, offset, model_size, language)
            for seg_path, offset in segments
        ]

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(_transcribe_worker, item): i
                for i, item in enumerate(work_items)
            }
            results_by_idx = {}
            for future in as_completed(futures):
                idx = futures[future]
                results_by_idx[idx] = future.result()

        # Merge results in order
        for i in range(len(segments)):
            all_results.extend(results_by_idx.get(i, []))

    # Sort by start time
    all_results.sort(key=lambda x: x[0])

    if not all_results:
        print("Warning: No transcription results produced.")
        return None, None

    # Write output files
    vtt_path = os.path.join(output_dir, "subtitle.vtt")
    txt_path = os.path.join(output_dir, "transcript.txt")

    write_vtt(all_results, vtt_path)
    write_txt(all_results, txt_path)

    print(f"VTT written: {vtt_path} ({len(all_results)} cues)")
    print(f"TXT written: {txt_path}")

    # Cleanup temp segment files
    for seg_path, _ in segments:
        if seg_path != audio_path:
            try:
                os.remove(seg_path)
            except OSError:
                pass
            # Try to remove parent tmpdir
            try:
                os.rmdir(os.path.dirname(seg_path))
            except OSError:
                pass

    return vtt_path, txt_path


def main():
    parser = argparse.ArgumentParser(
        description="Parallel Whisper transcription with silence-based splitting"
    )
    parser.add_argument("audio", help="Path to audio file")
    parser.add_argument(
        "-o", "--output",
        default=".",
        help="Output directory (default: current directory)"
    )
    parser.add_argument(
        "-m", "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "-l", "--language",
        default=None,
        help="Language code (e.g., zh, en). Default: auto-detect"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=None,
        help="Max parallel workers (default: CPU count)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"Error: Audio file not found: {args.audio}")
        sys.exit(1)

    vtt, txt = parallel_transcribe(
        audio_path=args.audio,
        output_dir=args.output,
        model_size=args.model,
        language=args.language,
        max_workers=args.workers,
    )

    sys.exit(0 if vtt else 1)


if __name__ == "__main__":
    main()
