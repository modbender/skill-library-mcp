#!/usr/bin/env python3
"""
Smart Stitch v2.0

Updated to work with the progressive experience storage structure.
Instead of dumping all experiences into SKILL.md, it now:
1. Updates the experience index
2. Stores experiences in appropriate category files
3. Only adds a brief summary to SKILL.md (not full content)
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# Add programming-assistant scripts to path
SCRIPT_DIR = Path(__file__).parent
PROG_ASSIST_SCRIPTS = SCRIPT_DIR.parent.parent / 'programming-assistant' / 'scripts'
if str(PROG_ASSIST_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PROG_ASSIST_SCRIPTS))


def stitch_skill_v2(skill_dir: str):
    """
    New version: Store experiences in progressive structure.
    Only add a summary reference to SKILL.md.
    """
    skill_path = Path(skill_dir)
    skill_md_path = skill_path / "SKILL.md"
    evolution_json_path = skill_path / "evolution.json"
    experience_dir = skill_path / "experience"

    if not skill_md_path.exists():
        print(f"Error: SKILL.md not found in {skill_dir}", file=sys.stderr)
        return False
        
    if not evolution_json_path.exists():
        print(f"Info: No evolution.json found in {skill_dir}. Nothing to stitch.", file=sys.stderr)
        return True

    try:
        with open(evolution_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error parsing evolution.json: {e}", file=sys.stderr)
        return False

    # Check if skill uses progressive loading
    skill_content = skill_md_path.read_text(encoding='utf-8')
    uses_progressive = 'progressive: true' in skill_content or 'progressive_load: true' in skill_content

    if uses_progressive:
        # Use new progressive storage
        return migrate_to_progressive(skill_path, data)
    else:
        # Fall back to legacy behavior
        return stitch_skill_legacy(skill_path, data)


def migrate_to_progressive(skill_path: Path, data: dict) -> bool:
    """Migrate evolution data to progressive storage structure."""
    experience_dir = skill_path / 'experience'
    experience_dir.mkdir(exist_ok=True)
    (experience_dir / 'tech').mkdir(exist_ok=True)
    (experience_dir / 'contexts').mkdir(exist_ok=True)

    # Load or create index
    index_path = experience_dir / 'index.json'
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {
            'version': '2.0.0',
            'last_updated': None,
            'index': {'tech_stacks': [], 'contexts': [], 'total_experiences': 0},
            'preferences': [],
            'fixes': []
        }

    # Migrate preferences
    for pref in data.get('preferences', []):
        if pref not in index['preferences']:
            index['preferences'].append(pref)
            index['index']['total_experiences'] += 1

    # Migrate fixes
    for fix in data.get('fixes', []):
        if fix not in index['fixes']:
            index['fixes'].append(fix)
            index['index']['total_experiences'] += 1

    # Migrate patterns to tech-specific files
    for tech, patterns in data.get('patterns', {}).items():
        if isinstance(patterns, list) and patterns:
            tech_lower = tech.lower()
            tech_file = experience_dir / 'tech' / f'{tech_lower}.json'
            
            if tech_file.exists():
                with open(tech_file, 'r', encoding='utf-8') as f:
                    tech_data = json.load(f)
            else:
                tech_data = {'name': tech, 'patterns': [], 'tips': []}
            
            for pattern in patterns:
                if pattern not in tech_data['patterns']:
                    tech_data['patterns'].append(pattern)
                    index['index']['total_experiences'] += 1
            
            with open(tech_file, 'w', encoding='utf-8') as f:
                json.dump(tech_data, f, indent=2, ensure_ascii=False)
            
            if tech_lower not in index['index']['tech_stacks']:
                index['index']['tech_stacks'].append(tech_lower)

    # Migrate context triggers
    for context, instruction in data.get('context_triggers', {}).items():
        context_lower = context.lower().replace(' ', '_')
        context_file = experience_dir / 'contexts' / f'{context_lower}.json'
        
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                ctx_data = json.load(f)
        else:
            ctx_data = {'name': context, 'instructions': []}
        
        if instruction not in ctx_data['instructions']:
            ctx_data['instructions'].append(instruction)
            index['index']['total_experiences'] += 1
        
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(ctx_data, f, indent=2, ensure_ascii=False)
        
        if context_lower not in index['index']['contexts']:
            index['index']['contexts'].append(context_lower)

    # Save index
    index['last_updated'] = datetime.now().isoformat()
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"Migrated {index['index']['total_experiences']} experiences to progressive structure")
    
    # Optionally remove evolution.json after migration
    # For safety, we'll rename it instead
    evolution_json_path = skill_path / 'evolution.json'
    backup_path = skill_path / 'evolution.json.migrated'
    if evolution_json_path.exists():
        evolution_json_path.rename(backup_path)
        print(f"Backed up evolution.json to evolution.json.migrated")

    return True


def stitch_skill_legacy(skill_path: Path, data: dict) -> bool:
    """Legacy behavior: stitch all experiences into SKILL.md."""
    skill_md_path = skill_path / "SKILL.md"
    
    # Prepare the Markdown content block
    evolution_section = []
    evolution_section.append("\n\n## User-Learned Best Practices & Constraints")
    evolution_section.append("\n> **Auto-Generated Section**: This section is maintained by `evolving-agent`. Do not edit manually.")

    if data.get("preferences"):
        evolution_section.append("\n### User Preferences")
        for item in data["preferences"]:
            evolution_section.append(f"- {item}")

    if data.get("fixes"):
        evolution_section.append("\n### Known Fixes & Workarounds")
        for item in data["fixes"]:
            evolution_section.append(f"- {item}")

    if data.get("patterns"):
        evolution_section.append("\n### Learned Patterns")
        for pattern_type, items in data["patterns"].items():
            if isinstance(items, list) and items:
                evolution_section.append(f"\n#### {pattern_type.capitalize()}")
                for item in items:
                    evolution_section.append(f"- {item}")

    if data.get("context_triggers"):
        evolution_section.append("\n### Context Triggers")
        for trigger, instruction in data["context_triggers"].items():
            evolution_section.append(f"\n- **{trigger}**: {instruction}")

    if data.get("custom_prompts"):
        evolution_section.append("\n### Custom Instruction Injection")
        evolution_section.append(f"\n{data['custom_prompts']}")

    evolution_block = "\n".join(evolution_section)

    # Read original SKILL.md
    content = skill_md_path.read_text(encoding='utf-8')

    # Regex to find existing User-Learned section and replace it
    pattern = r"(\n+## User-Learned Best Practices & Constraints.*$)"
    
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        print("Updating existing evolution section...", file=sys.stderr)
        new_content = content[:match.start()] + evolution_block
    else:
        print("Appending new evolution section...", file=sys.stderr)
        new_content = content + evolution_block

    skill_md_path.write_text(new_content, encoding='utf-8')
    print(f"Successfully stitched evolution data into {skill_md_path}")
    return True


def stitch_skill(skill_dir):
    """Entry point - use v2 by default."""
    return stitch_skill_v2(skill_dir)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smart_stitch.py <skill_dir>")
        sys.exit(1)
        
    target_dir = sys.argv[1]
    stitch_skill(target_dir)
