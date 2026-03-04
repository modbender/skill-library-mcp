#!/usr/bin/env python3
"""
Workspace Cleaner - Safe cleanup for OpenClaw workspaces.
Finds temp files, duplicates, and cruft while protecting important data.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Default configuration
DEFAULT_CONFIG = {
    "temp_extensions": [".tmp", ".bak", ".log", ".skill"],
    "temp_patterns": ["*~", "#*#", "*.swp", "*.swo"],
    "image_extensions": [".png", ".jpg", ".jpeg", ".gif", ".webp"],
    "protected_dirs": ["memory", "skills", "projects", ".git", "archive"],
    "protected_files": [
        "MEMORY.md", "SOUL.md", "USER.md", "AGENTS.md", "TOOLS.md",
        "HEARTBEAT.md", "IDENTITY.md", "BOOTSTRAP.md"
    ],
    "known_venvs": [".venv-skill-scanner"],
    "skip_dirs": ["node_modules", "__pycache__", ".git"]
}

# ANSI colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


def load_config(config_path: Optional[Path]) -> dict:
    """Load configuration from file or use defaults."""
    if config_path and config_path.exists():
        with open(config_path) as f:
            user_config = json.load(f)
            # Merge with defaults
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
    return DEFAULT_CONFIG.copy()


def get_size(path: Path) -> int:
    """Get size of file or directory in bytes."""
    if path.is_file():
        return path.stat().st_size
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                total += entry.stat().st_size
    except PermissionError:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format size in human-readable form."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def get_age_days(path: Path) -> float:
    """Get age of file in days."""
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return (datetime.now() - mtime).days


def get_git_remote(repo_path: Path) -> Optional[str]:
    """Get git remote URL for a repository."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def find_cleanup_targets(
    workspace: Path,
    config: dict,
    min_size_mb: float = 0,
    min_age_days: int = 0,
    include_recent: bool = False
) -> list[dict]:
    """Find all items that could be cleaned up."""
    targets = []
    
    # Track projects remotes for duplicate detection
    project_remotes = {}
    projects_dir = workspace / "projects"
    if projects_dir.exists():
        for pdir in projects_dir.iterdir():
            if pdir.is_dir() and (pdir / ".git").exists():
                remote = get_git_remote(pdir)
                if remote:
                    project_remotes[remote] = pdir.name

    # Check root-level items
    for item in workspace.iterdir():
        # Skip protected
        if item.name in config["protected_dirs"]:
            continue
        if item.name in config["protected_files"]:
            continue
        if item.name.startswith(".") and item.name not in [".DS_Store"]:
            # Skip hidden dirs except .DS_Store
            if item.is_dir():
                continue
        
        target = None
        
        # Check temp extensions
        if item.is_file():
            if item.suffix.lower() in config["temp_extensions"]:
                target = {"path": item, "reason": f"temp file ({item.suffix})"}
            # Check image files in root
            elif item.suffix.lower() in config["image_extensions"]:
                target = {"path": item, "reason": "image in root"}
            # Check temp patterns
            elif any(item.match(p) for p in config["temp_patterns"]):
                target = {"path": item, "reason": "temp pattern"}
            # .DS_Store
            elif item.name == ".DS_Store":
                target = {"path": item, "reason": "macOS metadata"}
        
        # Check directories
        elif item.is_dir():
            # node_modules in root
            if item.name == "node_modules":
                target = {"path": item, "reason": "root node_modules"}
            # venvs (except known)
            elif item.name.startswith(".venv") or item.name == "venv":
                if item.name not in config.get("known_venvs", []):
                    target = {"path": item, "reason": "python venv"}
            # Duplicate repos
            elif (item / ".git").exists():
                remote = get_git_remote(item)
                if remote and remote in project_remotes:
                    target = {
                        "path": item,
                        "reason": f"duplicate of projects/{project_remotes[remote]}"
                    }
        
        if target:
            size = get_size(target["path"])
            age = get_age_days(target["path"])
            
            # Apply filters
            if min_size_mb > 0 and size < min_size_mb * 1024 * 1024:
                continue
            if min_age_days > 0 and age < min_age_days:
                continue
            if not include_recent and age < 1:
                continue
            
            target["size"] = size
            target["size_human"] = format_size(size)
            target["size_mb"] = round(size / (1024 * 1024), 2)
            target["age_days"] = round(age, 1)
            targets.append(target)
    
    return targets


def trash_item(path: Path) -> bool:
    """Move item to trash. Returns True on success."""
    try:
        # Try 'trash' command (macOS)
        result = subprocess.run(
            ["trash", str(path)],
            capture_output=True
        )
        if result.returncode == 0:
            return True
        
        # Try 'trash-put' (Linux trash-cli)
        result = subprocess.run(
            ["trash-put", str(path)],
            capture_output=True
        )
        if result.returncode == 0:
            return True
        
        # Fallback: move to ~/.Trash (macOS) or fail
        trash_dir = Path.home() / ".Trash"
        if trash_dir.exists():
            dest = trash_dir / path.name
            if dest.exists():
                dest = trash_dir / f"{path.name}.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.move(str(path), str(dest))
            return True
            
    except Exception as e:
        print(f"{RED}Error trashing {path}: {e}{NC}", file=sys.stderr)
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Safe workspace cleanup for OpenClaw"
    )
    parser.add_argument(
        "-w", "--workspace",
        type=Path,
        default=Path(os.environ.get("CLAWD_WORKSPACE", Path.home() / "clawd")),
        help="Workspace path (default: ~/clawd or $CLAWD_WORKSPACE)"
    )
    parser.add_argument(
        "-x", "--execute",
        action="store_true",
        help="Actually delete (default: dry-run preview)"
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Custom config file path"
    )
    parser.add_argument(
        "--min-size",
        type=float,
        default=0,
        help="Only show items larger than N MB"
    )
    parser.add_argument(
        "--min-age",
        type=int,
        default=0,
        help="Only show items older than N days"
    )
    parser.add_argument(
        "--include-recent",
        action="store_true",
        help="Include files modified in last 24 hours"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    # Validate workspace
    if not args.workspace.exists():
        print(f"{RED}Workspace not found: {args.workspace}{NC}", file=sys.stderr)
        sys.exit(1)
    
    # Load config
    config = load_config(args.config)
    
    # Find targets
    targets = find_cleanup_targets(
        args.workspace,
        config,
        min_size_mb=args.min_size,
        min_age_days=args.min_age,
        include_recent=args.include_recent
    )
    
    # JSON output
    if args.json:
        output = {
            "workspace": str(args.workspace),
            "mode": "execute" if args.execute else "preview",
            "count": len(targets),
            "total_size_mb": round(sum(t["size"] for t in targets) / (1024 * 1024), 2),
            "items": [
                {
                    "path": str(t["path"]),
                    "reason": t["reason"],
                    "size_mb": t["size_mb"],
                    "age_days": t["age_days"]
                }
                for t in targets
            ]
        }
        print(json.dumps(output, indent=2))
        if args.execute:
            for t in targets:
                trash_item(t["path"])
        return
    
    # Human output
    if not args.quiet:
        print(f"{BLUE}=== Workspace Cleaner ==={NC}")
        print(f"Workspace: {args.workspace}")
        print(f"Mode: {RED}EXECUTE{NC}" if args.execute else f"Mode: {YELLOW}DRY RUN (preview){NC}")
        print()
    
    if not targets:
        if not args.quiet:
            print(f"{GREEN}✓ Workspace is clean! Nothing to delete.{NC}")
        return
    
    # Show targets
    total_size = 0
    for t in sorted(targets, key=lambda x: x["size"], reverse=True):
        total_size += t["size"]
        if not args.quiet:
            print(f"  {YELLOW}{t['size_human']:>8}{NC}  {t['path'].name}  {BLUE}({t['reason']}){NC}")
    
    print()
    print(f"Found {YELLOW}{len(targets)}{NC} items totaling {YELLOW}{format_size(total_size)}{NC}")
    print()
    
    if args.execute:
        print(f"{RED}Deleting...{NC}")
        success = 0
        for t in targets:
            if trash_item(t["path"]):
                success += 1
                if not args.quiet:
                    print(f"  Trashed: {t['path'].name}")
        print()
        print(f"{GREEN}✓ Cleanup complete! {success}/{len(targets)} items moved to trash.{NC}")
    else:
        print(f"{YELLOW}This was a dry run. To actually delete, run with --execute{NC}")


if __name__ == "__main__":
    main()
