#!/usr/bin/env python3
"""Merge model-selected query results and write per-paper metadata directories."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge selected indexes from per-query result JSON files.")
    parser.add_argument("--run-dir", required=True, help="Run directory initialized by init_collection_run.py.")
    parser.add_argument(
        "--keep",
        action="append",
        default=[],
        help="Keep indexes: label:0,2,5 (repeatable).",
    )
    parser.add_argument(
        "--keep-id",
        action="append",
        default=[],
        help="Keep arXiv IDs: label:2601.00001,2601.00002 (repeatable).",
    )
    parser.add_argument(
        "--selection-json",
        default="",
        help=(
            "Optional JSON file. Supports {label: [indexes_or_ids,...]} "
            "or {label: {keep_indexes:[...], keep_ids:[...]}}."
        ),
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help=(
            "Load existing query_selection/selected_by_query.json as base selection, "
            "then apply current keep options as updates."
        ),
    )
    parser.add_argument("--max-final", type=int, default=0, help="Optional cap on merged final papers.")
    parser.add_argument(
        "--sort-by",
        default="published_desc",
        choices=["published_desc", "published_asc", "title"],
        help="Final ordering before optional truncation.",
    )
    parser.add_argument(
        "--language",
        default="",
        help="Optional markdown language override. If empty, use task_meta.json params.language.",
    )
    return parser.parse_args()


def parse_keep_specs(specs: list[str]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid --keep spec '{spec}'. Expected label:0,1,2")
        label, raw = spec.split(":", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"Invalid --keep spec '{spec}'. Empty label.")
        indexes = []
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            indexes.append(int(part))
        out.setdefault(label, []).extend(indexes)
    for label in out:
        out[label] = sorted(set(out[label]))
    return out


def parse_keep_id_specs(specs: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for spec in specs:
        if ":" not in spec:
            raise ValueError(f"Invalid --keep-id spec '{spec}'. Expected label:id1,id2")
        label, raw = spec.split(":", 1)
        label = label.strip()
        if not label:
            raise ValueError(f"Invalid --keep-id spec '{spec}'. Empty label.")
        ids = [part.strip() for part in raw.split(",") if part.strip()]
        out.setdefault(label, []).extend(ids)
    for label in out:
        out[label] = sorted(set(out[label]))
    return out


def load_existing_selection_manifest(
    run_dir: Path,
) -> tuple[dict[str, list[int]], dict[str, list[str]], set[str]]:
    path = run_dir / "query_selection" / "selected_by_query.json"
    if not path.exists():
        return {}, {}, set()
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}, {}, set()
    if not isinstance(data, dict):
        return {}, {}, set()

    keep_by_index: dict[str, list[int]] = {}
    keep_by_id: dict[str, list[str]] = {}
    explicit_labels: set[str] = set()

    for raw_label, row in data.items():
        label = str(raw_label).strip()
        if not label or not isinstance(row, dict):
            continue
        explicit_labels.add(label)

        idx_values = row.get("keep_indexes", [])
        if isinstance(idx_values, list):
            keep_by_index[label] = sorted(
                set(int(x) for x in idx_values if isinstance(x, int) or str(x).isdigit())
            )

        id_values = row.get("keep_ids", [])
        if isinstance(id_values, list):
            keep_by_id[label] = sorted(
                set(str(x).strip() for x in id_values if str(x).strip())
            )

    return keep_by_index, keep_by_id, explicit_labels


def parse_selection_json_overrides(
    selection_path: Path,
) -> tuple[dict[str, list[int]], dict[str, list[str]], set[str]]:
    try:
        data = json.loads(selection_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid selection JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(
            "selection JSON must be an object: "
            "{label: [indexes_or_ids]} or {label: {keep_indexes:[...], keep_ids:[...]}}"
        )

    keep_by_index: dict[str, list[int]] = {}
    keep_by_id: dict[str, list[str]] = {}
    explicit_labels: set[str] = set()

    for raw_label, values in data.items():
        label = str(raw_label).strip()
        if not label:
            continue
        explicit_labels.add(label)

        indexes: list[int] = []
        keep_ids: list[str] = []

        if isinstance(values, list):
            for value in values:
                if isinstance(value, int):
                    indexes.append(value)
                elif isinstance(value, str):
                    stripped = value.strip()
                    if not stripped:
                        continue
                    if stripped.isdigit():
                        indexes.append(int(stripped))
                    else:
                        keep_ids.append(stripped)
        elif isinstance(values, dict):
            raw_indexes = values.get("keep_indexes", [])
            raw_ids = values.get("keep_ids", [])
            if isinstance(raw_indexes, list):
                for value in raw_indexes:
                    if isinstance(value, int):
                        indexes.append(value)
                    elif isinstance(value, str) and value.strip().isdigit():
                        indexes.append(int(value.strip()))
            if isinstance(raw_ids, list):
                for value in raw_ids:
                    stripped = str(value).strip()
                    if stripped:
                        keep_ids.append(stripped)
        else:
            raise ValueError(
                f"selection JSON entry for '{label}' must be list or object, got {type(values).__name__}"
            )

        keep_by_index[label] = sorted(set(indexes))
        keep_by_id[label] = sorted(set(keep_ids))

    return keep_by_index, keep_by_id, explicit_labels


def load_query_result(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        raise ValueError(f"Invalid query result json: {path}")
    return data


def normalize_arxiv_id(raw: str) -> str:
    raw = str(raw or "").strip()
    if not raw:
        return ""
    m = re.search(r"/(?:abs|pdf)/([^/?#]+)", raw)
    if m:
        raw = m.group(1)
    raw = raw.split("/")[-1]
    return re.sub(r"v\d+$", "", raw)


def normalize_language(raw: str) -> str:
    low = raw.strip().lower()
    if low in {"zh", "zh-cn", "zh-hans", "chinese", "cn", "中文", "汉语", "简体中文"}:
        return "zh"
    return "en"


def write_paper_metadata_md(paper: dict[str, Any], path: Path, lang_code: str) -> None:
    if lang_code == "zh":
        lines = [
            "# 论文元数据",
            "",
            f"- **ArXiv 编号**: {paper.get('base_id', '')}",
            f"- **版本编号**: {paper.get('id', '')}",
            f"- **标题**: {paper.get('title', '')}",
            f"- **作者**: {', '.join(paper.get('authors', []))}",
            f"- **主分类**: {paper.get('primary_category', '')}",
            f"- **全部分类**: {', '.join(paper.get('categories', []))}",
            f"- **发布时间**: {paper.get('published', '')}",
            f"- **更新时间**: {paper.get('updated', '')}",
            f"- **摘要页链接**: {paper.get('abs_url', '')}",
            f"- **PDF 链接**: {paper.get('pdf_url', '')}",
            f"- **来自查询标签**: {', '.join(sorted(set(paper.get('selected_from_labels', []))))}",
        ]
        if paper.get("comment"):
            lines.append(f"- **备注**: {paper.get('comment')}")
        if paper.get("journal_ref"):
            lines.append(f"- **期刊信息**: {paper.get('journal_ref')}")
        if paper.get("doi"):
            lines.append(f"- **DOI**: {paper.get('doi')}")

        lines += ["", "## 摘要", "", paper.get("summary", "").strip()]
    else:
        lines = [
            "# Paper Metadata",
            "",
            f"- **ArXiv ID**: {paper.get('base_id', '')}",
            f"- **Versioned ID**: {paper.get('id', '')}",
            f"- **Title**: {paper.get('title', '')}",
            f"- **Authors**: {', '.join(paper.get('authors', []))}",
            f"- **Primary Category**: {paper.get('primary_category', '')}",
            f"- **Categories**: {', '.join(paper.get('categories', []))}",
            f"- **Published**: {paper.get('published', '')}",
            f"- **Updated**: {paper.get('updated', '')}",
            f"- **Abs URL**: {paper.get('abs_url', '')}",
            f"- **PDF URL**: {paper.get('pdf_url', '')}",
            f"- **Selected From Query Labels**: {', '.join(sorted(set(paper.get('selected_from_labels', []))))}",
        ]
        if paper.get("comment"):
            lines.append(f"- **Comment**: {paper.get('comment')}")
        if paper.get("journal_ref"):
            lines.append(f"- **Journal Ref**: {paper.get('journal_ref')}")
        if paper.get("doi"):
            lines.append(f"- **DOI**: {paper.get('doi')}")

        lines += ["", "## Abstract", "", paper.get("summary", "").strip()]
    path.write_text("\n".join(lines).rstrip() + "\n")


def parse_published_ts(raw: str) -> float:
    from datetime import datetime

    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def sort_papers(papers: list[dict[str, Any]], mode: str) -> list[dict[str, Any]]:
    if mode == "title":
        return sorted(papers, key=lambda p: p.get("title", "").lower())
    if mode == "published_asc":
        return sorted(papers, key=lambda p: parse_published_ts(p.get("published", "")))
    return sorted(papers, key=lambda p: parse_published_ts(p.get("published", "")), reverse=True)


def load_task_meta(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "task_meta.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_task_meta(run_dir: Path, meta: dict[str, Any]) -> None:
    (run_dir / "task_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")


def load_existing_paper_dirs(run_dir: Path) -> set[Path]:
    path = run_dir / "papers_index.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return set()
    if not isinstance(data, list):
        return set()
    out: set[Path] = set()
    for row in data:
        if not isinstance(row, dict):
            continue
        paper_dir = str(row.get("paper_dir", "")).strip()
        if not paper_dir:
            continue
        p = Path(paper_dir).expanduser()
        if not p.is_absolute():
            p = (run_dir / p).resolve()
        else:
            p = p.resolve()
        if p.is_relative_to(run_dir):
            out.add(p)
    return out


def remove_stale_paper_dirs(old_dirs: set[Path], new_dirs: set[Path]) -> int:
    removed = 0
    for path in sorted(old_dirs - new_dirs):
        if path.exists() and path.is_dir():
            shutil.rmtree(path)
            removed += 1
    return removed


def run() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    if not run_dir.exists() or not run_dir.is_dir():
        print(f"[ERROR] run directory not found: {run_dir}")
        return 1

    task_meta = load_task_meta(run_dir)
    params = task_meta.get("params", {}) if isinstance(task_meta, dict) else {}
    language = args.language.strip() or str(params.get("language", "English"))
    lang_code = normalize_language(language)

    query_dir = run_dir / "query_results"
    if not query_dir.exists():
        print(f"[ERROR] query_results directory not found: {query_dir}")
        return 1

    try:
        cli_keep_by_index = parse_keep_specs(args.keep)
        cli_keep_by_id = parse_keep_id_specs(args.keep_id)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    keep_by_index: dict[str, list[int]] = {}
    keep_by_id: dict[str, list[str]] = {}
    explicit_labels: set[str] = set()

    if args.incremental:
        old_keep_by_index, old_keep_by_id, old_labels = load_existing_selection_manifest(run_dir)
        keep_by_index.update(old_keep_by_index)
        keep_by_id.update(old_keep_by_id)
        explicit_labels.update(old_labels)

    # CLI keep specs are additive updates.
    for label, indexes in cli_keep_by_index.items():
        keep_by_index[label] = sorted(set(keep_by_index.get(label, []) + indexes))
        explicit_labels.add(label)
    for label, ids in cli_keep_by_id.items():
        keep_by_id[label] = sorted(set(keep_by_id.get(label, []) + ids))
        explicit_labels.add(label)

    # selection-json acts as explicit per-label override (including empty keep list).
    if args.selection_json:
        selection_path = Path(args.selection_json).expanduser().resolve()
        if not selection_path.exists():
            print(f"[ERROR] selection JSON not found: {selection_path}")
            return 1
        try:
            json_keep_by_index, json_keep_by_id, json_labels = parse_selection_json_overrides(selection_path)
        except ValueError as exc:
            print(f"[ERROR] {exc}")
            return 1

        for label in json_labels:
            keep_by_index[label] = json_keep_by_index.get(label, [])
            keep_by_id[label] = json_keep_by_id.get(label, [])
        explicit_labels.update(json_labels)

    labels = sorted(
        set(explicit_labels)
        | set(keep_by_index.keys())
        | set(keep_by_id.keys())
    )
    if not labels:
        print(
            "[ERROR] No query labels provided. "
            "Use --keep/--keep-id/--selection-json, or --incremental with existing selection."
        )
        return 1

    for label in labels:
        keep_by_index[label] = sorted(set(keep_by_index.get(label, [])))
        keep_by_id[label] = sorted(
            set(
                normalize_arxiv_id(x)
                for x in keep_by_id.get(label, [])
                if normalize_arxiv_id(x)
            )
        )

    if sum(len(v) for v in keep_by_index.values()) + sum(len(v) for v in keep_by_id.values()) == 0:
        print(
            "[WARN] All keep selections are empty. "
            "The merge result will contain zero papers."
        )
    zero_keep_labels = sorted(
        label for label in labels if not keep_by_index.get(label) and not keep_by_id.get(label)
    )

    selected_raw: list[dict[str, Any]] = []
    selection_manifest: dict[str, Any] = {}

    for label in labels:
        query_path = query_dir / f"{label}.json"
        if not query_path.exists():
            print(f"[ERROR] Query result file missing for label '{label}': {query_path}")
            return 1
        payload = load_query_result(query_path)
        results = payload.get("results", [])
        if not isinstance(results, list):
            print(f"[ERROR] Invalid results field in {query_path}")
            return 1

        index_map = {
            int(item.get("index")): item
            for item in results
            if isinstance(item, dict) and isinstance(item.get("index"), int)
        }
        id_map = {
            normalize_arxiv_id(item.get("base_id") or item.get("id") or ""): item
            for item in results
            if isinstance(item, dict)
        }

        kept_items: list[dict[str, Any]] = []
        kept_indexes = keep_by_index.get(label, [])
        kept_ids = keep_by_id.get(label, [])

        for idx in kept_indexes:
            item = index_map.get(idx)
            if item is not None:
                kept_items.append(item)

        for keep_id in kept_ids:
            item = id_map.get(keep_id)
            if item is not None:
                kept_items.append(item)

        # Deduplicate within one label.
        seen_local: set[str] = set()
        unique_kept: list[dict[str, Any]] = []
        for item in kept_items:
            pid = normalize_arxiv_id(item.get("base_id") or item.get("id") or "")
            if not pid or pid in seen_local:
                continue
            unique_kept.append(item)
            seen_local.add(pid)

        selection_manifest[label] = {
            "keep_indexes": kept_indexes,
            "keep_ids": kept_ids,
            "selected_count": len(unique_kept),
            "query_file": str(query_path),
        }

        for item in unique_kept:
            selected_raw.append({**item, "selected_from_label": label})

    merged: dict[str, dict[str, Any]] = {}
    for item in selected_raw:
        pid = normalize_arxiv_id(item.get("base_id") or item.get("id") or "")
        if not pid:
            continue
        existing = merged.get(pid)
        if existing is None:
            row = dict(item)
            row["base_id"] = pid
            row["selected_from_labels"] = [item.get("selected_from_label", "")]
            merged[pid] = row
        else:
            existing.setdefault("selected_from_labels", [])
            existing["selected_from_labels"] = sorted(
                set(existing["selected_from_labels"] + [item.get("selected_from_label", "")])
            )

    merged_list = sort_papers(list(merged.values()), args.sort_by)
    if args.max_final > 0:
        merged_list = merged_list[: args.max_final]

    # Persist selection manifest and merged list.
    selection_dir = run_dir / "query_selection"
    selection_dir.mkdir(exist_ok=True)
    (selection_dir / "selected_by_query.json").write_text(
        json.dumps(selection_manifest, indent=2, ensure_ascii=False) + "\n"
    )
    (selection_dir / "merged_selected_raw.json").write_text(
        json.dumps(merged_list, indent=2, ensure_ascii=False) + "\n"
    )

    # Remove stale paper directories from previous merges.
    old_paper_dirs = load_existing_paper_dirs(run_dir)
    new_paper_dirs = {run_dir / paper["base_id"] for paper in merged_list}
    removed_paper_dirs = remove_stale_paper_dirs(old_paper_dirs, new_paper_dirs)

    # Write final per-paper metadata directories.
    paper_index = []
    for paper in merged_list:
        paper_dir = run_dir / paper["base_id"]
        paper_dir.mkdir(parents=True, exist_ok=True)

        metadata_json_path = paper_dir / "metadata.json"
        metadata_md_path = paper_dir / "metadata.md"

        metadata_json_path.write_text(json.dumps(paper, indent=2, ensure_ascii=False) + "\n")
        write_paper_metadata_md(paper, metadata_md_path, lang_code)

        paper_index.append(
            {
                "arxiv_id": paper.get("base_id", ""),
                "title": paper.get("title", ""),
                "primary_category": paper.get("primary_category", ""),
                "published": paper.get("published", ""),
                "paper_dir": str(paper_dir),
                "metadata_md": str(metadata_md_path),
            }
        )

    (run_dir / "papers_index.json").write_text(
        json.dumps(paper_index, indent=2, ensure_ascii=False) + "\n"
    )

    if lang_code == "zh":
        lines = ["# 论文索引", ""]
        for item in paper_index:
            lines += [
                f"- `{item['arxiv_id']}`: {item['title']}",
                f"  - 分类: {item['primary_category']}",
                f"  - 发布时间: {item['published']}",
                f"  - 目录: `{item['paper_dir']}`",
                f"  - 元数据: `{item['metadata_md']}`",
            ]
    else:
        lines = ["# Paper Index", ""]
        for item in paper_index:
            lines += [
                f"- `{item['arxiv_id']}`: {item['title']}",
                f"  - Category: {item['primary_category']}",
                f"  - Published: {item['published']}",
                f"  - Directory: `{item['paper_dir']}`",
                f"  - Metadata: `{item['metadata_md']}`",
            ]
    (run_dir / "papers_index.md").write_text("\n".join(lines).rstrip() + "\n")

    if task_meta:
        task_meta.setdefault("selection_logs", []).append(
            {
                "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                "selected_labels": labels,
                "merged_unique_count": len(merged_list),
                "selection_manifest_json": str(selection_dir / "selected_by_query.json"),
                "zero_keep_labels": zero_keep_labels,
                "incremental": args.incremental,
                "removed_stale_paper_dirs": removed_paper_dirs,
                "language": language,
                "language_normalized": lang_code,
            }
        )
        task_meta.setdefault("execution", {})
        task_meta["execution"]["selected_count"] = len(merged_list)
        task_meta["execution"]["candidate_after_merge"] = len(merged_list)
        save_task_meta(run_dir, task_meta)

    print(
        json.dumps(
            {
                "run_dir": str(run_dir),
                "selected_labels": labels,
                "final_paper_count": len(merged_list),
                "papers_index_json": str(run_dir / "papers_index.json"),
                "zero_keep_labels": zero_keep_labels,
                "incremental": args.incremental,
                "removed_stale_paper_dirs": removed_paper_dirs,
                "language": language,
                "language_normalized": lang_code,
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
