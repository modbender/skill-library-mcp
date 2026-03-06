#!/usr/bin/env python3
"""
Search competitor documentation files for relevant articles.

Document format:
- Articles are separated by: blank line, "---", blank line
- Each article starts with an H1 title (# Title)
- Source URL is on a line starting with "*Source:" or "Source:"

Usage:
    search_docs.py <docs_dir> <query> [--mode keyword|regex] [--max-results N] [--context-lines N]

Examples:
    search_docs.py ./docs "kubernetes backup" --mode keyword --max-results 10
    search_docs.py ./docs "AWS.*S3" --mode regex --max-results 5
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Article:
    """Represents a single documentation article."""
    title: str
    source_url: str
    content: str
    file_path: str
    start_line: int


def parse_articles(file_path: str) -> List[Article]:
    """Parse a documentation file into individual articles."""
    articles = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by article delimiter: blank line, ---, blank line
    # Pattern matches: \n\n---\n\n or variations with whitespace
    article_delimiter = r'\n\s*\n---\s*\n'
    raw_articles = re.split(article_delimiter, content)
    
    # Track line numbers for context
    current_line = 1
    
    for raw_article in raw_articles:
        if not raw_article.strip():
            continue
        
        # Extract title (first H1)
        title_match = re.search(r'^#\s+(.+)$', raw_article, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        
        # Extract source URL
        source_match = re.search(r'\*?Source:\s*(\S+)', raw_article)
        source_url = source_match.group(1) if source_match else "Unknown"
        
        article = Article(
            title=title,
            source_url=source_url,
            content=raw_article.strip(),
            file_path=file_path,
            start_line=current_line
        )
        articles.append(article)
        
        # Update line counter
        current_line += raw_article.count('\n') + 3  # +3 for the delimiter
    
    return articles


def keyword_search(query: str, text: str) -> List[Tuple[int, str]]:
    """Search for keyword matches, returning matching lines with context."""
    query_lower = query.lower()
    text_lower = text.lower()
    lines = text.split('\n')
    
    matches = []
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            matches.append((i + 1, line.strip()))
    
    return matches


def regex_search(pattern: str, text: str) -> List[Tuple[int, str]]:
    """Search for regex matches, returning matching lines."""
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        print(f"Invalid regex pattern: {e}", file=sys.stderr)
        return []
    
    lines = text.split('\n')
    matches = []
    
    for i, line in enumerate(lines):
        if regex.search(line):
            matches.append((i + 1, line.strip()))
    
    return matches


def get_context(content: str, match_line: int, context_lines: int) -> str:
    """Extract context around a matching line."""
    lines = content.split('\n')
    start = max(0, match_line - context_lines - 1)
    end = min(len(lines), match_line + context_lines)
    
    context = []
    for i in range(start, end):
        prefix = ">>> " if i == match_line - 1 else "    "
        context.append(f"{prefix}{lines[i]}")
    
    return '\n'.join(context)


def search_docs(
    docs_dir: str,
    query: str,
    mode: str = "keyword",
    max_results: int = 10,
    context_lines: int = 3
) -> List[dict]:
    """
    Search documentation directory for matching articles.
    
    Returns a list of result dictionaries with article info and matches.
    """
    results = []
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"Error: Documentation directory not found: {docs_dir}", file=sys.stderr)
        return results
    
    # Find all markdown files
    md_files = list(docs_path.rglob("*.md"))
    
    if not md_files:
        print(f"Warning: No markdown files found in {docs_dir}", file=sys.stderr)
        return results
    
    search_fn = keyword_search if mode == "keyword" else regex_search
    
    for md_file in md_files:
        articles = parse_articles(str(md_file))
        
        for article in articles:
            matches = search_fn(query, article.content)
            
            if matches:
                # Get context for first few matches
                match_contexts = []
                for line_num, matched_text in matches[:3]:  # Limit to first 3 matches per article
                    ctx = get_context(article.content, line_num, context_lines)
                    match_contexts.append({
                        "line": line_num,
                        "matched_text": matched_text[:200],  # Truncate long matches
                        "context": ctx
                    })
                
                results.append({
                    "title": article.title,
                    "source_url": article.source_url,
                    "file": str(md_file),
                    "total_matches": len(matches),
                    "matches": match_contexts,
                    "full_content": article.content
                })
    
    # Sort by number of matches (descending)
    results.sort(key=lambda x: x["total_matches"], reverse=True)
    
    # Limit results
    return results[:max_results]


def format_output(results: List[dict], show_full: bool = False) -> str:
    """Format search results for display."""
    output = []
    
    for i, result in enumerate(results, 1):
        output.append(f"\n{'='*80}")
        output.append(f"Result {i}: {result['title']}")
        output.append(f"Source: {result['source_url']}")
        output.append(f"File: {result['file']}")
        output.append(f"Matches: {result['total_matches']}")
        output.append("-" * 80)
        
        if show_full:
            output.append(result['full_content'])
        else:
            for match in result['matches']:
                output.append(f"\nLine {match['line']}:")
                output.append(match['context'])
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search competitor documentation files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("docs_dir", help="Path to documentation directory")
    parser.add_argument("query", help="Search query (keyword or regex pattern)")
    parser.add_argument("--mode", choices=["keyword", "regex"], default="keyword",
                        help="Search mode: keyword (default) or regex")
    parser.add_argument("--max-results", type=int, default=10,
                        help="Maximum number of articles to return (default: 10)")
    parser.add_argument("--context-lines", type=int, default=3,
                        help="Lines of context around matches (default: 3)")
    parser.add_argument("--full", action="store_true",
                        help="Show full article content instead of context snippets")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON for programmatic use")
    
    args = parser.parse_args()
    
    results = search_docs(
        args.docs_dir,
        args.query,
        args.mode,
        args.max_results,
        args.context_lines
    )
    
    if not results:
        print("No matches found.")
        return
    
    if args.json:
        import json
        # Don't include full_content in JSON by default (too large)
        for r in results:
            if not args.full:
                r.pop('full_content', None)
        print(json.dumps(results, indent=2))
    else:
        print(format_output(results, show_full=args.full))


if __name__ == "__main__":
    main()