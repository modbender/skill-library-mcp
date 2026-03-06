#!/usr/bin/env python3
"""Render collection_report.md from a model-authored template with arXiv-id placeholders.

The template should contain all human-authored parts (overview, tree structure, final synthesis).
For each paper leaf entry, include one placeholder line with an arXiv id. This script replaces
that placeholder line with:
- brief conclusion text extracted from summary.md section 10
- arXiv abs URL
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PLACEHOLDER_RE = re.compile(
    r"^\s*\{\{\s*ARXIV_BRIEF\s*:\s*([0-9]{4}\.[0-9]{4,5}(?:v\d+)?)\s*\}\}\s*$"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render final collection report by filling arXiv-id placeholders from per-paper summary.md files."
    )
    parser.add_argument("--base-dir", required=True, help="Run directory containing paper subdirectories.")
    parser.add_argument(
        "--template-file",
        default="collection_report_template.md",
        help="Template markdown file name or path. Default: collection_report_template.md",
    )
    parser.add_argument(
        "--output-file",
        default="collection_report.md",
        help="Rendered report file name under base dir. Default: collection_report.md",
    )
    parser.add_argument(
        "--summary-file-name",
        default="summary.md",
        help="Per-paper summary file name. Default: summary.md",
    )
    parser.add_argument(
        "--language",
        default="English",
        help="Output label language for inserted lines. Default: English.",
    )
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="Do not fail when a placeholder cannot be resolved; keep original line.",
    )
    parser.add_argument(
        "--print-to-stdout",
        action="store_true",
        help="Print rendered report to stdout after writing.",
    )
    return parser.parse_args()


def normalize_language(raw: str) -> str:
    low = raw.strip().lower()
    if low in {"zh", "zh-cn", "zh-hans", "chinese", "cn", "中文", "汉语", "简体中文"}:
        return "zh"
    return "en"


def parse_placeholder_id(line: str) -> str | None:
    m = PLACEHOLDER_RE.match(line)
    if not m:
        return None
    return m.group(1).strip()


def base_arxiv_id(arxiv_id: str) -> str:
    m = re.match(r"^([0-9]{4}\.[0-9]{4,5})(?:v\d+)?$", arxiv_id)
    if m:
        return m.group(1)
    return arxiv_id


def resolve_paper_dir(base_dir: Path, arxiv_id: str) -> Path | None:
    raw = arxiv_id.strip()
    base = base_arxiv_id(raw)
    candidates = [base_dir / raw, base_dir / base]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def extract_brief_conclusion(summary_text: str) -> str:
    heading = re.compile(
        r"^##\s*(?:10\.\s*)?(?:Brief Conclusion|简短总结|简要结论|结论总结)\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    m = heading.search(summary_text)
    if m:
        rest = summary_text[m.end() :]
        next_heading = re.search(r"^##\s+", rest, flags=re.MULTILINE)
        block = rest[: next_heading.start()] if next_heading else rest
        content = block.strip("\n")
        if content.strip():
            return content

    # Fallback: use the last level-2 section content.
    headings = list(re.finditer(r"^##\s+", summary_text, flags=re.MULTILINE))
    if headings:
        last = headings[-1]
        tail = summary_text[last.end() :].strip("\n")
        if tail.strip():
            return tail

    return ""


def injected_lines(
    *,
    source_line: str,
    brief_text: str,
    arxiv_id: str,
    lang_code: str,
) -> list[str]:
    indent = re.match(r"^(\s*)", source_line).group(1)
    marker_match = re.match(r"^\s*([*+-])\s+", source_line)
    marker = marker_match.group(1) if marker_match else "-"
    item_prefix = f"{indent}{marker} "
    cont_prefix = f"{indent}  "

    if lang_code == "zh":
        brief_label = "简要结论"
        url_label = "arXiv"
    else:
        brief_label = "Brief Conclusion"
        url_label = "ArXiv Abs URL"

    brief_lines = brief_text.splitlines() if brief_text else ["(missing brief conclusion)"]
    out = [f"{item_prefix}{brief_label}: {brief_lines[0]}"]
    for line in brief_lines[1:]:
        out.append(f"{cont_prefix}{line}")
    out.append(f"{item_prefix}{url_label}: https://arxiv.org/abs/{base_arxiv_id(arxiv_id)}")
    return out


def resolve_template_path(base_dir: Path, template_file: str) -> Path:
    candidate = Path(template_file).expanduser()
    if candidate.is_absolute():
        return candidate
    return base_dir / candidate


def run() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).expanduser().resolve()
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"[ERROR] base directory not found: {base_dir}")
        return 1

    template_path = resolve_template_path(base_dir, args.template_file)
    if not template_path.exists():
        print(f"[ERROR] template file not found: {template_path}")
        return 1

    lang_code = normalize_language(args.language)
    template_text = template_path.read_text()

    output_lines: list[str] = []
    replaced = 0
    unresolved: list[dict[str, str]] = []

    for line_no, line in enumerate(template_text.splitlines(), start=1):
        maybe_id = parse_placeholder_id(line)
        if not maybe_id:
            output_lines.append(line)
            continue

        paper_dir = resolve_paper_dir(base_dir, maybe_id)
        if not paper_dir:
            unresolved.append({"line": str(line_no), "arxiv_id": maybe_id, "reason": "paper directory not found"})
            output_lines.append(line)
            continue

        summary_path = paper_dir / args.summary_file_name
        if not summary_path.exists():
            unresolved.append({"line": str(line_no), "arxiv_id": maybe_id, "reason": f"missing {args.summary_file_name}"})
            output_lines.append(line)
            continue

        summary_text = summary_path.read_text()
        brief = extract_brief_conclusion(summary_text)
        if not brief.strip():
            unresolved.append({"line": str(line_no), "arxiv_id": maybe_id, "reason": "brief conclusion empty"})
            output_lines.append(line)
            continue

        output_lines.extend(
            injected_lines(
                source_line=line,
                brief_text=brief,
                arxiv_id=maybe_id,
                lang_code=lang_code,
            )
        )
        replaced += 1

    output_path = (base_dir / args.output_file).resolve()
    rendered = "\n".join(output_lines).rstrip() + "\n"
    output_path.write_text(rendered)

    payload = {
        "base_dir": str(base_dir),
        "template_path": str(template_path),
        "output_path": str(output_path),
        "language": args.language,
        "language_normalized": lang_code,
        "placeholders_replaced": replaced,
        "unresolved_count": len(unresolved),
        "unresolved": unresolved,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if unresolved and not args.allow_missing:
        print("[ERROR] unresolved placeholders found. Re-run with --allow-missing to keep unresolved placeholders.")
        return 1

    if replaced == 0:
        print("[ERROR] no placeholders were replaced. Check template placeholder syntax.")
        return 1

    if args.print_to_stdout:
        print("\n===== RENDERED REPORT START =====\n")
        print(rendered)
        print("\n===== RENDERED REPORT END =====\n")

    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
