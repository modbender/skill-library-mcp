#!/usr/bin/env python3
"""Serially fetch multiple arXiv queries with safe defaults and cache-friendly behavior."""

from __future__ import annotations

import argparse
import json
import math
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run fetch_query_metadata.py for multiple query items in serial mode."
    )
    parser.add_argument("--run-dir", required=True, help="Run directory initialized by init_collection_run.py.")
    parser.add_argument(
        "--plan-json",
        required=True,
        help="Query plan JSON path. Supports list or {'queries': [...]} format.",
    )
    parser.add_argument("--python-bin", default="python3", help="Python executable for sub-calls.")
    parser.add_argument(
        "--fetch-script",
        default="",
        help="Optional explicit path to fetch_query_metadata.py.",
    )
    parser.add_argument(
        "--language",
        default="",
        help="Language override. If empty, use task_meta.json params.language.",
    )
    parser.add_argument(
        "--rate-state-path",
        default="",
        help=(
            "Optional rate-state JSON path forwarded to fetch_query_metadata.py. "
            "Default: <run_dir>/.runtime/arxiv_api_state.json."
        ),
    )
    parser.add_argument(
        "--oversample-factor",
        type=int,
        default=2,
        help="Auto max_results multiplier over target_per_query. Default 2.",
    )
    parser.add_argument(
        "--default-max-results",
        type=int,
        default=0,
        help="Optional global max_results override. 0 means auto-derive.",
    )
    parser.add_argument(
        "--max-results-cap",
        type=int,
        default=60,
        help="Cap for auto-derived per-query max_results. Default 60.",
    )
    parser.add_argument(
        "--min-interval-sec",
        type=float,
        default=5.0,
        help="Passed to fetch_query_metadata.py. Default 5.0.",
    )
    parser.add_argument(
        "--retry-max",
        type=int,
        default=4,
        help="Passed to fetch_query_metadata.py. Default 4.",
    )
    parser.add_argument(
        "--retry-base-sec",
        type=float,
        default=5.0,
        help="Passed to fetch_query_metadata.py. Default 5.0.",
    )
    parser.add_argument(
        "--retry-max-sec",
        type=float,
        default=120.0,
        help="Passed to fetch_query_metadata.py. Default 120.0.",
    )
    parser.add_argument(
        "--retry-jitter-sec",
        type=float,
        default=1.0,
        help="Passed to fetch_query_metadata.py. Default 1.0.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue remaining items when one query fetch fails.",
    )
    parser.add_argument(
        "--print-commands",
        action="store_true",
        help="Print fully resolved per-query commands before execution.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_task_meta(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "task_meta.json"
    if not path.exists():
        return {}
    try:
        data = load_json(path)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80] or "query"


def parse_target_max(raw: str) -> int:
    value = str(raw or "").strip()
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", value)
    if m:
        return max(1, int(m.group(2)))
    if value.isdigit():
        return max(1, int(value))
    return 10


def parse_last_json_block(raw: str) -> dict[str, Any]:
    lines = raw.strip().splitlines()
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].lstrip().startswith("{"):
            chunk = "\n".join(lines[idx:])
            try:
                data = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data
    return {}


def normalize_categories(value: Any) -> str:
    if isinstance(value, list):
        return ",".join(str(x).strip() for x in value if str(x).strip())
    if value is None:
        return ""
    return str(value).strip()


def normalize_plan(plan_data: Any) -> list[dict[str, Any]]:
    if isinstance(plan_data, dict):
        queries = plan_data.get("queries", [])
    elif isinstance(plan_data, list):
        queries = plan_data
    else:
        raise ValueError("Plan JSON must be a list or an object with `queries` list.")

    if not isinstance(queries, list) or not queries:
        raise ValueError("Plan JSON has no query items.")

    out: list[dict[str, Any]] = []
    for i, item in enumerate(queries):
        if not isinstance(item, dict):
            raise ValueError(f"Plan item at index {i} must be an object.")
        query = str(item.get("query", "")).strip()
        if not query:
            raise ValueError(f"Plan item at index {i} missing non-empty `query`.")
        label = str(item.get("label", "")).strip() or slugify(query)
        out.append({**item, "query": query, "label": label})
    return out


def default_rate_state_path(run_dir: Path) -> str:
    return str((run_dir / ".runtime" / "arxiv_api_state.json").resolve())


def run() -> int:
    args = parse_args()
    run_dir = Path(args.run_dir).expanduser().resolve()
    if not run_dir.exists() or not run_dir.is_dir():
        print(f"[ERROR] run directory not found: {run_dir}")
        return 1

    plan_path = Path(args.plan_json).expanduser().resolve()
    if not plan_path.exists():
        print(f"[ERROR] plan json not found: {plan_path}")
        return 1

    if args.fetch_script.strip():
        fetch_script = Path(args.fetch_script).expanduser().resolve()
    else:
        fetch_script = Path(__file__).resolve().parent / "fetch_query_metadata.py"
    if not fetch_script.exists():
        print(f"[ERROR] fetch script not found: {fetch_script}")
        return 1

    task_meta = load_task_meta(run_dir)
    params = task_meta.get("params", {}) if isinstance(task_meta, dict) else {}
    plan_data = load_json(plan_path)
    items = normalize_plan(plan_data)

    query_count = len(items)
    target_max = parse_target_max(params.get("target_range", "5-10"))
    target_per_query = int(math.ceil(target_max / max(1, query_count)))

    if args.default_max_results > 0:
        auto_max_results = args.default_max_results
    else:
        auto_max_results = target_per_query * max(1, args.oversample_factor)
        auto_max_results = max(6, auto_max_results)
        auto_max_results = min(max(1, args.max_results_cap), auto_max_results)

    default_language = args.language.strip() or str(params.get("language", "English"))
    default_categories = normalize_categories(params.get("categories", []))
    effective_rate_state_path = args.rate_state_path.strip() or default_rate_state_path(run_dir)

    results: list[dict[str, Any]] = []
    failed = 0

    for idx, item in enumerate(items, start=1):
        label = str(item.get("label", "")).strip()
        query = str(item.get("query", "")).strip()
        max_results = item.get("max_results")
        if max_results is None:
            max_results = auto_max_results
        try:
            max_results_int = int(max_results)
        except (TypeError, ValueError):
            max_results_int = auto_max_results
        if max_results_int <= 0:
            max_results_int = auto_max_results

        categories = normalize_categories(item.get("categories", ""))
        if not categories:
            categories = default_categories

        language = str(item.get("language", "")).strip() or default_language

        cmd = [
            args.python_bin,
            str(fetch_script),
            "--run-dir",
            str(run_dir),
            "--label",
            label,
            "--query",
            query,
            "--max-results",
            str(max_results_int),
            "--min-interval-sec",
            str(args.min_interval_sec),
            "--retry-max",
            str(args.retry_max),
            "--retry-base-sec",
            str(args.retry_base_sec),
            "--retry-max-sec",
            str(args.retry_max_sec),
            "--retry-jitter-sec",
            str(args.retry_jitter_sec),
            "--language",
            language,
            "--rate-state-path",
            effective_rate_state_path,
        ]

        if categories:
            cmd += ["--categories", categories]

        optional_map = [
            ("from_date", "--from-date"),
            ("to_date", "--to-date"),
            ("sort_by", "--sort-by"),
            ("sort_order", "--sort-order"),
            ("start", "--start"),
            ("request_timeout", "--request-timeout"),
            ("user_agent", "--user-agent"),
        ]
        for key, flag in optional_map:
            val = item.get(key)
            if val is None:
                continue
            val_str = str(val).strip()
            if val_str:
                cmd += [flag, val_str]

        if args.print_commands:
            print(f"[CMD {idx}/{query_count}] " + " ".join(shlex.quote(x) for x in cmd))

        proc = subprocess.run(cmd, text=True, capture_output=True)
        parsed = parse_last_json_block(proc.stdout)

        entry: dict[str, Any] = {
            "index": idx - 1,
            "label": label,
            "query": query,
            "status": "ok" if proc.returncode == 0 else "error",
            "return_code": proc.returncode,
            "max_results": max_results_int,
            "language": language,
            "categories": categories,
            "rate_state_path": effective_rate_state_path,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
        if parsed:
            entry["result"] = parsed
        results.append(entry)

        if proc.returncode != 0:
            failed += 1
            if not args.continue_on_error:
                break

    summary = {
        "run_dir": str(run_dir),
        "plan_json": str(plan_path),
        "query_count": query_count,
        "default_language": default_language,
        "target_max": target_max,
        "target_per_query": target_per_query,
        "auto_max_results": auto_max_results,
        "rate_limit_defaults": {
            "min_interval_sec": args.min_interval_sec,
            "retry_max": args.retry_max,
            "retry_base_sec": args.retry_base_sec,
            "retry_max_sec": args.retry_max_sec,
            "retry_jitter_sec": args.retry_jitter_sec,
            "rate_state_path": effective_rate_state_path,
        },
        "executed": len(results),
        "failed": failed,
        "succeeded": len(results) - failed,
        "results": results,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if failed > 0 else 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
