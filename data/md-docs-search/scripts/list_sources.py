#!/usr/bin/env python3
"""
List documentation sources in a directory.

Shows all unique source URLs found in documentation files, useful for
discovering what documentation is available.

Usage:
    list_sources.py <docs_dir> [--filter <pattern>]

Examples:
    list_sources.py ./docs
    list_sources.py ./docs --filter "kubernetes"
"""

import argparse
import re
import sys
from pathlib import Path
from collections import Counter
from urllib.parse import urlparse


def extract_sources(docs_dir: str, filter_pattern: str = None) -> Counter:
    """Extract all unique source URLs from documentation."""
    docs_path = Path(docs_dir)
    sources = Counter()
    
    if not docs_path.exists():
        print(f"Error: Directory not found: {docs_dir}", file=sys.stderr)
        return sources
    
    md_files = list(docs_path.rglob("*.md"))
    
    if not md_files:
        print(f"Warning: No markdown files found in {docs_dir}", file=sys.stderr)
        return sources
    
    source_pattern = re.compile(r'\*?Source:\s*(\S+)')
    
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for match in source_pattern.finditer(content):
            url = match.group(1)
            if filter_pattern:
                if filter_pattern.lower() in url.lower():
                    sources[url] += 1
            else:
                sources[url] += 1
    
    return sources


def categorize_sources(sources: Counter) -> dict:
    """Group sources by domain."""
    categories = {}
    
    for url, count in sources.items():
        parsed = urlparse(url)
        domain = parsed.netloc or "unknown"
        
        if domain not in categories:
            categories[domain] = []
        
        categories[domain].append((url, count))
    
    return categories


def main():
    parser = argparse.ArgumentParser(description="List documentation sources")
    parser.add_argument("docs_dir", help="Path to documentation directory")
    parser.add_argument("--filter", dest="filter_pattern",
                        help="Filter sources containing this pattern")
    parser.add_argument("--by-domain", action="store_true",
                        help="Group sources by domain")
    parser.add_argument("--stats", action="store_true",
                        help="Show statistics only")
    
    args = parser.parse_args()
    
    sources = extract_sources(args.docs_dir, args.filter_pattern)
    
    if not sources:
        print("No sources found.")
        return
    
    if args.stats:
        print(f"Total unique sources: {len(sources)}")
        print(f"Total references: {sum(sources.values())}")
        print(f"\nTop 10 most referenced:")
        for url, count in sources.most_common(10):
            print(f"  {count:3d}x {url}")
        return
    
    if args.by_domain:
        categories = categorize_sources(sources)
        for domain, urls in sorted(categories.items()):
            print(f"\n[{domain}] ({len(urls)} sources)")
            for url, count in sorted(urls, key=lambda x: x[1], reverse=True)[:20]:
                print(f"  {count:3d}x {url}")
    else:
        for url, count in sources.most_common():
            print(f"{count:3d}x {url}")


if __name__ == "__main__":
    main()