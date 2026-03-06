#!/usr/bin/env python3
"""
Reformat aligned word-level JSON to match manually formatted lyrics lines.
Maps word timestamps from stable-ts output onto user-defined subtitle lines.
(The "v18 workflow" — proven best method for subtitle timing.)
"""

import json
import re
import argparse
import os
import sys


def normalize(text: str) -> str:
    """Remove whitespace for character-level comparison."""
    return re.sub(r'\s+', '', text).lower()


def reformat(aligned_path: str, formatted_path: str, output_path: str):
    # Load aligned word data
    with open(aligned_path) as f:
        data = json.load(f)

    all_words = []
    for seg in data.get("segments", []):
        words = seg.get("words", [])
        if words:
            all_words.extend(words)
        else:
            all_words.append({
                "word": seg.get("text", ""),
                "start": seg.get("start", 0),
                "end": seg.get("end", 0)
            })

    print(f"📖 Loaded {len(all_words)} words from aligned JSON")

    # Load formatted lyrics
    with open(formatted_path) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    print(f"📝 Loaded {len(lines)} formatted lines")

    # Match words to lines
    new_segments = []
    word_idx = 0
    total_words = len(all_words)

    for line_text in lines:
        if word_idx >= total_words:
            break

        chunk_words = []
        line_chars = normalize(line_text)
        collected = ""

        while word_idx < total_words:
            w = all_words[word_idx]
            chunk_words.append(w)
            collected += normalize(w.get("word", ""))
            word_idx += 1

            if len(collected) >= len(line_chars):
                break

        if not chunk_words:
            continue

        new_segments.append({
            "start": chunk_words[0]["start"],
            "end": chunk_words[-1]["end"],
            "text": line_text,
            "words": chunk_words
        })

    # Fill small gaps (< 1.0s) to prevent subtitle flickering
    for i in range(len(new_segments) - 1):
        gap = new_segments[i + 1]["start"] - new_segments[i]["end"]
        if 0 < gap < 1.0:
            new_segments[i]["end"] = new_segments[i + 1]["start"]

    output = {
        "text": "\n".join(lines),
        "segments": new_segments
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(new_segments)} segments to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Map word timestamps to formatted lyrics lines")
    parser.add_argument("--aligned", required=True, help="stable-ts aligned JSON")
    parser.add_argument("--formatted", required=True, help="Formatted lyrics text (1 line = 1 subtitle)")
    parser.add_argument("--output", required=True, help="Output JSON for Remotion")
    args = parser.parse_args()

    for path in [args.aligned, args.formatted]:
        if not os.path.exists(path):
            print(f"❌ File not found: {path}")
            sys.exit(1)

    reformat(args.aligned, args.formatted, args.output)
