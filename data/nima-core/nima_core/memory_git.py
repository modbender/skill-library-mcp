#!/usr/bin/env python3
"""
Memory Git — Auto-commit memory changes with context-aware messages.

Generalized version for nima-core — all paths configurable via env vars:
- NIMA_WORKSPACE: Base workspace directory (default: ~/.openclaw/workspace)
- NIMA_MEMORY_DIR: Memory directory for git repo (default: {workspace}/memory)
- NIMA_TRACKED_FILES: Comma-separated top-level files to track (default: MEMORY.md,LILU_STATUS.md)

Inspired by Letta's Context Repositories: every memory change is tracked,
timestamped, and attributed so you can always see what changed and why.

Usage:
    from nima_core.memory_git import commit_memory, get_log, setup_memory_repo

    commit_memory("capture", "User mentioned they love woodworking")
    commit_memory("dream", "Consolidated 12 episodic turns → 3 semantic patterns")
    commit_memory("reflection", "Updated MEMORY.md with project context")

CLI:
    python3 -m nima_core.memory_git commit "source" "message"
    python3 -m nima_core.memory_git log
    python3 -m nima_core.memory_git diff
"""

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# --- Configuration via environment variables ---
NIMA_WORKSPACE = Path(os.environ.get(
    "NIMA_WORKSPACE",
    os.path.expanduser("~/.openclaw/workspace")
))

NIMA_MEMORY_DIR = Path(os.environ.get(
    "NIMA_MEMORY_DIR",
    str(NIMA_WORKSPACE / "memory")
))

# Comma-separated list of top-level files to track
_TRACKED_FILES_ENV = os.environ.get("NIMA_TRACKED_FILES", "MEMORY.md,LILU_STATUS.md")
TRACKED_TOP_LEVEL = [f.strip() for f in _TRACKED_FILES_ENV.split(",") if f.strip()]

# Source → emoji for commit messages (part of NIMA identity)
SOURCE_EMOJI = {
    "capture":      "🧬",  # new memory captured
    "dream":        "🌙",  # dream engine consolidation
    "reflection":   "🪞",  # reflection agent ran
    "consolidation":"♻️",  # consolidation pass
    "heartbeat":    "💓",  # heartbeat memory update
    "user":         "👤",  # user-triggered
    "defrag":       "🧹",  # memory defrag/cleanup
    "init":         "🌱",  # initialization
    "manual":       "✍️",  # manual edit
}


def _run(cmd: list, cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """Run a git command, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        cwd=str(cwd or NIMA_MEMORY_DIR),
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def _is_git_repo() -> bool:
    """Check if MEMORY_DIR is a git repository."""
    if not NIMA_MEMORY_DIR.exists():
        return False
    code, _, _ = _run(["git", "rev-parse", "--git-dir"])
    return code == 0


def _has_changes() -> bool:
    """Check if there are any staged or unstaged changes."""
    code, out, _ = _run(["git", "status", "--porcelain"])
    return bool(out.strip())


def setup_memory_repo() -> bool:
    """
    Initialize a git repo in MEMORY_DIR if one doesn't exist.
    
    Creates the directory if needed, runs `git init`, and makes an initial commit.
    Returns True if repo was created or already exists, False on error.
    """
    # Ensure directory exists
    NIMA_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if already a git repo
    if _is_git_repo():
        return True
    
    # Initialize git repo
    code, _, err = _run(["git", "init"])
    if code != 0:
        print(f"⚠️ Failed to initialize git repo: {err}")
        return False
    
    # Create a .gitkeep or initial README if directory is empty
    gitkeep = NIMA_MEMORY_DIR / ".gitkeep"
    if not any(NIMA_MEMORY_DIR.iterdir()):
        gitkeep.touch()
    
    # Stage all existing files
    _run(["git", "add", "--all"])
    
    # Initial commit
    commit_msg = "🌱 [init] Initialized NIMA memory repository"
    code, _, err = _run(["git", "commit", "-m", commit_msg, "--allow-empty"])
    
    if code == 0:
        print(f"✅ Initialized memory repo at {NIMA_MEMORY_DIR}")
        return True
    elif "nothing to commit" in err.lower():
        # Empty repo is fine
        print(f"✅ Initialized empty memory repo at {NIMA_MEMORY_DIR}")
        return True
    else:
        print(f"⚠️ Initial commit failed: {err}")
        return False


def commit_memory(source: str, message: str, files: Optional[List[str]] = None) -> bool:
    """
    Stage and commit memory changes.

    Args:
        source: Who/what triggered the change (capture/dream/reflection/etc.)
        message: Human-readable description of what changed
        files: Specific files to commit (None = auto-stage all tracked changes)

    Returns:
        True if a commit was made, False if nothing to commit
    """
    # Ensure repo exists
    if not _is_git_repo():
        if not setup_memory_repo():
            return False
    
    emoji = SOURCE_EMOJI.get(source.lower(), "📝")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Stage: all files in memory dir
    _run(["git", "add", "--all"], cwd=NIMA_MEMORY_DIR)

    # Stage: top-level tracked files (MEMORY.md, etc.)
    for fname in TRACKED_TOP_LEVEL:
        fpath = NIMA_WORKSPACE / fname
        if fpath.exists():
            # Stage relative to memory repo using absolute path
            _run(["git", "add", str(fpath)], cwd=NIMA_MEMORY_DIR)

    # Stage any explicitly provided files
    if files:
        for f in files:
            _run(["git", "add", str(f)], cwd=NIMA_MEMORY_DIR)

    if not _has_changes():
        return False

    commit_msg = f"{emoji} [{source}] {message}\n\nTimestamp: {timestamp}"
    code, out, err = _run(["git", "commit", "-m", commit_msg])

    if code == 0:
        # Extract short hash for confirmation
        _, short_hash, _ = _run(["git", "rev-parse", "--short", "HEAD"])
        print(f"  📌 memory commit {short_hash}: {emoji} {message[:60]}")
        return True
    elif "nothing to commit" in err or "nothing to commit" in out:
        return False
    else:
        print(f"  ⚠️  memory_git commit failed: {err}")
        return False


def get_log(n: int = 10) -> List[Dict]:
    """Get the last N memory commits as structured dicts."""
    if not _is_git_repo():
        return []
    
    code, out, _ = _run([
        "git", "log", f"-{n}",
        "--pretty=format:%h|%ai|%s",
        "--no-merges"
    ])
    if code != 0 or not out:
        return []

    entries = []
    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3:
            entries.append({
                "hash": parts[0],
                "timestamp": parts[1],
                "message": parts[2],
            })
    return entries


def get_diff(commit: str = "HEAD~1") -> str:
    """Get diff of the last commit (or since a specific commit)."""
    if not _is_git_repo():
        return "Not a git repository"
    _, out, _ = _run(["git", "diff", commit, "HEAD", "--stat"])
    return out


def show_commit(hash: str) -> str:
    """Show full details of a commit."""
    if not _is_git_repo():
        return "Not a git repository"
    _, out, _ = _run(["git", "show", hash, "--stat", "--format=fuller"])
    return out


# ── CLI ──────────────────────────────────────────────────────────────────────

def _cli():
    """Command-line interface for memory_git."""
    cmd = sys.argv[1] if len(sys.argv) > 1 else "log"

    if cmd == "commit":
        source = sys.argv[2] if len(sys.argv) > 2 else "manual"
        msg = sys.argv[3] if len(sys.argv) > 3 else "manual memory update"
        made = commit_memory(source, msg)
        print("committed" if made else "nothing to commit")

    elif cmd == "log":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 15
        entries = get_log(n)
        if not entries:
            print("No memory commits yet.")
        else:
            print(f"Last {len(entries)} memory commits:\n")
            for e in entries:
                ts = e["timestamp"][:16]
                print(f"  {e['hash']}  {ts}  {e['message']}")

    elif cmd == "diff":
        print(get_diff())

    elif cmd == "show":
        hash_ref = sys.argv[2] if len(sys.argv) > 2 else "HEAD"
        print(show_commit(hash_ref))

    elif cmd == "setup":
        ok = setup_memory_repo()
        print("setup complete" if ok else "setup failed")

    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 -m nima_core.memory_git [commit|log|diff|show|setup] [args...]")


if __name__ == "__main__":
    _cli()
