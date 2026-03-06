#!/usr/bin/env python3
"""
Index competitor documentation for full-text search.

Creates an SQLite database with FTS5 virtual tables for fast,
ranked full-text search across documentation articles.

Usage:
    index_docs.py <docs_dir> [--db <database_path>] [--rebuild]

Examples:
    index_docs.py ./docs
    index_docs.py ./docs --db ./competitor.db
    index_docs.py ./docs --rebuild  # Force full rebuild
"""

import argparse
import hashlib
import os
import re
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Article:
    """Represents a single documentation article."""
    title: str
    source_url: str
    content: str
    file_path: str
    file_hash: str
    article_index: int  # Position in file


def compute_file_hash(file_path: str) -> str:
    """Compute MD5 hash of file for change detection."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def parse_articles(file_path: str) -> List[Article]:
    """Parse a documentation file into individual articles."""
    articles = []
    
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    file_hash = compute_file_hash(file_path)
    
    # Split by article delimiter: blank line, ---, blank line
    article_delimiter = r'\n\s*\n---\s*\n'
    raw_articles = re.split(article_delimiter, content)
    
    for idx, raw_article in enumerate(raw_articles):
        if not raw_article.strip():
            continue
        
        # Extract title (first H1)
        title_match = re.search(r'^#\s+(.+)$', raw_article, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        
        # Extract source URL - handle various formats
        source_match = re.search(r'\*?Source:\s*(\S+)', raw_article)
        source_url = source_match.group(1) if source_match else "Unknown"
        # Clean trailing asterisks or punctuation
        source_url = source_url.rstrip('*,.')
        
        article = Article(
            title=title,
            source_url=source_url,
            content=raw_article.strip(),
            file_path=file_path,
            file_hash=file_hash,
            article_index=idx
        )
        articles.append(article)
    
    return articles


def init_database(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database with FTS5 tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Main FTS5 table for articles
    cursor.execute('''
        CREATE VIRTUAL TABLE IF NOT EXISTS articles USING fts5(
            title,
            source_url,
            content,
            file_path,
            file_hash,
            indexed_at,
            tokenize = 'porter unicode61'
        )
    ''')
    
    # Metadata table for tracking indexed files
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_index (
            file_path TEXT PRIMARY KEY,
            file_hash TEXT,
            article_count INTEGER,
            indexed_at TEXT
        )
    ''')
    
    # Note: FTS5 virtual tables don't support regular indexes
    # File path lookups use the content column which is still fast
    
    conn.commit()
    return conn


def get_indexed_files(conn: sqlite3.Connection) -> dict:
    """Get list of already indexed files with their hashes."""
    cursor = conn.cursor()
    cursor.execute('SELECT file_path, file_hash, article_count FROM file_index')
    return {row[0]: (row[1], row[2]) for row in cursor.fetchall()}


def remove_file_articles(conn: sqlite3.Connection, file_path: str):
    """Remove all articles from a specific file."""
    cursor = conn.cursor()
    cursor.execute('DELETE FROM articles WHERE file_path = ?', (file_path,))
    cursor.execute('DELETE FROM file_index WHERE file_path = ?', (file_path,))
    conn.commit()


def index_file(conn: sqlite3.Connection, file_path: str, articles: List[Article]):
    """Index all articles from a file."""
    cursor = conn.cursor()
    indexed_at = datetime.now().isoformat()
    
    for article in articles:
        cursor.execute('''
            INSERT INTO articles (title, source_url, content, file_path, file_hash, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            article.title,
            article.source_url,
            article.content,
            article.file_path,
            article.file_hash,
            indexed_at
        ))
    
    # Update file index
    cursor.execute('''
        INSERT OR REPLACE INTO file_index (file_path, file_hash, article_count, indexed_at)
        VALUES (?, ?, ?, ?)
    ''', (file_path, articles[0].file_hash if articles else '', len(articles), indexed_at))
    
    conn.commit()


def index_docs(docs_dir: str, db_path: str, rebuild: bool = False) -> Tuple[int, int, int]:
    """
    Index all documentation in a directory.
    
    Returns: (files_processed, articles_indexed, articles_skipped)
    """
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"Error: Documentation directory not found: {docs_dir}", file=sys.stderr)
        return 0, 0, 0
    
    # Find all markdown files
    md_files = list(docs_path.rglob("*.md"))
    
    if not md_files:
        print(f"Warning: No markdown files found in {docs_dir}", file=sys.stderr)
        return 0, 0, 0
    
    # Initialize database
    conn = init_database(db_path)
    
    if rebuild:
        print("Rebuilding index from scratch...")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM articles')
        cursor.execute('DELETE FROM file_index')
        conn.commit()
    
    # Get already indexed files
    indexed_files = get_indexed_files(conn)
    
    files_processed = 0
    articles_indexed = 0
    articles_skipped = 0
    
    for md_file in md_files:
        file_path = str(md_file)
        file_hash = compute_file_hash(file_path)
        
        # Check if file changed
        if file_path in indexed_files:
            stored_hash, stored_count = indexed_files[file_path]
            if stored_hash == file_hash:
                # File unchanged, skip
                articles_skipped += stored_count
                continue
            else:
                # File changed, remove old articles
                remove_file_articles(conn, file_path)
        
        # Parse and index new/changed file
        print(f"Indexing: {md_file.name}")
        articles = parse_articles(file_path)
        
        if articles:
            index_file(conn, file_path, articles)
            files_processed += 1
            articles_indexed += len(articles)
    
    conn.close()
    return files_processed, articles_indexed, articles_skipped


def main():
    parser = argparse.ArgumentParser(
        description="Index competitor documentation for full-text search",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("docs_dir", help="Path to documentation directory")
    parser.add_argument("--db", default="competitor_docs.db",
                        help="Path to SQLite database (default: competitor_docs.db)")
    parser.add_argument("--rebuild", action="store_true",
                        help="Force full rebuild of index")
    parser.add_argument("--status", action="store_true",
                        help="Show index status without reindexing")
    
    args = parser.parse_args()
    
    if args.status:
        if not os.path.exists(args.db):
            print("No index database found.")
            return
        
        conn = sqlite3.connect(args.db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM articles')
        article_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM file_index')
        file_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT MIN(indexed_at), MAX(indexed_at) FROM articles')
        min_date, max_date = cursor.fetchone()
        
        print(f"Index Status: {args.db}")
        print(f"  Files indexed: {file_count}")
        print(f"  Articles indexed: {article_count}")
        print(f"  First indexed: {min_date or 'N/A'}")
        print(f"  Last indexed: {max_date or 'N/A'}")
        
        conn.close()
        return
    
    print(f"Indexing documentation from: {args.docs_dir}")
    print(f"Database: {args.db}")
    print()
    
    files, articles, skipped = index_docs(args.docs_dir, args.db, args.rebuild)
    
    print()
    print(f"Indexing complete:")
    print(f"  Files processed: {files}")
    print(f"  Articles indexed: {articles}")
    print(f"  Articles unchanged: {skipped}")


if __name__ == "__main__":
    main()