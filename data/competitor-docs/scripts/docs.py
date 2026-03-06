#!/usr/bin/env python3
"""
Unified CLI for competitor documentation search.

Provides a single entry point for indexing and searching documentation.

Usage:
    docs.py index <docs_dir> [--db <database>] [--rebuild]
    docs.py search <query> [--db <database>] [options]
    docs.py status [--db <database>]
    docs.py get <url_or_title> [--db <database>] [--full]

Examples:
    docs.py index ./docs
    docs.py search "kubernetes backup" --max 5
    docs.py search "AWS AND S3" --format json
    docs.py status
    docs.py get "system_requirements_for_kubernetes" --full
"""

import argparse
import os
import sys
from pathlib import Path

# Import from sibling scripts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from index_docs import index_docs, init_database, get_indexed_files
from fts_search import search_docs, format_text, format_json, format_markdown
from get_article import find_article, find_all_matching


def get_default_db():
    """Get default database path (in same directory as docs)."""
    # Look for docs directory and existing db files
    cwd = Path.cwd()
    
    # Check common locations for existing databases
    for docs_dir in [cwd / "docs", cwd / "Documentation", cwd / "CommvaultDocumentation", cwd]:
        if docs_dir.exists():
            # Check for existing databases
            for db_name in ["competitor_docs.db", "commvault.db", "docs.db"]:
                db_path = docs_dir / db_name
                if db_path.exists():
                    return str(db_path)
            # If docs dir exists but no db, return default path
            if docs_dir != cwd:
                return str(docs_dir / "competitor_docs.db")
    
    # Fallback to cwd
    return "competitor_docs.db"


def cmd_index(args):
    """Handle index command."""
    db_path = args.db or str(Path(args.docs_dir) / "competitor_docs.db")
    
    print(f"Indexing documentation from: {args.docs_dir}")
    print(f"Database: {db_path}")
    print()
    
    files, articles, skipped = index_docs(args.docs_dir, db_path, args.rebuild)
    
    print()
    print(f"Indexing complete:")
    print(f"  Files processed: {files}")
    print(f"  Articles indexed: {articles}")
    print(f"  Articles unchanged: {skipped}")
    
    # Show status after indexing
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM articles')
    total = cursor.fetchone()[0]
    conn.close()
    print(f"  Total articles in index: {total}")


def cmd_search(args):
    """Handle search command."""
    db_path = args.db or get_default_db()
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}", file=sys.stderr)
        print("Run 'docs.py index <docs_dir>' first.", file=sys.stderr)
        sys.exit(1)
    
    results = search_docs(
        db_path,
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
        include_content = args.full_content
        print(format_json(results, include_content))
    elif args.format == "markdown":
        print(format_markdown(results))


def cmd_status(args):
    """Handle status command."""
    db_path = args.db or get_default_db()
    
    if not os.path.exists(db_path):
        print(f"No index database found at: {db_path}")
        print("Run 'docs.py index <docs_dir>' to create an index.")
        sys.exit(1)
    
    import sqlite3
    from datetime import datetime
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM articles')
    article_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM file_index')
    file_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT MIN(indexed_at), MAX(indexed_at) FROM articles')
    min_date, max_date = cursor.fetchone()
    
    print(f"Index Status: {db_path}")
    print(f"  Files indexed: {file_count}")
    print(f"  Articles indexed: {article_count}")
    print(f"  First indexed: {min_date or 'N/A'}")
    print(f"  Last indexed: {max_date or 'N/A'}")
    
    # Show some statistics
    cursor.execute('SELECT source_url FROM articles LIMIT 1000')
    urls = cursor.fetchall()
    domains = {}
    for (url,) in urls:
        if url and url != "Unknown":
            # Extract domain
            from urllib.parse import urlparse
            try:
                domain = urlparse(url).netloc
                domains[domain] = domains.get(domain, 0) + 1
            except:
                pass
    
    if domains:
        print(f"  Sample domains: {', '.join(sorted(domains.keys())[:5])}")
    
    conn.close()


def cmd_get(args):
    """Handle get command."""
    db_path = args.db or get_default_db()
    docs_dir = str(Path(db_path).parent)
    
    if args.all:
        articles = find_all_matching(docs_dir, args.query)
        if not articles:
            print(f"No articles found matching: {args.query}")
            return
        
        for i, article in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"Title: {article.title}")
            print(f"Source: {article.source_url}")
            print(f"File: {article.file_path}")
            if args.full:
                print(f"\n{article.content}")
    else:
        article = find_article(docs_dir, args.query)
        
        if not article:
            print(f"No article found matching: {args.query}")
            return
        
        print(f"Title: {article.title}")
        print(f"Source: {article.source_url}")
        print(f"File: {article.file_path}")
        
        if args.full:
            print(f"\n{article.content}")
        else:
            # Preview
            preview = article.content[:500]
            if len(article.content) > 500:
                preview += "..."
            print(f"\n{preview}")


def main():
    parser = argparse.ArgumentParser(
        description="Competitor documentation search CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--db", help="Path to SQLite database (auto-detected if not specified)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index documentation files")
    index_parser.add_argument("docs_dir", help="Path to documentation directory")
    index_parser.add_argument("--rebuild", action="store_true", help="Force full rebuild")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Full-text search")
    search_parser.add_argument("query", help="Search query (FTS5 syntax supported)")
    search_parser.add_argument("--max", type=int, default=10, help="Max results")
    search_parser.add_argument("--title-only", action="store_true", help="Search titles only")
    search_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text")
    search_parser.add_argument("--full-content", action="store_true", help="Include full content")
    search_parser.add_argument("--context", type=int, default=200, help="Context characters")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show index status")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get article by URL or title")
    get_parser.add_argument("query", help="URL or title to search for")
    get_parser.add_argument("--full", action="store_true", help="Show full article")
    get_parser.add_argument("--all", action="store_true", help="Show all matching articles")
    
    args = parser.parse_args()
    
    if args.command == "index":
        cmd_index(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "get":
        cmd_get(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()