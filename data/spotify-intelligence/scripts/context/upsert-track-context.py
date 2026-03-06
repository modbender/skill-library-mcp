#!/usr/bin/env python3
import os, argparse, sqlite3, datetime, json


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS track_ratings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          track_id TEXT NOT NULL,
          rating INTEGER NOT NULL,
          reason TEXT,
          rated_at TEXT NOT NULL,
          source TEXT NOT NULL DEFAULT 'manual'
        );

        CREATE TABLE IF NOT EXISTS track_tags (
          track_id TEXT NOT NULL,
          tag TEXT NOT NULL,
          weight REAL NOT NULL DEFAULT 1,
          source TEXT NOT NULL DEFAULT 'manual',
          first_set_at TEXT NOT NULL,
          last_set_at TEXT NOT NULL,
          set_count INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(track_id, tag)
        );

        CREATE TABLE IF NOT EXISTS track_context_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          track_id TEXT NOT NULL,
          mood TEXT,
          intent TEXT,
          note TEXT,
          triggered_by TEXT NOT NULL DEFAULT 'manual_prompt',
          confidence REAL NOT NULL DEFAULT 0.7,
          happened_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS context_prompt_policy (
          key TEXT PRIMARY KEY,
          value TEXT,
          updated_at TEXT NOT NULL
        );
        """
    )


def set_defaults(conn):
    defaults = {
        "min_minutes_between_prompts": "90",
        "max_prompts_per_day": "4",
        "prompt_mode": "gentle",
    }
    ts = now_iso()
    for k, v in defaults.items():
        conn.execute(
            """
            INSERT INTO context_prompt_policy(key,value,updated_at)
            VALUES (?,?,?)
            ON CONFLICT(key) DO NOTHING
            """,
            (k, v, ts),
        )


def upsert_tag(conn, track_id, tag, source):
    ts = now_iso()
    conn.execute(
        """
        INSERT INTO track_tags(track_id,tag,weight,source,first_set_at,last_set_at,set_count)
        VALUES (?,?,1,?,?,?,1)
        ON CONFLICT(track_id,tag) DO UPDATE SET
          last_set_at=excluded.last_set_at,
          set_count=track_tags.set_count+1,
          source=excluded.source
        """,
        (track_id, tag, source, ts, ts),
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--track-id", required=True)
    ap.add_argument("--rating", type=int)
    ap.add_argument("--tags", default="")
    ap.add_argument("--mood", default="")
    ap.add_argument("--intent", default="")
    ap.add_argument("--note", default="")
    ap.add_argument("--source", default="manual")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    try:
        ensure(conn)
        set_defaults(conn)

        if args.rating is not None:
            conn.execute(
                "INSERT INTO track_ratings(track_id,rating,reason,rated_at,source) VALUES (?,?,?,?,?)",
                (args.track_id, args.rating, args.note or None, now_iso(), args.source),
            )

        tags = [t.strip() for t in args.tags.split(',') if t.strip()]
        for t in tags:
            upsert_tag(conn, args.track_id, t.lower(), args.source)

        if args.mood or args.intent or args.note:
            conn.execute(
                """
                INSERT INTO track_context_events(track_id,mood,intent,note,triggered_by,confidence,happened_at)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    args.track_id,
                    args.mood or None,
                    args.intent or None,
                    args.note or None,
                    args.source,
                    0.8 if args.source == 'manual' else 0.6,
                    now_iso(),
                ),
            )

        conn.commit()
        print(json.dumps({"ok": True, "trackId": args.track_id, "tags": tags}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()


