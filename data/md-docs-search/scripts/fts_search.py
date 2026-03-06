#!/usr/bin/env python3
"""
Full-text search across indexed competitor documentation.

Uses SQLite FTS5 for fast, ranked search with BM25 relevance scoring.
Supports boolean operators, phrase queries, and column-specific searches.

Usage:
    fts_search.py <db_path> <query> [options]

Examples:
    fts_search.py competitor.db "kubernetes backup"
    fts_search.py competitor.db "AWS AND S3" --max 5
    fts_search.py competitor.db '"exact phrase"' --title-only
    fts_search.py competitor.db "postgres*" --format json
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from typing import List, Optional


def search_docs(
    db_path: str,
    query: str,
    max_results: int = 10,
    title_only: bool = False,
    format_output: str = "text",
    context_chars: int = 200
) -> List[dict]:
    """
    Perform full-text search on indexed documentation.
    
    Returns list of results with relevance scores.
    """
    if not sqlite3.connect(db_path):
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # FTS5 query syntax:
    # - Simple terms: "kubernetes backup"
    # - Boolean: "kubernetes AND backup"
    # - Phrase: '"exact phrase"'
    # - Prefix: "kube*"
    # - NOT: "kubernetes NOT docker"
    # - Column-specific: "title:kubernetes"
    
    if title_only:
        # Search only in titles
        fts_query = f"title:{query}"
    else:
        fts_query = query
    
    # Use BM25 for relevance ranking (lower = more relevant)
    sql = '''
        SELECT 
            title,
            source_url,
            content,
            file_path,
            bm25(articles) as relevance
        FROM articles
        WHERE articles MATCH ?
        ORDER BY bm25(articles)
        LIMIT ?
    '''
    
    try:
        cursor.execute(sql, (fts_query, max_results))
        rows = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"Search error: {e}", file=sys.stderr)
        print("Tip: Use FTS5 syntax: 'term1 AND term2', '\"phrase\"', 'prefix*'", file=sys.stderr)
        conn.close()
        return []
    
    results = []
    for row in rows:
        title, source_url, content, file_path, relevance = row
        
        # Extract context around first match
        context = extract_context(content, query, context_chars)
        
        results.append({
            "title": title,
            "source_url": source_url,
            "content": content,
            "context": context,
            "file_path": file_path,
            "relevance": round(relevance, 2),
            "content_length": len(content)
        })
    
    conn.close()
    return results


def extract_context(content: str, query: str, max_chars: int) -> str:
    """Extract context snippet around the first query match."""
    # Find first occurrence of any query term
    terms = query.lower().replace('"', '').replace('*', '').replace('AND', '').replace('OR', '').replace('NOT', '').split()
    
    content_lower = content.lower()
    first_match = len(content)  # Default to start
    
    for term in terms:
        term = term.strip()
        if term:
            pos = content_lower.find(term)
            if pos != -1 and pos < first_match:
                first_match = pos
    
    # Extract context around match
    start = max(0, first_match - max_chars // 2)
    end = min(len(content), first_match + max_chars // 2)
    
    context = content[start:end]
    
    # Add ellipsis
    if start > 0:
        context = "..." + context
    if end < len(content):
        context = context + "..."
    
    return context


def format_text(results: List[dict]) -> str:
    """Format results as human-readable text."""
    if not results:
        return "No results found."
    
    output = []
    for i, result in enumerate(results, 1):
        output.append(f"\n{'='*80}")
        output.append(f"Result {i} (relevance: {result['relevance']})")
        output.append(f"Title: {result['title']}")
        output.append(f"Source: {result['source_url']}")
        output.append(f"File: {result['file_path']}")
        output.append("-" * 80)
        output.append(result['context'])
    
    return '\n'.join(output)


def format_json(results: List[dict], include_content: bool = False) -> str:
    """Format results as JSON."""
    output = []
    for result in results:
        item = {
            "title": result["title"],
            "source_url": result["source_url"],
            "file_path": result["file_path"],
            "relevance": result["relevance"],
            "context": result["context"],
            "content_length": result["content_length"]
        }
        if include_content:
            item["content"] = result["content"]
        output.append(item)
    
    return json.dumps(output, indent=2)


def format_markdown(results: List[dict]) -> str:
    """Format results as Markdown."""
    if not results:
        return "No results found."
    
    output = ["# Search Results\n"]
    
    for i, result in enumerate(results, 1):
        output.append(f"## {i}. {result['title']}\n")
        output.append(f"**Source:** {result['source_url']}")
        output.append(f"**Relevance:** {result['relevance']}")
        output.append(f"\n```\n{result['context']}\n```\n")
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Full-text search across indexed documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
FTS5 Query Syntax:
  term1 term2       - Documents containing term1 OR term2 (ranked by relevance)
  term1 AND term2   - Documents containing both terms
  term1 OR term2    - Documents containing either term
  "exact phrase"    - Documents containing the exact phrase
  prefix*           - Documents with words starting with prefix
  term1 NOT term2   - Documents with term1 but not term2
  title:term        - Search only in article titles
  content:term      - Search only in article content

Examples:
  "kubernetes backup"           - Natural language search
  kubernetes AND backup         - Must contain both terms
  "AWS S3" OR Azure             - Either phrase
  title:kubernetes              - Only in titles
  postgres*                     - Prefix match (postgresql, postgres, etc.)
        """
    )
    parser.add_argument("db_path", help="Path to SQLite database")
    parser.add_argument("query", help="Search query (FTS5 syntax supported)")
    parser.add_argument("--max", type=int, default=10,
                        help="Maximum results (default: 10)")
    parser.add_argument("--title-only", action="store_true",
                        help="Search only in article titles")
    parser.add_argument("--format", choices=["text", "json", "markdown"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--full-content", action="store_true",
                        help="Include full article content in JSON output")
    parser.add_argument("--context", type=int, default=200,
                        help="Context characters around match (default: 200)")
    
    args = parser.parse_args()
    
    results = search_docs(
        args.db_path,
        args.query,
        args.max,
        args.title_only,
        args.format,
        args.context
    )
    
    if not results:
        print("No results found.", file=sys.stderr)
        sys.exit(0)
    
    if args.format == "text":
        print(format_text(results))
    elif args.format == "json":
        print(format_json(results, args.full_content))
    elif args.format == "markdown":
        print(format_markdown(results))


if __name__ == "__main__":
    main()