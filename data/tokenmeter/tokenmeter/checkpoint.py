"""Checkpoint management for incremental imports.

Tracks file state (mtime, size, byte offset, header hash) so subsequent
imports only read new data appended since the last run.

JSONL files are append-only in normal operation. If a file gets compacted
(rewritten), the header hash won't match and we fall back to a full re-scan
for that file only.
"""

import json
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Optional

CHECKPOINT_PATH = Path.home() / ".tokenmeter" / "import-state.json"
HEADER_BYTES = 1024  # bytes to hash for compaction detection


def _file_header_hash(filepath: Path) -> str:
    """Hash the first HEADER_BYTES of a file for compaction detection."""
    try:
        with open(filepath, "rb") as f:
            header = f.read(HEADER_BYTES)
        return hashlib.sha256(header).hexdigest()[:16]
    except (OSError, IOError):
        return ""


def load_checkpoint() -> dict:
    """Load the checkpoint state from disk.
    
    Returns:
        {
            "version": 1,
            "files": {
                "/path/to/file.jsonl": {
                    "mtime": 1234567890.0,
                    "size": 12345,
                    "byte_offset": 12345,
                    "header_hash": "abc123...",
                    "last_imported": "2026-02-09T..."
                },
                ...
            }
        }
    """
    if not CHECKPOINT_PATH.exists():
        return {"version": 1, "files": {}}
    
    try:
        with open(CHECKPOINT_PATH, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "files" not in data:
            return {"version": 1, "files": {}}
        return data
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "files": {}}


def save_checkpoint(state: dict) -> None:
    """Atomically write checkpoint to disk (write to tmp, then rename)."""
    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file first, then atomic rename
    fd, tmp_path = tempfile.mkstemp(
        dir=CHECKPOINT_PATH.parent,
        prefix=".import-state-",
        suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp_path, str(CHECKPOINT_PATH))
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def get_file_state(filepath: Path) -> dict:
    """Get current filesystem state of a file."""
    try:
        stat = filepath.stat()
        return {
            "mtime": stat.st_mtime,
            "size": stat.st_size,
            "header_hash": _file_header_hash(filepath),
        }
    except (OSError, IOError):
        return {"mtime": 0, "size": 0, "header_hash": ""}


def classify_file(filepath: Path, checkpoint: dict) -> tuple[str, int]:
    """Classify a file for import and return (action, byte_offset).
    
    Returns:
        ("skip", 0)       — file unchanged since last import
        ("incremental", N) — file grew; seek to byte N and read new lines
        ("full", 0)        — file is new, compacted, or shrunk; full scan
    """
    key = str(filepath)
    current = get_file_state(filepath)
    
    if key not in checkpoint.get("files", {}):
        return ("full", 0)
    
    saved = checkpoint["files"][key]
    
    # Check if file was compacted/rewritten (header hash mismatch)
    if current["header_hash"] != saved.get("header_hash", ""):
        return ("full", 0)
    
    # Check if file shrunk (truncated or rewritten)
    if current["size"] < saved.get("size", 0):
        return ("full", 0)
    
    # Check if file is unchanged
    if (current["mtime"] == saved.get("mtime", 0) and
            current["size"] == saved.get("size", 0)):
        return ("skip", 0)
    
    # File grew — read from last byte offset
    byte_offset = saved.get("byte_offset", 0)
    return ("incremental", byte_offset)


def update_file_checkpoint(checkpoint: dict, filepath: Path, byte_offset: int) -> None:
    """Update checkpoint for a single file after import."""
    current = get_file_state(filepath)
    checkpoint.setdefault("files", {})[str(filepath)] = {
        "mtime": current["mtime"],
        "size": current["size"],
        "byte_offset": byte_offset,
        "header_hash": current["header_hash"],
        "last_imported": __import__("datetime").datetime.now().isoformat(),
    }


def prune_deleted_files(checkpoint: dict, existing_files: set[str]) -> list[str]:
    """Remove checkpoint entries for files that no longer exist.
    
    Returns list of pruned file paths.
    """
    pruned = []
    for key in list(checkpoint.get("files", {}).keys()):
        if key not in existing_files:
            del checkpoint["files"][key]
            pruned.append(key)
    return pruned
