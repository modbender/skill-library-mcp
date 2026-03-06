#!/usr/bin/env python3
"""
Validate a single field path against the OpenClaw Zod schema.
Auto-syncs schema if needed.
"""

import sys
from schema_loader import (
    ensure_schema_synced,
    get_field_info,
    find_similar_fields,
    SCHEMA_FIELDS,
    load_schema_json
)


def validate_field(field_path: str) -> dict:
    """Validate a field path and return result."""
    # Ensure schema is loaded
    fields = SCHEMA_FIELDS if SCHEMA_FIELDS else load_schema_fields()
    
    if not fields:
        return {
            "valid": False,
            "error": "Schema not loaded. Run: python3 scripts/sync_schema.py",
        }
    
    info = get_field_info(field_path, fields)
    
    if info:
        return {
            "valid": True,
            "path": field_path,
            "type": info.get("type", "unknown"),
            "optional": info.get("optional", True),
            "values": info.get("values", None),
        }
    else:
        suggestions = find_similar_fields(field_path, fields)
        return {
            "valid": False,
            "path": field_path,
            "suggestions": suggestions,
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_field.py <field-path>")
        print("Example: python3 validate_field.py agents.defaults.model.primary")
        print()
        print("This command auto-syncs schema if needed.")
        sys.exit(1)
    
    field_path = sys.argv[1]
    
    # Ensure schema is synced
    if not ensure_schema_synced():
        print("Warning: Could not sync schema, using fallback if available")
    
    result = validate_field(field_path)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    if result["valid"]:
        type_str = result["type"]
        if result.get("values"):
            values_display = ", ".join(result["values"][:5])
            if len(result["values"]) > 5:
                values_display += ", ..."
            type_str += f" ({values_display})"
        opt_str = "optional" if result["optional"] else "required"
        print(f"✓ Field exists: {result['path']}")
        print(f"  Type: {type_str}")
        print(f"  Required: {opt_str}")
    else:
        print(f"✗ Field not found: {result['path']}")
        if result["suggestions"]:
            print(f"\nDid you mean:")
            for suggestion in result["suggestions"]:
                print(f"  - {suggestion}")
        sys.exit(1)


if __name__ == "__main__":
    main()
