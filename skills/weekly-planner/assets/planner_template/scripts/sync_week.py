#!/usr/bin/env python3
"""Sync planner week TOML -> Google Calendar (via gog).

Safety:
- Only touches events on the configured planner calendar.
- Only manages events that contain our private props (marker_prefix + week/key).
- Default is dry-run; use --apply to make changes.
- Even with --apply, requires calendar.write_enabled = true in config.toml.

Usage:
  python3 planner/scripts/sync_week.py --week planner/weeks/2026-W10.toml           # dry-run
  python3 planner/scripts/sync_week.py --week planner/weeks/2026-W10.toml --apply   # write
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo


DAY_OFFSETS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass(frozen=True)
class DesiredEvent:
    week_id: str
    key: str
    summary: str
    start: dt.datetime
    end: dt.datetime
    description: str


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def sh(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        # Preserve any partial output for debugging.
        if e.output:
            print(e.output, file=sys.stderr)
        raise


def gog_json(args: list[str]) -> object:
    out = sh(["gog", "calendar", *args, "--json", "--results-only"])
    if not out.strip():
        return None
    return json.loads(out)


def week_id_from_path(week_path: Path) -> str:
    base = week_path.name
    if base.lower().endswith(".toml"):
        base = base[:-5]
    return base


def parse_date_iso(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def parse_hhmm(s: str) -> tuple[int, int]:
    hh, mm = s.split(":")
    return int(hh), int(mm)


def rfc3339(d: dt.datetime) -> str:
    # gog expects RFC3339; datetime.isoformat() is OK when tz-aware.
    return d.isoformat(timespec="seconds")


def mode_label(config: dict, mode: str) -> str:
    return (((config.get("modes") or {}).get(mode) or {}).get("label") or mode).strip()


def safe_int(value: object, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def format_minutes(total_minutes: int) -> str:
    total = max(0, int(total_minutes))
    hh, mm = divmod(total, 60)
    if hh and mm:
        return f"{hh}h {mm}m"
    if hh:
        return f"{hh}h"
    return f"{mm}m"


def discover_week_files(weeks_dir: Path) -> list[Path]:
    files: list[Path] = []
    for p in sorted(weeks_dir.glob("*.toml")):
        low = p.name.lower()
        if low == "week_template.toml" or low.endswith(".scratch.toml"):
            continue
        files.append(p)
    return files


def render_week_markdown(config: dict, week_id: str, week: dict) -> str:
    lines: list[str] = []

    lines.append(f"## {week_id}")
    lines.append("")

    week_start = (week.get("week_start") or "").strip()
    if week_start:
        lines.append(f"- week_start: {week_start}")

    goals = week.get("goals") or {}
    primary = (goals.get("primary_outcome") or "").strip()
    maintenance = (goals.get("maintenance_outcome") or "").strip()
    focus_tasks = goals.get("focus_tasks") or []

    if primary or maintenance or focus_tasks:
        lines.append("")
        lines.append("### Goals")
        if primary:
            lines.append(f"- primary_outcome: {primary}")
        if maintenance:
            lines.append(f"- maintenance_outcome: {maintenance}")
        if focus_tasks:
            lines.append("- focus_tasks:")
            for task in focus_tasks:
                lines.append(f"  - {task}")

    time_blocks = week.get("time_blocks") or []
    if time_blocks:
        lines.append("")
        lines.append("### Time blocks")

        def block_sort_key(block: dict) -> tuple[int, int, int, str]:
            day_idx = DAY_OFFSETS.get(block.get("day", ""), 99)
            start_s = str(block.get("start") or "99:99")
            try:
                hh, mm = parse_hhmm(start_s)
            except Exception:
                hh, mm = 99, 99
            return day_idx, hh, mm, str(block.get("id") or "")

        sorted_blocks = sorted(time_blocks, key=block_sort_key)
        for day in DAY_ORDER:
            day_blocks = [b for b in sorted_blocks if b.get("day") == day]
            if not day_blocks:
                continue
            lines.append(f"#### {day}")
            for block in day_blocks:
                mode = str(block.get("mode") or "")
                title = (block.get("title") or "").strip()
                mode_lbl = mode_label(config, mode)
                summary = title if title else mode_lbl
                start_s = str(block.get("start") or "??:??")
                dur = format_minutes(safe_int(block.get("minutes"), 0))
                lines.append(f"- {start_s} ({dur}) — {summary} [{mode}]")
                notes = (block.get("notes") or "").strip()
                if notes:
                    lines.append(f"  - notes: {notes}")

    weekly_bits = week.get("weekly_bits") or []
    if weekly_bits:
        lines.append("")
        lines.append("### Weekly bits")
        for bit in weekly_bits:
            status = str(bit.get("status") or "todo").lower()
            marker = "[x]" if status == "done" else ("[-]" if status == "skip" else "[ ]")
            text = (bit.get("text") or "").strip() or str(bit.get("id") or "(untitled)")
            mode = str(bit.get("mode") or "")
            est = format_minutes(safe_int(bit.get("est_minutes"), 0))
            lines.append(f"- {marker} {text} ({est}, {mode})")
            notes = (bit.get("notes") or "").strip()
            if notes:
                lines.append(f"  - notes: {notes}")

    daily_bits = week.get("daily_bits") or []
    if daily_bits:
        lines.append("")
        lines.append("### Daily bits")
        for day in DAY_ORDER:
            day_bits = [b for b in daily_bits if b.get("day") == day]
            if not day_bits:
                continue
            lines.append(f"#### {day}")
            for bit in day_bits:
                status = str(bit.get("status") or "todo").lower()
                marker = "[x]" if status == "done" else ("[-]" if status == "skip" else "[ ]")
                text = (bit.get("text") or "").strip() or str(bit.get("id") or "(untitled)")
                mode = str(bit.get("mode") or "")
                est = format_minutes(safe_int(bit.get("est_minutes"), 0))
                lines.append(f"- {marker} {text} ({est}, {mode})")
                notes = (bit.get("notes") or "").strip()
                if notes:
                    lines.append(f"  - notes: {notes}")

    review = week.get("review") or {}
    review_score = review.get("score")
    review_wins = review.get("wins") or []
    review_fails = review.get("fails") or []
    review_learned = (review.get("what_i_learned") or "").strip()
    review_next = (review.get("next_week_focus") or "").strip()
    has_review = any(
        [
            review_score not in (None, 0, "0"),
            bool(review_wins),
            bool(review_fails),
            bool(review_learned),
            bool(review_next),
        ]
    )

    if has_review:
        lines.append("")
        lines.append("### Review")
        if review_score is not None:
            lines.append(f"- score: {review_score}/10")
        if review_wins:
            lines.append("- wins:")
            for win in review_wins:
                lines.append(f"  - {win}")
        if review_fails:
            lines.append("- fails:")
            for fail in review_fails:
                lines.append(f"  - {fail}")
        if review_learned:
            lines.append(f"- what_i_learned: {review_learned}")
        if review_next:
            lines.append(f"- next_week_focus: {review_next}")

    lines.append("")
    return "\n".join(lines)


def write_weeks_markdown_index(config: dict, weeks_dir: Path, out_path: Path) -> int:
    week_files = discover_week_files(weeks_dir)

    lines: list[str] = []
    lines.append("# Planner Weeks Index")
    lines.append("")
    lines.append("Auto-generated from planner/weeks/*.toml by sync_week.py. Do not edit manually.")
    lines.append("")

    for week_file in week_files:
        week = load_toml(week_file)
        week_id = week_id_from_path(week_file)
        lines.append(render_week_markdown(config, week_id, week))

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return len(week_files)


def build_desired_events(config: dict, week: dict, week_id: str, marker_prefix: str) -> list[DesiredEvent]:
    tz = ZoneInfo(str(config.get("timezone") or "UTC"))

    week_start = parse_date_iso(week["week_start"])
    mode_cfg = (config.get("modes") or {})

    desired: list[DesiredEvent] = []
    seen_block_ids: set[str] = set()

    for block in week.get("time_blocks", []):
        block_id = (block.get("id") or "").strip()
        if not block_id:
            raise ValueError("Missing time_blocks[].id (required). Use a short mnemonic like 'sage-otter'.")
        if block_id in seen_block_ids:
            raise ValueError(f"Duplicate time_blocks[].id: {block_id!r}")
        seen_block_ids.add(block_id)

        day = block["day"]
        if day not in DAY_OFFSETS:
            raise ValueError(f"Invalid day: {day!r}. Use Mon..Sun")

        mode = block["mode"]
        start_s = block["start"]
        minutes = int(block["minutes"])
        title = (block.get("title") or "").strip()
        notes = (block.get("notes") or "").strip()

        mode_lbl = ((mode_cfg.get(mode) or {}).get("label") or mode).strip()

        d = week_start + dt.timedelta(days=DAY_OFFSETS[day])
        hh, mm = parse_hhmm(start_s)
        start = dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz)
        end = start + dt.timedelta(minutes=minutes)

        # Event title format: put the thing first, mode second.
        # If the title is missing (or matches the mode label), just use the label.
        if (not title) or (title.casefold() == mode_lbl.casefold()):
            summary = mode_lbl
        else:
            summary = f"{title} ({mode})"

        # Stable identifier: moving a block updates the same event.
        key = f"{week_id}|{block_id}"

        prefix = marker_prefix
        desc_lines = [
            f"{prefix}_week={week_id}",
            f"{prefix}_key={key}",
            f"{prefix}_block_id={block_id}",
        ]
        if notes:
            desc_lines += ["", notes]
        description = "\n".join(desc_lines)

        desired.append(DesiredEvent(week_id=week_id, key=key, summary=summary, start=start, end=end, description=description))

    return desired


def fetch_existing(calendar_id: str, week_id: str, start: dt.datetime, end: dt.datetime, marker_prefix: str) -> list[dict]:
    # Filter to only our events for this week.
    res = gog_json(
        [
            "events",
            calendar_id,
            "--from",
            rfc3339(start),
            "--to",
            rfc3339(end),
            "--all-pages",
            "--private-prop-filter",
            f"{marker_prefix}_week={week_id}",
        ]
    )
    if res is None:
        return []
    if isinstance(res, dict) and "events" in res:
        return res["events"]
    if isinstance(res, list):
        return res
    return []


def get_private_props(ev: dict) -> dict:
    return (((ev.get("extendedProperties") or {}).get("private") or {}))


def plan_actions(
    desired: list[DesiredEvent],
    existing: list[dict],
    marker_prefix: str,
) -> tuple[list[DesiredEvent], list[tuple[DesiredEvent, dict]], list[dict]]:
    desired_by_key = {d.key: d for d in desired}

    existing_by_key: dict[str, dict] = {}
    for ev in existing:
        props = get_private_props(ev)
        key = props.get(f"{marker_prefix}_key")
        if key:
            existing_by_key[str(key)] = ev

    to_create: list[DesiredEvent] = []
    to_update: list[tuple[DesiredEvent, dict]] = []
    to_delete: list[dict] = []

    # Create/update
    for key, d in desired_by_key.items():
        ev = existing_by_key.get(key)
        if not ev:
            to_create.append(d)
            continue

        ev_summary = ev.get("summary") or ""
        ev_desc = ev.get("description") or ""
        ev_start = (ev.get("start") or {}).get("dateTime")
        ev_end = (ev.get("end") or {}).get("dateTime")

        changed = False
        if ev_summary != d.summary:
            changed = True
        if (ev_start or "") != rfc3339(d.start):
            changed = True
        if (ev_end or "") != rfc3339(d.end):
            changed = True
        if ev_desc != d.description:
            changed = True

        if changed:
            to_update.append((d, ev))

    # Delete events that exist but are no longer desired
    for key, ev in existing_by_key.items():
        if key not in desired_by_key:
            to_delete.append(ev)

    return to_create, to_update, to_delete


def apply_create(calendar_id: str, d: DesiredEvent, marker_prefix: str) -> dict:
    block_id = d.key.split("|", 1)[1] if "|" in d.key else ""
    return gog_json(
        [
            "create",
            calendar_id,
            "--summary",
            d.summary,
            "--from",
            rfc3339(d.start),
            "--to",
            rfc3339(d.end),
            "--description",
            d.description,
            "--private-prop",
            f"{marker_prefix}_week={d.week_id}",
            "--private-prop",
            f"{marker_prefix}_key={d.key}",
            "--private-prop",
            f"{marker_prefix}_block_id={block_id}",
            "--send-updates",
            "none",
        ]
    )


def apply_update(calendar_id: str, d: DesiredEvent, ev: dict, marker_prefix: str) -> dict:
    ev_id = ev["id"]
    block_id = d.key.split("|", 1)[1] if "|" in d.key else ""
    return gog_json(
        [
            "update",
            calendar_id,
            ev_id,
            "--summary",
            d.summary,
            "--from",
            rfc3339(d.start),
            "--to",
            rfc3339(d.end),
            "--description",
            d.description,
            "--private-prop",
            f"{marker_prefix}_week={d.week_id}",
            "--private-prop",
            f"{marker_prefix}_key={d.key}",
            "--private-prop",
            f"{marker_prefix}_block_id={block_id}",
            "--force",
        ]
    )


def apply_delete(calendar_id: str, ev: dict) -> object:
    return gog_json(["delete", calendar_id, ev["id"], "--force"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", required=True, help="Path to weeks/YYYY-Www.toml")
    ap.add_argument("--planner", default=None, help="Path to planner root (default: parent of this script)")
    ap.add_argument("--config", default=None, help="Path to config.toml (default: <planner>/config.toml)")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    ap.add_argument("--no-index", action="store_true", help="Skip writing planner/weeks/INDEX.md")
    args = ap.parse_args()

    if shutil.which("gog") is None:
        raise SystemExit("gog: command not found. Install/enable the gog CLI (required for calendar sync).")

    week_path = Path(args.week).expanduser().resolve()
    if not week_path.exists():
        raise SystemExit(f"Week file not found: {week_path}")

    script_dir = Path(__file__).resolve().parent
    planner_dir = Path(args.planner).expanduser().resolve() if args.planner else script_dir.parent

    config_path = Path(args.config).expanduser().resolve() if args.config else (planner_dir / "config.toml")
    if not config_path.exists():
        raise SystemExit(f"Config not found: {config_path}")

    config = load_toml(config_path)
    week = load_toml(week_path)

    weeks_dir = week_path.parent
    weeks_index_path = weeks_dir / "INDEX.md"
    if not args.no_index:
        count = write_weeks_markdown_index(config, weeks_dir, weeks_index_path)
    else:
        count = 0

    cal = config.get("calendar") or {}
    calendar_id = cal.get("planner_calendar_id")
    if not calendar_id:
        raise SystemExit("Missing calendar.planner_calendar_id in config.toml")

    write_enabled = bool(cal.get("write_enabled", False))

    sync_cfg = config.get("sync") or {}
    marker_prefix = str(sync_cfg.get("marker_prefix") or "planner").strip()
    if not marker_prefix:
        raise SystemExit("sync.marker_prefix must be a non-empty string")

    week_id = week_id_from_path(week_path)

    desired = build_desired_events(config, week, week_id, marker_prefix)

    tz = ZoneInfo(str(config.get("timezone") or "UTC"))
    week_start = parse_date_iso(week["week_start"])
    range_start = dt.datetime(week_start.year, week_start.month, week_start.day, 0, 0, tzinfo=tz)
    range_end = range_start + dt.timedelta(days=7)

    existing = fetch_existing(calendar_id, week_id, range_start, range_end, marker_prefix)
    to_create, to_update, to_delete = plan_actions(desired, existing, marker_prefix)

    def fmt(d: DesiredEvent) -> str:
        return f"{d.key} | {d.summary} | {d.start.strftime('%a %H:%M')}–{d.end.strftime('%H:%M')}"

    print(f"Week: {week_id}")
    print(f"Calendar: {calendar_id}")
    print(f"Marker prefix: {marker_prefix}")
    print(f"Desired blocks: {len(desired)}")
    print(f"Existing managed events: {len(existing)}")
    if not args.no_index:
        print(f"Weeks index: {weeks_index_path} ({count} week files)")

    print("\nPlan:")
    for d in to_create:
        print("  CREATE", fmt(d))
    for d, ev in to_update:
        print("  UPDATE", fmt(d), f"(id={ev.get('id')})")
    for ev in to_delete:
        props = get_private_props(ev)
        print("  DELETE", props.get(f"{marker_prefix}_key"), f"(id={ev.get('id')})")

    if not args.apply:
        print("\nDry-run only. Re-run with --apply to write changes.")
        return 0

    if not write_enabled:
        raise SystemExit("Refusing to apply changes: calendar.write_enabled is false in config.toml")

    print("\nApplying...")
    for d in to_create:
        apply_create(calendar_id, d, marker_prefix)
    for d, ev in to_update:
        apply_update(calendar_id, d, ev, marker_prefix)
    for ev in to_delete:
        apply_delete(calendar_id, ev)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
