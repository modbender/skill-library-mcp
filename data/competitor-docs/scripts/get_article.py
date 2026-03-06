#!/usr/bin/env python3
"""
Get a specific article by source URL or title.

Usage:
    get_article.py <docs_dir> <url_or_title> [--full]

Examples:
    get_article.py ./docs "system_requirements_for_kubernetes" --full
    get_article.py ./docs "https://documentation.commvault.com/11.42/software/system_requirements_for_kubernetes.html"
"""

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Article:
    title: str
    source_url: str
    content: str
    file_path: str


def parse_articles(file_path: str) -> List[Article]:
    """Parse a documentation file into individual articles."""
    articles = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    article_delimiter = r'\n\s*\n---\s*\n'
    raw_articles = re.split(article_delimiter, content)
    
    for raw_article in raw_articles:
        if not raw_article.strip():
            continue
        
        title_match = re.search(r'^#\s+(.+)$', raw_article, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled"
        
        source_match = re.search(r'\*?Source:\s*(\S+)', raw_article)
        source_url = source_match.group(1) if source_match else "Unknown"
        
        article = Article(
            title=title,
            source_url=source_url,
            content=raw_article.strip(),
            file_path=file_path
        )
        articles.append(article)
    
    return articles


def find_article(docs_dir: str, search_term: str) -> Optional[Article]:
    """Find an article by URL or title (partial match)."""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        return None
    
    md_files = list(docs_path.rglob("*.md"))
    search_lower = search_term.lower()
    
    best_match = None
    best_score = 0
    
    for md_file in md_files:
        articles = parse_articles(str(md_file))
        
        for article in articles:
            # Score based on how well it matches
            score = 0
            
            # Exact URL match
            if search_term == article.source_url:
                return article
            
            # URL contains search term
            if search_lower in article.source_url.lower():
                score = 50 + len(search_term) / len(article.source_url) * 50
            
            # Title contains search term
            if search_lower in article.title.lower():
                title_score = 30 + len(search_term) / len(article.title) * 30
                score = max(score, title_score)
            
            if score > best_score:
                best_score = score
                best_match = article
    
    return best_match


def find_all_matching(docs_dir: str, search_term: str) -> List[Article]:
    """Find all articles matching a URL or title pattern."""
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        return []
    
    md_files = list(docs_path.rglob("*.md"))
    search_lower = search_term.lower()
    matches = []
    
    for md_file in md_files:
        articles = parse_articles(str(md_file))
        
        for article in articles:
            if (search_lower in article.source_url.lower() or 
                search_lower in article.title.lower()):
                matches.append(article)
    
    return matches


def main():
    parser = argparse.ArgumentParser(description="Get article by URL or title")
    parser.add_argument("docs_dir", help="Path to documentation directory")
    parser.add_argument("search", help="URL or title to search for")
    parser.add_argument("--full", action="store_true",
                        help="Show full article content")
    parser.add_argument("--all", action="store_true",
                        help="Show all matching articles")
    parser.add_argument("--metadata", action="store_true",
                        help="Show only metadata (title, source, file)")
    
    args = parser.parse_args()
    
    if args.all:
        articles = find_all_matching(args.docs_dir, args.search)
        if not articles:
            print("No matching articles found.")
            return
        
        for i, article in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"Title: {article.title}")
            print(f"Source: {article.source_url}")
            print(f"File: {article.file_path}")
            if args.full:
                print(f"\n{article.content}")
    else:
        article = find_article(args.docs_dir, args.search)
        
        if not article:
            print(f"No article found matching: {args.search}")
            return
        
        print(f"Title: {article.title}")
        print(f"Source: {article.source_url}")
        print(f"File: {article.file_path}")
        
        if args.full and not args.metadata:
            print(f"\n{article.content}")
        elif not args.metadata:
            # Show preview (first 500 chars)
            preview = article.content[:500]
            if len(article.content) > 500:
                preview += "..."
            print(f"\n{preview}")


if __name__ == "__main__":
    main()