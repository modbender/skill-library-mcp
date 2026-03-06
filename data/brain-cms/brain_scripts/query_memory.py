#!/usr/bin/env python3
"""
Brain CMS — Semantic Memory Query
Finds the most relevant schema files for a given query.

Usage:
    python3 query_memory.py "working on robot demo this weekend"
    python3 query_memory.py "job application status" --top 5
    python3 query_memory.py "what is my project" --sources-only
"""

import sys, argparse, requests
from pathlib import Path
import lancedb

STORE_DIR  = Path(__file__).parent / "vectorstore"
OLLAMA_URL = "http://localhost:11434/api/embeddings"
EMBED_MODEL = "nomic-embed-text"

def embed(text: str) -> list[float]:
    r = requests.post(OLLAMA_URL, json={"model": EMBED_MODEL, "prompt": text}, timeout=30)
    r.raise_for_status()
    return [float(x) for x in r.json()["embedding"]]

def query(text: str, top_k: int = 4) -> list[dict]:
    if not STORE_DIR.exists():
        print("[ERROR] Vector store not found. Run index_memory.py first.")
        return []
    db = lancedb.connect(str(STORE_DIR))
    tables = db.list_tables()
    if hasattr(tables, 'tables'): tables = tables.tables
    if "memory_chunks" not in tables:
        print("[ERROR] No memory_chunks table. Run index_memory.py first.")
        return []
    return db.open_table("memory_chunks").search(embed(text)).limit(top_k).to_list()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="+")
    parser.add_argument("--top", type=int, default=4)
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()

    results = query(" ".join(args.query), args.top)
    if not results:
        print("No results.")
        return

    if args.sources_only:
        seen = set()
        for r in results:
            src = r["source"]
            if src not in seen:
                seen.add(src)
                print(f"memory/{src}")
        return

    print(f"\n🧠 Results for: \"{' '.join(args.query)}\"\n")
    for i, r in enumerate(results, 1):
        score = r.get("_distance", "?")
        print(f"[{i}] {r['source']} | {r['section']}")
        print(f"     Score: {score:.4f}" if isinstance(score, float) else f"     Score: {score}")
        print(f"     {r['text'][:200].strip()}...\n")

if __name__ == "__main__":
    main()
