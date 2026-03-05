#!/usr/bin/env python3
"""
Search for notes by tag in a Foam workspace.

Usage:
    python3 search_tags.py <tag>
    python3 search_tags.py machine-learning --format json

Examples:
    python3 search_tags.py "#research"
    python3 search_tags.py research --include-frontmatter
"""

import argparse
import json
import re
import sys
from pathlib import Path

from foam_config import load_config, get_foam_root


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}

    try:
        end = content.find("---", 3)
        if end == -1:
            return {}

        import yaml

        fm_content = content[3:end].strip()
        return yaml.safe_load(fm_content) or {}
    except Exception:
        return {}


def find_by_tag(tag: str, foam_root: Path, include_frontmatter: bool = True) -> list:
    """Find all notes with a given tag."""
    # Normalize tag (remove # if present)
    tag = tag.lstrip("#")

    results = []
    tag_pattern = rf"#{re.escape(tag)}(?!\w)"  # Match #tag but not #tagged

    for md_file in foam_root.rglob("*.md"):
        # Skip certain directories
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        try:
            content = md_file.read_text()
            found = False
            match_context = None

            # Check inline tags
            if re.search(tag_pattern, content):
                found = True
                # Get context
                for line in content.split("\n"):
                    if f"#{tag}" in line:
                        match_context = line.strip()
                        break

            # Check frontmatter tags
            if include_frontmatter and not found:
                try:
                    fm = extract_frontmatter(content)
                    fm_tags = fm.get("tags", [])
                    if isinstance(fm_tags, str):
                        fm_tags = [fm_tags]
                    if tag in fm_tags:
                        found = True
                        match_context = f"Frontmatter tags: {fm_tags}"
                except Exception:
                    pass

            if found:
                results.append(
                    {
                        "file": str(md_file.relative_to(foam_root)),
                        "title": extract_title(content) or md_file.stem,
                        "context": match_context,
                    }
                )

        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)

    return results


def extract_title(content: str) -> str:
    """Extract title from markdown content."""
    lines = content.split("\n")
    for line in lines[:10]:
        if line.startswith("# "):
            return line[2:].strip()
    return None


def format_markdown(results: list, tag: str) -> str:
    """Format results as markdown."""
    if not results:
        return f"No notes found with tag '#{tag}'"

    lines = [f"# Notes tagged with #{tag}", ""]
    lines.append(f"Found {len(results)} note(s):")
    lines.append("")

    for result in results:
        note_link = result["file"].replace(".md", "")
        lines.append(f"- [[{note_link}]] — {result['title']}")
        if result["context"]:
            lines.append(f"  - {result['context']}")

    return "\n".join(lines)


def format_json(results: list) -> str:
    """Format results as JSON."""
    return json.dumps(results, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Search for notes by tag")
    parser.add_argument("tag", help="Tag to search for (with or without #)")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--include-frontmatter",
        "-F",
        action="store_true",
        help="Include frontmatter tags in search",
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

    results = find_by_tag(args.tag, foam_root, args.include_frontmatter)

    if args.format == "json":
        print(format_json(results))
    else:
        print(format_markdown(results, args.tag.lstrip("#")))


if __name__ == "__main__":
    main()
