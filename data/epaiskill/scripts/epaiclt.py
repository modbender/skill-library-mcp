#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import json
import requests

API_BASE = os.getenv("EPAI_API_BASE")
API_KEY = os.getenv("EPAI_API_KEY")
ACCOUNT = os.getenv("EPAI_ACCOUNT")
VERIFY_TLS = os.getenv("EPAI_VERIFY_TLS", "true").lower() == "true"
TIMEOUT = 60

if not API_BASE or not API_KEY or not ACCOUNT:
    print("❌ 缺少必需环境变量: EPAI_API_BASE、EPAI_API_KEY、EPAI_ACCOUNT")
    sys.exit(1)

HEADERS = {
    "Authorization": API_KEY,
    "Account": ACCOUNT
}

def check_file_exists(files):
    valid_files = []
    for f in files:
        if not os.path.exists(f):
            print(f"⚠ 文件不存在: {f}")
        else:
            valid_files.append(f)
    return valid_files

def kb_list():
    url = f"{API_BASE}/knowledge/list"
    r = requests.get(url, headers=HEADERS, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def kb_create(name, description="", catalog_id=None):
    if not catalog_id:
        print("❌ 必须指定 catalog_id，使用 --catalog_id 参数")
        sys.exit(1)
    url = f"{API_BASE}/knowledge/create"
    payload = {"name": name, "language": "zh-en", "description": description, "kb_type": "document", "catalog_id": catalog_id}
    r = requests.post(url, headers=HEADERS, json=payload, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def kb_delete(kb_ids):
    url = f"{API_BASE}/knowledge/delete"
    payload = {"kb_ids": kb_ids}
    r = requests.post(url, headers=HEADERS, json=payload, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def document_upload(kb_id, files):
    files = check_file_exists(files)
    if not files:
        print("❌ 没有有效文件可上传")
        return
    url = f"{API_BASE}/document/upload"
    parser_config = json.dumps({"lang_detect_enable": False,"backend": "pipeline-high-acc","chunk_type": "general","chunk_num": 256,"parent_chunk_num": 1024,"embed_model": "bge-m3","use_vision": True,"layout": True})
    data = {"parser_config": parser_config,"parse": "true","kb_id": kb_id}
    upload_files = [("files", (os.path.basename(f), open(f, "rb"))) for f in files]
    r = requests.post(url, headers=HEADERS, data=data, files=upload_files, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def catalog_list():
    url = f"{API_BASE}/catalog/list"
    r = requests.get(url, headers=HEADERS, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def catalog_create(name, parent_id=None):
    if not parent_id:
        print("❌ 必须指定 parent_id，使用 --parent_id 参数")
        sys.exit(1)
    url = f"{API_BASE}/catalog/create"
    payload = {"name": name, "parent_id": parent_id}
    r = requests.post(url, headers=HEADERS, json=payload, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def catalog_delete(catalog_id):
    url = f"{API_BASE}/catalog/delete"
    params = {"catalog_id": catalog_id, "Account": ACCOUNT}
    r = requests.delete(url, headers=HEADERS, params=params, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def document_list(kb_id):
    url = f"{API_BASE}/document/list"
    params = {"kb_id": kb_id}
    r = requests.get(url, headers=HEADERS, params=params, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def document_delete(doc_ids):
    url = f"{API_BASE}/document/delete"
    payload = {"doc_ids": doc_ids}
    r = requests.post(url, headers=HEADERS, json=payload, verify=VERIFY_TLS, timeout=TIMEOUT)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser("EPAI CLI")
    parser.add_argument("--method", required=True, choices=["kb_list","kb_create","kb_delete","document_upload","catalog_list","catalog_create","catalog_delete","document_list","document_delete"])
    parser.add_argument("--name")
    parser.add_argument("--description", default="")
    parser.add_argument("--kb_ids", nargs="+")
    parser.add_argument("--kb_id")
    parser.add_argument("--file", nargs="+")
    parser.add_argument("--catalog_id")
    parser.add_argument("--parent_id")
    parser.add_argument("--doc_ids", nargs="+")
    args = parser.parse_args()

    if args.method == "kb_list": kb_list()
    elif args.method == "kb_create": kb_create(args.name, args.description, args.catalog_id)
    elif args.method == "kb_delete": kb_delete(args.kb_ids)
    elif args.method == "document_upload": document_upload(args.kb_id, args.file)
    elif args.method == "catalog_list": catalog_list()
    elif args.method == "catalog_create": catalog_create(args.name, args.parent_id)
    elif args.method == "catalog_delete": catalog_delete(args.catalog_id)
    elif args.method == "document_list": document_list(args.kb_id)
    elif args.method == "document_delete": document_delete(args.doc_ids)

if __name__ == "__main__":
    main()
