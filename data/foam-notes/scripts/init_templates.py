#!/usr/bin/env python3
"""
Initialize .foam/templates directory with starter templates.

Copies starter templates from the skill's assets/ directory to the
Foam workspace's .foam/templates/ directory.

Usage:
    python3 init_templates.py
    python3 init_templates.py --foam-root /path/to/workspace
    python3 init_templates.py --list
    python3 init_templates.py --force

Examples:
    python3 init_templates.py                    # Copy to current workspace
    python3 init_templates.py --foam-root ~/notes
    python3 init_templates.py --list            # Show available templates
    python3 init_templates.py --force           # Overwrite existing templates
"""

import argparse
import shutil
import sys
from pathlib import Path

from foam_config import load_config, get_foam_root


def get_skill_dir() -> Path:
    """Get the skill directory path."""
    return Path(__file__).parent.parent


def get_starter_templates() -> list:
    """Get list of available starter templates."""
    skill_dir = get_skill_dir()
    templates_dir = skill_dir / 'assets' / 'templates'
    
    if not templates_dir.exists():
        return []
    
    return list(templates_dir.glob('*.md'))


def list_templates():
    """Print available starter templates."""
    templates = get_starter_templates()
    
    if not templates:
        print("No starter templates found in assets/templates/")
        return
    
    print("Available starter templates:")
    print()
    for template in sorted(templates):
        print(f"  - {template.name}")
        # Show first few lines of description
        try:
            content = template.read_text()
            lines = content.split('\n')[:5]
            for line in lines:
                if line.strip() and not line.startswith('---'):
                    print(f"    {line[:60]}")
                    break
        except Exception:
            pass
        print()


def init_templates(foam_root: Path, force: bool = False) -> None:
    """Copy starter templates to Foam workspace."""
    # Create .foam/templates directory
    templates_dir = foam_root / '.foam' / 'templates'
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Get starter templates from assets
    skill_dir = get_skill_dir()
    assets_dir = skill_dir / 'assets' / 'templates'
    
    if not assets_dir.exists():
        print(f"Error: Starter templates not found at {assets_dir}", file=sys.stderr)
        sys.exit(1)
    
    starter_templates = list(assets_dir.glob('*.md'))
    
    if not starter_templates:
        print("Error: No starter templates found.", file=sys.stderr)
        sys.exit(1)
    
    copied = []
    skipped = []
    
    for template in starter_templates:
        dest = templates_dir / template.name
        
        if dest.exists() and not force:
            skipped.append(template.name)
            continue
        
        shutil.copy2(template, dest)
        copied.append(template.name)
    
    # Report results
    print(f"Initialized .foam/templates/ in: {foam_root}")
    print()
    
    if copied:
        print(f"Created {len(copied)} template(s):")
        for name in copied:
            print(f"  ✓ {name}")
    
    if skipped:
        print()
        print(f"Skipped {len(skipped)} existing template(s) (use --force to overwrite):")
        for name in skipped:
            print(f"  - {name}")
    
    print()
    print("Next steps:")
    print("  1. Open VS Code in your Foam workspace")
    print("  2. Use 'Foam: Create New Note From Template' to use templates")
    print("  3. Customize templates in .foam/templates/")


def main():
    parser = argparse.ArgumentParser(
        description='Initialize .foam/templates with starter templates'
    )
    parser.add_argument(
        '--foam-root',
        help='Foam workspace root directory (overrides config)'
    )
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List available starter templates'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Overwrite existing templates'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be copied without actually copying'
    )
    
    args = parser.parse_args()
    
    # Just list templates
    if args.list:
        list_templates()
        return
    
    # Get foam root
    config = load_config()
    
    if args.foam_root:
        foam_root = Path(args.foam_root).expanduser().resolve()
    else:
        foam_root = get_foam_root(config=config)
    
    if foam_root is None:
        print("Error: Not in a Foam workspace.", file=sys.stderr)
        print("Set foam_root in config.json or use --foam-root", file=sys.stderr)
        sys.exit(1)
    
    # Check if it's actually a Foam workspace
    if not (foam_root / '.vscode').exists() and not (foam_root / '.foam').exists():
        print(f"Warning: {foam_root} doesn't look like a Foam workspace.", file=sys.stderr)
        print("Expected to find .vscode/ or .foam/ directory.", file=sys.stderr)
        response = input("Continue anyway? [y/N]: ")
        if response.lower() not in ('y', 'yes'):
            sys.exit(0)
    
    # Dry run
    if args.dry_run:
        print(f"Would initialize .foam/templates/ in: {foam_root}")
        print()
        templates = get_starter_templates()
        print(f"Would copy {len(templates)} template(s):")
        for template in sorted(templates):
            dest = foam_root / '.foam' / 'templates' / template.name
            exists = "[EXISTS]" if dest.exists() else "[NEW]"
            print(f"  {exists} {template.name}")
        return
    
    # Initialize templates
    init_templates(foam_root, force=args.force)


if __name__ == '__main__':
    main()
