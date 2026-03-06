#!/usr/bin/env python3
"""Calendar reminder planner (public/sanitized draft).

Reads a user config and produces a JSON plan of reminders to schedule.

- Google events are read via gcalcli (agenda TSV output).
- Optional CalDAV events are read via khal (vdirsyncer mirror).

It does *not* schedule reminders itself.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import subprocess
from zoneinfo import ZoneInfo

DEFAULT_CONFIG = os.path.expanduser("~/.config/openclaw/calendar.json")
DEFAULT_STATE = os.path.expanduser("~/.local/state/openclaw/calendar-reminders-state.json")

TZ_UTC = ZoneInfo("UTC")


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _utcnow() -> dt.datetime:
    return dt.datetime.now(TZ_UTC)


def _iso_z(d: dt.datetime) -> str:
    return d.astimezone(TZ_UTC).isoformat().replace("+00:00", "Z")


def _is_birthday(title: str) -> bool:
    return "birthday" in title.lower()


def _important_all_day(title: str, keywords: list[str]) -> bool:
    t = title.lower()
    return any(k.lower() in t for k in keywords)


def _gcalcli_rows(cfg: dict, day_local: dt.date, tz_local: ZoneInfo) -> list[dict[str, str]]:
    google = cfg.get("google") or {}
    gcalcli = os.path.expanduser(google.get("gcalcliPath") or "gcalcli")

    calendars = google.get("calendars") or []
    if not calendars:
        return []

    # Use local day window, but force gcalcli output parsing stability by running with TZ=UTC.
    start_local = dt.datetime(day_local.year, day_local.month, day_local.day, 0, 0, tzinfo=tz_local)
    end_local = start_local + dt.timedelta(days=1)

    env = dict(os.environ)
    env.setdefault("PYTHONWARNINGS", "ignore::FutureWarning")
    env["TZ"] = "UTC"

    cmd = [
        gcalcli,
        "--nocolor",
        "agenda",
        "--tsv",
        "--details",
        "id",
        "--details",
        "calendar",
    ]
    for c in calendars:
        name = str((c or {}).get("name") or "").strip()
        if name:
            cmd += ["--calendar", name]

    cmd += [
        start_local.isoformat(timespec="minutes"),
        end_local.isoformat(timespec="minutes"),
    ]

    out = subprocess.check_output(cmd, text=True, env=env)
    return list(csv.DictReader(out.splitlines(), delimiter="\t"))


def _khal_rows(cfg: dict, day_local: dt.date, tz_local: ZoneInfo) -> list[dict[str, str]]:
    caldav = cfg.get("caldav") or {}
    if not caldav.get("enabled"):
        return []

    khal = caldav.get("khalBin") or "khal"
    calendars = caldav.get("khalCalendars") or []
    if not calendars:
        return []

    start = day_local.isoformat()
    end = (day_local + dt.timedelta(days=1)).isoformat()

    env = dict(os.environ)
    env["TZ"] = str(cfg.get("timezone") or "Europe/Stockholm")

    fmt = "{uid}\t{start-date}\t{start-time}\t{end-time}\t{title}\t{calendar}"
    cmd = [khal, "list", "--day-format", "", "--format", fmt]
    for c in calendars:
        name = str((c or {}).get("name") or "").strip()
        if name:
            cmd += ["--include-calendar", name]
    cmd += [start, end]

    out = subprocess.check_output(cmd, text=True, env=env)

    rows: list[dict[str, str]] = []
    for line in out.splitlines():
        if "\t" not in line:
            continue
        uid, sdate, stime, etime, title, cal = line.split("\t", 5)
        rows.append(
            {
                "uid": uid.strip(),
                "start_date": sdate.strip(),
                "start_time": stime.strip(),
                "end_time": etime.strip(),
                "title": title.strip(),
                "calendar": cal.strip(),
            }
        )
    return rows


def _labels(cfg: dict) -> dict[str, str]:
    labels: dict[str, str] = {}

    google = cfg.get("google") or {}
    for c in google.get("calendars") or []:
        name = str((c or {}).get("name") or "").strip()
        label = str((c or {}).get("label") or "").strip()
        if name and label:
            labels[name] = label

    caldav = cfg.get("caldav") or {}
    for c in caldav.get("khalCalendars") or []:
        name = str((c or {}).get("name") or "").strip()
        label = str((c or {}).get("label") or "").strip()
        if name and label:
            labels[name] = label

    return labels


def _load_state(path: str) -> dict:
    try:
        return _load_json(path)
    except FileNotFoundError:
        return {"version": 1, "scheduled": {}}


def _state_has(state: dict, key: str, reminder_at_utc: str) -> bool:
    item = (state.get("scheduled") or {}).get(key)
    return bool(item and item.get("reminderAtUtc") == reminder_at_utc)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.environ.get("OPENCLAW_CALENDAR_CONFIG") or DEFAULT_CONFIG)
    ap.add_argument("--state", default=DEFAULT_STATE)
    ap.add_argument("--day", help="Local day YYYY-MM-DD (defaults to today in configured timezone)")
    ap.add_argument("--lead-min", type=int, default=None)
    args = ap.parse_args(argv)

    cfg = _load_json(os.path.expanduser(args.config))

    tz_name = str(cfg.get("timezone") or "Europe/Stockholm")
    tz_local = ZoneInfo(tz_name)

    if args.day:
        day_local = dt.date.fromisoformat(args.day)
    else:
        day_local = dt.datetime.now(tz_local).date()

    reminders_cfg = cfg.get("reminders") or {}
    lead_min = int(args.lead_min if args.lead_min is not None else (reminders_cfg.get("leadMinutes") or 15))

    ignore_birthdays = bool(reminders_cfg.get("ignoreBirthdays", True))
    all_day_cfg = reminders_cfg.get("allDay") or {}
    all_day_time = str(all_day_cfg.get("timeLocal") or "09:00")
    all_day_keywords = list(all_day_cfg.get("remindIfKeywords") or [])

    state = _load_state(os.path.expanduser(args.state))
    now_utc = _utcnow()

    labels = _labels(cfg)

    to_schedule: list[dict] = []
    skipped = {
        "birthdays": 0,
        "all_day_not_important": 0,
        "past": 0,
        "already_scheduled": 0,
        "google_error": 0,
    }

    # Google via gcalcli
    try:
        g_rows = _gcalcli_rows(cfg, day_local, tz_local)
    except subprocess.CalledProcessError as e:
        skipped["google_error"] = 1
        g_rows = []

    for r in g_rows:
        event_id = (r.get("id") or "").strip()
        title = (r.get("title") or "").strip()
        cal = (r.get("calendar") or "").strip()
        start_date = (r.get("start_date") or "").strip()
        start_time = (r.get("start_time") or "").strip()

        if not event_id or not title:
            continue

        if ignore_birthdays and _is_birthday(title):
            skipped["birthdays"] += 1
            continue

        allday = start_time == ""
        if allday:
            if not _important_all_day(title, all_day_keywords):
                skipped["all_day_not_important"] += 1
                continue
            hh, mm = [int(x) for x in all_day_time.split(":", 1)]
            remind_local = dt.datetime(day_local.year, day_local.month, day_local.day, hh, mm, tzinfo=tz_local)
            remind_utc = remind_local.astimezone(TZ_UTC)
            when_txt = "today (all-day)"
        else:
            # gcalcli output is UTC due to env TZ=UTC
            start_utc = dt.datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M").replace(tzinfo=TZ_UTC)
            remind_utc = start_utc - dt.timedelta(minutes=lead_min)
            when_txt = f"today {start_utc.astimezone(tz_local).strftime('%H:%M')}"

        reminder_at_utc = _iso_z(remind_utc)
        key = f"google:{event_id}"

        if _state_has(state, key, reminder_at_utc):
            skipped["already_scheduled"] += 1
            continue
        if remind_utc <= now_utc:
            skipped["past"] += 1
            continue

        cal_label = labels.get(cal, cal)
        to_schedule.append(
            {
                "source": "google",
                "key": key,
                "eventId": event_id,
                "calendar": cal,
                "calendarLabel": cal_label,
                "title": title,
                "dayLocal": day_local.isoformat(),
                "leadMin": lead_min,
                "reminderAtUtc": reminder_at_utc,
                "message": f"Calendar reminder: {title} — {when_txt} ({cal_label}).",
            }
        )

    # CalDAV via khal
    for r in _khal_rows(cfg, day_local, tz_local):
        uid = (r.get("uid") or "").strip()
        title = (r.get("title") or "").strip()
        cal = (r.get("calendar") or "").strip()
        sdate = (r.get("start_date") or "").strip()
        stime = (r.get("start_time") or "").strip()

        if not uid or not title:
            continue

        if ignore_birthdays and _is_birthday(title):
            skipped["birthdays"] += 1
            continue

        allday = stime == ""
        if allday:
            if not _important_all_day(title, all_day_keywords):
                skipped["all_day_not_important"] += 1
                continue
            hh, mm = [int(x) for x in all_day_time.split(":", 1)]
            remind_local = dt.datetime(day_local.year, day_local.month, day_local.day, hh, mm, tzinfo=tz_local)
            remind_utc = remind_local.astimezone(TZ_UTC)
            when_txt = "today (all-day)"
            start_key = "allday"
        else:
            start_local = dt.datetime.strptime(f"{sdate} {stime}", "%Y-%m-%d %H:%M").replace(tzinfo=tz_local)
            remind_utc = start_local.astimezone(TZ_UTC) - dt.timedelta(minutes=lead_min)
            when_txt = f"today {start_local.strftime('%H:%M')}"
            start_key = f"{sdate}T{stime}"

        reminder_at_utc = _iso_z(remind_utc)
        key = f"caldav:{cal}:{uid}:{start_key}"

        if _state_has(state, key, reminder_at_utc):
            skipped["already_scheduled"] += 1
            continue
        if remind_utc <= now_utc:
            skipped["past"] += 1
            continue

        cal_label = labels.get(cal, cal)
        to_schedule.append(
            {
                "source": "caldav",
                "key": key,
                "eventId": uid,
                "calendar": cal,
                "calendarLabel": cal_label,
                "title": title,
                "dayLocal": day_local.isoformat(),
                "leadMin": lead_min,
                "reminderAtUtc": reminder_at_utc,
                "message": f"Calendar reminder: {title} — {when_txt} ({cal_label}).",
            }
        )

    plan = {
        "dayLocal": day_local.isoformat(),
        "leadMin": lead_min,
        "reminderCount": len(to_schedule),
        "toSchedule": sorted(to_schedule, key=lambda x: x["reminderAtUtc"]),
        "skipped": skipped,
        "configPath": os.path.expanduser(args.config),
        "statePath": os.path.expanduser(args.state),
    }

    print(json.dumps(plan, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
