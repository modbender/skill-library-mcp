#!/usr/bin/env python3
import os, argparse
import os, json
import os, sqlite3
import os, datetime
from pathlib import Path


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def now_unix_ms():
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)


def table_has_column(conn, table_name, column_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(r[1] == column_name for r in rows)


def init_db(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS playback_session_state (
          id INTEGER PRIMARY KEY CHECK (id = 1),
          last_track_id TEXT,
          last_progress_ms INTEGER,
          last_duration_ms INTEGER,
          last_polled_at_ms INTEGER,
          last_is_playing INTEGER
        );

        CREATE TABLE IF NOT EXISTS playback_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          event_at TEXT NOT NULL,
          from_track_id TEXT,
          to_track_id TEXT,
          from_duration_ms INTEGER,
          played_ms_before_switch INTEGER,
          completion_ratio REAL,
          classification TEXT,
          reason TEXT,
          elapsed_raw_ms INTEGER,
          elapsed_used_ms INTEGER
        );

        CREATE TABLE IF NOT EXISTS track_play_stats (
          track_id TEXT PRIMARY KEY,
          observed_switches INTEGER NOT NULL DEFAULT 0,
          observed_skips INTEGER NOT NULL DEFAULT 0,
          observed_completions INTEGER NOT NULL DEFAULT 0,
          observed_uncertain INTEGER NOT NULL DEFAULT 0,
          total_played_ms_before_switch INTEGER NOT NULL DEFAULT 0,
          avg_played_ms_before_switch REAL NOT NULL DEFAULT 0,
          updated_at TEXT
        );
        """
    )

    # Lightweight forward migration for older DBs
    if not table_has_column(conn, "track_play_stats", "observed_uncertain"):
        conn.execute("ALTER TABLE track_play_stats ADD COLUMN observed_uncertain INTEGER NOT NULL DEFAULT 0")
    if not table_has_column(conn, "playback_events", "elapsed_raw_ms"):
        conn.execute("ALTER TABLE playback_events ADD COLUMN elapsed_raw_ms INTEGER")
    if not table_has_column(conn, "playback_events", "elapsed_used_ms"):
        conn.execute("ALTER TABLE playback_events ADD COLUMN elapsed_used_ms INTEGER")


def get_state(conn):
    return conn.execute(
        "SELECT last_track_id,last_progress_ms,last_duration_ms,last_polled_at_ms,last_is_playing FROM playback_session_state WHERE id=1"
    ).fetchone()


def set_state(conn, track_id, progress_ms, duration_ms, polled_at_ms, is_playing):
    conn.execute(
        """
        INSERT INTO playback_session_state(id,last_track_id,last_progress_ms,last_duration_ms,last_polled_at_ms,last_is_playing)
        VALUES (1,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          last_track_id=excluded.last_track_id,
          last_progress_ms=excluded.last_progress_ms,
          last_duration_ms=excluded.last_duration_ms,
          last_polled_at_ms=excluded.last_polled_at_ms,
          last_is_playing=excluded.last_is_playing
        """,
        (track_id, progress_ms, duration_ms, polled_at_ms, is_playing),
    )


def classify_switch(prev_duration_ms, est_played_ms, elapsed_raw_ms, elapsed_used_ms, stale_gap_ms):
    if not prev_duration_ms or prev_duration_ms <= 0:
        return "uncertain", "missing_duration", 0.0

    ratio = est_played_ms / prev_duration_ms

    # stale telemetry gap => low confidence
    if elapsed_raw_ms > stale_gap_ms:
        if ratio >= 0.97:
            return "completed", "natural_end_stale_gap", ratio
        return "uncertain", "stale_gap", ratio

    if ratio >= 0.97:
        return "completed", "natural_end", ratio
    if ratio >= 0.90:
        return "completed", "near_end", ratio

    # Heuristic: if we used 0 elapsed because prev wasn't playing, avoid hard skip label
    if elapsed_used_ms == 0:
        return "uncertain", "paused_or_no_progress", ratio

    return "skip", "likely_manual_or_auto_skip", ratio


def upsert_track_play_stats(conn, track_id, played_ms, classification):
    is_skip = 1 if classification == "skip" else 0
    is_completion = 1 if classification == "completed" else 0
    is_uncertain = 1 if classification == "uncertain" else 0

    conn.execute(
        """
        INSERT INTO track_play_stats(track_id, observed_switches, observed_skips, observed_completions, observed_uncertain,
                                     total_played_ms_before_switch, avg_played_ms_before_switch, updated_at)
        VALUES (?,1,?,?,?, ?,?,?)
        ON CONFLICT(track_id) DO UPDATE SET
          observed_switches = track_play_stats.observed_switches + 1,
          observed_skips = track_play_stats.observed_skips + excluded.observed_skips,
          observed_completions = track_play_stats.observed_completions + excluded.observed_completions,
          observed_uncertain = track_play_stats.observed_uncertain + excluded.observed_uncertain,
          total_played_ms_before_switch = track_play_stats.total_played_ms_before_switch + excluded.total_played_ms_before_switch,
          avg_played_ms_before_switch =
            CAST(track_play_stats.total_played_ms_before_switch + excluded.total_played_ms_before_switch AS REAL)
            / CAST(track_play_stats.observed_switches + 1 AS REAL),
          updated_at = excluded.updated_at
        """,
        (track_id, is_skip, is_completion, is_uncertain, played_ms, float(played_ms), now_iso()),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--payload", required=True)
    ap.add_argument("--max-elapsed-ms", type=int, default=15000, help="Cap elapsed contribution to avoid overestimation.")
    ap.add_argument("--stale-gap-ms", type=int, default=45000, help="Mark events as uncertain when poll gap is too large.")
    args = ap.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8-sig"))

    item = payload.get("item") or {}
    current_track_id = item.get("id")
    progress_ms = payload.get("progress_ms") or 0
    duration_ms = item.get("duration_ms") or 0
    is_playing = 1 if payload.get("is_playing") else 0
    polled_at_ms = now_unix_ms()

    conn = sqlite3.connect(args.db)
    try:
        init_db(conn)
        prev = get_state(conn)

        if prev:
            prev_track_id, prev_progress_ms, prev_duration_ms, prev_polled_at_ms, prev_is_playing = prev
            if prev_track_id and current_track_id and prev_track_id != current_track_id:
                elapsed_raw = max(0, polled_at_ms - (prev_polled_at_ms or polled_at_ms))
                elapsed_used = min(elapsed_raw, args.max_elapsed_ms) if prev_is_playing else 0

                est_played = max(0, (prev_progress_ms or 0) + elapsed_used)
                if prev_duration_ms and prev_duration_ms > 0:
                    est_played = min(est_played, prev_duration_ms)

                classification, reason, ratio = classify_switch(
                    prev_duration_ms=prev_duration_ms,
                    est_played_ms=est_played,
                    elapsed_raw_ms=elapsed_raw,
                    elapsed_used_ms=elapsed_used,
                    stale_gap_ms=args.stale_gap_ms,
                )

                conn.execute(
                    """
                    INSERT INTO playback_events(event_at,from_track_id,to_track_id,from_duration_ms,
                                                played_ms_before_switch,completion_ratio,classification,reason,
                                                elapsed_raw_ms,elapsed_used_ms)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        now_iso(),
                        prev_track_id,
                        current_track_id,
                        prev_duration_ms,
                        int(est_played),
                        ratio,
                        classification,
                        reason,
                        int(elapsed_raw),
                        int(elapsed_used),
                    ),
                )
                upsert_track_play_stats(conn, prev_track_id, int(est_played), classification)

        set_state(conn, current_track_id, progress_ms, duration_ms, polled_at_ms, is_playing)
        conn.commit()
        print(json.dumps({"ok": True, "trackId": current_track_id, "isPlaying": bool(is_playing)}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()


