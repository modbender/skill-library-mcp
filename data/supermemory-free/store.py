#!/usr/bin/env python3
"""
supermemory_cloud_store — Store knowledge to Supermemory.ai cloud.

Usage:
    python3 store.py "knowledge string"
    python3 store.py "knowledge string" --tag openclaw
    python3 store.py "knowledge string" --tag openclaw --source "session"
    python3 store.py "knowledge string" --custom-id "my-doc-id"

Uses: POST https://api.supermemory.ai/v3/documents
Free tier compatible — no Pro-only features.
Uses curl as HTTP backend to avoid Cloudflare bot detection on Python urllib.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


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


def store_document(
    content: str,
    tag: str | None = None,
    source: str | None = None,
    custom_id: str | None = None,
    entity_context: str | None = None,
) -> dict:
    """
    Store a document to Supermemory cloud via curl.
    POST /v3/documents
    """
    api_key = load_api_key()
    url = "https://api.supermemory.ai/v3/documents"

    payload: dict = {"content": content}
    if tag:
        payload["containerTag"] = tag
    if custom_id:
        payload["customId"] = custom_id
    if entity_context:
        payload["entityContext"] = entity_context[:1500]

    metadata: dict = {}
    if source:
        metadata["source"] = source
    metadata["stored_at"] = datetime.now(timezone.utc).isoformat()
    metadata["stored_by"] = "openclaw"
    if metadata:
        payload["metadata"] = metadata

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


def main():
    parser = argparse.ArgumentParser(
        description="Store knowledge to Supermemory.ai cloud (free tier).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 store.py "The nginx config is at /etc/nginx/sites-available/default"
  python3 store.py "User prefers Python over Node for scripts" --tag openclaw
  python3 store.py "Fixed: 403 on /v3/memories — use /v3/documents instead" --tag fixes
  python3 store.py "DB_PASSWORD is in /etc/secrets/db.env" --tag config
        """,
    )
    parser.add_argument("content", help="Knowledge string to store in the cloud")
    parser.add_argument(
        "--tag", "-t",
        default="openclaw",
        help="Container tag / namespace (default: openclaw)",
    )
    parser.add_argument(
        "--source", "-s",
        default="manual",
        help="Source label for metadata (default: manual)",
    )
    parser.add_argument(
        "--custom-id",
        help="Optional custom document ID (alphanumeric, hyphens, underscores, max 100 chars)",
    )
    parser.add_argument(
        "--entity-context",
        help="Context hint for memory extraction (max 1500 chars)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON response",
    )
    args = parser.parse_args()

    if not args.content.strip():
        print("ERROR: Content cannot be empty.", file=sys.stderr)
        sys.exit(1)

    try:
        result = store_document(
            content=args.content,
            tag=args.tag or None,
            source=args.source,
            custom_id=args.custom_id,
            entity_context=args.entity_context,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Handle both success and API error responses
        if "error" in result:
            print(f"❌ API Error: {result.get('error')}", file=sys.stderr)
            if "details" in result:
                print(f"   Details: {result['details']}", file=sys.stderr)
            sys.exit(1)

        doc_id = result.get("id", "unknown")
        status = result.get("status", "unknown")
        tag_display = args.tag or "none"
        print(f"✅ Stored to Supermemory cloud")
        print(f"   ID:     {doc_id}")
        print(f"   Status: {status}")
        print(f"   Tag:    {tag_display}")
        print(f"   Chars:  {len(args.content)}")


if __name__ == "__main__":
    main()
