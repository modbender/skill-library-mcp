#!/usr/bin/env python3
"""
Shared schema loading utilities.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Paths
CACHE_DIR = Path.home() / ".config" / "openclaw" / "skills" / "config-field"
CACHE_SCHEMA_FILE = CACHE_DIR / "schema.json"
BUILTIN_SCHEMA_FILE = Path(__file__).parent / "schema.json"


def load_schema_json() -> Dict[str, Any]:
    """Load schema from JSON file."""
    # Try cached schema first
    if CACHE_SCHEMA_FILE.exists():
        try:
            with open(CACHE_SCHEMA_FILE, 'r') as f:
                data = json.load(f)
                return data.get("fields", {})
        except (json.JSONDecodeError, IOError):
            pass
    
    # Fall back to built-in schema
    if BUILTIN_SCHEMA_FILE.exists():
        try:
            with open(BUILTIN_SCHEMA_FILE, 'r') as f:
                data = json.load(f)
                return data.get("fields", {})
        except (json.JSONDecodeError, IOError):
            pass
    
    return {}


def save_schema_json(fields: Dict[str, Any], version: str):
    """Save schema to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "version": version,
        "generated_at": "auto",
        "source": "openclaw zod-schema",
        "fields": fields
    }
    with open(CACHE_SCHEMA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_field_info(field_path: str, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get information about a specific field."""
    # Try exact match first
    if field_path in fields:
        return fields[field_path]
    
    # Try matching parent paths
    parts = field_path.split('.')
    for i in range(len(parts) - 1, 0, -1):
        parent_path = '.'.join(parts[:i])
        if parent_path in fields:
            parent_info = fields[parent_path]
            # Check if parent is an object that could contain this field
            if parent_info.get('type') == 'object':
                # Field might be valid but not documented individually
                return {
                    "type": "unknown (child of object)",
                    "optional": True,
                    "parent": parent_path,
                }
    
    return None


def find_similar_fields(field_path: str, fields: Dict[str, Any], max_results: int = 3) -> List[str]:
    """Find similar field paths for typo suggestions."""
    from difflib import get_close_matches
    
    all_paths = list(fields.keys())
    
    # Get close matches
    matches = get_close_matches(field_path, all_paths, n=max_results, cutoff=0.6)
    
    # Also try matching just the last part
    parts = field_path.split('.')
    if len(parts) > 1:
        last_part = parts[-1]
        for path in all_paths:
            if path.endswith(f".{last_part}") and path not in matches:
                matches.append(path)
                if len(matches) >= max_results:
                    break
    
    return matches[:max_results]


def get_schema_version() -> Optional[str]:
    """Get the version of the cached schema."""
    if CACHE_SCHEMA_FILE.exists():
        try:
            with open(CACHE_SCHEMA_FILE, 'r') as f:
                data = json.load(f)
                return data.get("version")
        except (json.JSONDecodeError, IOError):
            pass
    return None


def ensure_schema_synced() -> bool:
    """Ensure schema is synced before validation."""
    # Load current schema
    fields = load_schema_json()
    
    if not fields:
        print("Schema not found. Please run: python3 scripts/sync_schema.py")
        return False
    
    return True


# Load fields on module import
SCHEMA_FIELDS = load_schema_json()
