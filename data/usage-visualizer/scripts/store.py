"""
SQLite storage for LLM Cost Monitor
"""
import json
import os
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class UsageStore:
    def __init__(self, storage_path: str = "~/.llm-cost-monitor"):
        self.storage_path = os.path.expanduser(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)
        self.db_path = os.path.join(self.storage_path, "usage.db")
        self._init_db()

    def _init_db(self):
        """Initialize database schema and handle migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if we need to migrate api_key_hash to source_id_hash
        cursor.execute("PRAGMA table_info(usage_records)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'api_key_hash' in columns and 'source_id_hash' not in columns:
            print("Migrating database: api_key_hash -> source_id_hash")
            cursor.execute("ALTER TABLE usage_records RENAME COLUMN api_key_hash TO source_id_hash")

        # Usage records table (Safe create if not exists)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                provider TEXT NOT NULL,
                source_id_hash TEXT NOT NULL,
                model TEXT NOT NULL,
                app TEXT DEFAULT 'openclaw',
                source TEXT DEFAULT 'session',
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                cache_read_tokens INTEGER DEFAULT 0,
                cache_creation_tokens INTEGER DEFAULT 0,
                cost REAL DEFAULT 0,
                savings REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, provider, source_id_hash, model, app, source)
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_usage_date_provider
            ON usage_records(date, provider)
        """)

        conn.commit()
        conn.close()

    def add_usage(
        self,
        date: str,
        provider: str,
        source_id: str,
        model: str,
        app: str = "openclaw",
        source: str = "session",
        input_tokens: int = 0,
        output_tokens: int = 0,
        cache_read_tokens: int = 0,
        cache_creation_tokens: int = 0,
        cost: float = 0.0,
        savings: float = 0.0,
        incremental: bool = True
    ):
        """
        Add or update usage record
        source_id is typically a local session identifier (e.g., directory name), NOT a credential.
        """
        id_hash = self._hash_source_id(source_id)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if incremental:
            cursor.execute("""
                INSERT INTO usage_records
                (date, provider, source_id_hash, model, app, source, input_tokens, output_tokens,
                 cache_read_tokens, cache_creation_tokens, cost, savings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, provider, source_id_hash, model, app, source)
                DO UPDATE SET
                    input_tokens = usage_records.input_tokens + excluded.input_tokens,
                    output_tokens = usage_records.output_tokens + excluded.output_tokens,
                    cache_read_tokens = usage_records.cache_read_tokens + excluded.cache_read_tokens,
                    cache_creation_tokens = usage_records.cache_creation_tokens + excluded.cache_creation_tokens,
                    cost = usage_records.cost + excluded.cost,
                    savings = usage_records.savings + excluded.savings
            """, (date, provider, id_hash, model, app, source, input_tokens, output_tokens,
                  cache_read_tokens, cache_creation_tokens, cost, savings))
        else:
            cursor.execute("""
                INSERT INTO usage_records
                (date, provider, source_id_hash, model, app, source, input_tokens, output_tokens,
                 cache_read_tokens, cache_creation_tokens, cost, savings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, provider, source_id_hash, model, app, source)
                DO UPDATE SET
                    input_tokens = excluded.input_tokens,
                    output_tokens = excluded.output_tokens,
                    cache_read_tokens = excluded.cache_read_tokens,
                    cache_creation_tokens = excluded.cache_creation_tokens,
                    cost = excluded.cost,
                    savings = excluded.savings
            """, (date, provider, id_hash, model, app, source, input_tokens, output_tokens,
                  cache_read_tokens, cache_creation_tokens, cost, savings))

        conn.commit()
        conn.close()

    def clear_records(self, date: Optional[str] = None, source: Optional[str] = None):
        """Clear records for a specific date or source"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if date and source:
            cursor.execute("DELETE FROM usage_records WHERE date = ? AND source = ?", (date, source))
        elif date:
            cursor.execute("DELETE FROM usage_records WHERE date = ?", (date,))
        elif source:
            cursor.execute("DELETE FROM usage_records WHERE source = ?", (source,))
        else:
            cursor.execute("DELETE FROM usage_records")
            
        conn.commit()
        conn.close()

    def get_usage(
        self,
        start_date: str,
        end_date: str,
        provider: Optional[str] = None,
        app: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Dict]:
        """Get usage records for date range"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT date, provider, model, app, source,
                   SUM(input_tokens) as input_tokens,
                   SUM(output_tokens) as output_tokens,
                   SUM(cache_read_tokens) as cache_read_tokens,
                   SUM(cache_creation_tokens) as cache_creation_tokens,
                   SUM(cost) as cost
            FROM usage_records
            WHERE date >= ? AND date <= ?
        """
        params = [start_date, end_date]

        if provider:
            query += " AND provider = ?"
            params.append(provider)
        if app:
            query += " AND app = ?"
            params.append(app)
        if source:
            query += " AND source = ?"
            params.append(source)

        query += " GROUP BY date, provider, model, app, source ORDER BY date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_total_cost(
        self,
        start_date: str,
        end_date: str,
        provider: Optional[str] = None
    ) -> float:
        """Get total cost for date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT SUM(cost) FROM usage_records WHERE date >= ? AND date <= ?"
        params = [start_date, end_date]

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        cursor.execute(query, params)
        result = cursor.fetchone()[0]
        conn.close()

        return result or 0.0

    def get_cost_by_model(
        self,
        start_date: str,
        end_date: str,
        provider: Optional[str] = None
    ) -> Dict[str, float]:
        """Get cost breakdown by model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT model, SUM(cost) as cost
            FROM usage_records
            WHERE date >= ? AND date <= ?
        """
        params = [start_date, end_date]

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        query += " GROUP BY model ORDER BY cost DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return {row[0]: row[1] for row in rows}

    def get_cost_by_provider(
        self,
        start_date: str,
        end_date: str
    ) -> Dict[str, float]:
        """Get cost breakdown by provider"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = """
            SELECT provider, SUM(cost) as cost
            FROM usage_records
            WHERE date >= ? AND date <= ?
            GROUP BY provider
        """

        cursor.execute(query, [start_date, end_date])
        rows = cursor.fetchall()
        conn.close()

        return {row[0]: row[1] for row in rows}

    def get_tokens_summary(
        self,
        start_date: str,
        end_date: str,
        provider: Optional[str] = None
    ) -> Dict:
        """Get detailed token summary including cache tokens"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT 
                SUM(input_tokens) as total_input,
                SUM(output_tokens) as total_output,
                SUM(cache_read_tokens) as total_cache_read,
                SUM(cache_creation_tokens) as total_cache_write,
                SUM(input_tokens + output_tokens) as total_tokens,
                SUM(cost) as total_cost
            FROM usage_records
            WHERE date >= ? AND date <= ?
        """
        params = [start_date, end_date]

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "input_tokens": row["total_input"] or 0,
                "output_tokens": row["total_output"] or 0,
                "cache_read_tokens": row["total_cache_read"] or 0,
                "cache_creation_tokens": row["total_cache_write"] or 0,
                "total_tokens": row["total_tokens"] or 0,
                "total_cost": row["total_cost"] or 0
            }
        return {
            "input_tokens": 0, "output_tokens": 0, "cache_read_tokens": 0,
            "cache_creation_tokens": 0, "total_tokens": 0, "total_cost": 0
        }

    def get_daily_summary(
        self,
        start_date: str,
        end_date: str,
        provider: Optional[str] = None
    ) -> List[Dict]:
        """Get daily summary grouped by date"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT date,
                   SUM(input_tokens) as input_tokens,
                   SUM(output_tokens) as output_tokens,
                   SUM(cache_read_tokens) as cache_read_tokens,
                   SUM(cache_creation_tokens) as cache_creation_tokens,
                   SUM(cost) as cost
            FROM usage_records
            WHERE date >= ? AND date <= ?
        """
        params = [start_date, end_date]

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        query += " GROUP BY date ORDER BY date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def _hash_source_id(source_id: str) -> str:
        """
        Hashes the local source identifier (e.g., session directory name) 
        using SHA-256 to ensure data uniqueness and idempotent syncing.
        This is NOT a credential or API key.
        """
        return hashlib.sha256(source_id.encode()).hexdigest()[:16]


def get_store() -> UsageStore:
    """Get default usage store instance"""
    return UsageStore()
