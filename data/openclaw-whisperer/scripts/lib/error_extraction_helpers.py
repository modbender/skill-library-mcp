"""Helper functions for extracting error metadata from text."""
from __future__ import annotations

import re

TIMESTAMP_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}',
    r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]',
]


def extract_timestamp(line: str) -> str | None:
    """Extract timestamp from line.

    Args:
        line: Line text

    Returns:
        Timestamp string or None
    """
    for pattern in TIMESTAMP_PATTERNS:
        match = re.search(pattern, line)
        if match:
            return match.group(0)
    return None


def extract_error_code(text: str) -> str | None:
    """Extract error code from text.

    Common patterns:
    - NOT_LINKED, AGENT_TIMEOUT, CONFIG_INVALID
    - HTTP 404, HTTP 500

    Args:
        text: Text to search

    Returns:
        Error code or None
    """
    # OpenClaw style codes (CAPS_WITH_UNDERSCORES)
    code_match = re.search(r'\b([A-Z][A-Z_]{3,})\b', text)
    if code_match:
        return code_match.group(1)

    # HTTP status codes
    http_match = re.search(r'HTTP\s+([4-5]\d{2})', text, re.IGNORECASE)
    if http_match:
        return f"HTTP_{http_match.group(1)}"

    return None
