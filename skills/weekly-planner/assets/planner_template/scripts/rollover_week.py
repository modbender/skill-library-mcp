#!/usr/bin/env python3
"""Create the next week file and roll over unfinished bits from the previous week.

This script is a convenience wrapper around the common workflow:
- Find the most recent week in planner/weeks/
- Create the next ISO week file from runbook blocks
- Carry over unfinished weekly_bits and daily_bits

Examples (from workspace root):

  # Create next week based on the most recent week file
  python3 planner/scripts/rollover_week.py --next

  # Explicitly roll over from a specific week file
  python3 planner/scripts/rollover_week.py --from planner/weeks/2026-W09.toml

  # Override output week-start date (Monday ISO date)
  python3 planner/scripts/rollover_week.py --from planner/weeks/2026-W09.toml --week-start 2026-03-02

Notes:
- Refuses to overwrite an existing week file.
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
WEEK_FILE_RE = re.compile(r"^\d{4}-W\d{2}\.toml$", re.IGNORECASE)


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def parse_iso_date(s: str) -> dt.date:
    try:
        return dt.date.fromisoformat(s)
    except Exception as e:
        raise SystemExit(f"Invalid ISO date: {s!r}") from e


def week_id_from_week_start(week_start: dt.date) -> str:
    iso_year, iso_week, _ = week_start.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def week_id_from_path(p: Path) -> str:
    base = p.name
    if base.lower().endswith(".toml"):
        base = base[:-5]
    return base


def toml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def discover_week_files(weeks_dir: Path) -> list[Path]:
    files: list[Path] = []
    for p in sorted(weeks_dir.glob("*.toml")):
        if p.name == "WEEK_TEMPLATE.toml":
            continue
        if p.name.endswith(".scratch.toml"):
            continue
        if WEEK_FILE_RE.match(p.name):
            files.append(p)
    return files


def latest_week_file(weeks_dir: Path) -> Path | None:
    files = discover_week_files(weeks_dir)
    if not files:
        return None

    def key(p: Path):
        try:
            data = load_toml(p)
            ws = parse_iso_date(str(data.get("week_start") or ""))
            return ws
        except Exception:
            return dt.date.min

    files_sorted = sorted(files, key=key)
    return files_sorted[-1] if files_sorted else None


def carry_note(notes: str, prev_week_id: str) -> str:
    marker = f"Carried over from {prev_week_id}."
    notes = (notes or "").strip()
    if not notes:
        return marker
    if marker.lower() in notes.lower():
        return notes
    return f"{marker} {notes}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner", default="./planner", help="Planner directory (default: ./planner)")
    ap.add_argument("--from", dest="from_week", default=None, help="Previous week TOML path to roll over from")
    ap.add_argument("--next", action="store_true", help="Use the most recent week in planner/weeks/ as the source")
    ap.add_argument("--week-start", default=None, help="Override new week_start (Monday ISO date)")
    ap.add_argument("--week-id", default=None, help="Override output week id (default: computed from week_start ISO week)")
    ap.add_argument("--out", default=None, help="Override output path (default: planner/weeks/<week-id>.toml)")
    args = ap.parse_args()

    planner_dir = Path(args.planner).expanduser().resolve()
    weeks_dir = planner_dir / "weeks"
    runbook_path = planner_dir / "runbook.toml"
    config_path = planner_dir / "config.toml"

    if not weeks_dir.exists():
        raise SystemExit(f"weeks/ directory not found: {weeks_dir}")
    if not runbook_path.exists():
        raise SystemExit(f"runbook.toml not found: {runbook_path}")

    source_week_path: Path | None = None
    if args.from_week:
        source_week_path = Path(args.from_week).expanduser().resolve()
    elif args.next:
        source_week_path = latest_week_file(weeks_dir)

    if not source_week_path or not source_week_path.exists():
        raise SystemExit("Could not determine source week file (use --from or --next).")

    prev_week_id = week_id_from_path(source_week_path)

    prev_week = load_toml(source_week_path)
    prev_week_start = parse_iso_date(str(prev_week.get("week_start") or "").strip())

    new_week_start = parse_iso_date(args.week_start) if args.week_start else (prev_week_start + dt.timedelta(days=7))
    if new_week_start.weekday() != 0:
        print(
            f"Warning: new week_start {new_week_start.isoformat()} is not a Monday (weekday={new_week_start.weekday()}).",
            file=sys.stderr,
        )

    computed_week_id = week_id_from_week_start(new_week_start)
    new_week_id = (args.week_id or computed_week_id).strip()

    out_path = Path(args.out).expanduser().resolve() if args.out else (weeks_dir / f"{new_week_id}.toml")
    if out_path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {out_path}")

    # Load runbook blocks (same shape as new_week.py)
    runbook = load_toml(runbook_path)
    blocks = runbook.get("blocks", [])
    if not isinstance(blocks, list):
        raise SystemExit("runbook.toml: expected [[blocks]] array")

    # Carry over unfinished bits
    carry_weekly: list[dict] = []
    for b in (prev_week.get("weekly_bits") or []):
        if not isinstance(b, dict):
            continue
        status = str(b.get("status") or "todo").strip().lower()
        if status in {"done", "skip"}:
            continue
        carry_weekly.append(b)

    carry_daily: list[dict] = []
    for b in (prev_week.get("daily_bits") or []):
        if not isinstance(b, dict):
            continue
        status = str(b.get("status") or "todo").strip().lower()
        if status in {"done", "skip"}:
            continue
        carry_daily.append(b)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# Rolled over from {prev_week_id} ({source_week_path.name})")
    lines.append(f"week_start = {toml_str(new_week_start.isoformat())}\n")

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

    if carry_weekly:
        lines.append(f"# --- Carried weekly bits from {prev_week_id} ---")
        for b in carry_weekly:
            bid = str(b.get("id") or "").strip()
            text = str(b.get("text") or "").strip()
            est = b.get("est_minutes")
            mode = str(b.get("mode") or "").strip()
            notes = carry_note(str(b.get("notes") or ""), prev_week_id)
            lines.append("[[weekly_bits]]")
            lines.append(f"id = {toml_str(bid)}")
            lines.append(f"text = {toml_str(text)}")
            if isinstance(est, int) and est > 0:
                lines.append(f"est_minutes = {est}")
            if mode:
                lines.append(f"mode = {toml_str(mode)}")
            lines.append('status = "todo"')
            lines.append(f"notes = {toml_str(notes)}\n")

    if carry_daily:
        lines.append(f"# --- Carried daily bits from {prev_week_id} ---")
        for b in carry_daily:
            day = str(b.get("day") or "").strip()
            bid = str(b.get("id") or "").strip()
            text = str(b.get("text") or "").strip()
            est = b.get("est_minutes")
            mode = str(b.get("mode") or "").strip()
            notes = carry_note(str(b.get("notes") or ""), prev_week_id)
            lines.append("[[daily_bits]]")
            lines.append(f"day = {toml_str(day)}")
            lines.append(f"id = {toml_str(bid)}")
            lines.append(f"text = {toml_str(text)}")
            if isinstance(est, int) and est > 0:
                lines.append(f"est_minutes = {est}")
            if mode:
                lines.append(f"mode = {toml_str(mode)}")
            lines.append('status = "todo"')
            lines.append(f"notes = {toml_str(notes)}\n")

    lines.append("# --- End-of-week review ---")
    lines.append("[review]")
    lines.append("score = 0")
    lines.append("wins = []")
    lines.append("fails = []")
    lines.append('what_i_learned = ""')
    lines.append('next_week_focus = ""\n')

    out_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {out_path}")
    print(f"Carried over: {len(carry_weekly)} weekly bit(s), {len(carry_daily)} daily bit(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
