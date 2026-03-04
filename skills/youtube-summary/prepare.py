#!/usr/bin/env python3
"""
prepare.py

Extract only the `text` fields from youtube2md extract-mode JSON
and save them into a plain text file.

Usage:
  python3 prepare.py <input_json> [output_txt]

Examples:
  python3 prepare.py summaries/uJT_V5dS7zA.json
  python3 prepare.py summaries/uJT_V5dS7zA.json summaries/uJT_V5dS7zA.txt
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print("Usage: python3 prepare.py <input_json> [output_txt]", file=sys.stderr)
        return 1

    input_path = Path(sys.argv[1]).expanduser().resolve()
    if len(sys.argv) == 3:
        output_path = Path(sys.argv[2]).expanduser().resolve()
    else:
        output_path = input_path.with_suffix(".txt")

    if not input_path.exists():
        print(f"ERROR: input not found: {input_path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ERROR: failed to read JSON: {e}", file=sys.stderr)
        return 3

    segments = data.get("segments")
    if not isinstance(segments, list):
        print("ERROR: invalid format (missing list: segments)", file=sys.stderr)
        return 4

    texts: list[str] = []
    for item in segments:
        if isinstance(item, dict):
            text = item.get("text")
            if isinstance(text, str):
                cleaned = " ".join(text.split())
                if cleaned:
                    texts.append(cleaned)

    if not texts:
        print("ERROR: no text found in segments", file=sys.stderr)
        return 5

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(texts) + "\n", encoding="utf-8")

    print(f"OK: wrote {len(texts)} lines")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
