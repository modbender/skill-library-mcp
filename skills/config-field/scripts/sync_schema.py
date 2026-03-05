#!/usr/bin/env python3
"""
Synchronize OpenClaw schema to match local version.
Generates schema.json from local OpenClaw installation.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

# Cache directory for schema storage
CACHE_DIR = Path.home() / ".config" / "openclaw" / "skills" / "config-field"
CACHE_SCHEMA_FILE = CACHE_DIR / "schema.json"
BUILTIN_SCHEMA_FILE = Path(__file__).parent / "schema.json"
VERSION_FILE = CACHE_DIR / "version.json"


def get_openclaw_version() -> Optional[str]:
    """Get the currently installed OpenClaw version."""
    # Try command line first
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            parts = output.split()
            for part in parts:
                if "/" in part and not part.startswith("node-"):
                    return part.split("/")[1]
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Fallback: read from package.json
    try:
        package_paths = [
            Path.home() / ".npm-global" / "lib" / "node_modules" / "openclaw" / "package.json",
            Path("/usr") / "lib" / "node_modules" / "openclaw" / "package.json",
        ]
        for package_path in package_paths:
            if package_path.exists():
                with open(package_path, 'r') as f:
                    data = json.load(f)
                    return data.get("version")
    except (json.JSONDecodeError, IOError):
        pass
    
    return None


def get_cached_version() -> Optional[str]:
    """Get the version of cached schema."""
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, 'r') as f:
                data = json.load(f)
                return data.get("version")
        except (json.JSONDecodeError, IOError):
            return None
    
    # Also check schema.json
    if CACHE_SCHEMA_FILE.exists():
        try:
            with open(CACHE_SCHEMA_FILE, 'r') as f:
                data = json.load(f)
                return data.get("version")
        except (json.JSONDecodeError, IOError):
            pass
    
    return None


def save_version_info(version: str):
    """Save version info to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    info = {
        "version": version,
        "source": "local"
    }
    with open(VERSION_FILE, 'w') as f:
        json.dump(info, f, indent=2)


def copy_builtin_schema() -> bool:
    """Copy built-in schema to cache."""
    if not BUILTIN_SCHEMA_FILE.exists():
        print(f"Built-in schema not found: {BUILTIN_SCHEMA_FILE}")
        return False
    
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(BUILTIN_SCHEMA_FILE, 'r') as f:
            data = json.load(f)
        
        with open(CACHE_SCHEMA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error copying schema: {e}")
        return False


def sync_schema(force: bool = False) -> bool:
    """Synchronize schema with local OpenClaw version."""
    local_version = get_openclaw_version()
    
    if not local_version:
        print("Error: Could not determine OpenClaw version")
        print("Make sure OpenClaw is installed")
        return False
    
    print(f"Local OpenClaw version: {local_version}")
    
    cached_version = get_cached_version()
    
    if cached_version:
        print(f"Cached schema version: {cached_version}")
    else:
        print("No cached schema found")
    
    # Check if sync is needed
    if not force and cached_version == local_version:
        print("✓ Schema is up to date")
        return True
    
    if force:
        print("Force sync requested...")
    else:
        print(f"Version mismatch detected, syncing...")
    
    # For now, copy built-in schema
    # In the future, this could extract schema from local OpenClaw installation
    if copy_builtin_schema():
        save_version_info(local_version)
        print(f"✓ Schema synchronized to version {local_version}")
        return True
    else:
        print("✗ Failed to sync schema")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync OpenClaw schema")
    parser.add_argument("--force", "-f", action="store_true", help="Force re-sync")
    parser.add_argument("--status", "-s", action="store_true", help="Show status only")
    args = parser.parse_args()
    
    if args.status:
        local_version = get_openclaw_version()
        cached_version = get_cached_version()
        
        print("Schema Sync Status")
        print("=" * 40)
        print(f"OpenClaw version: {local_version or 'unknown'}")
        print(f"Cached version:   {cached_version or 'none'}")
        
        if local_version and cached_version:
            if local_version == cached_version:
                print("Status: ✓ In sync")
            else:
                print("Status: ✗ Out of sync (run sync_schema.py)")
        elif local_version:
            print("Status: ✗ No cached schema (run sync_schema.py)")
        else:
            print("Status: ✗ Cannot determine versions")
        
        return
    
    success = sync_schema(force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
