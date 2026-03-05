#!/usr/bin/env python3
"""Dify Knowledge Base operations for meme-collector skill.

Usage:
  python3 dify_ops.py list   --dataset-id ID --api-key KEY [--proxy URL]
  python3 dify_ops.py upload --dataset-id ID --api-key KEY --name NAME --text-file PATH [--proxy URL]
  python3 dify_ops.py batch  --dataset-id ID --api-key KEY --json-file PATH [--proxy URL]
"""

import argparse
import json
import sys
import time
import requests


BASE_URL = "https://api.dify.ai/v1"


def get_session(proxy=None):
    s = requests.Session()
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


def list_documents(session, dataset_id, api_key):
    """List all document names in a dataset. Returns list of names."""
    url = f"{BASE_URL}/datasets/{dataset_id}/documents"
    headers = {"Authorization": f"Bearer {api_key}"}
    names = []
    page = 1
    while True:
        resp = session.get(url, headers=headers, params={"page": page, "limit": 100}, timeout=30)
        data = resp.json()
        for doc in data.get("data", []):
            names.append(doc["name"])
        if not data.get("has_more", False):
            break
        page += 1
    return names


def upload_document(session, dataset_id, api_key, name, text):
    """Upload a single document. Returns (success, message)."""
    url = f"{BASE_URL}/datasets/{dataset_id}/document/create_by_text"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": name,
        "text": text,
        "indexing_technique": "high_quality",
        "process_rule": {"mode": "automatic"}
    }
    resp = session.post(url, headers=headers, json=payload, timeout=30)
    data = resp.json()
    if "document" in data:
        return True, data["document"].get("id", "unknown")
    return False, json.dumps(data, ensure_ascii=False)[:200]


def cmd_list(args):
    session = get_session(args.proxy)
    names = list_documents(session, args.dataset_id, args.api_key)
    for n in names:
        print(n)
    print(f"\n--- Total: {len(names)} documents ---", file=sys.stderr)


def cmd_upload(args):
    session = get_session(args.proxy)
    with open(args.text_file, "r") as f:
        text = f.read()
    ok, msg = upload_document(session, args.dataset_id, args.api_key, args.name, text)
    if ok:
        print(f"✅ {args.name} (id: {msg})")
    else:
        print(f"❌ {args.name}: {msg}", file=sys.stderr)
        sys.exit(1)


def cmd_batch(args):
    """Batch upload from a JSON file. Format: [{"name": "...", "text": "..."}]"""
    session = get_session(args.proxy)

    # First get existing names for dedup
    existing = set(list_documents(session, args.dataset_id, args.api_key))
    print(f"知识库已有 {len(existing)} 条文档", file=sys.stderr)

    with open(args.json_file, "r") as f:
        memes = json.load(f)

    success, skipped, failed = 0, 0, []
    for i, meme in enumerate(memes):
        name = meme["name"]
        if name in existing:
            print(f"[{i+1}/{len(memes)}] ⏭️  跳过（已存在）：{name}")
            skipped += 1
            continue
        print(f"[{i+1}/{len(memes)}] 写入：{name} ... ", end="", flush=True)
        ok, msg = upload_document(session, args.dataset_id, args.api_key, name, meme["text"])
        if ok:
            print(f"✅ (id: {msg})")
            success += 1
        else:
            print(f"❌ {msg}")
            failed.append(name)
        if i < len(memes) - 1:
            time.sleep(1)

    print(f"\n=== 完成 ===", file=sys.stderr)
    print(f"新增：{success} | 跳过：{skipped} | 失败：{len(failed)}", file=sys.stderr)
    if failed:
        print(f"失败列表：{', '.join(failed)}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Dify Knowledge Base operations")
    parser.add_argument("--dataset-id", required=True)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--proxy", default=None)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list")

    p_upload = sub.add_parser("upload")
    p_upload.add_argument("--name", required=True)
    p_upload.add_argument("--text-file", required=True)

    p_batch = sub.add_parser("batch")
    p_batch.add_argument("--json-file", required=True)

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "upload":
        cmd_upload(args)
    elif args.command == "batch":
        cmd_batch(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
