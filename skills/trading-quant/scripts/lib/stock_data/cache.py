"""SQLite cache backend for normalized kline data."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


class SQLiteKlineCache:
    """Simple SQLite cache with UPSERT for kline rows."""

    def __init__(self, db_path: str | Path = "stock_data/cache.db") -> None:
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS kline (
                    code TEXT NOT NULL,
                    date TEXT NOT NULL,
                    frequency TEXT NOT NULL,
                    source TEXT NOT NULL,
                    adjust TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume REAL,
                    amount REAL,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                    PRIMARY KEY (code, date, frequency, source, adjust)
                )
                """
            )
            conn.commit()

    def get(
        self,
        code: str,
        frequency: str,
        adjust: str,
        start: str | None = None,
        end: str | None = None,
    ) -> pd.DataFrame:
        query = (
            "SELECT code,date,frequency,source,adjust,open,high,low,close,volume,amount "
            "FROM kline WHERE code=? AND frequency=? AND adjust=?"
        )
        args: list[str] = [code, frequency, adjust]
        if start:
            query += " AND date>=?"
            args.append(start)
        if end:
            query += " AND date<=?"
            args.append(end)
        query += " ORDER BY date"
        with self._conn() as conn:
            return pd.read_sql_query(query, conn, params=args)

    def upsert(self, df: pd.DataFrame) -> None:
        if df is None or df.empty:
            return
        rows = [
            (
                str(r.code),
                str(r.date),
                str(r.frequency),
                str(r.source),
                str(r.adjust),
                float(r.open) if pd.notna(r.open) else None,
                float(r.high) if pd.notna(r.high) else None,
                float(r.low) if pd.notna(r.low) else None,
                float(r.close) if pd.notna(r.close) else None,
                float(r.volume) if pd.notna(r.volume) else None,
                float(r.amount) if pd.notna(r.amount) else None,
            )
            for r in df.itertuples(index=False)
        ]
        with self._conn() as conn:
            conn.executemany(
                """
                INSERT INTO kline (code,date,frequency,source,adjust,open,high,low,close,volume,amount)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(code,date,frequency,source,adjust)
                DO UPDATE SET
                    open=excluded.open,
                    high=excluded.high,
                    low=excluded.low,
                    close=excluded.close,
                    volume=excluded.volume,
                    amount=excluded.amount,
                    updated_at=datetime('now')
                """,
                rows,
            )
            conn.commit()

    def stats(self) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n, MAX(updated_at) AS latest_update FROM kline"
            ).fetchone()
            return {"rows": int(row[0] or 0), "latest_update": row[1]}
