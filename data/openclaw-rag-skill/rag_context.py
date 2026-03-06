#!/usr/bin/env python3
"""
RAG Context Checker - Simple wrapper for automatic knowledge base lookup

Usage from within Python/OpenClaw sessions:
    from rag_context import check_context
    check_context("your question here")

This prints relevant context if found, otherwise silent.
"""

import sys
import os
# Use current directory for imports (skill directory)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_query_wrapper import search_knowledge, format_for_ai


def check_context(query: str, max_results: int = 5, min_score: float = 0.3) -> None:
    """
    Check knowledge base for relevant context and print it.

    This is designed as a simple call-and-forget function. If context exists,
    it prints it. If not, it's silent.

    Args:
        query: The question or topic to search for
        max_results: Maximum results to retrieve
        min_score: Minimum similarity score (not used in current implementation)

    Example:
        >>> check_context("how to send SMS")
        📚 Found 3 relevant items...
        [prints context]
    """
    if not query or len(query) < 3:
        return

    try:
        results = search_knowledge(query, n_results=max_results)

        if results and results.get('count', 0) > 0:
            print("\n" + "="*80)
            print("📚 RELEVANT CONTEXT FROM KNOWLEDGE BASE\n")
            formatted = format_for_ai(results)
            print(formatted)
            print("="*80 + "\n")

    except Exception as e:
        # Fail silently - RAG errors shouldn't break conversations
        pass


def get_context(query: str, max_results: int = 5) -> str:
    """
    Get context as a string (for automated use).

    Returns formatted context string, or empty string if no results.

    Args:
        query: Search query
        max_results: Maximum results

    Returns:
        Formatted context string, or "" if no results

    Example:
        >>> context = get_context("Reddit automation")
        >>> if context:
        >>>     print("Found relevant past work:")
        >>>     print(context)
    """
    try:
        results = search_knowledge(query, n_results=max_results)

        if results and results.get('count', 0) > 0:
            return format_for_ai(results)

    except Exception as e:
        pass

    return ""


# Quick test when run directly
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        check_context(query)
    else:
        print("Usage: python3 rag_context.py <query>")
        print("Or import: from rag_context import check_context")