#!/usr/bin/env python3
"""Locate local OpenClaw docs directories for offline fallback search."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path



def derive_from_openclaw_bin() -> list[Path]:
    out: list[Path] = []
    binary = shutil.which("openclaw")
    if not binary:
        return out
    resolved = Path(binary).resolve()

    for parent in resolved.parents:
        if parent.name == "openclaw" and parent.parent.name == "node_modules":
            candidate = parent / "docs"
            out.append(candidate)
            break
    return out


def collect_candidates() -> list[Path]:
    home = Path.home()
    defaults = [
        home / "runtime" / "clawd-live" / "docs",
        home / ".openclaw" / "lib" / "node_modules" / "openclaw" / "docs",
        Path("/usr/local/lib/node_modules/openclaw/docs"),
        Path("/opt/homebrew/lib/node_modules/openclaw/docs"),
    ]

    ordered = derive_from_openclaw_bin() + defaults

    seen: set[str] = set()
    unique: list[Path] = []
    for p in ordered:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Find local OpenClaw docs directories")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    candidates = collect_candidates()
    existing = [p for p in candidates if p.exists() and p.is_dir()]

    if args.json:
        payload = {
            "existing": [str(p) for p in existing],
            "checked": [str(p) for p in candidates],
        }
        print(json.dumps(payload, indent=2))
        return 0

    if not existing:
        print("No local OpenClaw docs directories found.")
        print("Checked:")
        for p in candidates:
            print(f"- {p}")
        return 1

    print("Local OpenClaw docs roots:")
    for p in existing:
        print(f"- {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
