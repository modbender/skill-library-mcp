#!/usr/bin/env python3
"""
ArXiv Search Skill for OpenClaw
Search and retrieve papers from arXiv.org for research purposes.
"""

import sys
import os
import re

# Try to import arxiv
try:
    import arxiv
    from arxiv import Client, Search
except ImportError as e:
    print(f"Error: arxiv module not installed or import failed: {e}")
    print("Run: pip install arxiv")
    sys.exit(1)


# Valid arXiv ID pattern (e.g., 2310.12345, hep-th/9901001)
ARXIV_ID_PATTERN = re.compile(r'^[a-z\-]+/\d{7}$|^\d{4}\.\d{4,5}(v\d+)?$')


def is_valid_arxiv_id(arxiv_id):
    """Validate arXiv ID to prevent path traversal and injection attacks"""
    # Check for path traversal attempts
    if ".." in arxiv_id or "/" in arxiv_id and not "/" in arxiv_id.replace("hep-th/", "").replace("math-", ""):
        return False
    
    # Validate format
    if not ARXIV_ID_PATTERN.match(arxiv_id):
        return False
    
    return True


def search_papers(query, max_results=5, categories=None):
    """Search arXiv for papers"""
    
    # Build search query
    search_query = query
    if categories:
        cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
        search_query = f"({query}) AND ({cat_query})"
    
    client = Client()
    
    search_obj = Search(
        query=search_query,
        max_results=max_results
    )
    
    results = []
    for paper in client.results(search_obj):
        results.append({
            "title": paper.title,
            "summary": paper.summary[:300] + "..." if len(paper.summary) > 300 else paper.summary,
            "authors": [a.name for a in paper.authors[:5]],
            "published": str(paper.published)[:10],
            "pdf_url": paper.pdf_url,
            "arxiv_id": paper.entry_id.split("/")[-1],
            "categories": paper.categories
        })
    
    return results


def download_paper(arxiv_id, download_dir=None):
    """Download a paper by arXiv ID"""
    if download_dir is None:
        download_dir = os.path.join(os.path.expanduser("~"), "Downloads", "arxiv")
    
    os.makedirs(download_dir, exist_ok=True)
    
    client = Client()
    search_obj = Search(id_list=[arxiv_id])
    
    paper = next(client.results(search_obj))
    
    # Download PDF to specified directory
    path = paper.download_pdf(dirpath=download_dir, filename=f"{arxiv_id}.pdf")
    return str(path)


def main():
    if len(sys.argv) < 2:
        print("Usage: arxiv.py <search|download> [args]")
        print("  search <query> [--max N] [--cats categories]")
        print("  download <arxiv_id>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        # Parse args
        query = ""
        max_results = 5
        categories = None
        
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--max" and i + 1 < len(sys.argv):
                max_results = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--cats" and i + 1 < len(sys.argv):
                categories = sys.argv[i + 1].split(",")
                i += 2
            else:
                query += sys.argv[i] + " "
                i += 1
        
        results = search_papers(query.strip(), max_results, categories)
        
        for r in results:
            print(f"\n=== {r['title']} ===")
            print(f"ID: {r['arxiv_id']}")
            print(f"Published: {r['published']}")
            print(f"Authors: {', '.join(r['authors'])}")
            print(f"Categories: {', '.join(r['categories'])}")
            print(f"Summary: {r['summary']}")
            print(f"PDF: {r['pdf_url']}")
    
    elif command == "download":
        if len(sys.argv) < 3:
            print("Usage: arxiv.py download <arxiv_id>")
            sys.exit(1)
        
        arxiv_id = sys.argv[2]
        
        # Validate arXiv ID for security
        if not is_valid_arxiv_id(arxiv_id):
            print(f"Error: Invalid arXiv ID format: {arxiv_id}", file=sys.stderr)
            print("Expected format: YYYY.NNNNN or CATEGORY/NNNNNNN", file=sys.stderr)
            sys.exit(1)
        
        path = download_paper(arxiv_id)
        print(f"Downloaded to: {path}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
