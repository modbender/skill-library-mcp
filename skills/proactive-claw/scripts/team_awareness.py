#!/usr/bin/env python3
"""
team_awareness.py — Opt-in cross-calendar coordination for team members.

Lets users register team members' calendars (with their permission) and
surfaces availability conflicts, shared events, and coordination suggestions.
All data sharing is explicitly opt-in and stored locally.

Usage:
  python3 team_awareness.py --add-member "alice@example.com" "Alice"
  python3 team_awareness.py --remove-member "alice@example.com"
  python3 team_awareness.py --list-members
  python3 team_awareness.py --shared-events "this week"
  python3 team_awareness.py --availability "this week"       # find slots everyone is free
  python3 team_awareness.py --meeting-time "Sprint Review" --attendees "alice,bob"
  python3 team_awareness.py --sync                           # refresh member calendar cache
"""
from __future__ import annotations  # PEP 563 — required for Python 3.8 compat with dict[]/list[]/str|None hints

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
sys.path.insert(0, str(SKILL_DIR / "scripts"))

DB_FILE = SKILL_DIR / "memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT DEFAULT '',
    calendar_id TEXT DEFAULT '',
    opted_in INTEGER DEFAULT 1,
    added_at TEXT DEFAULT '',
    last_synced TEXT DEFAULT '',
    notes TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS team_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_email TEXT NOT NULL,
    event_id TEXT DEFAULT '',
    event_title TEXT DEFAULT '',
    event_start TEXT DEFAULT '',
    event_end TEXT DEFAULT '',
    is_all_day INTEGER DEFAULT 0,
    synced_at TEXT DEFAULT '',
    UNIQUE(member_email, event_id)
);

CREATE INDEX IF NOT EXISTS idx_te_member ON team_events(member_email);
CREATE INDEX IF NOT EXISTS idx_te_start ON team_events(event_start);
"""


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


# ── Member management ─────────────────────────────────────────────────────────

def add_member(conn: sqlite3.Connection, email: str, name: str,
               calendar_id: str = "") -> dict:
    """Register a team member for cross-calendar awareness."""
    email = email.lower().strip()
    now = datetime.now(timezone.utc).isoformat()
    try:
        conn.execute("""
            INSERT INTO team_members (email, name, calendar_id, opted_in, added_at)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(email) DO UPDATE SET
                name = excluded.name,
                calendar_id = CASE WHEN excluded.calendar_id != '' THEN excluded.calendar_id
                              ELSE team_members.calendar_id END,
                opted_in = 1
        """, (email, name, calendar_id, now))
        conn.commit()
        return {
            "status": "ok",
            "message": f"Added {name or email} to team. Run --sync to fetch their calendar.",
            "email": email,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def remove_member(conn: sqlite3.Connection, email: str) -> dict:
    """Remove a team member and delete their cached calendar data."""
    email = email.lower().strip()
    conn.execute("DELETE FROM team_events WHERE member_email = ?", (email,))
    result = conn.execute("DELETE FROM team_members WHERE email = ?", (email,))
    conn.commit()
    if result.rowcount == 0:
        return {"status": "not_found", "email": email}
    return {"status": "ok", "message": f"Removed {email} and deleted cached events."}


def list_members(conn: sqlite3.Connection) -> dict:
    """Return all registered team members."""
    rows = conn.execute("SELECT * FROM team_members ORDER BY name").fetchall()
    members = []
    for row in rows:
        event_count = conn.execute(
            "SELECT COUNT(*) FROM team_events WHERE member_email = ?",
            (row["email"],)).fetchone()[0]
        members.append({
            "email": row["email"],
            "name": row["name"],
            "opted_in": bool(row["opted_in"]),
            "added_at": row["added_at"][:10] if row["added_at"] else "",
            "last_synced": row["last_synced"][:10] if row["last_synced"] else "never",
            "cached_events": event_count,
        })
    return {"status": "ok", "members": members, "count": len(members)}


# ── Calendar sync ─────────────────────────────────────────────────────────────

def _find_member_calendar_id(backend, email: str) -> str | None:
    """
    Attempt to locate a team member's calendar.
    Works if:
    - They've shared their calendar with the authenticated account
    - Their email matches a calendar ID directly (Google Workspace shared cals)
    """
    try:
        calendars = backend.list_user_calendars()
        email_lower = email.lower()
        for cal in calendars:
            cal_id = (cal.get("id") or "").lower()
            summary = (cal.get("summary") or "").lower()
            if email_lower in cal_id or email_lower in summary:
                return cal["id"]
    except Exception:
        pass
    # Fallback: use email as calendar ID (works for Google Workspace shared calendars)
    return email


def sync_member(conn: sqlite3.Connection, member: sqlite3.Row) -> dict:
    """Sync upcoming events for a single team member."""
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
        email = member["email"]
        cal_id = member["calendar_id"] or _find_member_calendar_id(backend, email) or email

        now = datetime.now(timezone.utc)
        end = now + timedelta(days=14)

        try:
            events = backend.list_events(cal_id, now, end)
        except Exception as e:
            # Member's calendar not accessible — likely not shared
            return {
                "status": "not_accessible",
                "email": email,
                "message": f"Calendar not accessible: {e}. "
                           "Ask {member['name'] or email} to share their calendar with you.",
            }

        now_iso = now.isoformat()
        synced = 0
        for e in events:
            event_id = e.get("id", "")
            title = e.get("summary", "")
            start = (e.get("start") or {}).get("dateTime") or (e.get("start") or {}).get("date", "")
            end_dt = (e.get("end") or {}).get("dateTime") or (e.get("end") or {}).get("date", "")
            is_all_day = int("date" in (e.get("start") or {}) and
                             "dateTime" not in (e.get("start") or {}))
            try:
                conn.execute("""
                    INSERT OR REPLACE INTO team_events
                        (member_email, event_id, event_title, event_start, event_end,
                         is_all_day, synced_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (email, event_id, title, start, end_dt, is_all_day, now_iso))
                synced += 1
            except Exception:
                pass

        # Update last_synced
        conn.execute("UPDATE team_members SET last_synced = ?, calendar_id = ? WHERE email = ?",
                     (now_iso, cal_id, email))
        conn.commit()

        # Clean up old events (older than 2 days)
        cutoff = (now - timedelta(days=2)).isoformat()
        conn.execute("DELETE FROM team_events WHERE member_email = ? AND event_start < ?",
                     (email, cutoff))
        conn.commit()

        return {"status": "ok", "email": email, "synced": synced}
    except Exception as e:
        return {"status": "error", "email": member["email"], "message": str(e)}


def sync_all(conn: sqlite3.Connection) -> dict:
    """Sync all opted-in team members."""
    members = conn.execute(
        "SELECT * FROM team_members WHERE opted_in = 1").fetchall()
    if not members:
        return {"status": "ok", "message": "No team members registered. "
                "Add one with --add-member.", "results": []}
    results = [sync_member(conn, m) for m in members]
    ok = sum(1 for r in results if r.get("status") == "ok")
    return {"status": "ok", "synced": ok, "total": len(results), "results": results}


# ── Analysis ──────────────────────────────────────────────────────────────────

def _parse_window(window_str: str) -> tuple[datetime, datetime]:
    """Simple window parser for common phrases."""
    from cal_editor import parse_nl_window
    result = parse_nl_window(window_str)
    if result:
        return result
    now = datetime.now(timezone.utc)
    return now, now + timedelta(days=7)


def shared_events(conn: sqlite3.Connection, window_str: str = "this week") -> dict:
    """Find events that appear in both the user's calendar and team members' calendars."""
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
        win_start, win_end = _parse_window(window_str)
        user_events = []
        for cal in backend.list_user_calendars():
            try:
                evts = backend.list_events(cal["id"], win_start, win_end)
                user_events.extend(evts)
            except Exception:
                pass
    except Exception as e:
        return {"status": "error", "message": str(e)}

    # Get team events in window
    team_rows = conn.execute("""
        SELECT te.*, tm.name as member_name
        FROM team_events te
        JOIN team_members tm ON te.member_email = tm.email
        WHERE te.event_start >= ? AND te.event_start <= ?
    """, (win_start.isoformat(), win_end.isoformat())).fetchall()

    # Match by title similarity
    shared = []
    for u_event in user_events:
        u_title = (u_event.get("summary") or "").lower().strip()
        if not u_title:
            continue
        for t_row in team_rows:
            t_title = (t_row["event_title"] or "").lower().strip()
            if not t_title:
                continue
            # Simple match: 60%+ word overlap
            u_words = set(u_title.split())
            t_words = set(t_title.split())
            overlap = len(u_words & t_words) / max(len(u_words | t_words), 1)
            if overlap > 0.5 or u_title in t_title or t_title in u_title:
                shared.append({
                    "title": u_event.get("summary"),
                    "start": (u_event.get("start") or {}).get("dateTime", ""),
                    "also_on": t_row["member_name"] or t_row["member_email"],
                })
                break

    return {
        "status": "ok",
        "window": window_str,
        "shared_events": shared,
        "count": len(shared),
    }


def team_availability(conn: sqlite3.Connection,
                       window_str: str = "this week",
                       duration_minutes: int = 60) -> dict:
    """Find time slots when all team members are free."""
    win_start, win_end = _parse_window(window_str)
    members = conn.execute(
        "SELECT * FROM team_members WHERE opted_in = 1").fetchall()
    if not members:
        return {"status": "ok", "message": "No team members registered.", "free_slots": []}

    # Collect all busy times
    all_busy: list[tuple[datetime, datetime]] = []

    # User's own calendar
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
        for cal in backend.list_user_calendars():
            try:
                for e in backend.list_events(cal["id"], win_start, win_end):
                    s = (e.get("start") or {}).get("dateTime")
                    en = (e.get("end") or {}).get("dateTime")
                    if s and en:
                        try:
                            all_busy.append((
                                datetime.fromisoformat(s.replace("Z", "+00:00")),
                                datetime.fromisoformat(en.replace("Z", "+00:00"))))
                        except Exception:
                            pass
            except Exception:
                pass
    except Exception:
        pass

    # Team members' cached events
    team_rows = conn.execute("""
        SELECT event_start, event_end FROM team_events
        WHERE event_start >= ? AND event_start <= ? AND is_all_day = 0
    """, (win_start.isoformat(), win_end.isoformat())).fetchall()

    for row in team_rows:
        try:
            s = datetime.fromisoformat(row["event_start"].replace("Z", "+00:00"))
            e = datetime.fromisoformat(row["event_end"].replace("Z", "+00:00"))
            if s.tzinfo is None:
                s = s.replace(tzinfo=timezone.utc)
            if e.tzinfo is None:
                e = e.replace(tzinfo=timezone.utc)
            all_busy.append((s, e))
        except Exception:
            pass

    # Merge and find gaps (same logic as cal_editor.py)
    all_busy.sort(key=lambda x: x[0])
    merged: list[list[datetime]] = []
    for bs, be in all_busy:
        if merged and bs < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], be)
        else:
            merged.append([bs, be])

    free_slots = []
    cursor = win_start
    if cursor.hour < 8:
        cursor = cursor.replace(hour=8, minute=0, second=0, microsecond=0)

    for bs, be in merged:
        if cursor < bs:
            gap = int((bs - cursor).total_seconds() / 60)
            if gap >= duration_minutes:
                free_slots.append({
                    "start": cursor.isoformat(),
                    "end": (cursor + timedelta(minutes=duration_minutes)).isoformat(),
                    "available_minutes": gap,
                    "team_members": len(members),
                })
        cursor = max(cursor, be)
        biz_end = cursor.replace(hour=18, minute=0, second=0, microsecond=0)
        if cursor >= biz_end:
            next_day = (cursor + timedelta(days=1)).replace(
                hour=8, minute=0, second=0, microsecond=0)
            if next_day < win_end:
                cursor = next_day

    if cursor < win_end:
        gap = int((win_end - cursor).total_seconds() / 60)
        if gap >= duration_minutes:
            free_slots.append({
                "start": cursor.isoformat(),
                "end": (cursor + timedelta(minutes=duration_minutes)).isoformat(),
                "available_minutes": gap,
                "team_members": len(members),
            })

    return {
        "status": "ok",
        "window": window_str,
        "duration_minutes": duration_minutes,
        "team_members": len(members),
        "free_slots": free_slots[:8],
        "total_found": len(free_slots),
    }


def suggest_meeting_time(conn: sqlite3.Connection, title: str,
                          attendee_emails: list[str],
                          duration_minutes: int = 60) -> dict:
    """
    Suggest the best time for a meeting with specific attendees.
    Uses team availability window for the next 5 business days.
    """
    # Filter team members to only the requested attendees
    if not attendee_emails:
        return {"status": "error", "message": "No attendee emails provided."}
    placeholders = ",".join("?" * len(attendee_emails))
    members = conn.execute(
        f"SELECT * FROM team_members WHERE email IN ({placeholders})",
        [e.lower().strip() for e in attendee_emails]).fetchall()

    missing = [e for e in attendee_emails
               if e.lower().strip() not in [m["email"] for m in members]]

    avail = team_availability(conn, "this week", duration_minutes)
    slots = avail.get("free_slots", [])[:3]

    return {
        "status": "ok",
        "meeting_title": title,
        "attendees_found": len(members),
        "attendees_missing": missing,
        "suggested_slots": slots,
        "note": ("Some attendees not in team registry. "
                 "Add them with --add-member and run --sync." if missing else ""),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--add-member", nargs="+", metavar=("EMAIL", "NAME"),
                        help="Add a team member (email and optional name)")
    parser.add_argument("--remove-member", metavar="EMAIL")
    parser.add_argument("--list-members", action="store_true")
    parser.add_argument("--shared-events", metavar="WINDOW", nargs="?", const="this week")
    parser.add_argument("--availability", metavar="WINDOW", nargs="?", const="this week")
    parser.add_argument("--duration", type=int, default=60,
                        help="Duration in minutes for --availability / --meeting-time")
    parser.add_argument("--meeting-time", metavar="TITLE",
                        help="Suggest a meeting time for a title")
    parser.add_argument("--attendees", metavar="EMAILS",
                        help="Comma-separated emails for --meeting-time")
    parser.add_argument("--sync", action="store_true",
                        help="Sync all team member calendars")
    args = parser.parse_args()

    conn = get_db()

    if args.add_member:
        email = args.add_member[0]
        name = " ".join(args.add_member[1:]) if len(args.add_member) > 1 else ""
        print(json.dumps(add_member(conn, email, name), indent=2))
    elif args.remove_member:
        print(json.dumps(remove_member(conn, args.remove_member), indent=2))
    elif args.list_members:
        print(json.dumps(list_members(conn), indent=2))
    elif args.shared_events is not None:
        print(json.dumps(shared_events(conn, args.shared_events or "this week"), indent=2))
    elif args.availability is not None:
        print(json.dumps(team_availability(conn, args.availability or "this week",
                                            args.duration), indent=2))
    elif args.meeting_time:
        attendees = [e.strip() for e in (args.attendees or "").split(",") if e.strip()]
        print(json.dumps(suggest_meeting_time(conn, args.meeting_time, attendees,
                                               args.duration), indent=2))
    elif args.sync:
        print(json.dumps(sync_all(conn), indent=2))
    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
