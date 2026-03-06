#!/usr/bin/env python3
import os, argparse, sqlite3, datetime, json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def ensure(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS track_feedback (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          track_id TEXT NOT NULL,
          feedback_type TEXT NOT NULL,
          note TEXT,
          source TEXT NOT NULL DEFAULT 'manual',
          happened_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS track_feedback_profile (
          track_id TEXT PRIMARY KEY,
          like_count INTEGER NOT NULL DEFAULT 0,
          dislike_count INTEGER NOT NULL DEFAULT 0,
          skip_count INTEGER NOT NULL DEFAULT 0,
          keep_count INTEGER NOT NULL DEFAULT 0,
          dont_ask_again INTEGER NOT NULL DEFAULT 0,
          updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS context_prompt_suppression (
          track_id TEXT PRIMARY KEY,
          suppressed INTEGER NOT NULL DEFAULT 1,
          reason TEXT,
          updated_at TEXT NOT NULL
        );
        """
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track-id", required=True)
    ap.add_argument("--type", required=True, choices=["like", "dislike", "skip", "keep", "dont-ask-again"])
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    try:
        ensure(conn)
        ts = now_iso()

        conn.execute(
            "INSERT INTO track_feedback(track_id,feedback_type,note,source,happened_at) VALUES (?,?,?,?,?)",
            (args.track_id, args.type, args.note or None, "manual", ts),
        )

        inc = {"like": (1,0,0,0,0), "dislike": (0,1,0,0,0), "skip": (0,0,1,0,0), "keep": (0,0,0,1,0), "dont-ask-again": (0,0,0,0,1)}[args.type]

        conn.execute(
            """
            INSERT INTO track_feedback_profile(track_id,like_count,dislike_count,skip_count,keep_count,dont_ask_again,updated_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(track_id) DO UPDATE SET
              like_count=track_feedback_profile.like_count+excluded.like_count,
              dislike_count=track_feedback_profile.dislike_count+excluded.dislike_count,
              skip_count=track_feedback_profile.skip_count+excluded.skip_count,
              keep_count=track_feedback_profile.keep_count+excluded.keep_count,
              dont_ask_again=track_feedback_profile.dont_ask_again+excluded.dont_ask_again,
              updated_at=excluded.updated_at
            """,
            (args.track_id, *inc, ts),
        )

        if args.type == "dont-ask-again":
            conn.execute(
                "INSERT INTO context_prompt_suppression(track_id,suppressed,reason,updated_at) VALUES (?,?,?,?) ON CONFLICT(track_id) DO UPDATE SET suppressed=1, reason=excluded.reason, updated_at=excluded.updated_at",
                (args.track_id, 1, "manual_dont_ask_again", ts),
            )

        conn.commit()
        print(json.dumps({"ok": True, "trackId": args.track_id, "type": args.type}))
    finally:
        conn.close()


if __name__ == "__main__":
    main()



