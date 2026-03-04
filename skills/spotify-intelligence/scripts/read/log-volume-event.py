#!/usr/bin/env python3
import os, argparse, sqlite3, datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS volume_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          happened_at TEXT NOT NULL,
          track_id TEXT,
          device_id TEXT,
          device_name TEXT,
          volume_percent INTEGER,
          source TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS track_device_volume_stats (
          track_id TEXT NOT NULL,
          device_id TEXT NOT NULL,
          device_name TEXT,
          avg_volume REAL NOT NULL DEFAULT 0,
          min_volume INTEGER,
          max_volume INTEGER,
          samples INTEGER NOT NULL DEFAULT 0,
          updated_at TEXT NOT NULL,
          PRIMARY KEY(track_id, device_id)
        );
        """
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track-id", default="")
    ap.add_argument("--device-id", default="")
    ap.add_argument("--device-name", default="")
    ap.add_argument("--volume", type=int, required=True)
    ap.add_argument("--source", default="playback_snapshot")
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    try:
        ensure(conn)
        ts = now_iso()
        conn.execute(
            "INSERT INTO volume_events(happened_at,track_id,device_id,device_name,volume_percent,source) VALUES (?,?,?,?,?,?)",
            (ts, args.track_id or None, args.device_id or None, args.device_name or None, args.volume, args.source),
        )

        if args.track_id and args.device_id:
            row = conn.execute(
                "SELECT avg_volume,min_volume,max_volume,samples FROM track_device_volume_stats WHERE track_id=? AND device_id=?",
                (args.track_id, args.device_id),
            ).fetchone()
            if row:
                avg, mn, mx, n = row
                n2 = int(n) + 1
                avg2 = ((float(avg) * int(n)) + args.volume) / n2
                mn2 = args.volume if mn is None else min(int(mn), args.volume)
                mx2 = args.volume if mx is None else max(int(mx), args.volume)
                conn.execute(
                    "UPDATE track_device_volume_stats SET device_name=?, avg_volume=?, min_volume=?, max_volume=?, samples=?, updated_at=? WHERE track_id=? AND device_id=?",
                    (args.device_name or None, avg2, mn2, mx2, n2, ts, args.track_id, args.device_id),
                )
            else:
                conn.execute(
                    "INSERT INTO track_device_volume_stats(track_id,device_id,device_name,avg_volume,min_volume,max_volume,samples,updated_at) VALUES (?,?,?,?,?,?,?,?)",
                    (args.track_id, args.device_id, args.device_name or None, float(args.volume), args.volume, args.volume, 1, ts),
                )

        conn.commit()
        print("ok")
    finally:
        conn.close()


if __name__ == '__main__':
    main()



