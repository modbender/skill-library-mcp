#!/usr/bin/env python3
"""
retrieve.py — Retrieve relevant chunks from Ragie.ai

Usage:
  python3 retrieve.py --query "What is the return policy?" --top-k 6

Env:
  RAGIE_API_KEY  (required)

Optional flags:
  --top-k       Number of chunks to retrieve (default: 6)
  --partition   Scope retrieval to a specific partition
  --rerank      Enable Ragie reranking for higher accuracy (adds latency)
  --filter      JSON metadata filter e.g. '{"source": "HR"}'
  --raw         Print raw JSON response instead of formatted output
"""

import argparse
import json
import os
import sys

import requests
from dotenv import load_dotenv


load_dotenv()

API_BASE = "https://api.ragie.ai"


def get_headers():
    key = os.getenv("RAGIE_API_KEY")
    if not key:
        print("ERROR: RAGIE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def retrieve(query: str, top_k: int, partition: str | None, rerank: bool, filter_dict: dict) -> list:
    payload = {
        "query": query,
        "top_k": top_k,
        "rerank": rerank,
    }
    if partition:
        payload["partition"] = partition
    if filter_dict:
        payload["filter"] = filter_dict

    resp = requests.post(f"{API_BASE}/retrievals", headers=get_headers(), json=payload)
    resp.raise_for_status()
    data = resp.json()
    # Ragie returns { "scored_chunks": [...] }
    return data.get("scored_chunks", data)


def main():
    parser = argparse.ArgumentParser(description="Retrieve chunks from Ragie.ai")
    parser.add_argument("--query", required=True, help="The retrieval query")
    parser.add_argument("--top-k", type=int, default=6, help="Number of chunks to retrieve")
    parser.add_argument("--partition", default=None, help="Ragie partition to scope to")
    parser.add_argument("--rerank", action="store_true", help="Enable Ragie reranking")
    parser.add_argument("--filter", default="{}", help="JSON metadata filter")
    parser.add_argument("--raw", action="store_true", help="Print raw JSON")
    args = parser.parse_args()

    filter_dict = json.loads(args.filter)

    chunks = retrieve(args.query, args.top_k, args.partition, args.rerank, filter_dict)

    if args.raw:
        print(json.dumps(chunks, indent=2))
        return

    if not chunks:
        print("No results found.")
        return

    print(f"Found {len(chunks)} chunk(s) for query: \"{args.query}\"\n")
    print("=" * 70)
    for i, chunk in enumerate(chunks, 1):
        score = chunk.get("score", "N/A")
        doc_name = chunk.get("document_metadata", {}).get("name", chunk.get("document_name", "Unknown"))
        doc_id = chunk.get("document_id", "N/A")
        text = chunk.get("text", "")
        print(f"[{i}] Score: {score:.4f}  |  Document: {doc_name}  |  ID: {doc_id}")
        print(f"    {text[:300]}{'...' if len(text) > 300 else ''}")
        print("-" * 70)

    # Also output clean JSON for programmatic use
    simplified = [
        {
            "text": c.get("text", ""),
            "score": c.get("score"),
            "document_name": c.get("document_metadata", {}).get("name", c.get("document_name")),
            "document_id": c.get("document_id"),
        }
        for c in chunks
    ]
    print("\n--- JSON Output ---")
    print(json.dumps(simplified, indent=2))


if __name__ == "__main__":
    main()
