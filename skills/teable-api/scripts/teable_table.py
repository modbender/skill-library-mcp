#!/usr/bin/env python3
"""
Teable Table API Client
Complete management for Teable tables with security validations
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


class TeableTableClient:
    """Teable Table API Client with security validations"""

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

    def get_table(self, table_id: str) -> Dict[str, Any]:
        """Get Table details"""
        response = self._request("GET", f"/table/{table_id}")
        response.raise_for_status()
        return response.json()

    def list_tables(self, base_id: str, take: Optional[int] = None, skip: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get Table list"""
        params = {}
        if take:
            params["take"] = take
        if skip:
            params["skip"] = skip

        response = self._request("GET", f"/base/{base_id}/table", params=params)
        response.raise_for_status()
        return response.json()

    def create_table(self, base_id: str, name: str, fields: Optional[List[Dict[str, Any]]] = None, 
                     records: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create Table"""
        payload = {"baseId": base_id, "name": name}
        if fields:
            payload["fields"] = fields
        if records:
            payload["records"] = records

        response = self._request("POST", "/table", json=payload)
        response.raise_for_status()
        return response.json()

    def update_table(self, table_id: str, name: Optional[str] = None, icon: Optional[str] = None,
                     description: Optional[str] = None) -> Dict[str, Any]:
        """Update Table"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if icon is not None:
            payload["icon"] = icon
        if description is not None:
            payload["description"] = description

        response = self._request("PATCH", f"/table/{table_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def delete_table(self, table_id: str) -> bool:
        """Delete Table"""
        response = self._request("DELETE", f"/table/{table_id}")
        response.raise_for_status()
        return response.status_code == 200

    def duplicate_table(self, table_id: str, base_id: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """Duplicate Table"""
        payload = {}
        if base_id:
            payload["baseId"] = base_id
        if name:
            payload["name"] = name

        response = self._request("POST", f"/table/{table_id}/duplicate", json=payload)
        response.raise_for_status()
        return response.json()

    def get_fields(self, table_id: str, take: Optional[int] = None, skip: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get field list"""
        params = {}
        if take:
            params["take"] = take
        if skip:
            params["skip"] = skip

        response = self._request("GET", f"/table/{table_id}/field", params=params)
        response.raise_for_status()
        return response.json()

    def get_field(self, table_id: str, field_id: str) -> Dict[str, Any]:
        """Get field details"""
        response = self._request("GET", f"/table/{table_id}/field/{field_id}")
        response.raise_for_status()
        return response.json()

    def create_field(self, table_id: str, name: str, field_type: str, 
                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create field"""
        payload = {"name": name, "type": field_type}
        if options:
            payload["options"] = options

        response = self._request("POST", f"/table/{table_id}/field", json=payload)
        response.raise_for_status()
        return response.json()

    def update_field(self, table_id: str, field_id: str, name: Optional[str] = None,
                     description: Optional[str] = None) -> Dict[str, Any]:
        """Update field"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self._request("PATCH", f"/table/{table_id}/field/{field_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def delete_field(self, table_id: str, field_id: str) -> bool:
        """Delete field"""
        response = self._request("DELETE", f"/table/{table_id}/field/{field_id}")
        response.raise_for_status()
        return response.status_code == 200

    def delete_fields(self, table_id: str, field_ids: List[str]) -> bool:
        """Batch delete fields"""
        params = {"fieldIds": field_ids}
        response = self._request("DELETE", f"/table/{table_id}/field", params=params)
        response.raise_for_status()
        return response.status_code == 200

    def get_views(self, table_id: str) -> List[Dict[str, Any]]:
        """Get view list"""
        response = self._request("GET", f"/table/{table_id}/view")
        response.raise_for_status()
        return response.json()

    def get_view(self, table_id: str, view_id: str) -> Dict[str, Any]:
        """Get view details"""
        response = self._request("GET", f"/table/{table_id}/view/{view_id}")
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(description="Teable Table API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    list_parser = subparsers.add_parser("list", help="List tables")
    list_parser.add_argument("--base-id", required=True, help="Base ID")
    list_parser.add_argument("--take", type=int, help="Number of results")
    list_parser.add_argument("--skip", type=int, help="Skip count")

    get_parser = subparsers.add_parser("get", help="Get Table details")
    get_parser.add_argument("--table-id", required=True, help="Table ID")

    create_parser = subparsers.add_parser("create", help="Create Table")
    create_parser.add_argument("--base-id", required=True, help="Base ID")
    create_parser.add_argument("--name", required=True, help="Table name")
    create_parser.add_argument("--fields", help="Initial fields (JSON)")
    create_parser.add_argument("--records", help="Initial records (JSON)")

    update_parser = subparsers.add_parser("update", help="Update Table")
    update_parser.add_argument("--table-id", required=True, help="Table ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--icon", help="New icon")
    update_parser.add_argument("--description", help="New description")

    delete_parser = subparsers.add_parser("delete", help="Delete Table")
    delete_parser.add_argument("--table-id", required=True, help="Table ID")

    dup_parser = subparsers.add_parser("duplicate", help="Duplicate Table")
    dup_parser.add_argument("--table-id", required=True, help="Table ID")
    dup_parser.add_argument("--base-id", help="Target Base ID")
    dup_parser.add_argument("--name", help="New Table name")

    fields_parser = subparsers.add_parser("fields", help="List fields")
    fields_parser.add_argument("--table-id", required=True, help="Table ID")
    fields_parser.add_argument("--take", type=int, help="Number of results")
    fields_parser.add_argument("--skip", type=int, help="Skip count")

    views_parser = subparsers.add_parser("views", help="List views")
    views_parser.add_argument("--table-id", required=True, help="Table ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = TeableTableClient()

        if args.command == "list":
            result = client.list_tables(args.base_id, args.take, args.skip)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "get":
            result = client.get_table(args.table_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "create":
            fields = json.loads(args.fields) if args.fields else None
            records = json.loads(args.records) if args.records else None
            result = client.create_table(args.base_id, args.name, fields, records)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "update":
            result = client.update_table(args.table_id, args.name, args.icon, args.description)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "delete":
            success = client.delete_table(args.table_id)
            print(f"Deletion {'successful' if success else 'failed'}")

        elif args.command == "duplicate":
            result = client.duplicate_table(args.table_id, args.base_id, args.name)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "fields":
            result = client.get_fields(args.table_id, args.take, args.skip)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "views":
            result = client.get_views(args.table_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

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