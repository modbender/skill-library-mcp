#!/usr/bin/env python3
"""Skill release conductor (lightweight).

Subcommands:
- prepare: validate SKILL.md exists, basic frontmatter keys, and python syntax check on scripts/
- publish: run clawdhub publish
- draft: generate announcement drafts (MoltX + Moltbook) into a folder

This is intentionally minimal and operator-friendly.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    block = m.group(1)
    out = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"')
    return out


def cmd_prepare(skill_folder: Path) -> int:
    skill_md = skill_folder / "SKILL.md"
    if not skill_md.exists():
        print(f"Missing SKILL.md: {skill_md}")
        return 2

    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
    missing = [k for k in ("name", "description") if k not in fm]
    if missing:
        print(f"SKILL.md missing frontmatter keys: {missing}")
        return 3

    scripts_dir = skill_folder / "scripts"
    if scripts_dir.exists():
        for py in scripts_dir.rglob("*.py"):
            r = subprocess.run([sys.executable, "-m", "py_compile", str(py)], capture_output=True, text=True)
            if r.returncode != 0:
                print(f"Python syntax error in {py}\n{r.stderr}")
                return 4

    print("OK: prepare checks passed")
    return 0


def cmd_publish(skill_folder: Path, slug: str, name: str, version: str, changelog: str) -> int:
    cmd = [
        "clawdhub",
        "publish",
        str(skill_folder),
        "--slug",
        slug,
        "--name",
        name,
        "--version",
        version,
        "--changelog",
        changelog,
    ]
    print("RUN:", " ".join(cmd))
    r = subprocess.run(cmd)
    return r.returncode


def cmd_draft(slug: str, name: str, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    url = f"https://clawhub.ai/DeepSeekOracle/{slug}"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    moltx = (
        f"NEW SKILL: {name}\n\n"
        f"ClawHub: {url}\n\n"
        f"If you try it, reply with what workflow you want it to unlock next.\n"
        f"(drafted {stamp})"
    )
    moltbook = (
        f"{name} is live on ClawHub.\n\n"
        f"{url}\n\n"
        f"Tell me what you want this to do for your day-to-day agent flow, and I’ll iterate.\n"
        f"(drafted {stamp})"
    )

    (out_dir / f"{slug}_moltx.txt").write_text(moltx, encoding="utf-8")
    (out_dir / f"{slug}_moltbook.txt").write_text(moltbook, encoding="utf-8")
    print("OK: drafts written to", out_dir)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_prep = sub.add_parser("prepare")
    p_prep.add_argument("--skill-folder", required=True)

    p_pub = sub.add_parser("publish")
    p_pub.add_argument("--skill-folder", required=True)
    p_pub.add_argument("--slug", required=True)
    p_pub.add_argument("--name", required=True)
    p_pub.add_argument("--version", required=True)
    p_pub.add_argument("--changelog", required=True)

    p_draft = sub.add_parser("draft")
    p_draft.add_argument("--slug", required=True)
    p_draft.add_argument("--name", required=True)
    p_draft.add_argument("--out", required=True)

    args = ap.parse_args()

    if args.cmd == "prepare":
        return cmd_prepare(Path(args.skill_folder).resolve())
    if args.cmd == "publish":
        return cmd_publish(Path(args.skill_folder).resolve(), args.slug, args.name, args.version, args.changelog)
    if args.cmd == "draft":
        return cmd_draft(args.slug, args.name, Path(args.out).resolve())

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
