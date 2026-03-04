#!/usr/bin/env python3
"""
link.py — Discover semantic connections between notes.

Computes cosine similarity for all note pairs and outputs the connections
that exceed the configured threshold to links.json.

Usage:
  uv run scripts/link.py --config config/config.json --input <directory>
  uv run scripts/link.py --config config/config.json --input <directory> --threshold 0.7
"""

import sys
import json
import math
import argparse
import datetime
from pathlib import Path

# Import from embed.py (same directory)
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from embed import load_cache  # noqa: E402


# ── Similarity ───────────────────────────────────────────────────────────────

def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Link discovery ───────────────────────────────────────────────────────────

def find_links(
    cache: dict,
    threshold: float,
    max_threshold: float = 0.98,
) -> list[dict]:
    """
    Compute all-pairs similarity and return links above threshold.
    max_threshold filters out near-duplicates.
    """
    keys = list(cache.keys())
    n = len(keys)
    links = []

    print(f"🔢 Computing similarities for {n} notes ({n * (n - 1) // 2:,} pairs)...")

    for i in range(n):
        entry_a = cache[keys[i]]
        emb_a = entry_a["embedding"]
        stem_a = entry_a.get("stem", Path(keys[i]).stem)

        for j in range(i + 1, n):
            entry_b = cache[keys[j]]
            emb_b = entry_b["embedding"]
            stem_b = entry_b.get("stem", Path(keys[j]).stem)

            sim = cosine_similarity(emb_a, emb_b)
            if threshold <= sim < max_threshold:
                links.append({
                    "score": round(sim, 4),
                    "note_a": {
                        "stem": stem_a,
                        "rel": keys[i],
                        "path": entry_a.get("path", ""),
                    },
                    "note_b": {
                        "stem": stem_b,
                        "rel": keys[j],
                        "path": entry_b.get("path", ""),
                    },
                })

        # Progress every 50 notes
        if i % 50 == 0 and i > 0:
            print(f"  Progress: {i}/{n}...", end="\r")

    # Sort by score descending
    links.sort(key=lambda x: x["score"], reverse=True)
    return links


def build_per_note_links(links: list[dict]) -> dict:
    """Group links per note for easier consumption."""
    per_note = {}
    for link in links:
        stem_a = link["note_a"]["stem"]
        stem_b = link["note_b"]["stem"]
        score = link["score"]

        if stem_a not in per_note:
            per_note[stem_a] = []
        per_note[stem_a].append({
            "stem": stem_b,
            "rel": link["note_b"]["rel"],
            "score": score,
        })

        if stem_b not in per_note:
            per_note[stem_b] = []
        per_note[stem_b].append({
            "stem": stem_a,
            "rel": link["note_a"]["rel"],
            "score": score,
        })

    # Sort each note's links by score descending
    for stem in per_note:
        per_note[stem].sort(key=lambda x: x["score"], reverse=True)

    return per_note


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Discover semantic connections between notes"
    )
    parser.add_argument("--config", default="config/config.json",
                        help="Path to config.json (default: config/config.json)")
    parser.add_argument("--input", required=True, help="Path to the notes directory")
    parser.add_argument("--threshold", type=float, default=None,
                        help="Similarity threshold (default: from config)")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        print("   Run: uv run scripts/config.py")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = json.load(f)

    cache_dir = config.get("cache_dir", ".embeddings")
    threshold = args.threshold if args.threshold is not None else config.get("default_threshold", 0.65)

    input_dir = Path(args.input).resolve()
    cache_path = input_dir / cache_dir / "embeddings.json"
    output_path = input_dir / cache_dir / "links.json"

    # Load embeddings cache
    cache = load_cache(cache_path)
    if not cache:
        print(f"❌ No embeddings found at {cache_path}")
        print("   Run embed.py first:")
        print(f"   uv run scripts/embed.py --config {args.config} --input {args.input}")
        sys.exit(1)

    print(f"💾 Loaded {len(cache)} embeddings")
    print(f"📏 Threshold: {threshold}")

    # Find all links
    links = find_links(cache, threshold)
    per_note = build_per_note_links(links)

    print(f"\n✅ Found {len(links)} connections above {threshold} threshold")
    print(f"   Notes with connections: {len(per_note)}")

    # Build output
    output = {
        "generated": datetime.datetime.now().isoformat(),
        "threshold": threshold,
        "total_notes": len(cache),
        "total_links": len(links),
        "links": links,
        "per_note": per_note,
    }

    # Save to links.json
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"📝 Links saved to: {output_path}")

    # Print top 10 for quick preview
    print(f"\n=== Top 10 Connections ===")
    for link in links[:10]:
        a = link["note_a"]["stem"][:40]
        b = link["note_b"]["stem"][:40]
        print(f"  {link['score']:.4f}  {a:<40}  ↔  {b}")


if __name__ == "__main__":
    main()
