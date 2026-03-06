#!/usr/bin/env python3
"""
Create daily notes in Foam.

Usage:
    python3 daily_note.py
    python3 daily_note.py --template custom-template
    python3 daily_note.py --date 2024-01-15

Examples:
    python3 daily_note.py              # Create/open today's note
    python3 daily_note.py --yesterday   # Create yesterday's note
    python3 daily_note.py --tomorrow    # Create tomorrow's note
    python3 daily_note.py --print-path  # Print path without creating
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from foam_config import load_config, get_foam_root, get_daily_note_folder


def extract_template_content(template_text: str) -> str:
    """
    Extract note content from a template file, stripping template metadata.

    Template files have a foam_template: section that should not appear in
    generated notes. This function removes that section and returns the
    actual content with proper YAML frontmatter.
    """
    lines = template_text.split("\n")

    # Check if this is a template file with foam_template metadata
    if len(lines) >= 3 and lines[0] == "---":
        # Find the end of the foam_template section
        end_idx = -1
        in_foam_template = False

        for i, line in enumerate(lines[1:], start=1):
            if line == "---":
                end_idx = i
                break
            if line.strip().startswith("foam_template:"):
                in_foam_template = True

        # If we found a foam_template section, extract content after it
        if in_foam_template and end_idx > 0:
            content = "\n".join(lines[end_idx + 1 :]).strip()
            return content

    # No foam_template metadata, return as-is
    return template_text


def get_daily_note_path(
    foam_root: Path, date: datetime, daily_folder: str = "journals"
) -> Path:
    """Get the path for a daily note."""
    # Default: journals/yyyy-mm-dd.md or custom folder from config
    journals_dir = foam_root / daily_folder
    if not journals_dir.exists():
        journals_dir = foam_root  # Fallback to root

    filename = date.strftime("%Y-%m-%d") + ".md"
    return journals_dir / filename


def get_default_daily_template(date: datetime) -> str:
    """Return default daily note template."""
    date_str = date.strftime("%Y-%m-%d")
    day_name = date.strftime("%A")

    return f"""# {date_str} - {day_name}

## Tasks

- [ ]

## Notes

## Journal

"""


def create_daily_note(
    filepath: Path, date: datetime, template: str = None, foam_root: Path = None
):
    """Create a daily note if it doesn't exist."""
    if filepath.exists():
        return False

    # Try to load custom template
    if template and foam_root:
        template_path = foam_root / ".foam" / "templates" / f"{template}.md"
        if template_path.exists():
            content = template_path.read_text()
            # Replace variables
            content = content.replace("$FOAM_DATE_YEAR", date.strftime("%Y"))
            content = content.replace("$FOAM_DATE_MONTH", date.strftime("%m"))
            content = content.replace("$FOAM_DATE_DATE", date.strftime("%d"))
            content = content.replace("$FOAM_DATE_DAY_NAME", date.strftime("%A"))
            content = content.replace("$FOAM_DATE_DAY_NAME_SHORT", date.strftime("%a"))
        else:
            print(
                f"Warning: Template '{template}' not found. Using default.",
                file=sys.stderr,
            )
            content = get_default_daily_template(date)
    else:
        # No template specified - check for default daily template first
        default_template_path = foam_root / ".foam" / "templates" / "daily-note.md"
        if default_template_path.exists():
            raw_content = default_template_path.read_text()
            # Extract actual content (strip template metadata)
            content = extract_template_content(raw_content)
            # Replace variables
            content = content.replace("$FOAM_DATE_YEAR", date.strftime("%Y"))
            content = content.replace("${FOAM_DATE_YEAR}", date.strftime("%Y"))
            content = content.replace("$FOAM_DATE_MONTH", date.strftime("%m"))
            content = content.replace("${FOAM_DATE_MONTH}", date.strftime("%m"))
            content = content.replace("$FOAM_DATE_DATE", date.strftime("%d"))
            content = content.replace("${FOAM_DATE_DATE}", date.strftime("%d"))
            content = content.replace("$FOAM_DATE_DAY_NAME", date.strftime("%A"))
            content = content.replace("$FOAM_DATE_DAY_NAME_SHORT", date.strftime("%a"))
        else:
            # Fall back to hardcoded default
            content = get_default_daily_template(date)

    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    filepath.write_text(content)
    return True


def main():
    parser = argparse.ArgumentParser(description="Create daily notes")
    parser.add_argument("--date", "-d", help="Specific date (YYYY-MM-DD)")
    parser.add_argument(
        "--template", "-t", help="Template name (from .foam/templates/)"
    )
    parser.add_argument(
        "--yesterday", "-y", action="store_true", help="Create yesterday's note"
    )
    parser.add_argument(
        "--tomorrow", "-T", action="store_true", help="Create tomorrow's note"
    )
    parser.add_argument(
        "--print-path", "-p", action="store_true", help="Print path and exit"
    )
    parser.add_argument(
        "--foam-root", help="Foam workspace root directory (overrides config)"
    )

    args = parser.parse_args()

    config = load_config()

    # Get foam root with priority: CLI arg > config > auto-detect
    if args.foam_root:
        foam_root = Path(args.foam_root).expanduser().resolve()
    else:
        foam_root = get_foam_root(config=config)

    if foam_root is None:
        print("Error: Not in a Foam workspace.", file=sys.stderr)
        print("Set foam_root in config.json or use --foam-root", file=sys.stderr)
        sys.exit(1)

    # Determine date
    if args.yesterday:
        date = datetime.now() - timedelta(days=1)
    elif args.tomorrow:
        date = datetime.now() + timedelta(days=1)
    elif args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("Error: Date must be in YYYY-MM-DD format", file=sys.stderr)
            sys.exit(1)
    else:
        date = datetime.now()

    # Get daily note folder from config
    daily_folder = get_daily_note_folder(config)

    # Get filepath
    filepath = get_daily_note_path(foam_root, date, daily_folder)

    # Print path and exit if requested
    if args.print_path:
        print(filepath)
        return

    # Create if needed
    created = create_daily_note(filepath, date, args.template, foam_root)

    if created:
        print(f"Created: {filepath.relative_to(foam_root)}")
    elif filepath.exists():
        print(f"Exists: {filepath.relative_to(foam_root)}")
    else:
        print(
            f"Error: Could not create {filepath.relative_to(foam_root)}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
