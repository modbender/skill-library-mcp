"""
Research Library - Full-Text Search with Ranking

Provides FTS5-based search across research entries and attachments with:
- Material type weighting (Reference > Research)
- Confidence-based ranking
- Recency scoring
- Project-scoped searches
- Cross-project linked research traversal

Architecture:
    ResearchSearch connects to SQLite database with FTS5 virtual tables:
    - research_fts: Full-text index on research entries
    - attachments_fts: Full-text index on extracted attachment content

    Search results are ranked using the formula:
        score = (fts5_score × material_weight) + (confidence × 0.3) + (recency × 0.2)

Usage:
    from reslib import ResearchSearch
    
    searcher = ResearchSearch(db_path="~/.openclaw/research/library.db")
    
    # Basic search
    results = searcher.search("servo tuning")
    
    # Project-scoped search
    results = searcher.search_project("rc-quadcopter", "motor spec")
    
    # Cross-project search
    results = searcher.search_all_projects("PID controller")
    
    # Get linked research
    linked = searcher.get_linked_research(42)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple, Iterator
from pathlib import Path
import sqlite3
import os
import logging

from .ranking import (
    compute_rank_score,
    validate_material_type,
    score_confidence,
    get_material_weight,
    RankComponents,
    ResearchRanking,
    MATERIAL_WEIGHTS,
    CONFIDENCE_WEIGHT,
    RECENCY_WEIGHT,
)


# ==============================================================================
# LOGGING
# ==============================================================================

logger = logging.getLogger(__name__)


# ==============================================================================
# RESULT DATA CLASSES
# ==============================================================================

@dataclass
class SearchResult:
    """
    A single search result from the research library.
    
    Attributes:
        research_id: Unique ID of the research entry
        title: Research entry title
        content: Research content (may be truncated)
        summary: Optional summary field
        project_id: Project this research belongs to
        material_type: 'reference' or 'research'
        confidence: Document confidence score (0.0-1.0)
        catalog: 'real_world' or 'openclaw'
        created_at: Creation timestamp
        updated_at: Last update timestamp
        fts5_score: Raw FTS5 relevance score
        rank_score: Computed ranking score
        source_type: 'research' or 'attachment'
        attachment_id: If source_type='attachment', the attachment ID
        attachment_filename: If source_type='attachment', the filename
        snippet: Text snippet showing match context
    """
    research_id: int
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    project_id: str = "uncategorized"
    material_type: str = "research"
    confidence: float = 0.5
    catalog: str = "real_world"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    fts5_score: float = 0.0
    rank_score: float = 0.0
    source_type: str = "research"
    attachment_id: Optional[int] = None
    attachment_filename: Optional[str] = None
    snippet: Optional[str] = None
    rank_components: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "research_id": self.research_id,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "project_id": self.project_id,
            "material_type": self.material_type,
            "confidence": self.confidence,
            "catalog": self.catalog,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "fts5_score": self.fts5_score,
            "rank_score": self.rank_score,
            "source_type": self.source_type,
            "attachment_id": self.attachment_id,
            "attachment_filename": self.attachment_filename,
            "snippet": self.snippet,
            "rank_components": self.rank_components,
        }
    
    def __repr__(self) -> str:
        mat = "REF" if self.material_type == "reference" else "RES"
        return f"SearchResult(id={self.research_id}, title='{self.title[:30]}...', {mat}, score={self.rank_score:.3f})"


@dataclass
class LinkedResult:
    """
    A linked research entry from research_links table.
    
    Attributes:
        link_id: ID of the link record
        source_research_id: Source research entry ID
        target_research_id: Target research entry ID
        link_type: Type of relationship
        relevance_score: Link relevance (0.0-1.0)
        reason: Why the link was created
        research_title: Title of the linked research
        research_project_id: Project of the linked research
        research_material_type: Material type of linked research
        research_confidence: Confidence of linked research
    """
    link_id: int
    source_research_id: int
    target_research_id: int
    link_type: str
    relevance_score: float
    reason: Optional[str]
    research_title: str
    research_project_id: str
    research_material_type: str
    research_confidence: float
    created_at: Optional[str] = None
    agent_role: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "link_id": self.link_id,
            "source_research_id": self.source_research_id,
            "target_research_id": self.target_research_id,
            "link_type": self.link_type,
            "relevance_score": self.relevance_score,
            "reason": self.reason,
            "research_title": self.research_title,
            "research_project_id": self.research_project_id,
            "research_material_type": self.research_material_type,
            "research_confidence": self.research_confidence,
            "created_at": self.created_at,
            "agent_role": self.agent_role,
        }


@dataclass
class FileUsage:
    """
    Information about which research entries reference an attachment.
    
    Attributes:
        attachment_id: The attachment being queried
        filename: Attachment filename
        research_entries: List of research entries referencing this attachment
        total_references: Count of references
    """
    attachment_id: int
    filename: str
    research_entries: List[Dict[str, Any]] = field(default_factory=list)
    total_references: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "attachment_id": self.attachment_id,
            "filename": self.filename,
            "research_entries": self.research_entries,
            "total_references": self.total_references,
        }


# ==============================================================================
# FTS5 QUERY UTILITIES
# ==============================================================================

def sanitize_fts5_query(query: str) -> str:
    """
    Sanitize a user query for FTS5 MATCH.
    
    FTS5 has special syntax characters that need escaping or handling:
    - Quotes: Must be balanced
    - Special operators: AND, OR, NOT, NEAR
    - Prefix matching: term*
    - Column filters: column:term
    
    This function:
    1. Strips leading/trailing whitespace
    2. Escapes quotes if unbalanced
    3. Wraps terms in quotes if they contain special chars
    
    Args:
        query: Raw user query string
        
    Returns:
        Sanitized query safe for FTS5 MATCH
    """
    if not query:
        return ""
    
    query = query.strip()
    
    # Count quotes - if odd, escape the last one
    quote_count = query.count('"')
    if quote_count % 2 != 0:
        # Unbalanced quotes - escape them all for safety
        query = query.replace('"', '""')
    
    # Check for FTS5 special characters that might cause issues
    # If query contains only alphanumeric and spaces, it's safe
    safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ")
    if not all(c in safe_chars for c in query):
        # Has special chars - wrap each term in quotes
        terms = query.split()
        quoted_terms = []
        for term in terms:
            # Keep AND, OR, NOT as operators
            if term.upper() in ("AND", "OR", "NOT"):
                quoted_terms.append(term.upper())
            else:
                # Quote the term
                escaped = term.replace('"', '""')
                quoted_terms.append(f'"{escaped}"')
        query = " ".join(quoted_terms)
    
    return query


def build_fts5_query(
    terms: List[str],
    operator: str = "AND",
    prefix_match: bool = False,
) -> str:
    """
    Build an FTS5 query from a list of terms.
    
    Args:
        terms: List of search terms
        operator: 'AND' or 'OR' to combine terms
        prefix_match: If True, add * suffix for prefix matching
        
    Returns:
        FTS5 query string
        
    Examples:
        >>> build_fts5_query(['servo', 'tuning'])
        '"servo" AND "tuning"'
        >>> build_fts5_query(['servo', 'motor'], operator='OR')
        '"servo" OR "motor"'
        >>> build_fts5_query(['servo'], prefix_match=True)
        '"servo"*'
    """
    if not terms:
        return ""
    
    operator = operator.upper()
    if operator not in ("AND", "OR"):
        operator = "AND"
    
    quoted_terms = []
    for term in terms:
        term = term.strip()
        if not term:
            continue
        # Escape internal quotes
        escaped = term.replace('"', '""')
        if prefix_match:
            quoted_terms.append(f'"{escaped}"*')
        else:
            quoted_terms.append(f'"{escaped}"')
    
    return f" {operator} ".join(quoted_terms)


def extract_snippet(
    content: str,
    query_terms: List[str],
    max_length: int = 200,
    context_words: int = 10,
) -> str:
    """
    Extract a snippet from content showing query term context.
    
    Args:
        content: Full content text
        query_terms: Terms to highlight context for
        max_length: Maximum snippet length
        context_words: Words of context around match
        
    Returns:
        Snippet string with ellipsis if truncated
    """
    if not content:
        return ""
    
    content_lower = content.lower()
    words = content.split()
    
    # Find first matching term
    match_idx = None
    for term in query_terms:
        term_lower = term.lower()
        for i, word in enumerate(words):
            if term_lower in word.lower():
                match_idx = i
                break
        if match_idx is not None:
            break
    
    if match_idx is None:
        # No match found - return start of content
        snippet = " ".join(words[:context_words * 2])
        if len(words) > context_words * 2:
            snippet += "..."
        return snippet[:max_length]
    
    # Extract context around match
    start = max(0, match_idx - context_words)
    end = min(len(words), match_idx + context_words + 1)
    
    snippet_words = words[start:end]
    snippet = " ".join(snippet_words)
    
    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(words):
        snippet = snippet + "..."
    
    return snippet[:max_length]


# ==============================================================================
# DATABASE UTILITIES
# ==============================================================================

def get_age_days(timestamp: Optional[str]) -> int:
    """
    Calculate age in days from a timestamp string.
    
    Args:
        timestamp: ISO format timestamp string
        
    Returns:
        Age in days (0 if timestamp is None or invalid)
    """
    if not timestamp:
        return 0
    
    try:
        if isinstance(timestamp, datetime):
            dt = timestamp
        else:
            # Handle ISO format with optional timezone
            timestamp = timestamp.replace("Z", "+00:00")
            dt = datetime.fromisoformat(timestamp)
        
        now = datetime.now()
        
        # Make both naive or both aware for comparison
        if dt.tzinfo is not None and now.tzinfo is None:
            dt = dt.replace(tzinfo=None)
        
        delta = now - dt
        return max(0, delta.days)
    except (ValueError, TypeError):
        return 0


# ==============================================================================
# MAIN SEARCH CLASS
# ==============================================================================

class ResearchSearch:
    """
    Full-text search engine for the research library.
    
    Provides FTS5-based search with:
    - Material type weighting (Reference > Research)
    - Confidence-based ranking
    - Recency scoring
    - Project scoping
    - Cross-project link traversal
    
    Usage:
        # Initialize with database path
        searcher = ResearchSearch("~/.openclaw/research/library.db")
        
        # Basic search
        results = searcher.search("servo tuning")
        
        # Filtered search
        results = searcher.search(
            "motor control",
            project_id="rc-quadcopter",
            material_type="reference",
            confidence_min=0.7
        )
        
        # Get linked research
        links = searcher.get_linked_research(42)
        
        # Check file usage
        usage = searcher.get_file_usage(123)
    """
    
    def __init__(
        self,
        db_path: str = "~/.openclaw/research/library.db",
        create_if_missing: bool = True,
        ranking: Optional[ResearchRanking] = None,
    ):
        """
        Initialize the search engine.
        
        Args:
            db_path: Path to SQLite database
            create_if_missing: If True, create database with schema if missing
            ranking: Custom ResearchRanking instance (uses default if None)
        """
        self.db_path = os.path.expanduser(db_path)
        self.create_if_missing = create_if_missing
        self.ranking = ranking or ResearchRanking()
        self._connection: Optional[sqlite3.Connection] = None
        
        # Ensure parent directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Initialize database if needed
        if create_if_missing and not os.path.exists(self.db_path):
            self._create_schema()
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get or create database connection.
        
        Returns:
            sqlite3.Connection with row_factory set
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection
    
    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def _create_schema(self):
        """
        Create database schema if tables don't exist.
        
        Creates:
        - research table
        - research_fts FTS5 virtual table
        - attachments table
        - attachments_fts FTS5 virtual table
        - research_links table
        - All required indexes and triggers
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Research table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                summary TEXT,
                confidence REAL DEFAULT 0.5 CHECK (confidence >= 0.0 AND confidence <= 1.0),
                project_id TEXT NOT NULL DEFAULT 'uncategorized',
                material_type TEXT DEFAULT 'research' CHECK (material_type IN ('reference', 'research')),
                catalog TEXT DEFAULT 'real_world' CHECK (catalog IN ('real_world', 'openclaw')),
                source_url TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                archived INTEGER NOT NULL DEFAULT 0
            )
        """)
        
        # Research FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS research_fts USING fts5(
                title,
                content,
                summary,
                content=research,
                content_rowid=id,
                tokenize='porter unicode61'
            )
        """)
        
        # FTS5 triggers for research
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS research_fts_insert AFTER INSERT ON research BEGIN
                INSERT INTO research_fts(rowid, title, content, summary)
                VALUES (new.id, new.title, new.content, new.summary);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS research_fts_delete AFTER DELETE ON research BEGIN
                INSERT INTO research_fts(research_fts, rowid, title, content, summary)
                VALUES ('delete', old.id, old.title, old.content, old.summary);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS research_fts_update AFTER UPDATE ON research BEGIN
                INSERT INTO research_fts(research_fts, rowid, title, content, summary)
                VALUES ('delete', old.id, old.title, old.content, old.summary);
                INSERT INTO research_fts(rowid, title, content, summary)
                VALUES (new.id, new.title, new.content, new.summary);
            END
        """)
        
        # Attachments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                research_id INTEGER NOT NULL REFERENCES research(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                filetype TEXT NOT NULL,
                mime_type TEXT,
                path TEXT NOT NULL UNIQUE,
                sha256_checksum TEXT NOT NULL,
                size_kb INTEGER NOT NULL CHECK (size_kb > 0),
                extracted_text TEXT,
                extraction_confidence REAL DEFAULT 0.0 CHECK (extraction_confidence >= 0.0 AND extraction_confidence <= 1.0),
                extraction_language TEXT DEFAULT 'en',
                extracted_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                archived INTEGER NOT NULL DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Attachments FTS5 virtual table
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS attachments_fts USING fts5(
                filename,
                extracted_text,
                content=attachments,
                content_rowid=id,
                tokenize='porter unicode61'
            )
        """)
        
        # FTS5 triggers for attachments
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS attachments_fts_insert AFTER INSERT ON attachments BEGIN
                INSERT INTO attachments_fts(rowid, filename, extracted_text)
                VALUES (new.id, new.filename, new.extracted_text);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS attachments_fts_delete AFTER DELETE ON attachments BEGIN
                INSERT INTO attachments_fts(attachments_fts, rowid, filename, extracted_text)
                VALUES ('delete', old.id, old.filename, old.extracted_text);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS attachments_fts_update AFTER UPDATE ON attachments BEGIN
                INSERT INTO attachments_fts(attachments_fts, rowid, filename, extracted_text)
                VALUES ('delete', old.id, old.filename, old.extracted_text);
                INSERT INTO attachments_fts(rowid, filename, extracted_text)
                VALUES (new.id, new.filename, new.extracted_text);
            END
        """)
        
        # Research links table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_research_id INTEGER NOT NULL REFERENCES research(id) ON DELETE CASCADE,
                target_research_id INTEGER NOT NULL REFERENCES research(id) ON DELETE CASCADE,
                link_type TEXT NOT NULL CHECK (link_type IN (
                    'applies_to', 'contradicts', 'supersedes', 'related', 'references'
                )),
                relevance_score REAL DEFAULT 0.5 CHECK (relevance_score >= 0.0 AND relevance_score <= 1.0),
                agent_role TEXT,
                reason TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(source_research_id, target_research_id, link_type)
            )
        """)
        
        # Indexes for research table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_project ON research(project_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_project_type ON research(project_id, material_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_catalog ON research(catalog)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_project_created ON research(project_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_archived ON research(archived)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_updated ON research(updated_at DESC)")
        
        # Indexes for attachments table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_research ON attachments(research_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_filetype ON attachments(filetype)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_created ON attachments(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_sha256 ON attachments(sha256_checksum)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attachments_archived ON attachments(archived)")
        
        # Indexes for research_links table
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_links_source ON research_links(source_research_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_links_target ON research_links(target_research_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_links_type ON research_links(link_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_research_links_source_type ON research_links(source_research_id, link_type)")
        
        conn.commit()
        logger.info(f"Created database schema at {self.db_path}")
    
    # ==========================================================================
    # MAIN SEARCH METHODS
    # ==========================================================================
    
    def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        material_type: Optional[str] = None,
        confidence_min: float = 0.0,
        catalog: Optional[str] = None,
        include_attachments: bool = True,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False,
        debug: bool = False,
    ) -> List[SearchResult]:
        """
        Full-text search across research entries and attachments.
        
        Searches both research_fts and attachments_fts, combines results,
        and ranks using the weighted formula:
            score = (fts5 × material_weight) + (confidence × 0.3) + (recency × 0.2)
        
        Args:
            query: Search query string
            project_id: Filter to specific project (None = all projects)
            material_type: Filter to 'reference' or 'research' (None = both)
            confidence_min: Minimum confidence threshold (0.0-1.0)
            catalog: Filter to 'real_world' or 'openclaw' (None = both)
            include_attachments: If True, also search attachment content
            limit: Maximum results to return
            offset: Result offset for pagination
            include_archived: If True, include archived entries
            debug: If True, include rank component breakdown
            
        Returns:
            List of SearchResult sorted by rank_score (highest first)
            
        Examples:
            >>> searcher.search("servo tuning")
            [SearchResult(id=1, title='Servo Tuning Guide', REF, score=0.82), ...]
            
            >>> searcher.search("motor", project_id="rc-quadcopter")
            [SearchResult(id=5, title='Motor Specs', REF, score=0.75), ...]
            
            >>> searcher.search("PID", material_type="reference", confidence_min=0.8)
            [SearchResult(id=2, title='PID Controller Reference', REF, score=0.91), ...]
        """
        if not query or not query.strip():
            return []
        
        # Sanitize query for FTS5
        fts5_query = sanitize_fts5_query(query)
        query_terms = query.lower().split()
        
        conn = self._get_connection()
        results: List[SearchResult] = []
        
        # Search research entries
        research_results = self._search_research(
            conn=conn,
            fts5_query=fts5_query,
            query_terms=query_terms,
            project_id=project_id,
            material_type=material_type,
            confidence_min=confidence_min,
            catalog=catalog,
            include_archived=include_archived,
            debug=debug,
        )
        results.extend(research_results)
        
        # Search attachments
        if include_attachments:
            attachment_results = self._search_attachments(
                conn=conn,
                fts5_query=fts5_query,
                query_terms=query_terms,
                project_id=project_id,
                material_type=material_type,
                confidence_min=confidence_min,
                catalog=catalog,
                include_archived=include_archived,
                debug=debug,
            )
            results.extend(attachment_results)
        
        # Sort by rank_score (highest first), then by updated_at (tie-breaker)
        results = self.ranking.sort_results(
            results,
            score_key="rank_score",
            updated_key="updated_at",
            reverse=True,
        )
        
        # Apply pagination
        paginated = results[offset:offset + limit]
        
        return paginated
    
    def _search_research(
        self,
        conn: sqlite3.Connection,
        fts5_query: str,
        query_terms: List[str],
        project_id: Optional[str],
        material_type: Optional[str],
        confidence_min: float,
        catalog: Optional[str],
        include_archived: bool,
        debug: bool,
    ) -> List[SearchResult]:
        """
        Search research_fts and return ranked results.
        """
        # Build query with filters
        # Note: FTS5 rank column must be accessed via table name, not alias
        sql = """
            SELECT 
                r.id,
                r.title,
                r.content,
                r.summary,
                r.project_id,
                r.material_type,
                r.confidence,
                r.catalog,
                r.created_at,
                r.updated_at,
                research_fts.rank as fts5_score
            FROM research r
            JOIN research_fts ON r.id = research_fts.rowid
            WHERE research_fts MATCH ?
        """
        params: List[Any] = [fts5_query]
        
        # Apply filters
        if not include_archived:
            sql += " AND r.archived = 0"
        
        if project_id:
            sql += " AND r.project_id = ?"
            params.append(project_id)
        
        if material_type:
            sql += " AND r.material_type = ?"
            params.append(material_type)
        
        if confidence_min > 0:
            sql += " AND r.confidence >= ?"
            params.append(confidence_min)
        
        if catalog:
            sql += " AND r.catalog = ?"
            params.append(catalog)
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            logger.warning(f"FTS5 query error: {e}")
            return []
        
        results = []
        for row in rows:
            # Compute rank score
            age_days = get_age_days(row["updated_at"])
            
            if debug:
                score, components = compute_rank_score(
                    fts5_score=row["fts5_score"],
                    material_type=row["material_type"],
                    confidence=row["confidence"],
                    age_days=age_days,
                    return_components=True,
                )
                rank_components = components.to_dict()
            else:
                score = compute_rank_score(
                    fts5_score=row["fts5_score"],
                    material_type=row["material_type"],
                    confidence=row["confidence"],
                    age_days=age_days,
                )
                rank_components = None
            
            # Extract snippet
            content = row["content"] or row["summary"] or ""
            snippet = extract_snippet(content, query_terms)
            
            result = SearchResult(
                research_id=row["id"],
                title=row["title"],
                content=row["content"],
                summary=row["summary"],
                project_id=row["project_id"],
                material_type=row["material_type"],
                confidence=row["confidence"],
                catalog=row["catalog"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                fts5_score=row["fts5_score"],
                rank_score=score,
                source_type="research",
                snippet=snippet,
                rank_components=rank_components,
            )
            results.append(result)
        
        return results
    
    def _search_attachments(
        self,
        conn: sqlite3.Connection,
        fts5_query: str,
        query_terms: List[str],
        project_id: Optional[str],
        material_type: Optional[str],
        confidence_min: float,
        catalog: Optional[str],
        include_archived: bool,
        debug: bool,
    ) -> List[SearchResult]:
        """
        Search attachments_fts and return ranked results.
        
        Results inherit material_type and confidence from parent research entry.
        """
        # Note: FTS5 rank column must be accessed via table name, not alias
        sql = """
            SELECT 
                r.id as research_id,
                r.title,
                r.content,
                r.summary,
                r.project_id,
                r.material_type,
                r.confidence,
                r.catalog,
                r.created_at,
                r.updated_at,
                a.id as attachment_id,
                a.filename,
                a.extracted_text,
                a.extraction_confidence,
                attachments_fts.rank as fts5_score
            FROM attachments a
            JOIN attachments_fts ON a.id = attachments_fts.rowid
            JOIN research r ON a.research_id = r.id
            WHERE attachments_fts MATCH ?
              AND a.extracted_text IS NOT NULL
        """
        params: List[Any] = [fts5_query]
        
        # Apply filters
        if not include_archived:
            sql += " AND a.archived = 0 AND r.archived = 0"
        
        if project_id:
            sql += " AND r.project_id = ?"
            params.append(project_id)
        
        if material_type:
            sql += " AND r.material_type = ?"
            params.append(material_type)
        
        if confidence_min > 0:
            sql += " AND r.confidence >= ?"
            params.append(confidence_min)
        
        if catalog:
            sql += " AND r.catalog = ?"
            params.append(catalog)
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            logger.warning(f"FTS5 attachment query error: {e}")
            return []
        
        results = []
        for row in rows:
            # Compute rank score using parent research's properties
            age_days = get_age_days(row["updated_at"])
            
            if debug:
                score, components = compute_rank_score(
                    fts5_score=row["fts5_score"],
                    material_type=row["material_type"],
                    confidence=row["confidence"],
                    age_days=age_days,
                    return_components=True,
                )
                rank_components = components.to_dict()
            else:
                score = compute_rank_score(
                    fts5_score=row["fts5_score"],
                    material_type=row["material_type"],
                    confidence=row["confidence"],
                    age_days=age_days,
                )
                rank_components = None
            
            # Extract snippet from attachment text
            content = row["extracted_text"] or ""
            snippet = extract_snippet(content, query_terms)
            
            result = SearchResult(
                research_id=row["research_id"],
                title=row["title"],
                content=row["content"],
                summary=row["summary"],
                project_id=row["project_id"],
                material_type=row["material_type"],
                confidence=row["confidence"],
                catalog=row["catalog"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                fts5_score=row["fts5_score"],
                rank_score=score,
                source_type="attachment",
                attachment_id=row["attachment_id"],
                attachment_filename=row["filename"],
                snippet=snippet,
                rank_components=rank_components,
            )
            results.append(result)
        
        return results
    
    def search_project(
        self,
        project_id: str,
        query: str,
        material_type: Optional[str] = None,
        confidence_min: float = 0.0,
        limit: int = 50,
        offset: int = 0,
        debug: bool = False,
    ) -> List[SearchResult]:
        """
        Search within a specific project.
        
        Convenience method equivalent to search(..., project_id=project_id).
        Fast due to project_id index.
        
        Args:
            project_id: Project to search within
            query: Search query
            material_type: Filter to 'reference' or 'research'
            confidence_min: Minimum confidence threshold
            limit: Maximum results
            offset: Pagination offset
            debug: Include rank breakdown
            
        Returns:
            List of SearchResult for the specified project
            
        Examples:
            >>> searcher.search_project("rc-quadcopter", "motor")
            [SearchResult(id=5, title='Motor Specs', REF, score=0.75), ...]
        """
        return self.search(
            query=query,
            project_id=project_id,
            material_type=material_type,
            confidence_min=confidence_min,
            limit=limit,
            offset=offset,
            debug=debug,
        )
    
    def search_all_projects(
        self,
        query: str,
        material_type: Optional[str] = None,
        confidence_min: float = 0.0,
        limit: int = 50,
        offset: int = 0,
        debug: bool = False,
    ) -> List[SearchResult]:
        """
        Search across all projects.
        
        Same as search() without project_id filter, but explicitly named
        for clarity. Results include project_id in each result for grouping.
        
        Args:
            query: Search query
            material_type: Filter to 'reference' or 'research'
            confidence_min: Minimum confidence threshold
            limit: Maximum results
            offset: Pagination offset
            debug: Include rank breakdown
            
        Returns:
            List of SearchResult from all projects, sorted by rank
            
        Examples:
            >>> results = searcher.search_all_projects("servo")
            >>> for r in results:
            ...     print(f"{r.project_id}: {r.title}")
            rc-quadcopter: Servo Motor Datasheet
            robotic-arm: Servo Tuning Guide
        """
        return self.search(
            query=query,
            project_id=None,  # All projects
            material_type=material_type,
            confidence_min=confidence_min,
            limit=limit,
            offset=offset,
            debug=debug,
        )
    
    # ==========================================================================
    # LINKED RESEARCH METHODS
    # ==========================================================================
    
    def get_linked_research(
        self,
        research_id: int,
        link_types: Optional[List[str]] = None,
        relevance_min: float = 0.0,
        include_both_directions: bool = True,
        limit: int = 50,
    ) -> List[LinkedResult]:
        """
        Get research entries linked to the specified research.
        
        Follows relationships in research_links table:
        - applies_to: This code/spec applies to that component
        - contradicts: This info contradicts that info
        - supersedes: This newer version supersedes older
        - related: Generally related (weaker bond)
        - references: Explicitly cited
        
        Args:
            research_id: ID of the source research entry
            link_types: Filter to specific link types (None = all)
            relevance_min: Minimum relevance_score threshold
            include_both_directions: If True, also find entries that link TO this one
            limit: Maximum results
            
        Returns:
            List of LinkedResult sorted by relevance_score
            
        Examples:
            >>> links = searcher.get_linked_research(42)
            >>> for link in links:
            ...     print(f"{link.link_type}: {link.research_title}")
            applies_to: RC Quadcopter Motor Assembly
            related: Servo Tuning Best Practices
            
            >>> links = searcher.get_linked_research(42, link_types=['supersedes'])
            [LinkedResult(link_type='supersedes', ...)]
        """
        conn = self._get_connection()
        results: List[LinkedResult] = []
        
        # Outgoing links (source -> target)
        outgoing_sql = """
            SELECT 
                rl.id as link_id,
                rl.source_research_id,
                rl.target_research_id,
                rl.link_type,
                rl.relevance_score,
                rl.reason,
                rl.agent_role,
                rl.created_at,
                r.title as research_title,
                r.project_id as research_project_id,
                r.material_type as research_material_type,
                r.confidence as research_confidence
            FROM research_links rl
            JOIN research r ON rl.target_research_id = r.id
            WHERE rl.source_research_id = ?
              AND rl.relevance_score >= ?
              AND r.archived = 0
        """
        params: List[Any] = [research_id, relevance_min]
        
        if link_types:
            placeholders = ",".join("?" * len(link_types))
            outgoing_sql += f" AND rl.link_type IN ({placeholders})"
            params.extend(link_types)
        
        outgoing_sql += " ORDER BY rl.relevance_score DESC"
        
        cursor = conn.cursor()
        cursor.execute(outgoing_sql, params)
        
        for row in cursor.fetchall():
            results.append(LinkedResult(
                link_id=row["link_id"],
                source_research_id=row["source_research_id"],
                target_research_id=row["target_research_id"],
                link_type=row["link_type"],
                relevance_score=row["relevance_score"],
                reason=row["reason"],
                research_title=row["research_title"],
                research_project_id=row["research_project_id"],
                research_material_type=row["research_material_type"],
                research_confidence=row["research_confidence"],
                created_at=row["created_at"],
                agent_role=row["agent_role"],
            ))
        
        # Incoming links (others -> this)
        if include_both_directions:
            incoming_sql = """
                SELECT 
                    rl.id as link_id,
                    rl.source_research_id,
                    rl.target_research_id,
                    rl.link_type,
                    rl.relevance_score,
                    rl.reason,
                    rl.agent_role,
                    rl.created_at,
                    r.title as research_title,
                    r.project_id as research_project_id,
                    r.material_type as research_material_type,
                    r.confidence as research_confidence
                FROM research_links rl
                JOIN research r ON rl.source_research_id = r.id
                WHERE rl.target_research_id = ?
                  AND rl.relevance_score >= ?
                  AND r.archived = 0
            """
            params = [research_id, relevance_min]
            
            if link_types:
                placeholders = ",".join("?" * len(link_types))
                incoming_sql += f" AND rl.link_type IN ({placeholders})"
                params.extend(link_types)
            
            incoming_sql += " ORDER BY rl.relevance_score DESC"
            
            cursor.execute(incoming_sql, params)
            
            for row in cursor.fetchall():
                results.append(LinkedResult(
                    link_id=row["link_id"],
                    source_research_id=row["source_research_id"],
                    target_research_id=row["target_research_id"],
                    link_type=row["link_type"],
                    relevance_score=row["relevance_score"],
                    reason=row["reason"],
                    research_title=row["research_title"],
                    research_project_id=row["research_project_id"],
                    research_material_type=row["research_material_type"],
                    research_confidence=row["research_confidence"],
                    created_at=row["created_at"],
                    agent_role=row["agent_role"],
                ))
        
        # Sort by relevance and limit
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def get_superseding_research(
        self,
        research_id: int,
    ) -> Optional[LinkedResult]:
        """
        Find research that supersedes the specified entry.
        
        Useful for finding the "latest version" of a spec or document.
        
        Args:
            research_id: ID of the potentially outdated research
            
        Returns:
            LinkedResult if a superseding entry exists, None otherwise
            
        Examples:
            >>> newer = searcher.get_superseding_research(42)
            >>> if newer:
            ...     print(f"Superseded by: {newer.research_title}")
        """
        links = self.get_linked_research(
            research_id=research_id,
            link_types=["supersedes"],
            include_both_directions=False,
            limit=1,
        )
        
        if links:
            return links[0]
        return None
    
    def get_contradicting_research(
        self,
        research_id: int,
        relevance_min: float = 0.5,
    ) -> List[LinkedResult]:
        """
        Find research that contradicts the specified entry.
        
        Useful for identifying conflicting information.
        
        Args:
            research_id: ID of the research entry
            relevance_min: Minimum relevance threshold
            
        Returns:
            List of LinkedResult with contradicting research
        """
        return self.get_linked_research(
            research_id=research_id,
            link_types=["contradicts"],
            relevance_min=relevance_min,
            include_both_directions=True,
        )
    
    # ==========================================================================
    # FILE USAGE METHODS
    # ==========================================================================
    
    def get_file_usage(
        self,
        attachment_id: int,
    ) -> FileUsage:
        """
        Get information about which research entries reference an attachment.
        
        Args:
            attachment_id: ID of the attachment
            
        Returns:
            FileUsage object with research entry references
            
        Examples:
            >>> usage = searcher.get_file_usage(123)
            >>> print(f"{usage.filename} used by {usage.total_references} entries")
            motor-spec.pdf used by 3 entries
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get attachment info
        cursor.execute("""
            SELECT 
                a.id,
                a.filename,
                a.research_id,
                r.id as research_id,
                r.title,
                r.project_id,
                r.material_type,
                r.confidence
            FROM attachments a
            JOIN research r ON a.research_id = r.id
            WHERE a.id = ?
              AND a.archived = 0
              AND r.archived = 0
        """, (attachment_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return FileUsage(
                attachment_id=attachment_id,
                filename="",
                research_entries=[],
                total_references=0,
            )
        
        entries = [{
            "research_id": row["research_id"],
            "title": row["title"],
            "project_id": row["project_id"],
            "material_type": row["material_type"],
            "confidence": row["confidence"],
        }]
        
        # Check if this file (by checksum) is used elsewhere
        cursor.execute("""
            SELECT a.sha256_checksum 
            FROM attachments a 
            WHERE a.id = ?
        """, (attachment_id,))
        checksum_row = cursor.fetchone()
        
        if checksum_row:
            cursor.execute("""
                SELECT 
                    a.id as attachment_id,
                    r.id as research_id,
                    r.title,
                    r.project_id,
                    r.material_type,
                    r.confidence
                FROM attachments a
                JOIN research r ON a.research_id = r.id
                WHERE a.sha256_checksum = ?
                  AND a.id != ?
                  AND a.archived = 0
                  AND r.archived = 0
            """, (checksum_row["sha256_checksum"], attachment_id))
            
            for other_row in cursor.fetchall():
                entries.append({
                    "research_id": other_row["research_id"],
                    "title": other_row["title"],
                    "project_id": other_row["project_id"],
                    "material_type": other_row["material_type"],
                    "confidence": other_row["confidence"],
                })
        
        return FileUsage(
            attachment_id=attachment_id,
            filename=row["filename"],
            research_entries=entries,
            total_references=len(entries),
        )
    
    # ==========================================================================
    # CONFIDENCE VALIDATION
    # ==========================================================================
    
    def validate_material_type(
        self,
        material_type: str,
        confidence: float,
    ) -> bool:
        """
        Validate that material type and confidence are compatible.
        
        Reference material requires confidence >= 0.8.
        
        Args:
            material_type: 'reference' or 'research'
            confidence: Confidence score (0.0-1.0)
            
        Returns:
            True if valid, False if reference with low confidence
            
        Examples:
            >>> searcher.validate_material_type('reference', 0.9)
            True
            >>> searcher.validate_material_type('reference', 0.5)
            False
            >>> searcher.validate_material_type('research', 0.1)
            True
        """
        return validate_material_type(material_type, confidence)
    
    def score_confidence(
        self,
        source_type: str,
        recency_days: int,
    ) -> float:
        """
        Calculate confidence score based on source type and recency.
        
        Args:
            source_type: 'reference' or 'research'
            recency_days: Age of document in days
            
        Returns:
            Confidence score between 0.0 and 1.0
            
        Examples:
            >>> searcher.score_confidence('reference', 30)
            0.92
            >>> searcher.score_confidence('research', 365)
            0.55
        """
        return score_confidence(source_type, recency_days)
    
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================
    
    def get_project_ids(self) -> List[str]:
        """
        Get list of all project IDs in the database.
        
        Returns:
            List of project ID strings
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT project_id 
            FROM research 
            WHERE archived = 0
            ORDER BY project_id
        """)
        
        return [row["project_id"] for row in cursor.fetchall()]
    
    def get_project_stats(
        self,
        project_id: str,
    ) -> Dict[str, Any]:
        """
        Get statistics for a project.
        
        Args:
            project_id: Project to analyze
            
        Returns:
            Dict with counts and averages
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_entries,
                SUM(CASE WHEN material_type = 'reference' THEN 1 ELSE 0 END) as reference_count,
                SUM(CASE WHEN material_type = 'research' THEN 1 ELSE 0 END) as research_count,
                AVG(confidence) as avg_confidence,
                MIN(created_at) as oldest_entry,
                MAX(updated_at) as newest_entry
            FROM research
            WHERE project_id = ?
              AND archived = 0
        """, (project_id,))
        
        row = cursor.fetchone()
        
        return {
            "project_id": project_id,
            "total_entries": row["total_entries"] or 0,
            "reference_count": row["reference_count"] or 0,
            "research_count": row["research_count"] or 0,
            "avg_confidence": round(row["avg_confidence"] or 0.0, 2),
            "oldest_entry": row["oldest_entry"],
            "newest_entry": row["newest_entry"],
        }
    
    def count_results(
        self,
        query: str,
        project_id: Optional[str] = None,
    ) -> int:
        """
        Count search results without fetching full data.
        
        Useful for pagination UI.
        
        Args:
            query: Search query
            project_id: Optional project filter
            
        Returns:
            Total count of matching results
        """
        if not query:
            return 0
        
        fts5_query = sanitize_fts5_query(query)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Count research matches
        sql = """
            SELECT COUNT(*) as cnt
            FROM research r
            JOIN research_fts ON r.id = research_fts.rowid
            WHERE research_fts MATCH ?
              AND r.archived = 0
        """
        params: List[Any] = [fts5_query]
        
        if project_id:
            sql += " AND r.project_id = ?"
            params.append(project_id)
        
        try:
            cursor.execute(sql, params)
            research_count = cursor.fetchone()["cnt"]
        except sqlite3.OperationalError:
            research_count = 0
        
        # Count attachment matches
        sql = """
            SELECT COUNT(*) as cnt
            FROM attachments a
            JOIN attachments_fts ON a.id = attachments_fts.rowid
            JOIN research r ON a.research_id = r.id
            WHERE attachments_fts MATCH ?
              AND a.archived = 0
              AND r.archived = 0
        """
        params = [fts5_query]
        
        if project_id:
            sql += " AND r.project_id = ?"
            params.append(project_id)
        
        try:
            cursor.execute(sql, params)
            attachment_count = cursor.fetchone()["cnt"]
        except sqlite3.OperationalError:
            attachment_count = 0
        
        return research_count + attachment_count
    
    def explain_search(
        self,
        query: str,
        limit: int = 5,
    ) -> str:
        """
        Generate a human-readable explanation of search results.
        
        Useful for debugging and understanding ranking.
        
        Args:
            query: Search query
            limit: Number of results to explain
            
        Returns:
            Multi-line string with search explanation
        """
        results = self.search(query, limit=limit, debug=True)
        
        lines = [
            f"Search Explanation for: \"{query}\"",
            "=" * 60,
            f"Total results: {len(results)}",
            "",
        ]
        
        for i, r in enumerate(results, 1):
            lines.append(f"#{i}: {r.title}")
            lines.append(f"    Project: {r.project_id}")
            lines.append(f"    Type: {r.material_type.upper()} (weight: {get_material_weight(r.material_type)})")
            lines.append(f"    Confidence: {r.confidence}")
            lines.append(f"    Source: {r.source_type}")
            lines.append(f"    FTS5 Score: {r.fts5_score:.2f}")
            lines.append(f"    Rank Score: {r.rank_score:.4f}")
            if r.rank_components:
                lines.append(f"    Components:")
                lines.append(f"      - Relevance: {r.rank_components.get('relevance_component', 0):.4f}")
                lines.append(f"      - Confidence: {r.rank_components.get('confidence_component', 0):.4f}")
                lines.append(f"      - Recency: {r.rank_components.get('recency_component', 0):.4f}")
            if r.snippet:
                lines.append(f"    Snippet: {r.snippet[:80]}...")
            lines.append("")
        
        return "\n".join(lines)
