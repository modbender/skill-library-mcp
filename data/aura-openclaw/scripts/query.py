#!/usr/bin/env python3
"""Aura Query Script for OpenClaw Integration.

Searches through an .aura knowledge base for relevant documents.
Also supports searching agent memory via the Memory OS.

Security Manifest:
    Environment Variables: None
    External Endpoints: None
    Local Files Read: User-specified .aura file, ~/.aura/memory/
    Local Files Written: None

Usage:
    python query.py <aura_file> <search_query>
    python query.py --memory <search_query>
"""

import sys


def query_aura_file(aura_file, query):
    """Search a compiled .aura knowledge base."""
    try:
        from aura.rag import AuraRAGLoader
    except ImportError:
        print("❌ aura-core not installed. Run: pip install auralith-aura")
        sys.exit(1)

    loader = AuraRAGLoader(aura_file)

    print(f"🔍 Searching '{aura_file}' for: {query}")
    print(f"📦 Archive contains {len(loader)} documents")
    print("-" * 60)

    query_lower = query.lower()
    results = []

    for doc_id, text, meta in loader.iterate_texts():
        if not text:
            continue
        text_lower = text.lower()
        score = sum(1 for word in query_lower.split() if word in text_lower)
        if score > 0:
            results.append((score, doc_id, text, meta))

    results.sort(key=lambda x: x[0], reverse=True)

    if not results:
        print("No matching documents found.")
        loader.close()
        return

    for i, (score, doc_id, text, meta) in enumerate(results[:5], 1):
        source = meta.get("source", doc_id)
        preview = text[:300].replace("\n", " ").strip()
        print(f"\n📄 [{i}] {source} (relevance: {score})")
        print(f"   {preview}...")

    print(f"\n✅ Found {len(results)} matching documents (showing top 5)")
    loader.close()


def query_memory(query, namespace=None, top_k=5):
    """Search agent memory via the Memory OS."""
    try:
        from aura.memory import AuraMemoryOS
    except ImportError:
        print("❌ aura-core not installed. Run: pip install auralith-aura")
        sys.exit(1)

    memory = AuraMemoryOS()
    results = memory.query(query, namespace=namespace, top_k=top_k)

    if results:
        print(f"🔍 Found {len(results)} memory result(s):\n")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['namespace']}] (score: {r['score']:.2f})")
            print(f"     {r['content'][:200]}...")
            print(f"     Source: {r['source']}  |  {r['timestamp']}")
            print()
    else:
        print("No matching memories found.")


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python query.py <aura_file> <search_query>")
        print("  python query.py --memory <search_query>")
        print()
        print("Examples:")
        print('  python query.py knowledge.aura "contract termination clause"')
        print('  python query.py --memory "user preferences"')
        sys.exit(1)

    if sys.argv[1] == "--memory":
        query = " ".join(sys.argv[2:])
        query_memory(query)
    else:
        aura_file = sys.argv[1]
        query = " ".join(sys.argv[2:])
        query_aura_file(aura_file, query)


if __name__ == "__main__":
    main()
