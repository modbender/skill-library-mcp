#!/usr/bin/env python3
"""Render a LinkedIn-ready post from episode metadata/body.

Input can be:
- --json-file with fields: title, body (or script), substack_url, apple_podcasts_link
- stdin JSON with same fields.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def first_sentence(text: str, fallback: str) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return fallback
    m = re.split(r"(?<=[.!?])\s+", clean)
    return (m[0] if m else clean)[:240].strip()


def key_points(text: str, limit: int = 3) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    points: list[str] = []
    for s in sentences:
        s = s.strip(" -•\t")
        if len(s) < 40:
            continue
        if not re.search(r"\d", s):
            continue
        points.append(s[:180].rstrip(" .") + ".")
        if len(points) >= limit:
            break
    if not points:
        points = [first_sentence(text, "New episode is live.")]
    return points


def hashtags(title: str) -> str:
    base = ["#RealEstate", "#CanadaHousing", "#CREI", "#Investing", "#Multifamily"]
    low = title.lower()
    if "rent" in low:
        base.append("#RentalMarket")
    if "vacanc" in low:
        base.append("#Vacancy")
    return " ".join(base[:6])


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json-file")
    args = p.parse_args()

    if args.json_file:
        data = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    else:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}

    title = str(data.get("title") or "New Podcast Episode").strip()
    body = str(data.get("body") or data.get("script") or "").strip()
    substack_url = str(data.get("substack_url") or "").strip()
    apple = str(data.get("apple_podcasts_link") or "").strip()

    hook = first_sentence(body, f"{title} is now live.")
    points = key_points(body, 3)

    lines: list[str] = []
    lines.append(f"🎙️ {title}")
    lines.append("")
    lines.append(hook)
    lines.append("")
    lines.append("What stood out:")
    for pt in points:
        lines.append(f"• {pt}")
    lines.append("")
    if substack_url:
        lines.append(f"Full breakdown on Substack: {substack_url}")
    if apple:
        lines.append(f"Listen on Apple Podcasts: {apple}")
    lines.append("")
    lines.append("What are you seeing in your market right now?")
    lines.append(hashtags(title))

    print("\n".join(lines).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
