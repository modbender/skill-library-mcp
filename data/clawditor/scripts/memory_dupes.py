#!/usr/bin/env python3
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def paragraphize(text: str):
    parts = re.split(r"\n\s*\n", text)
    return [p.strip() for p in parts if p.strip()]


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def main():
    parser = argparse.ArgumentParser(description="Detect near-duplicate paragraphs in memory/*.md")
    parser.add_argument("path", nargs="?", default="memory", help="Memory directory")
    parser.add_argument("--threshold", type=float, default=0.9, help="Similarity threshold")
    parser.add_argument("--min-len", type=int, default=30, help="Minimum paragraph length")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.path)
    files = sorted(root.glob("*.md")) if root.exists() else []

    paragraphs = []
    for f in files:
        try:
            text = f.read_text()
        except OSError:
            continue
        for idx, para in enumerate(paragraphize(text)):
            if len(para) < args.min_len:
                continue
            norm = normalize(para)
            paragraphs.append({
                "file": str(f),
                "index": idx,
                "text": para,
                "norm": norm,
            })

    dup_pairs = []
    flagged = set()
    total = len(paragraphs)

    for i in range(total):
        a = paragraphs[i]
        for j in range(i + 1, total):
            b = paragraphs[j]
            if abs(len(a["norm"]) - len(b["norm"])) > max(20, 0.2 * len(a["norm"])):
                continue
            score = similarity(a["norm"], b["norm"])
            if score >= args.threshold:
                dup_pairs.append({
                    "a": {"file": a["file"], "index": a["index"], "snippet": a["text"][:160]},
                    "b": {"file": b["file"], "index": b["index"], "snippet": b["text"][:160]},
                    "score": round(score, 3),
                })
                flagged.add(i)
                flagged.add(j)

    dup_rate = (len(flagged) / total) if total else 0.0

    result = {
        "memory_path": str(root),
        "total_paragraphs": total,
        "duplicate_pairs": len(dup_pairs),
        "duplicate_paragraphs": len(flagged),
        "duplication_rate": round(dup_rate, 4),
        "pairs": dup_pairs,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Memory duplicate analysis")
    print(f"Total paragraphs: {total}")
    print(f"Duplicate paragraphs: {len(flagged)}")
    print(f"Duplication rate: {dup_rate:.2%}")
    print("\nPairs")
    for pair in dup_pairs:
        print(f"- {pair[score]:.2f} {pair[a][file]}#{pair[a][index]} <-> {pair[b][file]}#{pair[b][index]}")
        print(f"  A: {pair[a][snippet]}")
        print(f"  B: {pair[b][snippet]}")


if __name__ == "__main__":
    sys.exit(main())
