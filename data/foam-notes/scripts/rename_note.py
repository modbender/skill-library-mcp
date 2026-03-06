#!/usr/bin/env python3
"""
Rename a note in a Foam workspace and update all wikilinks.

Usage:
    python3 rename_note.py <old-name> <new-name>
    python3 rename_note.py "Old Note" "New Note" --force

Examples:
    python3 rename_note.py "My Note" "My Better Note"     # Interactive rename
    python3 rename_note.py "My Note" "My Better Note" --force  # Skip confirmation
"""

import argparse
import re
import sys
from pathlib import Path

from foam_config import load_config, get_foam_root, slugify


def find_note(target: str, foam_root: Path) -> Path:
    """Find a note by name or filename."""
    target_stem = target.replace(".md", "")

    # Try exact match first
    exact_path = foam_root / f"{target_stem}.md"
    if exact_path.exists():
        return exact_path

    # Search all markdown files
    for md_file in foam_root.rglob("*.md"):
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        if md_file.stem.lower() == target_stem.lower():
            return md_file

    return None


def find_backlinks(old_stem: str, foam_root: Path) -> list:
    """Find all notes that link to the old note name."""
    backlinks = []
    old_stem_lower = old_stem.lower()

    # Pattern to match wikilinks to this note
    patterns = [
        rf"\[\[{re.escape(old_stem_lower)}\]\]",
        rf"\[\[{re.escape(old_stem_lower)}#[^\]]+\]\]",
        rf"\[\[{re.escape(old_stem_lower)}\|[^\]]+\]\]",
    ]

    for md_file in foam_root.rglob("*.md"):
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        try:
            content = md_file.read_text()
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    backlinks.append(md_file)
                    break
        except Exception:
            continue

    return backlinks


def update_wikilinks(
    old_stem: str, new_stem: str, foam_root: Path, backlinks: list
) -> int:
    """Update all wikilinks from old name to new name."""
    updated_count = 0

    # Pattern to match wikilinks with optional section or alias
    # This captures: [[old-stem]], [[old-stem#section]], [[old-stem|alias]]
    pattern = rf"\[\[{re.escape(old_stem)}((?:#[^\]]+)?(?:\|[^\]]+)?)\]\]"

    def replace_link(match):
        suffix = match.group(1) or ""
        return f"[[{new_stem}{suffix}]]"

    for backlink_file in backlinks:
        try:
            content = backlink_file.read_text()
            original_content = content

            # Replace all wikilinks to the old note
            content = re.sub(pattern, replace_link, content, flags=re.IGNORECASE)

            if content != original_content:
                backlink_file.write_text(content)
                updated_count += 1
        except Exception as e:
            print(f"Warning: Could not update {backlink_file}: {e}", file=sys.stderr)

    return updated_count


def rename_note(
    old_name: str, new_name: str, foam_root: Path, force: bool = False
) -> bool:
    """Rename a note and update all wikilinks."""

    # Find the old note
    old_path = find_note(old_name, foam_root)
    if old_path is None:
        print(f"Error: Note '{old_name}' not found.", file=sys.stderr)
        return False

    old_stem = old_path.stem
    new_stem = slugify(new_name)
    new_path = old_path.parent / f"{new_stem}.md"

    # Check if new name already exists
    if new_path.exists():
        print(
            f"Error: Note '{new_name}' already exists at {new_path.relative_to(foam_root)}",
            file=sys.stderr,
        )
        return False

    # Check for backlinks
    backlinks = find_backlinks(old_stem, foam_root)

    # Show info and confirm unless --force
    if not force:
        print(f"Note to rename: {old_path.relative_to(foam_root)}")
        print(f"New name: {new_path.relative_to(foam_root)}")
        print(f"Notes that will be updated: {len(backlinks)}")

        if backlinks:
            print("\nNotes with wikilinks to update:")
            for bl in backlinks[:10]:
                print(f"  - {bl.relative_to(foam_root)}")
            if len(backlinks) > 10:
                print(f"  ... and {len(backlinks) - 10} more")

        response = input("\nProceed with rename? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            print("Rename cancelled.")
            return False

    # Update wikilinks in other notes
    if backlinks:
        count = update_wikilinks(old_stem, new_stem, foam_root, backlinks)
        print(f"Updated wikilinks in {count} note(s).")

    # Rename the file
    old_path.rename(new_path)
    print(
        f"Renamed: {old_path.relative_to(foam_root)} → {new_path.relative_to(foam_root)}"
    )

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Rename a note and update all wikilinks"
    )
    parser.add_argument("old_name", help="Current note name or filename")
    parser.add_argument("new_name", help="New note name")
    parser.add_argument(
        "--force", "-f", action="store_true", help="Skip confirmation prompt"
    )
    parser.add_argument(
        "--foam-root", help="Foam workspace root directory (overrides config)"
    )

    args = parser.parse_args()

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

    # Rename the note
    success = rename_note(args.old_name, args.new_name, foam_root, args.force)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
