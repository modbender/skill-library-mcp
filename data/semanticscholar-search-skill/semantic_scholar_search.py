#!/usr/bin/env python3
"""
Semantic Scholar Search - Search academic papers through Semantic Scholar API

This script provides a command-line interface to search for academic papers,
get paper details, author information, and citation data from Semantic Scholar.
"""

import argparse
import json
import sys
from typing import Dict, Any, List, Optional
import semanticscholar as sch
from semanticscholar import SemanticScholar, Author, Paper


class Config:
    """Configuration management."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    @property
    def client(self) -> SemanticScholar:
        """Get SemanticScholar client."""
        if self.api_key:
            return SemanticScholar(api_key=self.api_key)
        return SemanticScholar()


class SemanticScholarSearch:
    """Main search class for Semantic Scholar operations."""

    def __init__(self, config: Config):
        self.config = config
        self.client = config.client

    def search_papers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for papers using a query string.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of dictionaries containing paper information
        """
        try:
            results = self.client.search_paper(query, limit=limit)
            papers = []
            for paper in results:
                papers.append({
                    "paperId": paper.paperId,
                    "title": paper.title,
                    "abstract": paper.abstract,
                    "year": paper.year,
                    "authors": [{"name": author.name, "authorId": author.authorId} for author in paper.authors],
                    "url": paper.url,
                    "venue": paper.venue,
                    "publicationTypes": paper.publicationTypes,
                    "citationCount": paper.citationCount
                })
            return papers
        except sch.SemanticScholarException as e:
            return [{"error": f"Search failed: {str(e)}"}]

    def get_paper_details(self, paper_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific paper.

        Args:
            paper_id: Paper ID or DOI

        Returns:
            Dictionary containing paper details
        """
        try:
            paper = self.client.get_paper(paper_id)
            return {
                "paperId": paper.paperId,
                "title": paper.title,
                "abstract": paper.abstract,
                "year": paper.year,
                "authors": [{"name": author.name, "authorId": author.authorId} for author in paper.authors],
                "url": paper.url,
                "venue": paper.venue,
                "publicationTypes": paper.publicationTypes,
                "citationCount": paper.citationCount,
                "influentialCitationCount": paper.influentialCitationCount if hasattr(paper, 'influentialCitationCount') else None,
                "openAccessPdf": paper.openAccessPdf if hasattr(paper, 'openAccessPdf') else None
            }
        except sch.SemanticScholarException as e:
            return {"error": f"Failed to get paper details: {str(e)}"}

    def get_author_details(self, author_id: str) -> Dict[str, Any]:
        """Get detailed information about an author.

        Args:
            author_id: Author ID

        Returns:
            Dictionary containing author details
        """
        try:
            author = self.client.get_author(author_id)
            return {
                "authorId": author.authorId,
                "name": author.name,
                "url": author.url,
                "affiliations": author.affiliations if hasattr(author, 'affiliations') else [],
                "paperCount": author.paperCount,
                "citationCount": author.citationCount,
                "hIndex": author.hIndex
            }
        except sch.SemanticScholarException as e:
            return {"error": f"Failed to get author details: {str(e)}"}

    def get_citations_and_references(self, paper_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get citations and references for a paper.

        Args:
            paper_id: Paper ID or DOI
            limit: Maximum number of citations/references to return

        Returns:
            Dictionary containing lists of citations and references
        """
        try:
            paper = self.client.get_paper(paper_id)

            citations = []
            for citation in (paper.citations or [])[:limit]:
                citations.append({
                    "paperId": citation.paperId,
                    "title": citation.title,
                    "year": citation.year,
                    "authors": [{"name": author.name, "authorId": author.authorId} for author in citation.authors],
                    "citationCount": citation.citationCount if hasattr(citation, 'citationCount') else None,
                    "url": citation.url if hasattr(citation, 'url') else None
                })

            references = []
            for reference in (paper.references or [])[:limit]:
                references.append({
                    "paperId": reference.paperId,
                    "title": reference.title,
                    "year": reference.year,
                    "authors": [{"name": author.name, "authorId": author.authorId} for author in reference.authors],
                    "citationCount": reference.citationCount if hasattr(reference, 'citationCount') else None,
                    "url": reference.url if hasattr(reference, 'url') else None
                })

            return {
                "paperId": paper_id,
                "citations": citations,
                "references": references
            }
        except sch.SemanticScholarException as e:
            return {"error": f"Failed to get citations and references: {str(e)}"}


class OutputHandler:
    """Handle output formatting and file writing."""

    @staticmethod
    def print_console(data: Any, format_type: str = "console") -> None:
        """Print data to console.

        Args:
            data: Data to print
            format_type: Format type (console or json)
        """
        if format_type == "json":
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            OutputHandler._print_pretty(data)

    @staticmethod
    def _print_pretty(data: Any) -> None:
        """Print data in a human-readable format."""
        if isinstance(data, list):
            for i, item in enumerate(data, 1):
                if "error" in item:
                    print(f"Error: {item['error']}")
                    continue
                print(f"\n--- Result {i} ---")
                OutputHandler._print_paper(item)
        elif isinstance(data, dict):
            if "error" in data:
                print(f"Error: {data['error']}")
            elif "citations" in data and "references" in data:
                # Citations and references output
                print(f"\n论文ID: {data.get('paperId', 'N/A')}")

                print(f"\n引用 (Citations) - {len(data['citations'])} total:")
                for i, cit in enumerate(data['citations'][:10], 1):
                    print(f"\n  {i}. {cit.get('title', 'N/A')}")
                    if cit.get('authors'):
                        authors = ", ".join([a['name'] for a in cit['authors'][:3]])
                        print(f"     作者: {authors}")
                    if cit.get('year'):
                        print(f"     年份: {cit['year']}")
                    if cit.get('citationCount'):
                        print(f"     引用数: {cit['citationCount']}")

                print(f"\n参考文献 (References) - {len(data['references'])} total:")
                for i, ref in enumerate(data['references'][:10], 1):
                    print(f"\n  {i}. {ref.get('title', 'N/A')}")
                    if ref.get('authors'):
                        authors = ", ".join([a['name'] for a in ref['authors'][:3]])
                        print(f"     作者: {authors}")
                    if ref.get('year'):
                        print(f"     年份: {ref['year']}")
                    if ref.get('citationCount'):
                        print(f"     引用数: {ref['citationCount']}")
            elif "authorId" in data:
                # Author output
                print(f"\n作者ID: {data.get('authorId', 'N/A')}")
                print(f"姓名: {data.get('name', 'N/A')}")
                if data.get('affiliations'):
                    print(f"机构: {', '.join(data['affiliations'])}")
                print(f"论文数: {data.get('paperCount', 'N/A')}")
                print(f"引用数: {data.get('citationCount', 'N/A')}")
                print(f"H指数: {data.get('hIndex', 'N/A')}")
                if data.get('url'):
                    print(f"链接: {data['url']}")
            else:
                # Paper output
                OutputHandler._print_paper(data)

    @staticmethod
    def _print_paper(paper: Dict[str, Any]) -> None:
        """Print a single paper's information."""
        print(f"标题: {paper.get('title', 'N/A')}")
        if paper.get('authors'):
            authors = ", ".join([a['name'] for a in paper['authors'][:5]])
            if len(paper['authors']) > 5:
                authors += ", et al."
            print(f"作者: {authors}")
        if paper.get('year'):
            print(f"年份: {paper.get('year', 'N/A')}")
        if paper.get('venue'):
            print(f"发表: {paper.get('venue', 'N/A')}")
        if paper.get('citationCount') is not None:
            print(f"引用数: {paper.get('citationCount', 'N/A')}")
        if paper.get('paperId'):
            print(f"论文ID: {paper.get('paperId', 'N/A')}")
        if paper.get('abstract'):
            abstract = paper['abstract']
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."
            print(f"摘要: {abstract}")
        if paper.get('url'):
            print(f"链接: {paper.get('url', 'N/A')}")

    @staticmethod
    def write_file(data: Any, filepath: str) -> None:
        """Write data to a file in JSON format.

        Args:
            data: Data to write
            filepath: Path to output file
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n结果已保存到: {filepath}")
        except Exception as e:
            print(f"Error writing to file: {str(e)}", file=sys.stderr)


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Search academic papers through Semantic Scholar API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search papers
  %(prog)s search --query "deep learning"

  # Get paper details
  %(prog)s paper --paper-id "10.1038/nature12373"

  # Get author details
  %(prog)s author --author-id "1741101"

  # Get citations and references
  %(prog)s citations --paper-id "10.1038/nature12373"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for papers')
    search_parser.add_argument('--query', required=True, help='Search query string')
    search_parser.add_argument('--results', type=int, default=10, help='Number of results (default: 10)')
    search_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    search_parser.add_argument('--output', help='Output file path')

    # Paper command
    paper_parser = subparsers.add_parser('paper', help='Get paper details')
    paper_parser.add_argument('--paper-id', required=True, help='Paper ID or DOI')
    paper_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    paper_parser.add_argument('--output', help='Output file path')

    # Author command
    author_parser = subparsers.add_parser('author', help='Get author details')
    author_parser.add_argument('--author-id', required=True, help='Author ID')
    author_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    author_parser.add_argument('--output', help='Output file path')

    # Citations command
    citations_parser = subparsers.add_parser('citations', help='Get citations and references')
    citations_parser.add_argument('--paper-id', required=True, help='Paper ID or DOI')
    citations_parser.add_argument('--limit', type=int, default=10, help='Number of results (default: 10)')
    citations_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    citations_parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize
    config = Config()
    search = SemanticScholarSearch(config)
    output_handler = OutputHandler()

    # Execute command
    result = None
    if args.command == 'search':
        result = search.search_papers(args.query, args.results)
        output_format = args.format
    elif args.command == 'paper':
        result = search.get_paper_details(args.paper_id)
        output_format = args.format
    elif args.command == 'author':
        result = search.get_author_details(args.author_id)
        output_format = args.format
    elif args.command == 'citations':
        result = search.get_citations_and_references(args.paper_id, args.limit)
        output_format = args.format

    # Handle output
    if result:
        if hasattr(args, 'output') and args.output:
            output_handler.write_file(result, args.output)
        else:
            output_handler.print_console(result, output_format)


if __name__ == "__main__":
    main()
