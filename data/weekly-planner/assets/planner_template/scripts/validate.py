#!/usr/bin/env python3
"""Validate Weekly Planner files (config, inbox, runbook, week plans).

This is a deterministic safety net for agents and humans.

Examples (from workspace root):

  # Validate a specific week
  python3 planner/scripts/validate.py --week planner/weeks/2026-W10.toml

  # Validate config + inbox + runbook + latest week (default behaviour)
  python3 planner/scripts/validate.py

  # Validate all week files
  python3 planner/scripts/validate.py --all-weeks

Exit codes:
  0  OK (no errors; warnings allowed)
  1  Errors found
  2  No errors, but warnings found and --strict was set
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo

import tomllib


VALID_DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
DAY_OFFSETS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
WEEK_FILE_RE = re.compile(r"^\d{4}-W\d{2}\.toml$", re.IGNORECASE)


@dataclass
class Issue:
    level: str  # "ERROR" | "WARN"
    where: str
    message: str


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def parse_iso_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def parse_hhmm_to_minutes(s: str) -> int:
    hh, mm = s.split(":")
    hh_i = int(hh)
    mm_i = int(mm)
    if not (0 <= hh_i <= 23 and 0 <= mm_i <= 59):
        raise ValueError
    return hh_i * 60 + mm_i


def discover_week_files(weeks_dir: Path) -> list[Path]:
    files = []
    for p in sorted(weeks_dir.glob("*.toml")):
        if p.name == "WEEK_TEMPLATE.toml":
            continue
        if p.name.endswith(".scratch.toml"):
            continue
        if WEEK_FILE_RE.match(p.name):
            files.append(p)
    return files


def latest_week_file(weeks_dir: Path) -> Path | None:
    week_files = discover_week_files(weeks_dir)
    if not week_files:
        return None

    def key(p: Path):
        try:
            data = load_toml(p)
            ws = parse_iso_date(str(data.get("week_start") or ""))
            return ws
        except Exception:
            return dt.date.min

    week_files_sorted = sorted(week_files, key=key)
    return week_files_sorted[-1] if week_files_sorted else None


def validate_config(config: dict, path: Path, issues: list[Issue]) -> None:
    where = str(path)
    tz_name = str(config.get("timezone") or "").strip()
    if not tz_name:
        issues.append(Issue("ERROR", where, "Missing timezone (expected IANA name like 'Europe/Berlin')."))
    else:
        try:
            ZoneInfo(tz_name)
        except Exception:
            issues.append(Issue("ERROR", where, f"Invalid timezone: {tz_name!r} (must be an IANA tz name)."))

    day_bounds = config.get("day_bounds") or {}
    if isinstance(day_bounds, dict) and day_bounds:
        for key in ("start", "end"):
            if key in day_bounds:
                try:
                    parse_hhmm_to_minutes(str(day_bounds[key]))
                except Exception:
                    issues.append(Issue("ERROR", where, f"day_bounds.{key} must be HH:MM (got {day_bounds[key]!r})."))

    modes = config.get("modes") or {}
    if modes and not isinstance(modes, dict):
        issues.append(Issue("ERROR", where, "modes must be a table (e.g. [modes.ops])."))
        return

    for mode_key, m in (modes or {}).items():
        if not isinstance(m, dict):
            issues.append(Issue("ERROR", where, f"modes.{mode_key} must be a table."))
            continue
        label = m.get("label")
        if not isinstance(label, str) or not label.strip():
            issues.append(Issue("WARN", where, f"modes.{mode_key}.label is missing/empty (used for calendar titles)."))
        for fld in ("default_block_minutes", "min_block_minutes"):
            if fld in m:
                val = m.get(fld)
                if not isinstance(val, int) or val <= 0:
                    issues.append(Issue("ERROR", where, f"modes.{mode_key}.{fld} must be a positive int."))


def validate_inbox(inbox: dict, config: dict, path: Path, issues: list[Issue]) -> None:
    where = str(path)
    items = inbox.get("items", [])
    if items is None:
        return
    if not isinstance(items, list):
        issues.append(Issue("ERROR", where, "inbox.toml: expected [[items]] array."))
        return

    valid_modes = set((config.get("modes") or {}).keys()) if isinstance(config.get("modes"), dict) else set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            issues.append(Issue("ERROR", where, f"items[{i}] must be a table."))
            continue

        created = str(item.get("created") or "").strip()
        if created:
            try:
                dt.datetime.fromisoformat(created)
            except Exception:
                issues.append(Issue("WARN", where, f"items[{i}].created is not ISO/RFC3339: {created!r}"))
        else:
            issues.append(Issue("WARN", where, f"items[{i}].created is missing (recommended)."))

        text = str(item.get("text") or "").strip()
        if not text:
            issues.append(Issue("ERROR", where, f"items[{i}].text is required."))

        mode = str(item.get("mode") or "").strip()
        if mode and valid_modes and mode not in valid_modes:
            issues.append(Issue("WARN", where, f"items[{i}].mode {mode!r} not found in config modes."))

        est = item.get("est_minutes")
        if est is not None and (not isinstance(est, int) or est <= 0):
            issues.append(Issue("WARN", where, f"items[{i}].est_minutes should be a positive int (got {est!r})."))

        priority = str(item.get("priority") or "").strip().lower()
        if priority and priority not in {"low", "medium", "high"}:
            issues.append(Issue("WARN", where, f"items[{i}].priority should be low|medium|high (got {priority!r})."))

        status = str(item.get("status") or "").strip().lower()
        if status and status not in {"todo", "doing", "done", "dropped"}:
            issues.append(Issue("WARN", where, f"items[{i}].status should be todo|doing|done|dropped (got {status!r})."))


def validate_runbook(runbook: dict, config: dict, path: Path, issues: list[Issue]) -> None:
    where = str(path)
    blocks = runbook.get("blocks", [])
    if blocks is None:
        issues.append(Issue("WARN", where, "runbook.toml has no [[blocks]] (is that intentional?)."))
        return
    if not isinstance(blocks, list):
        issues.append(Issue("ERROR", where, "runbook.toml: expected [[blocks]] array."))
        return

    valid_modes = set((config.get("modes") or {}).keys()) if isinstance(config.get("modes"), dict) else set()

    seen: set[str] = set()
    for i, b in enumerate(blocks):
        if not isinstance(b, dict):
            issues.append(Issue("ERROR", where, f"blocks[{i}] must be a table."))
            continue

        bid = str(b.get("id") or "").strip()
        if not bid:
            issues.append(Issue("ERROR", where, f"blocks[{i}].id is required."))
        elif bid in seen:
            issues.append(Issue("ERROR", where, f"Duplicate blocks[].id: {bid!r}"))
        else:
            seen.add(bid)

        day = b.get("day")
        if day not in VALID_DAYS:
            issues.append(Issue("ERROR", where, f"blocks[{i}].day must be Mon..Sun (got {day!r})."))

        mode = str(b.get("mode") or "").strip()
        if not mode:
            issues.append(Issue("ERROR", where, f"blocks[{i}].mode is required."))
        elif valid_modes and mode not in valid_modes:
            issues.append(Issue("WARN", where, f"blocks[{i}].mode {mode!r} not found in config modes."))

        start = str(b.get("start") or "").strip()
        try:
            parse_hhmm_to_minutes(start)
        except Exception:
            issues.append(Issue("ERROR", where, f"blocks[{i}].start must be HH:MM (got {start!r})."))

        minutes = b.get("minutes")
        if not isinstance(minutes, int) or minutes <= 0:
            issues.append(Issue("ERROR", where, f"blocks[{i}].minutes must be a positive int (got {minutes!r})."))


def _validate_bits_common(
    bits: list[dict],
    where: str,
    config: dict,
    issues: list[Issue],
    *,
    kind: str,
    require_day: bool,
) -> None:
    valid_modes = set((config.get("modes") or {}).keys()) if isinstance(config.get("modes"), dict) else set()
    valid_status_weekly = {"todo", "done", "skip"}
    for i, b in enumerate(bits):
        if not isinstance(b, dict):
            issues.append(Issue("ERROR", where, f"{kind}[{i}] must be a table."))
            continue
        if require_day:
            day = b.get("day")
            if day not in VALID_DAYS:
                issues.append(Issue("ERROR", where, f"{kind}[{i}].day must be Mon..Sun (got {day!r})."))

        bid = str(b.get("id") or "").strip()
        if not bid:
            issues.append(Issue("ERROR", where, f"{kind}[{i}].id is required."))

        text = str(b.get("text") or "").strip()
        if not text:
            issues.append(Issue("ERROR", where, f"{kind}[{i}].text is required."))

        est = b.get("est_minutes")
        if est is not None and (not isinstance(est, int) or est <= 0):
            issues.append(Issue("WARN", where, f"{kind}[{i}].est_minutes should be a positive int (got {est!r})."))

        mode = str(b.get("mode") or "").strip()
        if mode and valid_modes and mode not in valid_modes:
            issues.append(Issue("WARN", where, f"{kind}[{i}].mode {mode!r} not found in config modes."))

        status = str(b.get("status") or "").strip().lower()
        if status and status not in valid_status_weekly:
            issues.append(Issue("WARN", where, f"{kind}[{i}].status should be todo|done|skip (got {status!r})."))


def validate_week(week: dict, config: dict, path: Path, issues: list[Issue]) -> None:
    where = str(path)

    week_start_raw = week.get("week_start")
    if not isinstance(week_start_raw, str) or not week_start_raw.strip():
        issues.append(Issue("ERROR", where, "Missing week_start (expected ISO date string)."))
        return
    try:
        week_start = parse_iso_date(week_start_raw.strip())
    except Exception:
        issues.append(Issue("ERROR", where, f"Invalid week_start: {week_start_raw!r} (expected YYYY-MM-DD)."))
        return

    if week_start.weekday() != 0:
        issues.append(Issue("WARN", where, f"week_start {week_start.isoformat()} is not a Monday."))

    # Time blocks
    blocks = week.get("time_blocks", [])
    if blocks is None:
        blocks = []
    if not isinstance(blocks, list):
        issues.append(Issue("ERROR", where, "time_blocks must be an array of tables ([[time_blocks]])."))
        blocks = []

    day_bounds = config.get("day_bounds") if isinstance(config.get("day_bounds"), dict) else {}
    bound_start = None
    bound_end = None
    if isinstance(day_bounds, dict):
        try:
            if "start" in day_bounds:
                bound_start = parse_hhmm_to_minutes(str(day_bounds["start"]))
            if "end" in day_bounds:
                bound_end = parse_hhmm_to_minutes(str(day_bounds["end"]))
        except Exception:
            # config validator will flag this; ignore here
            pass

    # Collect intervals per day for overlap checks
    intervals_by_day: dict[str, list[tuple[int, int, str]]] = {d: [] for d in VALID_DAYS}

    seen_ids: set[str] = set()
    for i, b in enumerate(blocks):
        if not isinstance(b, dict):
            issues.append(Issue("ERROR", where, f"time_blocks[{i}] must be a table."))
            continue
        bid = str(b.get("id") or "").strip()
        if not bid:
            issues.append(Issue("ERROR", where, f"time_blocks[{i}].id is required."))
        elif bid in seen_ids:
            issues.append(Issue("ERROR", where, f"Duplicate time_blocks[].id: {bid!r}"))
        else:
            seen_ids.add(bid)

        day = b.get("day")
        if day not in VALID_DAYS:
            issues.append(Issue("ERROR", where, f"time_blocks[{i}].day must be Mon..Sun (got {day!r})."))
            continue

        start_raw = str(b.get("start") or "").strip()
        try:
            start_min = parse_hhmm_to_minutes(start_raw)
        except Exception:
            issues.append(Issue("ERROR", where, f"time_blocks[{i}].start must be HH:MM (got {start_raw!r})."))
            continue

        minutes = b.get("minutes")
        if not isinstance(minutes, int) or minutes <= 0:
            issues.append(Issue("ERROR", where, f"time_blocks[{i}].minutes must be a positive int (got {minutes!r})."))
            continue

        end_min = start_min + int(minutes)

        if bound_start is not None and start_min < bound_start:
            issues.append(Issue("WARN", where, f"time_blocks[{i}] starts before day_bounds.start ({start_raw})."))
        if bound_end is not None and end_min > bound_end:
            issues.append(Issue("WARN", where, f"time_blocks[{i}] ends after day_bounds.end ({start_raw}+{minutes}m)."))

        intervals_by_day[str(day)].append((start_min, end_min, bid or f"idx-{i}"))

    # Overlap checks
    for day, intervals in intervals_by_day.items():
        if not intervals:
            continue
        intervals_sorted = sorted(intervals, key=lambda t: t[0])
        prev_s, prev_e, prev_id = intervals_sorted[0]
        for s, e, bid in intervals_sorted[1:]:
            if s < prev_e:
                issues.append(
                    Issue(
                        "ERROR",
                        where,
                        f"Overlapping time blocks on {day}: {prev_id!r} ({prev_s:04d}-{prev_e:04d}) overlaps {bid!r} ({s:04d}-{e:04d}).",
                    )
                )
            if e > prev_e:
                prev_s, prev_e, prev_id = s, e, bid

    # Bits
    weekly_bits = week.get("weekly_bits", [])
    if weekly_bits and not isinstance(weekly_bits, list):
        issues.append(Issue("ERROR", where, "weekly_bits must be an array of tables ([[weekly_bits]])."))
        weekly_bits = []
    daily_bits = week.get("daily_bits", [])
    if daily_bits and not isinstance(daily_bits, list):
        issues.append(Issue("ERROR", where, "daily_bits must be an array of tables ([[daily_bits]])."))
        daily_bits = []

    if isinstance(weekly_bits, list) and weekly_bits:
        _validate_bits_common(weekly_bits, where, config, issues, kind="weekly_bits", require_day=False)
    if isinstance(daily_bits, list) and daily_bits:
        _validate_bits_common(daily_bits, where, config, issues, kind="daily_bits", require_day=True)

    # Review sanity
    review = week.get("review") or {}
    if isinstance(review, dict) and "score" in review:
        score = review.get("score")
        if isinstance(score, int):
            if not (0 <= score <= 10):
                issues.append(Issue("WARN", where, f"review.score should be 0–10 (got {score})."))
        else:
            issues.append(Issue("WARN", where, f"review.score should be an int (got {score!r})."))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner", default="./planner", help="Planner directory (default: ./planner)")
    ap.add_argument("--week", action="append", default=[], help="Week file to validate (repeatable).")
    ap.add_argument("--all-weeks", action="store_true", help="Validate all week files in planner/weeks/")
    ap.add_argument("--inbox", action="store_true", help="Validate inbox.toml")
    ap.add_argument("--runbook", action="store_true", help="Validate runbook.toml")
    ap.add_argument("--config", action="store_true", help="Validate config.toml")
    ap.add_argument("--strict", action="store_true", help="Treat warnings as non-zero exit (code 2).")
    args = ap.parse_args()

    planner_dir = Path(args.planner).expanduser().resolve()
    config_path = planner_dir / "config.toml"
    inbox_path = planner_dir / "inbox.toml"
    runbook_path = planner_dir / "runbook.toml"
    weeks_dir = planner_dir / "weeks"

    issues: list[Issue] = []

    config: dict = {}
    if config_path.exists():
        try:
            config = load_toml(config_path)
        except Exception as e:
            issues.append(Issue("ERROR", str(config_path), f"Failed to parse TOML: {e}"))
            config = {}
    else:
        issues.append(Issue("WARN", str(config_path), "config.toml not found (validation will be limited)."))

    # Decide what to validate if no flags are given.
    any_explicit = bool(args.week) or args.all_weeks or args.inbox or args.runbook or args.config
    do_config = args.config or (not any_explicit)
    do_inbox = args.inbox or (not any_explicit)
    do_runbook = args.runbook or (not any_explicit)

    if do_config and config_path.exists():
        validate_config(config, config_path, issues)

    if do_inbox and inbox_path.exists():
        try:
            inbox = load_toml(inbox_path)
            validate_inbox(inbox, config, inbox_path, issues)
        except Exception as e:
            issues.append(Issue("ERROR", str(inbox_path), f"Failed to parse TOML: {e}"))
    elif do_inbox:
        issues.append(Issue("WARN", str(inbox_path), "inbox.toml not found."))

    if do_runbook and runbook_path.exists():
        try:
            runbook = load_toml(runbook_path)
            validate_runbook(runbook, config, runbook_path, issues)
        except Exception as e:
            issues.append(Issue("ERROR", str(runbook_path), f"Failed to parse TOML: {e}"))
    elif do_runbook:
        issues.append(Issue("WARN", str(runbook_path), "runbook.toml not found."))

    week_paths: list[Path] = []
    for w in args.week:
        week_paths.append(Path(w).expanduser().resolve())

    if args.all_weeks:
        if weeks_dir.exists():
            week_paths.extend(discover_week_files(weeks_dir))
        else:
            issues.append(Issue("WARN", str(weeks_dir), "weeks/ directory not found."))

    if not any_explicit and not week_paths:
        # Default: validate latest week if present.
        if weeks_dir.exists():
            latest = latest_week_file(weeks_dir)
            if latest:
                week_paths.append(latest)

    for wp in week_paths:
        if not wp.exists():
            issues.append(Issue("ERROR", str(wp), "Week file not found."))
            continue
        try:
            week = load_toml(wp)
            validate_week(week, config, wp, issues)
        except Exception as e:
            issues.append(Issue("ERROR", str(wp), f"Failed to parse TOML: {e}"))

    # Print
    errs = [x for x in issues if x.level == "ERROR"]
    warns = [x for x in issues if x.level == "WARN"]

    for x in issues:
        print(f"{x.level}: {x.where}: {x.message}")

    print()
    print(f"Summary: {len(errs)} error(s), {len(warns)} warning(s).")

    if errs:
        return 1
    if args.strict and warns:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
