"""
ConvoYield Cloud Database — Dual-backend analytics storage.

Supports both SQLite (local dev) and PostgreSQL (Cloud Run / Supabase).
Set DATABASE_URL env var to a postgres:// connection string for production.
If unset, falls back to SQLite at ~/.convoyield/analytics.db.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


DATABASE_URL = os.environ.get("DATABASE_URL", "")
SQLITE_PATH = os.environ.get("CONVOYIELD_DB", str(Path.home() / ".convoyield" / "analytics.db"))


def _is_postgres() -> bool:
    return DATABASE_URL.startswith("postgres")


class Database:
    def __init__(self, db_url: Optional[str] = None):
        self._url = db_url or DATABASE_URL
        self._pg = self._url.startswith("postgres") if self._url else False
        self._conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        if self._pg:
            import psycopg2
            import psycopg2.extras
            self._conn = psycopg2.connect(self._url)
            self._conn.autocommit = True
        else:
            import sqlite3
            Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")

    def _cursor(self):
        if self._pg:
            import psycopg2.extras
            return self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self._conn.cursor()

    def _ph(self, count: int = 1) -> str:
        """Return placeholder string for the active backend."""
        p = "%s" if self._pg else "?"
        return ", ".join([p] * count)

    def _row_to_dict(self, row) -> Optional[dict]:
        if row is None:
            return None
        if isinstance(row, dict):
            return row
        return dict(row)

    # ── Schema ─────────────────────────────────────────────────────────────

    def _create_tables(self):
        if self._pg:
            self._create_tables_pg()
        else:
            self._create_tables_sqlite()
        self._migrate_stripe_columns()

    def _create_tables_sqlite(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                company TEXT,
                tier TEXT DEFAULT 'free',
                api_key TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                active_playbooks TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS yield_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                turn_number INTEGER,
                timestamp TEXT NOT NULL,
                sentiment REAL,
                sentiment_delta REAL,
                momentum REAL,
                estimated_yield REAL,
                captured_yield REAL,
                phase TEXT,
                risk_level REAL,
                recommended_play TEXT,
                arbitrage_types TEXT DEFAULT '[]',
                micro_conversion_types TEXT DEFAULT '[]',
                user_message_length INTEGER DEFAULT 0,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                conversion_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id TEXT NOT NULL,
                session_id TEXT UNIQUE NOT NULL,
                total_turns INTEGER,
                estimated_yield REAL,
                captured_yield REAL,
                final_phase TEXT,
                final_sentiment REAL,
                duration_seconds REAL,
                plays_recommended TEXT DEFAULT '[]',
                arbitrage_detected TEXT DEFAULT '[]',
                conversions_captured TEXT DEFAULT '[]',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS webhooks (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                url TEXT NOT NULL,
                events TEXT DEFAULT '[]',
                threshold REAL DEFAULT 100.0,
                active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE INDEX IF NOT EXISTS idx_events_account ON yield_events(account_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_events_session ON yield_events(session_id);
            CREATE INDEX IF NOT EXISTS idx_conversions_account ON conversions(account_id, timestamp);
            CREATE INDEX IF NOT EXISTS idx_sessions_account ON sessions(account_id, created_at);
        """)
        self._conn.commit()

    def _create_tables_pg(self):
        cur = self._cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                company TEXT,
                tier TEXT DEFAULT 'free',
                api_key TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                active_playbooks TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS yield_events (
                id SERIAL PRIMARY KEY,
                account_id TEXT NOT NULL REFERENCES accounts(id),
                session_id TEXT NOT NULL,
                turn_number INTEGER,
                timestamp TIMESTAMPTZ NOT NULL,
                sentiment DOUBLE PRECISION,
                sentiment_delta DOUBLE PRECISION,
                momentum DOUBLE PRECISION,
                estimated_yield DOUBLE PRECISION,
                captured_yield DOUBLE PRECISION,
                phase TEXT,
                risk_level DOUBLE PRECISION,
                recommended_play TEXT,
                arbitrage_types TEXT DEFAULT '[]',
                micro_conversion_types TEXT DEFAULT '[]',
                user_message_length INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS conversions (
                id SERIAL PRIMARY KEY,
                account_id TEXT NOT NULL REFERENCES accounts(id),
                session_id TEXT NOT NULL,
                conversion_type TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                account_id TEXT NOT NULL REFERENCES accounts(id),
                session_id TEXT UNIQUE NOT NULL,
                total_turns INTEGER,
                estimated_yield DOUBLE PRECISION,
                captured_yield DOUBLE PRECISION,
                final_phase TEXT,
                final_sentiment DOUBLE PRECISION,
                duration_seconds DOUBLE PRECISION,
                plays_recommended TEXT DEFAULT '[]',
                arbitrage_detected TEXT DEFAULT '[]',
                conversions_captured TEXT DEFAULT '[]',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS webhooks (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL REFERENCES accounts(id),
                url TEXT NOT NULL,
                events TEXT DEFAULT '[]',
                threshold DOUBLE PRECISION DEFAULT 100.0,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        # Create indexes (IF NOT EXISTS for indexes requires PG 9.5+)
        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_events_account ON yield_events(account_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_events_session ON yield_events(session_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversions_account ON conversions(account_id, timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_account ON sessions(account_id, created_at)",
        ]:
            cur.execute(idx_sql)
        cur.close()

    def _migrate_stripe_columns(self):
        """Add Stripe-related columns and subscriptions table (safe for re-runs)."""
        cur = self._cursor()
        # Add stripe columns to accounts
        for col in ["stripe_customer_id TEXT", "stripe_subscription_id TEXT"]:
            try:
                cur.execute(f"ALTER TABLE accounts ADD COLUMN {col}")
            except Exception:
                pass  # Column already exists
        # Create subscriptions table
        if self._pg:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL REFERENCES accounts(id),
                    stripe_subscription_id TEXT,
                    stripe_customer_id TEXT,
                    product_type TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    current_period_end TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
        else:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    account_id TEXT NOT NULL,
                    stripe_subscription_id TEXT,
                    stripe_customer_id TEXT,
                    product_type TEXT NOT NULL,
                    product_id TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    current_period_end TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """)
            self._conn.commit()
        cur.close()

    # ── Account Management ────────────────────────────────────────────────

    def create_account(self, account_id: str, email: str, company: Optional[str],
                       tier: str, api_key: str):
        cur = self._cursor()
        cur.execute(
            f"INSERT INTO accounts (id, email, company, tier, api_key) VALUES ({self._ph(5)})",
            (account_id, email, company, tier, api_key),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def get_account_by_key(self, api_key: str) -> Optional[dict]:
        cur = self._cursor()
        cur.execute(
            f"SELECT * FROM accounts WHERE api_key = {self._ph(1)}", (api_key,)
        )
        row = cur.fetchone()
        cur.close()
        return self._row_to_dict(row)

    def activate_playbook(self, account_id: str, playbook_id: str):
        cur = self._cursor()
        cur.execute(
            f"SELECT active_playbooks FROM accounts WHERE id = {self._ph(1)}", (account_id,)
        )
        row = cur.fetchone()
        if row:
            raw = self._row_to_dict(row)["active_playbooks"]
            playbooks = json.loads(raw)
            if playbook_id not in playbooks:
                playbooks.append(playbook_id)
            cur.execute(
                f"UPDATE accounts SET active_playbooks = {self._ph(1)} WHERE id = {self._ph(1)}",
                (json.dumps(playbooks), account_id),
            )
            if not self._pg:
                self._conn.commit()
        cur.close()

    def update_account_stripe(self, account_id: str, stripe_customer_id: str,
                              stripe_subscription_id: Optional[str] = None):
        cur = self._cursor()
        cur.execute(
            f"UPDATE accounts SET stripe_customer_id = {self._ph(1)}, "
            f"stripe_subscription_id = {self._ph(1)} WHERE id = {self._ph(1)}",
            (stripe_customer_id, stripe_subscription_id, account_id),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def update_account_tier(self, account_id: str, tier: str):
        cur = self._cursor()
        cur.execute(
            f"UPDATE accounts SET tier = {self._ph(1)} WHERE id = {self._ph(1)}",
            (tier, account_id),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def get_account_by_id(self, account_id: str) -> Optional[dict]:
        cur = self._cursor()
        cur.execute(
            f"SELECT * FROM accounts WHERE id = {self._ph(1)}", (account_id,)
        )
        row = cur.fetchone()
        cur.close()
        return self._row_to_dict(row)

    def get_account_by_stripe_customer(self, stripe_customer_id: str) -> Optional[dict]:
        cur = self._cursor()
        cur.execute(
            f"SELECT * FROM accounts WHERE stripe_customer_id = {self._ph(1)}",
            (stripe_customer_id,),
        )
        row = cur.fetchone()
        cur.close()
        return self._row_to_dict(row)

    def create_subscription(self, sub_id: str, account_id: str,
                            stripe_subscription_id: str, stripe_customer_id: str,
                            product_type: str, product_id: str,
                            current_period_end: Optional[str] = None):
        cur = self._cursor()
        cur.execute(
            f"INSERT INTO subscriptions (id, account_id, stripe_subscription_id, "
            f"stripe_customer_id, product_type, product_id, status, current_period_end) "
            f"VALUES ({self._ph(8)})",
            (sub_id, account_id, stripe_subscription_id, stripe_customer_id,
             product_type, product_id, "active", current_period_end),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def update_subscription_status(self, stripe_subscription_id: str, status: str):
        cur = self._cursor()
        cur.execute(
            f"UPDATE subscriptions SET status = {self._ph(1)} "
            f"WHERE stripe_subscription_id = {self._ph(1)}",
            (status, stripe_subscription_id),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def get_active_subscriptions(self, account_id: str) -> list[dict]:
        cur = self._cursor()
        cur.execute(
            f"SELECT * FROM subscriptions WHERE account_id = {self._ph(1)} AND status = 'active'",
            (account_id,),
        )
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_dict(r) for r in rows]

    def deactivate_playbook(self, account_id: str, playbook_id: str):
        cur = self._cursor()
        cur.execute(
            f"SELECT active_playbooks FROM accounts WHERE id = {self._ph(1)}", (account_id,)
        )
        row = cur.fetchone()
        if row:
            raw = self._row_to_dict(row)["active_playbooks"]
            playbooks = json.loads(raw)
            if playbook_id in playbooks:
                playbooks.remove(playbook_id)
            cur.execute(
                f"UPDATE accounts SET active_playbooks = {self._ph(1)} WHERE id = {self._ph(1)}",
                (json.dumps(playbooks), account_id),
            )
            if not self._pg:
                self._conn.commit()
        cur.close()

    # ── Event Ingestion ───────────────────────────────────────────────────

    def insert_yield_event(self, **kwargs):
        cur = self._cursor()
        cols = ", ".join(kwargs.keys())
        cur.execute(
            f"INSERT INTO yield_events ({cols}) VALUES ({self._ph(len(kwargs))})",
            tuple(kwargs.values()),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def insert_conversion(self, **kwargs):
        cur = self._cursor()
        cols = ", ".join(kwargs.keys())
        cur.execute(
            f"INSERT INTO conversions ({cols}) VALUES ({self._ph(len(kwargs))})",
            tuple(kwargs.values()),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def insert_session_summary(self, **kwargs):
        cur = self._cursor()
        cols = ", ".join(kwargs.keys())
        if self._pg:
            # ON CONFLICT for Postgres upsert
            update_cols = ", ".join(f"{k} = EXCLUDED.{k}" for k in kwargs.keys() if k != "session_id")
            cur.execute(
                f"INSERT INTO sessions ({cols}) VALUES ({self._ph(len(kwargs))}) "
                f"ON CONFLICT (session_id) DO UPDATE SET {update_cols}",
                tuple(kwargs.values()),
            )
        else:
            cur.execute(
                f"INSERT OR REPLACE INTO sessions ({cols}) VALUES ({self._ph(len(kwargs))})",
                tuple(kwargs.values()),
            )
            self._conn.commit()
        cur.close()

    # ── Analytics Queries ─────────────────────────────────────────────────

    def get_overview_stats(self, account_id: str, since: str) -> dict:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        cur.execute(f"""
            SELECT
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(*) as total_turns,
                COALESCE(SUM(estimated_yield), 0) as total_estimated_yield,
                COALESCE(SUM(captured_yield), 0) as total_captured_yield,
                COALESCE(AVG(estimated_yield), 0) as avg_yield_per_session,
                COALESCE(AVG(sentiment), 0) as avg_sentiment,
                COALESCE(AVG(momentum), 0) as avg_momentum,
                COALESCE(AVG(risk_level), 0) as avg_risk
            FROM yield_events
            WHERE account_id = {p} AND timestamp >= {p}
        """, (account_id, since))
        row = cur.fetchone()
        cur.close()
        if row:
            return self._row_to_dict(row)
        return {
            "total_sessions": 0, "total_turns": 0,
            "total_estimated_yield": 0, "total_captured_yield": 0,
            "avg_yield_per_session": 0, "avg_sentiment": 0,
            "avg_momentum": 0, "avg_risk": 0,
        }

    def get_play_stats(self, account_id: str, since: str) -> list[dict]:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        cur.execute(f"""
            SELECT
                recommended_play as play,
                COUNT(*) as count,
                AVG(estimated_yield) as avg_yield,
                AVG(captured_yield) as avg_captured
            FROM yield_events
            WHERE account_id = {p} AND timestamp >= {p} AND recommended_play IS NOT NULL
            GROUP BY recommended_play
            ORDER BY count DESC
        """, (account_id, since))
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_dict(r) for r in rows]

    def get_arbitrage_stats(self, account_id: str, since: str) -> list[dict]:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        cur.execute(f"""
            SELECT arbitrage_types, estimated_yield
            FROM yield_events
            WHERE account_id = {p} AND timestamp >= {p} AND arbitrage_types != '[]'
        """, (account_id, since))
        rows = cur.fetchall()
        cur.close()

        type_stats: dict[str, dict] = {}
        for row in rows:
            r = self._row_to_dict(row)
            types = json.loads(r["arbitrage_types"])
            for t in types:
                if t not in type_stats:
                    type_stats[t] = {"type": t, "count": 0, "total_yield": 0.0}
                type_stats[t]["count"] += 1
                type_stats[t]["total_yield"] += r["estimated_yield"]

        return sorted(type_stats.values(), key=lambda x: x["count"], reverse=True)

    def get_conversion_stats(self, account_id: str, since: str) -> list[dict]:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        cur.execute(f"""
            SELECT
                conversion_type,
                COUNT(*) as count,
                SUM(value) as total_value,
                AVG(value) as avg_value
            FROM conversions
            WHERE account_id = {p} AND timestamp >= {p}
            GROUP BY conversion_type
            ORDER BY total_value DESC
        """, (account_id, since))
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_dict(r) for r in rows]

    def get_yield_timeline(self, account_id: str, since: str,
                           granularity: str = "hour") -> list[dict]:
        cur = self._cursor()
        p = "%s" if self._pg else "?"

        if self._pg:
            # Postgres: use date_trunc
            trunc = "hour" if granularity == "hour" else "day"
            cur.execute(f"""
                SELECT
                    date_trunc('{trunc}', timestamp) as period,
                    COUNT(DISTINCT session_id) as sessions,
                    SUM(estimated_yield) as estimated,
                    SUM(captured_yield) as captured,
                    AVG(sentiment) as avg_sentiment,
                    AVG(momentum) as avg_momentum
                FROM yield_events
                WHERE account_id = {p} AND timestamp >= {p}
                GROUP BY period
                ORDER BY period
            """, (account_id, since))
        else:
            # SQLite: use strftime
            time_fmt = "%Y-%m-%d %H:00" if granularity == "hour" else "%Y-%m-%d"
            cur.execute(f"""
                SELECT
                    strftime('{time_fmt}', timestamp) as period,
                    COUNT(DISTINCT session_id) as sessions,
                    SUM(estimated_yield) as estimated,
                    SUM(captured_yield) as captured,
                    AVG(sentiment) as avg_sentiment,
                    AVG(momentum) as avg_momentum
                FROM yield_events
                WHERE account_id = {p} AND timestamp >= {p}
                GROUP BY period
                ORDER BY period
            """, (account_id, since))

        rows = cur.fetchall()
        cur.close()
        result = []
        for r in rows:
            d = self._row_to_dict(r)
            # Normalize period to string for JSON serialization
            if hasattr(d.get("period"), "isoformat"):
                d["period"] = d["period"].isoformat()
            result.append(d)
        return result

    def get_sessions(self, account_id: str, limit: int = 50,
                     offset: int = 0) -> list[dict]:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        cur.execute(f"""
            SELECT * FROM sessions
            WHERE account_id = {p}
            ORDER BY created_at DESC
            LIMIT {p} OFFSET {p}
        """, (account_id, limit, offset))
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_dict(r) for r in rows]

    def get_leaderboard(self, account_id: str, since: str) -> list[dict]:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        cur.execute(f"""
            SELECT
                session_id,
                MAX(estimated_yield) as peak_yield,
                MAX(captured_yield) as captured,
                COUNT(*) as turns,
                MAX(phase) as last_phase
            FROM yield_events
            WHERE account_id = {p} AND timestamp >= {p}
            GROUP BY session_id
            ORDER BY peak_yield DESC
            LIMIT 20
        """, (account_id, since))
        rows = cur.fetchall()
        cur.close()
        return [self._row_to_dict(r) for r in rows]

    def count_events_today(self, account_id: str) -> int:
        cur = self._cursor()
        p = "%s" if self._pg else "?"
        if self._pg:
            cur.execute(f"""
                SELECT COUNT(*) as cnt FROM yield_events
                WHERE account_id = {p} AND timestamp >= CURRENT_DATE
            """, (account_id,))
        else:
            cur.execute(f"""
                SELECT COUNT(*) as cnt FROM yield_events
                WHERE account_id = {p} AND timestamp >= date('now')
            """, (account_id,))
        row = cur.fetchone()
        cur.close()
        r = self._row_to_dict(row)
        return r["cnt"] if r else 0

    def create_webhook(self, account_id: str, webhook_id: str, url: str,
                       events: str, threshold: float):
        cur = self._cursor()
        cur.execute(
            f"INSERT INTO webhooks (id, account_id, url, events, threshold) VALUES ({self._ph(5)})",
            (webhook_id, account_id, url, events, threshold),
        )
        if not self._pg:
            self._conn.commit()
        cur.close()

    def close(self):
        self._conn.close()
