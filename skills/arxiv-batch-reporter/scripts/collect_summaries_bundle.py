#!/usr/bin/env python3
"""Collect all paper summaries under a run directory into one long markdown bundle."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Concatenate all summary.md files for model-level final synthesis.")
    parser.add_argument("--base-dir", required=True, help="Run directory containing paper subdirectories.")
    parser.add_argument(
        "--output-file",
        default="summaries_bundle.md",
        help="Output bundle markdown file under base dir.",
    )
    parser.add_argument(
        "--language",
        default="English",
        help="Bundle scaffold language. Default: English.",
    )
    parser.add_argument(
        "--summary-file-name",
        default="summary.md",
        help="Per-paper summary file name.",
    )
    parser.add_argument(
        "--print-to-stdout",
        action="store_true",
        help="Print full bundle markdown to stdout after writing file.",
    )
    return parser.parse_args()


def normalize_language(raw: str) -> str:
    low = raw.strip().lower()
    if low in {"zh", "zh-cn", "zh-hans", "chinese", "cn", "中文", "汉语", "简体中文"}:
        return "zh"
    return "en"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def parse_metadata_md(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data: dict[str, Any] = {}
    mapping = {
        "ArXiv ID": "base_id",
        "Versioned ID": "id",
        "Title": "title",
        "Primary Category": "primary_category",
        "Published": "published",
        "ArXiv 编号": "base_id",
        "版本编号": "id",
        "标题": "title",
        "主分类": "primary_category",
        "发布时间": "published",
    }
    text = path.read_text()
    for line in text.splitlines():
        m = re.match(r"^- \*\*(.+?)\*\*: ?(.*)$", line.strip())
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        mapped = mapping.get(key)
        if mapped:
            data[mapped] = value.strip()
    return data


def extract_brief_conclusion(summary_text: str) -> str:
    heading = re.compile(
        r"^##\s*(?:10\.\s*)?(Brief Conclusion|简短总结|简要结论|结论总结)\s*$",
        flags=re.IGNORECASE | re.MULTILINE,
    )
    m = heading.search(summary_text)
    if m:
        rest = summary_text[m.end() :]
        next_heading = re.search(r"^##\s+", rest, flags=re.MULTILINE)
        block = rest[: next_heading.start()] if next_heading else rest
        line = re.sub(r"\s+", " ", block).strip()
        if line:
            return line

    headings = list(re.finditer(r"^##\s+", summary_text, flags=re.MULTILINE))
    if headings:
        tail = summary_text[headings[-1].end() :]
        line = re.sub(r"\s+", " ", tail).strip()
        if line:
            return line
    return ""


def rel(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def collect_papers(base_dir: Path, summary_file_name: str) -> list[dict[str, Any]]:
    papers: list[dict[str, Any]] = []
    for child in sorted(base_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        meta_json = child / "metadata.json"
        meta_md = child / "metadata.md"
        summary_path = child / summary_file_name
        if not meta_json.exists() and not meta_md.exists():
            continue

        metadata = read_json(meta_json) if meta_json.exists() else {}
        if not metadata:
            metadata = parse_metadata_md(meta_md)

        summary_text = summary_path.read_text() if summary_path.exists() else ""

        arxiv_id = str(metadata.get("base_id") or metadata.get("id") or child.name)
        title = str(metadata.get("title") or "(untitled)")
        primary_category = str(metadata.get("primary_category") or "unknown")
        published = str(metadata.get("published") or "")
        brief = extract_brief_conclusion(summary_text)

        papers.append(
            {
                "arxiv_id": arxiv_id,
                "title": title,
                "primary_category": primary_category,
                "published": published,
                "paper_dir": child,
                "summary_path": summary_path if summary_path.exists() else None,
                "summary_text": summary_text,
                "brief": brief,
            }
        )
    return papers


def load_task_meta(base_dir: Path) -> dict[str, Any]:
    data = read_json(base_dir / "task_meta.json")
    if data:
        return data
    return {}


def render_bundle(
    *,
    base_dir: Path,
    language: str,
    lang_code: str,
    task_meta: dict[str, Any],
    papers: list[dict[str, Any]],
) -> str:
    params = task_meta.get("params", {}) if isinstance(task_meta, dict) else {}
    topic = params.get("topic", "")
    target = params.get("target_range", "")
    from_date = params.get("from_date", "")
    to_date = params.get("to_date", "")

    if lang_code == "zh":
        lines = [
            "# 论文总结汇总包",
            "",
            f"- **生成时间**: {dt.datetime.now(dt.timezone.utc).isoformat()}",
            f"- **语言参数**: {language}",
            f"- **基础目录**: `{base_dir}`",
            f"- **主题**: {topic}",
            f"- **目标数量范围**: {target}",
            f"- **时间范围**: {from_date} to {to_date}",
            f"- **论文数量**: {len(papers)}",
            "",
            "## 给模型的任务",
            "",
            "根据下方所有论文的元数据和摘要内容，写出层次化论文集报告。",
            "要求：类别层次适中、每个叶子类列出论文题目和简短总结，最后给整体精简总结。",
            "",
            "## 论文条目",
            "",
        ]
    else:
        lines = [
            "# Paper Summary Bundle",
            "",
            f"- **Generated At**: {dt.datetime.now(dt.timezone.utc).isoformat()}",
            f"- **Language Parameter**: {language}",
            f"- **Base Directory**: `{base_dir}`",
            f"- **Topic**: {topic}",
            f"- **Target Range**: {target}",
            f"- **Time Window**: {from_date} to {to_date}",
            f"- **Paper Count**: {len(papers)}",
            "",
            "## Model Task",
            "",
            "Use all metadata + summary blocks below to produce a hierarchical collection report.",
            "Keep category depth moderate and end with one concise overall synthesis paragraph.",
            "",
            "## Paper Entries",
            "",
        ]

    for i, paper in enumerate(papers, start=1):
        if lang_code == "zh":
            lines += [
                "",
                f"### {i}. {paper['title']} ({paper['arxiv_id']})",
                "",
                f"- 分类: {paper['primary_category']}",
                f"- 发布时间: {paper['published']}",
                f"- 目录: `{rel(paper['paper_dir'], base_dir)}`",
                f"- 摘要路径: `{rel(paper['summary_path'], base_dir) if paper['summary_path'] else '(缺失)'}`",
                f"- 简短总结: {paper['brief'] or '(缺失)'}",
                "",
                "#### 完整摘要",
                "",
            ]
        else:
            lines += [
                "",
                f"### {i}. {paper['title']} ({paper['arxiv_id']})",
                "",
                f"- Category: {paper['primary_category']}",
                f"- Published: {paper['published']}",
                f"- Directory: `{rel(paper['paper_dir'], base_dir)}`",
                f"- Summary Path: `{rel(paper['summary_path'], base_dir) if paper['summary_path'] else '(missing)'}`",
                f"- Brief Conclusion: {paper['brief'] or '(missing)'}",
                "",
                "#### Full Summary",
                "",
            ]
        if paper["summary_text"]:
            lines.append(paper["summary_text"].rstrip())
        else:
            lines.append("(缺失 summary.md)" if lang_code == "zh" else "(missing summary.md)")

    return normalize_markdown_layout("\n".join(lines).rstrip() + "\n")


def normalize_markdown_layout(text: str) -> str:
    """Normalize heading/list spacing for markdownlint-friendly output."""
    normalized = normalize_heading_blank_lines(text)
    normalized = normalize_list_blank_lines(normalized)
    # Re-run heading spacing in case list normalization changed nearby context.
    return normalize_heading_blank_lines(normalized)


def normalize_heading_blank_lines(text: str) -> str:
    """Ensure markdown headings are surrounded by blank lines (MD022-friendly)."""
    src_lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    heading_re = re.compile(r"^#{1,6}\s+\S")

    for line in src_lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            continue

        is_heading = (not in_fence) and bool(heading_re.match(stripped))
        if is_heading:
            if out and out[-1].strip():
                out.append("")
            out.append(line)
            out.append("")
            continue

        out.append(line)

    # Collapse repeated blank lines to one line for cleaner output.
    compact: list[str] = []
    blank = False
    for line in out:
        if line.strip() == "":
            if blank:
                continue
            blank = True
            compact.append("")
        else:
            blank = False
            compact.append(line)

    return "\n".join(compact).rstrip() + "\n"


def normalize_list_blank_lines(text: str) -> str:
    """Ensure list blocks have surrounding blank lines (MD032-friendly)."""
    src_lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    in_list = False
    list_re = re.compile(r"^\s*(?:[-+*]|\d+\.)\s+\S")

    for line in src_lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append(line)
            in_list = False
            continue

        if in_fence:
            out.append(line)
            continue

        is_list_item = bool(list_re.match(line))

        if is_list_item:
            if out and out[-1].strip():
                out.append("")
            out.append(line)
            in_list = True
            continue

        if in_list:
            if stripped == "":
                out.append(line)
                in_list = False
                continue

            # Allow indented continuation lines to stay in list context.
            if re.match(r"^\s{2,}\S", line):
                out.append(line)
                continue

            if out and out[-1].strip():
                out.append("")
            out.append(line)
            in_list = False
            continue

        out.append(line)

    compact: list[str] = []
    blank = False
    for line in out:
        if line.strip() == "":
            if blank:
                continue
            blank = True
            compact.append("")
        else:
            blank = False
            compact.append(line)

    return "\n".join(compact).rstrip() + "\n"


def run() -> int:
    args = parse_args()
    base_dir = Path(args.base_dir).expanduser().resolve()
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"[ERROR] base directory not found: {base_dir}")
        return 1

    lang_code = normalize_language(args.language)
    task_meta = load_task_meta(base_dir)
    papers = collect_papers(base_dir, args.summary_file_name)

    bundle_text = render_bundle(
        base_dir=base_dir,
        language=args.language,
        lang_code=lang_code,
        task_meta=task_meta,
        papers=papers,
    )

    output_path = base_dir / args.output_file
    output_path.write_text(bundle_text)

    payload = {
        "base_dir": str(base_dir),
        "language": args.language,
        "language_normalized": lang_code,
        "paper_count": len(papers),
        "bundle_path": str(output_path),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.print_to_stdout:
        print("\n===== BUNDLE START =====\n")
        print(bundle_text)
        print("\n===== BUNDLE END =====\n")

    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
