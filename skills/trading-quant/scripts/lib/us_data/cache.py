"""SQLite cache backend for US snapshots."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


class SQLiteSnapshotCache:
    """Simple SQLite cache for symbol snapshots."""

    def __init__(self, db_path: str | Path = "us_data/cache.db") -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS snapshot (
                    symbol TEXT NOT NULL,
                    quote_time TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last REAL,
                    prev REAL,
                    pct REAL,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    PRIMARY KEY (symbol, quote_time, source)
                )
                """
            )
            conn.commit()

    def get_latest_batch(self, symbols: list[str]) -> pd.DataFrame:
        if not symbols:
            return pd.DataFrame(columns=["symbol", "last", "prev", "pct", "quote_time", "source", "status"])

        placeholders = ",".join("?" for _ in symbols)
        query = f"""
            SELECT s.symbol, s.last, s.prev, s.pct, s.quote_time, s.source, s.status
            FROM snapshot s
            INNER JOIN (
                SELECT symbol, MAX(quote_time) AS max_qt
                FROM snapshot
                WHERE symbol IN ({placeholders})
                GROUP BY symbol
            ) t ON s.symbol = t.symbol AND s.quote_time = t.max_qt
            WHERE s.symbol IN ({placeholders})
            ORDER BY s.symbol
        """
        params = symbols + symbols
        with self._conn() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def upsert(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return
        rows = [
            (
                str(r.symbol),
                str(r.quote_time),
                str(r.source),
                str(r.status),
                float(r.last) if pd.notna(r.last) else None,
                float(r.prev) if pd.notna(r.prev) else None,
                float(r.pct) if pd.notna(r.pct) else None,
            )
            for r in df.itertuples(index=False)
        ]
        with self._conn() as conn:
            conn.executemany(
                """
                INSERT INTO snapshot (symbol,quote_time,source,status,last,prev,pct)
                VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(symbol,quote_time,source)
                DO UPDATE SET
                    status=excluded.status,
                    last=excluded.last,
                    prev=excluded.prev,
                    pct=excluded.pct,
                    updated_at=datetime('now')
                """,
                rows,
            )
            conn.commit()

    def stats(self) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n, MAX(updated_at) AS latest_update FROM snapshot"
            ).fetchone()
            return {"rows": int(row[0] or 0), "latest_update": row[1]}
