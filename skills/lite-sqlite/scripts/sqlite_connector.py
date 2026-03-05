#!/usr/bin/env python3
"""
Lite SQLite - Lightweight SQLite Database Wrapper for OpenClaw Agents

Ultra-lightweight database operations with minimal RAM and storage overhead.
Optimized for OpenClaw agents with connection pooling and performance tuning.
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
import threading
from pathlib import Path
from contextlib import contextmanager


class SQLiteDB:
    """Lightweight SQLite database wrapper with performance optimizations."""

    def __init__(
        self,
        path: str = ":memory:",
        wal_mode: bool = True,
        synchronous: str = "NORMAL",
        cache_size: int = 64000,
        check_same_thread: bool = True
    ):
        """Initialize SQLite database connection.

        Args:
            path: Database file path or ":memory:" for in-memory DB
            wal_mode: Enable Write-Ahead Logging (3-4x faster writes)
            synchronous: NORMAL or FULL (NORMAL is faster, FULL is safer)
            cache_size: Cache size in negative KB (default: 64MB)
            check_same_thread: False for multi-threaded use
        """
        self.path = path
        self.is_memory = (path == ":memory:")

        # Create parent directories if needed
        if not self.is_memory:
            Path(path).parent.mkdir(parents=True, exist_ok=True)

        # Connect with optimizations
        self.conn = sqlite3.connect(
            path,
            check_same_thread=check_same_thread,
            isolation_level=None  # Autocommit mode
        )

        # Enable WAL mode for concurrent access and performance
        if wal_mode and not self.is_memory:
            self.conn.execute("PRAGMA journal_mode=WAL")

        # Performance optimizations
        self.conn.execute(f"PRAGMA synchronous={synchronous}")
        self.conn.execute(f"PRAGMA cache_size=-{cache_size}")
        self.conn.execute("PRAGMA page_size=4096")
        self.conn.execute("PRAGMA temp_store=MEMORY")

        # Row factory for dict-like access
        self.conn.row_factory = sqlite3.Row

    def create_table(self, name: str, schema: Dict[str, str]) -> None:
        """Create a table with specified schema.

        Args:
            name: Table name
            schema: Dictionary of {column_name: type_definition}
                    e.g., {"id": "INTEGER PRIMARY KEY", "name": "TEXT NOT NULL"}
        """
        columns = ", ".join([f"{col} {defn}" for col, defn in schema.items()])
        stmt = f"CREATE TABLE IF NOT EXISTS {name} ({columns})"
        self.conn.execute(stmt)
        self.conn.commit()

    def create_index(self, table: str, columns: str) -> None:
        """Create index on specified columns.

        Args:
            table: Table name
            columns: Column name(s), comma-separated for composite index
        """
        index_name = f"idx_{table}_{columns.replace(',', '_').replace(' ', '')}"
        stmt = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table} ({columns})"
        self.conn.execute(stmt)
        self.conn.commit()

    def insert(self, table: str, **kwargs) -> int:
        """Insert a row into table.

        Args:
            table: Table name
            **kwargs: Column name -> value pairs

        Returns:
            Last inserted row ID
        """
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        stmt = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        cursor = self.conn.execute(stmt, list(kwargs.values()))
        return cursor.lastrowid

    def batch_insert(self, table: str, rows: List[Dict[str, Any]]) -> int:
        """Insert multiple rows efficiently.

        Args:
            table: Table name
            rows: List of dictionaries with column->value pairs

        Returns:
            Number of rows inserted
        """
        if not rows:
            return 0

        columns = ", ".join(rows[0].keys())
        placeholders = ", ".join(["?"] * len(rows[0]))
        stmt = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        values = [list(row.values()) for row in rows]
        cursor = self.conn.executemany(stmt, values)
        return cursor.rowcount

    def insert_or_replace(self, table: str, **kwargs) -> int:
        """Insert or replace row (upsert by primary key).

        Args:
            table: Table name
            **kwargs: Column name -> value pairs

        Returns:
            Last inserted row ID
        """
        columns = ", ".join(kwargs.keys())
        placeholders = ", ".join(["?"] * len(kwargs))
        stmt = f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})"

        cursor = self.conn.execute(stmt, list(kwargs.values()))
        return cursor.lastrowid

    def query(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dicts.

        Args:
            sql: SQL SELECT statement
            params: Query parameters

        Returns:
            List of row dictionaries
        """
        cursor = self.conn.execute(sql, params or ())
        return [dict(row) for row in cursor.fetchall()]

    def query_one(
        self,
        sql: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> Optional[Dict[str, Any]]:
        """Execute SELECT query and return single row.

        Args:
            sql: SQL SELECT statement
            params: Query parameters

        Returns:
            Row dictionary or None if not found
        """
        cursor = self.conn.execute(sql, params or ())
        row = cursor.fetchone()
        return dict(row) if row else None

    def update(
        self,
        table: str,
        where: str,
        values: Dict[str, Any],
        where_params: Optional[Tuple[Any, ...]] = None
    ) -> int:
        """Update rows in table.

        Args:
            table: Table name
            where: WHERE clause (without "WHERE")
            values: Column name -> new value
            where_params: WHERE clause parameters

        Returns:
            Number of rows updated
        """
        set_clause = ", ".join([f"{col} = ?" for col in values.keys()])
        stmt = f"UPDATE {table} SET {set_clause} WHERE {where}"

        params = list(values.values()) + (list(where_params) if where_params else [])
        cursor = self.conn.execute(stmt, params)
        return cursor.rowcount

    def delete(
        self,
        table: str,
        where: str,
        params: Optional[Tuple[Any, ...]] = None
    ) -> int:
        """Delete rows from table.

        Args:
            table: Table name
            where: WHERE clause (without "WHERE")
            params: WHERE clause parameters

        Returns:
            Number of rows deleted
        """
        stmt = f"DELETE FROM {table} WHERE {where}"
        cursor = self.conn.execute(stmt, params or ())
        return cursor.rowcount

    def execute(self, sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
        """Execute arbitrary SQL statement.

        Args:
            sql: SQL statement
            params: Parameters

        Returns:
            Row count
        """
        cursor = self.conn.execute(sql, params or ())
        return cursor.rowcount

    def add_column(self, table: str, column: str, definition: str) -> None:
        """Add column to table if it doesn't exist.

        Args:
            table: Table name
            column: Column name
            definition: Column type and constraints
        """
        stmt = f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        try:
            self.conn.execute(stmt)
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column might already exist
            pass

    def table_exists(self, table: str) -> bool:
        """Check if table exists.

        Args:
            table: Table name

        Returns:
            True if table exists
        """
        result = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone()
        return result is not None

    def count(self, table: str, where: Optional[str] = None) -> int:
        """Count rows in table.

        Args:
            table: Table name
            where: Optional WHERE clause

        Returns:
            Row count
        """
        sql = f"SELECT COUNT(*) FROM {table}"
        if where:
            sql += f" WHERE {where}"
        result = self.conn.execute(sql).fetchone()
        return result[0]

    def cleanup_expired(self, table: str, column: str) -> int:
        """Delete expired entries based on timestamp column.

        Args:
            table: Table name
            column: Timestamp column name

        Returns:
            Number of rows deleted
        """
        now = datetime.now().isoformat()
        return self.delete(table, f"{column} < ?", (now,))

    def cleanup_old(self, table: str, column: str, days: int = 7) -> int:
        """Delete entries older than specified days.

        Args:
            table: Table name
            column: Timestamp column name
            days: Number of days

        Returns:
            Number of rows deleted
        """
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return self.delete(table, f"{column} < ?", (cutoff,))

    def backup(self, backup_path: str) -> None:
        """Create backup of database.

        Args:
            backup_path: Path for backup file
        """
        # Create parent directories
        Path(backup_path).parent.mkdir(parents=True, exist_ok=True)

        # SQLite backup
        backup = sqlite3.connect(backup_path)
        self.conn.backup(backup)
        backup.close()

    def auto_backup(self, backup_dir: str, period: str = "daily") -> None:
        """Create timestamped backup.

        Args:
            backup_dir: Directory for backups
            period: Backup frequency (daily, hourly)
        """
        if period == "daily":
            timestamp = datetime.now().strftime("%Y-%m-%d")
        elif period == "hourly":
            timestamp = datetime.now().strftime("%Y-%m-%d_%H")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        name = Path(self.path).stem if not self.is_memory else "memory"
        backup_path = os.path.join(backup_dir, f"{name}_{timestamp}.db")
        self.backup(backup_path)

    def vacuum(self) -> None:
        """Reclaim space after deletes (optimize database)."""
        self.conn.execute("VACUUM")
        self.conn.commit()

    def analyze(self) -> None:
        """Update query planner statistics."""
        self.conn.execute("ANALYZE")
        self.conn.commit()

    def size(self) -> Dict[str, float]:
        """Get database size information.

        Returns:
            Dictionary with size info in MB
        """
        info = self.conn.execute("PRAGMA page_count, page_size").fetchone()

        return {
            "page_count": info[0],
            "page_size": info[1],
            "size_mb": (info[0] * info[1]) / (1024 * 1024),
            "path": self.path if not self.is_memory else ":memory:"
        }

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()


class ConnectionPool:
    """Simple connection pool for concurrent database access."""

    def __init__(self, path: str, max_connections: int = 5, **kwargs):
        """Initialize connection pool.

        Args:
            path: Database file path
            max_connections: Max concurrent connections
            **kwargs: Additional args for SQLiteDB
        """
        self.path = path
        self.max_connections = max_connections
        self.kwargs = kwargs
        self.pool = []
        self.lock = threading.Lock()

        # Create initial connection
        for _ in range(max_connections):
            conn = SQLiteDB(path, check_same_thread=False, **kwargs)
            self.pool.append(conn)

    def get_connection(self, timeout: float = 5.0) -> SQLiteDB:
        """Get connection from pool.

        Args:
            timeout: Timeout in seconds

        Returns:
            SQLiteDB connection
        """
        deadline = datetime.now() + timedelta(seconds=timeout)

        while datetime.now() < deadline:
            with self.lock:
                if self.pool:
                    return self.pool.pop()

        raise TimeoutError("No available connections in pool")

    def release_connection(self, conn: SQLiteDB) -> None:
        """Release connection back to pool.

        Args:
            conn: Connection to release
        """
        with self.lock:
            if len(self.pool) < self.max_connections:
                self.pool.append(conn)
            else:
                conn.close()

    def close_all(self) -> None:
        """Close all connections in pool."""
        with self.lock:
            for conn in self.pool:
                conn.close()
            self.pool.clear()


# Convenience functions
def get_db(path: str = ":memory:", **kwargs) -> SQLiteDB:
    """Quick database access function.

    Args:
        path: Database path (default: in-memory)
        **kwargs: SQLiteDB options

    Returns:
        SQLiteDB instance
    """
    return SQLiteDB(path, **kwargs)


def json_loads(value: str) -> Any:
    """Safely parse JSON string.

    Args:
        value: JSON string

    Returns:
        Parsed object or string if invalid JSON
    """
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


def json_dumps(value: Any) -> str:
    """Convert value to JSON string.

    Args:
        value: Object to serialize

    Returns:
        JSON string
    """
    if isinstance(value, str):
        return value
    return json.dumps(value)


# Database migration helpers
class Migration:
    """Database migration utility."""

    def __init__(self, db: SQLiteDB):
        """Initialize migration.

        Args:
            db: SQLiteDB instance
        """
        self.db = db

    def ensure_version_table(self) -> None:
        """Ensure migrations table exists."""
        if not self.db.table_exists("migrations"):
            self.db.create_table("migrations", {
                "version": "INTEGER PRIMARY KEY",
                "applied_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
            })

    def is_applied(self, version: int) -> bool:
        """Check if migration version is applied.

        Args:
            version: Migration version number

        Returns:
            True if migration applied
        """
        result = self.db.query_one(
            "SELECT version FROM migrations WHERE version = ?",
            (version,)
        )
        return result is not None

    def mark_applied(self, version: int) -> None:
        """Mark migration as applied.

        Args:
            version: Migration version number
        """
        self.db.insert("migrations", version=version)
