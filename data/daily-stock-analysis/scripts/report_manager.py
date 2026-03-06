#!/usr/bin/env python3
"""Deterministic report path and migration manager for daily-stock-analysis."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from datetime import date
from typing import Dict, List

from _report_utils import (
    FILENAME_RE,
    canonical_reports_dir,
    discover_reports,
    is_within_workdir,
)


def _same_day_versions_in_canonical(
    reports: List, reports_dir: str, run_date: str, ticker_upper: str
) -> List[int]:
    versions = []
    for report in reports:
        if report.run_date != run_date:
            continue
        if report.ticker != ticker_upper:
            continue
        if os.path.dirname(report.path) != reports_dir:
            continue
        versions.append(report.version)
    return versions


def plan_output(
    workdir: str,
    ticker: str,
    run_date: str,
    versioning: str,
    unattended: bool,
    history_limit: int,
) -> Dict[str, object]:
    root = os.path.abspath(workdir)
    ticker_upper = ticker.upper()
    reports_dir = canonical_reports_dir(root)
    os.makedirs(reports_dir, exist_ok=True)

    reports = discover_reports(root, ticker_upper)
    history_files = [r.path for r in reports[:history_limit]]
    legacy_files = [r.path for r in reports if not r.in_canonical_dir]

    base_name = f"{run_date}-{ticker_upper}-analysis.md"
    base_path = os.path.join(reports_dir, base_name)
    base_exists = os.path.exists(base_path)

    requires_user_choice = False
    selected_mode = "new_file"
    selected_path = base_path

    if base_exists:
        if versioning == "overwrite":
            selected_mode = "overwrite"
        elif versioning == "new_version":
            selected_mode = "new_version"
        else:
            if unattended:
                selected_mode = "new_version"
            else:
                selected_mode = "new_version"
                requires_user_choice = True

    if selected_mode == "new_version":
        versions = _same_day_versions_in_canonical(
            reports, reports_dir, run_date, ticker_upper
        )
        next_version = max(versions or [1]) + 1
        selected_path = os.path.join(
            reports_dir, f"{run_date}-{ticker_upper}-analysis-v{next_version}.md"
        )

    return {
        "ticker": ticker_upper,
        "workdir": root,
        "reports_dir": reports_dir,
        "base_output_file": base_path,
        "selected_output_file": selected_path,
        "selected_versioning_mode": selected_mode,
        "requires_user_choice": requires_user_choice,
        "history_files": history_files,
        "legacy_files": legacy_files,
        "history_limit": history_limit,
        "security_scope": "working_directory_only",
    }


def migrate_files(workdir: str, files: List[str]) -> Dict[str, object]:
    root = os.path.abspath(workdir)
    reports_dir = canonical_reports_dir(root)
    os.makedirs(reports_dir, exist_ok=True)

    moved = []
    skipped = []

    for raw_path in files:
        src = os.path.abspath(raw_path)
        if not is_within_workdir(src, root):
            skipped.append({"file": src, "reason": "outside_workdir"})
            continue
        if not os.path.isfile(src):
            skipped.append({"file": src, "reason": "not_file"})
            continue
        if os.path.islink(src):
            skipped.append({"file": src, "reason": "symlink_not_allowed"})
            continue
        if not FILENAME_RE.match(os.path.basename(src)):
            skipped.append({"file": src, "reason": "filename_not_supported"})
            continue

        dst = os.path.join(reports_dir, os.path.basename(src))
        if os.path.abspath(src) == os.path.abspath(dst):
            skipped.append({"file": src, "reason": "already_in_reports_dir"})
            continue

        if os.path.exists(dst):
            # Keep migration deterministic and non-destructive.
            skipped.append({"file": src, "reason": "target_exists"})
            continue

        try:
            shutil.move(src, dst)
        except OSError as exc:
            skipped.append({"file": src, "reason": f"move_failed:{exc}"})
            continue

        moved.append({"from": src, "to": dst})

    return {
        "reports_dir": reports_dir,
        "moved": moved,
        "skipped": skipped,
        "security_scope": "working_directory_only",
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage report paths and migrations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Plan output path and history usage.")
    plan_parser.add_argument("--workdir", default=os.getcwd())
    plan_parser.add_argument("--ticker", required=True)
    plan_parser.add_argument("--run-date", default=date.today().isoformat())
    plan_parser.add_argument(
        "--versioning",
        choices=["auto", "overwrite", "new_version"],
        default="auto",
    )
    plan_parser.add_argument("--unattended", action="store_true")
    plan_parser.add_argument("--history-limit", type=int, default=5)

    migrate_parser = subparsers.add_parser(
        "migrate", help="Move legacy report files into canonical reports directory."
    )
    migrate_parser.add_argument("--workdir", default=os.getcwd())
    migrate_parser.add_argument("--file", action="append", required=True)

    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "plan":
        result = plan_output(
            workdir=args.workdir,
            ticker=args.ticker,
            run_date=args.run_date,
            versioning=args.versioning,
            unattended=args.unattended,
            history_limit=max(args.history_limit, 1),
        )
    else:
        result = migrate_files(workdir=args.workdir, files=args.file)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
