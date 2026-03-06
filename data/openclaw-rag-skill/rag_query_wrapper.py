#!/usr/bin/env python3
"""
RAG Query Wrapper - Simple function for the AI to call from within sessions

This is designed for automatic RAG integration. The AI can call this function
to retrieve relevant context from past conversations, code, and documentation.

Usage (from within Python script or session):
    from rag_query_wrapper import search_knowledge
    results = search_knowledge("your question")
    print(results)
"""

import sys
from pathlib import Path

# Add RAG directory to path
rag_dir = Path(__file__).parent
sys.path.insert(0, str(rag_dir))

from rag_system import RAGSystem


def search_knowledge(query: str, n_results: int = 5) -> dict:
    """
    Search the knowledge base and return structured results.

    This is the primary function for automatic RAG integration.
    Returns a structured dict with results for easy programmatic use.

    Args:
        query: Search query
        n_results: Number of results to return

    Returns:
        dict with:
            - query: the search query
            - count: number of results found
            - items: list of result dicts with text and metadata
    """
    try:
        rag = RAGSystem()
        results = rag.search(query, n_results=n_results)

        items = []
        for result in results:
            meta = result.get('metadata', {})
            items.append({
                'text': result.get('text', ''),
                'type': meta.get('type', 'unknown'),
                'source': meta.get('source', 'unknown'),
                'chunk_index': meta.get('chunk_index', 0),
                'date': meta.get('date', '')
            })

        return {
            'query': query,
            'count': len(items),
            'items': items
        }

    except Exception as e:
        return {
            'query': query,
            'count': 0,
            'items': [],
            'error': str(e)
        }


def format_for_ai(results: dict) -> str:
    """
    Format RAG results for AI consumption.

    Args:
        results: dict from search_knowledge()

    Returns:
        Formatted string suitable for insertion into AI context
    """
    if results['count'] == 0:
        return ""

    output = [f"📚 Found {results['count']} relevant items from knowledge base:\n"]

    for item in results['items']:
        doc_type = item['type']
        source = item['source']
        text = item['text']

        if doc_type == 'session':
            header = f"📄 Past Conversation ({source})"
        elif doc_type == 'workspace':
            header = f"📁 Code/Documentation ({source})"
        elif doc_type == 'skill':
            header = f"📜 Skill Guide ({source})"
        else:
            header = f"🔹 Reference ({doc_type})"

        # Truncate if too long
        if len(text) > 700:
            text = text[:700] + "..."

        output.append(f"\n{header}\n{text}\n")

    return '\n'.join(output)


# Test function
def _test():
    """Quick test of RAG integration"""
    results = search_knowledge("Reddit account automation", n_results=3)
    print(format_for_ai(results))


if __name__ == "__main__":
    _test()