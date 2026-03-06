#!/usr/bin/env python3
"""Minimal cron lint checks for schedule syntax and discipline tags."""

import re
import sys
from typing import List, Tuple

BAD_MODELS = {
    "haiku-4-6",
}

ANNOUNCE_HINTS = (
    "announce",
    "announcement",
    "inbox",
    "notify",
    "message",
    "broadcast",
)


def load_lines(path: str) -> List[str]:
    if path == "-":
        return sys.stdin.read().splitlines()
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def parse_cron_line(line: str) -> Tuple[str, str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return "", ""

    parts = stripped.split()
    if len(parts) < 6:
        return "", stripped

    schedule = " ".join(parts[:5])
    command = " ".join(parts[5:])
    return schedule, command


def is_probably_announce(command: str) -> bool:
    c = command.lower()
    return any(h in c for h in ANNOUNCE_HINTS)


def lint(lines: List[str]) -> List[str]:
    issues: List[str] = []

    for idx, raw in enumerate(lines, start=1):
        schedule, command = parse_cron_line(raw)
        if not schedule and not command:
            continue

        if not schedule and command:
            issues.append(f"line {idx}: expected 5 cron schedule fields before command")
            continue

        schedule_fields = schedule.split()
        if len(schedule_fields) != 5:
            issues.append(f"line {idx}: cron schedule field count is {len(schedule_fields)} (expected 5)")

        lower_command = command.lower()
        for bad in BAD_MODELS:
            if bad in lower_command:
                issues.append(f"line {idx}: disallowed model name detected: {bad}")

        if is_probably_announce(command) and "NO_REPLY" not in command:
            issues.append("line {}: announce-like job missing NO_REPLY marker".format(idx))

    return issues


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: cron-lint.py <crontab-file|->", file=sys.stderr)
        return 2

    path = sys.argv[1]
    try:
        lines = load_lines(path)
    except OSError as exc:
        print(f"error: failed to read {path}: {exc}", file=sys.stderr)
        return 2

    issues = lint(lines)
    if not issues:
        print("OK: no issues found")
        return 0

    print("FAIL: issues found")
    for issue in issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
