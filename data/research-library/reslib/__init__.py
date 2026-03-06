"""
Research Library - Document Extraction and Search

This package provides document extraction, indexing, and search
capabilities for a personal research library.
"""

from pathlib import Path

from .extractor import (
    DocumentExtractor,
    ExtractionResult,
    FileType,
    ConfidenceScores,
    BatchExtractor,
    extract_file,
    extract_text,
    get_supported_extensions,
    PDFExtractor,
    ImageExtractor,
    CodeExtractor,
)

__version__ = "1.0.0"

# Default paths for CLI
DEFAULT_DATA_DIR = Path.home() / ".reslib"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "research.db"
DEFAULT_ATTACHMENTS_DIR = DEFAULT_DATA_DIR / "attachments"
DEFAULT_BACKUPS_DIR = DEFAULT_DATA_DIR / "backups"

# Material types
MATERIAL_TYPES = ("reference", "research")

# Link types for document relationships
LINK_TYPES = ("applies_to", "contradicts", "supersedes", "related")

# Supported file types for auto-detection
SUPPORTED_EXTENSIONS = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "py": "text/x-python",
    "js": "text/javascript",
    "ts": "text/typescript",
    "rs": "text/x-rust",
    "go": "text/x-go",
    "c": "text/x-c",
    "cpp": "text/x-c++",
    "h": "text/x-c",
    "java": "text/x-java",
    "rb": "text/x-ruby",
    "md": "text/markdown",
    "txt": "text/plain",
    "json": "application/json",
    "yaml": "application/yaml",
    "yml": "application/yaml",
    "xml": "application/xml",
    "html": "text/html",
    "css": "text/css",
    "sql": "text/x-sql",
    "sh": "text/x-shellscript",
    "bash": "text/x-shellscript",
}

__all__ = [
    'DocumentExtractor',
    'ExtractionResult',
    'FileType',
    'ConfidenceScores',
    'BatchExtractor',
    'extract_file',
    'extract_text',
    'get_supported_extensions',
    'PDFExtractor',
    'ImageExtractor',
    'CodeExtractor',
    # CLI constants
    'DEFAULT_DATA_DIR',
    'DEFAULT_DB_PATH',
    'DEFAULT_ATTACHMENTS_DIR',
    'DEFAULT_BACKUPS_DIR',
    'MATERIAL_TYPES',
    'LINK_TYPES',
    'SUPPORTED_EXTENSIONS',
]
