#!/usr/bin/env python3
"""
supermemory_cloud_search — Search Supermemory.ai cloud for knowledge.

Usage:
    python3 search.py "your query"
    python3 search.py "your query" --tag openclaw
    python3 search.py "your query" --limit 10
    python3 search.py "your query" --threshold 0.7
    python3 search.py "your query" --no-tag     # search all tags

Uses: POST https://api.supermemory.ai/v3/search
Free tier compatible — no Pro-only features.
Uses curl as HTTP backend to avoid Cloudflare bot detection on Python urllib.
"""

import argparse
import json
import os
import subprocess
import sys


def load_api_key() -> str:
    """Load API key from environment or .env file."""
    key = os.environ.get("SUPERMEMORY_OPENCLAW_API_KEY", "").strip()
    if key:
        return key

    search_dirs = [
        os.path.dirname(os.path.abspath(__file__)),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."),
        os.path.expanduser("~/.openclaw/workspace"),
    ]
    for d in search_dirs:
        env_path = os.path.join(d, ".env")
        if os.path.isfile(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("SUPERMEMORY_OPENCLAW_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val

    raise ValueError(
        "SUPERMEMORY_OPENCLAW_API_KEY not found. Set it in .env or as an environment variable."
    )


def search_documents(
    query: str,
    tag: str | None = None,
    limit: int = 5,
    threshold: float = 0.0,
) -> dict:
    """
    Search Supermemory cloud via curl.
    POST /v3/search
    """
    api_key = load_api_key()
    url = "https://api.supermemory.ai/v3/search"

    payload: dict = {
        "q": query,
        "limit": limit,
        "chunkThreshold": max(0.0, min(1.0, threshold)),
    }
    if tag:
        payload["containerTag"] = tag

    body = json.dumps(payload)

    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json",
        "--data", body,
        "--max-time", "30",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr.strip()}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid JSON response: {result.stdout[:200]}")


def format_results(data: dict, query: str) -> str:
    """Format search results for human-readable output."""
    # Handle API errors
    if "error" in data:
        return f"❌ API Error: {data['error']}\n   {data.get('details', '')}"

    results = data.get("results", [])

    if not results:
        return (
            f"🔍 No results found for: \"{query}\"\n"
            f"   Try a broader query, different --tag, or --no-tag to search all."
        )

    lines = [f"🔍 Cloud memory search: \"{query}\"", f"   Found {len(results)} result(s)\n"]

    for i, r in enumerate(results, 1):
        score = r.get("score", r.get("similarity", "?"))
        score_str = f"{score:.3f}" if isinstance(score, float) else str(score)

        # Content may live in different fields depending on API version
        # v3 search returns chunks array with content inside
        chunks = r.get("chunks", [])
        if chunks and isinstance(chunks, list):
            chunk_texts = [c.get("content", "") for c in chunks if c.get("isRelevant", True)]
            content = "\n".join(t for t in chunk_texts if t)
        else:
            content = (
                r.get("content")
                or r.get("text")
                or r.get("memory")
                or (r.get("document") or {}).get("content", "")
                or str(r)
            )
        if len(content) > 600:
            content = content[:597] + "..."

        doc_id = r.get("documentId") or r.get("id") or r.get("docId", "")
        title = r.get("title", "")
        tag = r.get("containerTag") or r.get("tag", "")
        meta = r.get("metadata") or (r.get("document") or {}).get("metadata", {})
        stored_at = meta.get("stored_at", "") if isinstance(meta, dict) else ""

        lines.append(f"--- Result {i} (score: {score_str}) ---")
        lines.append(content)
        footer = []
        if title:
            footer.append(f"title: {title[:60]}")
        if doc_id:
            footer.append(f"id: {doc_id}")
        if tag:
            footer.append(f"tag: {tag}")
        if stored_at:
            footer.append(f"stored: {stored_at[:10]}")
        if footer:
            lines.append(f"[{' | '.join(footer)}]")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Search Supermemory.ai cloud for knowledge (free tier).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 search.py "nginx config location"
  python3 search.py "SSL certificate fix" --tag fixes
  python3 search.py "user preferences" --tag openclaw --limit 10
  python3 search.py "database setup" --threshold 0.6
  python3 search.py "anything" --no-tag    # search across all tags
        """,
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument(
        "--tag", "-t",
        default="openclaw",
        help="Filter by container tag (default: openclaw)",
    )
    parser.add_argument(
        "--no-tag",
        action="store_true",
        help="Search across all tags (no container filter)",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=5,
        help="Max results to return (default: 5)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Minimum similarity threshold 0-1 (default: 0.0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response",
    )
    args = parser.parse_args()

    if not args.query.strip():
        print("ERROR: Query cannot be empty.", file=sys.stderr)
        sys.exit(1)

    tag = None if args.no_tag else (args.tag or None)

    try:
        result = search_documents(
            query=args.query,
            tag=tag,
            limit=args.limit,
            threshold=args.threshold,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_results(result, args.query))


if __name__ == "__main__":
    main()
