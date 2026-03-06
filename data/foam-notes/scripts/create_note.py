#!/usr/bin/env python3
"""
Create a new Foam note from a template.

Usage:
    python3 create_note.py <title> [--template TEMPLATE] [--dir DIRECTORY]

Examples:
    python3 create_note.py "My New Idea"
    python3 create_note.py "Meeting Notes" --template meeting
    python3 create_note.py "Research Topic" --dir research/
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from foam_config import (
    load_config,
    get_foam_root,
    get_default_template,
    get_default_notes_folder,
    slugify,
)


def get_default_template_content() -> str:
    """Return default note template content with Foam-compliant YAML frontmatter."""
    return """---
title: {title}
date: {date}
tags: []
---

# {title}

"""


def get_daily_template() -> str:
    """Return daily note template with Foam-compliant YAML frontmatter."""
    return """---
title: Daily Note - {date}
date: {date}
tags: [daily]
---

# {date}

## Tasks

- [ ]

## Notes

"""


def extract_template_content(template_text: str) -> str:
    """
    Extract note content from a template file, stripping only foam_template metadata.

    Template files have a foam_template: section that should not appear in
    generated notes, but all other frontmatter should be preserved.
    This function removes only the foam_template section and keeps the rest.
    """
    lines = template_text.split("\n")

    # Check if this is a template file with frontmatter
    if len(lines) >= 3 and lines[0] == "---":
        # Find the end of the frontmatter section
        end_idx = -1
        has_foam_template = False

        for i, line in enumerate(lines[1:], start=1):
            if line == "---":
                end_idx = i
                break
            if line.strip().startswith("foam_template:"):
                has_foam_template = True

        # If we found foam_template in the frontmatter, rebuild without it
        if has_foam_template and end_idx > 0:
            # Extract the frontmatter lines (excluding --- markers)
            frontmatter_lines = lines[1:end_idx]
            # Filter out foam_template and its nested content
            filtered_frontmatter = []
            in_foam_template = False

            for line in frontmatter_lines:
                if line.strip().startswith("foam_template:"):
                    in_foam_template = True
                    continue
                if in_foam_template:
                    # Check if this line is still part of foam_template (indented)
                    if (
                        line.strip()
                        and not line.startswith(" ")
                        and not line.startswith("\t")
                    ):
                        # This is a new top-level key, not part of foam_template
                        in_foam_template = False
                        filtered_frontmatter.append(line)
                    # Otherwise skip (it's part of foam_template)
                    continue
                filtered_frontmatter.append(line)

            # Get the content after frontmatter
            content_lines = lines[end_idx + 1 :]
            content = "\n".join(content_lines).strip()

            # Rebuild the note with filtered frontmatter
            if filtered_frontmatter:
                result = (
                    "---\n" + "\n".join(filtered_frontmatter) + "\n---\n\n" + content
                )
            else:
                result = content
            return result

    # No foam_template metadata or no frontmatter, return as-is
    return template_text


def add_frontmatter_if_missing(content: str, title: str, date_str: str) -> str:
    """
    Add Foam-compliant YAML frontmatter if the content doesn't already have it.

    Args:
        content: The note content
        title: The note title
        date_str: The date string

    Returns:
        Content with proper frontmatter
    """
    # Check if content already has frontmatter
    if content.strip().startswith("---"):
        return content

    # Add frontmatter
    frontmatter = f"""---
title: {title}
date: {date_str}
tags: []
---

"""
    return frontmatter + content


def create_note(
    title: str,
    template: str = None,
    output_dir: Path = None,
    foam_root: Path = None,
    config: dict = None,
):
    """Create a new Foam note."""
    if config is None:
        config = load_config()

    if foam_root is None:
        foam_root = get_foam_root(config=config)

    if foam_root is None:
        print(
            "Error: Not in a Foam workspace. Could not find .foam directory.",
            file=sys.stderr,
        )
        print("Set foam_root in config.json or use --foam-root", file=sys.stderr)
        sys.exit(1)

    # Determine output directory
    if output_dir is None:
        output_dir = foam_root
    elif not output_dir.is_absolute():
        output_dir = foam_root / output_dir

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    slug = slugify(title)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{slug}.md"
    filepath = output_dir / filename

    # Check for existing file
    counter = 1
    original_filepath = filepath
    while filepath.exists():
        filename = f"{slug}-{counter}.md"
        filepath = output_dir / filename
        counter += 1

    # Prepare template content
    if template == "daily":
        content = get_daily_template().format(date=date_str, title=title)
    elif template:
        # Try to load custom template
        template_path = foam_root / ".foam" / "templates" / f"{template}.md"
        if template_path.exists():
            raw_content = template_path.read_text()
            # Extract actual content (strip template metadata)
            content = extract_template_content(raw_content)
            # Replace variables
            content = content.replace("$FOAM_TITLE", title)
            content = content.replace("${FOAM_TITLE}", title)
            content = content.replace("$FOAM_SLUG", slug)
            content = content.replace("$FOAM_DATE_YEAR", datetime.now().strftime("%Y"))
            content = content.replace(
                "${FOAM_DATE_YEAR}", datetime.now().strftime("%Y")
            )
            content = content.replace("$FOAM_DATE_MONTH", datetime.now().strftime("%m"))
            content = content.replace(
                "${FOAM_DATE_MONTH}", datetime.now().strftime("%m")
            )
            content = content.replace("$FOAM_DATE_DATE", datetime.now().strftime("%d"))
            content = content.replace(
                "${FOAM_DATE_DATE}", datetime.now().strftime("%d")
            )
            # Replace time variables
            now = datetime.now()
            content = content.replace("$CURRENT_HOUR", now.strftime("%H"))
            content = content.replace("$CURRENT_MINUTE", now.strftime("%M"))
            content = content.replace("$CURRENT_SECOND", now.strftime("%S"))
            # Handle shell-style variables like $1, $2, etc. - replace with empty
            content = re.sub(r"\$\d+", "", content)
            # Ensure proper frontmatter
            content = add_frontmatter_if_missing(content, title, date_str)
        else:
            print(
                f"Warning: Template '{template}' not found. Using default.",
                file=sys.stderr,
            )
            content = get_default_template_content().format(title=title, date=date_str)
    else:
        # No template specified - check for default template first
        default_template_path = foam_root / ".foam" / "templates" / "new-note.md"
        if default_template_path.exists():
            raw_content = default_template_path.read_text()
            # Extract actual content (strip template metadata)
            content = extract_template_content(raw_content)
            # Replace variables
            content = content.replace("$FOAM_TITLE", title)
            content = content.replace("${FOAM_TITLE}", title)
            content = content.replace("$FOAM_SLUG", slug)
            content = content.replace("$FOAM_DATE_YEAR", datetime.now().strftime("%Y"))
            content = content.replace(
                "${FOAM_DATE_YEAR}", datetime.now().strftime("%Y")
            )
            content = content.replace("$FOAM_DATE_MONTH", datetime.now().strftime("%m"))
            content = content.replace(
                "${FOAM_DATE_MONTH}", datetime.now().strftime("%m")
            )
            content = content.replace("$FOAM_DATE_DATE", datetime.now().strftime("%d"))
            content = content.replace(
                "${FOAM_DATE_DATE}", datetime.now().strftime("%d")
            )
            # Replace time variables
            now = datetime.now()
            content = content.replace("$CURRENT_HOUR", now.strftime("%H"))
            content = content.replace("$CURRENT_MINUTE", now.strftime("%M"))
            content = content.replace("$CURRENT_SECOND", now.strftime("%S"))
            # Handle shell-style variables like $1, $2, etc. - replace with empty
            content = re.sub(r"\$\d+", "", content)
            # Ensure proper frontmatter
            content = add_frontmatter_if_missing(content, title, date_str)
        else:
            # Fall back to hardcoded default
            content = get_default_template_content().format(title=title, date=date_str)

    # Write the file
    filepath.write_text(content)
    print(f"Created: {filepath.relative_to(foam_root)}")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Create a new Foam note")
    parser.add_argument("title", help="Note title")
    parser.add_argument(
        "--template", "-t", help="Template name (from .foam/templates/)"
    )
    parser.add_argument("--dir", "-d", help="Output directory (relative to Foam root)")
    parser.add_argument(
        "--foam-root", help="Foam workspace root directory (overrides config)"
    )

    args = parser.parse_args()

    config = load_config()

    # Get foam root with priority: CLI arg > config > auto-detect
    foam_root = None
    if args.foam_root:
        foam_root = Path(args.foam_root).expanduser().resolve()
    else:
        foam_root = get_foam_root(config=config)

    # Use default template from config if not specified
    template = args.template
    if not template:
        template = get_default_template(config)

    # Use default notes folder from config if --dir not specified
    output_dir = None
    if args.dir:
        output_dir = Path(args.dir)
    else:
        notes_folder = get_default_notes_folder(config)
        if notes_folder:
            output_dir = Path(notes_folder)

    create_note(args.title, template, output_dir, foam_root, config)


if __name__ == "__main__":
    main()
