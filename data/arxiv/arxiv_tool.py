#!/usr/bin/env python3
"""
arXiv Research Assistant
Search, fetch, and analyze academic papers from arXiv.org

Usage:
    python arxiv_tool.py search "query" [--max 5] [--sort relevance|date]
    python arxiv_tool.py get <arxiv_id>
    python arxiv_tool.py download <arxiv_id> [--output ./papers/]
    python arxiv_tool.py list-saved
    python arxiv_tool.py save <arxiv_id>
"""

import arxiv
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Optional MongoDB integration
try:
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

# Configuration
MONGO_URI = os.getenv('MONGODB_URI', '')
MONGO_DB = os.getenv('MONGODB_DB_NAME', 'garud_brain')
PAPERS_DIR = os.getenv('ARXIV_PAPERS_DIR', './papers')


class ArxivAssistant:
    def __init__(self):
        self.client = arxiv.Client()
        self.db = None
        if MONGO_AVAILABLE and MONGO_URI:
            try:
                mongo_client = MongoClient(MONGO_URI)
                self.db = mongo_client[MONGO_DB]
            except Exception as e:
                print(f"Warning: MongoDB connection failed: {e}", file=sys.stderr)

    def search(self, query: str, max_results: int = 5, sort_by: str = "relevance") -> list:
        """Search arXiv for papers matching query"""
        
        sort_criterion = arxiv.SortCriterion.Relevance
        if sort_by == "date":
            sort_criterion = arxiv.SortCriterion.SubmittedDate
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_criterion
        )
        
        results = []
        for paper in self.client.results(search):
            results.append(self._paper_to_dict(paper))
        
        return results
    
    def get_paper(self, arxiv_id: str) -> dict:
        """Get details for a specific paper by arXiv ID"""
        
        # Clean the ID
        arxiv_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "")
        if "/" not in arxiv_id and "." in arxiv_id:
            # New format: 2401.12345
            pass
        
        search = arxiv.Search(id_list=[arxiv_id])
        
        for paper in self.client.results(search):
            return self._paper_to_dict(paper, full=True)
        
        return {"error": f"Paper {arxiv_id} not found"}
    
    def download_pdf(self, arxiv_id: str, output_dir: str = None) -> str:
        """Download PDF for a paper"""
        
        output_dir = output_dir or PAPERS_DIR
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        arxiv_id = arxiv_id.replace("arXiv:", "").replace("arxiv:", "")
        search = arxiv.Search(id_list=[arxiv_id])
        
        for paper in self.client.results(search):
            filename = f"{arxiv_id.replace('/', '_')}.pdf"
            filepath = os.path.join(output_dir, filename)
            paper.download_pdf(dirpath=output_dir, filename=filename)
            return filepath
        
        return None
    
    def save_paper(self, arxiv_id: str, status: str = "to-read") -> bool:
        """Save paper to MongoDB reading list"""
        
        if self.db is None:
            print("MongoDB not configured. Paper not saved.", file=sys.stderr)
            return False
        
        paper = self.get_paper(arxiv_id)
        if "error" in paper:
            return False
        
        paper["status"] = status
        paper["saved_at"] = datetime.utcnow()
        
        self.db.papers.update_one(
            {"arxiv_id": paper["arxiv_id"]},
            {"$set": paper},
            upsert=True
        )
        return True
    
    def list_saved(self, status: str = None) -> list:
        """List saved papers from MongoDB"""
        
        if self.db is None:
            return []
        
        query = {}
        if status:
            query["status"] = status
        
        return list(self.db.papers.find(query, {"_id": 0}))
    
    def update_status(self, arxiv_id: str, status: str) -> bool:
        """Update paper status (to-read, reading, read, cited)"""
        
        if self.db is None:
            return False
        
        result = self.db.papers.update_one(
            {"arxiv_id": arxiv_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    def _paper_to_dict(self, paper, full: bool = False) -> dict:
        """Convert arxiv.Result to dictionary"""
        
        data = {
            "arxiv_id": paper.entry_id.split("/")[-1],
            "title": paper.title,
            "authors": [str(a) for a in paper.authors[:5]],  # Limit authors
            "published": paper.published.isoformat() if paper.published else None,
            "updated": paper.updated.isoformat() if paper.updated else None,
            "categories": paper.categories,
            "primary_category": paper.primary_category,
            "pdf_url": paper.pdf_url,
            "abstract": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
        }
        
        if full:
            data["abstract"] = paper.summary
            data["authors"] = [str(a) for a in paper.authors]
            data["comment"] = paper.comment
            data["journal_ref"] = paper.journal_ref
            data["doi"] = paper.doi
            data["links"] = [{"href": l.href, "title": l.title} for l in paper.links]
        
        return data


def format_paper(paper: dict, verbose: bool = False) -> str:
    """Format paper for display"""
    
    lines = []
    lines.append(f"📄 {paper['title']}")
    lines.append(f"   ID: {paper['arxiv_id']}")
    lines.append(f"   Authors: {', '.join(paper['authors'][:3])}" + 
                 (f" (+{len(paper['authors'])-3} more)" if len(paper['authors']) > 3 else ""))
    lines.append(f"   Published: {paper['published'][:10] if paper['published'] else 'N/A'}")
    lines.append(f"   Category: {paper['primary_category']}")
    lines.append(f"   PDF: {paper['pdf_url']}")
    
    if verbose:
        lines.append(f"\n   Abstract:\n   {paper['abstract']}")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="arXiv Research Assistant")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for papers")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max", type=int, default=5, help="Max results")
    search_parser.add_argument("--sort", choices=["relevance", "date"], default="relevance")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")
    search_parser.add_argument("-v", "--verbose", action="store_true", help="Show abstracts")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get paper details")
    get_parser.add_argument("arxiv_id", help="arXiv paper ID")
    get_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Download command
    dl_parser = subparsers.add_parser("download", help="Download PDF")
    dl_parser.add_argument("arxiv_id", help="arXiv paper ID")
    dl_parser.add_argument("--output", default="./papers", help="Output directory")
    
    # Save command
    save_parser = subparsers.add_parser("save", help="Save paper to reading list")
    save_parser.add_argument("arxiv_id", help="arXiv paper ID")
    save_parser.add_argument("--status", default="to-read", choices=["to-read", "reading", "read", "cited"])
    
    # List command
    list_parser = subparsers.add_parser("list", help="List saved papers")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update paper status")
    update_parser.add_argument("arxiv_id", help="arXiv paper ID")
    update_parser.add_argument("status", choices=["to-read", "reading", "read", "cited"])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    assistant = ArxivAssistant()
    
    if args.command == "search":
        results = assistant.search(args.query, args.max, args.sort)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n🔍 Found {len(results)} papers for: \"{args.query}\"\n")
            for paper in results:
                print(format_paper(paper, args.verbose))
                print()
    
    elif args.command == "get":
        paper = assistant.get_paper(args.arxiv_id)
        if args.json:
            print(json.dumps(paper, indent=2))
        else:
            if "error" in paper:
                print(f"❌ {paper['error']}")
            else:
                print(format_paper(paper, verbose=True))
    
    elif args.command == "download":
        filepath = assistant.download_pdf(args.arxiv_id, args.output)
        if filepath:
            print(f"✅ Downloaded: {filepath}")
        else:
            print(f"❌ Failed to download paper {args.arxiv_id}")
    
    elif args.command == "save":
        if assistant.save_paper(args.arxiv_id, args.status):
            print(f"✅ Paper {args.arxiv_id} saved as '{args.status}'")
        else:
            print(f"❌ Failed to save paper")
    
    elif args.command == "list":
        papers = assistant.list_saved(args.status)
        if args.json:
            print(json.dumps(papers, indent=2, default=str))
        else:
            print(f"\n📚 Saved Papers: {len(papers)}\n")
            for paper in papers:
                status_emoji = {"to-read": "📖", "reading": "📚", "read": "✅", "cited": "📝"}.get(paper.get("status"), "📄")
                print(f"{status_emoji} [{paper.get('status', 'N/A')}] {paper.get('title', 'N/A')}")
                print(f"   ID: {paper.get('arxiv_id', 'N/A')}")
                print()
    
    elif args.command == "update":
        if assistant.update_status(args.arxiv_id, args.status):
            print(f"✅ Updated {args.arxiv_id} to '{args.status}'")
        else:
            print(f"❌ Failed to update paper")


if __name__ == "__main__":
    main()
