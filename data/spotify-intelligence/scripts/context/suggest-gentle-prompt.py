#!/usr/bin/env python3
import os, sqlite3, datetime, json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def parse_iso(s):
    if not s:
        return None
    s = str(s)
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


def get_policy(conn, key, default):
    r = conn.execute("SELECT value FROM context_prompt_policy WHERE key=?", (key,)).fetchone()
    return r[0] if r and r[0] else default


def main():
    conn = sqlite3.connect(DB)
    try:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS context_prompt_log(id INTEGER PRIMARY KEY AUTOINCREMENT,prompted_at TEXT NOT NULL,track_id TEXT,reason TEXT);
        CREATE TABLE IF NOT EXISTS context_prompt_policy(key TEXT PRIMARY KEY,value TEXT,updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS track_context_events(id INTEGER PRIMARY KEY AUTOINCREMENT,track_id TEXT NOT NULL,mood TEXT,intent TEXT,note TEXT,triggered_by TEXT,confidence REAL,happened_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS tracks(track_id TEXT PRIMARY KEY,name TEXT,artists TEXT,updated_at TEXT);
        CREATE TABLE IF NOT EXISTS context_prompt_suppression(track_id TEXT PRIMARY KEY,suppressed INTEGER NOT NULL DEFAULT 1,reason TEXT,updated_at TEXT NOT NULL);
        """)

        min_minutes = int(get_policy(conn, "min_minutes_between_prompts", "90"))
        max_per_day = int(get_policy(conn, "max_prompts_per_day", "4"))

        last = conn.execute("SELECT prompted_at FROM context_prompt_log ORDER BY id DESC LIMIT 1").fetchone()
        if last:
            dt = parse_iso(last[0])
            if dt and (now_utc() - dt).total_seconds() < min_minutes * 60:
                print(json.dumps({"ok": True, "shouldPrompt": False, "reason": "cooldown"}))
                return

        day_start = now_utc().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_count = conn.execute("SELECT COUNT(*) FROM context_prompt_log WHERE prompted_at >= ?", (day_start,)).fetchone()[0]
        if day_count >= max_per_day:
            print(json.dumps({"ok": True, "shouldPrompt": False, "reason": "daily_limit"}))
            return

        row = conn.execute(
            """
            SELECT t.track_id, t.name, t.artists
            FROM tracks t
            LEFT JOIN track_context_events c ON c.track_id = t.track_id
            LEFT JOIN context_prompt_suppression s ON s.track_id = t.track_id
            WHERE COALESCE(s.suppressed,0) = 0
               OR s.track_id IS NULL
            ORDER BY c.happened_at IS NOT NULL, c.happened_at ASC, t.updated_at DESC
            LIMIT 1
            """
        ).fetchone()
        if not row:
            print(json.dumps({"ok": True, "shouldPrompt": False, "reason": "no_track"}))
            return

        track_id, name, artists = row
        question = f"Kurze Frage zu '{name}' von {artists}: Warum hÃ¶rst du den gerade â€“ Fokus, Energie, Nostalgie oder was anderes?"
        print(json.dumps({"ok": True, "shouldPrompt": True, "trackId": track_id, "question": question}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()



