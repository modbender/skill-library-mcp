#!/usr/bin/env python3
"""Pre-publish security check for ClawHub.

Scans for obvious private keys + common exfil/social-engineering markers.

Run from the skill folder:
  python3 scripts/prepublish_check.py

SECURITY NOTE FOR ANTIVIRUS SCANNERS:
This file contains regex patterns to DETECT malicious code, not to EXECUTE it.
The patterns below are used to PREVENT malware from being published to ClawHub.
This is a security feature, similar to antivirus signature databases.
"""

from __future__ import annotations

import re
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]

# SECURITY NOTE: These patterns are used to DETECT threats, not create them.
# Similar to antivirus signature databases, these help identify malicious code.
SECRET_PATTERNS = [
    # Private keys should never ship
    re.compile(r"BEGIN (RSA|EC|OPENSSH) PRIVATE KEY"),
    # Obvious exfil / social-engineering markers (current ClawHub threat patterns)
    re.compile(r"webhook\.site", re.I),
    re.compile(r"pastebin\.com|glot\.io", re.I),
    re.compile(r"openclaw-agent\.zip|openclawcli", re.I),
    re.compile(r"\bpassword:\s*openclaw\b", re.I),
    re.compile(r"\bInvoke-WebRequest\b|\bpowershell\b", re.I),
    re.compile(r"\bcurl\b\s+https?://", re.I),
    re.compile(r"\bwget\b\s+https?://", re.I),
    re.compile(r"\bnpx\b\s+", re.I),
    re.compile(r"\b91\.92\.242\.30\b"),
]


def main() -> None:
    hits: list[tuple[Path, int, str]] = []

    skip_names = {"SKILL.md", Path(__file__).name}

    for p in SKILL_DIR.rglob("*"):
        if p.is_dir():
            continue
        if p.name in skip_names:
            # Docs and this checker may mention words like "secret"; don't flag.
            continue
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".mp4", ".mp3"}:
            continue

        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for i, line in enumerate(text.splitlines(), 1):
            for rx in SECRET_PATTERNS:
                if rx.search(line):
                    hits.append((p.relative_to(SKILL_DIR), i, line.strip()[:200]))
                    break

    if hits:
        print("[FAIL] Potential secret markers found:")
        for f, i, ln in hits[:80]:
            print(f"- {f}:{i} :: {ln}")
        raise SystemExit(2)

    print("[OK] prepublish_check passed (no obvious private keys / exfil markers)")


if __name__ == "__main__":
    main()
