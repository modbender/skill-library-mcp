#!/usr/bin/env python3
"""
Research Library CLI - Command-line interface for managing research materials.

This module provides the main CLI using Click framework with commands for:
- Adding research materials (files or URLs)
- Searching across projects
- Getting, archiving, and exporting documents
- Managing document relationships (links)
- System status and backups
"""

import click
import json
import os
import re
import shutil
import sqlite3
import sys
import time
import hashlib
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse

from reslib import (
    __version__,
    DEFAULT_DATA_DIR,
    DEFAULT_DB_PATH,
    DEFAULT_ATTACHMENTS_DIR,
    DEFAULT_BACKUPS_DIR,
    MATERIAL_TYPES,
    LINK_TYPES,
    SUPPORTED_EXTENSIONS,
)


# ============================================================================
# Database Schema and Initialization
# ============================================================================

SCHEMA_SQL = """
-- Research documents table
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    material_type TEXT NOT NULL CHECK (material_type IN ('reference', 'research')),
    project_id TEXT,
    source_path TEXT,
    source_url TEXT,
    mime_type TEXT,
    file_hash TEXT,
    content_text TEXT,
    confidence REAL DEFAULT 0.5 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    tags TEXT,  -- JSON array
    metadata TEXT,  -- JSON object
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    archived_at TEXT DEFAULT NULL,
    is_archived INTEGER DEFAULT 0
);

-- Attachments table (for multi-file documents)
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    mime_type TEXT,
    file_size INTEGER,
    file_hash TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Document links/relationships table
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    target_id INTEGER NOT NULL,
    link_type TEXT NOT NULL CHECK (link_type IN ('applies_to', 'contradicts', 'supersedes', 'related')),
    relevance REAL DEFAULT 0.5 CHECK (relevance >= 0.0 AND relevance <= 1.0),
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (target_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE (source_id, target_id, link_type)
);

-- Extraction queue for async processing
CREATE TABLE IF NOT EXISTS extraction_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    worker_id TEXT,
    attempts INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Projects table for organization
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Full-text search virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    title,
    content_text,
    tags,
    content='documents',
    content_rowid='id'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
    INSERT INTO documents_fts(rowid, title, content_text, tags)
    VALUES (new.id, new.title, new.content_text, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, title, content_text, tags)
    VALUES ('delete', old.id, old.title, old.content_text, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
    INSERT INTO documents_fts(documents_fts, rowid, title, content_text, tags)
    VALUES ('delete', old.id, old.title, old.content_text, old.tags);
    INSERT INTO documents_fts(rowid, title, content_text, tags)
    VALUES (new.id, new.title, new.content_text, new.tags);
END;

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_documents_project ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_documents_material ON documents(material_type);
CREATE INDEX IF NOT EXISTS idx_documents_archived ON documents(is_archived);
CREATE INDEX IF NOT EXISTS idx_documents_confidence ON documents(confidence);
CREATE INDEX IF NOT EXISTS idx_attachments_document ON attachments(document_id);
CREATE INDEX IF NOT EXISTS idx_links_source ON links(source_id);
CREATE INDEX IF NOT EXISTS idx_links_target ON links(target_id);
CREATE INDEX IF NOT EXISTS idx_queue_status ON extraction_queue(status);
"""


def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize the database with schema if needed."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def get_connection(ctx: click.Context) -> sqlite3.Connection:
    """Get database connection from context, initializing if needed."""
    if "conn" not in ctx.obj:
        ctx.obj["conn"] = init_database(ctx.obj["db_path"])
    return ctx.obj["conn"]


# ============================================================================
# Utility Functions
# ============================================================================

def detect_mime_type(file_path: Path) -> str:
    """Detect MIME type from file extension."""
    ext = file_path.suffix.lower().lstrip(".")
    if ext in SUPPORTED_EXTENSIONS:
        return SUPPORTED_EXTENSIONS[ext]
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_text_from_file(file_path: Path, mime_type: str) -> Tuple[str, float]:
    """
    Extract text content from a file with confidence score.
    
    Returns:
        Tuple of (extracted_text, confidence_score)
    """
    confidence = 0.5  # Default confidence
    text = ""
    
    try:
        # Text-based files - high confidence
        if mime_type.startswith("text/") or mime_type in ("application/json", "application/yaml", "application/xml"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
            confidence = 0.95
        
        # PDF files - requires extraction (queue for async)
        elif mime_type == "application/pdf":
            # Try basic extraction, queue for OCR if needed
            try:
                import pypdf
                reader = pypdf.PdfReader(str(file_path))
                text_parts = []
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = "\n".join(text_parts)
                confidence = 0.8 if text.strip() else 0.2
            except ImportError:
                # pypdf not installed, queue for extraction
                confidence = 0.1
            except Exception:
                confidence = 0.1
        
        # Images - low confidence, need OCR
        elif mime_type.startswith("image/"):
            # Would need OCR - queue for async extraction
            confidence = 0.1
            text = f"[Image: {file_path.name}]"
        
        else:
            # Unknown type
            confidence = 0.1
            text = f"[Binary file: {file_path.name}]"
            
    except Exception as e:
        text = f"[Error extracting: {e}]"
        confidence = 0.0
    
    return text, confidence


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_timestamp(timestamp: str) -> str:
    """Format a timestamp for display."""
    if not timestamp:
        return "Never"
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return timestamp[:16] if len(timestamp) > 16 else timestamp


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis if too long."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def generate_title_from_path(file_path: Path) -> str:
    """Generate a document title from file path."""
    name = file_path.stem
    # Convert underscores and hyphens to spaces
    name = re.sub(r"[_-]+", " ", name)
    # Capitalize words
    name = name.title()
    return name


def is_url(s: str) -> bool:
    """Check if a string is a URL."""
    try:
        result = urlparse(s)
        return result.scheme in ("http", "https", "ftp")
    except Exception:
        return False


def validate_project_exists(conn: sqlite3.Connection, project_id: str) -> bool:
    """Check if a project exists, creating it if auto-create is enabled."""
    cursor = conn.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    if cursor.fetchone():
        return True
    # Auto-create project
    conn.execute(
        "INSERT INTO projects (id, name) VALUES (?, ?)",
        (project_id, project_id.replace("-", " ").title())
    )
    conn.commit()
    return True


# ============================================================================
# Output Formatting
# ============================================================================

class TableFormatter:
    """Format data as ASCII tables for terminal output."""
    
    def __init__(self, columns: List[Tuple[str, int]], use_color: bool = True):
        """
        Initialize formatter with column definitions.
        
        Args:
            columns: List of (name, width) tuples
            use_color: Whether to use ANSI color codes
        """
        self.columns = columns
        self.use_color = use_color and sys.stdout.isatty()
    
    def _colorize(self, text: str, style: str) -> str:
        """Apply ANSI color codes."""
        if not self.use_color:
            return text
        
        codes = {
            "bold": "\033[1m",
            "dim": "\033[2m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "red": "\033[31m",
            "cyan": "\033[36m",
            "reset": "\033[0m",
        }
        
        if style in codes:
            return f"{codes[style]}{text}{codes['reset']}"
        return text
    
    def _pad(self, text: str, width: int, align: str = "left") -> str:
        """Pad text to width."""
        text = str(text)[:width]  # Truncate if needed
        if align == "right":
            return text.rjust(width)
        elif align == "center":
            return text.center(width)
        return text.ljust(width)
    
    def header(self) -> str:
        """Generate table header."""
        parts = []
        for name, width in self.columns:
            parts.append(self._pad(name, width))
        header_line = " │ ".join(parts)
        separator = "─" * (sum(w for _, w in self.columns) + 3 * (len(self.columns) - 1))
        return self._colorize(header_line, "bold") + "\n" + separator
    
    def row(self, values: List[Any], highlight: bool = False) -> str:
        """Generate table row."""
        parts = []
        for (_, width), value in zip(self.columns, values):
            parts.append(self._pad(str(value), width))
        line = " │ ".join(parts)
        if highlight:
            line = self._colorize(line, "bold")
        return line
    
    def footer(self, text: str) -> str:
        """Generate footer text."""
        return self._colorize(text, "dim")


def echo_success(message: str):
    """Print success message with checkmark."""
    click.echo(click.style(f"✅ {message}", fg="green"))


def echo_error(message: str):
    """Print error message."""
    click.echo(click.style(f"❌ {message}", fg="red"), err=True)


def echo_warning(message: str):
    """Print warning message."""
    click.echo(click.style(f"⚠️  {message}", fg="yellow"), err=True)


def echo_info(message: str):
    """Print info message."""
    click.echo(click.style(f"ℹ️  {message}", fg="blue"))


# ============================================================================
# CLI Group and Context
# ============================================================================

@click.group()
@click.option(
    "--data-dir",
    type=click.Path(path_type=Path),
    default=DEFAULT_DATA_DIR,
    envvar="RESLIB_DATA_DIR",
    help="Data directory for database and attachments."
)
@click.option(
    "--db",
    "db_path",
    type=click.Path(path_type=Path),
    default=None,
    envvar="RESLIB_DB",
    help="Database file path (overrides data-dir)."
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress non-essential output."
)
@click.option(
    "--json-output",
    is_flag=True,
    help="Output results as JSON."
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context, data_dir: Path, db_path: Optional[Path], quiet: bool, json_output: bool):
    """
    Research Library CLI - Manage your research materials.
    
    Organize PDFs, images, code, and other research materials with full-text
    search, cross-project linking, and confidence scoring.
    
    \b
    Quick Start:
      reslib add paper.pdf --project myproject --material-type reference
      reslib search "machine learning"
      reslib status
    """
    ctx.ensure_object(dict)
    
    # Set up paths
    data_dir.mkdir(parents=True, exist_ok=True)
    ctx.obj["data_dir"] = data_dir
    ctx.obj["db_path"] = db_path or (data_dir / "research.db")
    ctx.obj["attachments_dir"] = data_dir / "attachments"
    ctx.obj["backups_dir"] = data_dir / "backups"
    ctx.obj["quiet"] = quiet
    ctx.obj["json_output"] = json_output
    
    # Create directories
    ctx.obj["attachments_dir"].mkdir(parents=True, exist_ok=True)
    ctx.obj["backups_dir"].mkdir(parents=True, exist_ok=True)


# ============================================================================
# ADD Command
# ============================================================================

@cli.command("add")
@click.argument("path", type=str)
@click.option(
    "--project", "-p",
    required=True,
    help="Project ID to associate with this document."
)
@click.option(
    "--material-type", "-m",
    type=click.Choice(MATERIAL_TYPES),
    required=True,
    help="Type of material: reference (vetted) or research (working)."
)
@click.option(
    "--url", "-u",
    help="Source URL if the file was downloaded from the web."
)
@click.option(
    "--confidence", "-c",
    type=float,
    default=None,
    help="Confidence score (0.0-1.0). Auto-detected if not specified."
)
@click.option(
    "--title", "-t",
    help="Document title. Auto-generated from filename if not specified."
)
@click.option(
    "--tags",
    help="Comma-separated tags for the document."
)
@click.option(
    "--extract/--no-extract",
    default=True,
    help="Whether to extract text content from the file."
)
@click.pass_context
def add_document(
    ctx: click.Context,
    path: str,
    project: str,
    material_type: str,
    url: Optional[str],
    confidence: Optional[float],
    title: Optional[str],
    tags: Optional[str],
    extract: bool
):
    """
    Add a research document to the library.
    
    PATH can be a local file path or a URL. For URLs, the file will be
    downloaded first.
    
    \b
    Examples:
      reslib add paper.pdf -p myproject -m reference
      reslib add screenshot.png -p myproject -m research -c 0.3
      reslib add https://arxiv.org/pdf/1234.pdf -p ai-papers -m reference
    """
    conn = get_connection(ctx)
    attachments_dir = ctx.obj["attachments_dir"]
    quiet = ctx.obj["quiet"]
    json_output = ctx.obj["json_output"]
    
    # Validate confidence range
    if confidence is not None and (confidence < 0.0 or confidence > 1.0):
        echo_error("Confidence must be between 0.0 and 1.0")
        ctx.exit(1)
    
    # Ensure project exists
    validate_project_exists(conn, project)
    
    # Handle URL vs file path
    source_url = url
    if is_url(path):
        source_url = path
        # Download the file
        if not quiet and not json_output:
            echo_info(f"Downloading from {path}...")
        try:
            import urllib.request
            import tempfile
            
            # Create temp file with appropriate extension
            parsed = urlparse(path)
            ext = Path(parsed.path).suffix or ".bin"
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                urllib.request.urlretrieve(path, tmp.name)
                file_path = Path(tmp.name)
        except Exception as e:
            echo_error(f"Failed to download: {e}")
            ctx.exit(1)
    else:
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists():
            echo_error(f"File not found: {path}")
            ctx.exit(1)
    
    # Detect file type
    mime_type = detect_mime_type(file_path)
    file_hash = compute_file_hash(file_path)
    file_size = file_path.stat().st_size
    
    # Check for duplicate
    cursor = conn.execute(
        "SELECT id, title FROM documents WHERE file_hash = ? AND is_archived = 0",
        (file_hash,)
    )
    existing = cursor.fetchone()
    if existing:
        echo_warning(f"Duplicate detected: #{existing['id']} - {existing['title']}")
        if not click.confirm("Add anyway?"):
            ctx.exit(0)
    
    # Extract text content
    content_text = ""
    auto_confidence = 0.5
    if extract:
        if not quiet and not json_output:
            echo_info("Extracting text content...")
        content_text, auto_confidence = extract_text_from_file(file_path, mime_type)
    
    # Use provided confidence or auto-detected
    final_confidence = confidence if confidence is not None else auto_confidence
    
    # Generate title if not provided
    final_title = title or generate_title_from_path(file_path)
    
    # Parse tags
    tags_json = json.dumps(tags.split(",") if tags else [])
    
    # Copy file to attachments directory
    dest_dir = attachments_dir / project / datetime.now().strftime("%Y-%m")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{file_hash[:8]}_{file_path.name}"
    
    if not dest_path.exists():
        shutil.copy2(file_path, dest_path)
    
    # Insert document
    cursor = conn.execute(
        """
        INSERT INTO documents (
            title, material_type, project_id, source_path, source_url,
            mime_type, file_hash, content_text, confidence, tags
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            final_title, material_type, project, str(dest_path), source_url,
            mime_type, file_hash, content_text, final_confidence, tags_json
        )
    )
    doc_id = cursor.lastrowid
    
    # Create attachment record
    conn.execute(
        """
        INSERT INTO attachments (document_id, filename, file_path, mime_type, file_size, file_hash)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (doc_id, file_path.name, str(dest_path), mime_type, file_size, file_hash)
    )
    
    # Queue for extraction if needed (low confidence or binary file)
    if final_confidence < 0.5 or mime_type.startswith("image/") or mime_type == "application/pdf":
        conn.execute(
            "INSERT INTO extraction_queue (document_id) VALUES (?)",
            (doc_id,)
        )
    
    conn.commit()
    
    # Clean up temp file if downloaded
    if is_url(path):
        file_path.unlink(missing_ok=True)
    
    # Output result
    if json_output:
        click.echo(json.dumps({
            "id": doc_id,
            "title": final_title,
            "project": project,
            "material_type": material_type,
            "confidence": final_confidence,
            "mime_type": mime_type,
            "file_size": file_size,
        }))
    else:
        echo_success(f"Saved as research #{doc_id}")
        if not quiet:
            click.echo(f"   Title: {final_title}")
            click.echo(f"   Project: {project}")
            click.echo(f"   Type: {material_type}")
            click.echo(f"   Confidence: {final_confidence:.2f}")
            click.echo(f"   Size: {format_file_size(file_size)}")


# ============================================================================
# SEARCH Command
# ============================================================================

@cli.command("search")
@click.argument("query", required=True)
@click.option(
    "--project", "-p",
    help="Limit search to a specific project."
)
@click.option(
    "--all-projects", "-a",
    is_flag=True,
    help="Search across all projects (default behavior)."
)
@click.option(
    "--material", "-m",
    type=click.Choice(MATERIAL_TYPES),
    help="Filter by material type."
)
@click.option(
    "--confidence-min",
    type=float,
    default=0.0,
    help="Minimum confidence score filter."
)
@click.option(
    "--limit", "-n",
    type=int,
    default=20,
    help="Maximum number of results."
)
@click.option(
    "--include-archived",
    is_flag=True,
    help="Include archived documents in results."
)
@click.pass_context
def search_documents(
    ctx: click.Context,
    query: str,
    project: Optional[str],
    all_projects: bool,
    material: Optional[str],
    confidence_min: float,
    limit: int,
    include_archived: bool
):
    """
    Search for documents matching a query.
    
    Uses full-text search across titles, content, and tags.
    Results are sorted with references first, then by relevance.
    
    \b
    Examples:
      reslib search "neural networks"
      reslib search "python" -p code-snippets -m research
      reslib search "API" --confidence-min 0.7
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    start_time = time.time()
    
    # Build query
    sql_parts = ["""
        SELECT d.id, d.title, d.material_type, d.confidence, d.project_id,
               d.created_at, d.mime_type,
               highlight(documents_fts, 1, '[', ']') as snippet
        FROM documents_fts
        JOIN documents d ON documents_fts.rowid = d.id
        WHERE documents_fts MATCH ?
    """]
    params: List[Any] = [query]
    
    # Apply filters
    if not include_archived:
        sql_parts.append("AND d.is_archived = 0")
    
    if project and not all_projects:
        sql_parts.append("AND d.project_id = ?")
        params.append(project)
    
    if material:
        sql_parts.append("AND d.material_type = ?")
        params.append(material)
    
    if confidence_min > 0:
        sql_parts.append("AND d.confidence >= ?")
        params.append(confidence_min)
    
    # Order: references first, then by FTS rank
    sql_parts.append("""
        ORDER BY 
            CASE d.material_type WHEN 'reference' THEN 0 ELSE 1 END,
            rank
        LIMIT ?
    """)
    params.append(limit)
    
    sql = "\n".join(sql_parts)
    
    try:
        cursor = conn.execute(sql, params)
        results = cursor.fetchall()
    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            echo_error("Search index not found. Try adding some documents first.")
        else:
            echo_error(f"Search error: {e}")
        ctx.exit(1)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    # Output results
    if json_output:
        output = {
            "query": query,
            "count": len(results),
            "elapsed_ms": round(elapsed_ms, 2),
            "results": [dict(row) for row in results]
        }
        click.echo(json.dumps(output, indent=2))
        return
    
    # Table output
    if not results:
        echo_info(f"No results found for '{query}'")
        return
    
    # Determine if we need project column (multiple projects in results)
    projects_in_results = set(r["project_id"] for r in results)
    show_project = len(projects_in_results) > 1 or (project and project not in projects_in_results)
    
    # Define columns
    if show_project:
        columns = [
            ("ID", 6),
            ("Title", 35),
            ("Material", 10),
            ("Conf", 6),
            ("Project", 12),
        ]
    else:
        columns = [
            ("ID", 6),
            ("Title", 45),
            ("Material", 10),
            ("Conf", 6),
        ]
    
    formatter = TableFormatter(columns)
    click.echo()
    click.echo(formatter.header())
    
    current_project = project
    for row in results:
        is_reference = row["material_type"] == "reference"
        project_display = row["project_id"]
        
        # Mark cross-project results
        if current_project and row["project_id"] != current_project:
            project_display = "(other)"
        
        if show_project:
            values = [
                f"#{row['id']}",
                truncate_text(row["title"], 35),
                row["material_type"],
                f"{row['confidence']:.2f}",
                truncate_text(project_display, 12),
            ]
        else:
            values = [
                f"#{row['id']}",
                truncate_text(row["title"], 45),
                row["material_type"],
                f"{row['confidence']:.2f}",
            ]
        
        click.echo(formatter.row(values, highlight=is_reference))
    
    click.echo()
    click.echo(formatter.footer(f"{len(results)} results found in {elapsed_ms:.1f}ms"))


# ============================================================================
# GET Command
# ============================================================================

@cli.command("get")
@click.argument("research_id", type=int)
@click.option(
    "--show-content/--no-content",
    default=False,
    help="Show extracted text content."
)
@click.option(
    "--show-links/--no-links",
    default=True,
    help="Show linked documents."
)
@click.pass_context
def get_document(ctx: click.Context, research_id: int, show_content: bool, show_links: bool):
    """
    Get detailed information about a document.
    
    \b
    Examples:
      reslib get 42
      reslib get 42 --show-content
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    # Fetch document
    cursor = conn.execute(
        """
        SELECT d.*, 
               (SELECT COUNT(*) FROM attachments WHERE document_id = d.id) as attachment_count
        FROM documents d
        WHERE d.id = ?
        """,
        (research_id,)
    )
    doc = cursor.fetchone()
    
    if not doc:
        echo_error(f"Document #{research_id} not found")
        ctx.exit(1)
    
    # Fetch attachments
    attachments = conn.execute(
        "SELECT * FROM attachments WHERE document_id = ?",
        (research_id,)
    ).fetchall()
    
    # Fetch links
    links_out = []
    links_in = []
    if show_links:
        links_out = conn.execute(
            """
            SELECT l.*, d.title as target_title, d.material_type as target_type
            FROM links l
            JOIN documents d ON l.target_id = d.id
            WHERE l.source_id = ?
            """,
            (research_id,)
        ).fetchall()
        
        links_in = conn.execute(
            """
            SELECT l.*, d.title as source_title, d.material_type as source_type
            FROM links l
            JOIN documents d ON l.source_id = d.id
            WHERE l.target_id = ?
            """,
            (research_id,)
        ).fetchall()
    
    # JSON output
    if json_output:
        output = dict(doc)
        output["attachments"] = [dict(a) for a in attachments]
        output["links_outgoing"] = [dict(l) for l in links_out]
        output["links_incoming"] = [dict(l) for l in links_in]
        click.echo(json.dumps(output, indent=2, default=str))
        return
    
    # Formatted output
    click.echo()
    click.echo(click.style(f"Document #{doc['id']}: {doc['title']}", bold=True))
    click.echo("=" * 60)
    
    click.echo(f"  Project:       {doc['project_id']}")
    click.echo(f"  Material Type: {doc['material_type']}")
    click.echo(f"  Confidence:    {doc['confidence']:.2f}")
    click.echo(f"  MIME Type:     {doc['mime_type']}")
    click.echo(f"  Created:       {format_timestamp(doc['created_at'])}")
    
    if doc["source_url"]:
        click.echo(f"  Source URL:    {doc['source_url']}")
    
    if doc["tags"]:
        tags = json.loads(doc["tags"])
        if tags:
            click.echo(f"  Tags:          {', '.join(tags)}")
    
    if doc["is_archived"]:
        click.echo(click.style(f"  Archived:      {format_timestamp(doc['archived_at'])}", fg="yellow"))
    
    # Attachments
    if attachments:
        click.echo()
        click.echo(click.style("Attachments:", bold=True))
        for att in attachments:
            size = format_file_size(att["file_size"]) if att["file_size"] else "?"
            click.echo(f"  • {att['filename']} ({size})")
    
    # Links
    if links_out:
        click.echo()
        click.echo(click.style("Links (outgoing):", bold=True))
        for link in links_out:
            click.echo(f"  → #{link['target_id']} {link['target_title']}")
            click.echo(f"    ({link['link_type']}, relevance: {link['relevance']:.2f})")
    
    if links_in:
        click.echo()
        click.echo(click.style("Links (incoming):", bold=True))
        for link in links_in:
            click.echo(f"  ← #{link['source_id']} {link['source_title']}")
            click.echo(f"    ({link['link_type']}, relevance: {link['relevance']:.2f})")
    
    # Content
    if show_content and doc["content_text"]:
        click.echo()
        click.echo(click.style("Content:", bold=True))
        click.echo("-" * 60)
        content = doc["content_text"]
        if len(content) > 2000:
            click.echo(content[:2000])
            click.echo(click.style(f"\n... (truncated, {len(content)} chars total)", dim=True))
        else:
            click.echo(content)
    
    click.echo()


# ============================================================================
# ARCHIVE Command
# ============================================================================

@cli.command("archive")
@click.argument("research_id", type=int)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Archive without confirmation."
)
@click.pass_context
def archive_document(ctx: click.Context, research_id: int, force: bool):
    """
    Archive a document (soft delete).
    
    Archived documents are hidden from search by default but can be
    restored later.
    
    \b
    Examples:
      reslib archive 42
      reslib archive 42 --force
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    # Check document exists
    cursor = conn.execute(
        "SELECT id, title, is_archived FROM documents WHERE id = ?",
        (research_id,)
    )
    doc = cursor.fetchone()
    
    if not doc:
        echo_error(f"Document #{research_id} not found")
        ctx.exit(1)
    
    if doc["is_archived"]:
        echo_warning(f"Document #{research_id} is already archived")
        ctx.exit(0)
    
    # Confirm
    if not force:
        click.echo(f"Archive '{doc['title']}' (#{research_id})?")
        if not click.confirm("Continue?"):
            ctx.exit(0)
    
    # Archive
    conn.execute(
        """
        UPDATE documents 
        SET is_archived = 1, archived_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (research_id,)
    )
    conn.commit()
    
    if json_output:
        click.echo(json.dumps({"id": research_id, "archived": True}))
    else:
        echo_success(f"Archived document #{research_id}")


# ============================================================================
# EXPORT Command
# ============================================================================

@cli.command("export")
@click.argument("research_id", type=int)
@click.option(
    "--format", "-f",
    "export_format",
    type=click.Choice(["json", "markdown"]),
    default="json",
    help="Export format."
)
@click.option(
    "--output", "-o",
    type=click.Path(path_type=Path),
    help="Output file path. Defaults to stdout."
)
@click.option(
    "--include-attachments/--no-attachments",
    default=False,
    help="Copy attachments to output directory."
)
@click.pass_context
def export_document(
    ctx: click.Context,
    research_id: int,
    export_format: str,
    output: Optional[Path],
    include_attachments: bool
):
    """
    Export a document in JSON or Markdown format.
    
    \b
    Examples:
      reslib export 42 --format json
      reslib export 42 --format markdown -o doc.md
      reslib export 42 --format json --include-attachments -o ./export/
    """
    conn = get_connection(ctx)
    
    # Fetch document with all related data
    cursor = conn.execute("SELECT * FROM documents WHERE id = ?", (research_id,))
    doc = cursor.fetchone()
    
    if not doc:
        echo_error(f"Document #{research_id} not found")
        ctx.exit(1)
    
    attachments = conn.execute(
        "SELECT * FROM attachments WHERE document_id = ?",
        (research_id,)
    ).fetchall()
    
    links = conn.execute(
        """
        SELECT l.*, 
               ds.title as source_title, dt.title as target_title
        FROM links l
        LEFT JOIN documents ds ON l.source_id = ds.id
        LEFT JOIN documents dt ON l.target_id = dt.id
        WHERE l.source_id = ? OR l.target_id = ?
        """,
        (research_id, research_id)
    ).fetchall()
    
    # Build export data
    doc_dict = dict(doc)
    doc_dict["tags"] = json.loads(doc["tags"]) if doc["tags"] else []
    doc_dict["attachments"] = [dict(a) for a in attachments]
    doc_dict["links"] = [dict(l) for l in links]
    
    # Generate output
    if export_format == "json":
        content = json.dumps(doc_dict, indent=2, default=str)
    else:
        # Markdown format
        lines = [
            f"# {doc['title']}",
            "",
            f"**ID:** #{doc['id']}  ",
            f"**Project:** {doc['project_id']}  ",
            f"**Material Type:** {doc['material_type']}  ",
            f"**Confidence:** {doc['confidence']:.2f}  ",
            f"**Created:** {format_timestamp(doc['created_at'])}  ",
            "",
        ]
        
        if doc["source_url"]:
            lines.append(f"**Source:** [{doc['source_url']}]({doc['source_url']})  ")
            lines.append("")
        
        tags = json.loads(doc["tags"]) if doc["tags"] else []
        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}  ")
            lines.append("")
        
        if attachments:
            lines.append("## Attachments")
            lines.append("")
            for att in attachments:
                size = format_file_size(att["file_size"]) if att["file_size"] else "unknown size"
                lines.append(f"- {att['filename']} ({size})")
            lines.append("")
        
        if links:
            lines.append("## Related Documents")
            lines.append("")
            for link in links:
                if link["source_id"] == research_id:
                    lines.append(f"- **{link['link_type']}** → #{link['target_id']} {link['target_title']}")
                else:
                    lines.append(f"- **{link['link_type']}** ← #{link['source_id']} {link['source_title']}")
            lines.append("")
        
        if doc["content_text"]:
            lines.append("## Content")
            lines.append("")
            lines.append(doc["content_text"])
            lines.append("")
        
        content = "\n".join(lines)
    
    # Write output
    if output:
        output = Path(output)
        if include_attachments:
            # Create directory and copy attachments
            output.mkdir(parents=True, exist_ok=True)
            output_file = output / f"document_{research_id}.{export_format}"
            
            for att in attachments:
                src = Path(att["file_path"])
                if src.exists():
                    dst = output / att["filename"]
                    shutil.copy2(src, dst)
        else:
            output_file = output
            output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_file.write_text(content)
        echo_success(f"Exported to {output_file}")
    else:
        click.echo(content)


# ============================================================================
# STATUS Command
# ============================================================================

@cli.command("status")
@click.pass_context
def show_status(ctx: click.Context):
    """
    Show system status and statistics.
    
    Displays document counts, storage usage, queue status, and backup info.
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    db_path = ctx.obj["db_path"]
    attachments_dir = ctx.obj["attachments_dir"]
    backups_dir = ctx.obj["backups_dir"]
    
    # Gather statistics
    stats = {}
    
    # Document counts
    stats["total_documents"] = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE is_archived = 0"
    ).fetchone()[0]
    
    stats["archived_documents"] = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE is_archived = 1"
    ).fetchone()[0]
    
    stats["reference_count"] = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE material_type = 'reference' AND is_archived = 0"
    ).fetchone()[0]
    
    stats["research_count"] = conn.execute(
        "SELECT COUNT(*) FROM documents WHERE material_type = 'research' AND is_archived = 0"
    ).fetchone()[0]
    
    # Attachments
    stats["total_attachments"] = conn.execute(
        "SELECT COUNT(*) FROM attachments"
    ).fetchone()[0]
    
    # Queue status
    queue_stats = conn.execute(
        """
        SELECT status, COUNT(*) as count
        FROM extraction_queue
        GROUP BY status
        """
    ).fetchall()
    stats["queue"] = {row["status"]: row["count"] for row in queue_stats}
    
    # Projects
    stats["project_count"] = conn.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]
    
    # Links
    stats["link_count"] = conn.execute(
        "SELECT COUNT(*) FROM links"
    ).fetchone()[0]
    
    # Storage sizes
    stats["db_size"] = db_path.stat().st_size if db_path.exists() else 0
    
    attachment_size = 0
    if attachments_dir.exists():
        for f in attachments_dir.rglob("*"):
            if f.is_file():
                attachment_size += f.stat().st_size
    stats["attachment_size"] = attachment_size
    
    # Backup info
    stats["backup_location"] = str(backups_dir)
    backup_files = sorted(backups_dir.glob("*.db")) if backups_dir.exists() else []
    if backup_files:
        last_backup = backup_files[-1]
        stats["last_backup"] = last_backup.stat().st_mtime
        stats["last_backup_file"] = last_backup.name
    else:
        stats["last_backup"] = None
        stats["last_backup_file"] = None
    
    # JSON output
    if json_output:
        click.echo(json.dumps(stats, indent=2, default=str))
        return
    
    # Formatted output
    click.echo()
    click.echo(click.style("📚 Research Library Status", bold=True))
    click.echo("=" * 40)
    
    click.echo()
    click.echo(click.style("Documents:", bold=True))
    click.echo(f"  Total:      {stats['total_documents']}")
    click.echo(f"  References: {stats['reference_count']}")
    click.echo(f"  Research:   {stats['research_count']}")
    click.echo(f"  Archived:   {stats['archived_documents']}")
    
    click.echo()
    click.echo(click.style("Organization:", bold=True))
    click.echo(f"  Projects:    {stats['project_count']}")
    click.echo(f"  Links:       {stats['link_count']}")
    click.echo(f"  Attachments: {stats['total_attachments']}")
    
    click.echo()
    click.echo(click.style("Storage:", bold=True))
    click.echo(f"  Database:    {format_file_size(stats['db_size'])}")
    click.echo(f"  Attachments: {format_file_size(stats['attachment_size'])}")
    click.echo(f"  Total:       {format_file_size(stats['db_size'] + stats['attachment_size'])}")
    
    click.echo()
    click.echo(click.style("Extraction Queue:", bold=True))
    if stats["queue"]:
        for status, count in stats["queue"].items():
            icon = {"pending": "⏳", "processing": "⚙️", "completed": "✅", "failed": "❌"}.get(status, "•")
            click.echo(f"  {icon} {status}: {count}")
    else:
        click.echo("  (empty)")
    
    click.echo()
    click.echo(click.style("Backups:", bold=True))
    click.echo(f"  Location: {stats['backup_location']}")
    if stats["last_backup"]:
        last_time = datetime.fromtimestamp(stats["last_backup"])
        click.echo(f"  Last:     {last_time.strftime('%Y-%m-%d %H:%M')} ({stats['last_backup_file']})")
    else:
        click.echo("  Last:     Never")
    
    click.echo()


# ============================================================================
# RESTORE Command
# ============================================================================

@cli.command("restore")
@click.argument("date", type=str)
@click.option(
    "--list", "list_backups",
    is_flag=True,
    help="List available backups instead of restoring."
)
@click.option(
    "--force", "-f",
    is_flag=True,
    help="Restore without confirmation."
)
@click.pass_context
def restore_backup(ctx: click.Context, date: str, list_backups: bool, force: bool):
    """
    Restore database from a backup.
    
    DATE should be in YYYY-MM-DD format. Use --list to see available backups.
    
    \b
    Examples:
      reslib restore --list
      reslib restore 2026-02-01
    """
    backups_dir = ctx.obj["backups_dir"]
    db_path = ctx.obj["db_path"]
    json_output = ctx.obj["json_output"]
    
    # List available backups
    if list_backups or date == "--list":
        backups = sorted(backups_dir.glob("*.db")) if backups_dir.exists() else []
        
        if json_output:
            click.echo(json.dumps([
                {"file": b.name, "date": b.stem.replace("research_", ""), "size": b.stat().st_size}
                for b in backups
            ], indent=2))
            return
        
        if not backups:
            echo_info("No backups found")
            return
        
        click.echo()
        click.echo(click.style("Available Backups:", bold=True))
        for backup in backups:
            size = format_file_size(backup.stat().st_size)
            date_str = backup.stem.replace("research_", "")
            click.echo(f"  • {date_str} ({size})")
        click.echo()
        return
    
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        echo_error("Date must be in YYYY-MM-DD format")
        ctx.exit(1)
    
    # Find backup file
    backup_file = backups_dir / f"research_{date}.db"
    if not backup_file.exists():
        echo_error(f"No backup found for {date}")
        echo_info("Use 'reslib restore --list' to see available backups")
        ctx.exit(1)
    
    # Confirm restore
    if not force:
        click.echo(f"Restore from backup: {backup_file.name}")
        click.echo(click.style("⚠️  This will overwrite the current database!", fg="yellow"))
        if not click.confirm("Continue?"):
            ctx.exit(0)
    
    # Close current connection
    if "conn" in ctx.obj:
        ctx.obj["conn"].close()
        del ctx.obj["conn"]
    
    # Create backup of current database
    if db_path.exists():
        current_backup = backups_dir / f"research_pre-restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_path, current_backup)
        echo_info(f"Current database backed up to {current_backup.name}")
    
    # Restore
    shutil.copy2(backup_file, db_path)
    
    if json_output:
        click.echo(json.dumps({"restored": True, "from": backup_file.name}))
    else:
        echo_success(f"Restored database from {backup_file.name}")


# ============================================================================
# LINK Command
# ============================================================================

@cli.command("link")
@click.argument("source_id", type=int)
@click.argument("target_id", type=int)
@click.option(
    "--type", "-t",
    "link_type",
    type=click.Choice(LINK_TYPES),
    required=True,
    help="Type of relationship."
)
@click.option(
    "--relevance", "-r",
    type=float,
    default=0.5,
    help="Relevance score (0.0-1.0)."
)
@click.option(
    "--notes",
    help="Notes about this relationship."
)
@click.option(
    "--bidirectional", "-b",
    is_flag=True,
    help="Create link in both directions."
)
@click.pass_context
def link_documents(
    ctx: click.Context,
    source_id: int,
    target_id: int,
    link_type: str,
    relevance: float,
    notes: Optional[str],
    bidirectional: bool
):
    """
    Create a relationship link between two documents.
    
    \b
    Link Types:
      applies_to  - Source applies to or supports target
      contradicts - Source contradicts or refutes target
      supersedes  - Source replaces or updates target
      related     - General relationship
    
    \b
    Examples:
      reslib link 42 43 --type applies_to
      reslib link 42 43 --type supersedes --relevance 0.9
      reslib link 42 43 --type related --bidirectional
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    # Validate relevance
    if relevance < 0.0 or relevance > 1.0:
        echo_error("Relevance must be between 0.0 and 1.0")
        ctx.exit(1)
    
    # Check both documents exist
    for doc_id in [source_id, target_id]:
        cursor = conn.execute("SELECT id, title FROM documents WHERE id = ?", (doc_id,))
        if not cursor.fetchone():
            echo_error(f"Document #{doc_id} not found")
            ctx.exit(1)
    
    # Prevent self-links
    if source_id == target_id:
        echo_error("Cannot link a document to itself")
        ctx.exit(1)
    
    # Create link
    try:
        conn.execute(
            """
            INSERT INTO links (source_id, target_id, link_type, relevance, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (source_id, target_id, link_type, relevance, notes)
        )
        
        if bidirectional:
            # Create reverse link with 'related' type (most relationships aren't symmetric)
            reverse_type = "related" if link_type in ("applies_to", "supersedes", "contradicts") else link_type
            try:
                conn.execute(
                    """
                    INSERT INTO links (source_id, target_id, link_type, relevance, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (target_id, source_id, reverse_type, relevance, notes)
                )
            except sqlite3.IntegrityError:
                pass  # Reverse link already exists
        
        conn.commit()
        
    except sqlite3.IntegrityError:
        echo_error(f"Link already exists between #{source_id} and #{target_id} ({link_type})")
        ctx.exit(1)
    
    if json_output:
        click.echo(json.dumps({
            "source_id": source_id,
            "target_id": target_id,
            "link_type": link_type,
            "relevance": relevance,
            "bidirectional": bidirectional,
        }))
    else:
        echo_success(f"Linked #{source_id} → #{target_id} ({link_type})")
        if bidirectional:
            echo_info(f"Also created reverse link #{target_id} → #{source_id}")


# ============================================================================
# Additional Utility Commands
# ============================================================================

@cli.command("projects")
@click.option("--create", "-c", help="Create a new project with this ID.")
@click.option("--name", "-n", help="Name for the new project.")
@click.option("--description", "-d", help="Description for the new project.")
@click.pass_context
def manage_projects(
    ctx: click.Context,
    create: Optional[str],
    name: Optional[str],
    description: Optional[str]
):
    """
    List or create projects.
    
    \b
    Examples:
      reslib projects
      reslib projects --create ml-papers --name "Machine Learning Papers"
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    if create:
        # Create project
        project_name = name or create.replace("-", " ").title()
        try:
            conn.execute(
                "INSERT INTO projects (id, name, description) VALUES (?, ?, ?)",
                (create, project_name, description)
            )
            conn.commit()
            echo_success(f"Created project '{create}'")
        except sqlite3.IntegrityError:
            echo_error(f"Project '{create}' already exists")
            ctx.exit(1)
        return
    
    # List projects
    cursor = conn.execute(
        """
        SELECT p.*, 
               (SELECT COUNT(*) FROM documents WHERE project_id = p.id AND is_archived = 0) as doc_count
        FROM projects p
        ORDER BY p.created_at DESC
        """
    )
    projects = cursor.fetchall()
    
    if json_output:
        click.echo(json.dumps([dict(p) for p in projects], indent=2))
        return
    
    if not projects:
        echo_info("No projects found. Create one with 'reslib projects --create <id>'")
        return
    
    click.echo()
    click.echo(click.style("Projects:", bold=True))
    for p in projects:
        click.echo(f"  • {p['id']} ({p['doc_count']} docs)")
        if p["name"] != p["id"]:
            click.echo(f"    Name: {p['name']}")
        if p["description"]:
            click.echo(f"    {p['description']}")
    click.echo()


@cli.command("unarchive")
@click.argument("research_id", type=int)
@click.pass_context
def unarchive_document(ctx: click.Context, research_id: int):
    """
    Restore an archived document.
    
    \b
    Examples:
      reslib unarchive 42
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    cursor = conn.execute(
        "SELECT id, title, is_archived FROM documents WHERE id = ?",
        (research_id,)
    )
    doc = cursor.fetchone()
    
    if not doc:
        echo_error(f"Document #{research_id} not found")
        ctx.exit(1)
    
    if not doc["is_archived"]:
        echo_warning(f"Document #{research_id} is not archived")
        ctx.exit(0)
    
    conn.execute(
        """
        UPDATE documents 
        SET is_archived = 0, archived_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (research_id,)
    )
    conn.commit()
    
    if json_output:
        click.echo(json.dumps({"id": research_id, "unarchived": True}))
    else:
        echo_success(f"Restored document #{research_id}")


@cli.command("backup")
@click.option("--name", "-n", help="Custom backup name (default: date-based).")
@click.pass_context
def create_backup(ctx: click.Context, name: Optional[str]):
    """
    Create a backup of the database.
    
    \b
    Examples:
      reslib backup
      reslib backup --name before-major-import
    """
    db_path = ctx.obj["db_path"]
    backups_dir = ctx.obj["backups_dir"]
    json_output = ctx.obj["json_output"]
    
    if not db_path.exists():
        echo_error("No database to backup")
        ctx.exit(1)
    
    # Close connection to ensure clean backup
    if "conn" in ctx.obj:
        ctx.obj["conn"].close()
        del ctx.obj["conn"]
    
    # Generate backup name
    if name:
        backup_name = f"research_{name}.db"
    else:
        backup_name = f"research_{datetime.now().strftime('%Y-%m-%d')}.db"
    
    backup_path = backups_dir / backup_name
    
    # Check for existing backup
    if backup_path.exists():
        if not click.confirm(f"Backup '{backup_name}' already exists. Overwrite?"):
            ctx.exit(0)
    
    shutil.copy2(db_path, backup_path)
    
    if json_output:
        click.echo(json.dumps({
            "backup": backup_name,
            "size": backup_path.stat().st_size,
            "path": str(backup_path),
        }))
    else:
        echo_success(f"Created backup: {backup_name}")
        click.echo(f"   Size: {format_file_size(backup_path.stat().st_size)}")
        click.echo(f"   Path: {backup_path}")


@cli.command("tags")
@click.argument("research_id", type=int)
@click.option("--add", "-a", multiple=True, help="Add tags.")
@click.option("--remove", "-r", multiple=True, help="Remove tags.")
@click.option("--set", "set_tags", help="Replace all tags (comma-separated).")
@click.pass_context
def manage_tags(
    ctx: click.Context,
    research_id: int,
    add: Tuple[str, ...],
    remove: Tuple[str, ...],
    set_tags: Optional[str]
):
    """
    View or modify tags on a document.
    
    \b
    Examples:
      reslib tags 42
      reslib tags 42 --add important --add review
      reslib tags 42 --remove obsolete
      reslib tags 42 --set "ml,python,tutorial"
    """
    conn = get_connection(ctx)
    json_output = ctx.obj["json_output"]
    
    cursor = conn.execute(
        "SELECT id, title, tags FROM documents WHERE id = ?",
        (research_id,)
    )
    doc = cursor.fetchone()
    
    if not doc:
        echo_error(f"Document #{research_id} not found")
        ctx.exit(1)
    
    current_tags = set(json.loads(doc["tags"]) if doc["tags"] else [])
    
    # Just viewing
    if not add and not remove and not set_tags:
        if json_output:
            click.echo(json.dumps({"id": research_id, "tags": list(current_tags)}))
        else:
            if current_tags:
                click.echo(f"Tags for #{research_id}: {', '.join(sorted(current_tags))}")
            else:
                click.echo(f"No tags on #{research_id}")
        return
    
    # Modifying
    if set_tags:
        current_tags = set(t.strip() for t in set_tags.split(",") if t.strip())
    else:
        current_tags.update(add)
        current_tags -= set(remove)
    
    tags_json = json.dumps(sorted(current_tags))
    conn.execute(
        "UPDATE documents SET tags = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (tags_json, research_id)
    )
    conn.commit()
    
    if json_output:
        click.echo(json.dumps({"id": research_id, "tags": sorted(current_tags)}))
    else:
        echo_success(f"Updated tags for #{research_id}")
        if current_tags:
            click.echo(f"   Tags: {', '.join(sorted(current_tags))}")
        else:
            click.echo("   (no tags)")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    cli()
