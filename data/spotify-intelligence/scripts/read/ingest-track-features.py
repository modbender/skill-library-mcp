#!/usr/bin/env python3
import os, argparse, json, sqlite3, datetime
from pathlib import Path


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS spotify_track_features (
          track_id TEXT PRIMARY KEY,
          danceability REAL,
          energy REAL,
          key_value INTEGER,
          loudness REAL,
          mode_value INTEGER,
          speechiness REAL,
          acousticness REAL,
          instrumentalness REAL,
          liveness REAL,
          valence REAL,
          tempo REAL,
          time_signature INTEGER,
          analysis_url TEXT,
          source TEXT,
          fetched_at TEXT NOT NULL
        );
        """
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--payload", required=True)
    ap.add_argument("--source", default="spotify_audio_features")
    args = ap.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8-sig"))
    items = payload.get("audio_features") if isinstance(payload, dict) else payload
    if not items:
      items = []

    conn = sqlite3.connect(args.db)
    try:
        ensure(conn)
        count = 0
        for f in items:
            if not f:
                continue
            tid = f.get("id")
            if not tid:
                continue
            conn.execute(
                """
                INSERT INTO spotify_track_features(
                  track_id,danceability,energy,key_value,loudness,mode_value,speechiness,acousticness,
                  instrumentalness,liveness,valence,tempo,time_signature,analysis_url,source,fetched_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(track_id) DO UPDATE SET
                  danceability=excluded.danceability,
                  energy=excluded.energy,
                  key_value=excluded.key_value,
                  loudness=excluded.loudness,
                  mode_value=excluded.mode_value,
                  speechiness=excluded.speechiness,
                  acousticness=excluded.acousticness,
                  instrumentalness=excluded.instrumentalness,
                  liveness=excluded.liveness,
                  valence=excluded.valence,
                  tempo=excluded.tempo,
                  time_signature=excluded.time_signature,
                  analysis_url=excluded.analysis_url,
                  source=excluded.source,
                  fetched_at=excluded.fetched_at
                """,
                (
                    tid,
                    f.get("danceability"), f.get("energy"), f.get("key"), f.get("loudness"), f.get("mode"),
                    f.get("speechiness"), f.get("acousticness"), f.get("instrumentalness"), f.get("liveness"),
                    f.get("valence"), f.get("tempo"), f.get("time_signature"), f.get("analysis_url"),
                    args.source, now_iso()
                ),
            )
            count += 1
        conn.commit()
        print(json.dumps({"ok": True, "upserted": count}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()


