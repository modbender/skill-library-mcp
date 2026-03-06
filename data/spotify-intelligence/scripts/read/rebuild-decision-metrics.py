#!/usr/bin/env python3
import os, sqlite3, datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def main():
    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
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
            )
            """
        )

        rows = conn.execute(
            """
            SELECT track_id, observed_switches, observed_skips, observed_completions, observed_uncertain
            FROM track_play_stats
            """
        ).fetchall()

        for track_id, switches, skips, completions, uncertain in rows:
            switches = switches or 0
            skips = skips or 0
            completions = completions or 0
            uncertain = uncertain or 0

            if switches <= 0:
                skip_rate = completion_rate = uncertain_rate = confidence = 0.0
            else:
                skip_rate = skips / switches
                completion_rate = completions / switches
                uncertain_rate = uncertain / switches

                sample_factor = clamp(switches / 25.0)  # full confidence around 25 observed switches
                certainty_factor = clamp(1.0 - uncertain_rate)
                confidence = round(clamp(sample_factor * certainty_factor), 4)

            conn.execute(
                """
                INSERT INTO track_decision_metrics(track_id, switches, skips, completions, uncertain,
                                                   skip_rate, completion_rate, uncertain_rate, confidence_score, updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(track_id) DO UPDATE SET
                  switches=excluded.switches,
                  skips=excluded.skips,
                  completions=excluded.completions,
                  uncertain=excluded.uncertain,
                  skip_rate=excluded.skip_rate,
                  completion_rate=excluded.completion_rate,
                  uncertain_rate=excluded.uncertain_rate,
                  confidence_score=excluded.confidence_score,
                  updated_at=excluded.updated_at
                """,
                (track_id, switches, skips, completions, uncertain, skip_rate, completion_rate, uncertain_rate, confidence, now_iso()),
            )

        conn.commit()
        print(f"ok rebuilt metrics for {len(rows)} tracks")
    finally:
        conn.close()


if __name__ == "__main__":
    main()



