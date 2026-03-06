#!/usr/bin/env python3
"""
relationship_memory.py — Lightweight CRM built from calendar attendees + outcome notes.

Automatically extracts people from calendar events and correlates them with
outcome sentiment, action items, and frequency of interaction.

Usage:
  python3 relationship_memory.py --ingest          # scan past outcomes + upcoming events
  python3 relationship_memory.py --lookup "Alice"  # find contact + interaction history
  python3 relationship_memory.py --brief "Sprint Review"  # people attending + context
  python3 relationship_memory.py --stale --days 30 # contacts not seen in N days
  python3 relationship_memory.py --top             # most frequent / highest-impact contacts
"""
from __future__ import annotations  # PEP 563 — required for Python 3.8 compat with str|None hints

import argparse
import json
import re
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
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    name TEXT DEFAULT '',
    first_seen TEXT DEFAULT '',
    last_seen TEXT DEFAULT '',
    interaction_count INTEGER DEFAULT 0,
    avg_sentiment REAL DEFAULT 0.0,
    total_action_items INTEGER DEFAULT 0,
    notes TEXT DEFAULT '',
    tags TEXT DEFAULT '',
    updated_at TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS contact_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_email TEXT NOT NULL,
    event_title TEXT DEFAULT '',
    event_datetime TEXT DEFAULT '',
    sentiment TEXT DEFAULT '',
    action_items_count INTEGER DEFAULT 0,
    FOREIGN KEY (contact_email) REFERENCES contacts(email)
);

CREATE INDEX IF NOT EXISTS idx_ce_email ON contact_events(contact_email);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
"""

SENTIMENT_SCORE = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def _normalise_name(raw: str) -> str:
    """Extract display name from 'Name <email>' or return email prefix."""
    m = re.match(r"^(.+?)\s*<[^>]+>$", raw.strip())
    if m:
        return m.group(1).strip().strip('"\'')
    if "@" in raw:
        return raw.split("@")[0].replace(".", " ").replace("_", " ").title()
    return raw.strip()


def _extract_email(raw: str) -> str | None:
    """Extract email address from a string."""
    m = re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", raw)
    return m.group(0).lower() if m else None


def upsert_contact(conn: sqlite3.Connection, email: str, name: str, event_dt: str,
                   sentiment: str = "neutral", action_items_count: int = 0):
    """Insert or update a contact record."""
    email = email.lower().strip()
    now_iso = datetime.now(timezone.utc).isoformat()
    score = SENTIMENT_SCORE.get(sentiment, 0.0)

    existing = conn.execute(
        "SELECT * FROM contacts WHERE email = ?", (email,)).fetchone()

    if existing:
        new_count = existing["interaction_count"] + 1
        # Rolling average sentiment
        new_avg = ((existing["avg_sentiment"] * existing["interaction_count"]) + score) / new_count
        conn.execute("""
            UPDATE contacts SET
                name = CASE WHEN name = '' THEN ? ELSE name END,
                last_seen = MAX(last_seen, ?),
                interaction_count = ?,
                avg_sentiment = ?,
                total_action_items = total_action_items + ?,
                updated_at = ?
            WHERE email = ?
        """, (name, event_dt, new_count, round(new_avg, 3), action_items_count, now_iso, email))
    else:
        conn.execute("""
            INSERT INTO contacts
                (email, name, first_seen, last_seen, interaction_count,
                 avg_sentiment, total_action_items, updated_at)
            VALUES (?, ?, ?, ?, 1, ?, ?, ?)
        """, (email, name, event_dt, event_dt, score, action_items_count, now_iso))

    conn.execute("""
        INSERT INTO contact_events
            (contact_email, event_title, event_datetime, sentiment, action_items_count)
        VALUES (?, ?, ?, ?, ?)
    """, (email, "", event_dt, sentiment, action_items_count))
    conn.commit()


def ingest_from_outcomes(conn: sqlite3.Connection) -> dict:
    """Pull attendee data from outcome JSON files in the outcomes/ directory.

    The DB outcomes table does not store attendees or action_items columns —
    those live in the per-event JSON files written by capture_outcome.py.
    """
    outcomes_dir = SKILL_DIR / "outcomes"
    if not outcomes_dir.exists():
        return {"status": "ok", "ingested": 0}

    ingested = 0
    for json_file in sorted(outcomes_dir.glob("*.json")):
        try:
            data = json.loads(json_file.read_text())
        except Exception:
            continue

        attendees_raw = data.get("attendees") or []
        sentiment = data.get("sentiment") or "neutral"
        event_dt = data.get("event_datetime") or data.get("start") or ""
        event_title = data.get("event_title") or data.get("title") or ""
        action_items = data.get("action_items") or []
        ai_count = len(action_items) if isinstance(action_items, list) else 0

        # Attendees can be a JSON array of strings or dicts, or a comma-separated string
        if isinstance(attendees_raw, str):
            attendee_list = [a.strip() for a in attendees_raw.split(",") if a.strip()]
        else:
            attendee_list = attendees_raw  # already a list

        for raw_attendee in attendee_list:
            if isinstance(raw_attendee, dict):
                email = raw_attendee.get("email", "")
                name = raw_attendee.get("displayName") or _normalise_name(email)
            else:
                email = _extract_email(str(raw_attendee)) or ""
                name = _normalise_name(str(raw_attendee))
            if not email:
                continue
            upsert_contact(conn, email, name, event_dt, sentiment, ai_count)
            # Back-fill event_title on the row just inserted (rowid-based, no ORDER BY needed)
            last_id = conn.execute(
                "SELECT MAX(id) FROM contact_events WHERE contact_email = ? AND event_datetime = ? AND event_title = ''",
                (email.lower().strip(), event_dt)
            ).fetchone()[0]
            if last_id is not None:
                conn.execute(
                    "UPDATE contact_events SET event_title = ? WHERE id = ?",
                    (event_title, last_id)
                )
            conn.commit()
            ingested += 1

    return {"status": "ok", "ingested": ingested}


def ingest_from_calendar(conn: sqlite3.Connection) -> dict:
    """Pull attendees from upcoming calendar events via cal_backend."""
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=30)
        calendars = backend.list_user_calendars()
        ingested = 0
        for cal in calendars:
            try:
                events = backend.list_events(cal["id"], now, end)
                for e in events:
                    attendees = e.get("attendees") or []
                    event_dt = (e.get("start") or {}).get("dateTime", "")
                    for a in attendees:
                        email = a.get("email", "")
                        if not email or "resource.calendar.google.com" in email:
                            continue
                        name = a.get("displayName") or _normalise_name(email)
                        upsert_contact(conn, email, name, event_dt, "neutral", 0)
                        ingested += 1
            except Exception:
                continue
        return {"status": "ok", "ingested": ingested}
    except Exception as e:
        return {"status": "error", "message": str(e), "ingested": 0}


def lookup_contact(conn: sqlite3.Connection, query: str) -> dict:
    """Find a contact by name or email and return interaction history."""
    query_lower = f"%{query.lower()}%"
    rows = conn.execute("""
        SELECT * FROM contacts
        WHERE LOWER(email) LIKE ? OR LOWER(name) LIKE ?
        ORDER BY interaction_count DESC
        LIMIT 5
    """, (query_lower, query_lower)).fetchall()

    if not rows:
        return {"status": "not_found", "query": query}

    results = []
    for row in rows:
        email = row["email"]
        events = conn.execute("""
            SELECT event_title, event_datetime, sentiment, action_items_count
            FROM contact_events
            WHERE contact_email = ?
            ORDER BY event_datetime DESC
            LIMIT 10
        """, (email,)).fetchall()

        # Sentiment label
        avg = row["avg_sentiment"]
        if avg > 0.3:
            sentiment_label = "positive"
        elif avg < -0.3:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"

        results.append({
            "email": email,
            "name": row["name"],
            "first_seen": row["first_seen"],
            "last_seen": row["last_seen"],
            "interaction_count": row["interaction_count"],
            "avg_sentiment": row["avg_sentiment"],
            "sentiment_label": sentiment_label,
            "total_action_items": row["total_action_items"],
            "notes": row["notes"],
            "tags": row["tags"],
            "recent_events": [
                {
                    "title": e["event_title"],
                    "date": e["event_datetime"][:10] if e["event_datetime"] else "",
                    "sentiment": e["sentiment"],
                }
                for e in events
            ],
        })

    return {"status": "ok", "results": results}


def brief_for_event(conn: sqlite3.Connection, event_title: str, days_ahead: int = 7) -> dict:
    """
    Return a contextual brief on attendees for an upcoming event.
    Looks up each attendee in contact history.
    """
    try:
        from cal_backend import CalendarBackend
        backend = CalendarBackend()
        now = datetime.now(timezone.utc)
        end = now + timedelta(days=days_ahead)
        calendars = backend.list_user_calendars()

        target_event = None
        for cal in calendars:
            try:
                events = backend.list_events(cal["id"], now, end)
                for e in events:
                    if event_title.lower() in (e.get("summary") or "").lower():
                        target_event = e
                        break
            except Exception:
                continue
            if target_event:
                break

        if not target_event:
            return {"status": "not_found", "message": f"No upcoming event matching '{event_title}'"}

        attendees = target_event.get("attendees") or []
        briefs = []
        for a in attendees:
            email = a.get("email", "")
            if not email or "resource.calendar.google.com" in email:
                continue
            result = lookup_contact(conn, email)
            if result.get("status") == "ok" and result["results"]:
                c = result["results"][0]
                tip = ""
                if c["interaction_count"] == 0:
                    tip = "First time meeting."
                elif c["sentiment_label"] == "negative":
                    tip = "⚠️ Interactions tend to be challenging — prepare carefully."
                elif c["sentiment_label"] == "positive":
                    tip = "✅ Good working relationship."
                if c["total_action_items"] > 0:
                    tip += f" {c['total_action_items']} open action items historically."
                briefs.append({
                    "name": c["name"] or email,
                    "email": email,
                    "interactions": c["interaction_count"],
                    "sentiment": c["sentiment_label"],
                    "last_seen": c["last_seen"][:10] if c["last_seen"] else "never",
                    "tip": tip.strip(),
                })
            else:
                briefs.append({
                    "name": a.get("displayName") or email.split("@")[0],
                    "email": email,
                    "interactions": 0,
                    "sentiment": "unknown",
                    "last_seen": "never",
                    "tip": "First time meeting.",
                })

        return {
            "status": "ok",
            "event": target_event.get("summary"),
            "event_start": (target_event.get("start") or {}).get("dateTime", ""),
            "attendee_count": len(briefs),
            "briefs": briefs,
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def find_stale_contacts(conn: sqlite3.Connection, days: int = 30) -> dict:
    """Return contacts not seen in the last N days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = conn.execute("""
        SELECT * FROM contacts
        WHERE last_seen < ? AND interaction_count > 0
        ORDER BY last_seen ASC
        LIMIT 20
    """, (cutoff,)).fetchall()

    results = []
    for row in rows:
        days_ago = ""
        if row["last_seen"]:
            try:
                last = datetime.fromisoformat(row["last_seen"].replace("Z", "+00:00"))
                if last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)
                days_ago = str((datetime.now(timezone.utc) - last).days)
            except Exception:
                pass
        results.append({
            "name": row["name"] or row["email"],
            "email": row["email"],
            "last_seen": row["last_seen"][:10] if row["last_seen"] else "",
            "days_since": days_ago,
            "interaction_count": row["interaction_count"],
        })

    return {"status": "ok", "stale_contacts": results, "count": len(results), "days_threshold": days}


def top_contacts(conn: sqlite3.Connection, limit: int = 10) -> dict:
    """Return most frequent and highest-impact contacts."""
    rows = conn.execute("""
        SELECT * FROM contacts
        ORDER BY interaction_count DESC, avg_sentiment DESC
        LIMIT ?
    """, (limit,)).fetchall()

    results = []
    for row in rows:
        avg = row["avg_sentiment"]
        sentiment_label = "positive" if avg > 0.3 else ("negative" if avg < -0.3 else "neutral")
        results.append({
            "name": row["name"] or row["email"],
            "email": row["email"],
            "interactions": row["interaction_count"],
            "avg_sentiment": row["avg_sentiment"],
            "sentiment_label": sentiment_label,
            "last_seen": row["last_seen"][:10] if row["last_seen"] else "",
            "total_action_items": row["total_action_items"],
        })

    return {"status": "ok", "top_contacts": results, "total_contacts": conn.execute(
        "SELECT COUNT(*) FROM contacts").fetchone()[0]}


def add_note(conn: sqlite3.Connection, email: str, note: str) -> dict:
    """Append a manual note to a contact."""
    email = email.lower().strip()
    existing = conn.execute("SELECT notes FROM contacts WHERE email = ?", (email,)).fetchone()
    if not existing:
        return {"status": "not_found", "email": email}
    current = existing["notes"] or ""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_notes = f"{current}\n[{timestamp}] {note}".strip()
    conn.execute("UPDATE contacts SET notes = ?, updated_at = ? WHERE email = ?",
                 (new_notes, datetime.now(timezone.utc).isoformat(), email))
    conn.commit()
    return {"status": "ok", "email": email, "note_added": note}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest", action="store_true",
                        help="Ingest contacts from outcomes + upcoming calendar events")
    parser.add_argument("--lookup", metavar="QUERY",
                        help="Look up a contact by name or email")
    parser.add_argument("--brief", metavar="EVENT_TITLE",
                        help="Attendee brief for an upcoming event")
    parser.add_argument("--stale", action="store_true",
                        help="List contacts not seen recently")
    parser.add_argument("--days", type=int, default=30,
                        help="Days threshold for --stale (default 30)")
    parser.add_argument("--top", action="store_true",
                        help="Top contacts by frequency and impact")
    parser.add_argument("--add-note", nargs=2, metavar=("EMAIL", "NOTE"),
                        help="Add a manual note to a contact")
    args = parser.parse_args()

    conn = get_db()

    if args.ingest:
        out1 = ingest_from_outcomes(conn)
        out2 = ingest_from_calendar(conn)
        print(json.dumps({
            "outcomes_ingested": out1.get("ingested", 0),
            "calendar_ingested": out2.get("ingested", 0),
            "status": "ok",
        }, indent=2))
    elif args.lookup:
        print(json.dumps(lookup_contact(conn, args.lookup), indent=2))
    elif args.brief:
        print(json.dumps(brief_for_event(conn, args.brief), indent=2))
    elif args.stale:
        print(json.dumps(find_stale_contacts(conn, args.days), indent=2))
    elif args.top:
        print(json.dumps(top_contacts(conn), indent=2))
    elif args.add_note:
        print(json.dumps(add_note(conn, args.add_note[0], args.add_note[1]), indent=2))
    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
