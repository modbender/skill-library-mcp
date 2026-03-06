#!/usr/bin/env python3
"""Generate a new week file from runbook blocks.

This script:
- Creates planner/weeks/YYYY-Www.toml
- Copies runbook [[blocks]] into week [[time_blocks]]

Usage (from workspace root):
  python3 planner/scripts/new_week.py --week-start 2026-03-02
  python3 planner/scripts/new_week.py --week-id 2026-W10 --week-start 2026-03-02

Notes:
- Refuses to overwrite existing week files.
- Requires Python 3.11+ (tomllib).
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

import tomllib


VALID_DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
WEEK_ID_RE = re.compile(r"^\d{4}-W\d{2}$")


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def parse_iso_date(s: str) -> dt.date:
    try:
        return dt.date.fromisoformat(s)
    except Exception as e:
        raise SystemExit(f"Invalid ISO date: {s!r}") from e


def parse_hhmm(s: str) -> None:
    try:
        hh, mm = s.split(":")
        hh_i = int(hh)
        mm_i = int(mm)
        if not (0 <= hh_i <= 23 and 0 <= mm_i <= 59):
            raise ValueError
    except Exception as e:
        raise SystemExit(f"Invalid HH:MM time: {s!r}") from e


def week_id_from_week_start(week_start: dt.date) -> str:
    iso_year, iso_week, _iso_weekday = week_start.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def toml_str(s: str) -> str:
    # Minimal TOML string escaping for our use case.
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--week-start",
        required=True,
        help="Monday date (ISO), e.g. 2026-03-02",
    )
    ap.add_argument(
        "--week-id",
        default=None,
        help="Optional, e.g. 2026-W10 (default: computed from --week-start ISO week)",
    )
    ap.add_argument(
        "--planner",
        default=None,
        help="Path to planner root (default: parent of this script)",
    )
    ap.add_argument("--runbook", default=None, help="Override path to runbook.toml")
    ap.add_argument("--config", default=None, help="Override path to config.toml (used for mode validation)")
    ap.add_argument("--out", default=None, help="Override output path (default: <planner>/weeks/<week-id>.toml)")
    args = ap.parse_args()

    week_start = parse_iso_date(args.week_start.strip())
    if week_start.weekday() != 0:
        print(
            f"Warning: week_start {week_start.isoformat()} is not a Monday (weekday={week_start.weekday()}).",
            file=sys.stderr,
        )

    computed_week_id = week_id_from_week_start(week_start)
    week_id = (args.week_id or computed_week_id).strip()

    if args.week_id and args.week_id.strip() != computed_week_id:
        print(
            f"Warning: provided week-id {args.week_id.strip()!r} does not match ISO week for week_start "
            f"({computed_week_id}).",
            file=sys.stderr,
        )
    if not WEEK_ID_RE.match(week_id):
        print(f"Warning: week-id {week_id!r} does not match the usual pattern YYYY-Www", file=sys.stderr)

    script_dir = Path(__file__).resolve().parent
    planner_dir = Path(args.planner).expanduser().resolve() if args.planner else script_dir.parent

    runbook_path = Path(args.runbook).expanduser().resolve() if args.runbook else (planner_dir / "runbook.toml")
    config_path = Path(args.config).expanduser().resolve() if args.config else (planner_dir / "config.toml")

    out_path = Path(args.out).expanduser().resolve() if args.out else (planner_dir / "weeks" / f"{week_id}.toml")

    if out_path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {out_path}")

    if not runbook_path.exists():
        raise SystemExit(f"Runbook not found: {runbook_path}")

    runbook = load_toml(runbook_path)
    blocks = runbook.get("blocks", [])
    if not isinstance(blocks, list):
        raise SystemExit("runbook.toml: expected [[blocks]] array")

    valid_modes: set[str] | None = None
    if config_path.exists():
        cfg = load_toml(config_path)
        modes = cfg.get("modes") or {}
        if isinstance(modes, dict) and modes:
            valid_modes = set(modes.keys())

    seen_ids: set[str] = set()
    for b in blocks:
        bid = str(b.get("id") or "").strip()
        if not bid:
            raise SystemExit("runbook.toml: missing blocks[].id")
        if bid in seen_ids:
            raise SystemExit(f"runbook.toml: duplicate blocks[].id: {bid!r}")
        seen_ids.add(bid)

        day = b.get("day")
        if day not in VALID_DAYS:
            raise SystemExit(f"runbook.toml: invalid day for {bid!r}: {day!r}")

        mode = str(b.get("mode") or "").strip()
        if not mode:
            raise SystemExit(f"runbook.toml: missing mode for {bid!r}")
        if valid_modes is not None and mode not in valid_modes:
            raise SystemExit(
                f"runbook.toml: invalid mode for {bid!r}: {mode!r}. Expected one of: {sorted(valid_modes)}"
            )

        start = str(b.get("start") or "").strip()
        parse_hhmm(start)

        minutes = b.get("minutes")
        if not isinstance(minutes, int) or minutes <= 0:
            raise SystemExit(f"runbook.toml: invalid minutes for {bid!r}: {minutes!r}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Write explicit TOML (hand-friendly).
    lines: list[str] = []
    lines.append(f"week_start = {toml_str(week_start.isoformat())}\n")

    lines.append("[goals]")
    lines.append('primary_outcome = ""')
    lines.append('maintenance_outcome = ""\n')
    lines.append("# Optional: 2–5 focus tasks you keep coming back to all week.")
    lines.append("focus_tasks = []\n")

    lines.append("# Time blocks (published to calendar)")
    lines.append("# id: required, unique within week")
    lines.append("# day: Mon|Tue|Wed|Thu|Fri|Sat|Sun")
    lines.append("# mode: any key defined in config.toml under [modes.*]\n")

    for b in blocks:
        title = str(b.get("title") or "")
        notes = str(b.get("notes") or "")
        lines.append("[[time_blocks]]")
        lines.append(f"id = {toml_str(str(b['id']))}")
        lines.append(f"day = {toml_str(str(b['day']))}")
        lines.append(f"mode = {toml_str(str(b['mode']))}")
        lines.append(f"start = {toml_str(str(b['start']))}")
        lines.append(f"minutes = {int(b['minutes'])}")
        lines.append(f"title = {toml_str(title)}")
        lines.append(f"notes = {toml_str(notes)}\n")

    # Unscheduled bits (commented examples)
    lines.append("# --- Unscheduled bits (no fixed time) ---\n")

    lines.append("# Weekly bits: do sometime this week")
    lines.append("# [[weekly_bits]]")
    lines.append('# id = "pay-bills"')
    lines.append('# text = "Pay bills"')
    lines.append("# est_minutes = 20")
    lines.append('# mode = "ops"')
    lines.append('# status = "todo"   # todo|done|skip')
    lines.append('# notes = ""\n')

    lines.append("# Daily bits: do sometime on a given day")
    lines.append("# [[daily_bits]]")
    lines.append('# day = "Tue"')
    lines.append('# id = "groceries"')
    lines.append('# text = "Buy groceries"')
    lines.append("# est_minutes = 45")
    lines.append('# mode = "ops"')
    lines.append('# status = "todo"')
    lines.append('# notes = ""\n')

    # End-of-week review
    lines.append("# --- End-of-week review ---")
    lines.append("[review]")
    lines.append("score = 0")
    lines.append("wins = []")
    lines.append("fails = []")
    lines.append('what_i_learned = ""')
    lines.append('next_week_focus = ""\n')

    out_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
