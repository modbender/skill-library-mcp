#!/usr/bin/env python3
"""
notion.py - Notion API CLI + importable module
Usage:
  python3 notion.py search "query"
  python3 notion.py read PAGE_ID
  python3 notion.py create DATABASE_ID --title "Title" --props '{"Status": {"select": {"name": "Done"}}}'
  python3 notion.py append PAGE_ID --text "New content"
  python3 notion.py databases
"""
import os
import sys
import json
import argparse
from urllib import request, error

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "ntn_R368210231801s4MMnfbcy6pFjMrW0hk2DhcmK01vmJ9n8")
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


def _headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _req(method, path, data=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode() if data else None
    req = request.Request(url, data=body, headers=_headers(), method=method)
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read())
    except error.HTTPError as e:
        msg = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {msg}")


# --- API functions ---

def search(query, filter_type=None):
    """Search pages and databases in Notion."""
    payload = {"query": query, "page_size": 20}
    if filter_type:
        payload["filter"] = {"value": filter_type, "property": "object"}
    return _req("POST", "/search", payload)


def read_page(page_id):
    """Get page metadata."""
    return _req("GET", f"/pages/{page_id}")


def read_blocks(block_id, cursor=None):
    """Get child blocks of a page or block."""
    path = f"/blocks/{block_id}/children?page_size=100"
    if cursor:
        path += f"&start_cursor={cursor}"
    return _req("GET", path)


def read_page_content(page_id):
    """Get full page metadata + all blocks."""
    page = read_page(page_id)
    blocks = read_blocks(page_id)
    return {"page": page, "blocks": blocks}


def create_page(database_id, title, extra_props=None):
    """Create a new page in a database."""
    props = {
        "title": {
            "title": [{"type": "text", "text": {"content": title}}]
        }
    }
    if extra_props:
        props.update(extra_props)
    payload = {
        "parent": {"database_id": database_id},
        "properties": props,
    }
    return _req("POST", "/pages", payload)


def append_blocks(page_id, text):
    """Append a paragraph block to a page."""
    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": text}}
                    ]
                }
            }
        ]
    }
    return _req("PATCH", f"/blocks/{page_id}/children", payload)


def list_databases():
    """List all databases accessible to the integration."""
    result = search("", filter_type="database")
    return result


# --- Pretty printers ---

def _print_title(obj):
    """Extract title string from a Notion object."""
    props = obj.get("properties", {})
    for key, val in props.items():
        if val.get("type") == "title":
            parts = val["title"]
            return "".join(p.get("plain_text", "") for p in parts)
    # Fallback for search results
    t = obj.get("title", [])
    if isinstance(t, list):
        return "".join(p.get("plain_text", "") for p in t)
    return "(untitled)"


def _blocks_to_text(blocks_resp):
    lines = []
    for block in blocks_resp.get("results", []):
        btype = block.get("type", "")
        content = block.get(btype, {})
        rich = content.get("rich_text", [])
        text = "".join(r.get("plain_text", "") for r in rich)
        if text:
            lines.append(f"[{btype}] {text}")
    return "\n".join(lines) if lines else "(no text content)"


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Notion CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_search = sub.add_parser("search", help="Search Notion")
    p_search.add_argument("query")
    p_search.add_argument("--type", choices=["page", "database"], default=None)

    p_read = sub.add_parser("read", help="Read a page")
    p_read.add_argument("page_id")
    p_read.add_argument("--blocks", action="store_true", help="Include block content")

    p_create = sub.add_parser("create", help="Create page in database")
    p_create.add_argument("database_id")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--props", default=None, help="JSON extra properties")

    p_append = sub.add_parser("append", help="Append text block to page")
    p_append.add_argument("page_id")
    p_append.add_argument("--text", required=True)

    p_db = sub.add_parser("databases", help="List databases")

    args = parser.parse_args()

    if args.cmd == "search":
        result = search(args.query, args.type)
        items = result.get("results", [])
        if not items:
            print("No results found.")
        for item in items:
            oid = item.get("id")
            otype = item.get("object")
            title = _print_title(item)
            print(f"[{otype}] {title}\n  ID: {oid}")

    elif args.cmd == "read":
        if args.blocks:
            data = read_page_content(args.page_id)
            page = data["page"]
            print(f"Title: {_print_title(page)}")
            print(f"ID: {page['id']}")
            print(f"URL: {page.get('url', '')}")
            print("\n--- Content ---")
            print(_blocks_to_text(data["blocks"]))
        else:
            page = read_page(args.page_id)
            print(json.dumps(page, indent=2))

    elif args.cmd == "create":
        extra = json.loads(args.props) if args.props else None
        page = create_page(args.database_id, args.title, extra)
        print(f"Created page: {page['id']}")
        print(f"URL: {page.get('url', '')}")

    elif args.cmd == "append":
        result = append_blocks(args.page_id, args.text)
        added = len(result.get("results", []))
        print(f"Appended {added} block(s) to page {args.page_id}")

    elif args.cmd == "databases":
        result = list_databases()
        items = result.get("results", [])
        if not items:
            print("No databases found.")
        for item in items:
            title = _print_title(item)
            print(f"[database] {title}\n  ID: {item['id']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
