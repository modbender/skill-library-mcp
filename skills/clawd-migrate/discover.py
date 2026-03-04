"""
Discover source bot assets (moltbot or clawdbot): config, memory, and clawdbook data.
Works on any user's system; no machine-specific paths.
"""

import os
from pathlib import Path
from typing import Optional

from .config import (
    SOURCE_CONFIG_PATHS,
    SOURCE_MEMORY_FILES,
    SOURCE_EXTRA_DIRS,
)


def discover_source_assets(root: Optional[Path] = None) -> dict:
    """
    Scan root (or cwd) for moltbot/clawdbot config, memory, and clawdbook data.
    Returns paths that exist, grouped by type. Safe for any user's system.
    """
    root = Path(root or os.getcwd()).resolve()
    out = {
        "root": str(root),
        "memory": [],
        "config": [],
        "clawdbook": [],
        "extra": [],
    }

    # Memory files
    for name in SOURCE_MEMORY_FILES:
        p = root / name
        if p.is_file():
            out["memory"].append(str(p))

    # Config paths (moltbook/clawdbook = credentials, API keys)
    for rel in SOURCE_CONFIG_PATHS:
        p = root / rel
        if p.exists():
            if p.is_dir():
                for f in p.rglob("*"):
                    if f.is_file():
                        out["config"].append(str(f))
                if str(p) not in [os.path.dirname(c) for c in out["config"]]:
                    out["clawdbook"].append(str(p))
            else:
                out["config"].append(str(p))
                if "moltbook" in rel.lower() or "moltbot" in rel.lower() or "credentials" in rel.lower():
                    out["clawdbook"].append(str(p))

    out["config"] = list(dict.fromkeys(out["config"]))

    # Extra dirs (e.g. projects/)
    for rel in SOURCE_EXTRA_DIRS:
        rel_clean = rel.rstrip("/")
        extra_path = root / rel_clean
        if extra_path.is_dir():
            for f in extra_path.rglob("*"):
                if f.is_file():
                    out["extra"].append(str(f))

    out["clawdbook"] = list(dict.fromkeys(out["clawdbook"]))
    return out


def discover_clawdbot_assets(root: Optional[Path] = None) -> dict:
    """Alias for discover_source_assets (backward compatibility)."""
    return discover_source_assets(root)
