#!/usr/bin/env python3
"""Create a Quartz-ready episode markdown stub in a draft directory."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True, help="Series display name (e.g., 야간조)")
    ap.add_argument("--series-dir", required=True, help="Quartz series dir (e.g., .../Drama/야간조)")
    ap.add_argument("--episode", required=True, type=int)
    ap.add_argument("--slug", required=True, help="korean slug (no spaces) used in filename")
    ap.add_argument("--draft-dir", required=True, help="draft output dir")
    args = ap.parse_args()

    series = args.series.strip()
    series_dir = Path(args.series_dir)
    draft_dir = Path(args.draft_dir)
    draft_dir.mkdir(parents=True, exist_ok=True)

    ep = args.episode
    ep2 = f"{ep:02d}"

    filename = f"{series}-{ep2}-{args.slug}.md"
    out = draft_dir / filename

    cover_name = f"{series.lower()}-novel-ep{ep2}-cover.webp"  # you can rename later

    from datetime import datetime
    today = datetime.now().date().isoformat()

    content = f"""---
title: \"{series} {ep2} — {args.slug.replace('-', ' ')}\"
date: {today}
tags:
  - domain-storytelling
  - topic-webnovel
  - format-serial
  - audience-general
  - intent-entertainment
  - lang-ko
  - series-{series.lower()}
  - episode-{ep2}
---

한 줄 요약: (여기에 1문장)

![[Drama/{series}/images/{cover_name}]]

## {ep2}

(본문)

## 다음화 예고
(1문장 훅)
"""

    out.write_text(content, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
