#!/usr/bin/env python3
"""
Quick search script for zotero-cli with formatted output.

Usage:
    python quick_search.py <query> [--limit N] [--format {console,table,json,markdown}]

Examples:
    python quick_search.py "machine learning" --limit 10 --format table
    python quick_search.py "\"deep learning\"" --format json
"""

import argparse
import json
import subprocess
import sys
from typing import List, Dict, Any


def run_zotcli_query(query: str) -> str:
    """Run zotcli query command and return output."""
    try:
        result = subprocess.run(
            ['zotcli', 'query', query],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running zotcli query: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: zotcli not found. Please install zotero-cli first.", file=sys.stderr)
        sys.exit(1)


def parse_zotcli_output(output: str) -> List[Dict[str, Any]]:
    """Parse zotcli query output into structured data."""
    items = []
    lines = output.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # zotcli typically outputs: [ID] Author(s): Title
        if line.startswith('['):
            try:
                # Extract id
                id_end = line.index(']')
                item_id = line[1:id_end]
                rest = line[id_end + 1:].strip()

                # Extract authors and title
                if ':' in rest:
                    authors, title = rest.split(':', 1)
                    items.append({
                        'id': item_id,
                        'authors': authors.strip(),
                        'title': title.strip()
                    })
            except (ValueError, IndexError):
                # Skip malformed lines
                continue

    return items


def format_console(items: List[Dict[str, Any]]) -> str:
    """Format items for console output."""
    output = []
    for item in items:
        output.append(f"[{item['id']}] {item['title']}")
        output.append(f"    Authors: {item['authors']}")
        output.append('')
    return '\n'.join(output)


def format_table(items: List[Dict[str, Any]]) -> str:
    """Format items as a table."""
    if not items:
        return "No items found."

    # Calculate column widths
    max_id = max(len(item['id']) for item in items)
    max_authors = max(len(item['authors']) for item in items)
    max_title = max(len(item['title']) for item in items)

    # Build header
    header = f"{'ID'.ljust(max_id)}  {'Authors'.ljust(max_authors)}  {'Title'.ljust(max_title)}"
    separator = f"{'-' * max_id}  {'-' * max_authors}  {'-' * max_title}"

    # Build rows
    rows = []
    for item in items:
        rows.append(f"{item['id'].ljust(max_id)}  {item['authors'].ljust(max_authors)}  {item['title'].ljust(max_title)}")

    return '\n'.join([header, separator] + rows)


def format_json(items: List[Dict[str, Any]]) -> str:
    """Format items as JSON."""
    return json.dumps(items, indent=2)


def format_markdown(items: List[Dict[str, Any]]) -> str:
    """Format items as Markdown table."""
    if not items:
        return "No items found."

    # Header
    output = ['| ID | Authors | Title |', '|---|---|---|']

    # Rows
    for item in items:
        # Escape pipe characters in markdown
        title = item['title'].replace('|', '\\|')
        authors = item['authors'].replace('|', '\\|')
        output.append(f"| {item['id']} | {authors} | {title} |")

    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Quick search for zotero-cli with formatted output'
    )
    parser.add_argument('query', help='Search query for zotero-cli')
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of results (note: zotcli doesn't support this directly)'
    )
    parser.add_argument(
        '--format',
        choices=['console', 'table', 'json', 'markdown'],
        default='console',
        help='Output format (default: console)'
    )

    args = parser.parse_args()

    # Run query
    output = run_zotcli_query(args.query)

    # Parse output
    items = parse_zotcli_output(output)

    # Apply limit
    if args.limit and len(items) > args.limit:
        items = items[:args.limit]
        print(f"Showing first {args.limit} of {len(items) + (query.count) - args.limit} results\n", file=sys.stderr)

    # Format output
    if args.format == 'console':
        formatted = format_console(items)
    elif args.format == 'table':
        formatted = format_table(items)
    elif args.format == 'json':
        formatted = format_json(items)
    elif args.format == 'markdown':
        formatted = format_markdown(items)
    else:
        formatted = format_console(items)

    print(formatted)


if __name__ == '__main__':
    main()
