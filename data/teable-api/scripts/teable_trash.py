#!/usr/bin/env python3
"""
Teable Trash API Client
Complete management for Teable trash with security validations
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse

DEFAULT_BASE_URL = "https://app.teable.ai"
API_PREFIX = "/api"
ALLOWED_SCHEMES = ["https", "http"]


def validate_url(url: str) -> str:
    """Validate URL to prevent SSRF and credential exfiltration."""
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        
        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            raise ValueError(f"Invalid URL scheme: '{parsed.scheme}'. Only {ALLOWED_SCHEMES} are allowed.")
        
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: missing domain in '{url}'")
        
        if parsed.scheme.lower() == "http":
            print("WARNING: Using HTTP instead of HTTPS. Your API key will be transmitted in plaintext!", file=sys.stderr)
        
        return url.rstrip("/")
        
    except Exception as e:
        raise ValueError(f"Invalid TEABLE_URL '{url}': {e}")


class TeableTrashClient:
    """Teable Trash API Client with security validations"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        raw_url = base_url or os.getenv("TEABLE_URL") or DEFAULT_BASE_URL
        self.base_url = validate_url(raw_url)
        self.api_key = api_key or os.getenv("TEABLE_API_KEY")

        if not self.api_key:
            raise ValueError("Teable API Key is not set! Please set TEABLE_API_KEY environment variable.")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = urljoin(self.base_url + API_PREFIX, path.lstrip("/"))
        response = self.session.request(method, url, **kwargs)
        return response

    def list_trash(self, base_id: str, take: Optional[int] = None, skip: Optional[int] = None,
                   cursor: Optional[str] = None) -> Dict[str, Any]:
        """Get trash items list"""
        params = {"resourceId": base_id, "resourceType": "base"}
        if take:
            params["take"] = take
        if skip:
            params["skip"] = skip
        if cursor:
            params["cursor"] = cursor

        response = self._request("GET", "/trash", params=params)
        response.raise_for_status()
        return response.json()

    def reset_items(self, resource_id: str, resource_type: str = "base", cursor: Optional[str] = None) -> bool:
        """Empty trash"""
        params = {
            "resourceId": resource_id,
            "resourceType": resource_type
        }
        if cursor:
            params["cursor"] = cursor

        response = self._request("DELETE", "/trash/reset-items", params=params)
        response.raise_for_status()
        return response.status_code == 200

    def get_trash_item(self, item_id: str) -> Dict[str, Any]:
        """Get trash item details"""
        response = self._request("GET", f"/trash/{item_id}")
        response.raise_for_status()
        return response.json()

    def restore_item(self, item_id: str) -> Dict[str, Any]:
        """Restore trash item"""
        response = self._request("POST", f"/trash/{item_id}/restore")
        response.raise_for_status()
        return response.json()

    def restore_items(self, item_ids: List[str]) -> List[Dict[str, Any]]:
        """Batch restore trash items"""
        payload = {"itemIds": item_ids}
        response = self._request("POST", "/trash/restore", json=payload)
        response.raise_for_status()
        return response.json().get("items", [])

    def permanent_delete_item(self, item_id: str) -> bool:
        """Permanently delete trash item"""
        response = self._request("DELETE", f"/trash/{item_id}")
        response.raise_for_status()
        return response.status_code == 200

    def permanent_delete_items(self, item_ids: List[str]) -> bool:
        """Batch permanently delete trash items"""
        payload = {"itemIds": item_ids}
        response = self._request("DELETE", "/trash", json=payload)
        response.raise_for_status()
        return response.status_code == 200


def main():
    parser = argparse.ArgumentParser(description="Teable Trash API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    list_parser = subparsers.add_parser("list", help="List trash items")
    list_parser.add_argument("--base-id", required=True, help="Base ID")
    list_parser.add_argument("--take", type=int, help="Number of results")
    list_parser.add_argument("--skip", type=int, help="Skip count")

    reset_parser = subparsers.add_parser("reset", help="Empty trash")
    reset_parser.add_argument("--resource-id", required=True, help="Resource ID")
    reset_parser.add_argument("--resource-type", default="base", choices=["base", "table"])

    get_parser = subparsers.add_parser("get", help="Get trash item details")
    get_parser.add_argument("--item-id", required=True, help="Trash item ID")

    restore_parser = subparsers.add_parser("restore", help="Restore trash item")
    restore_parser.add_argument("--item-id", required=True, help="Trash item ID")
    restore_parser.add_argument("--item-ids", help="Batch restore item IDs (JSON array)")

    delete_parser = subparsers.add_parser("delete", help="Permanently delete trash item")
    delete_parser.add_argument("--item-id", help="Trash item ID")
    delete_parser.add_argument("--item-ids", help="Batch delete item IDs (JSON array)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = TeableTrashClient()

        if args.command == "list":
            result = client.list_trash(args.base_id, args.take, args.skip)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "reset":
            success = client.reset_items(args.resource_id, args.resource_type)
            print(f"Trash emptied {'successfully' if success else 'failed'}")

        elif args.command == "get":
            result = client.get_trash_item(args.item_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "restore":
            if args.item_ids:
                item_ids = json.loads(args.item_ids)
                result = client.restore_items(item_ids)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                result = client.restore_item(args.item_id)
                print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "delete":
            if args.item_ids:
                item_ids = json.loads(args.item_ids)
                success = client.permanent_delete_items(item_ids)
            else:
                success = client.permanent_delete_item(args.item_id)
            print(f"Permanent deletion {'successful' if success else 'failed'}")

    except ValueError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code}", file=sys.stderr)
        print(e.response.text, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()