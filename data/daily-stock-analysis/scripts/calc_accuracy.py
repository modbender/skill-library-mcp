#!/usr/bin/env python3
"""Compute rolling forecast accuracy from existing report files."""

from __future__ import annotations

import argparse
import json
import os
from statistics import mean
from typing import Dict, List

from _report_utils import discover_reports, parse_bool, parse_float, read_frontmatter


def _window_list(text: str) -> List[int]:
    windows = []
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        value = int(item)
        if value <= 0:
            continue
        if value not in windows:
            windows.append(value)
    return windows or [1, 3, 7, 30]


def _build_review_rows(workdir: str, ticker: str, history_limit: int) -> List[Dict[str, object]]:
    reports = discover_reports(workdir, ticker)[:history_limit]
    rows: List[Dict[str, object]] = []
    seen_run_date = set()

    for report in reports:
        # Keep the newest report for each run_date to avoid same-day duplicate counting.
        if report.run_date in seen_run_date:
            continue
        frontmatter = read_frontmatter(report.path)
        ape = parse_float(frontmatter.get("APE"))
        strict = parse_bool(frontmatter.get("strict_hit"))
        loose = parse_bool(frontmatter.get("loose_hit"))

        if strict is None and ape is not None:
            strict = ape <= 1.0
        if loose is None and ape is not None:
            loose = ape <= 2.0

        if ape is None and strict is None and loose is None:
            continue

        rows.append(
            {
                "run_date": report.run_date,
                "path": report.path,
                "ape": ape,
                "strict_hit": strict,
                "loose_hit": loose,
            }
        )
        seen_run_date.add(report.run_date)

    return rows


def _rate(hit_count: int, total: int):
    if total == 0:
        return None
    return round(hit_count * 100.0 / total, 2)


def compute_accuracy(workdir: str, ticker: str, windows: List[int], history_limit: int) -> Dict[str, object]:
    rows = _build_review_rows(workdir, ticker, history_limit)
    metrics = {}

    for window in windows:
        sample = rows[:window]
        n = len(sample)
        strict_hits = sum(1 for r in sample if r["strict_hit"] is True)
        loose_hits = sum(1 for r in sample if r["loose_hit"] is True)
        ape_values = [r["ape"] for r in sample if isinstance(r["ape"], float)]
        metrics[str(window)] = {
            "n": n,
            "strict_rate_percent": _rate(strict_hits, n),
            "loose_rate_percent": _rate(loose_hits, n),
            "avg_ape_percent": round(mean(ape_values), 4) if ape_values else None,
        }

    latest = rows[0] if rows else None
    return {
        "ticker": ticker.upper(),
        "workdir": os.path.abspath(workdir),
        "windows": metrics,
        "review_samples": len(rows),
        "latest_review": latest,
        "status": "ok" if rows else "insufficient_history",
        "security_scope": "working_directory_only",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calculate rolling forecast accuracy.")
    parser.add_argument("--workdir", default=os.getcwd())
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--windows", default="1,3,7,30")
    parser.add_argument("--history-limit", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = compute_accuracy(
        workdir=args.workdir,
        ticker=args.ticker,
        windows=_window_list(args.windows),
        history_limit=max(args.history_limit, 1),
    )
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
