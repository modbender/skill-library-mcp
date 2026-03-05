from pathlib import Path


class CacheDB:
    def __init__(self, path: Path):
        import sqlite3

        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                fetched_at INTEGER,
                status INTEGER,
                body BLOB
            )
            """
        )
        self.conn.commit()

    def put(self, url: str, status: int, body: bytes):
        self.conn.execute(
            """
            INSERT INTO pages(url, fetched_at, status, body)
            VALUES (?, strftime('%s','now'), ?, ?)
            ON CONFLICT(url) DO UPDATE SET
              fetched_at=excluded.fetched_at,
              status=excluded.status,
              body=excluded.body
            """,
            (url, status, body),
        )
        self.conn.commit()
