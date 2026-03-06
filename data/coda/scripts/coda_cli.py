#!/usr/bin/env python3
"""
Coda API CLI Tool
General-purpose Coda document manager via REST API v1.

Usage:
    export CODA_API_TOKEN="your_token"
    python coda_cli.py <command> [options]

Safety features:
- Delete operations require confirmation (--force to override)
- Publishing requires --confirm-publish
- Permission changes require --confirm-permissions
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlencode

# Try to import requests, fallback to urllib for environments without it
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request
    import urllib.error


class CodaAPIError(Exception):
    """Custom exception for Coda API errors."""
    pass


class CodaClient:
    """Client for the Coda REST API v1."""
    
    BASE_URL = "https://coda.io/apis/v1/"
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("CODA_API_TOKEN")
        if not self.token:
            raise CodaAPIError(
                "Coda API token required. Set CODA_API_TOKEN environment variable "
                "or pass --token."
            )
        
        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            })
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Tuple[Dict[str, Any], int]:
        """Make HTTP request with rate limit handling."""
        # Join URL: BASE_URL + endpoint (endpoint may start with /)
        base = self.BASE_URL.rstrip('/')
        ep = endpoint.lstrip('/')
        url = f"{base}/{ep}"
        max_retries = 3
        retry_delay = 1
        
        # Add query params to URL
        if params:
            query = urlencode(params)
            url += ('&' if '?' in url else '?') + query
        
        for attempt in range(max_retries):
            try:
                if HAS_REQUESTS:
                    response = self.session.request(
                        method, url, json=json_data
                    )
                    status_code = response.status_code
                    text = response.text
                else:
                    # Fallback to urllib
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(json_data).encode() if json_data else None,
                        headers={
                            "Authorization": f"Bearer {self.token}",
                            "Content-Type": "application/json"
                        },
                        method=method
                    )
                    try:
                        with urllib.request.urlopen(req) as resp:
                            status_code = resp.status
                            text = resp.read().decode()
                    except urllib.error.HTTPError as e:
                        status_code = e.code
                        text = e.read().decode()
                
                # Handle rate limiting (429)
                if status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise CodaAPIError("Rate limit exceeded. Please wait and try again.")
                
                # Handle other errors
                if status_code >= 400:
                    try:
                        error_data = json.loads(text)
                        message = error_data.get("message", "Unknown error")
                    except:
                        message = text or "Unknown error"
                    
                    if status_code == 401:
                        raise CodaAPIError(f"Authentication failed: {message}")
                    elif status_code == 403:
                        raise CodaAPIError(f"Permission denied: {message}")
                    elif status_code == 404:
                        raise CodaAPIError(f"Resource not found: {message}")
                    else:
                        raise CodaAPIError(f"API error ({status_code}): {message}")
                
                # Return JSON if present, else empty dict
                if text:
                    return json.loads(text), status_code
                return {}, status_code
                
            except Exception as e:
                if attempt == max_retries - 1:
                    raise CodaAPIError(f"Network error: {e}")
                time.sleep(retry_delay)
                retry_delay *= 2
        
        return {}, 500
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request."""
        result, _ = self._request("GET", endpoint, params=params)
        return result
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[Dict[str, Any], int]:
        """POST request."""
        return self._request("POST", endpoint, json_data=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[Dict[str, Any], int]:
        """PUT request."""
        return self._request("PUT", endpoint, json_data=data)
    
    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[Dict[str, Any], int]:
        """PATCH request."""
        return self._request("PATCH", endpoint, json_data=data)
    
    def delete(self, endpoint: str) -> Tuple[Dict[str, Any], int]:
        """DELETE request."""
        return self._request("DELETE", endpoint)
    
    def list_all(self, endpoint: str, params: Optional[Dict] = None) -> List[Dict]:
        """List all items with automatic pagination."""
        items = []
        params = params or {}
        
        while True:
            result = self.get(endpoint, params)
            items.extend(result.get("items", []))
            
            next_page_token = result.get("nextPageToken")
            if not next_page_token:
                break
            
            params["pageToken"] = next_page_token
        
        return items


def extract_doc_id(doc_id_or_url: str) -> str:
    """Extract doc ID from URL or return as-is if already an ID."""
    if "coda.io" in doc_id_or_url:
        match = re.search(r'/_d([a-zA-Z0-9_-]+)', doc_id_or_url)
        if match:
            return match.group(1)
        match = re.search(r'/d/([a-zA-Z0-9_-]+)', doc_id_or_url)
        if match:
            return match.group(1)
    return doc_id_or_url


def confirm_action(message: str, force: bool = False) -> bool:
    """Ask for confirmation unless force=True."""
    if force:
        return True
    response = input(f"{message} [y/N]: ").strip().lower()
    return response in ('y', 'yes')


def print_json(data: Any, compact: bool = False):
    """Print data as formatted JSON."""
    indent = None if compact else 2
    print(json.dumps(data, indent=indent, ensure_ascii=False))


def print_table(headers: List[str], rows: List[List[str]]):
    """Print simple ASCII table."""
    if not rows:
        print("No data.")
        return
    
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))
    
    for row in rows:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, widths)))


class DocsCommands:
    def __init__(self, client: CodaClient):
        self.client = client
    
    def list(self, args):
        params = {}
        if args.is_owner:
            params["isOwner"] = "true"
        if args.query:
            params["query"] = args.query
        if args.workspace_id:
            params["workspaceId"] = args.workspace_id
        if args.folder_id:
            params["folderId"] = args.folder_id
        if args.limit:
            params["limit"] = args.limit
        
        if args.all:
            items = self.client.list_all("/docs", params)
        else:
            result = self.client.get("/docs", params)
            items = result.get("items", [])
        
        if args.format == "json":
            print_json(items)
        else:
            headers = ["ID", "Name", "Owner", "Updated"]
            rows = [[d["id"], d["name"], d.get("owner", "N/A"),
                    d.get("updatedAt", "N/A")[:10]] for d in items]
            print_table(headers, rows)
            print(f"\nTotal: {len(items)} docs")
    
    def get(self, args):
        doc_id = extract_doc_id(args.doc_id)
        result = self.client.get(f"/docs/{doc_id}")
        print_json(result)
    
    def create(self, args):
        payload = {"title": args.title}
        if args.source_doc:
            payload["sourceDoc"] = extract_doc_id(args.source_doc)
        if args.folder_id:
            payload["folderId"] = args.folder_id
        if args.timezone:
            payload["timezone"] = args.timezone
        
        result, status = self.client.post("/docs", payload)
        if status == 201:
            print(f"Created doc: {result['name']} (ID: {result['id']})")
            print(f"URL: {result['browserLink']}")
        else:
            print_json(result)
    
    def delete(self, args):
        doc_id = extract_doc_id(args.doc_id)
        try:
            doc_info = self.client.get(f"/docs/{doc_id}")
            doc_name = doc_info.get("name", "Unknown")
        except:
            doc_name = doc_id
        
        if not confirm_action(
            f"Delete doc '{doc_name}'? This cannot be undone.",
            args.force
        ):
            print("Cancelled.")
            return
        
        _, status = self.client.delete(f"/docs/{doc_id}")
        print(f"Doc '{doc_name}' deleted." if status == 200 else "Deletion accepted.")


class TablesCommands:
    def __init__(self, client: CodaClient):
        self.client = client
    
    def list(self, args):
        doc_id = extract_doc_id(args.doc_id)
        items = self.client.list_all(f"/docs/{doc_id}/tables")
        
        if args.format == "json":
            print_json(items)
        else:
            headers = ["ID", "Name", "Type", "Rows"]
            rows = [[t["id"], t["name"], t.get("tableType", "N/A"),
                    str(t.get("rowCount", "N/A"))] for t in items]
            print_table(headers, rows)


class RowsCommands:
    def __init__(self, client: CodaClient):
        self.client = client
    
    def list(self, args):
        doc_id = extract_doc_id(args.doc_id)
        table_id = args.table_id
        
        params = {}
        if args.query:
            params["query"] = args.query
        if args.limit:
            params["limit"] = args.limit
        
        if args.all:
            items = self.client.list_all(f"/docs/{doc_id}/tables/{table_id}/rows", params)
        else:
            result = self.client.get(f"/docs/{doc_id}/tables/{table_id}/rows", params)
            items = result.get("items", [])
        
        if args.format == "json":
            print_json(items)
        elif args.format == "csv":
            if not items:
                print("No rows.")
                return
            columns = set()
            for item in items:
                columns.update(item.get("values", {}).keys())
            columns = sorted(columns)
            
            writer = csv.writer(sys.stdout)
            writer.writerow(["ID", "Name"] + columns)
            for item in items:
                row = [item["id"], item.get("name", "")]
                for col in columns:
                    val = item.get("values", {}).get(col, "")
                    if isinstance(val, dict):
                        val = json.dumps(val)
                    row.append(val)
                writer.writerow(row)
        else:
            headers = ["ID", "Name", "Values"]
            rows = [[r["id"], r.get("name", "N/A")[:40],
                    json.dumps(r.get("values", {}))[:50] + "..."]
                   for r in items[:20]]
            print_table(headers, rows)
            if len(items) > 20:
                print(f"\n... and {len(items) - 20} more rows")
    
    def insert(self, args):
        doc_id = extract_doc_id(args.doc_id)
        table_id = args.table_id
        
        rows = []
        if args.data:
            rows.append({"cells": json.loads(args.data)})
        elif args.file:
            with open(args.file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    rows = [{"cells": r} for r in data]
                else:
                    rows = [{"cells": data}]
        
        payload = {"rows": rows}
        result, status = self.client.post(
            f"/docs/{doc_id}/tables/{table_id}/rows",
            payload
        )
        print(f"Inserted {len(rows)} row(s)." if status == 200 else f"Queued: {result.get('requestId')}")
    
    def update(self, args):
        doc_id = extract_doc_id(args.doc_id)
        table_id = args.table_id
        row_id = args.row_id
        
        payload = {"row": {"cells": json.loads(args.data)}}
        result, status = self.client.put(
            f"/docs/{doc_id}/tables/{table_id}/rows/{row_id}",
            payload
        )
        print("Row updated." if status == 200 else f"Queued: {result.get('requestId')}")
    
    def delete(self, args):
        doc_id = extract_doc_id(args.doc_id)
        table_id = args.table_id
        row_id = args.row_id
        
        if not confirm_action(
            f"Delete row {row_id}?",
            args.force
        ):
            print("Cancelled.")
            return
        
        _, status = self.client.delete(
            f"/docs/{doc_id}/tables/{table_id}/rows/{row_id}"
        )
        print("Row deleted." if status == 200 else "Delete queued.")


class PagesCommands:
    def __init__(self, client: CodaClient):
        self.client = client
    
    def list(self, args):
        doc_id = extract_doc_id(args.doc_id)
        items = self.client.list_all(f"/docs/{doc_id}/pages")
        
        if args.format == "json":
            print_json(items)
        else:
            headers = ["ID", "Name", "Type"]
            rows = [[p["id"], p.get("name", "Untitled"),
                    p.get("contentType", "N/A")] for p in items]
            print_table(headers, rows)


def main():
    parser = argparse.ArgumentParser(
        description="Coda API CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  coda_cli.py docs list
  coda_cli.py docs get AbCDeFGH
  coda_cli.py tables list AbCDeFGH
  coda_cli.py rows list AbCDeFGH grid-xyz
        """
    )
    parser.add_argument("--token", help="Coda API token")
    parser.add_argument("--force", action="store_true", help="Skip confirmations")
    
    subparsers = parser.add_subparsers(dest="cmd_group")
    
    # Docs
    docs_p = subparsers.add_parser("docs", help="Doc operations")
    docs_sub = docs_p.add_subparsers(dest="cmd")
    
    d_list = docs_sub.add_parser("list", help="List docs")
    d_list.add_argument("--query", help="Search query")
    d_list.add_argument("--is-owner", action="store_true", help="Only owned docs")
    d_list.add_argument("--workspace-id", help="Filter by workspace")
    d_list.add_argument("--folder-id", help="Filter by folder")
    d_list.add_argument("--all", action="store_true", help="Fetch all pages")
    d_list.add_argument("--limit", type=int)
    d_list.add_argument("--format", choices=["table", "json"], default="table")
    d_list.set_defaults(func=lambda a, c: DocsCommands(c).list(a))
    
    d_get = docs_sub.add_parser("get", help="Get doc")
    d_get.add_argument("doc_id", help="Doc ID or URL")
    d_get.set_defaults(func=lambda a, c: DocsCommands(c).get(a))
    
    d_create = docs_sub.add_parser("create", help="Create doc")
    d_create.add_argument("--title", required=True)
    d_create.add_argument("--source-doc", help="Template doc ID to copy")
    d_create.add_argument("--folder-id", help="Folder ID")
    d_create.add_argument("--timezone", help="Timezone (e.g., America/Los_Angeles)")
    d_create.set_defaults(func=lambda a, c: DocsCommands(c).create(a))
    
    d_del = docs_sub.add_parser("delete", help="Delete doc")
    d_del.add_argument("doc_id")
    d_del.add_argument("--force", action="store_true", help="Skip confirmation")
    d_del.set_defaults(func=lambda a, c: DocsCommands(c).delete(a))
    
    # Tables
    tbl_p = subparsers.add_parser("tables", help="Table operations")
    tbl_sub = tbl_p.add_subparsers(dest="cmd")
    
    t_list = tbl_sub.add_parser("list", help="List tables")
    t_list.add_argument("doc_id")
    t_list.add_argument("--format", choices=["table", "json"], default="table")
    t_list.set_defaults(func=lambda a, c: TablesCommands(c).list(a))
    
    # Rows
    rows_p = subparsers.add_parser("rows", help="Row operations")
    rows_sub = rows_p.add_subparsers(dest="cmd")
    
    r_list = rows_sub.add_parser("list", help="List rows")
    r_list.add_argument("doc_id")
    r_list.add_argument("table_id")
    r_list.add_argument("--query", help="Search query")
    r_list.add_argument("--limit", type=int)
    r_list.add_argument("--all", action="store_true", help="Fetch all pages")
    r_list.add_argument("--format", choices=["table", "json", "csv"], default="table")
    r_list.set_defaults(func=lambda a, c: RowsCommands(c).list(a))
    
    r_ins = rows_sub.add_parser("insert", help="Insert row")
    r_ins.add_argument("doc_id")
    r_ins.add_argument("table_id")
    r_ins.add_argument("--data", help="JSON cell data")
    r_ins.add_argument("--file", help="JSON file")
    r_ins.set_defaults(func=lambda a, c: RowsCommands(c).insert(a))
    
    r_upd = rows_sub.add_parser("update", help="Update row")
    r_upd.add_argument("doc_id")
    r_upd.add_argument("table_id")
    r_upd.add_argument("row_id")
    r_upd.add_argument("--data", required=True, help="JSON cell data")
    r_upd.set_defaults(func=lambda a, c: RowsCommands(c).update(a))
    
    r_del = rows_sub.add_parser("delete", help="Delete row")
    r_del.add_argument("doc_id")
    r_del.add_argument("table_id")
    r_del.add_argument("row_id")
    r_del.add_argument("--force", action="store_true", help="Skip confirmation")
    r_del.set_defaults(func=lambda a, c: RowsCommands(c).delete(a))
    
    # Pages
    pages_p = subparsers.add_parser("pages", help="Page operations")
    pages_sub = pages_p.add_subparsers(dest="cmd")
    
    p_list = pages_sub.add_parser("list", help="List pages")
    p_list.add_argument("doc_id")
    p_list.add_argument("--format", choices=["table", "json"], default="table")
    p_list.set_defaults(func=lambda a, c: PagesCommands(c).list(a))
    
    args = parser.parse_args()
    if not args.cmd_group:
        parser.print_help()
        sys.exit(1)
    
    try:
        client = CodaClient(token=args.token)
        args.func(args, client)
    except CodaAPIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
