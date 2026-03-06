"""
Post-migration verification: confirm every discovered source file was copied
to the correct openclaw destination. Returns a detailed report so users know
exactly what succeeded, what's missing, and whether the migration is complete.
"""

import os
from pathlib import Path
from typing import Optional

from .config import (
    OPENCLAW_MEMORY_DIR,
    OPENCLAW_CONFIG_DIR,
    OPENCLAW_CLAWDBOOK_DIR,
)
from .discover import discover_source_assets


def verify_migration(
    root: Optional[Path] = None,
    output_root: Optional[Path] = None,
    migration_result: Optional[dict] = None,
) -> dict:
    """
    Verify that all discovered source assets were migrated to their openclaw
    destinations. Checks file existence and optionally file size match.

    Parameters
    ----------
    root : Path, optional
        Source root used for discovery (default: cwd).
    output_root : Path, optional
        Where migrated files should live (default: root).
    migration_result : dict, optional
        If provided, the result dict from run_migration is used to cross-check
        what the migrator *said* it copied.

    Returns
    -------
    dict with keys:
        passed          : bool   – True if every expected file is present
        total_expected  : int    – number of source files discovered
        total_verified  : int    – number of files confirmed at destination
        missing         : list[dict] – files that should exist but don't
        verified        : list[dict] – files confirmed present
        errors          : list[str]  – any unexpected errors during verification
    """
    root = Path(root or os.getcwd()).resolve()
    out_root = Path(output_root or root).resolve()
    assets = discover_source_assets(root)

    memory_dir = out_root / OPENCLAW_MEMORY_DIR
    config_dir = out_root / OPENCLAW_CONFIG_DIR
    clawdbook_dir = out_root / OPENCLAW_CLAWDBOOK_DIR

    result = {
        "passed": False,
        "total_expected": 0,
        "total_verified": 0,
        "missing": [],
        "verified": [],
        "errors": [],
    }

    # Helper: classify a config path as clawdbook or general config
    def _is_clawdbook(path_str: str) -> bool:
        p = path_str.lower()
        return "moltbook" in p or "clawdbook" in p or "moltbot" in p

    # --- Memory files ---
    for src in assets.get("memory", []):
        src_path = Path(src)
        if not src_path.is_file():
            continue
        result["total_expected"] += 1
        dest = memory_dir / src_path.name
        entry = {"source": str(src_path), "destination": str(dest), "type": "memory"}
        if dest.is_file():
            # Optional: verify size matches
            if dest.stat().st_size == src_path.stat().st_size:
                entry["size_match"] = True
            else:
                entry["size_match"] = False
            result["total_verified"] += 1
            result["verified"].append(entry)
        else:
            result["missing"].append(entry)

    # --- Config files ---
    for src in assets.get("config", []):
        src_path = Path(src)
        if not src_path.is_file():
            continue
        result["total_expected"] += 1
        if _is_clawdbook(src):
            dest = clawdbook_dir / src_path.name
            ftype = "clawdbook"
        else:
            dest = config_dir / src_path.name
            ftype = "config"
        entry = {"source": str(src_path), "destination": str(dest), "type": ftype}
        if dest.is_file():
            if dest.stat().st_size == src_path.stat().st_size:
                entry["size_match"] = True
            else:
                entry["size_match"] = False
            result["total_verified"] += 1
            result["verified"].append(entry)
        else:
            result["missing"].append(entry)

    # --- Extra files (projects/) ---
    for src in assets.get("extra", []):
        src_path = Path(src)
        if not src_path.is_file():
            continue
        result["total_expected"] += 1
        try:
            rel = src_path.relative_to(root)
        except ValueError:
            rel = Path("projects") / src_path.name
        dest = out_root / rel
        entry = {"source": str(src_path), "destination": str(dest), "type": "extra"}
        if dest.is_file():
            if dest.stat().st_size == src_path.stat().st_size:
                entry["size_match"] = True
            else:
                entry["size_match"] = False
            result["total_verified"] += 1
            result["verified"].append(entry)
        else:
            # For in-place migrations, source == dest, and the file still exists
            if src_path.resolve() == dest.resolve() and src_path.is_file():
                entry["size_match"] = True
                result["total_verified"] += 1
                result["verified"].append(entry)
            else:
                result["missing"].append(entry)

    # --- Cross-check with migration_result if provided ---
    if migration_result:
        reported_copied = (
            migration_result.get("memory_copied", [])
            + migration_result.get("config_copied", [])
            + migration_result.get("clawdbook_copied", [])
        )
        for reported in reported_copied:
            rp = Path(reported)
            if not rp.is_file():
                result["errors"].append(
                    f"Migration reported copying to {reported} but file does not exist"
                )

    result["passed"] = (
        result["total_verified"] == result["total_expected"]
        and len(result["missing"]) == 0
        and len(result["errors"]) == 0
    )

    return result
