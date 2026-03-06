"""
Shared utilities for the Natural Language Planner.

Provides common functions used across all modules: slug generation,
YAML frontmatter parsing/serializing, date handling, and ID generation.
"""

import re
import uuid
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Any, Optional

logger = logging.getLogger("nlplanner")


def generate_slug(text: str, max_length: int = 50) -> str:
    """
    Generate a URL/filesystem-safe slug from text.

    Args:
        text: The text to slugify.
        max_length: Maximum length of the slug.

    Returns:
        A lowercase, hyphen-separated slug string.

    Example:
        >>> generate_slug("My Cool Project!")
        'my-cool-project'
    """
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    return slug[:max_length]


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with an optional prefix.

    Args:
        prefix: Optional prefix for the ID (e.g., 'task', 'proj').

    Returns:
        A unique identifier string.

    Example:
        >>> generate_id("task")
        'task-a1b2c3d4'
    """
    short_uuid = uuid.uuid4().hex[:8]
    if prefix:
        return f"{prefix}-{short_uuid}"
    return short_uuid


def generate_task_id(counter: int) -> str:
    """
    Generate a sequential task ID.

    Args:
        counter: The task number.

    Returns:
        Formatted task ID like 'task-001'.

    Example:
        >>> generate_task_id(42)
        'task-042'
    """
    return f"task-{counter:03d}"


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Parse YAML frontmatter from a markdown file's content.

    Expects content in the form:
        ---
        key: value
        ---
        Body text here.

    Args:
        content: The full markdown file content.

    Returns:
        A tuple of (frontmatter_dict, body_text).
        If no frontmatter is found, returns ({}, full_content).

    Example:
        >>> meta, body = parse_frontmatter("---\\ntitle: Hello\\n---\\nWorld")
        >>> meta
        {'title': 'Hello'}
        >>> body
        'World'
    """
    # Lazy import to avoid import-time dependency issues
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML is required. Install with: pip install pyyaml")
        return {}, content

    pattern = r"^---\s*\n(.*?)\n---\s*\n?(.*)"
    match = re.match(pattern, content, re.DOTALL)
    if not match:
        return {}, content

    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        logger.warning("Failed to parse YAML frontmatter: %s", e)
        frontmatter = {}

    body = match.group(2).strip()
    return frontmatter, body


def serialize_frontmatter(metadata: dict[str, Any], body: str) -> str:
    """
    Serialize metadata and body into a markdown string with YAML frontmatter.

    Args:
        metadata: Dictionary of metadata fields.
        body: The markdown body content.

    Returns:
        Complete markdown string with YAML frontmatter block.

    Example:
        >>> content = serialize_frontmatter({"title": "Hello"}, "World")
        >>> print(content)
        ---
        title: Hello
        ---
        <BLANKLINE>
        World
    """
    try:
        import yaml
    except ImportError:
        logger.error("PyYAML is required. Install with: pip install pyyaml")
        return body

    # Custom representer for dates — keep them as plain strings
    def date_representer(dumper: yaml.Dumper, data: date) -> yaml.ScalarNode:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())

    dumper = yaml.Dumper
    dumper.add_representer(date, date_representer)
    dumper.add_representer(datetime, date_representer)

    yaml_str = yaml.dump(
        metadata,
        Dumper=dumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    return f"---\n{yaml_str.strip()}\n---\n\n{body}"


def today_str() -> str:
    """Return today's date as an ISO-formatted string (YYYY-MM-DD)."""
    return date.today().isoformat()


def now_str() -> str:
    """Return current datetime as an ISO-formatted string."""
    return datetime.now().isoformat(timespec="seconds")


def ensure_directory(path: Path) -> bool:
    """
    Ensure a directory exists, creating it and any parents if needed.

    Args:
        path: The directory path to ensure exists.

    Returns:
        True if the directory exists (or was created), False on error.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.error("Failed to create directory %s: %s", path, e)
        return False


def safe_read_file(path: Path) -> Optional[str]:
    """
    Safely read a text file, returning None on error.

    Args:
        path: Path to the file.

    Returns:
        File contents as a string, or None if the file can't be read.
    """
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.error("Failed to read file %s: %s", path, e)
        return None


def safe_write_file(path: Path, content: str) -> bool:
    """
    Safely write content to a text file, creating parent directories as needed.

    Args:
        path: Path to the file.
        content: String content to write.

    Returns:
        True if the file was written successfully, False on error.
    """
    try:
        ensure_directory(path.parent)
        path.write_text(content, encoding="utf-8")
        return True
    except OSError as e:
        logger.error("Failed to write file %s: %s", path, e)
        return False


def safe_child_path(root: Path, *segments: str) -> Optional[Path]:
    """Construct a path from *root* + *segments* and verify it stays inside *root*.

    Returns the resolved ``Path`` if the result is inside *root*, or
    ``None`` if any segment (e.g. containing ``..``) would escape it.
    This prevents path-traversal attacks when IDs come from untrusted
    input such as URL parameters or user-supplied project/task names.

    Args:
        root: The trusted base directory (must already be resolved).
        *segments: One or more path components to join.

    Returns:
        Resolved ``Path`` inside *root*, or ``None`` on traversal.
    """
    try:
        target = root.joinpath(*segments).resolve()
        # is_relative_to is available in Python 3.9+
        if target.is_relative_to(root):
            return target
    except (ValueError, OSError):
        pass
    logger.warning("Path traversal blocked: %s / %s", root, segments)
    return None


def validate_status(status: str) -> bool:
    """Check if a status value is valid for tasks."""
    return status in ("todo", "in-progress", "done", "archived")


def validate_priority(priority: str) -> bool:
    """Check if a priority value is valid."""
    return priority in ("low", "medium", "high")


# Configure default logging
def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging for the Natural Language Planner.

    Args:
        level: Logging level (default: INFO).
    """
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(name)s %(levelname)s] %(message)s")
    )
    root = logging.getLogger("nlplanner")
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
