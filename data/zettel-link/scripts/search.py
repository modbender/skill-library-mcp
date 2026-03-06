#!/usr/bin/env python3
"""
search.py — Semantic search over embedded notes.

Embeds a query and compares it against cached note embeddings to find
the top-k most similar notes.

Usage:
  uv run scripts/search.py --config config/config.json --input <directory> --query "your query"
  uv run scripts/search.py --config config/config.json --input <directory> --query "your query" --top-k 10
"""

import sys
import json
import math
import argparse
from pathlib import Path

# Import embedding function from embed.py (same directory)
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from embed import embed_text, load_cache  # noqa: E402


# ── Similarity ───────────────────────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Semantic search over notes")
    parser.add_argument("--config", default="config/config.json",
                        help="Path to config.json (default: config/config.json)")
    parser.add_argument("--input", required=True, help="Path to the notes directory")
    parser.add_argument("--query", required=True, help="Search query text")
    parser.add_argument("--top-k", type=int, default=None,
                        help="Number of results (default: from config)")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        print("   Run: uv run scripts/config.py")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    model = config["model"]
    provider = config["provider"]
    max_input_length = config.get("max_input_length", 8192)
    cache_dir = config.get("cache_dir", ".embeddings")
    top_k = args.top_k if args.top_k is not None else config.get("top_k", 5)

    input_dir = Path(args.input).resolve()
    cache_path = input_dir / cache_dir / "embeddings.json"

    # Load embeddings cache
    cache = load_cache(cache_path)
    if not cache:
        print(f"❌ No embeddings found at {cache_path}")
        print("   Run embed.py first:")
        print(f"   uv run scripts/embed.py --config {args.config} --input {args.input}")
        sys.exit(1)

    print(f"💾 Loaded {len(cache)} embeddings")
    print(f"🔍 Query: \"{args.query}\"")
    print(f"🤖 Provider: {provider['name']} | Model: {model}")

    # Embed the query (truncate to max_input_length)
    query_text = args.query[:max_input_length]
    query_embedding = embed_text(query_text, model, provider)

    # Compute similarities
    results = []
    for rel, entry in cache.items():
        sim = cosine_similarity(query_embedding, entry["embedding"])
        results.append((sim, rel, entry))

    # Sort by similarity descending
    results.sort(key=lambda x: x[0], reverse=True)

    # Print top-k results
    print(f"\n📊 Top {top_k} results:\n")
    print(f"{'Score':>7}  {'Note'}")
    print(f"{'─' * 7}  {'─' * 60}")

    for i, (sim, rel, entry) in enumerate(results[:top_k]):
        stem = entry.get("stem", Path(rel).stem)
        preview = entry.get("text_preview", "")[:80].replace("\n", " ")
        print(f"  {sim:.4f}  {stem}")
        if preview:
            print(f"          {preview}...")
        print()

    # Output as JSON to stdout for programmatic use
    output = {
        "query": args.query,
        "top_k": top_k,
        "results": [
            {
                "score": round(sim, 4),
                "stem": entry.get("stem", Path(rel).stem),
                "rel": rel,
                "path": entry.get("path", ""),
                "text_preview": entry.get("text_preview", "")[:200],
            }
            for sim, rel, entry in results[:top_k]
        ],
    }

    # Save results to search_results.json
    results_path = input_dir / cache_dir / "search_results.json"
    with open(results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"📝 Results saved to: {results_path}")


if __name__ == "__main__":
    main()
