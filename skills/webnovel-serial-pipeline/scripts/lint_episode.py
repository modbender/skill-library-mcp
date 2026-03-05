#!/usr/bin/env python3
"""Lightweight style linter for our webnovel rules."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


BANNED_PATTERNS = [
    (re.compile(r"같아서|것\s*같아서"), "pattern-spam: ~같아서"),
    (re.compile(r"그래서\s+더\s+\w+였다"), "writer-commentary: 그래서 더 ~였다"),
]

SUGGEST_PATTERNS = [
    (re.compile(r"오히려"), "check-tone: 오히려 (overuse?)"),
    (re.compile(r"증거처럼"), "check-tone: 증거처럼 (essay tone?)"),
    (re.compile(r"생활의\s+기술"), "check-tone: 생활의 기술 (essay tone?)"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    args = ap.parse_args()

    p = Path(args.file)
    t = p.read_text(encoding="utf-8", errors="ignore")
    lines = t.splitlines()

    errors = []
    warns = []

    for i, ln in enumerate(lines, 1):
        for rx, msg in BANNED_PATTERNS:
            if rx.search(ln):
                errors.append((i, msg, ln.strip()))
        for rx, msg in SUGGEST_PATTERNS:
            if rx.search(ln):
                warns.append((i, msg, ln.strip()))

    print(f"file: {p}")
    print(f"errors: {len(errors)} warnings: {len(warns)}")

    if errors:
        print("\n[ERRORS]")
        for i, msg, ln in errors[:80]:
            print(f"{i:>4}: {msg} :: {ln}")

    if warns:
        print("\n[WARNINGS]")
        for i, msg, ln in warns[:80]:
            print(f"{i:>4}: {msg} :: {ln}")

    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
