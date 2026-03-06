#!/usr/bin/env python3
"""
ingest.py — Ingest a document into Ragie.ai

Usage:
  python3 ingest.py --file /path/to/doc.pdf --name "My Doc"
  python3 ingest.py --url https://example.com/doc.pdf --name "Remote Doc"

Env:
  RAGIE_API_KEY  (required)

Optional flags:
  --partition   Partition name to scope the document to (default: none)
  --metadata    JSON string of arbitrary metadata e.g. '{"source": "HR"}'
"""

import argparse
import json
import os
import sys
import time
from dotenv import load_dotenv
import requests

load_dotenv()

API_BASE = "https://api.ragie.ai"


def get_headers():
    key = os.getenv("RAGIE_API_KEY")
    if not key:
        print("ERROR: RAGIE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return {"Authorization": f"Bearer {key}"}


def ingest_file(path, name, partition, metadata):
    headers = get_headers()
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f)}
        data = {"name": name}
        if partition:
            data["partition"] = partition
        if metadata:
            data["metadata"] = json.dumps(metadata)
        resp = requests.post(f"{API_BASE}/documents", headers=headers, files=files, data=data)
    resp.raise_for_status()
    return resp.json()


def ingest_url(url: str, name: str, partition: str | None, metadata: dict) -> dict:
    headers = get_headers()
    headers["Content-Type"] = "application/json"
    payload = {"url": url, "name": name}
    if partition:
        payload["partition"] = partition
    if metadata:
        payload["metadata"] = metadata
    resp = requests.post(f"{API_BASE}/documents/url", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def wait_for_ready(doc_id: str, timeout: int = 120):
    """Poll document status until ready or failed."""
    headers = get_headers()
    start = time.time()
    while time.time() - start < timeout:
        resp = requests.get(f"{API_BASE}/documents/{doc_id}", headers=headers)
        resp.raise_for_status()
        doc = resp.json()
        status = doc.get("status", "unknown")
        print(f"  Status: {status}")
        if status == "ready":
            return doc
        if status in ("failed", "error"):
            print(f"ERROR: Document processing failed: {doc}", file=sys.stderr)
            sys.exit(1)
        time.sleep(3)
    print(f"WARNING: Timed out waiting for document {doc_id} to become ready.")
    return None


def main():
    parser = argparse.ArgumentParser(description="Ingest a document into Ragie.ai")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Local file path to ingest")
    group.add_argument("--url", help="Remote URL of document to ingest")
    parser.add_argument("--name", required=True, help="Human-readable name for the document")
    parser.add_argument("--partition", default=None, help="Ragie partition name")
    parser.add_argument("--metadata", default="{}", help="JSON metadata string")
    parser.add_argument("--wait", action="store_true", help="Wait until document is ready")
    args = parser.parse_args()

    metadata = json.loads(args.metadata)

    print(f"Ingesting '{args.name}'...")
    if args.file:
        result = ingest_file(args.file, args.name, args.partition, metadata)
    else:
        result = ingest_url(args.url, args.name, args.partition, metadata)

    doc_id = result.get("id")
    print(f"✅ Document created: {doc_id}")
    print(json.dumps(result, indent=2))

    if args.wait and doc_id:
        print("Waiting for document to become ready...")
        wait_for_ready(doc_id)
        print("✅ Document is ready for retrieval.")


if __name__ == "__main__":
    main()
