#!/usr/bin/env python3
"""Initialize one arXiv collection run directory and task metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize run directory for query-driven collection.")
    parser.add_argument("--output-root", required=True, help="Root path containing collection runs.")
    parser.add_argument("--topic", required=True, help="Original user goal/topic description.")
    parser.add_argument(
        "--keywords",
        default="",
        help="Optional comma-separated high-level keywords for reference only.",
    )
    parser.add_argument(
        "--categories",
        default="",
        help="Optional comma-separated categories for reference only.",
    )
    parser.add_argument(
        "--target-range",
        default="5-10",
        help="Desired paper count range, e.g. 2-5, 5-10, 10-50.",
    )
    parser.add_argument(
        "--lookback",
        default="7d",
        help="Lookback window when --from-date is not provided. Format Nd/Nw/Nm.",
    )
    parser.add_argument("--from-date", default="", help="Start date YYYY-MM-DD.")
    parser.add_argument("--to-date", default="", help="End date YYYY-MM-DD.")
    parser.add_argument("--run-name", default="", help="Optional explicit run directory name.")
    parser.add_argument(
        "--notes",
        default="",
        help="Optional free text notes stored in task metadata.",
    )
    parser.add_argument(
        "--language",
        default="English",
        help="Language for generated markdown files. Example: English, Chinese, zh.",
    )
    return parser.parse_args()


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "topic"


def parse_date(raw: str, end_of_day: bool) -> dt.datetime:
    base = dt.datetime.strptime(raw, "%Y-%m-%d")
    if end_of_day:
        base = base.replace(hour=23, minute=59, second=59)
    return base.replace(tzinfo=dt.timezone.utc)


def parse_lookback(raw: str) -> dt.timedelta:
    m = re.fullmatch(r"\s*(\d+)\s*([dwm])\s*", raw)
    if not m:
        raise ValueError("Invalid lookback format. Use Nd/Nw/Nm.")
    amount = int(m.group(1))
    unit = m.group(2)
    if amount <= 0:
        raise ValueError("Lookback must be positive.")
    if unit == "d":
        return dt.timedelta(days=amount)
    if unit == "w":
        return dt.timedelta(weeks=amount)
    return dt.timedelta(days=amount * 30)


def normalize_language(raw: str) -> str:
    low = raw.strip().lower()
    if low in {"zh", "zh-cn", "zh-hans", "chinese", "cn", "中文", "汉语", "简体中文"}:
        return "zh"
    return "en"


def resolve_window(args: argparse.Namespace) -> tuple[str, str, str]:
    now = dt.datetime.now(dt.timezone.utc)
    to_dt = parse_date(args.to_date, end_of_day=True) if args.to_date else now
    if args.from_date:
        from_dt = parse_date(args.from_date, end_of_day=False)
        label = f"{from_dt.date()}_to_{to_dt.date()}"
    else:
        from_dt = to_dt - parse_lookback(args.lookback)
        label = args.lookback.strip().replace(" ", "")
    if from_dt > to_dt:
        raise ValueError("from-date must be <= to-date")
    return from_dt.date().isoformat(), to_dt.date().isoformat(), label


def write_task_meta_md(meta: dict, path: Path) -> None:
    params = meta.get("params", {})
    lang_code = normalize_language(str(params.get("language", "English")))

    if lang_code == "zh":
        lines = [
            "# 任务元信息",
            "",
            "## 请求参数",
            f"- **主题**: {params.get('topic', '')}",
            f"- **关键词**: {', '.join(params.get('keywords', [])) or '(无)'}",
            f"- **分类**: {', '.join(params.get('categories', [])) or '(无)'}",
            f"- **目标数量范围**: {params.get('target_range', '')}",
            f"- **时间窗口**: {params.get('from_date', '')} to {params.get('to_date', '')}",
            f"- **回看范围**: {params.get('lookback', '')}",
            f"- **语言**: {params.get('language', 'English')}",
        ]
    else:
        lines = [
            "# Task Metadata",
            "",
            "## Request",
            f"- **Topic**: {params.get('topic', '')}",
            f"- **Keywords**: {', '.join(params.get('keywords', [])) or '(none)'}",
            f"- **Categories**: {', '.join(params.get('categories', [])) or '(none)'}",
            f"- **Target Range**: {params.get('target_range', '')}",
            f"- **Date Window**: {params.get('from_date', '')} to {params.get('to_date', '')}",
            f"- **Lookback**: {params.get('lookback', '')}",
            f"- **Language**: {params.get('language', 'English')}",
        ]

    notes = meta.get("notes", "")
    if notes:
        if lang_code == "zh":
            lines += ["", "## 备注", notes]
        else:
            lines += ["", "## Notes", notes]

    if lang_code == "zh":
        lines += [
            "",
            "## 流程状态",
            "- 查询规划: pending",
            "- 分查询检索: pending",
            "- 模型相关性筛选: pending",
            "- 合并与去重: pending",
            "",
            "## 目录结构",
            "- `query_results/`: 每个查询的原始结果列表",
            "- `query_selection/`: 模型保留索引或ID",
            "- `<arxiv_id>/`: 合并后每篇论文的元数据目录",
        ]
    else:
        lines += [
            "",
            "## Workflow Status",
            "- Query planning: pending",
            "- Per-query retrieval: pending",
            "- Per-query relevance filtering by model: pending",
            "- Merge and dedupe: pending",
            "",
            "## Directory Layout",
            "- `query_results/`: raw result lists for each query",
            "- `query_selection/`: model-selected keep indexes",
            "- `<arxiv_id>/`: per-paper metadata output after merge",
        ]
    path.write_text("\n".join(lines).rstrip() + "\n")


def run() -> int:
    args = parse_args()
    try:
        from_date, to_date, range_label = resolve_window(args)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    output_root = Path(args.output_root).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    run_name = args.run_name.strip() or (
        f"{slugify(args.topic)}-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S')}-{range_label}"
    )
    run_dir = output_root / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    (run_dir / "query_results").mkdir(exist_ok=True)
    (run_dir / "query_selection").mkdir(exist_ok=True)

    task_meta = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "params": {
            "topic": args.topic,
            "keywords": split_csv(args.keywords),
            "categories": split_csv(args.categories),
            "target_range": args.target_range,
            "lookback": args.lookback,
            "from_date": from_date,
            "to_date": to_date,
            "language": args.language,
            "language_normalized": normalize_language(args.language),
        },
        "notes": args.notes,
        "query_plan": [],
        "query_fetch_logs": [],
        "selection_logs": [],
    }

    (run_dir / "task_meta.json").write_text(json.dumps(task_meta, indent=2, ensure_ascii=False) + "\n")
    write_task_meta_md(task_meta, run_dir / "task_meta.md")

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "task_meta_json": str(run_dir / "task_meta.json"),
                "task_meta_md": str(run_dir / "task_meta.md"),
                "language": args.language,
                "language_normalized": normalize_language(args.language),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
