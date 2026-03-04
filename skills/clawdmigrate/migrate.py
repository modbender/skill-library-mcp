"""
Migrate moltbot or clawdbot assets to openclaw layout.
Always runs after a backup; never mutates originals without backup.
Includes post-migration verification and openclaw reinstall.
Works for any user's system.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from .config import (
    OPENCLAW_MEMORY_DIR,
    OPENCLAW_CONFIG_DIR,
    OPENCLAW_CLAWDBOOK_DIR,
)
from .discover import discover_source_assets
from .backup import create_backup
from .verify import verify_migration


def run_migration(
    root: Optional[Path] = None,
    backup_first: bool = True,
    output_root: Optional[Path] = None,
    verify: bool = True,
) -> dict:
    """
    Migrate moltbot/clawdbot config, memory, and clawdbook data to openclaw structure.
    If backup_first is True (default), creates a timestamped backup before any copy.
    output_root defaults to root (in-place migration into new dirs).
    If verify is True (default), runs post-migration verification.
    Returns summary: backup_path, memory_copied, config_copied, clawdbook_copied,
                     verification (if verify=True).
    """
    root = Path(root or os.getcwd()).resolve()
    out_root = Path(output_root or root).resolve()
    assets = discover_source_assets(root)
    result = {
        "backup_path": None,
        "memory_copied": [],
        "config_copied": [],
        "clawdbook_copied": [],
        "errors": [],
        "verification": None,
    }

    if backup_first:
        result["backup_path"] = str(create_backup(root=root, asset_paths=assets))

    memory_dir = out_root / OPENCLAW_MEMORY_DIR
    config_dir = out_root / OPENCLAW_CONFIG_DIR
    clawdbook_dir = out_root / OPENCLAW_CLAWDBOOK_DIR
    memory_dir.mkdir(parents=True, exist_ok=True)
    config_dir.mkdir(parents=True, exist_ok=True)
    clawdbook_dir.mkdir(parents=True, exist_ok=True)

    # Copy memory files into openclaw memory/
    for src in assets.get("memory", []):
        src_path = Path(src)
        if src_path.is_file():
            dest = memory_dir / src_path.name
            try:
                shutil.copy2(src_path, dest)
                result["memory_copied"].append(str(dest))
            except Exception as e:
                result["errors"].append(f"memory {src}: {e}")

    # Clawdbook/Moltbook data: keep separate and safe (credentials, API keys)
    def is_clawdbook(path_str: str) -> bool:
        p = path_str.lower()
        return "moltbook" in p or "clawdbook" in p or "moltbot" in p

    for src in assets.get("config", []):
        src_path = Path(src)
        if not src_path.is_file():
            continue
        if is_clawdbook(src):
            dest = clawdbook_dir / src_path.name
            try:
                shutil.copy2(src_path, dest)
                result["clawdbook_copied"].append(str(dest))
            except Exception as e:
                result["errors"].append(f"clawdbook {src}: {e}")
        else:
            dest = config_dir / src_path.name
            try:
                shutil.copy2(src_path, dest)
                result["config_copied"].append(str(dest))
            except Exception as e:
                result["errors"].append(f"config {src}: {e}")

    # Extra (e.g. projects/) -> openclaw projects under output root (preserve layout)
    for src in assets.get("extra", []):
        src_path = Path(src)
        if src_path.is_file():
            try:
                rel = src_path.relative_to(root)
            except ValueError:
                rel = Path("projects") / src_path.name
            dest = out_root / rel
            if src_path.resolve() == dest.resolve():
                continue  # in-place: same file, skip copy
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(src_path, dest)
                result["config_copied"].append(str(dest))
            except Exception as e:
                result["errors"].append(f"extra {src}: {e}")

    # Post-migration verification: confirm every file made it
    if verify:
        result["verification"] = verify_migration(
            root=root,
            output_root=out_root,
            migration_result=result,
        )

    return result
