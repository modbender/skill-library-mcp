#!/usr/bin/env python3
"""
Google Scholar Search - Search academic literature through Google Scholar

This script provides a command-line interface to search for academic papers
and get author information from Google Scholar.
"""

import argparse
import json
import sys
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import time


class GoogleScholarSearch:
    """Main search class for Google Scholar operations."""

    def __init__(self):
        self.base_url = "https://scholar.google.com/scholar"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search_papers(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search for papers using a query string.

        Args:
            query: Search query string
            num_results: Maximum number of results to return

        Returns:
            List of dictionaries containing paper information
        """
        search_url = f"{self.base_url}?q={query.replace(' ', '+')}"

        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return [{"error": f"Failed to fetch data. HTTP Status code: {response.status_code}"}]

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            for item in soup.find_all('div', class_='gs_ri')[:num_results]:
                title_tag = item.find('h3', class_='gs_rt')
                title = title_tag.get_text() if title_tag else 'No title available'

                link = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else 'No link available'

                authors_tag = item.find('div', class_='gs_a')
                authors = authors_tag.get_text() if authors_tag else 'No authors available'

                abstract_tag = item.find('div', class_='gs_rs')
                abstract = abstract_tag.get_text() if abstract_tag else 'No abstract available'

                results.append({
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "url": link
                })

            return results

        except requests.RequestException as e:
            return [{"error": f"Request failed: {str(e)}"}]
        except Exception as e:
            return [{"error": f"An error occurred: {str(e)}"}]

    def search_papers_advanced(self, query: str, author: Optional[str] = None,
                              year_start: Optional[int] = None,
                              year_end: Optional[int] = None,
                              num_results: int = 10) -> List[Dict[str, Any]]:
        """Search for papers using advanced filters.

        Args:
            query: Search query string
            author: Filter by author name
            year_start: Start year for year range filter
            year_end: End year for year range filter
            num_results: Maximum number of results to return

        Returns:
            List of dictionaries containing paper information
        """
        search_params = {'q': query.replace(' ', '+')}
        if author:
            search_params['as_auth'] = author
        if year_start:
            search_params['as_ylo'] = year_start
        if year_end:
            search_params['as_yhi'] = year_end

        search_url = self.base_url + '?' + '&'.join([f"{key}={value}" for key, value in search_params.items()])

        try:
            response = requests.get(search_url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return [{"error": f"Failed to fetch data. HTTP Status code: {response.status_code}"}]

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            for item in soup.find_all('div', class_='gs_ri')[:num_results]:
                title_tag = item.find('h3', class_='gs_rt')
                title = title_tag.get_text() if title_tag else 'No title available'

                link = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else 'No link available'

                authors_tag = item.find('div', class_='gs_a')
                authors = authors_tag.get_text() if authors_tag else 'No authors available'

                abstract_tag = item.find('div', class_='gs_rs')
                abstract = abstract_tag.get_text() if abstract_tag else 'No abstract available'

                results.append({
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "url": link
                })

            return results

        except requests.RequestException as e:
            return [{"error": f"Request failed: {str(e)}"}]
        except Exception as e:
            return [{"error": f"An error occurred: {str(e)}"}]

    def get_author_info(self, author_name: str) -> Dict[str, Any]:
        """Get author information using scholarly library.

        Args:
            author_name: Name of the author

        Returns:
            Dictionary containing author details
        """
        try:
            from scholarly import scholarly

            search_query = scholarly.search_author(author_name)
            author = next(search_query, None)

            if not author:
                return {"error": f"Author '{author_name}' not found"}

            author = scholarly.fill(author)

            return {
                "name": author.get("name", "N/A"),
                "affiliation": author.get("affiliation", "N/A"),
                "interests": author.get("interests", []),
                "citedby": author.get("citedby", 0),
                "homepage": author.get("homepage", ""),
                "publications": [
                    {
                        "title": pub.get("bib", {}).get("title", "N/A"),
                        "year": pub.get("bib", {}).get("pub_year", "N/A"),
                        "citations": pub.get("num_citations", 0)
                    }
                    for pub in author.get("publications", [])[:10]
                ]
            }

        except ImportError:
            return {"error": "scholarly library not installed. Install it with: pip install scholarly"}
        except Exception as e:
            return {"error": f"Failed to get author info: {str(e)}"}


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
            if not data:
                print("No results found.")
                return

            for i, item in enumerate(data, 1):
                if "error" in item:
                    print(f"Error: {item['error']}")
                    continue
                print(f"\n--- 结果 {i} ---")
                OutputHandler._print_paper(item)
        elif isinstance(data, dict):
            if "error" in data:
                print(f"Error: {data['error']}")
            elif "name" in data and "citedby" in data:
                # Author output
                print(f"\n姓名: {data.get('name', 'N/A')}")
                if data.get('affiliation'):
                    print(f"机构: {data.get('affiliation', 'N/A')}")
                if data.get('interests'):
                    interests = ", ".join(data.get('interests', []))
                    print(f"研究领域: {interests}")
                if data.get('citedby'):
                    print(f"总引用数: {data.get('citedby', 'N/A')}")
                if data.get('homepage'):
                    print(f"主页: {data.get('homepage', 'N/A')}")

                if data.get('publications'):
                    print(f"\n近期论文 (前10篇):")
                    for i, pub in enumerate(data['publications'], 1):
                        print(f"\n  {i}. {pub.get('title', 'N/A')}")
                        if pub.get('year') and pub['year'] != 'N/A':
                            print(f"     年份: {pub['year']}")
                        if pub.get('citations'):
                            print(f"     引用数: {pub['citations']}")

    @staticmethod
    def _print_paper(paper: Dict[str, Any]) -> None:
        """Print a single paper's information."""
        print(f"标题: {paper.get('title', 'N/A')}")
        print(f"作者: {paper.get('authors', 'N/A')}")

        abstract = paper.get('abstract', 'N/A')
        if abstract and abstract != 'No abstract available':
            # Clean up the abstract (remove extra whitespace)
            abstract = ' '.join(abstract.split())
            if len(abstract) > 300:
                abstract = abstract[:300] + "..."
            print(f"摘要: {abstract}")

        url = paper.get('url', '')
        if url and url != 'No link available':
            print(f"链接: {url}")

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
        description='Search academic literature through Google Scholar',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search papers
  %(prog)s search --query "machine learning"

  # Advanced search with author filter
  %(prog)s advanced --query "deep learning" --author "Ian Goodfellow"

  # Search with year range
  %(prog)s advanced --query "neural networks" --year-start 2018 --year-end 2022

  # Get author information
  %(prog)s author --name "Geoffrey Hinton"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search papers by keywords')
    search_parser.add_argument('--query', required=True, help='Search query string')
    search_parser.add_argument('--results', type=int, default=10, help='Number of results (default: 10)')
    search_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    search_parser.add_argument('--output', help='Output file path')

    # Advanced search command
    advanced_parser = subparsers.add_parser('advanced', help='Advanced search with filters')
    advanced_parser.add_argument('--query', required=True, help='Search query string')
    advanced_parser.add_argument('--author', help='Filter by author name')
    advanced_parser.add_argument('--year-start', type=int, help='Start year')
    advanced_parser.add_argument('--year-end', type=int, help='End year')
    advanced_parser.add_argument('--results', type=int, default=10, help='Number of results (default: 10)')
    advanced_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    advanced_parser.add_argument('--output', help='Output file path')

    # Author command
    author_parser = subparsers.add_parser('author', help='Get author information')
    author_parser.add_argument('--name', required=True, help='Author name')
    author_parser.add_argument('--format', choices=['console', 'json'], default='console', help='Output format')
    author_parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize
    searcher = GoogleScholarSearch()
    output_handler = OutputHandler()

    # Execute command
    result = None
    if args.command == 'search':
        result = searcher.search_papers(args.query, args.results)
        output_format = args.format
    elif args.command == 'advanced':
        result = searcher.search_papers_advanced(
            args.query,
            author=args.author,
            year_start=args.year_start,
            year_end=args.year_end,
            num_results=args.results
        )
        output_format = args.format
    elif args.command == 'author':
        result = searcher.get_author_info(args.name)
        output_format = args.format

    # Handle output
    if result:
        if hasattr(args, 'output') and args.output:
            output_handler.write_file(result, args.output)
        else:
            output_handler.print_console(result, output_format)


if __name__ == "__main__":
    main()
