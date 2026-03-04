#!/usr/bin/env python3
"""
Find all notes that link to a given note (backlinks).

Usage:
    python3 find_backlinks.py <note-name>
    python3 find_backlinks.py "My Note" --format json

Examples:
    python3 find_backlinks.py "Machine Learning"
    python3 find_backlinks.py ml-basics --format markdown
"""

import argparse
import json
import re
import sys
from pathlib import Path

from foam_config import load_config, get_foam_root


def find_backlinks(target: str, foam_root: Path) -> list:
    """Find all notes that link to the target note."""
    target = target.replace(".md", "")  # Remove extension if present

    # Wikilink patterns to match
    patterns = [
        rf"\[\[{re.escape(target)}\]\]",  # [[Target]]
        rf"\[\[{re.escape(target)}#[^\]]+\]\]",  # [[Target#Section]]
        rf"\[([^\]]+)\]\({re.escape(target)}\.md\)",  # [text](Target.md)
    ]

    backlinks = []

    # Scan all markdown files
    for md_file in foam_root.rglob("*.md"):
        # Skip certain directories
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        try:
            content = md_file.read_text()
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    backlinks.append(
                        {
                            "file": str(md_file.relative_to(foam_root)),
                            "title": extract_title(content) or md_file.stem,
                        }
                    )
                    break
        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)

    return backlinks


def extract_title(content: str) -> str:
    """Extract title from markdown content."""
    lines = content.split("\n")
    for line in lines[:10]:  # Check first 10 lines
        if line.startswith("# "):
            return line[2:].strip()
    return None


def format_markdown(backlinks: list, target: str) -> str:
    """Format backlinks as markdown list."""
    if not backlinks:
        return f"No backlinks found for '[[{target}]]'"

    lines = [f"# Backlinks to [[{target}]]", ""]
    lines.append(f"Found {len(backlinks)} note(s) that link to this:")
    lines.append("")

    for link in backlinks:
        lines.append(f"- [[{link['file'].replace('.md', '')}]] — {link['title']}")

    return "\n".join(lines)


def format_json(backlinks: list) -> str:
    """Format backlinks as JSON."""
    return json.dumps(backlinks, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Find backlinks to a note")
    parser.add_argument("target", help="Target note name (without .md)")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--foam-root", help="Foam workspace root directory (overrides config)"
    )

    args = parser.parse_args()

    config = load_config()

    if args.foam_root:
        foam_root = Path(args.foam_root).expanduser().resolve()
    else:
        foam_root = get_foam_root(config=config)

    if foam_root is None:
        print("Error: Not in a Foam workspace.", file=sys.stderr)
        print("Set foam_root in config.json or use --foam-root", file=sys.stderr)
        sys.exit(1)

    backlinks = find_backlinks(args.target, foam_root)

    if args.format == "json":
        print(format_json(backlinks))
    else:
        print(format_markdown(backlinks, args.target))


if __name__ == "__main__":
    main()
