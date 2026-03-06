#!/usr/bin/env python3
"""
List all tags in a Foam workspace.

Usage:
    python3 list_tags.py
    python3 list_tags.py --format json --sorted

Examples:
    python3 list_tags.py --min-count 3
    python3 list_tags.py --include-frontmatter --hierarchy
"""

import argparse
import json
import re
import sys
from collections import Counter
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


def extract_inline_tags(content: str) -> set:
    """Extract inline tags from content."""
    # Pattern: #tag (not in code blocks, not part of URL)
    tags = set()

    # Remove code blocks first
    lines = content.split("\n")
    in_code_block = False
    clean_lines = []

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            clean_lines.append(line)

    clean_content = "\n".join(clean_lines)

    # Find tags
    pattern = r"#([a-zA-Z][\w/-]*)"
    for match in re.finditer(pattern, clean_content):
        tag = match.group(1)
        # Filter out hex colors and URLs
        if not re.match(r"^[0-9a-fA-F]{6}$", tag):
            tags.add(tag.lower())

    return tags


def extract_fm_tags(content: str) -> set:
    """Extract frontmatter tags."""
    try:
        fm = extract_frontmatter(content)
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            return {tags.lower()}
        return {t.lower() for t in tags}
    except Exception:
        return set()


def analyze_tags(foam_root: Path, include_frontmatter: bool = True) -> dict:
    """Analyze all tags in the workspace."""
    all_inline_tags = Counter()
    all_fm_tags = Counter()
    tag_files = {}

    for md_file in foam_root.rglob("*.md"):
        # Skip hidden directories
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        try:
            content = md_file.read_text()
            rel_path = str(md_file.relative_to(foam_root))

            # Inline tags
            inline = extract_inline_tags(content)
            for tag in inline:
                all_inline_tags[tag] += 1
                if tag not in tag_files:
                    tag_files[tag] = []
                tag_files[tag].append(rel_path)

            # Frontmatter tags
            if include_frontmatter:
                fm = extract_fm_tags(content)
                for tag in fm:
                    all_fm_tags[tag] += 1
                    if tag not in tag_files:
                        tag_files[tag] = []
                    if rel_path not in tag_files[tag]:
                        tag_files[tag].append(rel_path)

        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)

    return {
        "inline": dict(all_inline_tags),
        "frontmatter": dict(all_fm_tags) if include_frontmatter else {},
        "files": tag_files,
        "total": dict(all_inline_tags + all_fm_tags),
    }


def build_hierarchy(tags: list) -> dict:
    """Build hierarchical tag structure."""
    hierarchy = {}

    for tag in tags:
        parts = tag.split("/")
        current = hierarchy
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]

    return hierarchy


def format_hierarchy(hierarchy: dict, indent: int = 0) -> str:
    """Format hierarchy as indented text."""
    lines = []
    for key in sorted(hierarchy.keys()):
        lines.append("  " * indent + f"- {key}")
        if hierarchy[key]:
            lines.append(format_hierarchy(hierarchy[key], indent + 1))
    return "\n".join(lines)


def format_markdown(results: dict, args) -> str:
    """Format results as markdown."""
    lines = ["# Tag Analysis", ""]

    # Summary
    total_inline = sum(results["inline"].values())
    total_fm = sum(results["frontmatter"].values())
    unique_tags = len(results["total"])

    lines.append(f"## Summary")
    lines.append(f"- Unique tags: {unique_tags}")
    lines.append(f"- Inline tag instances: {total_inline}")
    if args.include_frontmatter:
        lines.append(f"- Frontmatter tag instances: {total_fm}")
    lines.append("")

    # Filter by min-count
    tags = [(tag, count) for tag, count in results["total"].items()]
    if args.min_count:
        tags = [(t, c) for t, c in tags if c >= args.min_count]

    # Sort
    if args.sorted:
        tags = sorted(tags, key=lambda x: (-x[1], x[0]))
    else:
        tags = sorted(tags, key=lambda x: x[0])

    # Display
    if args.hierarchy:
        lines.append("## Tag Hierarchy")
        hierarchy = build_hierarchy([t for t, _ in tags])
        lines.append(format_hierarchy(hierarchy))
    else:
        lines.append("## All Tags")
        lines.append("")
        for tag, count in tags:
            lines.append(f"- **{tag}** — {count} occurrence(s)")

    return "\n".join(lines)


def format_json(results: dict) -> str:
    """Format results as JSON."""
    return json.dumps(results, indent=2)


def main():
    parser = argparse.ArgumentParser(description="List all tags in Foam workspace")
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
        default=True,
        help="Include frontmatter tags",
    )
    parser.add_argument("--min-count", "-m", type=int, help="Minimum count to include")
    parser.add_argument(
        "--sorted", "-s", action="store_true", help="Sort by count (descending)"
    )
    parser.add_argument(
        "--hierarchy", action="store_true", help="Show hierarchical structure"
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

    results = analyze_tags(foam_root, args.include_frontmatter)

    if args.format == "json":
        print(format_json(results))
    else:
        print(format_markdown(results, args))


if __name__ == "__main__":
    main()
