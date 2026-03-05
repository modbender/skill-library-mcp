"""
Create a timestamped backup of source bot (moltbot/clawdbot) config, memory, and clawdbook data.
Never overwrite; always safe. Works for any user's system.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config import DEFAULT_BACKUP_DIR, BACKUP_PREFIX
from .discover import discover_source_assets


def create_backup(
    root: Optional[Path] = None,
    backup_dir: Optional[Path] = None,
    asset_paths: Optional[dict] = None,
) -> Path:
    """
    Copy all discovered (or provided) assets into a timestamped backup directory.
    Returns the path to the backup directory.
    """
    root = Path(root or os.getcwd()).resolve()
    backup_base = Path(backup_dir or root / DEFAULT_BACKUP_DIR)
    backup_base.mkdir(parents=True, exist_ok=True)

    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_base / f"{BACKUP_PREFIX}{stamp}"
    backup_path.mkdir(parents=True, exist_ok=True)

    assets = asset_paths or discover_source_assets(root)
    all_paths: List[str] = (
        assets.get("memory", [])
        + assets.get("config", [])
        + assets.get("clawdbook", [])
        + assets.get("extra", [])
    )
    all_paths = list(dict.fromkeys(all_paths))

    for src in all_paths:
        src_path = Path(src)
        if not src_path.is_file():
            continue
        try:
            rel = src_path.relative_to(root)
        except ValueError:
            rel = src_path.name
        dest = backup_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_path, dest)

    # Also write a manifest so we know what was backed up
    manifest = backup_path / "_manifest.txt"
    with open(manifest, "w", encoding="utf-8") as f:
        f.write(f"Backup at {stamp}\nRoot: {root}\n\n")
        for k, v in assets.items():
            if isinstance(v, list):
                f.write(f"{k}:\n")
                for p in v:
                    f.write(f"  {p}\n")
            else:
                f.write(f"{k}: {v}\n")

    return backup_path
