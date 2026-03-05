#!/usr/bin/env python3
"""
faster-whisper transcription CLI
High-performance speech-to-text using CTranslate2 backend with batched inference.

Features:
- Multiple output formats: text, JSON, SRT, VTT
- URL/YouTube input via yt-dlp
- Speaker diarization (optional, requires pyannote.audio)
- Batch processing with glob patterns and directories
- Initial prompt for domain-specific terminology
- Confidence-based segment filtering
- Performance statistics
"""

import sys
import os
import json
import time
import copy
import csv
import fnmatch
import glob
import argparse
import tempfile
import subprocess
import shutil
import re
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from faster_whisper import WhisperModel, BatchedInferencePipeline
except ImportError:
    print("Error: faster-whisper not installed", file=sys.stderr)
    print("Run setup: ./setup.sh", file=sys.stderr)
    sys.exit(1)


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


def format_ts_srt(seconds):
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_ts_vtt(seconds):
    """Format seconds as VTT timestamp: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_duration(seconds):
    """Format duration as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m}m{s:.0f}s"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h}h{m}m"


def is_url(path):
    """Check if the input looks like a URL."""
    return path.startswith(("http://", "https://", "www."))


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def to_srt(segments, max_words_per_line=None, max_chars_per_line=None):
    """Format segments as SRT subtitle content."""
    lines = []
    cue_num = 1
    for seg in segments:
        text = seg["text"].strip()
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"
        if max_chars_per_line and seg.get("words"):
            words = seg["words"]
            for chunk in split_words_by_chars(words, max_chars_per_line):
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(str(cue_num))
                lines.append(f"{format_ts_srt(chunk[0]['start'])} --> {format_ts_srt(chunk[-1]['end'])}")
                lines.append(chunk_text)
                lines.append("")
                cue_num += 1
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i:i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(str(cue_num))
                lines.append(f"{format_ts_srt(chunk[0]['start'])} --> {format_ts_srt(chunk[-1]['end'])}")
                lines.append(chunk_text)
                lines.append("")
                cue_num += 1
        else:
            lines.append(str(cue_num))
            lines.append(f"{format_ts_srt(seg['start'])} --> {format_ts_srt(seg['end'])}")
            lines.append(text)
            lines.append("")
            cue_num += 1
    return "\n".join(lines)


def to_vtt(segments, max_words_per_line=None, max_chars_per_line=None):
    """Format segments as WebVTT subtitle content."""
    lines = ["WEBVTT", ""]
    cue_num = 1
    for seg in segments:
        text = seg["text"].strip()
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"
        if max_chars_per_line and seg.get("words"):
            words = seg["words"]
            for chunk in split_words_by_chars(words, max_chars_per_line):
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(str(cue_num))
                lines.append(f"{format_ts_vtt(chunk[0]['start'])} --> {format_ts_vtt(chunk[-1]['end'])}")
                lines.append(chunk_text)
                lines.append("")
                cue_num += 1
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i:i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(str(cue_num))
                lines.append(f"{format_ts_vtt(chunk[0]['start'])} --> {format_ts_vtt(chunk[-1]['end'])}")
                lines.append(chunk_text)
                lines.append("")
                cue_num += 1
        else:
            lines.append(str(cue_num))
            lines.append(f"{format_ts_vtt(seg['start'])} --> {format_ts_vtt(seg['end'])}")
            lines.append(text)
            lines.append("")
            cue_num += 1
    return "\n".join(lines)


def to_text(segments):
    """Format segments as plain text, with speaker labels if present.

    Inserts paragraph breaks between segments marked with 'paragraph_start'.
    """
    has_speakers = any(seg.get("speaker") for seg in segments)
    has_paragraphs = any(seg.get("paragraph_start") for seg in segments)

    if not has_speakers:
        if not has_paragraphs:
            return "".join(seg["text"] for seg in segments).strip()
        parts = []
        for seg in segments:
            if seg.get("paragraph_start") and parts:
                parts.append("\n\n")
            parts.append(seg["text"])
        return "".join(parts).strip()

    lines = []
    current_speaker = None
    for seg in segments:
        sp = seg.get("speaker")
        if has_paragraphs and seg.get("paragraph_start") and lines:
            lines.append("\n")
        if sp and sp != current_speaker:
            current_speaker = sp
            lines.append(f"\n[{sp}]")
        lines.append(seg["text"])
    return "".join(lines).strip()


def to_tsv(segments):
    """Format segments as TSV (OpenAI Whisper format): start_ms TAB end_ms TAB text"""
    lines = []
    for seg in segments:
        start_ms = int(round(seg["start"] * 1000))
        end_ms = int(round(seg["end"] * 1000))
        text = seg["text"].strip()
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"
        lines.append(f"{start_ms}\t{end_ms}\t{text}")
    return "\n".join(lines)


def to_csv(segments):
    """Format segments as CSV with header: start_s, end_s, text [, speaker].

    Properly quoted via the stdlib csv module — safe for commas in text.
    start_s / end_s are decimal seconds (3 decimal places).
    """
    import io as _io
    has_speakers = any(seg.get("speaker") for seg in segments)
    fieldnames = ["start_s", "end_s", "text"] + (["speaker"] if has_speakers else [])
    buf = _io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for seg in segments:
        row = {
            "start_s": f"{seg['start']:.3f}",
            "end_s": f"{seg['end']:.3f}",
            "text": seg["text"].strip(),
        }
        if has_speakers:
            row["speaker"] = seg.get("speaker", "")
        writer.writerow(row)
    return buf.getvalue()


def format_ts_ass(seconds):
    """Format seconds as ASS/SSA timestamp: H:MM:SS.cc (centiseconds)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def to_ass(segments, max_words_per_line=None, max_chars_per_line=None):
    """Format segments as ASS/SSA (Advanced SubStation Alpha) subtitle content.

    Produces a standard v4.00+ ASS file with default styling. Compatible with
    Aegisub, VLC, mpv, MPC-HC, and most video editors.
    """
    header = (
        "[Script Info]\n"
        "Title: Transcript\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 384\n"
        "PlayResY: 288\n"
        "Timer: 100.0000\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,"
        "0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    )

    lines = [header]

    for seg in segments:
        text = seg["text"].strip().replace("\n", "\\N")
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"

        if max_chars_per_line and seg.get("words"):
            words = seg["words"]
            for chunk in split_words_by_chars(words, max_chars_per_line):
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(
                    f"Dialogue: 0,{format_ts_ass(chunk[0]['start'])},"
                    f"{format_ts_ass(chunk[-1]['end'])},Default,,0,0,0,,{chunk_text}"
                )
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i:i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(
                    f"Dialogue: 0,{format_ts_ass(chunk[0]['start'])},"
                    f"{format_ts_ass(chunk[-1]['end'])},Default,,0,0,0,,{chunk_text}"
                )
        else:
            lines.append(
                f"Dialogue: 0,{format_ts_ass(seg['start'])},"
                f"{format_ts_ass(seg['end'])},Default,,0,0,0,,{text}"
            )

    return "\n".join(lines)


def to_lrc(segments):
    """Format segments as LRC (timed lyrics) format used by music players.

    Format: [mm:ss.xx]Lyric line here
    Where xx = centiseconds (hundredths of a second).
    """
    lines = []
    for seg in segments:
        t = seg["start"]
        mm = int(t // 60)
        ss = t % 60
        ss_int = int(ss)
        cs = int((ss - ss_int) * 100)
        ts = f"[{mm:02d}:{ss_int:02d}.{cs:02d}]"
        text = seg["text"].strip()
        if seg.get("speaker"):
            text = f"[{seg['speaker']}] {text}"
        lines.append(f"{ts}{text}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# TTML (Timed Text Markup Language) output
# ---------------------------------------------------------------------------

def format_ts_ttml(seconds):
    """Format seconds as TTML timestamp: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def to_ttml(segments, language="en", max_words_per_line=None, max_chars_per_line=None):
    """Format segments as TTML (Timed Text Markup Language / DFXP) subtitles.

    Produces a W3C TTML 1.0 file compatible with broadcast platforms,
    Netflix, Amazon Prime, BBC iPlayer, and most professional video tools.
    """
    lang_attr = (language or "en").replace("_", "-")

    def xml_escape(text):
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<tt xml:lang="{lang_attr}"',
        '    xmlns="http://www.w3.org/ns/ttml"',
        '    xmlns:tts="http://www.w3.org/ns/ttml#styling"',
        '    xmlns:ttm="http://www.w3.org/ns/ttml#metadata">',
        '  <head>',
        '    <metadata>',
        '      <ttm:title>Transcript</ttm:title>',
        '    </metadata>',
        '    <styling>',
        '      <style xml:id="s1"',
        '             tts:fontFamily="Arial, Helvetica, sans-serif"',
        '             tts:fontSize="100%"',
        '             tts:fontWeight="normal"',
        '             tts:color="white"',
        '             tts:textAlign="center"',
        '             tts:backgroundColor="transparent"/>',
        '    </styling>',
        '    <layout>',
        '      <region xml:id="r1"',
        '              tts:origin="10% 85%"',
        '              tts:extent="80% 10%"',
        '              tts:displayAlign="before"/>',
        '    </layout>',
        '  </head>',
        '  <body>',
        '    <div region="r1">',
    ]

    for seg in segments:
        if max_chars_per_line and seg.get("words"):
            words = seg["words"]
            for chunk in split_words_by_chars(words, max_chars_per_line):
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                begin = format_ts_ttml(chunk[0]["start"])
                end = format_ts_ttml(chunk[-1]["end"])
                lines.append(
                    f'      <p begin="{begin}" end="{end}" style="s1">{xml_escape(chunk_text)}</p>'
                )
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i:i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                begin = format_ts_ttml(chunk[0]["start"])
                end = format_ts_ttml(chunk[-1]["end"])
                lines.append(
                    f'      <p begin="{begin}" end="{end}" style="s1">{xml_escape(chunk_text)}</p>'
                )
        else:
            text = seg["text"].strip()
            if seg.get("speaker"):
                text = f"[{seg['speaker']}] {text}"
            begin = format_ts_ttml(seg["start"])
            end = format_ts_ttml(seg["end"])
            lines.append(
                f'      <p begin="{begin}" end="{end}" style="s1">{xml_escape(text)}</p>'
            )

    lines.extend([
        '    </div>',
        '  </body>',
        '</tt>',
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------

def to_html(result):
    """Format transcript as HTML with confidence-colored words."""
    file_name = result.get("file", "")
    language = result.get("language", "")
    duration = result.get("duration", 0)
    segments = result.get("segments", [])

    def fmt_ts(s):
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:06.3f}" if h else f"{m:02d}:{sec:06.3f}"

    segs_html = []
    for seg in segments:
        ts = f'<span class="ts">[{fmt_ts(seg["start"])} → {fmt_ts(seg["end"])}]</span>'
        speaker_html = ""
        if seg.get("speaker"):
            speaker_html = f' <span class="speaker">[{seg["speaker"]}]</span>'

        words = seg.get("words")
        if words:
            word_parts = []
            for w in words:
                p = w.get("probability", 1.0)
                if p >= 0.9:
                    cls = "conf-high"
                elif p >= 0.7:
                    cls = "conf-med"
                else:
                    cls = "conf-low"
                word_parts.append(f'<span class="{cls}" title="{p:.2f}">{w["word"]}</span>')
            text_html = "".join(word_parts)
        else:
            text_html = seg.get("text", "").strip()

        segs_html.append(
            f'<div class="seg">{ts}{speaker_html} <span class="text">{text_html}</span></div>'
        )

    dur_str = f"{int(duration // 60)}m{int(duration % 60)}s" if duration else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Transcript: {file_name}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 820px; margin: 2em auto; padding: 0 1em; color: #222; line-height: 1.6; }}
    h1 {{ font-size: 1.4em; color: #333; margin-bottom: 0.2em; }}
    .meta {{ color: #888; font-size: 0.85em; margin-bottom: 1.5em; }}
    .seg {{ margin: 0.5em 0; padding: 0.3em 0.5em; border-left: 3px solid #ddd; }}
    .seg:hover {{ background: #f9f9f9; }}
    .ts {{ color: #888; font-size: 0.8em; font-family: monospace; }}
    .speaker {{ font-weight: bold; color: #0066cc; }}
    .text {{ }}
    .conf-high {{ background: #d4edda; border-radius: 2px; }}
    .conf-med  {{ background: #fff3cd; border-radius: 2px; }}
    .conf-low  {{ background: #f8d7da; border-radius: 2px; }}
    .legend {{ margin-top: 2em; font-size: 0.8em; color: #666; }}
    .legend span {{ padding: 1px 6px; border-radius: 2px; margin-right: 6px; }}
  </style>
</head>
<body>
  <h1>📝 {file_name}</h1>
  <div class="meta">Language: {language} &nbsp;·&nbsp; Duration: {dur_str}</div>
  <div class="transcript">
    {"".join(segs_html)}
  </div>
  <div class="legend">
    Word confidence: <span class="conf-high">≥90%</span>
    <span class="conf-med">70–89%</span>
    <span class="conf-low">&lt;70%</span>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Hallucination filter
# ---------------------------------------------------------------------------

HALLUCINATION_PATTERNS = [
    re.compile(r'^\s*\[?\s*(music|applause|laughter|silence|inaudible|background noise)\s*\]?\s*$', re.I),
    re.compile(r'^\s*\(?\s*(music|applause|laughter|upbeat music|dramatic music|suspenseful music|tense music|gentle music)\s*\)?\s*$', re.I),
    re.compile(r'thank\s+you\s+for\s+watching', re.I),
    re.compile(r'thank\s+you\s+for\s+(listening|your\s+attention)', re.I),
    re.compile(r'subtitles?\s+by', re.I),
    re.compile(r'(transcribed|captioned)\s+by', re.I),
    re.compile(r'^\s*www\.\S+\s*$', re.I),
    re.compile(r'^\s*[.!?,;:\u2026]+\s*$'),  # lone punctuation / ellipsis
    re.compile(r'^\s*$'),                      # empty
]


def filter_hallucinations(segments):
    """Remove segments matching common Whisper hallucination patterns."""
    filtered = []
    prev_text = None
    for seg in segments:
        text = seg.get("text", "").strip()
        if any(p.search(text) for p in HALLUCINATION_PATTERNS):
            continue
        if text == prev_text:  # exact duplicate consecutive segment
            continue
        prev_text = text
        filtered.append(seg)
    return filtered


# ---------------------------------------------------------------------------
# Channel extraction
# ---------------------------------------------------------------------------

def extract_channel(audio_path, channel, quiet=False):
    """Extract a stereo channel from audio using ffmpeg.

    channel: 'left' (c0), 'right' (c1), or 'mix' (no-op, returns original).
    Returns (output_path, tmp_path_to_cleanup_or_None).
    """
    if channel == "mix":
        return audio_path, None

    if not shutil.which("ffmpeg"):
        if not quiet:
            print("⚠️  ffmpeg not found — cannot extract channel; using full mix", file=sys.stderr)
        return audio_path, None

    pan = "c0" if channel == "left" else "c1"
    tmp_path = audio_path + f".{channel}.wav"
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-af", f"pan=mono|c0={pan}",
        "-ar", "16000",
        tmp_path,
    ]
    if not quiet:
        print(f"🎚️  Extracting {channel} channel...", file=sys.stderr)
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return tmp_path, tmp_path
    except subprocess.CalledProcessError:
        if not quiet:
            print("⚠️  Channel extraction failed; using full mix", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return audio_path, None


# ---------------------------------------------------------------------------
# Filler word removal
# ---------------------------------------------------------------------------

_FILLER_PATTERNS = [
    # Single-word hesitation sounds (word boundary match)
    re.compile(r'\b(um+|uh+|er+|ah+|hmm+|hm+)\b', re.I),
    # Discourse markers (case-insensitive, word boundaries)
    re.compile(r'\byou know\b', re.I),
    re.compile(r'\bI mean\b', re.I),
    re.compile(r'\byou see\b', re.I),
]

# Single-word filler matcher (stripped of surrounding whitespace and punctuation)
_FILLER_WORD_RE = re.compile(r'^(um+|uh+|er+|ah+|hmm+|hm+)$', re.I)

# Multi-word discourse markers as tuples of lowercased bare words
_FILLER_BIGRAMS = [("you", "know"), ("i", "mean"), ("you", "see")]


def _word_bare(w):
    """Return the bare lowercased text of a word token (strip spaces + punctuation)."""
    return re.sub(r"[^\w']", "", w["word"].lower().strip())


def _filter_word_list(words):
    """Remove filler words from a word list.

    Removes single-word hesitations and multi-word discourse markers.
    Returns a new list (does not mutate the input).
    """
    if not words:
        return words

    # First pass: mark words to remove
    remove_idx = set()

    # Single-word fillers
    for i, w in enumerate(words):
        if _FILLER_WORD_RE.match(_word_bare(w)):
            remove_idx.add(i)

    # Multi-word bigram markers
    for i in range(len(words) - 1):
        if i in remove_idx or i + 1 in remove_idx:
            continue
        pair = (_word_bare(words[i]), _word_bare(words[i + 1]))
        if pair in _FILLER_BIGRAMS:
            remove_idx.add(i)
            remove_idx.add(i + 1)

    return [w for idx, w in enumerate(words) if idx not in remove_idx]


def remove_filler_words(segments):
    """Strip hesitation fillers and discourse markers from segment text and word list.

    Modifies segment['text'] using regex substitution and also filters
    segment['words'] to remove matching word tokens.  Drops segments that
    become empty after cleaning.
    """
    cleaned = []
    for seg in segments:
        text = seg["text"]
        for pat in _FILLER_PATTERNS:
            text = pat.sub("", text)
        # Remove leading punctuation left behind after filler removal
        text = re.sub(r'^[\s,.!?;:]+', '', text)
        # Fix up punctuation spacing: remove spaces before punctuation
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        # Collapse consecutive identical punctuation (e.g. ",," → ",")
        text = re.sub(r'([,.!?;:])\1+', r'\1', text)
        # Remove orphaned commas before terminal punctuation (e.g. ",?" → "?")
        text = re.sub(r',([.!?])', r'\1', text)
        # Collapse multiple spaces
        text = re.sub(r'  +', ' ', text)
        text = text.strip()
        if not text:
            continue
        seg = dict(seg)  # shallow copy to avoid mutating original
        seg["text"] = text
        # Also clean the word list so word-split formatters (--max-words-per-line,
        # --max-chars-per-line) don't re-introduce filler words in SRT/VTT/ASS/TTML.
        if seg.get("words"):
            seg["words"] = _filter_word_list(seg["words"])
        cleaned.append(seg)
    return cleaned


# ---------------------------------------------------------------------------
# Paragraph detection
# ---------------------------------------------------------------------------

def detect_paragraphs(segments, min_gap=3.0, sentence_gap=1.5):
    """Mark segment dicts with 'paragraph_start': True at paragraph boundaries.

    A new paragraph starts when:
    - The gap to the previous segment >= min_gap seconds, OR
    - The previous segment ends a sentence (terminal punct) AND
      the gap >= sentence_gap seconds.
    The first segment always gets paragraph_start = True.
    Uses _TERMINAL_PUNCT defined in the merge_sentences section below.
    """
    if not segments:
        return segments
    segments[0]["paragraph_start"] = True
    for i in range(1, len(segments)):
        prev = segments[i - 1]
        curr = segments[i]
        gap = curr["start"] - prev["end"]
        prev_text = prev.get("text", "").rstrip()
        ends_sentence = bool(_TERMINAL_PUNCT.search(prev_text))
        if gap >= min_gap or (ends_sentence and gap >= sentence_gap):
            curr["paragraph_start"] = True
    return segments


# ---------------------------------------------------------------------------
# Character-based subtitle line splitting
# ---------------------------------------------------------------------------

def split_words_by_chars(words, max_chars):
    """Split a list of word dicts into chunks where each chunk's joined text
    fits within max_chars characters.

    Returns a list of word lists (chunks).
    """
    if not words:
        return [words]
    chunks = []
    current = []
    current_len = 0
    for w in words:
        word_text = w["word"]
        candidate_len = current_len + len(word_text)
        if current and candidate_len > max_chars:
            chunks.append(current)
            current = [w]
            current_len = len(word_text)
        else:
            current.append(w)
            current_len = candidate_len
    if current:
        chunks.append(current)
    return chunks


# ---------------------------------------------------------------------------
# Speaker name mapping
# ---------------------------------------------------------------------------

def apply_speaker_names(segments, names_str):
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
# Subtitle burn-in
# ---------------------------------------------------------------------------

def burn_subtitles(video_path, srt_content, output_path, quiet=False):
    """Burn SRT subtitles into a video file using ffmpeg."""
    tmp_srt = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".srt", delete=False, encoding="utf-8"
        ) as f:
            f.write(srt_content)
            tmp_srt = f.name

        # Escape colons/backslashes in path for ffmpeg filtergraph
        escaped = tmp_srt.replace("\\", "/").replace(":", "\\:")
        cmd = [
            "ffmpeg", "-y", "-i", video_path,
            "-vf", f"subtitles={escaped}",
            "-c:a", "copy",
            output_path,
        ]
        if not quiet:
            print(f"🎬 Burning subtitles into {output_path}...", file=sys.stderr)
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd, check=True, capture_output=True)
        if not quiet:
            print(f"✅ Burned: {output_path}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Burn-in failed: {e}", file=sys.stderr)
    finally:
        if tmp_srt and os.path.exists(tmp_srt):
            os.unlink(tmp_srt)


# ---------------------------------------------------------------------------
# URL download
# ---------------------------------------------------------------------------

def download_url(url, quiet=False):
    """Download audio from URL using yt-dlp. Returns (audio_path, tmpdir)."""
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        pipx_path = Path.home() / ".local/share/pipx/venvs/yt-dlp/bin/yt-dlp"
        if pipx_path.exists():
            ytdlp = str(pipx_path)
        else:
            print("Error: yt-dlp not found. Install with: pipx install yt-dlp", file=sys.stderr)
            sys.exit(1)

    tmpdir = tempfile.mkdtemp(prefix="faster-whisper-")
    out_tmpl = os.path.join(tmpdir, "audio.%(ext)s")

    cmd = [ytdlp, "-x", "--audio-format", "mp3", "-o", out_tmpl, "--no-playlist"]
    if quiet:
        cmd.append("-q")
    cmd.append(url)

    if not quiet:
        print("⬇️  Downloading audio from URL...", file=sys.stderr)

    try:
        subprocess.run(cmd, check=True, capture_output=quiet)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading URL: {e}", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    files = list(Path(tmpdir).glob("audio.*"))
    if not files:
        print("Error: No audio file downloaded", file=sys.stderr)
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    return str(files[0]), tmpdir


# ---------------------------------------------------------------------------
# RSS / Podcast feed
# ---------------------------------------------------------------------------

def fetch_rss_episodes(rss_url, latest=5, quiet=False):
    """Parse a podcast RSS feed and return audio enclosure URLs.

    Returns list of (url, title) tuples, newest-first (standard RSS order).
    Uses only stdlib — no extra dependencies.
    """
    import urllib.request
    import xml.etree.ElementTree as ET

    if not quiet:
        print(f"📡 Fetching RSS feed: {rss_url}", file=sys.stderr)

    try:
        req = urllib.request.Request(
            rss_url, headers={"User-Agent": "faster-whisper-skill/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read()
    except Exception as e:
        print(f"Error fetching RSS feed: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"Error parsing RSS XML: {e}", file=sys.stderr)
        sys.exit(1)

    items = root.findall(".//item")
    if not items:
        print("Error: No <item> elements found in RSS feed", file=sys.stderr)
        sys.exit(1)

    episodes = []
    for item in items:
        enclosure = item.find("enclosure")
        if enclosure is None:
            continue
        url = (enclosure.get("url") or "").strip()
        if not url:
            continue
        title_el = item.find("title")
        title = (title_el.text or url).strip() if title_el is not None else url
        episodes.append((url, title))

    if not episodes:
        print("Error: No audio <enclosure> elements found in RSS feed", file=sys.stderr)
        sys.exit(1)

    total = len(episodes)
    take = min(latest, total) if latest else total
    if not quiet:
        print(f"   Found {total} episode(s) — processing {take}", file=sys.stderr)

    return episodes[:take] if latest else episodes


# ---------------------------------------------------------------------------
# Audio preprocessing
# ---------------------------------------------------------------------------

def preprocess_audio(audio_path, normalize=False, denoise=False, quiet=False):
    """Preprocess audio with ffmpeg filters (normalize volume, reduce noise).

    Returns (processed_path, tmp_path_to_cleanup_or_None).
    """
    if not normalize and not denoise:
        return audio_path, None

    filters = []
    if denoise:
        # High-pass to remove rumble + FFT-based noise reduction
        filters.append("highpass=f=200")
        filters.append("afftdn=nf=-25")
    if normalize:
        # EBU R128 loudness normalization
        filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")

    tmp_path = audio_path + ".preprocessed.wav"
    filter_str = ",".join(filters)
    cmd = [
        "ffmpeg", "-y", "-i", audio_path,
        "-af", filter_str,
        "-ar", "16000", "-ac", "1",
        tmp_path,
    ]

    if not quiet:
        labels = []
        if normalize:
            labels.append("normalizing")
        if denoise:
            labels.append("denoising")
        print(f"🔧 Preprocessing: {' + '.join(labels)}...", file=sys.stderr)

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return tmp_path, tmp_path
    except subprocess.CalledProcessError:
        if not quiet:
            print("⚠️  Preprocessing failed, using original audio", file=sys.stderr)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        return audio_path, None


# ---------------------------------------------------------------------------
# Word-level alignment (wav2vec2)
# ---------------------------------------------------------------------------

_align_cache = {}  # reuse model across files in batch mode

# Characters to strip before alignment (numbers, punctuation except apostrophe)
_ALIGN_CLEAN = re.compile(r"[^a-z'\u00e0-\u00ff]")  # keep letters, ', accented


def run_alignment(audio_path, segments, quiet=False):
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
        print(
            "Error: torchaudio not installed (required for --precise).\n"
            "  Reinstall with: ./setup.sh",
            file=sys.stderr,
        )
        sys.exit(1)

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
        except Exception:
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
        word_map = []  # (index-in-words, token_groups, group_count)
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
            except Exception:
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
        except Exception:
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


# ---------------------------------------------------------------------------
# Speaker diarization
# ---------------------------------------------------------------------------

def run_diarization(audio_path, segments, quiet=False, min_speakers=None, max_speakers=None, hf_token=None):
    """Assign speaker labels to segments using pyannote.audio."""
    try:
        from pyannote.audio import Pipeline as PyannotePipeline
    except ImportError:
        print(
            "Error: pyannote.audio not installed.\n"
            "  Install: ./setup.sh --diarize\n"
            "  Or:      pip install pyannote.audio",
            file=sys.stderr,
        )
        sys.exit(1)

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
        sys.exit(1)

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
                check=True, capture_output=True,
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
            new_segments.append({
                "start": current_words[0]["start"],
                "end": current_words[-1]["end"],
                "text": "".join(w["word"] for w in current_words),
                "speaker": current_speaker,
                "words": list(current_words),
            })

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


# ---------------------------------------------------------------------------
# Speaker audio export
# ---------------------------------------------------------------------------

def export_speakers_audio(audio_path, segments, output_dir, quiet=False):
    """Export each speaker's audio as a separate WAV file.

    Groups diarized segments by speaker and uses ffmpeg's *aselect* filter to
    extract and concatenate each speaker's turns into a single file.
    Requires ffmpeg and diarized segments (speaker field on each segment).
    """
    if not shutil.which("ffmpeg"):
        print("⚠️  --export-speakers requires ffmpeg in PATH", file=sys.stderr)
        return

    # Group by speaker
    speaker_ranges = {}
    for seg in segments:
        sp = seg.get("speaker")
        if not sp:
            continue
        speaker_ranges.setdefault(sp, []).append((seg["start"], seg["end"]))

    if not speaker_ranges:
        print(
            "⚠️  No speaker-labeled segments found — diarization produced no speakers.\n"
            "     This usually means no speech was detected in the audio.",
            file=sys.stderr,
        )
        return

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for speaker, ranges in sorted(speaker_ranges.items()):
        out_file = out_dir / f"{speaker}.wav"

        # Build aselect expression: 'between(t,S,E)+between(t,S,E)+...'
        select_expr = "+".join(
            f"between(t,{start:.3f},{end:.3f})" for start, end in ranges
        )

        cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-af", f"aselect='{select_expr}',asetpts=N/SR/TB",
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


# ---------------------------------------------------------------------------
# Sentence merging
# ---------------------------------------------------------------------------

_TERMINAL_PUNCT = re.compile(r'[.!?…。！？]["\')\]]*\s*$')


def merge_sentences(segments):
    """Merge consecutive short segments into sentence-boundary-aware chunks.

    A new chunk is started when:
    - The previous segment's text ends with terminal punctuation (. ! ? … etc.)
    - OR the gap between consecutive segments exceeds 2 seconds.
    """
    MAX_GAP = 2.0  # seconds

    merged = []
    accum = []

    def flush():
        if not accum:
            return
        start = accum[0]["start"]
        end = accum[-1]["end"]
        text = " ".join(s["text"].strip() for s in accum).strip()
        words = []
        for s in accum:
            words.extend(s.get("words", []))
        # Most common speaker in merged segments
        speakers = [s.get("speaker") for s in accum if s.get("speaker")]
        speaker = max(set(speakers), key=speakers.count) if speakers else None
        seg = {"start": start, "end": end, "text": text}
        if words:
            seg["words"] = words
        if speaker:
            seg["speaker"] = speaker
        merged.append(seg)

    for seg in segments:
        if accum:
            gap = seg["start"] - accum[-1]["end"]
            if gap > MAX_GAP:
                flush()
                accum = []
        accum.append(seg)
        if _TERMINAL_PUNCT.search(seg["text"]):
            flush()
            accum = []

    flush()
    return merged


# ---------------------------------------------------------------------------
# Chapter detection
# ---------------------------------------------------------------------------

def detect_chapters(segments, min_gap=8.0):
    """Detect chapter breaks from silence gaps between segments.

    A new chapter starts when the silence between two consecutive segments
    exceeds *min_gap* seconds.  Returns a list of chapter dicts:
        {"chapter": N, "start": seconds, "title": "Chapter N"}
    """
    if not segments:
        return []

    chapters = [{"chapter": 1, "start": segments[0]["start"], "title": "Chapter 1"}]
    chapter_num = 1

    for i in range(1, len(segments)):
        gap = segments[i]["start"] - segments[i - 1]["end"]
        if gap >= min_gap:
            chapter_num += 1
            chapters.append({
                "chapter": chapter_num,
                "start": segments[i]["start"],
                "title": f"Chapter {chapter_num}",
            })

    return chapters


def _fmt_chapter_ts(seconds):
    """Format chapter timestamp: M:SS or H:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def format_chapters_output(chapters, fmt="youtube"):
    """Render chapter list.

    fmt="youtube"  → "0:00 Chapter 1\\n5:30 Chapter 2" (YouTube description format)
    fmt="text"     → "Chapter 1: 00:00:00\\nChapter 2: 00:05:30"
    fmt="json"     → JSON array
    """
    if fmt == "json":
        return json.dumps(chapters, indent=2, ensure_ascii=False)

    if fmt == "text":
        lines = []
        for ch in chapters:
            h = int(ch["start"] // 3600)
            m = int((ch["start"] % 3600) // 60)
            s = int(ch["start"] % 60)
            ts = f"{h:02d}:{m:02d}:{s:02d}"
            lines.append(f"{ch['title']}: {ts}")
        return "\n".join(lines)

    # Default: YouTube-compatible "M:SS Title"
    return "\n".join(
        f"{_fmt_chapter_ts(ch['start'])} {ch['title']}" for ch in chapters
    )


# ---------------------------------------------------------------------------
# Transcript search
# ---------------------------------------------------------------------------

def search_transcript(segments, query, fuzzy=False):
    """Search transcript segments for *query*.

    Returns a list of matching segment dicts (with start, end, text, speaker).
    Case-insensitive.  With fuzzy=True, also matches partial/approximate terms
    by checking individual word tokens for similarity (ratio ≥ 0.6).
    """
    import difflib

    query_lower = query.lower()
    matches = []

    for seg in segments:
        text = seg["text"].strip()
        text_lower = text.lower()

        matched = query_lower in text_lower

        if not matched and fuzzy:
            # Check each word token in the segment for similarity to query.
            # This handles short queries (e.g. "wrld" matching "world") better
            # than comparing the full segment text via SequenceMatcher ratio.
            words_in_seg = re.findall(r"[\w']+", text_lower)
            for word in words_in_seg:
                ratio = difflib.SequenceMatcher(None, query_lower, word).ratio()
                if ratio >= 0.6:
                    matched = True
                    break
            # Fallback: also try full-text ratio for multi-word query phrases
            if not matched and " " in query_lower:
                ratio = difflib.SequenceMatcher(None, query_lower, text_lower).ratio()
                if ratio >= 0.6:
                    matched = True

        if matched:
            matches.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": text,
                "speaker": seg.get("speaker"),
            })

    return matches


def format_search_results(matches, query):
    """Format search results for display."""
    if not matches:
        return f'No matches found for: "{query}"'

    lines = [f'🔍 {len(matches)} match(es) for "{query}":']
    for m in matches:
        ts = _fmt_chapter_ts(m["start"])
        speaker = f"[{m['speaker']}] " if m.get("speaker") else ""
        lines.append(f"  [{ts}]  {speaker}{m['text']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Language map (per-file language override for batch mode)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# File resolution
# ---------------------------------------------------------------------------

AUDIO_EXTS = {
    ".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm",
    ".mp4", ".mkv", ".avi", ".wma", ".aac",
}


def resolve_inputs(inputs):
    """Expand globs, directories, and URLs into a flat list of audio paths."""
    files = []
    for inp in inputs:
        if is_url(inp):
            files.append(inp)
            continue
        expanded = sorted(glob.glob(inp, recursive=True)) or [inp]
        for p_str in expanded:
            p = Path(p_str)
            if p.is_dir():
                files.extend(
                    str(f) for f in sorted(p.iterdir())
                    if f.is_file() and f.suffix.lower() in AUDIO_EXTS
                )
            elif p.is_file():
                files.append(str(p))
            else:
                print(f"Warning: not found: {inp}", file=sys.stderr)
    return files


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
        effective_path, channel_tmp = extract_channel(
            effective_path, channel, quiet=args.quiet
        )

    if args.normalize or args.denoise:
        effective_path, preprocess_tmp = preprocess_audio(
            effective_path, normalize=args.normalize, denoise=args.denoise,
            quiet=args.quiet,
        )

    need_words = (
        args.word_timestamps
        or args.min_confidence is not None
        or args.diarize   # word-level needed for accurate speaker assignment
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
                raise ValueError(f"Invalid clip range '{clip_str}'. Expected 'start,end' (seconds).")
        kw["clip_timestamps"] = parsed_clips
    if args.progress:
        kw["log_progress"] = True

    if not args.no_batch:
        kw["batch_size"] = args.batch_size

    # VAD tuning parameters
    vad_dict = {}
    vad_threshold = args.vad_threshold if args.vad_threshold is not None else args.vad_onset
    vad_neg_threshold = args.vad_neg_threshold if args.vad_neg_threshold is not None else args.vad_offset
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
            print(f"⚠️  Invalid --suppress-tokens value: {args.suppress_tokens!r} — skipped", file=sys.stderr)

    if args.max_initial_timestamp is not None:
        kw["max_initial_timestamp"] = args.max_initial_timestamp

    if args.prepend_punctuations is not None:
        kw["prepend_punctuations"] = args.prepend_punctuations

    if args.append_punctuations is not None:
        kw["append_punctuations"] = args.append_punctuations

    segments_iter, info = pipeline.transcribe(effective_path, **kw)

    segments = []
    full_text = ""

    for seg in segments_iter:
        # Confidence filter (needs word-level probabilities)
        if args.min_confidence is not None and seg.words:
            avg = sum(w.probability for w in seg.words) / len(seg.words)
            if avg < args.min_confidence:
                continue

        full_text += seg.text
        seg_data = {"start": seg.start, "end": seg.end, "text": seg.text}

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
            effective_path, segments, quiet=args.quiet,
            min_speakers=args.min_speakers, max_speakers=args.max_speakers,
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
        "text": full_text.strip(),
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
# Output
# ---------------------------------------------------------------------------

EXT_MAP = {
    "text": ".txt", "json": ".json", "srt": ".srt",
    "vtt": ".vtt", "tsv": ".tsv", "csv": ".csv", "lrc": ".lrc",
    "html": ".html", "ass": ".ass", "ttml": ".ttml",
}


def format_result(result, fmt, max_words_per_line=None, max_chars_per_line=None):
    """Render a result dict in the requested format."""
    if fmt == "json":
        return json.dumps(result, indent=2, ensure_ascii=False)
    if fmt == "srt":
        return to_srt(result["segments"], max_words_per_line=max_words_per_line,
                      max_chars_per_line=max_chars_per_line)
    if fmt == "vtt":
        return to_vtt(result["segments"], max_words_per_line=max_words_per_line,
                      max_chars_per_line=max_chars_per_line)
    if fmt == "tsv":
        return to_tsv(result["segments"])
    if fmt == "csv":
        return to_csv(result["segments"])
    if fmt == "lrc":
        return to_lrc(result["segments"])
    if fmt == "html":
        return to_html(result)
    if fmt == "ass":
        return to_ass(result["segments"], max_words_per_line=max_words_per_line,
                      max_chars_per_line=max_chars_per_line)
    if fmt == "ttml":
        return to_ttml(
            result["segments"],
            language=result.get("language", "en"),
            max_words_per_line=max_words_per_line,
            max_chars_per_line=max_chars_per_line,
        )
    return to_text(result["segments"])


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
                ["uv", "pip", "install", "--python", str(_venv_python), "--upgrade", "faster-whisper"],
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
        "audio", nargs="*", metavar="AUDIO",
        help="Audio file(s), directory, glob pattern, or URL. Optional when --rss is used.",
    )

    # --- Model & language ---
    p.add_argument(
        "-m", "--model", default="distil-large-v3.5",
        help="Whisper model (default: distil-large-v3.5)",
    )
    p.add_argument(
        "--revision", default=None, metavar="REV",
        help="Model revision (git branch/tag/commit hash) to pin a specific version",
    )
    p.add_argument(
        "-l", "--language", default=None,
        help="Language code, e.g. en, es, fr (auto-detects if omitted)",
    )
    p.add_argument(
        "--language-map", default=None, metavar="MAP",
        help="Per-file language override for batch mode. Inline: 'interview*.mp3=en,lecture.wav=fr' "
             "or JSON file: '@/path/to/map.json'. Overrides --language for matched files; "
             "unmatched files fall back to --language (or auto-detect). "
             "Patterns support fnmatch globs on filename or stem.",
    )
    p.add_argument(
        "--initial-prompt", default=None, metavar="TEXT",
        help="Prompt to condition the model (terminology, formatting hints)",
    )
    p.add_argument(
        "--prefix", default=None, metavar="TEXT",
        help="Prefix to condition the first segment (e.g. known starting words)",
    )
    p.add_argument(
        "--hotwords", default=None, metavar="WORDS",
        help="Hotwords to boost recognition (space-separated)",
    )
    p.add_argument(
        "--translate", action="store_true",
        help="Translate to English instead of transcribing",
    )
    p.add_argument(
        "--multilingual", action="store_true",
        help="Enable multilingual/code-switching mode (helps smaller models)",
    )
    p.add_argument(
        "--hf-token", default=None, metavar="TOKEN",
        help="HuggingFace token for private models and diarization (overrides cached token)",
    )
    p.add_argument(
        "--model-dir", default=None, metavar="PATH",
        help="Custom directory for model cache (default: ~/.cache/huggingface/hub)",
    )

    # --- Output format ---
    p.add_argument(
        "-f", "--format", default="text",
        help="Output format (default: text). "
             "Accepts one or a comma-separated list of: "
             "text, json, srt, vtt, tsv, csv, lrc, html, ass, ttml. "
             "Example: --format srt,text",
    )
    p.add_argument(
        "--word-timestamps", action="store_true",
        help="Include word-level timestamps (auto-enabled for --diarize)",
    )
    p.add_argument(
        "--stream", action="store_true",
        help="Output segments as they are transcribed (streaming mode; disables diarize/alignment)",
    )
    p.add_argument(
        "--max-words-per-line", type=int, default=None, metavar="N",
        help="For SRT/VTT, split long segments into sub-cues with at most N words each "
             "(requires word-level timestamps; falls back to full segment if no word data)",
    )
    p.add_argument(
        "--max-chars-per-line", type=int, default=None, metavar="N",
        help="For SRT/VTT/ASS/TTML, split subtitle lines so each fits within N characters "
             "(requires word-level timestamps; takes priority over --max-words-per-line)",
    )
    p.add_argument(
        "--channel", default="mix", choices=["left", "right", "mix"],
        help="Stereo channel to transcribe: left, right, or mix (default: mix). "
             "Requires ffmpeg.",
    )
    p.add_argument(
        "--clean-filler", action="store_true",
        help="Remove hesitation fillers (um, uh, er, ah, hmm) and discourse markers "
             "(you know, I mean, you see) from transcript text",
    )
    p.add_argument(
        "--detect-paragraphs", action="store_true",
        help="Insert paragraph breaks in text output based on silence gaps between segments",
    )
    p.add_argument(
        "--paragraph-gap", type=float, default=3.0, metavar="SEC",
        help="Minimum silence gap in seconds to start a new paragraph (default: 3.0). "
             "Used with --detect-paragraphs",
    )
    p.add_argument(
        "--merge-sentences", action="store_true",
        help="Merge consecutive segments into sentence-level chunks "
             "(useful for improving SRT/VTT readability)",
    )
    p.add_argument(
        "-o", "--output", default=None, metavar="PATH",
        help="Output file or directory (directory for batch mode)",
    )
    p.add_argument(
        "--output-template", default=None, metavar="TEMPLATE",
        help="Output filename template for batch mode. Supports: "
             "{stem} (input filename without ext), {lang} (detected language), "
             "{ext} (format extension), {model} (model name). "
             "Example: '{stem}_{lang}.{ext}' → 'interview_en.srt'",
    )

    # --- Inference tuning ---
    p.add_argument(
        "--beam-size", type=int, default=5, metavar="N",
        help="Beam search size (default: 5)",
    )
    p.add_argument(
        "--temperature", default=None, metavar="T",
        help="Sampling temperature or comma-separated fallback list (e.g. '0.0' or '0.0,0.2,0.4'); "
             "default uses faster-whisper's built-in schedule [0.0,0.2,0.4,0.6,0.8,1.0]",
    )
    p.add_argument(
        "--no-speech-threshold", type=float, default=None, metavar="PROB",
        help="Probability threshold below which segments are treated as silence/no-speech "
             "(default: 0.6)",
    )
    p.add_argument(
        "--batch-size", type=int, default=8, metavar="N",
        help="Batch size for batched inference (default: 8; reduce if OOM)",
    )
    p.add_argument("--no-vad", action="store_true",
                    help="Disable voice activity detection")
    p.add_argument(
        "--vad-threshold", type=float, default=None, metavar="T",
        help="VAD speech probability threshold (default: 0.5); higher = more conservative",
    )
    p.add_argument(
        "--vad-neg-threshold", type=float, default=None, metavar="T",
        help="VAD negative threshold for ending speech segments (default: auto)",
    )
    p.add_argument(
        "--vad-onset", type=float, default=None, metavar="T",
        help="Alias for --vad-threshold (legacy compatibility)",
    )
    p.add_argument(
        "--vad-offset", type=float, default=None, metavar="T",
        help="Alias for --vad-neg-threshold (legacy compatibility)",
    )
    p.add_argument(
        "--min-speech-duration", type=int, default=None, metavar="MS",
        help="Minimum speech segment duration in milliseconds (default: 0)",
    )
    p.add_argument(
        "--max-speech-duration", type=float, default=None, metavar="SEC",
        help="Maximum speech segment duration in seconds (default: unlimited)",
    )
    p.add_argument(
        "--min-silence-duration", type=int, default=None, metavar="MS",
        help="Minimum silence duration before splitting a segment in ms (default: 2000)",
    )
    p.add_argument(
        "--speech-pad", type=int, default=None, metavar="MS",
        help="Padding added around speech segments in milliseconds (default: 400)",
    )
    p.add_argument("--no-batch", action="store_true",
                    help="Disable batched inference (use standard WhisperModel)")
    p.add_argument(
        "--hallucination-silence-threshold", type=float, default=None, metavar="SEC",
        help="Skip silent sections where model hallucinates (e.g. 1.0 sec)",
    )
    p.add_argument(
        "--no-condition-on-previous-text", action="store_true",
        help="Don't condition on previous text (reduces repetition/hallucination loops; auto-enabled for distil models)",
    )
    p.add_argument(
        "--condition-on-previous-text", action="store_true",
        help="Force-enable conditioning on previous text (overrides auto-disable for distil models)",
    )
    p.add_argument(
        "--compression-ratio-threshold", type=float, default=None, metavar="RATIO",
        help="Filter segments above this compression ratio (default: 2.4)",
    )
    p.add_argument(
        "--log-prob-threshold", type=float, default=None, metavar="PROB",
        help="Filter segments below this avg log probability (default: -1.0)",
    )
    p.add_argument(
        "--max-new-tokens", type=int, default=None, metavar="N",
        help="Maximum tokens per segment (prevents runaway generation)",
    )
    p.add_argument(
        "--clip-timestamps", default=None, metavar="RANGE",
        help="Transcribe specific time ranges: '30,60' or '0,30;60,90' (seconds)",
    )
    p.add_argument(
        "--progress", action="store_true",
        help="Show transcription progress bar",
    )
    p.add_argument(
        "--best-of", type=int, default=None, metavar="N",
        help="Number of candidates when sampling with non-zero temperature (default: 5)",
    )
    p.add_argument(
        "--patience", type=float, default=None, metavar="F",
        help="Beam search patience factor; higher allows more beam candidates (default: 1.0)",
    )
    p.add_argument(
        "--repetition-penalty", type=float, default=None, metavar="F",
        help="Penalty applied to previously generated tokens to reduce repetition (default: 1.0)",
    )
    p.add_argument(
        "--no-repeat-ngram-size", type=int, default=None, metavar="N",
        help="Prevent repetition of n-grams of this size (default: 0 = disabled)",
    )

    # --- Advanced inference tuning ---
    p.add_argument(
        "--no-timestamps", action="store_true",
        help="Output text segments without timing information (faster; "
             "incompatible with --word-timestamps, --format srt/vtt/tsv, --diarize)",
    )
    p.add_argument(
        "--chunk-length", type=int, default=None, metavar="N",
        help="Audio chunk length in seconds for batched inference (default: auto); "
             "ignored with --no-batch",
    )
    p.add_argument(
        "--language-detection-threshold", type=float, default=None, metavar="T",
        help="Confidence threshold for automatic language detection (default: 0.5)",
    )
    p.add_argument(
        "--language-detection-segments", type=int, default=None, metavar="N",
        help="Number of audio segments to sample for language detection "
             "(default: 1; increase for more accurate detection)",
    )
    p.add_argument(
        "--length-penalty", type=float, default=None, metavar="F",
        help="Length penalty for beam search; >1 favors longer outputs, <1 favors shorter "
             "(default: 1.0)",
    )
    p.add_argument(
        "--prompt-reset-on-temperature", type=float, default=None, metavar="T",
        help="Reset initial prompt when temperature fallback reaches this threshold (default: 0.5)",
    )
    p.add_argument(
        "--no-suppress-blank", action="store_true",
        help="Disable blank token suppression (may improve transcription of soft speech)",
    )
    p.add_argument(
        "--suppress-tokens", default=None, metavar="IDS",
        help="Comma-separated token IDs to suppress in addition to the default -1 "
             "(e.g. '1234,5678')",
    )
    p.add_argument(
        "--max-initial-timestamp", type=float, default=None, metavar="T",
        help="Maximum timestamp allowed for the first transcribed segment in seconds "
             "(default: 1.0)",
    )
    p.add_argument(
        "--prepend-punctuations", default=None, metavar="CHARS",
        help="Punctuation characters to merge into the preceding word "
             "(default: \"'¿([{-\")",
    )
    p.add_argument(
        "--append-punctuations", default=None, metavar="CHARS",
        help="Punctuation characters to merge into the following word "
             "(default: \"'.。,，!！?？:：\")]}\、\")",
    )

    # --- Advanced features ---
    p.add_argument(
        "--diarize", action="store_true",
        help="Speaker diarization (requires pyannote.audio; install via setup.sh --diarize)",
    )
    p.add_argument(
        "--min-speakers", type=int, default=None, metavar="N",
        help="Minimum number of speakers hint for diarization",
    )
    p.add_argument(
        "--max-speakers", type=int, default=None, metavar="N",
        help="Maximum number of speakers hint for diarization",
    )
    p.add_argument(
        "--min-confidence", type=float, default=None, metavar="PROB",
        help="Drop segments below this avg word confidence (0.0–1.0)",
    )
    p.add_argument(
        "--skip-existing", action="store_true",
        help="Skip files whose output already exists (batch mode)",
    )
    p.add_argument(
        "--detect-language-only", action="store_true",
        help="Detect the language of the audio and exit (no transcription). "
             "Output: 'Language: en (probability: 0.984)'. With --format json: JSON object.",
    )
    p.add_argument(
        "--stats-file", default=None, metavar="PATH",
        help="Write performance stats JSON sidecar after transcription. "
             "If a directory: writes {stem}.stats.json in that dir. "
             "In batch mode, one stats file per input.",
    )
    p.add_argument(
        "--burn-in", default=None, metavar="OUTPUT",
        help="Burn subtitles into the original video: transcribe, then ffmpeg-overlay SRT "
             "into the input file and save to OUTPUT (single-file mode only; requires ffmpeg)",
    )
    p.add_argument(
        "--speaker-names", default=None, metavar="NAMES",
        help="Comma-separated speaker names to replace SPEAKER_1, SPEAKER_2, etc. "
             "(e.g. 'Alice,Bob'). Requires --diarize",
    )
    p.add_argument(
        "--filter-hallucinations", action="store_true",
        help="Filter common Whisper hallucinations: music/applause markers, "
             "'Thank you for watching', duplicate consecutive segments, etc.",
    )
    p.add_argument(
        "--keep-temp", action="store_true",
        help="Keep temp files from URL downloads instead of deleting them "
             "(useful for re-processing downloaded audio without re-downloading)",
    )
    p.add_argument(
        "--parallel", type=int, default=None, metavar="N",
        help="Number of parallel workers for batch processing "
             "(default: sequential; mainly useful on CPU with many small files)",
    )

    # --- Preprocessing ---
    p.add_argument(
        "--normalize", action="store_true",
        help="Normalize audio volume before transcription (EBU R128 loudnorm)",
    )
    p.add_argument(
        "--denoise", action="store_true",
        help="Apply noise reduction before transcription (high-pass + FFT denoise)",
    )

    # --- Device ---
    p.add_argument(
        "--device", default="auto", choices=["auto", "cpu", "cuda"],
        help="Compute device (default: auto)",
    )
    p.add_argument(
        "--compute-type", default="auto",
        choices=["auto", "int8", "int8_float16", "float16", "float32"],
        help="Quantization (default: auto; int8_float16 = hybrid for GPU)",
    )
    p.add_argument(
        "--threads", type=int, default=None, metavar="N",
        help="Number of CPU threads for CTranslate2 inference (default: auto)",
    )
    p.add_argument(
        "-q", "--quiet", action="store_true",
        help="Suppress progress messages",
    )
    p.add_argument(
        "--log-level", default="warning",
        choices=["debug", "info", "warning", "error"],
        help="Set faster_whisper library logging level (default: warning)",
    )

    # --- Utility ---
    p.add_argument(
        "--version", action="store_true",
        help="Show installed faster-whisper version and exit",
    )
    p.add_argument(
        "--update", action="store_true",
        help="Upgrade faster-whisper in the skill venv and exit",
    )

    # --- RSS / Podcast ---
    p.add_argument(
        "--rss", default=None, metavar="URL",
        help="Podcast RSS feed URL — extracts audio enclosures and transcribes them. "
             "AUDIO positional is optional when --rss is used.",
    )
    p.add_argument(
        "--rss-latest", type=int, default=5, metavar="N",
        help="Number of most-recent episodes to process from --rss feed "
             "(default: 5; use 0 for all episodes)",
    )

    # --- Reliability ---
    p.add_argument(
        "--retries", type=int, default=0, metavar="N",
        help="Retry failed files up to N times with exponential backoff "
             "(default: 0 = no retry; incompatible with --parallel)",
    )

    # --- Transcript search ---
    p.add_argument(
        "--search", default=None, metavar="TERM",
        help="Search the transcript for TERM and print matching segments with timestamps. "
             "Replaces the normal transcript output (use with -o to save search results to file).",
    )
    p.add_argument(
        "--search-fuzzy", action="store_true",
        help="Use fuzzy/approximate matching with --search (useful for typos or partial words)",
    )

    # --- Chapter detection ---
    p.add_argument(
        "--detect-chapters", action="store_true",
        help="Detect chapter/section breaks from silence gaps between segments and print chapter markers.",
    )
    p.add_argument(
        "--chapter-gap", type=float, default=8.0, metavar="SEC",
        help="Minimum silence gap in seconds to start a new chapter (default: 8.0)",
    )
    p.add_argument(
        "--chapters-file", default=None, metavar="PATH",
        help="Write chapter markers to this file (default: print to stdout alongside transcript). "
             "Format is controlled by --chapter-format.",
    )
    p.add_argument(
        "--chapter-format", default="youtube",
        choices=["youtube", "text", "json"],
        help="Chapter output format: youtube (M:SS Title), text (Title: HH:MM:SS), json (default: youtube)",
    )

    # --- Speaker audio export ---
    p.add_argument(
        "--export-speakers", default=None, metavar="DIR",
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
            sys.exit(1)

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
    if is_distil and not args.no_condition_on_previous_text and not args.condition_on_previous_text:
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
            print("⚠️  --stream disables word-level alignment (needs all segments)", file=sys.stderr)

    # Conflict check: --chunk-length requires batched mode
    if args.chunk_length is not None and args.no_batch:
        print("⚠️  --chunk-length ignored with --no-batch (only valid for batched inference)", file=sys.stderr)
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
            print("Error: stdin '-' cannot be combined with other inputs in batch mode", file=sys.stderr)
            sys.exit(1)
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
        sys.exit(1)

    is_batch = len(audio_files) > 1

    # ---- Device setup ----
    device = args.device
    compute_type = args.compute_type
    cuda_ok, gpu_name = check_cuda_available()

    if device == "auto":
        device = "cuda" if cuda_ok else "cpu"
        if device == "cpu" and not args.quiet:
            print("⚠️  CUDA not available — using CPU (this will be slow!)", file=sys.stderr)
            print("   To enable GPU: pip install torch --index-url https://download.pytorch.org/whl/cu121", file=sys.stderr)

    if compute_type == "auto":
        compute_type = "float16" if device == "cuda" else "int8"

    if cuda_ok and compute_type == "float16" and args.compute_type == "auto" and not args.quiet:
        import re as _re
        gpu_name = gpu_name or ""
        if _re.search(r"RTX 30[0-9]{2}", gpu_name, _re.IGNORECASE):
            print(f"💡 Tip: For {gpu_name}, --compute-type int8_float16 saves ~1GB VRAM with minimal quality loss", file=sys.stderr)

    use_batched = not args.no_batch

    if not args.quiet:
        mode = f"batched (bs={args.batch_size})" if use_batched else "standard"
        gpu_str = f" on {gpu_name}" if device == "cuda" and gpu_name else ""
        task_str = " [translate→en]" if args.translate else ""
        stream_str = " [streaming]" if args.stream else ""
        print(f"🎙️  {args.model} ({device}/{compute_type}){gpu_str} [{mode}]{task_str}{stream_str}", file=sys.stderr)
        if is_batch:
            print(f"📁 {len(audio_files)} files queued", file=sys.stderr)

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
        print(f"Error loading model: {e}", file=sys.stderr)
        sys.exit(1)

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
                    import numpy as np
                    import subprocess as _sp
                    cmd = ["ffmpeg", "-i", path, "-ar", str(sampling_rate), "-ac", "1",
                           "-f", "f32le", "-"]
                    result = _sp.run(cmd, capture_output=True, check=True)
                    return np.frombuffer(result.stdout, dtype=np.float32)

        exit_code = 0
        for audio_path in audio_files:
            try:
                audio_np = decode_audio(audio_path)
                lang, lang_prob, _ = model.detect_language(audio=audio_np)
                prob_val = float(lang_prob)
                if args.format == "json":
                    print(json.dumps({"language": lang, "language_probability": round(prob_val, 4)}, ensure_ascii=False))
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

    # ---- Transcribe ----
    results = []
    failed_files = []
    total_audio = 0
    wall_start = time.time()

    _skip_count = [0]  # mutable counter for batch summary

    def _should_skip(audio_path):
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
                f"⚠️  --parallel on GPU: each call uses the full GPU; "
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
                executor.submit(transcribe_file, af, pipe, _make_args(af)): af
                for af in pending
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
                if not is_batch:
                    sys.exit(1)

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
        print("Error: No files transcribed", file=sys.stderr)
        sys.exit(1)

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
                    audio_src, r.get("segments", []),
                    args.export_speakers, quiet=args.quiet,
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
                    r, fmt,
                    max_words_per_line=args.max_words_per_line,
                    max_chars_per_line=getattr(args, "max_chars_per_line", None),
                )

                if args.output:
                    out_path = Path(args.output)
                    # Treat as directory when: it's already a dir, OR batch mode, OR multiple formats requested
                    multi_fmt = len(formats) > 1
                    if out_path.is_dir() or (is_batch and not out_path.suffix) or (multi_fmt and not out_path.suffix):
                        out_path.mkdir(parents=True, exist_ok=True)
                        # Apply output template if provided
                        if args.output_template:
                            filename = args.output_template.format(
                                stem=stem, lang=lang, ext=ext, model=model_name,
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
                    print("⚠️  --burn-in is only supported for single-file mode; skipping", file=sys.stderr)
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
