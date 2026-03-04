#!/usr/bin/env python3
"""Export planner week TOML -> .ics (iCalendar) file.

This is a safe, non-destructive alternative to direct Google Calendar sync.

Only week [[time_blocks]] are exported.

Examples (from workspace root):

  python3 planner/scripts/export_ics.py --week planner/weeks/2026-W10.toml
  python3 planner/scripts/export_ics.py --week planner/weeks/2026-W10.toml --out /tmp/week.ics

Notes:
- Uses timezone from planner/config.toml (default: UTC).
- Writes events in UTC (Z) so imports are timezone-correct.
- Produces stable UIDs so re-importing is less likely to duplicate events (calendar-app dependent).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import re
from pathlib import Path
from zoneinfo import ZoneInfo

import tomllib


VALID_DAYS = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
DAY_OFFSETS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
WEEK_ID_RE = re.compile(r"^\d{4}-W\d{2}$", re.IGNORECASE)


def load_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def week_id_from_path(week_path: Path) -> str:
    base = week_path.name
    if base.lower().endswith(".toml"):
        base = base[:-5]
    return base


def parse_iso_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def parse_hhmm(s: str) -> tuple[int, int]:
    hh, mm = s.split(":")
    return int(hh), int(mm)


def to_utc_z(d: dt.datetime) -> str:
    # RFC5545 UTC format: YYYYMMDDTHHMMSSZ
    return d.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ics_escape(text: str) -> str:
    # RFC5545 value escaping for TEXT
    return (
        text.replace("\\", "\\\\")
        .replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def fold_ics_line(line: str, limit: int = 75) -> str:
    # Simple line folding at ~75 characters (not octets). Good enough for ASCII-heavy content.
    if len(line) <= limit:
        return line
    parts = [line[:limit]]
    rest = line[limit:]
    while rest:
        parts.append(" " + rest[: limit - 1])
        rest = rest[limit - 1 :]
    return "\r\n".join(parts)


def stable_uid(marker_prefix: str, week_id: str, block_id: str) -> str:
    raw = f"{marker_prefix}|{week_id}|{block_id}".encode("utf-8")
    h = hashlib.sha1(raw).hexdigest()[:16]
    return f"{marker_prefix}-{h}@weekly-planner.local"


def build_events(config: dict, week: dict, week_id: str) -> list[dict]:
    tz_name = str(config.get("timezone") or "UTC")
    tz = ZoneInfo(tz_name)

    marker_prefix = "planner"
    sync_cfg = config.get("sync")
    if isinstance(sync_cfg, dict):
        marker_prefix = str(sync_cfg.get("marker_prefix") or marker_prefix)

    modes = config.get("modes") if isinstance(config.get("modes"), dict) else {}

    week_start = parse_iso_date(str(week.get("week_start")))
    blocks = week.get("time_blocks", []) or []
    if not isinstance(blocks, list):
        raise SystemExit("Week file: expected [[time_blocks]] array")

    events: list[dict] = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        block_id = str(b.get("id") or "").strip()
        day = str(b.get("day") or "").strip()
        mode = str(b.get("mode") or "").strip()
        start_str = str(b.get("start") or "").strip()
        minutes = b.get("minutes")

        if not block_id or day not in VALID_DAYS or not start_str or not isinstance(minutes, int):
            continue

        hh, mm = parse_hhmm(start_str)
        start_local = dt.datetime.combine(
            week_start + dt.timedelta(days=DAY_OFFSETS[day]),
            dt.time(hour=hh, minute=mm),
            tzinfo=tz,
        )
        end_local = start_local + dt.timedelta(minutes=int(minutes))

        title = str(b.get("title") or "").strip()
        mode_label = str((modes.get(mode) or {}).get("label") or mode)
        summary = title if title else mode_label
        if title and mode:
            summary = f"{title} ({mode_label})"

        notes = str(b.get("notes") or "").strip()

        desc_lines = [
            f"{marker_prefix}_week={week_id}",
            f"{marker_prefix}_block_id={block_id}",
        ]
        if notes:
            desc_lines.append("")
            desc_lines.append(notes)

        events.append(
            {
                "uid": stable_uid(marker_prefix, week_id, block_id),
                "summary": summary,
                "start_utc": to_utc_z(start_local),
                "end_utc": to_utc_z(end_local),
                "description": "\n".join(desc_lines),
            }
        )

    return events


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planner", default="./planner", help="Planner directory (default: ./planner)")
    ap.add_argument("--week", required=True, help="Week TOML file (e.g. planner/weeks/2026-W10.toml)")
    ap.add_argument("--out", default=None, help="Output .ics path (default: alongside week file)")
    args = ap.parse_args()

    planner_dir = Path(args.planner).expanduser().resolve()
    config_path = planner_dir / "config.toml"

    week_path = Path(args.week).expanduser().resolve()
    if not week_path.exists():
        raise SystemExit(f"Week file not found: {week_path}")

    week_id = week_id_from_path(week_path)
    if not WEEK_ID_RE.match(week_id):
        # still allow export, but warn
        print(f"Warning: week id {week_id!r} does not match YYYY-Www", flush=True)

    config = {}
    if config_path.exists():
        config = load_toml(config_path)

    week = load_toml(week_path)

    events = build_events(config, week, week_id)

    out_path = Path(args.out).expanduser().resolve() if args.out else week_path.with_suffix(".ics")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    now_utc = dt.datetime.now(dt.timezone.utc)
    lines: list[str] = []
    lines.append("BEGIN:VCALENDAR")
    lines.append("VERSION:2.0")
    lines.append("CALSCALE:GREGORIAN")
    lines.append("PRODID:-//weekly-planner//EN")
    # Optional cosmetic name
    export_cfg = config.get("export") if isinstance(config.get("export"), dict) else {}
    calname = str((export_cfg or {}).get("ics_calendar_name") or "Weekly Planner")
    lines.append(f"X-WR-CALNAME:{ics_escape(calname)}")

    for ev in events:
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{ev['uid']}")
        lines.append(f"DTSTAMP:{to_utc_z(now_utc)}")
        lines.append(f"SUMMARY:{ics_escape(ev['summary'])}")
        lines.append(f"DTSTART:{ev['start_utc']}")
        lines.append(f"DTEND:{ev['end_utc']}")
        lines.append("STATUS:CONFIRMED")
        lines.append("TRANSP:OPAQUE")
        lines.append(f"DESCRIPTION:{ics_escape(ev['description'])}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")

    # Fold + CRLF
    out_text = "\r\n".join(fold_ics_line(x) for x in lines) + "\r\n"
    out_path.write_text(out_text, encoding="utf-8")

    print(f"Wrote: {out_path} ({len(events)} event(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
