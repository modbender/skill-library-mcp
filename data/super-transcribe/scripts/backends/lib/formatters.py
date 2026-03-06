"""
Shared output formatters for super-transcribe backends.
Supports: text, JSON, SRT, VTT, ASS, LRC, TTML, CSV, TSV, HTML.
"""

from __future__ import annotations

import csv
import html as _html
import io
import json
import math
from typing import Any

# AIDEV-NOTE: Segment is an untyped dict throughout; backends produce varying shapes.
Segment = dict[str, Any]


# ---------------------------------------------------------------------------
# Timestamp helpers
# ---------------------------------------------------------------------------


def format_ts_srt(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_ts_vtt(seconds: float) -> str:
    """Format seconds as VTT timestamp: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_ts_ass(seconds: float) -> str:
    """Format seconds as ASS/SSA timestamp: H:MM:SS.cc (centiseconds)"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def format_ts_ttml(seconds: float) -> str:
    """Format seconds as TTML timestamp: HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_duration(seconds: float) -> str:
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


# ---------------------------------------------------------------------------
# Character-based subtitle line splitting
# ---------------------------------------------------------------------------


def split_words_by_chars(words: list[Segment], max_chars: int) -> list[list[Segment]]:
    """Split a list of word dicts into chunks where each chunk's joined text
    fits within max_chars characters."""
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
# SRT
# ---------------------------------------------------------------------------


def to_srt(
    segments: list[Segment],
    max_words_per_line: int | None = None,
    max_chars_per_line: int | None = None,
) -> str:
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
                lines.append(
                    f"{format_ts_srt(chunk[0]['start'])} --> {format_ts_srt(chunk[-1]['end'])}"
                )
                lines.append(chunk_text)
                lines.append("")
                cue_num += 1
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i : i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(str(cue_num))
                lines.append(
                    f"{format_ts_srt(chunk[0]['start'])} --> {format_ts_srt(chunk[-1]['end'])}"
                )
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


# ---------------------------------------------------------------------------
# VTT
# ---------------------------------------------------------------------------


def to_vtt(
    segments: list[Segment],
    max_words_per_line: int | None = None,
    max_chars_per_line: int | None = None,
) -> str:
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
                lines.append(
                    f"{format_ts_vtt(chunk[0]['start'])} --> {format_ts_vtt(chunk[-1]['end'])}"
                )
                lines.append(chunk_text)
                lines.append("")
                cue_num += 1
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i : i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                lines.append(str(cue_num))
                lines.append(
                    f"{format_ts_vtt(chunk[0]['start'])} --> {format_ts_vtt(chunk[-1]['end'])}"
                )
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


# ---------------------------------------------------------------------------
# Plain text
# ---------------------------------------------------------------------------


def to_text(segments: list[Segment]) -> str:
    """Format segments as plain text, with speaker labels if present."""
    has_speakers = any(seg.get("speaker") for seg in segments)
    has_paragraphs = any(seg.get("paragraph_start") for seg in segments)

    if not has_speakers:
        if not has_paragraphs:
            return " ".join(seg["text"].strip() for seg in segments if seg["text"].strip())
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
            lines.append(f"\n[{sp}] ")
        elif lines and not lines[-1].endswith(("\n", " ")):
            lines.append(" ")
        lines.append(seg["text"].strip())
    return "".join(lines).strip()


# ---------------------------------------------------------------------------
# TSV
# ---------------------------------------------------------------------------


def to_tsv(segments: list[Segment]) -> str:
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


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------


def to_csv(segments: list[Segment]) -> str:
    """Format segments as CSV with header: start_s, end_s, text [, speaker]."""
    has_speakers = any(seg.get("speaker") for seg in segments)
    fieldnames = ["start_s", "end_s", "text"] + (["speaker"] if has_speakers else [])
    buf = io.StringIO()
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


# ---------------------------------------------------------------------------
# ASS/SSA
# ---------------------------------------------------------------------------


def to_ass(
    segments: list[Segment],
    max_words_per_line: int | None = None,
    max_chars_per_line: int | None = None,
) -> str:
    """Format segments as ASS/SSA (Advanced SubStation Alpha) subtitle content."""
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
                chunk = words[i : i + max_words_per_line]
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


# ---------------------------------------------------------------------------
# LRC
# ---------------------------------------------------------------------------


def to_lrc(segments: list[Segment]) -> str:
    """Format segments as LRC (timed lyrics) format."""
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
# TTML
# ---------------------------------------------------------------------------


def to_ttml(
    segments: list[Segment],
    language: str = "en",
    max_words_per_line: int | None = None,
    max_chars_per_line: int | None = None,
) -> str:
    """Format segments as TTML (Timed Text Markup Language / DFXP) subtitles."""
    lang_attr = (language or "en").replace("_", "-")

    def xml_escape(text):
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<tt xml:lang="{lang_attr}"',
        '    xmlns="http://www.w3.org/ns/ttml"',
        '    xmlns:tts="http://www.w3.org/ns/ttml#styling"',
        '    xmlns:ttm="http://www.w3.org/ns/ttml#metadata">',
        "  <head>",
        "    <metadata>",
        "      <ttm:title>Transcript</ttm:title>",
        "    </metadata>",
        "    <styling>",
        '      <style xml:id="s1"',
        '             tts:fontFamily="Arial, Helvetica, sans-serif"',
        '             tts:fontSize="100%"',
        '             tts:fontWeight="normal"',
        '             tts:color="white"',
        '             tts:textAlign="center"',
        '             tts:backgroundColor="transparent"/>',
        "    </styling>",
        "    <layout>",
        '      <region xml:id="r1"',
        '              tts:origin="10% 85%"',
        '              tts:extent="80% 10%"',
        '              tts:displayAlign="before"/>',
        "    </layout>",
        "  </head>",
        "  <body>",
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
                    f'      <p begin="{begin}" end="{end}"'
                    f' style="s1">{xml_escape(chunk_text)}</p>'
                )
        elif max_words_per_line and seg.get("words"):
            words = seg["words"]
            for i in range(0, len(words), max_words_per_line):
                chunk = words[i : i + max_words_per_line]
                chunk_text = "".join(w["word"] for w in chunk).strip()
                if seg.get("speaker"):
                    chunk_text = f"[{seg['speaker']}] {chunk_text}"
                begin = format_ts_ttml(chunk[0]["start"])
                end = format_ts_ttml(chunk[-1]["end"])
                lines.append(
                    f'      <p begin="{begin}" end="{end}"'
                    f' style="s1">{xml_escape(chunk_text)}</p>'
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

    lines.extend(
        [
            "    </div>",
            "  </body>",
            "</tt>",
        ]
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------


def to_html(result: dict[str, Any]) -> str:
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
                # AIDEV-NOTE: html.escape required — word text may contain angle brackets (XSS)
                word_parts.append(
                    f'<span class="{cls}" title="{p:.2f}">{_html.escape(w["word"])}</span>'
                )
            text_html = "".join(word_parts)
        else:
            text_html = _html.escape(seg.get("text", "").strip())

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
            max-width: 820px; margin: 2em auto; padding: 0 1em;
            color: #222; line-height: 1.6; }}
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
# JSON
# ---------------------------------------------------------------------------


def to_json(result: dict[str, Any]) -> str:
    """Format result as JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Agent compact JSON (for chatbot/agent integration)
# ---------------------------------------------------------------------------


def _extract_summary_hint(segments: list[Segment]) -> dict[str, str] | None:
    """Extract first and last meaningful sentences for agent preview.

    Returns {"first": "...", "last": "..."} or None if transcript is too short.
    """
    if not segments:
        return None

    # Collect all non-empty segment texts
    texts = [s["text"].strip() for s in segments if s.get("text", "").strip()]
    if len(texts) < 2:
        return None

    first = texts[0]
    last = texts[-1]

    # Only include if transcript is long enough to warrant a hint
    total_chars = sum(len(t) for t in texts)
    if total_chars < 400:
        return None

    # Truncate individual hints if very long
    if len(first) > 200:
        first = first[:197] + "..."
    if len(last) > 200:
        last = last[:197] + "..."

    return {"first": first, "last": last}


def _compute_avg_confidence(segments: list[Segment]) -> float | None:
    """Compute average word confidence across all segments.

    Returns float 0.0-1.0 or None if no confidence data available.
    """
    confidences = []
    for seg in segments:
        # Check segment-level confidence
        if "avg_logprob" in seg:
            # Convert log probability to rough confidence (0-1)
            confidences.append(math.exp(seg["avg_logprob"]))
        # Check word-level confidence
        for word in seg.get("words", []):
            if "probability" in word:
                confidences.append(word["probability"])
            elif "confidence" in word:
                confidences.append(word["confidence"])
    if not confidences:
        return None
    return round(sum(confidences) / len(confidences), 4)


def format_agent_json(result: dict[str, Any], backend_name: str) -> str:
    """Format a result as compact single-line JSON for agent consumption.

    Returns fields an agent needs to reply to a user:
    text, duration, language, processing stats, speaker info,
    confidence, file paths, and summary hint for long transcripts.
    """
    segments = result.get("segments", [])

    agent_data = {
        "text": result.get("text", ""),
        "duration": round(result.get("duration", 0), 2),
        "language": result.get("language"),
        "language_probability": round(result.get("language_probability", 0), 4),
        "processing_time": result.get("stats", {}).get("processing_time", 0),
        "backend": backend_name,
        "segments": len(segments),
        "speakers": result.get("speakers"),
        "word_count": sum(len(s["text"].split()) for s in segments),
    }

    # Feature 6: avg_confidence
    avg_conf = _compute_avg_confidence(segments)
    if avg_conf is not None:
        agent_data["avg_confidence"] = avg_conf

    # Feature 6: file_path and output_path (echo back for multi-file tracking)
    if result.get("file_path"):
        agent_data["file_path"] = result["file_path"]
    if result.get("output_path"):
        agent_data["output_path"] = result["output_path"]

    # Feature 8: summary_hint for long transcripts
    hint = _extract_summary_hint(segments)
    if hint:
        agent_data["summary_hint"] = hint

    return json.dumps(agent_data, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Unified format_result
# ---------------------------------------------------------------------------

EXT_MAP = {
    "text": ".txt",
    "json": ".json",
    "srt": ".srt",
    "vtt": ".vtt",
    "tsv": ".tsv",
    "csv": ".csv",
    "lrc": ".lrc",
    "html": ".html",
    "ass": ".ass",
    "ttml": ".ttml",
}

VALID_FORMATS = {"text", "json", "srt", "vtt", "tsv", "csv", "lrc", "html", "ass", "ttml"}


def format_result(
    result: dict[str, Any],
    fmt: str,
    max_words_per_line: int | None = None,
    max_chars_per_line: int | None = None,
) -> str:
    """Render a result dict in the requested format."""
    if fmt == "json":
        return to_json(result)
    if fmt == "srt":
        return to_srt(
            result["segments"],
            max_words_per_line=max_words_per_line,
            max_chars_per_line=max_chars_per_line,
        )
    if fmt == "vtt":
        return to_vtt(
            result["segments"],
            max_words_per_line=max_words_per_line,
            max_chars_per_line=max_chars_per_line,
        )
    if fmt == "tsv":
        return to_tsv(result["segments"])
    if fmt == "csv":
        return to_csv(result["segments"])
    if fmt == "lrc":
        return to_lrc(result["segments"])
    if fmt == "html":
        return to_html(result)
    if fmt == "ass":
        return to_ass(
            result["segments"],
            max_words_per_line=max_words_per_line,
            max_chars_per_line=max_chars_per_line,
        )
    if fmt == "ttml":
        return to_ttml(
            result["segments"],
            language=result.get("language", "en"),
            max_words_per_line=max_words_per_line,
            max_chars_per_line=max_chars_per_line,
        )
    return to_text(result["segments"])
