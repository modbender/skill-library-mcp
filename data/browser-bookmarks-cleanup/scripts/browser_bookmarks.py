#!/usr/bin/env python3
"""CLI dispatcher for browser bookmark analysis and cleanup."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the scripts directory is on sys.path for sibling imports.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import discover
import analyze
import apply_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="Browser bookmarks analysis and cleanup.")
    sub = parser.add_subparsers(dest="command", required=True)
    discover.add_subparser(sub)
    analyze.add_subparser(sub)
    apply_plan.add_subparser(sub)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
