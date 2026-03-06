#!/usr/bin/env python3
import os, argparse, sqlite3, datetime


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--request-ms", type=int, default=0)
    ap.add_argument("--payload-bytes", type=int, default=0)
    ap.add_argument("--items-count", type=int, default=0)
    ap.add_argument("--has-next", type=int, default=0)
    ap.add_argument("--status", default="ok")
    ap.add_argument("--http-code", type=int, default=0)
    ap.add_argument("--error", default="")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
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
            CREATE INDEX IF NOT EXISTS idx_api_metrics_source_time ON api_request_metrics(source, requested_at DESC);
            """
        )

        conn.execute(
            """
            INSERT INTO api_request_metrics(
              requested_at, source, endpoint, page, limit_value, offset_value,
              request_ms, payload_bytes, items_count, has_next, status, http_code, error_message
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                now_iso(),
                args.source,
                args.endpoint,
                args.page,
                args.limit,
                args.offset,
                args.request_ms,
                args.payload_bytes,
                args.items_count,
                1 if args.has_next else 0,
                args.status,
                args.http_code,
                args.error,
            ),
        )
        conn.commit()
        print("ok")
    finally:
        conn.close()


if __name__ == "__main__":
    main()


