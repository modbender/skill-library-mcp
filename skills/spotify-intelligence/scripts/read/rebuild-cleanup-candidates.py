#!/usr/bin/env python3
import os, argparse
import os, sqlite3
import os, datetime


def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)


def now_iso():
    return now_utc().isoformat()


def months_ago(months: int):
    return now_utc() - datetime.timedelta(days=30 * months)


def parse_iso(ts):
    if not ts:
        return None
    ts = str(ts).strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    try:
        dt = datetime.datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


def ensure_tables(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS system_meta (
          key TEXT PRIMARY KEY,
          value TEXT,
          updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS track_decision_metrics (
          track_id TEXT PRIMARY KEY,
          switches INTEGER NOT NULL DEFAULT 0,
          skips INTEGER NOT NULL DEFAULT 0,
          completions INTEGER NOT NULL DEFAULT 0,
          uncertain INTEGER NOT NULL DEFAULT 0,
          skip_rate REAL NOT NULL DEFAULT 0,
          completion_rate REAL NOT NULL DEFAULT 0,
          uncertain_rate REAL NOT NULL DEFAULT 0,
          confidence_score REAL NOT NULL DEFAULT 0,
          updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tracks (
          track_id TEXT PRIMARY KEY,
          name TEXT,
          artists TEXT
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

        CREATE TABLE IF NOT EXISTS track_play_stats (
          track_id TEXT PRIMARY KEY,
          total_played_ms_before_switch INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS playlist_track_membership (
          playlist_id TEXT NOT NULL,
          track_id TEXT NOT NULL,
          first_added_at TEXT,
          currently_present INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(playlist_id, track_id)
        );

        CREATE TABLE IF NOT EXISTS playlist_cleanup_candidates (
          run_id TEXT NOT NULL,
          generated_at TEXT NOT NULL,
          window_months INTEGER NOT NULL,
          window_start TEXT NOT NULL,
          min_confidence REAL NOT NULL,
          min_switches INTEGER NOT NULL,
          min_skip_rate REAL NOT NULL,
          max_completion_rate REAL NOT NULL,
          track_id TEXT NOT NULL,
          track_name TEXT,
          artists TEXT,
          observed_switches INTEGER NOT NULL,
          observed_skips INTEGER NOT NULL,
          observed_completions INTEGER NOT NULL,
          observed_uncertain INTEGER NOT NULL,
          skip_rate REAL NOT NULL,
          completion_rate REAL NOT NULL,
          confidence_score REAL NOT NULL,
          last_seen_at TEXT,
          oldest_playlist_added_at TEXT,
          years_in_playlist REAL,
          playlist_count INTEGER NOT NULL DEFAULT 0,
          total_played_ms INTEGER NOT NULL DEFAULT 0,
          total_played_minutes REAL NOT NULL DEFAULT 0,
          score REAL NOT NULL,
          reason TEXT,
          PRIMARY KEY(run_id, track_id)
        );

        CREATE INDEX IF NOT EXISTS idx_cleanup_candidates_run ON playlist_cleanup_candidates(run_id);
        CREATE INDEX IF NOT EXISTS idx_cleanup_candidates_score ON playlist_cleanup_candidates(score DESC);
        """
    )


def table_has_column(conn, table_name, column_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(r[1] == column_name for r in rows)


def migrate_columns(conn):
    wanted = {
        "oldest_playlist_added_at": "TEXT",
        "years_in_playlist": "REAL",
        "playlist_count": "INTEGER NOT NULL DEFAULT 0",
        "total_played_ms": "INTEGER NOT NULL DEFAULT 0",
        "total_played_minutes": "REAL NOT NULL DEFAULT 0",
    }
    for col, typ in wanted.items():
        if not table_has_column(conn, "playlist_cleanup_candidates", col):
            conn.execute(f"ALTER TABLE playlist_cleanup_candidates ADD COLUMN {col} {typ}")

    if not table_has_column(conn, "tracks", "artists"):
        conn.execute("ALTER TABLE tracks ADD COLUMN artists TEXT")


def set_counting_start_if_missing(conn):
    row = conn.execute("SELECT value FROM system_meta WHERE key='counting_started_at'").fetchone()
    if row and row[0]:
        return row[0]
    ts = now_iso()
    conn.execute(
        "INSERT INTO system_meta(key,value,updated_at) VALUES ('counting_started_at',?,?)",
        (ts, ts),
    )
    return ts


def update_last_cleanup_run(conn, run_id, window_months, window_start):
    ts = now_iso()
    kv = {
        "last_cleanup_run_id": run_id,
        "last_cleanup_window_months": str(window_months),
        "last_cleanup_window_start": window_start,
    }
    for k, v in kv.items():
        conn.execute(
            """
            INSERT INTO system_meta(key,value,updated_at) VALUES (?,?,?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            """,
            (k, v, ts),
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--window-months", type=int, default=6)
    ap.add_argument("--min-confidence", type=float, default=0.45)
    ap.add_argument("--min-switches", type=int, default=4)
    ap.add_argument("--min-skip-rate", type=float, default=0.65)
    ap.add_argument("--max-completion-rate", type=float, default=0.25)
    ap.add_argument("--max-total-played-minutes", type=float, default=20.0)
    ap.add_argument("--min-years-in-playlist", type=float, default=0.5)
    ap.add_argument("--top", type=int, default=200)
    args = ap.parse_args()

    if args.window_months <= 0:
        raise ValueError("--window-months must be > 0")

    window_start = months_ago(args.window_months).isoformat()
    run_id = now_utc().strftime("cleanup_%Y%m%dT%H%M%SZ")

    conn = sqlite3.connect(args.db)
    try:
        ensure_tables(conn)
        migrate_columns(conn)
        counting_started_at = set_counting_start_if_missing(conn)

        rows = conn.execute(
            """
            SELECT
              m.track_id,
              t.name,
              t.artists,
              m.switches,
              m.skips,
              m.completions,
              m.uncertain,
              m.skip_rate,
              m.completion_rate,
              m.confidence_score,
              MAX(rc.last_seen_at) AS rc_last_seen_at,
              MIN(ptm.first_added_at) AS oldest_playlist_added_at,
              COUNT(DISTINCT ptm.playlist_id) AS playlist_count,
              COALESCE(ps.total_played_ms_before_switch, 0) AS total_played_ms
            FROM track_decision_metrics m
            LEFT JOIN tracks t ON t.track_id = m.track_id
            LEFT JOIN read_counters rc ON rc.entity_type = 'track' AND rc.entity_id = m.track_id
            LEFT JOIN playlist_track_membership ptm ON ptm.track_id = m.track_id AND ptm.currently_present = 1
            LEFT JOIN track_play_stats ps ON ps.track_id = m.track_id
            GROUP BY m.track_id, t.name, t.artists, m.switches, m.skips, m.completions, m.uncertain,
                     m.skip_rate, m.completion_rate, m.confidence_score, ps.total_played_ms_before_switch
            HAVING
              m.switches >= ?
              AND m.confidence_score >= ?
              AND m.skip_rate >= ?
              AND m.completion_rate <= ?
              AND (rc_last_seen_at IS NULL OR rc_last_seen_at < ?)
            LIMIT ?
            """,
            (
                args.min_switches,
                args.min_confidence,
                args.min_skip_rate,
                args.max_completion_rate,
                window_start,
                args.top * 5,
            ),
        ).fetchall()

        generated_at = now_iso()
        inserted = 0
        for r in rows:
            (
                track_id,
                track_name,
                artists,
                switches,
                skips,
                completions,
                uncertain,
                skip_rate,
                completion_rate,
                confidence_score,
                last_seen_at,
                oldest_added_at,
                playlist_count,
                total_played_ms,
            ) = r

            total_played_ms = int(total_played_ms or 0)
            total_played_minutes = round(total_played_ms / 60000.0, 3)

            years_in_playlist = 0.0
            if oldest_added_at:
                dt_old = parse_iso(oldest_added_at)
                if dt_old:
                    years_in_playlist = max(0.0, (now_utc() - dt_old).days / 365.25)

            # Apply age/playtime gates for cleanup logic
            if years_in_playlist < args.min_years_in_playlist:
                continue
            if total_played_minutes > args.max_total_played_minutes:
                continue

            score = (
                float(skip_rate)
                * float(confidence_score)
                * min(int(switches), 40)
                * (1.0 + min(years_in_playlist, 5.0) / 5.0)
                * (1.0 if total_played_minutes <= 0 else min(1.0, args.max_total_played_minutes / max(total_played_minutes, 1e-6)))
            )

            reason = (
                f"old_in_playlist={years_in_playlist:.2f}y|"
                f"low_total_play={total_played_minutes:.2f}m|"
                f"skip_rate={skip_rate:.2f}|confidence={confidence_score:.2f}|switches={switches}"
            )

            conn.execute(
                """
                INSERT INTO playlist_cleanup_candidates(
                  run_id, generated_at, window_months, window_start,
                  min_confidence, min_switches, min_skip_rate, max_completion_rate,
                  track_id, track_name, artists,
                  observed_switches, observed_skips, observed_completions, observed_uncertain,
                  skip_rate, completion_rate, confidence_score,
                  last_seen_at, oldest_playlist_added_at, years_in_playlist, playlist_count,
                  total_played_ms, total_played_minutes,
                  score, reason
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    run_id,
                    generated_at,
                    args.window_months,
                    window_start,
                    args.min_confidence,
                    args.min_switches,
                    args.min_skip_rate,
                    args.max_completion_rate,
                    track_id,
                    track_name,
                    artists,
                    switches,
                    skips,
                    completions,
                    uncertain,
                    skip_rate,
                    completion_rate,
                    confidence_score,
                    last_seen_at,
                    oldest_added_at,
                    years_in_playlist,
                    int(playlist_count or 0),
                    total_played_ms,
                    total_played_minutes,
                    score,
                    reason,
                ),
            )
            inserted += 1
            if inserted >= args.top:
                break

        update_last_cleanup_run(conn, run_id, args.window_months, window_start)
        conn.commit()
        print(
            f"ok run_id={run_id} inserted={inserted} window_months={args.window_months} window_start={window_start} counting_started_at={counting_started_at}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    main()


