#!/usr/bin/env python3
"""Shared path-validation helpers for RLM scripts.

All file I/O in RLM helper scripts should route through validate_path()
to enforce directory-traversal and containment checks consistently.
"""
import os
import sys


def validate_path(path):
    """Reject directory traversal and paths that resolve outside the working directory.

    Checks:
    1. Reject explicit '..' path segments (directory traversal).
    2. Resolve the real path (following symlinks) and verify it stays
       within the real working directory (base-dir containment).

    Returns the resolved real path on success, exits on violation.
    """
    if '..' in path.split(os.sep):
        print(f"ERROR: path traversal detected: {path}", file=sys.stderr)
        sys.exit(1)
    rp = os.path.realpath(path)
    base_dir = os.path.realpath(os.getcwd())
    try:
        common = os.path.commonpath([base_dir, rp])
    except ValueError:
        # Different drives on Windows; treat as escape.
        print(f"ERROR: resolved path is outside the working directory: {path}", file=sys.stderr)
        sys.exit(1)
    if common != base_dir:
        print(f"ERROR: resolved path is outside the working directory: {path}", file=sys.stderr)
        sys.exit(1)
    return rp
