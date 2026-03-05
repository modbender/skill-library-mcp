#!/usr/bin/env python3
"""
Generate schema-fields.md from schema.json.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

SCRIPT_DIR = Path(__file__).parent
SCHEMA_FILE = SCRIPT_DIR / "schema.json"
OUTPUT_FILE = SCRIPT_DIR.parent / "references" / "schema-fields.md"


def format_type(field_info: Dict[str, Any]) -> str:
    """Format field type for display."""
    type_name = field_info.get("type", "unknown")
    
    if type_name == "enum":
        values = field_info.get("values", [])
        if values:
            display_vals = ", ".join(values[:5])
            if len(values) > 5:
                display_vals += ", ..."
            return f"enum ({display_vals})"
    
    return type_name


def generate_markdown(fields: Dict[str, Any]) -> str:
    """Generate markdown documentation."""
    lines = []
    
    lines.append("# OpenClaw Configuration Schema Fields")
    lines.append("")
    lines.append("Auto-generated from official Zod schema.")
    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("- **Field**: Configuration field path")
    lines.append("- **Type**: Data type")
    lines.append("- **Optional**: Whether field is optional (✓) or required (✗)")
    lines.append("")
    lines.append("## Field Reference")
    lines.append("")
    lines.append("| Field | Type | Optional |")
    lines.append("|-------|------|----------|")
    
    # Sort fields by path
    for field_path in sorted(fields.keys()):
        info = fields[field_path]
        type_str = format_type(info)
        optional = "✓" if info.get("optional", True) else "✗"
        lines.append(f"| `{field_path}` | {type_str} | {optional} |")
    
    lines.append("")
    lines.append("## Usage Examples")
    lines.append("")
    lines.append("### Validate a field:")
    lines.append("```bash")
    lines.append("python3 scripts/validate_field.py agents.defaults.model.primary")
    lines.append("```")
    lines.append("")
    lines.append("### Validate config file:")
    lines.append("```bash")
    lines.append("python3 scripts/validate_config.py ~/.config/openclaw/openclaw.json")
    lines.append("```")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("*Generated automatically from OpenClaw Zod Schema*")
    
    return "\n".join(lines)


def main():
    print("Generating field reference from schema...")
    
    if not SCHEMA_FILE.exists():
        print(f"Error: Schema file not found: {SCHEMA_FILE}")
        sys.exit(1)
    
    with open(SCHEMA_FILE, 'r') as f:
        data = json.load(f)
    
    fields = data.get("fields", {})
    print(f"Loaded {len(fields)} field definitions")
    
    markdown = generate_markdown(fields)
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(markdown)
    
    print(f"✓ Generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
