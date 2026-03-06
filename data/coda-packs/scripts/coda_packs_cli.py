#!/usr/bin/env python3
"""
Coda Packs CLI Tool

Manage Coda Packs via REST API v1.

LIMITATIONS:
- The REST API only supports basic Pack management (list, create, update, delete)
- Builds, Gallery submission, Analytics, and Collaborators require the Pack SDK CLI
- Pack SDK CLI: npx @codahq/packs-sdk

Usage:
    export CODA_API_TOKEN="your_token"
    python coda_packs_cli.py <command> [options]

Features:
- Pack name resolution to IDs
- Safety confirmations for destructive operations
"""

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class CodaAPIError(Exception):
    """Custom exception for Coda API errors."""
    pass


class CodaClient:
    """Client for the Coda REST API v1."""
    
    BASE_URL = "https://coda.io/apis/v1"
    
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
        else:
            import urllib.request
            self._opener = urllib.request.build_opener()
            self._opener.addheaders = [
                ("Authorization", f"Bearer {self.token}"),
                ("Content-Type", "application/json")
            ]
        
        self._pack_cache: Dict[str, Dict] = {}
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Tuple[Dict[str, Any], int]:
        """Make HTTP request with rate limit handling."""
        base = self.BASE_URL.rstrip('/')
        ep = endpoint.lstrip('/')
        url = f"{base}/{ep}"
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if HAS_REQUESTS:
                    response = self.session.request(method, url, **kwargs)
                    status_code = response.status_code
                    text = response.text
                else:
                    import urllib.request
                    req = urllib.request.Request(url, method=method)
                    for header, value in self._opener.addheaders:
                        req.add_header(header, value)
                    if 'json' in kwargs:
                        data = json.dumps(kwargs['json']).encode('utf-8')
                        req.data = data
                    try:
                        response = urllib.request.urlopen(req)
                        status_code = response.getcode()
                        text = response.read().decode('utf-8')
                    except urllib.error.HTTPError as e:
                        status_code = e.code
                        text = e.read().decode('utf-8') if hasattr(e, 'read') else ""
                
                if status_code == 429:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    raise CodaAPIError("Rate limit exceeded. Please wait and try again.")
                
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
                    elif status_code == 409:
                        raise CodaAPIError(f"Conflict: {message}")
                    else:
                        raise CodaAPIError(f"API error ({status_code}): {message}")
                
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
        return self._request("POST", endpoint, json=data)
    
    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Tuple[Dict[str, Any], int]:
        """PATCH request."""
        return self._request("PATCH", endpoint, json=data)
    
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
    
    def list_packs(self) -> List[Dict]:
        """List all packs with caching."""
        packs = self.list_all("/packs")
        for pack in packs:
            self._pack_cache[pack["id"]] = pack
        return packs
    
    def resolve_pack_id(self, identifier: str) -> str:
        """
        Resolve Pack ID from identifier (ID or name).
        Returns Pack ID or raises error if ambiguous/not found.
        """
        # If it looks like a numeric Pack ID, use directly
        if identifier.isdigit():
            return identifier
        
        # Otherwise, search by name
        packs = self.list_packs()
        matches = [p for p in packs if identifier.lower() in p.get("name", "").lower()]
        
        if not matches:
            raise CodaAPIError(f"No Pack found matching '{identifier}'")
        
        if len(matches) == 1:
            return str(matches[0]["id"])
        
        # Multiple matches - error with list
        error_msg = f"Multiple Packs found matching '{identifier}':\n"
        for p in matches:
            error_msg += f"  - {p['id']}: \"{p.get('name', 'Unknown')}\" "
            error_msg += f"({'gallery' if p.get('galleryId') else 'private'})\n"
        error_msg += "Please specify exact Pack ID."
        raise CodaAPIError(error_msg)
    
    def get_pack(self, pack_id: str) -> Dict:
        """Get pack by ID."""
        return self.get(f"/packs/{pack_id}")


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


class PacksCommands:
    """Handler for Pack management."""
    
    def __init__(self, client: CodaClient):
        self.client = client
    
    def list(self, args):
        """List all Packs."""
        packs = self.client.list_packs()
        
        if args.format == "json":
            print_json(packs)
        else:
            headers = ["ID", "Name", "Type", "Version", "Installs"]
            rows = []
            for p in packs:
                pack_type = "Gallery" if p.get("galleryId") else "Private"
                version = p.get("latestVersion", "N/A")
                installs = str(p.get("installCount", 0))
                rows.append([str(p["id"]), p.get("name", "Untitled")[:30], pack_type, version, installs])
            print_table(headers, rows)
            print(f"\nTotal: {len(packs)} Packs")
    
    def get(self, args):
        """Get Pack details."""
        pack_id = self.client.resolve_pack_id(args.pack_id_or_name)
        pack = self.client.get_pack(pack_id)
        print_json(pack)
    
    def create(self, args):
        """Create new Pack (no confirmation required)."""
        payload = {
            "name": args.name,
            "description": args.description or ""
        }
        if args.readme:
            payload["readme"] = args.readme
        
        result, status = self.client.post("/packs", payload)
        if status == 201:
            print(f"Created Pack: {result['name']} (ID: {result['id']})")
            print(f"Short ID: {result.get('shortId', 'N/A')}")
            print("\n⚠️  NOTE: This creates a Pack shell.")
            print("   For builds and Gallery submission, use the Pack SDK CLI:")
            print("   npx @codahq/packs-sdk")
        else:
            print_json(result)
    
    def update(self, args):
        """Update Pack metadata."""
        pack_id = self.client.resolve_pack_id(args.pack_id_or_name)
        
        payload = {}
        if args.name:
            payload["name"] = args.name
        if args.description:
            payload["description"] = args.description
        
        if not payload:
            print("No updates specified.")
            return
        
        result, _ = self.client.patch(f"/packs/{pack_id}", payload)
        print("Pack updated successfully.")
        print_json(result)
    
    def delete(self, args):
        """Delete Pack (requires confirmation)."""
        pack_id = self.client.resolve_pack_id(args.pack_id_or_name)
        pack = self.client.get_pack(pack_id)
        
        install_count = pack.get("installCount", 0)
        warning = ""
        if install_count > 0:
            warning = f" WARNING: {install_count} active installations!"
        
        if not confirm_action(
            f"Delete Pack '{pack.get('name')}' (ID: {pack_id})?{warning} "
            "This cannot be undone.",
            args.force
        ):
            print("Cancelled.")
            return
        
        _, status = self.client.delete(f"/packs/{pack_id}")
        if status == 202:
            print("Pack deletion accepted. Processing...")
        else:
            print("Pack deleted.")


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Coda Packs CLI Tool - REST API v1 (Limited Features)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
LIMITATIONS:
  The REST API only supports basic Pack management.
  For builds, Gallery, Analytics, use: npx @codahq/packs-sdk

Examples:
    # List Packs
    coda_packs_cli.py packs list
    
    # Create Pack shell
    coda_packs_cli.py packs create --name "My Pack" --description "Desc"
    
    # Update Pack
    coda_packs_cli.py packs update my-pack-id --description "New desc"
    
    # Delete Pack (requires confirmation)
    coda_packs_cli.py packs delete my-pack-id
    
    # Full Pack development workflow:
    # 1. Create shell: coda_packs_cli.py packs create ...
    # 2. Develop locally with: npx @codahq/packs-sdk init my-pack
    # 3. Build & upload: npx @codahq/packs-sdk build && npx @codahq/packs-sdk upload
        """
    )
    parser.add_argument("--token", help="Coda API token (or set CODA_API_TOKEN env var)")
    parser.add_argument("--force", action="store_true", help="Skip confirmations (use with caution)")
    
    subparsers = parser.add_subparsers(dest="command_group")
    
    # Packs commands
    packs_parser = subparsers.add_parser("packs", help="Pack management (REST API)")
    packs_sub = packs_parser.add_subparsers(dest="command")
    
    list_cmd = packs_sub.add_parser("list", help="List Packs")
    list_cmd.add_argument("--format", choices=["table", "json"], default="table")
    list_cmd.set_defaults(func=lambda args, client: PacksCommands(client).list(args))
    
    get_cmd = packs_sub.add_parser("get", help="Get Pack info")
    get_cmd.add_argument("pack_id_or_name", help="Pack ID or Pack name")
    get_cmd.set_defaults(func=lambda args, client: PacksCommands(client).get(args))
    
    create_cmd = packs_sub.add_parser("create", help="Create Pack shell (no confirmation)")
    create_cmd.add_argument("--name", required=True, help="Pack name")
    create_cmd.add_argument("--description", help="Pack description")
    create_cmd.add_argument("--readme", help="Path to README file")
    create_cmd.set_defaults(func=lambda args, client: PacksCommands(client).create(args))
    
    update_cmd = packs_sub.add_parser("update", help="Update Pack")
    update_cmd.add_argument("pack_id_or_name", help="Pack ID or name")
    update_cmd.add_argument("--name", help="New name")
    update_cmd.add_argument("--description", help="New description")
    update_cmd.set_defaults(func=lambda args, client: PacksCommands(client).update(args))
    
    delete_cmd = packs_sub.add_parser("delete", help="Delete Pack (requires confirmation)")
    delete_cmd.add_argument("pack_id_or_name", help="Pack ID or name")
    delete_cmd.set_defaults(func=lambda args, client: PacksCommands(client).delete(args))
    
    # Note about unavailable features
    note_parser = subparsers.add_parser("builds", help="NOT AVAILABLE via REST API - use Pack SDK CLI")
    note_parser.set_defaults(func=lambda args, client: print(
        "ERROR: Pack builds are not available via REST API v1.\n\n"
        "Use the Pack SDK CLI instead:\n"
        "  npx @codahq/packs-sdk build\n"
        "  npx @codahq/packs-sdk upload\n\n"
        "See: https://coda.io/packs/build/latest/guides/quickstart/"
    ) or sys.exit(1))
    
    gallery_parser = subparsers.add_parser("gallery", help="NOT AVAILABLE via REST API - use Pack SDK CLI")
    gallery_parser.set_defaults(func=lambda args, client: print(
        "ERROR: Gallery operations are not available via REST API v1.\n\n"
        "Use the Pack SDK CLI instead:\n"
        "  npx @codahq/packs-sdk release\n\n"
        "See: https://coda.io/packs/build/latest/guides/publish/"
    ) or sys.exit(1))
    
    analytics_parser = subparsers.add_parser("analytics", help="NOT AVAILABLE via REST API - use Pack SDK CLI")
    analytics_parser.set_defaults(func=lambda args, client: print(
        "ERROR: Analytics are not available via REST API v1.\n\n"
        "Use the Coda web UI or Pack SDK CLI."
    ) or sys.exit(1))
    
    collaborators_parser = subparsers.add_parser("collaborators", help="NOT AVAILABLE via REST API - use Pack SDK CLI")
    collaborators_parser.set_defaults(func=lambda args, client: print(
        "ERROR: Collaborator management is not available via REST API v1.\n\n"
        "Use the Pack SDK CLI or Coda web UI."
    ) or sys.exit(1))
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command_group:
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
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
