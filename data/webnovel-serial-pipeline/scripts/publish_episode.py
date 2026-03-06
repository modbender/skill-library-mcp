#!/usr/bin/env python3
"""Publish a reviewed draft episode into Quartz.

- Runs lint
- Verifies embedded webp assets exist (basic check)
- Copies (default) or moves the draft into the Quartz series folder with normalized naming

Safe default: copy to Quartz, keep draft.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


WIKILINK_EMBED_RE = re.compile(r"!\[\[([^\]]+\.webp)\]\]")


@dataclass
class Args:
    draft_file: Path
    quartz_root: Path
    series_dir: Path
    series: str
    episode: int
    slug: str
    move: bool


def run_lint(lint_script: Path, file: Path) -> None:
    proc = subprocess.run(["python3", str(lint_script), "--file", str(file)])
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def find_embedded_webps(md_text: str) -> list[str]:
    return [m.group(1).strip() for m in WIKILINK_EMBED_RE.finditer(md_text)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft-file", required=True)
    ap.add_argument("--quartz-root", required=True, help="e.g., /home/tw2/Documents/n8n/data/shared/syn/8.quartz")
    ap.add_argument("--series-dir", required=True, help="e.g., .../8.quartz/Drama/야간조")
    ap.add_argument("--series", required=True, help="e.g., 야간조")
    ap.add_argument("--episode", required=True, type=int)
    ap.add_argument("--slug", required=True, help="kebab-ish slug used in filename")
    ap.add_argument("--move", action="store_true", help="move draft into Quartz instead of copy")
    ns = ap.parse_args()

    args = Args(
        draft_file=Path(ns.draft_file),
        quartz_root=Path(ns.quartz_root),
        series_dir=Path(ns.series_dir),
        series=ns.series.strip(),
        episode=ns.episode,
        slug=ns.slug.strip(),
        move=bool(ns.move),
    )

    if not args.draft_file.exists():
        raise SystemExit(f"Draft not found: {args.draft_file}")

    args.quartz_root = args.quartz_root.resolve()
    args.series_dir = args.series_dir.resolve()

    lint_script = Path(__file__).with_name("lint_episode.py")
    run_lint(lint_script, args.draft_file)

    md_text = args.draft_file.read_text(encoding="utf-8", errors="ignore")
    embeds = find_embedded_webps(md_text)

    missing = []
    for rel in embeds:
        # rel is expected to be Quartz-relative path like Drama/야간조/images/xxx.webp
        asset = args.quartz_root / rel
        if not asset.exists():
            missing.append(rel)

    if missing:
        print("[ERROR] missing embedded assets:")
        for m in missing:
            print(f" - {m}")
        raise SystemExit(2)

    ep2 = f"{args.episode:02d}"
    out_name = f"{args.series}-{ep2}-{args.slug}.md"
    out_path = args.series_dir / out_name
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.move:
        shutil.move(str(args.draft_file), str(out_path))
    else:
        shutil.copy2(args.draft_file, out_path)

    print(out_path)


if __name__ == "__main__":
    main()
