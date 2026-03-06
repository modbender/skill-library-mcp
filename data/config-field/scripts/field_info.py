#!/usr/bin/env python3
"""
Get detailed information about a configuration field.
Auto-syncs schema if needed.
"""

import sys
from schema_loader import (
    ensure_schema_synced,
    get_field_info,
    SCHEMA_FIELDS,
    load_schema_json
)


def format_field_info(field_path: str, info: dict) -> str:
    """Format field information for display."""
    if not info:
        return f"Field not found: {field_path}"
    
    lines = []
    lines.append(f"Field: {field_path}")
    lines.append(f"{'=' * 50}")
    
    # Type
    field_type = info.get("type", "unknown")
    lines.append(f"Type: {field_type}")
    
    # Optional/Required
    optional = info.get("optional", True)
    lines.append(f"Required: {'No (optional)' if optional else 'Yes'}")
    
    # Enum values
    if "values" in info and info["values"]:
        lines.append(f"\nAllowed values:")
        for value in info["values"]:
            lines.append(f"  - {value}")
    
    # Parent info for child fields
    if "parent" in info:
        lines.append(f"\nParent: {info['parent']}")
        lines.append("(This field is a child of the above object)")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 field_info.py <field-path>")
        print("Example: python3 field_info.py agents.defaults.model")
        print()
        print("Common field paths:")
        print("  agents.defaults.model.primary")
        print("  agents.defaults.workspace")
        print("  channels.telegram.enabled")
        print("  logging.level")
        print()
        print("This command auto-syncs schema if needed.")
        sys.exit(1)
    
    field_path = sys.argv[1]
    
    # Ensure schema is synced
    if not ensure_schema_synced():
        print("Warning: Could not sync schema, using fallback if available")
    
    # Load fields
    fields = SCHEMA_FIELDS if SCHEMA_FIELDS else load_schema_json()
    
    if not fields:
        print("Error: Schema not loaded. Run: python3 scripts/sync_schema.py")
        sys.exit(1)
    
    info = get_field_info(field_path, fields)
    
    if info:
        print(format_field_info(field_path, info))
    else:
        print(f"Field not found: {field_path}")
        
        # Try to provide context by checking parent paths
        parts = field_path.split('.')
        for i in range(len(parts) - 1, 0, -1):
            parent_path = '.'.join(parts[:i])
            parent_info = get_field_info(parent_path, fields)
            if parent_info:
                print(f"\nParent field '{parent_path}' exists:")
                print(format_field_info(parent_path, parent_info))
                break
        
        sys.exit(1)


if __name__ == "__main__":
    main()
