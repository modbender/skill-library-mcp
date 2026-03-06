#!/usr/bin/env python3
"""
manage.py — Manage documents in Ragie.ai (list, status, delete)

Usage:
  python3 manage.py list
  python3 manage.py list --partition my-partition
  python3 manage.py status --id doc_abc123
  python3 manage.py delete --id doc_abc123

Env:
  RAGIE_API_KEY  (required)
"""

import argparse
import json
import os
import sys
from dotenv import load_dotenv 
import requests


load_dotenv()

API_BASE = "https://api.ragie.ai"


def get_headers(content_type=False):
    key = os.getenv("RAGIE_API_KEY")
    if not key:
        print("ERROR: RAGIE_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    h = {"Authorization": f"Bearer {key}"}
    if content_type:
        h["Content-Type"] = "application/json"
    return h


def list_documents(partition: str | None):
    params = {}
    if partition:
        params["partition"] = partition
    resp = requests.get(f"{API_BASE}/documents", headers=get_headers(), params=params)
    resp.raise_for_status()
    data = resp.json()
    res = data.get("results", data) if isinstance(data, dict) else data
    if not res:
        print("No documents found.")
        return
    # print(docs)
    docs = res.get('documents')
    print(f"{'ID':<30}  {'Name':<40}  {'Status':<12}  {'Created'}")
    print("-" * 100)
    for doc in docs:
        print(f"{doc.get('id',''):<30}  {doc.get('name',''):<40}  {doc.get('status',''):<12}  {doc.get('created_at','')}")


def get_status(doc_id: str):
    resp = requests.get(f"{API_BASE}/documents/{doc_id}", headers=get_headers())
    resp.raise_for_status()
    print(json.dumps(resp.json().get("status", ""), indent=2))


def delete_document(doc_id: str):
    confirm = input(f"Delete document {doc_id}? [y/N] ").strip().lower()
    if confirm != "y":
        print("Aborted.")
        return
    resp = requests.delete(f"{API_BASE}/documents/{doc_id}", headers=get_headers())
    resp.raise_for_status()
    print(f"✅ Document {doc_id} deleted.")


def main():
    parser = argparse.ArgumentParser(description="Manage Ragie.ai documents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_p = subparsers.add_parser("list", help="List all documents")
    list_p.add_argument("--partition", default=None)

    status_p = subparsers.add_parser("status", help="Get document status")
    status_p.add_argument("--id", required=True)

    delete_p = subparsers.add_parser("delete", help="Delete a document")
    delete_p.add_argument("--id", required=True)

    args = parser.parse_args()

    if args.command == "list":
        list_documents(args.partition)
    elif args.command == "status":
        get_status(args.id)
    elif args.command == "delete":
        delete_document(args.id)


if __name__ == "__main__":
    main()
