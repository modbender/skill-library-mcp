#!/usr/bin/env python3
"""
Quick RAG Query - Simple function to call from Python scripts or sessions

Usage:
    from rag.rag_query_quick import search_context
    results = search_context("your question here")
"""

import sys
from pathlib import Path

# Add parent directory
sys.path.insert(0, str(Path(__file__).parent))

from rag_system import RAGSystem


def search_context(
    query: str,
    n_results: int = 5,
    collection_name: str = "openclaw_knowledge"
) -> str:
    """
    Search the RAG knowledge base and return formatted results.

    This is the simplest way to use RAG from within Python code.

    Args:
        query: Search question
        n_results: Number of results to return
        collection_name: ChromaDB collection name

    Returns:
        Formatted string with relevant context

    Example:
        >>> from rag.rag_query_quick import search_context
        >>> context = search_context("How do I send SMS?")
        >>> print(context)
    """
    try:
        rag = RAGSystem(collection_name=collection_name)
        results = rag.search(query, n_results=n_results)

        if not results:
            return "No relevant context found in knowledge base."

        output = []
        output.append(f"🔍 Found {len(results)} relevant items:\n")

        for i, result in enumerate(results, 1):
            meta = result.get('metadata', {})
            doc_type = meta.get('type', 'unknown')
            source = meta.get('source', 'unknown')

            # Format header
            if doc_type == 'session':
                header = f"📄 Session reference {i}"
            elif doc_type == 'workspace':
                header = f"📁 Code/Docs: {source}"
            elif doc_type == 'skill':
                header = f"📜 Skill: {source}"
            else:
                header = f"Reference {i}"

            # Format content
            text = result.get('text', '')
            if len(text) > 600:
                text = text[:600] + "..."

            output.append(f"\n{header}\n{text}\n")

        return '\n'.join(output)

    except Exception as e:
        return f"❌ RAG error: {e}"


# Test it when run directly
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 rag_query_quick.py <query>")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    print(search_context(query))