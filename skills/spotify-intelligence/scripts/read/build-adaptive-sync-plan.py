#!/usr/bin/env python3
import os, sqlite3, datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def now_iso():
    return now_utc().isoformat()


def parse_iso(ts):
    if not ts:
        return None
    s = str(ts).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


def age_minutes(dt):
    if not dt:
        return 10**9
    return (now_utc() - dt).total_seconds() / 60.0


def choose_interval(source, base_sec, activity_age_min):
    # Activity-aware intervals
    if source == "currently-playing":
        if activity_age_min <= 20:
            return 8
        if activity_age_min <= 180:
            return 30
        if activity_age_min <= 1440:
            return 180
        return 900  # 15 min when no activity for long time

    if source == "recently-played":
        if activity_age_min <= 60:
            return 120
        if activity_age_min <= 1440:
            return 900
        return 3600  # keep cross-device backfill alive hourly

    if source == "playlist-items":
        if activity_age_min <= 1440:
            return max(base_sec, 3600)
        return max(base_sec, 21600)

    if source in {"playlists", "profile", "top-short", "top-medium", "top-long"}:
        return max(base_sec, 21600)

    return base_sec


def main():
    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS playback_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              event_at TEXT
            );

            CREATE TABLE IF NOT EXISTS read_counters (
              source TEXT NOT NULL,
              entity_type TEXT NOT NULL,
              entity_id TEXT NOT NULL,
              seen_total INTEGER NOT NULL DEFAULT 0,
              first_seen_at TEXT NOT NULL,
              last_seen_at TEXT NOT NULL,
              PRIMARY KEY(source, entity_type, entity_id)
            );

            CREATE TABLE IF NOT EXISTS api_request_metrics (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              requested_at TEXT NOT NULL,
              source TEXT NOT NULL,
              endpoint TEXT NOT NULL,
              page INTEGER,
              limit_value INTEGER,
              offset_value INTEGER,
              request_ms INTEGER,
              payload_bytes INTEGER,
              items_count INTEGER,
              has_next INTEGER,
              status TEXT,
              http_code INTEGER,
              error_message TEXT
            );

            CREATE TABLE IF NOT EXISTS sync_source_strategy (
              source TEXT PRIMARY KEY,
              samples INTEGER NOT NULL DEFAULT 0,
              error_rate REAL NOT NULL DEFAULT 0,
              p90_request_ms INTEGER NOT NULL DEFAULT 0,
              avg_items_count REAL NOT NULL DEFAULT 0,
              avg_payload_bytes REAL NOT NULL DEFAULT 0,
              recommended_interval_sec INTEGER NOT NULL DEFAULT 300,
              updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS adaptive_sync_plan (
              source TEXT PRIMARY KEY,
              activity_ref_at TEXT,
              activity_age_minutes REAL,
              strategy_interval_sec INTEGER,
              adaptive_interval_sec INTEGER,
              reason TEXT,
              updated_at TEXT
            );
            """
        )

        # Last known listening activity from multiple signals
        r1 = conn.execute("SELECT MAX(event_at) FROM playback_events").fetchone()[0]
        r2 = conn.execute("SELECT MAX(last_seen_at) FROM read_counters WHERE entity_type='track'").fetchone()[0]
        r3 = conn.execute("SELECT MAX(requested_at) FROM api_request_metrics WHERE source='currently-playing' AND status='ok' AND items_count > 0").fetchone()[0]
        candidates = [parse_iso(x) for x in [r1, r2, r3] if x]
        activity_dt = max(candidates) if candidates else None
        a_min = age_minutes(activity_dt)
        activity_ref = activity_dt.isoformat() if activity_dt else None

        # merge from measured strategy table
        rows = conn.execute(
            "SELECT source, recommended_interval_sec FROM sync_source_strategy"
        ).fetchall()
        if not rows:
            rows = [
                ("currently-playing", 8),
                ("recently-played", 120),
                ("playlist-items", 1800),
                ("playlists", 1800),
                ("profile", 21600),
                ("top-short", 43200),
                ("top-medium", 86400),
                ("top-long", 172800),
            ]

        for source, base_sec in rows:
            base_sec = int(base_sec or 300)
            adaptive = choose_interval(source, base_sec, a_min)
            reason = f"activity_age_min={a_min:.1f};base={base_sec}"
            conn.execute(
                """
                INSERT INTO adaptive_sync_plan(source, activity_ref_at, activity_age_minutes, strategy_interval_sec,
                                               adaptive_interval_sec, reason, updated_at)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(source) DO UPDATE SET
                  activity_ref_at=excluded.activity_ref_at,
                  activity_age_minutes=excluded.activity_age_minutes,
                  strategy_interval_sec=excluded.strategy_interval_sec,
                  adaptive_interval_sec=excluded.adaptive_interval_sec,
                  reason=excluded.reason,
                  updated_at=excluded.updated_at
                """,
                (source, activity_ref, a_min, base_sec, adaptive, reason, now_iso()),
            )

        conn.commit()
        print("ok")
    finally:
        conn.close()


if __name__ == "__main__":
    main()



