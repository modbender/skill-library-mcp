#!/usr/bin/env python3
import os, argparse, sqlite3, datetime, json


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def table_has_column(conn, table_name, column_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(r[1] == column_name for r in rows)


def ensure(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS life_phase_flags (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS playlist_reorg_rules (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          rule_key TEXT UNIQUE NOT NULL,
          description TEXT NOT NULL,
          enabled INTEGER NOT NULL DEFAULT 1,
          source_playlist TEXT,
          target_playlist TEXT,
          min_years_in_playlist REAL DEFAULT 0,
          max_total_played_minutes REAL DEFAULT 99999,
          min_confidence REAL DEFAULT 0,
          min_skip_rate REAL DEFAULT 0,
          min_speed_proxy REAL DEFAULT 0,
          min_energy_proxy REAL DEFAULT 0,
          min_focus_proxy REAL DEFAULT 0,
          require_tag TEXT,
          exclude_if_tag TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS track_tags (
          track_id TEXT NOT NULL,
          tag TEXT NOT NULL,
          weight REAL NOT NULL DEFAULT 1,
          source TEXT,
          first_set_at TEXT,
          last_set_at TEXT,
          set_count INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(track_id, tag)
        );

        CREATE TABLE IF NOT EXISTS track_derived_features (
          track_id TEXT PRIMARY KEY,
          speed_proxy REAL NOT NULL DEFAULT 0,
          energy_proxy REAL NOT NULL DEFAULT 0,
          focus_proxy REAL NOT NULL DEFAULT 0,
          mood_stability_proxy REAL NOT NULL DEFAULT 0,
          novelty_proxy REAL NOT NULL DEFAULT 0,
          confidence REAL NOT NULL DEFAULT 0,
          signals_json TEXT,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS playlist_reorg_runs (
          run_id TEXT PRIMARY KEY,
          generated_at TEXT NOT NULL,
          inserted_count INTEGER NOT NULL DEFAULT 0,
          meta_json TEXT
        );

        CREATE TABLE IF NOT EXISTS playlist_reorg_candidates (
          run_id TEXT NOT NULL,
          generated_at TEXT NOT NULL,
          rule_key TEXT NOT NULL,
          playlist_id TEXT,
          playlist_name TEXT,
          track_id TEXT NOT NULL,
          track_name TEXT,
          artists TEXT,
          years_in_playlist REAL,
          total_played_minutes REAL,
          skip_rate REAL,
          confidence_score REAL,
          matched_tags TEXT,
          rationale TEXT,
          action TEXT NOT NULL,
          target_playlist TEXT,
          status TEXT NOT NULL DEFAULT 'proposed',
          PRIMARY KEY(run_id, rule_key, track_id)
        );
        """
    )

    for col in ["min_speed_proxy", "min_energy_proxy", "min_focus_proxy"]:
        if not table_has_column(conn, "playlist_reorg_rules", col):
            conn.execute(f"ALTER TABLE playlist_reorg_rules ADD COLUMN {col} REAL DEFAULT 0")


def upsert_default_rules(conn):
    ts = now_iso()
    rules = [
        {
            "rule_key": "old_low_playtime_to_delete_suggestions",
            "description": "Very old in playlist + barely played -> suggest move to delete suggestions",
            "source_playlist": None,
            "target_playlist": "LÃ¶schvorschlÃ¤ge",
            "min_years": 1.0,
            "max_minutes": 20.0,
            "min_conf": 0.25,
            "min_skip": 0.0,
            "min_speed": 0.0,
            "min_energy": 0.0,
            "min_focus": 0.0,
            "require_tag": None,
            "exclude_tag": "keep",
        },
        {
            "rule_key": "heartbreak_phase_archive_when_relationship_happy",
            "description": "Tracks tagged heartbreak move to archive suggestions if relationship_happy=true",
            "source_playlist": None,
            "target_playlist": "Emotions-Archiv",
            "min_years": 0.0,
            "max_minutes": 99999.0,
            "min_conf": 0.0,
            "min_skip": 0.0,
            "min_speed": 0.0,
            "min_energy": 0.0,
            "min_focus": 0.0,
            "require_tag": "heartbreak",
            "exclude_tag": "core-memory",
        },
    ]
    for r in rules:
        conn.execute(
            """
            INSERT INTO playlist_reorg_rules(rule_key,description,enabled,source_playlist,target_playlist,
                                             min_years_in_playlist,max_total_played_minutes,min_confidence,min_skip_rate,
                                             min_speed_proxy,min_energy_proxy,min_focus_proxy,
                                             require_tag,exclude_if_tag,created_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(rule_key) DO UPDATE SET
              description=excluded.description,
              updated_at=excluded.updated_at
            """,
            (
                r["rule_key"], r["description"], 1, r["source_playlist"], r["target_playlist"],
                r["min_years"], r["max_minutes"], r["min_conf"], r["min_skip"],
                r["min_speed"], r["min_energy"], r["min_focus"],
                r["require_tag"], r["exclude_tag"], ts, ts,
            ),
        )


def get_flag(conn, key, default="false"):
    row = conn.execute("SELECT value FROM life_phase_flags WHERE key=?", (key,)).fetchone()
    return (row[0] if row else default).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--top", type=int, default=200)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        ensure(conn)
        upsert_default_rules(conn)

        run_id = datetime.datetime.now(datetime.timezone.utc).strftime("reorg_%Y%m%dT%H%M%SZ")
        generated_at = now_iso()

        relationship_happy = get_flag(conn, "relationship_happy", "false") == "true"

        rules = conn.execute("SELECT rule_key,description,source_playlist,target_playlist,min_years_in_playlist,max_total_played_minutes,min_confidence,min_skip_rate,min_speed_proxy,min_energy_proxy,min_focus_proxy,require_tag,exclude_if_tag FROM playlist_reorg_rules WHERE enabled=1").fetchall()

        inserted = 0
        for rule in rules:
            (rule_key, desc, src_pl, tgt_pl, min_years, max_minutes, min_conf, min_skip, min_speed, min_energy, min_focus, req_tag, ex_tag) = rule

            if rule_key == "heartbreak_phase_archive_when_relationship_happy" and not relationship_happy:
                continue

            rows = conn.execute(
                """
                SELECT p.playlist_id,
                       p.name,
                       t.track_id,
                       t.name,
                       t.artists,
                       COALESCE((julianday('now') - julianday(ptm.first_added_at))/365.25, 0) AS years_in_playlist,
                       COALESCE(ps.total_played_ms_before_switch,0)/60000.0 AS total_played_minutes,
                       COALESCE(dm.skip_rate,0) AS skip_rate,
                       COALESCE(dm.confidence_score,0) AS confidence_score,
                       COALESCE(df.speed_proxy,0) AS speed_proxy,
                       COALESCE(df.energy_proxy,0) AS energy_proxy,
                       COALESCE(df.focus_proxy,0) AS focus_proxy
                FROM playlist_track_membership ptm
                LEFT JOIN playlists p ON p.playlist_id = ptm.playlist_id
                LEFT JOIN tracks t ON t.track_id = ptm.track_id
                LEFT JOIN track_play_stats ps ON ps.track_id = ptm.track_id
                LEFT JOIN track_decision_metrics dm ON dm.track_id = ptm.track_id
                LEFT JOIN track_derived_features df ON df.track_id = ptm.track_id
                WHERE ptm.currently_present = 1
                  AND (? IS NULL OR p.name = ?)
                  AND COALESCE((julianday('now') - julianday(ptm.first_added_at))/365.25, 0) >= ?
                  AND COALESCE(ps.total_played_ms_before_switch,0)/60000.0 <= ?
                  AND COALESCE(dm.confidence_score,0) >= ?
                  AND COALESCE(dm.skip_rate,0) >= ?
                  AND COALESCE(df.speed_proxy,0) >= ?
                  AND COALESCE(df.energy_proxy,0) >= ?
                  AND COALESCE(df.focus_proxy,0) >= ?
                LIMIT ?
                """,
                (src_pl, src_pl, min_years, max_minutes, min_conf, min_skip, min_speed, min_energy, min_focus, args.top),
            ).fetchall()

            for r in rows:
                (pl_id, pl_name, track_id, track_name, artists, years_in_playlist, total_played_minutes, skip_rate, conf, speed_proxy, energy_proxy, focus_proxy) = r
                tags = [x[0] for x in conn.execute("SELECT tag FROM track_tags WHERE track_id=?", (track_id,)).fetchall()]

                if req_tag and req_tag not in tags:
                    continue
                if ex_tag and ex_tag in tags:
                    continue

                rationale = f"rule={rule_key}|years={years_in_playlist:.2f}|play_min={total_played_minutes:.2f}|skip={skip_rate:.2f}|conf={conf:.2f}|spd={speed_proxy:.2f}|eng={energy_proxy:.2f}|foc={focus_proxy:.2f}"
                conn.execute(
                    """
                    INSERT OR IGNORE INTO playlist_reorg_candidates(
                      run_id,generated_at,rule_key,playlist_id,playlist_name,track_id,track_name,artists,
                      years_in_playlist,total_played_minutes,skip_rate,confidence_score,matched_tags,rationale,
                      action,target_playlist,status
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        run_id, generated_at, rule_key, pl_id, pl_name, track_id, track_name, artists,
                        years_in_playlist, total_played_minutes, skip_rate, conf,
                        ",".join(tags), rationale, "move_suggested", tgt_pl, "proposed",
                    ),
                )
                inserted += 1

        conn.execute(
            "INSERT OR REPLACE INTO playlist_reorg_runs(run_id,generated_at,inserted_count,meta_json) VALUES (?,?,?,?)",
            (run_id, generated_at, inserted, json.dumps({"relationship_happy": relationship_happy})),
        )
        conn.commit()
        print(json.dumps({"ok": True, "runId": run_id, "inserted": inserted, "relationship_happy": relationship_happy}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()


