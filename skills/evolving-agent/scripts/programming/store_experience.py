#!/usr/bin/env python3
"""
Experience Storage Tool (v2.0)

Store experiences in a progressive-loading friendly structure.
Experiences are stored by tech stack and context, not all in one file.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def ensure_directories(experience_dir: Path):
    """Ensure experience directory structure exists."""
    experience_dir.mkdir(parents=True, exist_ok=True)
    (experience_dir / 'tech').mkdir(exist_ok=True)
    (experience_dir / 'contexts').mkdir(exist_ok=True)


def load_index(experience_dir: Path) -> dict:
    """Load the experience index."""
    index_path = experience_dir / 'index.json'
    if not index_path.exists():
        return {
            'version': '2.0.0',
            'last_updated': None,
            'index': {'tech_stacks': [], 'contexts': [], 'total_experiences': 0},
            'preferences': [],
            'fixes': []
        }
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_index(experience_dir: Path, index: dict):
    """Save the experience index."""
    index['last_updated'] = datetime.now().isoformat()
    index_path = experience_dir / 'index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def add_preference(experience_dir: Path, preference: str):
    """Add a user preference."""
    index = load_index(experience_dir)
    if preference not in index['preferences']:
        index['preferences'].append(preference)
        index['index']['total_experiences'] += 1
        save_index(experience_dir, index)
        print(f"Added preference: {preference}")
    else:
        print(f"Preference already exists: {preference}")


def add_fix(experience_dir: Path, fix: str):
    """Add a known fix."""
    index = load_index(experience_dir)
    if fix not in index['fixes']:
        index['fixes'].append(fix)
        index['index']['total_experiences'] += 1
        save_index(experience_dir, index)
        print(f"Added fix: {fix}")
    else:
        print(f"Fix already exists: {fix}")


def add_tech_pattern(experience_dir: Path, tech: str, pattern: str):
    """Add a pattern for a specific tech stack."""
    tech_lower = tech.lower()
    tech_file = experience_dir / 'tech' / f'{tech_lower}.json'
    
    if tech_file.exists():
        with open(tech_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'name': tech, 'patterns': [], 'tips': []}
    
    if pattern not in data['patterns']:
        data['patterns'].append(pattern)
        with open(tech_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = load_index(experience_dir)
        if tech_lower not in index['index']['tech_stacks']:
            index['index']['tech_stacks'].append(tech_lower)
        index['index']['total_experiences'] += 1
        save_index(experience_dir, index)
        
        print(f"Added pattern to {tech}: {pattern}")
    else:
        print(f"Pattern already exists in {tech}: {pattern}")


def add_context_trigger(experience_dir: Path, context: str, instruction: str):
    """Add a context trigger."""
    context_lower = context.lower().replace(' ', '_')
    context_file = experience_dir / 'contexts' / f'{context_lower}.json'
    
    if context_file.exists():
        with open(context_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'name': context, 'instructions': []}
    
    if instruction not in data['instructions']:
        data['instructions'].append(instruction)
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = load_index(experience_dir)
        if context_lower not in index['index']['contexts']:
            index['index']['contexts'].append(context_lower)
        index['index']['total_experiences'] += 1
        save_index(experience_dir, index)
        
        print(f"Added context trigger: {context} -> {instruction}")
    else:
        print(f"Context trigger already exists: {context}")


def merge_from_json(experience_dir: Path, json_str: str):
    """Merge experiences from JSON string (for backward compatibility)."""
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return False
    
    # Process preferences
    for pref in data.get('preferences', []):
        add_preference(experience_dir, pref)
    
    # Process fixes
    for fix in data.get('fixes', []):
        add_fix(experience_dir, fix)
    
    # Process patterns (tech-specific)
    for tech, patterns in data.get('patterns', {}).items():
        if isinstance(patterns, list):
            for pattern in patterns:
                add_tech_pattern(experience_dir, tech, pattern)
    
    # Process context triggers
    for context, instruction in data.get('context_triggers', {}).items():
        add_context_trigger(experience_dir, context, instruction)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Store programming experiences progressively',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python store_experience.py --preference "使用 pnpm 而非 npm"
  python store_experience.py --fix "macOS 上 node-gyp 需要 Xcode CLI"
  python store_experience.py --tech react --pattern "使用函数式组件"
  python store_experience.py --context when_testing --instruction "使用 Vitest"
  python store_experience.py --merge '{"preferences": ["..."]}'
        """
    )
    
    parser.add_argument(
        '--preference',
        help='Add a user preference'
    )
    parser.add_argument(
        '--fix',
        help='Add a known fix/workaround'
    )
    parser.add_argument(
        '--tech',
        help='Tech stack name (used with --pattern)'
    )
    parser.add_argument(
        '--pattern',
        help='Add a pattern for a tech stack'
    )
    parser.add_argument(
        '--context',
        help='Context trigger name (used with --instruction)'
    )
    parser.add_argument(
        '--instruction',
        help='Add an instruction for a context'
    )
    parser.add_argument(
        '--merge',
        help='Merge experiences from JSON string'
    )
    parser.add_argument(
        '--experience-dir',
        default=os.path.join(os.path.dirname(__file__), '..', 'experience'),
        help='Experience directory path'
    )
    
    args = parser.parse_args()
    experience_dir = Path(args.experience_dir)
    ensure_directories(experience_dir)
    
    if args.preference:
        add_preference(experience_dir, args.preference)
    elif args.fix:
        add_fix(experience_dir, args.fix)
    elif args.tech and args.pattern:
        add_tech_pattern(experience_dir, args.tech, args.pattern)
    elif args.context and args.instruction:
        add_context_trigger(experience_dir, args.context, args.instruction)
    elif args.merge:
        merge_from_json(experience_dir, args.merge)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
