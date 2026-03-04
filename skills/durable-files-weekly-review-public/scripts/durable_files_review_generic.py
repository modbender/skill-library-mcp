#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

FILES = [
    "AGENTS.md",
    "SOUL.md",
    "USER.md",
    "TOOLS.md",
    "MEMORY.md",
    "IDENTITY.md",
    "PRIORITIES.md",
    "SKILLS.md",
    "projects.md",
]

STALE_PATTERNS = [
    r"\\bdeprecated\\b",
    r"\\blegacy\\b",
    r"\\bTODO\\b",
    r"\\b20\\d{2}-\\d{2}-\\d{2}\\b",
    r"cannot access|missing|not found",
]


def token_estimate(text: str) -> int:
    return max(1, int(len(text) / 4))


def build_report(root: Path, out_dir: Path) -> Path:
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    ts = now.strftime("%Y-%m-%d %H:%M")

    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{date}.md"

    lines = [
        f"# Durable Files Weekly Review ({date})",
        "",
        f"- Generated: {ts}",
        f"- Root: `{root}`",
        "- Rule: do not remove content without explicit user approval",
        "",
        "## File Metrics",
        "",
        "| File | Lines | Chars | Est. tokens |",
        "|---|---:|---:|---:|",
    ]

    total_tokens = 0
    findings: list[str] = []

    for rel in FILES:
        p = root / rel
        if not p.exists():
            findings.append(f"- Missing file: `{rel}`")
            continue

        text = p.read_text(encoding="utf-8", errors="replace")
        n_lines = text.count("\n") + 1
        n_chars = len(text)
        est = token_estimate(text)
        total_tokens += est

        lines.append(f"| `{rel}` | {n_lines} | {n_chars} | {est} |")

        for pat in STALE_PATTERNS:
            if re.search(pat, text, flags=re.IGNORECASE):
                findings.append(f"- `{rel}` potential stale marker: pattern `{pat}`")

        if n_lines > 220:
            findings.append(f"- `{rel}` is large ({n_lines} lines); candidate for compaction/splitting")

    lines += [
        "",
        f"**Total estimated tokens:** {total_tokens}",
        "",
        "## Suggested Actions",
    ]

    if findings:
        lines.extend(findings)
    else:
        lines.append("- No obvious stale markers found via automated scan.")

    lines += [
        "",
        "## Manual Approval Queue",
        "- Propose removals in chat before editing.",
        "- Apply only approved batches.",
    ]

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly durable-file review report generator")
    parser.add_argument("--root", default=".", help="Workspace root to scan")
    parser.add_argument("--out", default="knowledge/reports/durable-files", help="Output directory for reports")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out

    report = build_report(root, out)
    print(str(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
