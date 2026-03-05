from __future__ import annotations

from pathlib import Path
from typing import Optional


def find_workspace_root(start_file: str | Path) -> Path:
    """Find OpenClaw workspace root by walking upward until we find AGENTS.md.

    This avoids common bugs where scripts accidentally compute WS relative to skill folders
    (writing to skills/state instead of state).
    """

    p = Path(start_file).resolve()
    cur = p if p.is_dir() else p.parent
    for _ in range(15):
        if (cur / "AGENTS.md").exists() and (cur / "SOUL.md").exists():
            return cur
        cur = cur.parent
    raise RuntimeError(f"Workspace root not found walking up from {p}")


def ws_path(start_file: str | Path, *parts: str) -> Path:
    return find_workspace_root(start_file).joinpath(*parts)
