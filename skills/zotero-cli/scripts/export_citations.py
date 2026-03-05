#!/usr/bin/env python3
"""
Export citations from Zotero using zotero-cli.

Usage:
    python export_citations.py <query> --format {bib,ris,txt}

Examples:
    python export_citations.py "machine learning" --format bib > refs.bib
    python export_citations.py "\"deep learning\"" --format txt > refs.txt
"""

import argparse
import subprocess
import sys
import re
from typing import List


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


def parse_zotcli_output(output: str) -> List[dict]:
    """Parse zotcli query output into structured data."""
    items = []
    lines = output.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or not line.startswith('['):
            continue

        try:
            id_end = line.index(']')
            item_id = line[1:id_end]
            rest = line[id_end + 1:].strip()

            if ':' in rest:
                authors, title = rest.split(':', 1)
                # Generate simple BibTeX key from title
                bibtex_key = generate_bibtex_key(title.strip(), authors.strip())

                items.append({
                    'id': item_id,
                    'authors': authors.strip(),
                    'title': title.strip(),
                    'bibtex_key': bibtex_key
                })
        except (ValueError, IndexError):
            continue

    return items


def generate_bibtex_key(title: str, authors: str) -> str:
    """Generate a simple BibTeX key from title and authors."""
    # Extract first author's surname
    if authors:
        first_author = authors.split(',')[0].strip()..split()[-1].lower()
    else:
        first_author = 'unknown'

    # Extract first word from title, remove punctuation
    title_words = re.findall(r'\b[a-zA-Z]+\b', title)
    second_word = title_words[0].lower() if title_words else 'unknown'

    # Combine to create key
    return f"{first_author}{second_word}_{hash(title[:20]) % 1000}"


def format_bibtex(items: List[dict]) -> str:
    """Format items as BibTeX entries."""
    output = []
    for item in items:
        entry = f"""@{{{''}article}}}{item['bibtex_key']},{{{''}'}}
  title = {{{"{item['title']}"}}},
  author = {{{"{item['authors']}"}}},
}
"""
        output.append(entry)
    return '\n'.join(output)


def format_ris(items: List[dict]) -> str:
    """Format items as RIS entries."""
    output = []
    for item in items:
        entry = f"""TY  - JOUR
TI  - {item['title']}
AU  - {item['authors']}
ID  - {item['id']}
ER  -
"""
        output.append(entry)
    return '\n'.join(output)


def format_txt(items: List[dict]) -> str:
    """Format items as plain text."""
    output = []
    for i, item in enumerate(items, 1):
        output.append(f"{i}. [{item['id']}] {item['authors']}: {item['title']}")
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Export citations from Zotero using zotero-cli'
    )
    parser.add_argument('query', help='Search query for zotero-cli')
    parser.add_argument(
        '--format',
        choices=['bib', 'ris', 'txt'],
        default='txt',
        help='Output format (default: txt)'
    )

    args = parser.parse_args()

    # Run query
    output = run_zotcli_query(args.query)

    # Parse output
    items = parse_zotcli_output(output)

    if not items:
        print("No items found.", file=sys.stderr)
        sys.exit(0)

    # Format output
    if args.format == 'bib':
        formatted = format_bibtex(items)
    elif args.format == 'ris':
        formatted = format_ris(items)
    else:  # txt
        formatted = format_txt(items)

    print(formatted)


if __name__ == '__main__':
    main()
