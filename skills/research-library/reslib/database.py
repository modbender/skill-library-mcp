"""
Database module for Research Library.

Handles SQLite database initialization, schema management, and FTS5 support.
"""

import sqlite3
import threading
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class ResearchDatabase:
    """
    SQLite database manager with FTS5 support for research documents.
    
    Thread-safe connection pooling with proper locking for concurrent access.
    """
    
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: str | Path, timeout: float = 30.0):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
            timeout: Connection timeout in seconds
        """
        self.db_path = Path(db_path)
        self.timeout = timeout
        self._local = threading.local()
        self._lock = threading.RLock()
        
        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema
        self._init_schema()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=self.timeout,
                check_same_thread=False
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._local.connection = conn
        return self._local.connection
    
    @contextmanager
    def connection(self):
        """Context manager for database connections."""
        conn = self._get_connection()
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions with automatic commit/rollback."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL statement with automatic retry on database lock."""
        import time
        max_retries = 5
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                with self._lock:
                    conn = self._get_connection()
                    cursor = conn.execute(sql, params)
                    conn.commit()
                    return cursor
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    logger.warning(f"Database locked, retry {attempt + 1}/{max_retries}")
                    time.sleep(retry_delay * (2 ** attempt))
                else:
                    raise
        raise sqlite3.OperationalError("Database locked after max retries")
    
    def executemany(self, sql: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """Execute SQL statement with multiple parameter sets."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.executemany(sql, params_list)
            conn.commit()
            return cursor
    
    def fetchone(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one result."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.execute(sql, params)
            return cursor.fetchone()
    
    def fetchall(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute query and fetch all results."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.execute(sql, params)
            return cursor.fetchall()
    
    def _init_schema(self):
        """Initialize database schema."""
        with self.transaction() as conn:
            # Attachments table - stores document metadata
            conn.execute("""
                CREATE TABLE IF NOT EXISTS attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    path TEXT NOT NULL UNIQUE,
                    mime_type TEXT,
                    file_size INTEGER,
                    checksum TEXT,
                    extracted_text TEXT,
                    extraction_confidence REAL,
                    extracted_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Extraction queue table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS extraction_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    attachment_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    worker_id TEXT,
                    priority INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    error_message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    next_retry_at TIMESTAMP,
                    FOREIGN KEY (attachment_id) REFERENCES attachments(id) ON DELETE CASCADE
                )
            """)
            
            # Create index for queue polling
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_queue_status_created 
                ON extraction_queue(status, created_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_queue_status_retry 
                ON extraction_queue(status, next_retry_at)
            """)
            
            # Worker heartbeat table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS worker_heartbeat (
                    worker_id TEXT PRIMARY KEY,
                    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'idle',
                    current_job_id INTEGER,
                    jobs_completed INTEGER DEFAULT 0,
                    jobs_failed INTEGER DEFAULT 0,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Extraction metrics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS extraction_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL,
                    attachment_id INTEGER NOT NULL,
                    worker_id TEXT,
                    extraction_time_ms INTEGER,
                    confidence REAL,
                    status TEXT,
                    error_type TEXT,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES extraction_queue(id),
                    FOREIGN KEY (attachment_id) REFERENCES attachments(id)
                )
            """)
            
            # FTS5 virtual table for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS attachments_fts USING fts5(
                    filename,
                    extracted_text,
                    content='attachments',
                    content_rowid='id'
                )
            """)
            
            # Triggers to keep FTS in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS attachments_ai AFTER INSERT ON attachments BEGIN
                    INSERT INTO attachments_fts(rowid, filename, extracted_text)
                    VALUES (new.id, new.filename, new.extracted_text);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS attachments_ad AFTER DELETE ON attachments BEGIN
                    INSERT INTO attachments_fts(attachments_fts, rowid, filename, extracted_text)
                    VALUES('delete', old.id, old.filename, old.extracted_text);
                END
            """)
            
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS attachments_au AFTER UPDATE ON attachments BEGIN
                    INSERT INTO attachments_fts(attachments_fts, rowid, filename, extracted_text)
                    VALUES('delete', old.id, old.filename, old.extracted_text);
                    INSERT INTO attachments_fts(rowid, filename, extracted_text)
                    VALUES (new.id, new.filename, new.extracted_text);
                END
            """)
            
            # Schema version tracking
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert schema version if not exists
            existing = conn.execute(
                "SELECT version FROM schema_version WHERE version = ?",
                (self.SCHEMA_VERSION,)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (self.SCHEMA_VERSION,)
                )
    
    def add_attachment(
        self,
        filename: str,
        path: str,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        checksum: Optional[str] = None
    ) -> int:
        """
        Add a new attachment to the database.
        
        Returns:
            Attachment ID
        """
        cursor = self.execute(
            """
            INSERT INTO attachments (filename, path, mime_type, file_size, checksum)
            VALUES (?, ?, ?, ?, ?)
            """,
            (filename, path, mime_type, file_size, checksum)
        )
        return cursor.lastrowid
    
    def get_attachment(self, attachment_id: int) -> Optional[Dict[str, Any]]:
        """Get attachment by ID."""
        row = self.fetchone(
            "SELECT * FROM attachments WHERE id = ?",
            (attachment_id,)
        )
        return dict(row) if row else None
    
    def update_attachment_extraction(
        self,
        attachment_id: int,
        extracted_text: str,
        confidence: float
    ):
        """Update attachment with extraction results."""
        self.execute(
            """
            UPDATE attachments 
            SET extracted_text = ?, 
                extraction_confidence = ?,
                extracted_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (extracted_text, confidence, attachment_id)
        )
    
    def search_attachments(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Full-text search across attachments."""
        rows = self.fetchall(
            """
            SELECT a.*, 
                   highlight(attachments_fts, 1, '<mark>', '</mark>') as snippet
            FROM attachments a
            JOIN attachments_fts fts ON a.id = fts.rowid
            WHERE attachments_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (query, limit)
        )
        return [dict(row) for row in rows]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        total = self.fetchone("SELECT COUNT(*) as count FROM attachments")
        extracted = self.fetchone(
            "SELECT COUNT(*) as count FROM attachments WHERE extracted_text IS NOT NULL"
        )
        queue_pending = self.fetchone(
            "SELECT COUNT(*) as count FROM extraction_queue WHERE status = 'pending'"
        )
        queue_processing = self.fetchone(
            "SELECT COUNT(*) as count FROM extraction_queue WHERE status = 'processing'"
        )
        queue_failed = self.fetchone(
            "SELECT COUNT(*) as count FROM extraction_queue WHERE status = 'failed'"
        )
        
        return {
            "total_attachments": total["count"] if total else 0,
            "extracted_attachments": extracted["count"] if extracted else 0,
            "queue_pending": queue_pending["count"] if queue_pending else 0,
            "queue_processing": queue_processing["count"] if queue_processing else 0,
            "queue_failed": queue_failed["count"] if queue_failed else 0,
        }
    
    def close(self):
        """Close database connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
