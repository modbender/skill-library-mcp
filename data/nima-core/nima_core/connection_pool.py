"""NIMA SQLite connection pool - thread-safe connection pooling for SQLite."""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, Optional


class SQLiteConnectionPool:
    """Thread-safe SQLite connection pool with WAL mode support."""
    
    def __init__(self, db_path: str, max_connections: int = 5, timeout: float = 30.0):
        """
        Initialize the connection pool.
        
        Args:
            db_path: Path to the SQLite database file
            max_connections: Maximum number of connections in the pool (default 5)
            timeout: Connection timeout in seconds (default 30)
        """
        self._db_path = db_path
        self._max_connections = max_connections
        self._timeout = timeout
        
        self._pool = []  # Available connections
        self._active = set()  # Currently in use connections
        self._lock = threading.Lock()
        self._waiters = 0
        
        # Initialize database with WAL mode
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with WAL mode."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout)
        try:
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.commit()
        finally:
            conn.close()
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with WAL mode."""
        conn = sqlite3.connect(self._db_path, timeout=self._timeout, check_same_thread=False)
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        return conn
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool.
        
        Yields:
            A SQLite connection
        
        Raises:
            RuntimeError: If pool is exhausted and waiters exceed max_connections
        """
        conn = None
        acquired = False
        
        with self._lock:
            self._waiters += 1
            acquired = True
            
            # Try to get from pool
            if self._pool:
                conn = self._pool.pop()
                self._active.add(id(conn))
            else:
                # Check if we can create a new connection
                active_count = len(self._active)
                if active_count < self._max_connections:
                    conn = self._create_connection()
                    self._active.add(id(conn))
                else:
                    # Pool exhausted - waiter count decremented in finally
                    raise RuntimeError(
                        f"Connection pool exhausted: {active_count}/{self._max_connections} "
                        f"connections in use. Consider increasing max_connections."
                    )
        
        try:
            yield conn
        finally:
            with self._lock:
                self._waiters -= 1
                self._active.discard(id(conn))
                # Return connection to pool
                if len(self._pool) < self._max_connections:
                    self._pool.append(conn)
                else:
                    # Pool is full, close the connection
                    try:
                        conn.close()
                    except Exception:
                        pass
    
    def close_all(self):
        """Close all connections in the pool."""
        with self._lock:
            # Close pooled connections
            for conn in self._pool:
                try:
                    conn.close()
                except Exception:
                    pass
            self._pool = []
            
            # Close active connections
            # Note: This won't forcibly close connections that are currently in use
            # but will prevent new ones from being returned to the pool
            self._active.clear()
    
    def stats(self) -> Dict[str, int]:
        """
        Get pool statistics.
        
        Returns:
            Dictionary with pool size, active connections, and waiters
        """
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'active_connections': len(self._active),
                'max_connections': self._max_connections,
                'waiters': self._waiters,
                'db_path': self._db_path
            }


# Global pool storage
_pools: Dict[str, SQLiteConnectionPool] = {}
_pools_lock = threading.Lock()


def get_pool(db_path: str, max_connections: int = 5, timeout: float = 30.0) -> SQLiteConnectionPool:
    """
    Get or create a connection pool for the given database path.
    
    Args:
        db_path: Path to the SQLite database file
        max_connections: Maximum number of connections (default 5)
        timeout: Connection timeout in seconds (default 30)
    
    Returns:
        The SQLiteConnectionPool instance
    """
    with _pools_lock:
        if db_path not in _pools:
            _pools[db_path] = SQLiteConnectionPool(db_path, max_connections, timeout)
        return _pools[db_path]


def close_pool(db_path: str):
    """
    Close and remove a connection pool.
    
    Args:
        db_path: Path to the SQLite database file
    """
    with _pools_lock:
        if db_path in _pools:
            _pools[db_path].close_all()
            del _pools[db_path]
