#!/usr/bin/env python3
"""
Generate a summary report of a Foam knowledge graph.

Usage:
    python3 graph_summary.py
    python3 graph_summary.py --orphans --hubs

Examples:
    python3 graph_summary.py --format json
    python3 graph_summary.py --unlinked
"""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from foam_config import load_config, get_foam_root


def extract_wikilinks(content: str) -> set:
    """Extract wikilinks from content."""
    # Pattern: [[note]] or [[note#section]]
    pattern = r"\[\[([^\]#|]+)(?:#[^\]]+)?(?:\|[^\]]+)?\]\]"
    matches = re.findall(pattern, content)
    return set(m.strip() for m in matches)


def extract_title(content: str, filename: str) -> str:
    """Extract title from markdown content."""
    lines = content.split("\n")
    for line in lines[:10]:
        if line.startswith("# "):
            return line[2:].strip()
    return filename.replace(".md", "")


def analyze_graph(foam_root: Path) -> dict:
    """Analyze the knowledge graph."""
    notes = {}
    all_links = Counter()

    for md_file in foam_root.rglob("*.md"):
        # Skip hidden directories
        if any(part.startswith(".") for part in md_file.relative_to(foam_root).parts):
            continue

        try:
            content = md_file.read_text()
            rel_path = str(md_file.relative_to(foam_root))
            filename = md_file.name

            # Extract info
            title = extract_title(content, filename)
            wikilinks = extract_wikilinks(content)

            notes[rel_path] = {
                "title": title,
                "filename": filename,
                "links": list(wikilinks),
                "link_count": len(wikilinks),
            }

            # Count links
            for link in wikilinks:
                all_links[link.lower()] += 1

        except Exception as e:
            print(f"Warning: Could not read {md_file}: {e}", file=sys.stderr)

    # Find orphaned notes (no links to or from)
    orphans = []
    for path, info in notes.items():
        # Check if any other note links to this one
        is_linked = False
        basename = path.replace(".md", "").lower()
        for other_path, other_info in notes.items():
            if other_path == path:
                continue
            for link in other_info["links"]:
                if link.lower() == basename:
                    is_linked = True
                    break
            if is_linked:
                break

        # Orphan = no outgoing links AND no incoming links
        if not info["links"] and not is_linked:
            orphans.append(path)

    # Find placeholder notes (referenced but don't exist)
    existing = set(n.replace(".md", "").lower() for n in notes.keys())
    placeholders = []
    for link, count in all_links.items():
        if link not in existing:
            placeholders.append({"name": link, "references": count})

    # Find hub notes (most linked to)
    hub_scores = Counter()
    for path, info in notes.items():
        basename = path.replace(".md", "").lower()
        for other_path, other_info in notes.items():
            if other_path == path:
                continue
            for link in other_info["links"]:
                if link.lower() == basename:
                    hub_scores[path] += 1

    return {
        "total_notes": len(notes),
        "total_links": sum(info["link_count"] for info in notes.values()),
        "orphans": orphans,
        "placeholders": placeholders,
        "hubs": hub_scores.most_common(20),
        "top_linkers": sorted(
            [(p, i["link_count"]) for p, i in notes.items()], key=lambda x: -x[1]
        )[:20],
        "notes": notes,
    }


def format_markdown(summary: dict) -> str:
    """Format summary as markdown."""
    lines = [
        "# Foam Knowledge Graph Summary",
        "",
        "## Overview",
        f"- Total notes: {summary['total_notes']}",
        f"- Total links: {summary['total_links']}",
        f"- Average links per note: {summary['total_links'] / summary['total_notes']:.1f}"
        if summary["total_notes"] > 0
        else "- Average links per note: 0",
        "",
        "## Hub Notes (Most Referenced)",
        "",
    ]

    if summary["hubs"]:
        for path, count in summary["hubs"][:10]:
            note_name = path.replace(".md", "")
            lines.append(f"- [[{note_name}]] — {count} backlink(s)")
    else:
        lines.append("_No hub notes found_")

    lines.extend(["", "## Most Prolific Linkers", ""])
    if summary["top_linkers"]:
        for path, count in summary["top_linkers"][:10]:
            note_name = path.replace(".md", "")
            lines.append(f"- [[{note_name}]] — {count} outgoing link(s)")
    else:
        lines.append("_No notes with links found_")

    lines.extend(["", "## Orphaned Notes", "_Notes with no connections_", ""])
    if summary["orphans"]:
        for path in summary["orphans"][:20]:
            note_name = path.replace(".md", "")
            lines.append(f"- [[{note_name}]]")
    else:
        lines.append("_No orphan notes found_")

    lines.extend(["", "## Placeholder Notes", "_Referenced but not yet created_", ""])
    if summary["placeholders"]:
        for ph in sorted(summary["placeholders"], key=lambda x: -x["references"])[:20]:
            lines.append(f"- [[{ph['name']}]] — referenced {ph['references']} time(s)")
    else:
        lines.append("_No placeholders found_")

    return "\n".join(lines)


def format_json(summary: dict) -> str:
    """Format summary as JSON."""
    return json.dumps(summary, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Analyze Foam knowledge graph")
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

    summary = analyze_graph(foam_root)

    if args.format == "json":
        print(format_json(summary))
    else:
        print(format_markdown(summary))


if __name__ == "__main__":
    main()
