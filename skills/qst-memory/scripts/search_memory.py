#!/usr/bin/env python3
"""
QST Memory Search: Semantic search using agent's own LLM reasoning.
"""
import os

MEMORY_DIR = "/root/.openclaw/workspace/memory"
LONG_TERM_FILE = "/root/.openclaw/workspace/MEMORY.md"

def read_file(path):
    """Read file contents."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return ""

def search_memory(query):
    """
    Search memory using agent's LLM reasoning.
    This script prepares context; the actual semantic
    understanding is done by the LLM agent.
    """
    # Read long-term memory
    long_term = read_file(LONG_TERM_FILE)

    # Read recent daily memories
    memories = [long_term]

    # Add daily files (last 7 days)
    import glob
    daily_files = sorted(glob.glob(os.path.join(MEMORY_DIR, "*.md")), reverse=True)[:7]
    for path in daily_files:
        if os.path.basename(path) != "MEMORY.md":
            memories.append(read_file(path))

    return {
        "query": query,
        "context": "\n\n---\n\n".join(memories)
    }

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    result = search_memory(query)
    print(f"Query: {result['query']}")
    print(f"Context length: {len(result['context'])} chars")
