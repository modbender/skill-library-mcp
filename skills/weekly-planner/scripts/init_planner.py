#!/usr/bin/env python3
"""Initialise a fresh Weekly Planner folder in a workspace.

This script copies the template planner directory bundled with this skill into a target path.

Usage:
  python3 {baseDir}/scripts/init_planner.py --target ./planner

Safety:
  - Refuses to overwrite an existing non-empty target unless --force is provided.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import NoReturn


def die(msg: str, code: int = 1) -> NoReturn:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--target",
        default="./planner",
        help="Target directory to create (default: ./planner)",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the target directory if it already exists (DANGEROUS).",
    )
    args = ap.parse_args()

    skill_root = Path(__file__).resolve().parents[1]
    template_dir = skill_root / "assets" / "planner_template"

    if not template_dir.exists():
        die(f"Template directory not found: {template_dir}")

    target_dir = Path(args.target).expanduser().resolve()

    if target_dir.exists():
        if any(target_dir.iterdir()):
            if not args.force:
                die(
                    "Refusing to overwrite existing non-empty directory:\n"
                    f"  {target_dir}\n\n"
                    "If you really want to replace it, re-run with --force (this will delete it first)."
                )
            shutil.rmtree(target_dir)
        else:
            # copytree() requires the destination to not exist
            shutil.rmtree(target_dir)

    shutil.copytree(template_dir, target_dir)

    print(f"Initialised planner at: {target_dir}")
    print("Next steps:")
    print(f"  1) Edit {target_dir / 'config.toml'} (timezone, modes, optional calendar settings)")
    print("  2) Create a week: python3 planner/scripts/new_week.py --week-start YYYY-MM-DD")
    print("  3) Validate:     python3 planner/scripts/validate.py --week planner/weeks/YYYY-Www.toml")
    print("  4) Publish (optional):")
    print("     - Google Calendar sync (dry-run): python3 planner/scripts/sync_week.py --week planner/weeks/YYYY-Www.toml")
    print("     - Export .ics:                   python3 planner/scripts/export_ics.py --week planner/weeks/YYYY-Www.toml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
