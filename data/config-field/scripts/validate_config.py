#!/usr/bin/env python3
"""
Validate an entire OpenClaw configuration file against the Zod schema.
Auto-syncs schema if needed.
"""

import sys
import json
import re
from pathlib import Path
from schema_loader import (
    ensure_schema_synced,
    get_field_info,
    find_similar_fields,
    SCHEMA_FIELDS,
    load_schema_json
)


def extract_field_paths(obj: any, prefix: str = "") -> list:
    """Extract all field paths from a configuration object."""
    paths = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Skip special keys
            if key.startswith("$"):
                continue
            
            path = f"{prefix}.{key}" if prefix else key
            paths.append(path)
            
            if isinstance(value, (dict, list)):
                paths.extend(extract_field_paths(value, path))
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, (dict, list)):
                paths.extend(extract_field_paths(item, prefix))
    
    return paths


def validate_config_file(config_path: str) -> dict:
    """Validate a configuration file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        return {"error": f"File not found: {config_path}"}
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Try to parse as JSON/JSON5
        try:
            config = json.loads(content)
        except json.JSONDecodeError:
            # Try JSON5-like parsing (allow comments and trailing commas)
            # Remove comments
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # Remove trailing commas
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            config = json.loads(content)
    
    except Exception as e:
        return {"error": f"Failed to parse config: {e}"}
    
    # Load schema fields
    fields = SCHEMA_FIELDS if SCHEMA_FIELDS else load_schema_json()
    
    if not fields:
        return {"error": "Schema not loaded. Run: python3 scripts/sync_schema.py"}
    
    # Extract all field paths
    field_paths = extract_field_paths(config)
    
    # Validate each path
    valid_fields = []
    invalid_fields = []
    warnings = []
    
    for path in field_paths:
        info = get_field_info(path, fields)
        if info:
            valid_fields.append({
                "path": path,
                "type": info.get("type", "unknown"),
            })
        else:
            suggestions = find_similar_fields(path, fields)
            invalid_fields.append({
                "path": path,
                "suggestions": suggestions,
            })
    
    return {
        "valid_fields": valid_fields,
        "invalid_fields": invalid_fields,
        "warnings": warnings,
        "total": len(field_paths),
    }


def print_validation_report(result: dict, config_path: str):
    """Print a formatted validation report."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print(f"Validating: {config_path}")
    print(f"Total fields: {result['total']}")
    print()
    
    if result["valid_fields"]:
        print("✓ Valid fields:")
        for field in sorted(result["valid_fields"], key=lambda x: x["path"]):
            print(f"  - {field['path']} ({field['type']})")
        print()
    
    if result["invalid_fields"]:
        print("✗ Invalid fields:")
        for field in sorted(result["invalid_fields"], key=lambda x: x["path"]):
            print(f"  - {field['path']}")
            if field["suggestions"]:
                print(f"    Suggestion: {field['suggestions'][0]}")
        print()
    
    if result["warnings"]:
        print("⚠ Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
        print()
    
    # Summary
    valid_count = len(result["valid_fields"])
    invalid_count = len(result["invalid_fields"])
    
    print("=" * 50)
    if invalid_count == 0:
        print(f"✓ All {valid_count} fields are valid!")
    else:
        print(f"✗ Found {invalid_count} invalid field(s) out of {result['total']}")
        print(f"  Valid: {valid_count}")
        print(f"  Invalid: {invalid_count}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_config.py <config-file>")
        print("Example: python3 validate_config.py ~/.config/openclaw/openclaw.json")
        print()
        print("This command auto-syncs schema if needed.")
        sys.exit(1)
    
    config_path = sys.argv[1]
    
    # Ensure schema is synced
    if not ensure_schema_synced():
        print("Warning: Could not sync schema, using fallback if available")
    
    result = validate_config_file(config_path)
    print_validation_report(result, config_path)
    
    # Exit with error code if invalid fields found
    if result.get("invalid_fields"):
        sys.exit(1)


if __name__ == "__main__":
    main()
