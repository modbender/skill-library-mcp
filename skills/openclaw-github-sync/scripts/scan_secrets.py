#!/usr/bin/env python3
"""Lightweight secret scanner.

Exit codes:
  0 = no findings
  3 = findings found

Writes a human-readable report to stdout.

This is intentionally heuristic (false positives are acceptable).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# High-signal patterns.
PATTERNS: list[tuple[str, re.Pattern]] = [
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{30,}\b")),
    ("generic_password_assignment", re.compile(r"(?i)\b(pass(word)?|pwd|secret|api[_-]?key|token)\b\s*[:=]\s*['\"]?[^\s'\"]{6,}")),
]

# File types to scan; skip large binaries.
SCAN_EXTS = {
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".js",
    ".ts",
    ".php",
    ".sh",
    ".py",
    ".env",
    "",  # extensionless
}

SKIP_DIR_NAMES = {".git", "node_modules", "vendor", ".archive"}
SKIP_FILE_NAMES = {"hosts.yml", "known_hosts", "known_hosts.old"}


def load_ignore_rules() -> list[str]:
    """Load relative-path ignore rules from SCAN_IGNORE_FILE.

    Rules:
    - blank/comment lines ignored
    - trailing slash => directory prefix ignore
    - otherwise exact relative path match
    """
    p = os.environ.get("SCAN_IGNORE_FILE", "").strip()
    if not p:
        return []

    ignore_file = Path(p)
    if not ignore_file.exists() or not ignore_file.is_file():
        return []

    rules: list[str] = []
    for raw in ignore_file.read_text("utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rules.append(line)
    return rules


def is_ignored(rel_path: str, rules: list[str]) -> bool:
    for rule in rules:
        if rule.endswith("/"):
            if rel_path.startswith(rule):
                return True
        elif rel_path == rule:
            return True
    return False


def looks_binary(p: Path) -> bool:
    try:
        data = p.read_bytes()[:2048]
    except Exception:
        return True
    if b"\x00" in data:
        return True
    return False


def should_scan(p: Path) -> bool:
    if p.name in SKIP_FILE_NAMES:
        return False
    # Skip very large files
    try:
        if p.stat().st_size > 2_000_000:
            return False
    except FileNotFoundError:
        return False

    ext = p.suffix.lower()
    if ext not in SCAN_EXTS:
        # still scan extensionless small text files
        return False
    if looks_binary(p):
        return False
    return True


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: scan_secrets.py <dir>", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    if not root.exists() or not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    findings: list[tuple[str, str, int, str]] = []
    ignore_rules = load_ignore_rules()

    for dirpath, dirnames, filenames in os.walk(root):
        # prune dirs
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for fn in filenames:
            p = Path(dirpath) / fn
            rel = str(p.relative_to(root))
            if is_ignored(rel, ignore_rules):
                continue
            if not should_scan(p):
                continue
            try:
                text = p.read_text("utf-8", errors="replace")
            except Exception:
                continue

            for label, rx in PATTERNS:
                for m in rx.finditer(text):
                    # approximate line number
                    line_no = text[: m.start()].count("\n") + 1
                    snippet = m.group(0)
                    if len(snippet) > 120:
                        snippet = snippet[:120] + "…"
                    findings.append((label, rel, line_no, snippet))

    if not findings:
        print("OK: no likely secrets found")
        return 0

    print("POTENTIAL SECRETS DETECTED — refusing to commit/push")
    print("Review and remove/redact these before syncing:")
    for label, rel, line_no, snippet in findings[:200]:
        print(f"- {label}: {rel}:{line_no}: {snippet}")

    if len(findings) > 200:
        print(f"… plus {len(findings) - 200} more")

    return 3


if __name__ == "__main__":
    raise SystemExit(main())
