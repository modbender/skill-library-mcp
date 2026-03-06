"""
Research Library Database Schema

SQLite database initialization, schema creation, migrations, and health checks.
"""
import sqlite3
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


# =============================================================================
# Schema Definitions
# =============================================================================

SCHEMA_VERSION = 1

SCHEMA_SQL = """
-- =============================================================================
-- Core Tables
-- =============================================================================

-- Research documents/notes
CREATE TABLE IF NOT EXISTS research (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    title TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    project_id TEXT NOT NULL,
    material_type TEXT NOT NULL DEFAULT 'note' 
        CHECK (material_type IN ('note', 'source', 'reference', 'draft', 'archive')),
    confidence REAL NOT NULL DEFAULT 0.5 
        CHECK (confidence >= 0.0 AND confidence <= 1.0),
    source_url TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    -- Reference material requires high confidence
    CHECK (material_type != 'reference' OR confidence >= 0.8)
);

-- Tags for categorization
CREATE TABLE IF NOT EXISTS tags (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL UNIQUE,
    color TEXT,  -- Hex color code
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Many-to-many: research <-> tags
CREATE TABLE IF NOT EXISTS research_tags (
    research_id TEXT NOT NULL REFERENCES research(id) ON DELETE CASCADE,
    tag_id TEXT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (research_id, tag_id)
);

-- Links between research documents
CREATE TABLE IF NOT EXISTS research_links (
    source_id TEXT NOT NULL REFERENCES research(id) ON DELETE CASCADE,
    target_id TEXT NOT NULL REFERENCES research(id) ON DELETE CASCADE,
    link_type TEXT NOT NULL DEFAULT 'related'
        CHECK (link_type IN ('related', 'supports', 'contradicts', 'cites', 'derived_from', 'supersedes')),
    relevance_score REAL NOT NULL DEFAULT 0.5
        CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (source_id, target_id)
);

-- =============================================================================
-- Attachments & Versions
-- =============================================================================

-- File attachments
CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    research_id TEXT NOT NULL REFERENCES research(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    path TEXT NOT NULL,  -- Relative storage path
    mime_type TEXT,
    file_size INTEGER,
    extracted_text TEXT,
    extraction_confidence REAL NOT NULL DEFAULT 0.0
        CHECK (extraction_confidence >= 0.0 AND extraction_confidence <= 1.0),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Version history for attachments
CREATE TABLE IF NOT EXISTS attachment_versions (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    attachment_id TEXT NOT NULL REFERENCES attachments(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL DEFAULT 1,
    path TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (attachment_id, version_number)
);

-- =============================================================================
-- Extraction Queue
-- =============================================================================

-- Queue for text extraction jobs
CREATE TABLE IF NOT EXISTS extraction_queue (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    attachment_id TEXT NOT NULL REFERENCES attachments(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'skipped')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    error_message TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (attachment_id)
);

-- =============================================================================
-- Embeddings (Vector Search)
-- =============================================================================

-- Vector embeddings for semantic search
CREATE TABLE IF NOT EXISTS embeddings (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    research_id TEXT NOT NULL REFERENCES research(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    embedding_model TEXT NOT NULL,
    embedding BLOB NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (research_id, chunk_index, embedding_model)
);

-- =============================================================================
-- Full-Text Search (FTS5)
-- =============================================================================

-- FTS for research content
CREATE VIRTUAL TABLE IF NOT EXISTS research_fts USING fts5(
    title,
    content,
    content='research',
    content_rowid='rowid'
);

-- FTS for attachment extracted text
CREATE VIRTUAL TABLE IF NOT EXISTS attachments_fts USING fts5(
    filename,
    extracted_text,
    content='attachments',
    content_rowid='rowid'
);

-- =============================================================================
-- Indexes
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_research_project ON research(project_id);
CREATE INDEX IF NOT EXISTS idx_research_type ON research(material_type);
CREATE INDEX IF NOT EXISTS idx_research_confidence ON research(confidence);
CREATE INDEX IF NOT EXISTS idx_research_created ON research(created_at);
CREATE INDEX IF NOT EXISTS idx_research_updated ON research(updated_at);

CREATE INDEX IF NOT EXISTS idx_attachments_research ON attachments(research_id);
CREATE INDEX IF NOT EXISTS idx_attachments_mime ON attachments(mime_type);

CREATE INDEX IF NOT EXISTS idx_extraction_status ON extraction_queue(status);
CREATE INDEX IF NOT EXISTS idx_extraction_created ON extraction_queue(created_at);

CREATE INDEX IF NOT EXISTS idx_embeddings_research ON embeddings(research_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON embeddings(embedding_model);

CREATE INDEX IF NOT EXISTS idx_links_source ON research_links(source_id);
CREATE INDEX IF NOT EXISTS idx_links_target ON research_links(target_id);
CREATE INDEX IF NOT EXISTS idx_links_type ON research_links(link_type);

-- =============================================================================
-- Triggers
-- =============================================================================

-- Auto-update updated_at on research changes
CREATE TRIGGER IF NOT EXISTS trg_research_updated 
    AFTER UPDATE ON research
    FOR EACH ROW
BEGIN
    UPDATE research SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Auto-update updated_at on extraction_queue changes
CREATE TRIGGER IF NOT EXISTS trg_extraction_updated
    AFTER UPDATE ON extraction_queue
    FOR EACH ROW
BEGIN
    UPDATE extraction_queue SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Sync research FTS on insert
CREATE TRIGGER IF NOT EXISTS trg_research_fts_insert
    AFTER INSERT ON research
BEGIN
    INSERT INTO research_fts(rowid, title, content) VALUES (NEW.rowid, NEW.title, NEW.content);
END;

-- Sync research FTS on update
CREATE TRIGGER IF NOT EXISTS trg_research_fts_update
    AFTER UPDATE ON research
BEGIN
    UPDATE research_fts SET title = NEW.title, content = NEW.content WHERE rowid = NEW.rowid;
END;

-- Sync research FTS on delete
CREATE TRIGGER IF NOT EXISTS trg_research_fts_delete
    AFTER DELETE ON research
BEGIN
    DELETE FROM research_fts WHERE rowid = OLD.rowid;
END;

-- Sync attachments FTS on insert
CREATE TRIGGER IF NOT EXISTS trg_attachments_fts_insert
    AFTER INSERT ON attachments
BEGIN
    INSERT INTO attachments_fts(rowid, filename, extracted_text) 
    VALUES (NEW.rowid, NEW.filename, COALESCE(NEW.extracted_text, ''));
END;

-- Sync attachments FTS on update
CREATE TRIGGER IF NOT EXISTS trg_attachments_fts_update
    AFTER UPDATE ON attachments
BEGIN
    UPDATE attachments_fts 
    SET filename = NEW.filename, extracted_text = COALESCE(NEW.extracted_text, '')
    WHERE rowid = NEW.rowid;
END;

-- Sync attachments FTS on delete
CREATE TRIGGER IF NOT EXISTS trg_attachments_fts_delete
    AFTER DELETE ON attachments
BEGIN
    DELETE FROM attachments_fts WHERE rowid = OLD.rowid;
END;

-- Auto-create extraction job when attachment is inserted
CREATE TRIGGER IF NOT EXISTS trg_attachment_extraction_queue
    AFTER INSERT ON attachments
BEGIN
    INSERT INTO extraction_queue(attachment_id) VALUES (NEW.id);
END;

-- =============================================================================
-- Metadata Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS _schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


# =============================================================================
# ResearchDatabase Class
# =============================================================================

class ResearchDatabase:
    """
    SQLite database manager for the Research Library.
    
    Handles initialization, schema creation, migrations, and health checks.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file (will be created if not exists)
        """
        self.db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        
    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection (creates if needed).
        
        Returns:
            sqlite3.Connection with row factory enabled
        """
        if self._connection is None:
            # Ensure parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            # WAL mode for better concurrency
            self._connection.execute("PRAGMA journal_mode = WAL")
            
        return self._connection
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def init_schema(self) -> bool:
        """
        Initialize database schema.
        
        Creates all tables, indexes, triggers, and FTS tables.
        
        Returns:
            True if schema was created/updated successfully
        """
        conn = self.get_connection()
        
        try:
            # Execute schema in a transaction
            conn.executescript(SCHEMA_SQL)
            
            # Set schema version
            conn.execute(
                "INSERT OR REPLACE INTO _schema_meta(key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION))
            )
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Failed to initialize schema: {e}")
    
    def get_schema_version(self) -> int:
        """Get current schema version."""
        conn = self.get_connection()
        try:
            cursor = conn.execute(
                "SELECT value FROM _schema_meta WHERE key = 'schema_version'"
            )
            row = cursor.fetchone()
            return int(row[0]) if row else 0
        except sqlite3.Error:
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform database health check.
        
        Returns:
            Dict with health status and diagnostics
        """
        result = {
            "healthy": False,
            "db_exists": self.db_path.exists(),
            "db_path": str(self.db_path),
            "schema_version": 0,
            "tables": [],
            "issues": []
        }
        
        if not result["db_exists"]:
            result["issues"].append("Database file does not exist")
            return result
        
        try:
            conn = self.get_connection()
            
            # Check schema version
            result["schema_version"] = self.get_schema_version()
            
            # Check tables exist
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            result["tables"] = [row[0] for row in cursor.fetchall()]
            
            required_tables = [
                "research", "tags", "research_tags", "research_links",
                "attachments", "attachment_versions", "extraction_queue",
                "embeddings", "_schema_meta"
            ]
            
            for table in required_tables:
                if table not in result["tables"]:
                    result["issues"].append(f"Missing table: {table}")
            
            # Check FTS tables
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_fts%'"
            )
            fts_tables = [row[0] for row in cursor.fetchall()]
            
            if "research_fts" not in fts_tables:
                result["issues"].append("Missing FTS table: research_fts")
            if "attachments_fts" not in fts_tables:
                result["issues"].append("Missing FTS table: attachments_fts")
            
            # Check integrity
            cursor = conn.execute("PRAGMA integrity_check")
            integrity = cursor.fetchone()[0]
            if integrity != "ok":
                result["issues"].append(f"Integrity check failed: {integrity}")
            
            result["healthy"] = len(result["issues"]) == 0
            
        except sqlite3.Error as e:
            result["issues"].append(f"Database error: {e}")
        
        return result
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get database statistics.
        
        Returns:
            Dict with counts for documents, attachments, queue depth, etc.
        """
        conn = self.get_connection()
        
        stats = {
            "research_count": 0,
            "attachment_count": 0,
            "tag_count": 0,
            "link_count": 0,
            "embedding_count": 0,
            "queue_pending": 0,
            "queue_processing": 0,
            "queue_failed": 0,
            "queue_completed": 0,
        }
        
        try:
            # Research count
            cursor = conn.execute("SELECT COUNT(*) FROM research")
            stats["research_count"] = cursor.fetchone()[0]
            
            # Attachment count
            cursor = conn.execute("SELECT COUNT(*) FROM attachments")
            stats["attachment_count"] = cursor.fetchone()[0]
            
            # Tag count
            cursor = conn.execute("SELECT COUNT(*) FROM tags")
            stats["tag_count"] = cursor.fetchone()[0]
            
            # Link count
            cursor = conn.execute("SELECT COUNT(*) FROM research_links")
            stats["link_count"] = cursor.fetchone()[0]
            
            # Embedding count
            cursor = conn.execute("SELECT COUNT(*) FROM embeddings")
            stats["embedding_count"] = cursor.fetchone()[0]
            
            # Queue stats
            cursor = conn.execute(
                "SELECT status, COUNT(*) FROM extraction_queue GROUP BY status"
            )
            for row in cursor.fetchall():
                status, count = row
                stats[f"queue_{status}"] = count
                
        except sqlite3.Error:
            pass  # Return zeros on error
        
        return stats
    
    # =========================================================================
    # Migration Helpers
    # =========================================================================
    
    def add_column(self, table: str, column: str, column_type: str, 
                   default: Optional[str] = None) -> bool:
        """
        Add a column to an existing table (if it doesn't exist).
        
        Args:
            table: Table name
            column: Column name
            column_type: SQLite column type (TEXT, INTEGER, REAL, BLOB)
            default: Default value (optional)
            
        Returns:
            True if column was added or already exists
        """
        conn = self.get_connection()
        
        # Check if column exists
        cursor = conn.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if column in columns:
            return True
        
        # Build ALTER statement
        sql = f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"
        if default is not None:
            sql += f" DEFAULT {default}"
        
        try:
            conn.execute(sql)
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to add column: {e}")
    
    def create_index(self, index_name: str, table: str, columns: List[str],
                     unique: bool = False) -> bool:
        """
        Create an index (if it doesn't exist).
        
        Args:
            index_name: Name for the index
            table: Table to index
            columns: Columns to include in index
            unique: Whether index should enforce uniqueness
            
        Returns:
            True if index was created or already exists
        """
        conn = self.get_connection()
        
        unique_str = "UNIQUE" if unique else ""
        columns_str = ", ".join(columns)
        
        sql = f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {table}({columns_str})"
        
        try:
            conn.execute(sql)
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create index: {e}")
    
    def create_view(self, view_name: str, select_sql: str, 
                    replace: bool = False) -> bool:
        """
        Create a view.
        
        Args:
            view_name: Name for the view
            select_sql: SELECT statement for view definition
            replace: If True, replace existing view
            
        Returns:
            True if view was created
        """
        conn = self.get_connection()
        
        create_type = "CREATE OR REPLACE VIEW" if replace else "CREATE VIEW IF NOT EXISTS"
        sql = f"{create_type} {view_name} AS {select_sql}"
        
        try:
            conn.execute(sql)
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create view: {e}")
    
    def table_exists(self, table: str) -> bool:
        """Check if a table exists."""
        conn = self.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        )
        return cursor.fetchone() is not None
    
    def get_table_info(self, table: str) -> List[Dict[str, Any]]:
        """Get column info for a table."""
        conn = self.get_connection()
        cursor = conn.execute(f"PRAGMA table_info({table})")
        return [
            {
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "default": row[4],
                "pk": bool(row[5])
            }
            for row in cursor.fetchall()
        ]
    
    def vacuum(self) -> bool:
        """Vacuum database to reclaim space and optimize."""
        conn = self.get_connection()
        try:
            conn.execute("VACUUM")
            return True
        except sqlite3.Error:
            return False


# =============================================================================
# Utility Functions
# =============================================================================

def generate_id() -> str:
    """Generate a new UUID for use as primary key."""
    return uuid.uuid4().hex


def init_database(db_path: str) -> ResearchDatabase:
    """
    Convenience function to create and initialize a database.
    
    Args:
        db_path: Path to database file
        
    Returns:
        Initialized ResearchDatabase instance
    """
    db = ResearchDatabase(db_path)
    db.init_schema()
    return db
