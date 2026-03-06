#!/usr/bin/env python3
"""
RAG Query - Search the OpenClaw knowledge base
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag_system import RAGSystem


def format_result(result: dict, index: int) -> str:
    """Format a single search result"""
    metadata = result['metadata']

    # Determine type
    doc_type = metadata.get('type', 'unknown')
    source = metadata.get('source', '?')

    # Header based on type
    if doc_type == 'session':
        chunk_idx = metadata.get('chunk_index', '?')
        header = f"\n📄 Session {source} (chunk {chunk_idx})"
    elif doc_type == 'workspace':
        header = f"\n📁 {source}"
    elif doc_type == 'skill':
        skill_name = metadata.get('skill_name', source)
        header = f"\n📜 Skill: {skill_name}"
    elif doc_type == 'memory':
        header = f"\n🧠 Memory: {source}"
    else:
        header = f"\n🔹 {doc_type}: {source}"

    # Format text (limit length)
    text = result['text']
    if len(text) > 1000:
        text = text[:1000] + "..."

    # Get date if available
    info = []
    if 'ingested_at' in metadata:
        info.append(f"indexed {metadata['ingested_at'][:10]}")

    # Chunk info
    if 'chunk_index' in metadata and 'total_chunks' in metadata:
        info.append(f"chunk {metadata['chunk_index']+1}/{metadata['total_chunks']}")

    info_str = f" ({', '.join(info)})" if info else ""

    return f"{header}{info_str}\n{text}"


def search(
    query: str,
    n_results: int = 10,
    filters: dict = None,
    collection_name: str = "openclaw_knowledge",
    verbose: bool = True
) -> list:
    """
    Search the RAG knowledge base

    Args:
        query: Search query
        n_results: Number of results
        filters: Metadata filters (e.g., {"type": "skill"})
        collection_name: Collection name
        verbose: Print results

    Returns:
        List of result dicts
    """
    if verbose:
        print(f"🔍 Query: {query}")
        if filters:
            print(f"🎯 Filters: {filters}")
        print()

    # Initialize RAG
    rag = RAGSystem(collection_name=collection_name)

    # Search
    results = rag.search(query, n_results=n_results, filters=filters)

    if not results:
        if verbose:
            print("❌ No results found")
        return []

    if verbose:
        print(f"✅ Found {len(results)} results\n")
        print("=" * 80)

        for i, result in enumerate(results, 1):
            print(format_result(result, i))
            print("=" * 80)

    return results


def interactive_search(collection_name: str = "openclaw_knowledge"):
    """Interactive search mode"""
    print("🚀 OpenClaw RAG Search - Interactive Mode")
    print("Type 'quit' or 'exit' to stop\n")

    rag = RAGSystem(collection_name=collection_name)

    # Show stats
    stats = rag.get_stats()
    print(f"📊 Collection: {stats['collection_name']}")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Storage: {stats['persist_directory']}\n")

    while True:
        try:
            query = input("\n🔍 Search query: ").strip()

            if not query:
                continue

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            # Parse filters if any
            filters = None
            if query.startswith("type:"):
                parts = query.split(maxsplit=1)
                if len(parts) > 1:
                    doc_type = parts[0].replace("type:", "")
                    query = parts[1]
                    filters = {"type": doc_type}

            # Search
            results = rag.search(query, n_results=10, filters=filters)

            if results:
                print(f"\n✅ {len(results)} results:")
                print("=" * 80)

                for i, result in enumerate(results, 1):
                    print(format_result(result, i))
                    print("=" * 80)
            else:
                print("❌ No results found")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search OpenClaw RAG knowledge base")
    parser.add_argument("query", nargs="?", help="Search query (if not provided, enters interactive mode)")
    parser.add_argument("-n", "--num-results", type=int, default=10, help="Number of results")
    parser.add_argument("--type", help="Filter by document type (session, workspace, skill, memory)")
    parser.add_argument("--collection", default="openclaw_knowledge", help="Collection name")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")

    args = parser.parse_args()

    # Build filters
    filters = None
    if args.type:
        filters = {"type": args.type}

    if args.interactive or not args.query:
        interactive_search(collection_name=args.collection)
    else:
        search(
            query=args.query,
            n_results=args.num_results,
            filters=filters,
            collection_name=args.collection
        )