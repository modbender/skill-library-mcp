#!/usr/bin/env python3
"""Sync episode links in a series index.md between markers.

Markers required in index.md:
- <!-- episodes:start -->
- <!-- episodes:end -->

The script scans the series directory for "<series>-NN-*.md" files and writes:
- [[Drama/<series>/<file>|NN. <slug with spaces>]]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


START = "<!-- episodes:start -->"
END = "<!-- episodes:end -->"


def slug_to_title(slug: str) -> str:
    return slug.replace("-", " ")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-file", required=True)
    ap.add_argument("--series-dir", required=True)
    ap.add_argument("--series", required=True, help="folder name under Drama, e.g., 야간조")
    ns = ap.parse_args()

    index_file = Path(ns.index_file)
    series_dir = Path(ns.series_dir)
    series = ns.series

    text = index_file.read_text(encoding="utf-8", errors="ignore")
    if START not in text or END not in text:
        raise SystemExit("index.md missing markers: <!-- episodes:start --> / <!-- episodes:end -->")

    # find published episodes
    rx = re.compile(rf"^{re.escape(series)}-(\d\d)-(.+)\.md$")
    eps = []
    for p in sorted(series_dir.glob(f"{series}-??-*.md")):
        m = rx.match(p.name)
        if not m:
            continue
        num = int(m.group(1))
        slug = m.group(2)
        eps.append((num, slug, p.name))

    eps.sort(key=lambda x: x[0])

    bullets = []
    for num, slug, fname in eps:
        num2 = f"{num:02d}"
        title = slug_to_title(slug)
        bullets.append(f"- [[Drama/{series}/{fname}|{num2}. {title}]]")

    between = "\n" + "\n".join(bullets) + "\n"

    pre, rest = text.split(START, 1)
    _, post = rest.split(END, 1)

    new_text = pre + START + between + END + post
    index_file.write_text(new_text, encoding="utf-8")
    print(index_file)


if __name__ == "__main__":
    main()
