"""
Shared post-processing functions for super-transcribe backends.
Includes: search, chapters, filler removal, paragraph detection,
sentence merging, hallucination filtering.
"""

from __future__ import annotations

import difflib
import json
import re
from typing import Any

# AIDEV-NOTE: Segment is an untyped dict throughout; mirrors formatters.Segment.
Segment = dict[str, Any]


# ---------------------------------------------------------------------------
# Terminal punctuation pattern (used by merge_sentences and detect_paragraphs)
# ---------------------------------------------------------------------------

_TERMINAL_PUNCT = re.compile(r'[.!?…。！？]["\')\]]*\s*$')


# ---------------------------------------------------------------------------
# Hallucination filter
# ---------------------------------------------------------------------------

HALLUCINATION_PATTERNS = [
    re.compile(
        r"^\s*\[?\s*(music|applause|laughter|silence|inaudible|background noise)\s*\]?\s*$",
        re.I,
    ),
    re.compile(
        r"^\s*\(?\s*(music|applause|laughter|upbeat music|dramatic music"
        r"|suspenseful music|tense music|gentle music)\s*\)?\s*$",
        re.I,
    ),
    re.compile(r"thank\s+you\s+for\s+watching", re.I),
    re.compile(r"thank\s+you\s+for\s+(listening|your\s+attention)", re.I),
    re.compile(r"subtitles?\s+by", re.I),
    re.compile(r"(transcribed|captioned)\s+by", re.I),
    re.compile(r"^\s*www\.\S+\s*$", re.I),
    re.compile(r"^\s*[.!?,;:\u2026]+\s*$"),
    re.compile(r"^\s*$"),
]


def filter_hallucinations(segments: list[Segment]) -> list[Segment]:
    """Remove segments matching common hallucination patterns."""
    filtered = []
    prev_text = None
    for seg in segments:
        text = seg.get("text", "").strip()
        if any(p.search(text) for p in HALLUCINATION_PATTERNS):
            continue
        if text == prev_text:
            continue
        prev_text = text
        filtered.append(seg)
    return filtered


# ---------------------------------------------------------------------------
# Filler word removal
# ---------------------------------------------------------------------------

_FILLER_PATTERNS = [
    re.compile(r"\b(um+|uh+|er+|ah+|hmm+|hm+)\b", re.I),
    re.compile(r"\byou know\b", re.I),
    re.compile(r"\bI mean\b", re.I),
    re.compile(r"\byou see\b", re.I),
]

_FILLER_WORD_RE = re.compile(r"^(um+|uh+|er+|ah+|hmm+|hm+)$", re.I)
_FILLER_BIGRAMS = [("you", "know"), ("i", "mean"), ("you", "see")]


def _word_bare(w: Segment) -> str:
    """Return the bare lowercased text of a word token."""
    return re.sub(r"[^\w']", "", w["word"].lower().strip())


def _filter_word_list(words: list[Segment]) -> list[Segment]:
    """Remove filler words from a word list."""
    if not words:
        return words

    remove_idx = set()

    for i, w in enumerate(words):
        if _FILLER_WORD_RE.match(_word_bare(w)):
            remove_idx.add(i)

    for i in range(len(words) - 1):
        if i in remove_idx or i + 1 in remove_idx:
            continue
        pair = (_word_bare(words[i]), _word_bare(words[i + 1]))
        if pair in _FILLER_BIGRAMS:
            remove_idx.add(i)
            remove_idx.add(i + 1)

    return [w for idx, w in enumerate(words) if idx not in remove_idx]


def remove_filler_words(segments: list[Segment]) -> list[Segment]:
    """Strip hesitation fillers and discourse markers from segments."""
    cleaned = []
    for seg in segments:
        text = seg["text"]
        for pat in _FILLER_PATTERNS:
            text = pat.sub("", text)
        text = re.sub(r"^[\s,.!?;:]+", "", text)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([,.!?;:])\1+", r"\1", text)
        text = re.sub(r",([.!?])", r"\1", text)
        text = re.sub(r"  +", " ", text)
        text = text.strip()
        if not text:
            continue
        seg = dict(seg)
        seg["text"] = text
        if seg.get("words"):
            seg["words"] = _filter_word_list(seg["words"])
        cleaned.append(seg)
    return cleaned


# ---------------------------------------------------------------------------
# Paragraph detection
# ---------------------------------------------------------------------------


def detect_paragraphs(
    segments: list[Segment], min_gap: float = 3.0, sentence_gap: float = 1.5
) -> list[Segment]:
    """Mark segments with 'paragraph_start': True at paragraph boundaries."""
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
# Sentence merging
# ---------------------------------------------------------------------------


def merge_sentences(segments: list[Segment]) -> list[Segment]:
    """Merge consecutive short segments into sentence-boundary-aware chunks."""
    MAX_GAP = 2.0

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


def detect_chapters(segments: list[Segment], min_gap: float = 8.0) -> list[dict[str, Any]]:
    """Detect chapter breaks from silence gaps between segments."""
    if not segments:
        return []

    chapters = [{"chapter": 1, "start": segments[0]["start"], "title": "Chapter 1"}]
    chapter_num = 1

    for i in range(1, len(segments)):
        gap = segments[i]["start"] - segments[i - 1]["end"]
        if gap >= min_gap:
            chapter_num += 1
            chapters.append(
                {
                    "chapter": chapter_num,
                    "start": segments[i]["start"],
                    "title": f"Chapter {chapter_num}",
                }
            )

    return chapters


def _fmt_chapter_ts(seconds: float) -> str:
    """Format chapter timestamp: M:SS or H:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def format_chapters_output(chapters: list[dict[str, Any]], fmt: str = "youtube") -> str:
    """Render chapter list."""
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

    return "\n".join(f"{_fmt_chapter_ts(ch['start'])} {ch['title']}" for ch in chapters)


# ---------------------------------------------------------------------------
# Transcript search
# ---------------------------------------------------------------------------


def search_transcript(
    segments: list[Segment], query: str, fuzzy: bool = False
) -> list[dict[str, Any]]:
    """Search transcript segments for *query*."""
    query_lower = query.lower()
    matches = []

    for seg in segments:
        text = seg["text"].strip()
        text_lower = text.lower()

        matched = query_lower in text_lower

        if not matched and fuzzy:
            words_in_seg = re.findall(r"[\w']+", text_lower)
            for word in words_in_seg:
                ratio = difflib.SequenceMatcher(None, query_lower, word).ratio()
                if ratio >= 0.6:
                    matched = True
                    break
            if not matched and " " in query_lower:
                ratio = difflib.SequenceMatcher(None, query_lower, text_lower).ratio()
                if ratio >= 0.6:
                    matched = True

        if matched:
            matches.append(
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": text,
                    "speaker": seg.get("speaker"),
                }
            )

    return matches


def format_search_results(matches: list[dict[str, Any]], query: str) -> str:
    """Format search results for display."""
    if not matches:
        return f'No matches found for: "{query}"'

    lines = [f'🔍 {len(matches)} match(es) for "{query}":']
    for m in matches:
        ts = _fmt_chapter_ts(m["start"])
        speaker = f"[{m['speaker']}] " if m.get("speaker") else ""
        lines.append(f"  [{ts}]  {speaker}{m['text']}")

    return "\n".join(lines)
