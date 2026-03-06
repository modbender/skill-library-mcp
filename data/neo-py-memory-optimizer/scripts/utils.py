#!/usr/bin/env python3
"""
Utility functions for Python static analysis.

Provides helpers for extracting source segments from AST nodes
and other common operations.
"""

import ast
from typing import Optional


def get_source_segment(source: str, node: ast.AST) -> str:
    """
    Return the source code segment corresponding to the given AST node.
    Uses node.lineno and node.end_lineno (Python 3.8+) to extract lines.
    Falls back to a single line if end_lineno is not available.
    """
    lines = source.splitlines()
    start_line = node.lineno - 1
    end_line = getattr(node, "end_lineno", node.lineno) - 1

    start_line = max(0, start_line)
    end_line = min(end_line, len(lines) - 1)

    segment_lines = lines[start_line : end_line + 1]
    return "\n".join(segment_lines)


def severity_rank(severity: str) -> int:
    """Return a numeric rank for sorting by severity (higher = more severe)."""
    ranks = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return ranks.get(severity.lower(), 0)


def format_line_ref(filename: str, line: int) -> str:
    """Format a file:line reference string."""
    return f"{filename}:{line}"


def count_by_severity(issues: list) -> dict:
    """Count issues grouped by severity level."""
    counts: dict = {}
    for issue in issues:
        sev = issue.get("severity", "unknown")
        counts[sev] = counts.get(sev, 0) + 1
    return counts
