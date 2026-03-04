#!/usr/bin/env python3
"""
Delete a note from a Foam workspace with optional backup and backlink handling.

Usage:
    python3 delete_note.py <note-name>
    python3 delete_note.py "My Note" --backup
    python3 delete_note.py "My Note" --fix-links --force

Examples:
    python3 delete_note.py "Old Note"                    # Interactive deletion
    python3 delete_note.py "Old Note" --force              # Skip confirmation
    python3 delete_note.py "Old Note" --backup             # Move to .foam/trash/
    python3 delete_note.py "Old Note" --fix-links          # Remove wikilinks from other notes
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from foam_config import load_config, get_foam_root, slugify


def find_note(target: str, foam_root: Path) -> Path:
    """Find a note by name or filename."""
    target_stem = target.replace(".md", "")
    target_slug = slugify(target_stem)

    # Try exact match first
    exact_path = foam_root / f"{target_stem}.md"
    if exact_path.exists():
        return exact_path

    # Try slugified match
    slug_path = foam_root / f"{target_slug}.md"
    if slug_path.exists():
        return slug_path

    # Search all markdown files (case-insensitive and slugified)
    for md_file in foam_root.rglob("*.md"):
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        # Match by original stem or slugified stem
        if md_file.stem.lower() == target_stem.lower():
            return md_file
        if slugify(md_file.stem) == target_slug:
            return md_file

    return None


def find_backlinks(target: str, foam_root: Path) -> list:
    """Find all notes that link to the target note."""
    target_stem = target.replace(".md", "").lower()
    backlinks = []

    # Pattern to match wikilinks to this note
    patterns = [
        rf"\[\[{re.escape(target_stem)}\]\]",
        rf"\[\[{re.escape(target_stem)}#[^\]]+\]\]",
        rf"\[\[{re.escape(target_stem)}\|[^\]]+\]\]",
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


def remove_wikilinks(target: str, foam_root: Path, backlinks: list) -> int:
    """Remove all wikilinks to the target note from other notes."""
    target_stem = target.replace(".md", "").lower()
    removed_count = 0

    # Pattern to match wikilinks with optional section or alias
    pattern = rf"\[\[{re.escape(target_stem)}(?:#[^\]]+)?(?:\|[^\]]+)?\]\]"

    for backlink_file in backlinks:
        try:
            content = backlink_file.read_text()
            original_content = content

            # Remove the wikilinks (keep the surrounding text)
            content = re.sub(
                pattern, target_stem.replace("-", " "), content, flags=re.IGNORECASE
            )

            if content != original_content:
                backlink_file.write_text(content)
                removed_count += 1
        except Exception as e:
            print(f"Warning: Could not update {backlink_file}: {e}", file=sys.stderr)

    return removed_count


def backup_note(note_path: Path, foam_root: Path) -> Path:
    """Move note to .foam/trash/ with timestamp."""
    trash_dir = foam_root / ".foam" / "trash"
    trash_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped filename to avoid collisions
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{note_path.stem}_{timestamp}.md"
    backup_path = trash_dir / backup_name

    shutil.move(str(note_path), str(backup_path))
    return backup_path


def delete_note(
    target: str,
    foam_root: Path,
    backup: bool = False,
    fix_links: bool = False,
    force: bool = False,
) -> bool:
    """Delete a note with optional backup and backlink handling."""

    # Find the note
    note_path = find_note(target, foam_root)
    if note_path is None:
        print(f"Error: Note '{target}' not found.", file=sys.stderr)
        return False

    # Check for backlinks
    backlinks = find_backlinks(note_path.stem, foam_root)

    # Show info and confirm unless --force
    if not force:
        print(f"Note to delete: {note_path.relative_to(foam_root)}")
        print(f"Backlinks found: {len(backlinks)} note(s) link to this note")

        if backlinks:
            print("\nNotes that will be affected:")
            for bl in backlinks[:10]:
                print(f"  - {bl.relative_to(foam_root)}")
            if len(backlinks) > 10:
                print(f"  ... and {len(backlinks) - 10} more")

        print(
            f"\nBackup: {'Yes (.foam/trash/)' if backup else 'No (permanent deletion)'}"
        )
        print(
            f"Fix links: {'Yes (remove wikilinks)' if fix_links else 'No (leave links as-is)'}"
        )

        response = input("\nProceed with deletion? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            print("Deletion cancelled.")
            return False

    # Fix links if requested
    if fix_links and backlinks:
        count = remove_wikilinks(note_path.stem, foam_root, backlinks)
        print(f"Removed wikilinks from {count} note(s).")

    # Delete or backup
    if backup:
        backup_path = backup_note(note_path, foam_root)
        print(f"Backed up to: {backup_path.relative_to(foam_root)}")
    else:
        note_path.unlink()

    print(f"Deleted: {note_path.relative_to(foam_root)}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Delete a note from a Foam workspace")
    parser.add_argument("target", help="Note name or filename to delete")
    parser.add_argument(
        "--backup",
        "-b",
        action="store_true",
        help="Move to .foam/trash/ instead of permanent deletion",
    )
    parser.add_argument(
        "--fix-links",
        "-f",
        action="store_true",
        help="Remove wikilinks from other notes that point to this one",
    )
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
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

    # Delete the note
    success = delete_note(
        args.target, foam_root, args.backup, args.fix_links, args.force
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
