#!/usr/bin/env python3
"""Memory Search - Search vector memory by semantic similarity."""

import os
import sys
import json
import argparse
import psycopg2
from typing import Optional
import requests

DB_HOST = os.environ.get("VECTOR_MEMORY_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("VECTOR_MEMORY_DB_PORT", "5432"))
DB_NAME = os.environ.get("VECTOR_MEMORY_DB_NAME", "vector_memory")
DB_USER = os.environ.get("VECTOR_MEMORY_DB_USER", "aister")
DB_PASSWORD = os.environ.get("VECTOR_MEMORY_DB_PASSWORD", "")

EMBEDDING_SERVICE_URL = os.environ.get("EMBEDDING_SERVICE_URL", "http://127.0.0.1:8765")
DEFAULT_THRESHOLD = float(os.environ.get("VECTOR_MEMORY_THRESHOLD", "0.5"))
DEFAULT_LIMIT = int(os.environ.get("VECTOR_MEMORY_LIMIT", "5"))


def get_embedding(text: str) -> Optional[list]:
    """Get embedding from the embedding service."""
    try:
        response = requests.post(
            f"{EMBEDDING_SERVICE_URL}/embed_query",
            json={"query": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except Exception as e:
        print(f"Error getting embedding: {e}", file=sys.stderr)
        return None


def search_memory(query: str, limit: int = DEFAULT_LIMIT, threshold: float = DEFAULT_THRESHOLD) -> list:
    """Search for similar memories."""
    embedding = get_embedding(query)
    if not embedding:
        return []

    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        cur.execute("""
            SELECT 
                id, 
                content, 
                metadata, 
                source, 
                created_at,
                1 - (embedding <=> %s::vector) as similarity
            FROM memories
            WHERE 1 - (embedding <=> %s::vector) > %s
            ORDER BY similarity DESC
            LIMIT %s
        """, (str(embedding), str(embedding), threshold, limit))

        results = []
        for row in cur.fetchall():
            results.append({
                "id": row[0],
                "content": row[1],
                "metadata": row[2],
                "source": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "similarity": row[5]
            })

        cur.close()
        return results

    except psycopg2.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        return []
    finally:
        if conn:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description="Search vector memory")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-l", "--limit", type=int, default=DEFAULT_LIMIT, help=f"Max results (default: {DEFAULT_LIMIT})")
    parser.add_argument("-t", "--threshold", type=float, default=DEFAULT_THRESHOLD, help=f"Similarity threshold (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    results = search_memory(args.query, args.limit, args.threshold)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        if not results:
            print("No results found.")
            return

        print(f"Found {len(results)} results:\n")
        for i, r in enumerate(results, 1):
            print(f"[{i}] Similarity: {r['similarity']:.3f}")
            print(f"    Source: {r['source']}")
            print(f"    Content: {r['content'][:200]}...")
            print()


if __name__ == "__main__":
    main()
