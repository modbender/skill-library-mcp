"""
Research Library Data Models

Dataclasses representing the core entities in the research library.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# =============================================================================
# Constants
# =============================================================================

MATERIAL_TYPES = [
    "note",           # Quick notes, observations
    "source",         # Primary source material
    "reference",      # Vetted reference material (requires confidence >= 0.8)
    "draft",          # Work in progress
    "archive",        # Archived/deprecated material
]

LINK_TYPES = [
    "related",        # General relationship
    "supports",       # Source supports target
    "contradicts",    # Source contradicts target
    "cites",          # Source cites target
    "derived_from",   # Source derived from target
    "supersedes",     # Source replaces target
]

JOB_STATUSES = [
    "pending",        # Waiting to be processed
    "processing",     # Currently being extracted
    "completed",      # Successfully extracted
    "failed",         # Extraction failed
    "skipped",        # Skipped (unsupported format, etc.)
]


# =============================================================================
# Dataclasses
# =============================================================================

@dataclass
class Research:
    """A research document/note in the library."""
    id: Optional[str] = None
    title: str = ""
    content: str = ""
    project_id: str = ""  # Required - groups research by project
    material_type: str = "note"
    confidence: float = 0.5  # 0.0-1.0 scale
    source_url: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.material_type not in MATERIAL_TYPES:
            raise ValueError(f"Invalid material_type: {self.material_type}. Must be one of {MATERIAL_TYPES}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
        if self.material_type == "reference" and self.confidence < 0.8:
            raise ValueError(f"Reference material requires confidence >= 0.8, got {self.confidence}")
        if not self.project_id:
            raise ValueError("project_id is required")


@dataclass
class Attachment:
    """A file attached to a research document."""
    id: Optional[str] = None
    research_id: str = ""
    filename: str = ""
    path: str = ""  # Relative path in storage
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    extracted_text: Optional[str] = None
    extraction_confidence: float = 0.0  # Confidence in text extraction
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not 0.0 <= self.extraction_confidence <= 1.0:
            raise ValueError(f"extraction_confidence must be between 0.0 and 1.0")


@dataclass
class AttachmentVersion:
    """Version history for attachments."""
    id: Optional[str] = None
    attachment_id: str = ""
    version_number: int = 1
    path: str = ""
    file_hash: str = ""
    created_at: Optional[datetime] = None


@dataclass
class Tag:
    """A tag/category for organizing research."""
    id: Optional[str] = None
    name: str = ""
    color: Optional[str] = None  # Hex color for UI
    created_at: Optional[datetime] = None


@dataclass
class ResearchLink:
    """A relationship between two research documents."""
    source_id: str = ""
    target_id: str = ""
    link_type: str = "related"
    relevance_score: float = 0.5  # 0.0-1.0 scale
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.link_type not in LINK_TYPES:
            raise ValueError(f"Invalid link_type: {self.link_type}. Must be one of {LINK_TYPES}")
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError(f"relevance_score must be between 0.0 and 1.0")


@dataclass
class Embedding:
    """Vector embedding for semantic search."""
    id: Optional[str] = None
    research_id: str = ""
    chunk_index: int = 0  # For chunked documents
    embedding_model: str = ""
    embedding: bytes = b""  # Serialized vector
    created_at: Optional[datetime] = None


@dataclass
class ExtractionJob:
    """Queue entry for text extraction from attachments."""
    id: Optional[str] = None
    attachment_id: str = ""
    status: str = "pending"
    attempts: int = 0
    max_attempts: int = 3
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.status not in JOB_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {JOB_STATUSES}")
