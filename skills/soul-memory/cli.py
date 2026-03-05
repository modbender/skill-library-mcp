#!/usr/bin/env python3
"""
Soul Memory CLI Interface for OpenClaw Plugin

Provides a simple command-line interface for searching memories.
Output is JSON formatted for easy parsing by TypeScript/JavaScript.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core import SoulMemorySystem, SearchResult
except ImportError:
    print("Error: Could not import SoulMemorySystem", file=sys.stderr)
    sys.exit(1)


def format_results_for_json(results: List[SearchResult]) -> List[Dict[str, Any]]:
    """Format search results for JSON output"""
    formatted = []
    for result in results:
        formatted.append({
            "path": result.source if hasattr(result, 'source') else "UNKNOWN",
            "content": result.content.strip(),
            "score": float(result.score),
            "priority": result.priority if hasattr(result, 'priority') else "N"
        })
    return formatted


def search_command(args: argparse.Namespace) -> None:
    """Execute search command and output JSON results"""
    try:
        # Suppress initialization output by redirecting stdout for initialization only
        import io
        old_stdout = sys.stdout

        # Initialize memory system silently
        sys.stdout = io.StringIO()
        try:
            memory_system = SoulMemorySystem()
            memory_system.initialize()
        finally:
            sys.stdout = old_stdout

        # Search
        results = memory_system.search(
            args.query,
            top_k=args.top_k
        )

        # Filter by min_score if provided
        if args.min_score > 0:
            results = [r for r in results if r.score >= args.min_score]

        # Format and output (pure JSON only)
        formatted = format_results_for_json(results)
        print(json.dumps(formatted, ensure_ascii=False, indent=2))

    except Exception as e:
        import traceback
        error_result = [{
            "error": str(e),
            "path": "ERROR",
            "content": f"Search failed: {e}",
            "score": 0.0
        }]
        print(json.dumps(error_result, ensure_ascii=False), file=sys.stdout)
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Soul Memory CLI for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "SSH VPS problem" --top_k 3
  %(prog)s search "QST physics" --min_score 2.0
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search memory')
    search_parser.add_argument('query', help='Search query text')
    search_parser.add_argument('--top_k', type=int, default=5,
                               help='Number of results to return (default: 5)')
    search_parser.add_argument('--min_score', type=float, default=0.0,
                               help='Minimum similarity score (default: 0.0)')
    search_parser.set_defaults(func=search_command)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if args.command == 'search':
        search_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
