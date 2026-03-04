#!/usr/bin/env python3
"""excretion.py - local pee/poop tracker (SQLite)

Usage examples:
  python3 excretion.py init
  python3 excretion.py log pee --start-at "2026-03-01 10:10" --duration-sec 45 --color yellow --pain 0 --notes ""
  python3 excretion.py log poop --start-at "2026-03-01 10:12" --duration-sec 120 --color normal_brown --pain 1 --bristol 4
  python3 excretion.py log attempt --start-at "2026-03-01 10:30" --duration-sec 1200 --pain 2 --intent poop --notes "abdominal cramps, no output"
  python3 excretion.py week
  python3 excretion.py config set poop_remind_hours 24
  python3 excretion.py config get

DB path: ~/.openclaw/excretion/excretion.db
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any

DEFAULT_TZ = "Asia/Shanghai"

PEE_COLORS = {"clear","pale_yellow","yellow","dark_yellow","amber","red","brown","other"}
POOP_COLORS = {"normal_brown","light_brown","yellow","green","black","red","pale","other"}


def db_path() -> Path:
    return Path.home() / ".openclaw" / "excretion" / "excretion.db"


def ensure_db_dir() -> None:
    db_path().parent.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    ensure_db_dir()
    con = sqlite3.connect(db_path())
    con.row_factory = sqlite3.Row
    return con


def init_db(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
          id TEXT PRIMARY KEY,
          type TEXT NOT NULL,
          start_at TEXT NOT NULL,
          duration_sec INTEGER NOT NULL,
          tz TEXT NOT NULL,
          payload_json TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS config (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );
        """
    )
    # default config
    cur.execute("INSERT OR IGNORE INTO config(key,value) VALUES(?,?)", ("poop_remind_hours","24"))
    con.commit()


def parse_dt(s: str) -> str:
    """Return ISO string. Accepts 'YYYY-MM-DD HH:MM' or ISO."""
    s = s.strip()
    try:
        # try ISO
        dt = datetime.fromisoformat(s)
    except ValueError:
        dt = datetime.strptime(s, "%Y-%m-%d %H:%M")
    if dt.tzinfo is None:
        # store naive as local label; keep as ISO without offset
        return dt.isoformat(timespec="seconds")
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def uuid() -> str:
    import uuid as _uuid
    return str(_uuid.uuid4())


def log_event(args: argparse.Namespace) -> None:
    con = connect()
    init_db(con)

    typ = args.kind
    start_at = parse_dt(args.start_at) if args.start_at else now_iso()
    duration = int(args.duration_sec)
    pain = int(args.pain)

    if pain < 0 or pain > 3:
        raise SystemExit("pain must be 0-3")

    payload: Dict[str, Any] = {"pain": pain, "notes": args.notes or ""}

    if typ == "pee":
        color = args.color
        if color not in PEE_COLORS:
            raise SystemExit(f"invalid pee color: {color}")
        payload["color"] = color
    elif typ == "poop":
        color = args.color
        if color not in POOP_COLORS:
            raise SystemExit(f"invalid poop color: {color}")
        payload["color"] = color
        if args.bristol is None:
            raise SystemExit("poop requires --bristol 1-7")
        br = int(args.bristol)
        if br < 1 or br > 7:
            raise SystemExit("bristol must be 1-7")
        payload["bristol"] = br
        if args.blood:
            payload["blood"] = args.blood
    elif typ == "attempt":
        payload["intent"] = getattr(args, "intent", "unknown")
    else:
        raise SystemExit("kind must be pee, poop, or attempt")

    event_id = uuid()
    con.execute(
        "INSERT INTO events(id,type,start_at,duration_sec,tz,payload_json) VALUES(?,?,?,?,?,?)",
        (event_id, typ, start_at, duration, DEFAULT_TZ, json.dumps(payload, ensure_ascii=False)),
    )
    con.commit()
    print(json.dumps({"ok": True, "id": event_id, "type": typ, "start_at": start_at}, ensure_ascii=False))


def get_config(con: sqlite3.Connection) -> Dict[str,str]:
    cur = con.execute("SELECT key,value FROM config")
    return {r["key"]: r["value"] for r in cur.fetchall()}


def set_config(args: argparse.Namespace) -> None:
    con = connect(); init_db(con)
    con.execute("INSERT INTO config(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (args.key, str(args.value)))
    con.commit()
    print(json.dumps({"ok": True, args.key: str(args.value)}, ensure_ascii=False))


def show_config() -> None:
    con = connect(); init_db(con)
    cfg = get_config(con)
    print(json.dumps(cfg, ensure_ascii=False, indent=2))


def week_summary() -> None:
    con = connect(); init_db(con)
    now = datetime.now()
    start = now - timedelta(days=7)
    rows = con.execute("SELECT * FROM events WHERE start_at >= ? ORDER BY start_at ASC", (start.isoformat(timespec='seconds'),)).fetchall()

    pee = 0
    poop = 0
    poop_bristol = {i:0 for i in range(1,8)}
    poop_pain_sum = 0
    poop_pain_n = 0
    pee_night = 0

    poop_times = []

    for r in rows:
        payload = json.loads(r["payload_json"])
        if r["type"] == "pee":
            pee += 1
            # night: 00:00-06:00 local naive
            try:
                dt = datetime.fromisoformat(r["start_at"])
                if 0 <= dt.hour < 6:
                    pee_night += 1
            except Exception:
                pass
        else:
            poop += 1
            br = payload.get("bristol")
            if isinstance(br, int) and 1 <= br <= 7:
                poop_bristol[br] += 1
            p = payload.get("pain")
            if isinstance(p, int):
                poop_pain_sum += p
                poop_pain_n += 1
            try:
                poop_times.append(datetime.fromisoformat(r["start_at"]))
            except Exception:
                pass

    avg_interval_h = None
    if len(poop_times) >= 2:
        intervals = [(poop_times[i]-poop_times[i-1]).total_seconds()/3600.0 for i in range(1,len(poop_times))]
        avg_interval_h = sum(intervals)/len(intervals)

    result = {
        "window_days": 7,
        "pee_count": pee,
        "pee_night_count": pee_night,
        "poop_count": poop,
        "poop_avg_interval_hours": round(avg_interval_h,2) if avg_interval_h is not None else None,
        "poop_bristol_counts": poop_bristol,
        "poop_pain_avg": round(poop_pain_sum/poop_pain_n,2) if poop_pain_n else None,
        "note": "Not medical advice. If blood/severe pain/persistent symptoms, seek professional help."
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    log = sub.add_parser("log")
    log_sub = log.add_subparsers(dest="kind", required=True)

    def add_common(p):
        p.add_argument("--start-at", default=None)
        p.add_argument("--duration-sec", required=True)
        p.add_argument("--pain", required=True)
        p.add_argument("--notes", default="")

    pee_p = log_sub.add_parser("pee")
    add_common(pee_p)
    pee_p.add_argument("--color", required=True)

    poop_p = log_sub.add_parser("poop")
    add_common(poop_p)
    poop_p.add_argument("--color", required=True)
    poop_p.add_argument("--bristol", required=True)
    poop_p.add_argument("--blood", default=None, help="none|bright_red|dark|unknown")

    attempt_p = log_sub.add_parser("attempt")
    add_common(attempt_p)
    attempt_p.add_argument("--intent", default="poop", choices=["poop","pee","unknown"], help="what you were trying to do")

    cfg = sub.add_parser("config")
    cfg_sub = cfg.add_subparsers(dest="cfgcmd", required=True)
    cfg_get = cfg_sub.add_parser("get")
    cfg_set = cfg_sub.add_parser("set")
    cfg_set.add_argument("key")
    cfg_set.add_argument("value")

    sub.add_parser("week")

    args = ap.parse_args()

    if args.cmd == "init":
        con = connect(); init_db(con)
        print(json.dumps({"ok": True, "db": str(db_path())}, ensure_ascii=False))
        return

    if args.cmd == "log":
        log_event(args)
        return

    if args.cmd == "config":
        if args.cfgcmd == "get":
            show_config(); return
        if args.cfgcmd == "set":
            set_config(args); return

    if args.cmd == "week":
        week_summary(); return


if __name__ == "__main__":
    main()
