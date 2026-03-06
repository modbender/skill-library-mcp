#!/usr/bin/env python3
"""
link_store.py — Persistent SQLite link graph for the 2-calendar architecture.

Connects user events ↔ action events ↔ relationships.
Stored in proactive_links.db (separate from memory.db outcome data).

Tables:
  user_events      — tracked user calendar events
  action_events    — action calendar entries (reminders, prep, buffer, etc.)
  links            — relationships between user and action events
  suppression      — events the user said "don't ask again"
  sent_actions     — idempotency log for fired actions

Usage:
  python3 link_store.py --status
  python3 link_store.py --missing
  python3 link_store.py --links <user_event_uid>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
LINKS_DB_FILE = SKILL_DIR / "proactive_links.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS user_events (
    user_event_uid TEXT PRIMARY KEY,
    backend TEXT NOT NULL,
    calendar_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    fingerprint TEXT DEFAULT '',
    title TEXT DEFAULT '',
    start_ts INTEGER DEFAULT 0,
    end_ts INTEGER DEFAULT 0,
    last_seen_ts INTEGER DEFAULT 0,
    missing_count INTEGER DEFAULT 0,
    state TEXT DEFAULT 'active'
);
CREATE INDEX IF NOT EXISTS idx_ue_state ON user_events(state);
CREATE INDEX IF NOT EXISTS idx_ue_fingerprint ON user_events(fingerprint);
CREATE INDEX IF NOT EXISTS idx_ue_event_id ON user_events(event_id);

CREATE TABLE IF NOT EXISTS action_events (
    action_event_uid TEXT PRIMARY KEY,
    backend TEXT NOT NULL,
    action_calendar_id TEXT NOT NULL,
    event_id TEXT DEFAULT '',
    action_type TEXT NOT NULL,
    status TEXT DEFAULT 'planned',
    due_ts INTEGER DEFAULT 0,
    start_ts INTEGER DEFAULT 0,
    end_ts INTEGER DEFAULT 0,
    last_fired_ts INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_ae_status ON action_events(status);
CREATE INDEX IF NOT EXISTS idx_ae_due ON action_events(due_ts);

CREATE TABLE IF NOT EXISTS links (
    link_uid TEXT PRIMARY KEY,
    user_event_uid TEXT NOT NULL,
    action_event_uid TEXT NOT NULL,
    relationship TEXT NOT NULL,
    created_ts INTEGER DEFAULT 0,
    FOREIGN KEY (user_event_uid) REFERENCES user_events(user_event_uid),
    FOREIGN KEY (action_event_uid) REFERENCES action_events(action_event_uid)
);
CREATE INDEX IF NOT EXISTS idx_links_user ON links(user_event_uid);
CREATE INDEX IF NOT EXISTS idx_links_action ON links(action_event_uid);

CREATE TABLE IF NOT EXISTS suppression (
    scope TEXT NOT NULL,
    key TEXT NOT NULL,
    created_ts INTEGER DEFAULT 0,
    PRIMARY KEY (scope, key)
);

CREATE TABLE IF NOT EXISTS sent_actions (
    idempotency_key TEXT PRIMARY KEY,
    sent_ts INTEGER DEFAULT 0
);
"""

VALID_USER_STATES = ("active", "missing", "deleted_confirmed", "suppressed")
VALID_ACTION_STATUSES = ("planned", "pending", "paused", "fired", "canceled", "done")
VALID_RELATIONSHIPS = ("reminder_for", "prep_for", "buffer_after", "debrief_for",
                       "followup_for", "confirm_delete_for")


def get_db() -> sqlite3.Connection:
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(LINKS_DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def compute_user_event_uid(backend: str, calendar_id: str, event_id: str) -> str:
    """SHA256 hash of backend + calendar_id + event_id."""
    raw = f"{backend}|{calendar_id}|{event_id}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def compute_fingerprint(title: str, start: str, end: str,
                        attendees: str = "", location: str = "") -> str:
    """SHA256 of normalized event content for move/recreate detection."""
    normalized = f"{title.lower().strip()}|{start}|{end}|{attendees}|{location}"
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


# ─── User Event Functions ─────────────────────────────────────────────────────

def upsert_user_event(conn: sqlite3.Connection, backend: str, calendar_id: str,
                      event_id: str, title: str, start_ts: int, end_ts: int,
                      fingerprint: str = "") -> str:
    """Insert or update a user event. Returns user_event_uid."""
    uid = compute_user_event_uid(backend, calendar_id, event_id)
    now = _now_ts()
    conn.execute("""
        INSERT INTO user_events
            (user_event_uid, backend, calendar_id, event_id, fingerprint,
             title, start_ts, end_ts, last_seen_ts, missing_count, state)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'active')
        ON CONFLICT(user_event_uid) DO UPDATE SET
            fingerprint = excluded.fingerprint,
            title = excluded.title,
            start_ts = excluded.start_ts,
            end_ts = excluded.end_ts,
            last_seen_ts = ?,
            missing_count = 0,
            state = 'active'
    """, (uid, backend, calendar_id, event_id, fingerprint,
          title, start_ts, end_ts, now, now))
    conn.commit()
    return uid


def mark_seen(conn: sqlite3.Connection, user_event_uid: str):
    """Update last_seen timestamp and reset missing count."""
    conn.execute("""
        UPDATE user_events SET last_seen_ts = ?, missing_count = 0, state = 'active'
        WHERE user_event_uid = ?
    """, (_now_ts(), user_event_uid))
    conn.commit()


def mark_missing_and_pause(conn: sqlite3.Connection, user_event_uid: str):
    """Increment missing_count, set state=missing, pause linked actions."""
    conn.execute("""
        UPDATE user_events SET missing_count = missing_count + 1, state = 'missing'
        WHERE user_event_uid = ?
    """, (user_event_uid,))
    pause_linked_actions(conn, user_event_uid)
    conn.commit()


def set_deleted_confirmed(conn: sqlite3.Connection, user_event_uid: str):
    """Mark event as confirmed deleted."""
    conn.execute("""
        UPDATE user_events SET state = 'deleted_confirmed'
        WHERE user_event_uid = ?
    """, (user_event_uid,))
    cancel_linked_actions(conn, user_event_uid)
    conn.commit()


def suppress_event(conn: sqlite3.Connection, user_event_uid: str):
    """Suppress event — never prompt again."""
    conn.execute("""
        UPDATE user_events SET state = 'suppressed'
        WHERE user_event_uid = ?
    """, (user_event_uid,))
    conn.execute("""
        INSERT OR REPLACE INTO suppression (scope, key, created_ts)
        VALUES ('event', ?, ?)
    """, (user_event_uid, _now_ts()))
    cancel_linked_actions(conn, user_event_uid)
    conn.commit()


def find_by_fingerprint(conn: sqlite3.Connection, fingerprint: str,
                        exclude_uid: str = "") -> list:
    """Find user events with matching fingerprint (for move/recreate detection)."""
    rows = conn.execute("""
        SELECT * FROM user_events
        WHERE fingerprint = ? AND user_event_uid != ? AND state = 'active'
    """, (fingerprint, exclude_uid)).fetchall()
    return [dict(r) for r in rows]


def find_by_title_near(conn: sqlite3.Connection, title: str,
                       start_ts: int, tolerance_sec: int = 300) -> list:
    """Find events with same title within tolerance of start time."""
    rows = conn.execute("""
        SELECT * FROM user_events
        WHERE title = ? AND state = 'active'
        AND ABS(start_ts - ?) <= ?
    """, (title, start_ts, tolerance_sec)).fetchall()
    return [dict(r) for r in rows]


# ─── Action Event Functions ───────────────────────────────────────────────────

def create_action_event(conn: sqlite3.Connection, backend: str,
                        action_calendar_id: str, event_id: str,
                        action_type: str, status: str = "planned",
                        due_ts: int = 0, start_ts: int = 0,
                        end_ts: int = 0) -> str:
    """Create a new action event. Returns action_event_uid."""
    uid = str(uuid.uuid4())[:16]
    conn.execute("""
        INSERT INTO action_events
            (action_event_uid, backend, action_calendar_id, event_id,
             action_type, status, due_ts, start_ts, end_ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (uid, backend, action_calendar_id, event_id,
          action_type, status, due_ts, start_ts, end_ts))
    conn.commit()
    return uid


def update_action_status(conn: sqlite3.Connection, action_event_uid: str,
                         status: str):
    """Update status of an action event."""
    updates = {"status": status}
    if status == "fired":
        updates["last_fired_ts"] = _now_ts()
    conn.execute("""
        UPDATE action_events SET status = ?, last_fired_ts = CASE WHEN ? = 'fired' THEN ? ELSE last_fired_ts END
        WHERE action_event_uid = ?
    """, (status, status, _now_ts(), action_event_uid))
    conn.commit()


def get_due_actions(conn: sqlite3.Connection, now_ts: int,
                    lookahead_sec: int = 1200) -> list:
    """Get action events due in [now, now + lookahead]."""
    end_ts = now_ts + lookahead_sec
    rows = conn.execute("""
        SELECT ae.*, l.user_event_uid, l.relationship
        FROM action_events ae
        LEFT JOIN links l ON l.action_event_uid = ae.action_event_uid
        WHERE ae.due_ts >= ? AND ae.due_ts <= ?
        AND ae.status IN ('planned', 'pending')
        ORDER BY ae.due_ts ASC
    """, (now_ts, end_ts)).fetchall()
    return [dict(r) for r in rows]


# ─── Link Functions ───────────────────────────────────────────────────────────

def link_action(conn: sqlite3.Connection, user_event_uid: str,
                action_event_uid: str, relationship: str) -> str:
    """Create a link between user event and action event."""
    link_uid = str(uuid.uuid4())[:16]
    conn.execute("""
        INSERT INTO links (link_uid, user_event_uid, action_event_uid,
                          relationship, created_ts)
        VALUES (?, ?, ?, ?, ?)
    """, (link_uid, user_event_uid, action_event_uid, relationship, _now_ts()))
    conn.commit()
    return link_uid


def get_linked_actions(conn: sqlite3.Connection, user_event_uid: str) -> list:
    """Get all action events linked to a user event."""
    rows = conn.execute("""
        SELECT ae.*, l.relationship, l.link_uid
        FROM action_events ae
        JOIN links l ON l.action_event_uid = ae.action_event_uid
        WHERE l.user_event_uid = ?
    """, (user_event_uid,)).fetchall()
    return [dict(r) for r in rows]


def pause_linked_actions(conn: sqlite3.Connection, user_event_uid: str):
    """Pause all linked actions for a user event."""
    conn.execute("""
        UPDATE action_events SET status = 'paused'
        WHERE action_event_uid IN (
            SELECT action_event_uid FROM links WHERE user_event_uid = ?
        ) AND status IN ('planned', 'pending')
    """, (user_event_uid,))
    conn.commit()


def cancel_linked_actions(conn: sqlite3.Connection, user_event_uid: str):
    """Cancel all linked actions for a user event."""
    conn.execute("""
        UPDATE action_events SET status = 'canceled'
        WHERE action_event_uid IN (
            SELECT action_event_uid FROM links WHERE user_event_uid = ?
        ) AND status NOT IN ('done', 'canceled')
    """, (user_event_uid,))
    conn.commit()


def has_confirm_delete(conn: sqlite3.Connection, user_event_uid: str) -> bool:
    """Check if a confirm_delete action already exists for this user event."""
    row = conn.execute("""
        SELECT 1 FROM action_events ae
        JOIN links l ON l.action_event_uid = ae.action_event_uid
        WHERE l.user_event_uid = ? AND ae.action_type = 'confirm_delete'
        AND ae.status NOT IN ('canceled', 'done')
        LIMIT 1
    """, (user_event_uid,)).fetchone()
    return row is not None


# ─── Suppression Functions ────────────────────────────────────────────────────

def is_suppressed(conn: sqlite3.Connection, user_event_uid: str) -> bool:
    """Check if an event is suppressed."""
    row = conn.execute(
        "SELECT 1 FROM suppression WHERE scope = 'event' AND key = ?",
        (user_event_uid,)
    ).fetchone()
    return row is not None


# ─── Idempotency Functions ────────────────────────────────────────────────────

def record_sent(conn: sqlite3.Connection, idempotency_key: str):
    """Record that an action was sent."""
    conn.execute("""
        INSERT OR IGNORE INTO sent_actions (idempotency_key, sent_ts)
        VALUES (?, ?)
    """, (idempotency_key, _now_ts()))
    conn.commit()


def was_sent(conn: sqlite3.Connection, idempotency_key: str) -> bool:
    """Check if an action was already sent."""
    row = conn.execute(
        "SELECT 1 FROM sent_actions WHERE idempotency_key = ?",
        (idempotency_key,)
    ).fetchone()
    return row is not None


# ─── Query Functions ──────────────────────────────────────────────────────────

def missing_candidates(conn: sqlite3.Connection, threshold_misses: int = 2) -> list:
    """Get events that have been missing for >= threshold consecutive scans."""
    rows = conn.execute("""
        SELECT * FROM user_events
        WHERE state = 'missing' AND missing_count >= ?
    """, (threshold_misses,)).fetchall()
    return [dict(r) for r in rows]


def get_all_active_user_events(conn: sqlite3.Connection) -> list:
    """Get all active user events."""
    rows = conn.execute(
        "SELECT * FROM user_events WHERE state = 'active'"
    ).fetchall()
    return [dict(r) for r in rows]


def get_status_summary(conn: sqlite3.Connection) -> dict:
    """Get summary of link store state."""
    user_counts = {}
    for row in conn.execute(
        "SELECT state, COUNT(*) as cnt FROM user_events GROUP BY state"
    ).fetchall():
        user_counts[row["state"]] = row["cnt"]

    action_counts = {}
    for row in conn.execute(
        "SELECT status, COUNT(*) as cnt FROM action_events GROUP BY status"
    ).fetchall():
        action_counts[row["status"]] = row["cnt"]

    link_count = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    suppressed_count = conn.execute("SELECT COUNT(*) FROM suppression").fetchone()[0]
    sent_count = conn.execute("SELECT COUNT(*) FROM sent_actions").fetchone()[0]

    return {
        "user_events": user_counts,
        "action_events": action_counts,
        "links": link_count,
        "suppressed": suppressed_count,
        "sent_actions": sent_count,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true",
                        help="Show link store status summary")
    parser.add_argument("--missing", action="store_true",
                        help="Show missing user events")
    parser.add_argument("--links", metavar="USER_EVENT_UID",
                        help="Show linked actions for a user event")
    args = parser.parse_args()

    conn = get_db()

    if args.status:
        print(json.dumps(get_status_summary(conn), indent=2))
    elif args.missing:
        candidates = missing_candidates(conn)
        print(json.dumps({"missing_events": candidates}, indent=2))
    elif args.links:
        actions = get_linked_actions(conn, args.links)
        print(json.dumps({"user_event_uid": args.links, "linked_actions": actions}, indent=2))
    else:
        parser.print_help()

    conn.close()


if __name__ == "__main__":
    main()
