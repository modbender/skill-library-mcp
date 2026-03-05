#!/usr/bin/env python3
import os, sqlite3, datetime, math

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB = os.path.join(BASE_DIR, "data", "spotify-intelligence.sqlite")

BASE_SEC = {
    "currently-playing": 8,
    "recently-played": 120,
    "playlists": 1800,
    "profile": 21600,
    "top-short": 43200,
    "top-medium": 86400,
    "top-long": 172800,
}


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def p90(values):
    if not values:
        return 0
    xs = sorted(values)
    idx = int(math.ceil(0.9 * len(xs))) - 1
    idx = max(0, min(idx, len(xs) - 1))
    return xs[idx]


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def main():
    conn = sqlite3.connect(DB)
    try:
        conn.executescript(
            """
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
            )
            """
        )

        sources = [r[0] for r in conn.execute("SELECT DISTINCT source FROM api_request_metrics").fetchall()]
        for source in sources:
            rows = conn.execute(
                "SELECT request_ms, items_count, payload_bytes, status FROM api_request_metrics WHERE source=? ORDER BY id DESC LIMIT 500",
                (source,),
            ).fetchall()
            if not rows:
                continue

            ms_vals = [int(r[0] or 0) for r in rows if (r[3] or "") == "ok"]
            p90_ms = p90(ms_vals) if ms_vals else 0
            samples = len(rows)
            err = sum(1 for r in rows if (r[3] or "") != "ok")
            error_rate = err / samples if samples else 0.0
            avg_items = sum(float(r[1] or 0) for r in rows) / samples
            avg_bytes = sum(float(r[2] or 0) for r in rows) / samples

            base = BASE_SEC.get(source, 600)
            load_factor = max(1.0, (p90_ms / 1000.0) / 0.8) if p90_ms else 1.0
            err_factor = 1.0 + min(1.5, error_rate * 3.0)
            rec = int(clamp(base * load_factor * err_factor, 8, 7 * 24 * 3600))

            conn.execute(
                """
                INSERT INTO sync_source_strategy(source, samples, error_rate, p90_request_ms, avg_items_count, avg_payload_bytes, recommended_interval_sec, updated_at)
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(source) DO UPDATE SET
                  samples=excluded.samples,
                  error_rate=excluded.error_rate,
                  p90_request_ms=excluded.p90_request_ms,
                  avg_items_count=excluded.avg_items_count,
                  avg_payload_bytes=excluded.avg_payload_bytes,
                  recommended_interval_sec=excluded.recommended_interval_sec,
                  updated_at=excluded.updated_at
                """,
                (source, samples, error_rate, p90_ms, avg_items, avg_bytes, rec, now_iso()),
            )

        conn.commit()
        print("ok")
    finally:
        conn.close()


if __name__ == "__main__":
    main()



