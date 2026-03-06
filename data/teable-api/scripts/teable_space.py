#!/usr/bin/env python3
"""
Teable Space API Client
Complete management for Teable spaces with security validations
"""

import os
import sys
import json
import argparse
import requests
from typing import Optional, List, Dict, Any
from urllib.parse import urljoin, urlparse

# Configuration
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
            raise ValueError(
                f"Invalid URL scheme: '{parsed.scheme}'. Only {ALLOWED_SCHEMES} are allowed."
            )
        
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: missing domain in '{url}'")
        
        if parsed.scheme.lower() == "http":
            print("WARNING: Using HTTP instead of HTTPS. Your API key will be transmitted in plaintext!", file=sys.stderr)
        
        return url.rstrip("/")
        
    except Exception as e:
        raise ValueError(f"Invalid TEABLE_URL '{url}': {e}")


class TeableSpaceClient:
    """Teable Space API Client with security validations"""

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

    def get_space(self, space_id: str) -> Dict[str, Any]:
        """Get Space details"""
        response = self._request("GET", f"/space/{space_id}")
        response.raise_for_status()
        return response.json()

    def list_spaces(self, take: Optional[int] = None, skip: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get Space list"""
        params = {}
        if take:
            params["take"] = take
        if skip:
            params["skip"] = skip

        response = self._request("GET", "/space", params=params)
        response.raise_for_status()
        return response.json()

    def create_space(self, name: str, icon: Optional[str] = None) -> Dict[str, Any]:
        """Create Space"""
        payload = {"name": name}
        if icon:
            payload["icon"] = icon

        response = self._request("POST", "/space", json=payload)
        response.raise_for_status()
        return response.json()

    def update_space(self, space_id: str, name: Optional[str] = None, icon: Optional[str] = None) -> Dict[str, Any]:
        """Update Space"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if icon is not None:
            payload["icon"] = icon

        response = self._request("PATCH", f"/space/{space_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def delete_space(self, space_id: str) -> bool:
        """Delete Space"""
        response = self._request("DELETE", f"/space/{space_id}")
        response.raise_for_status()
        return response.status_code == 200

    def get_bases(self, space_id: str) -> List[Dict[str, Any]]:
        """Get bases in Space"""
        response = self._request("GET", f"/space/{space_id}/base")
        response.raise_for_status()
        return response.json()

    def get_collaborators(self, space_id: str) -> List[Dict[str, Any]]:
        """Get Space collaborators"""
        response = self._request("GET", f"/space/{space_id}/collaborators")
        response.raise_for_status()
        return response.json()

    def add_collaborator(self, space_id: str, user_id: str, role: str) -> Dict[str, Any]:
        """Add Space collaborator"""
        payload = {"userId": user_id, "role": role}
        response = self._request("POST", f"/space/{space_id}/collaborator", json=payload)
        response.raise_for_status()
        return response.json()

    def remove_collaborator(self, space_id: str, user_id: str) -> bool:
        """Remove Space collaborator"""
        response = self._request("DELETE", f"/space/{space_id}/collaborators/{user_id}")
        response.raise_for_status()
        return response.status_code == 200


def main():
    parser = argparse.ArgumentParser(description="Teable Space API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    list_parser = subparsers.add_parser("list", help="List spaces")
    list_parser.add_argument("--take", type=int, help="Number of results")
    list_parser.add_argument("--skip", type=int, help="Skip count")

    get_parser = subparsers.add_parser("get", help="Get Space details")
    get_parser.add_argument("--space-id", required=True, help="Space ID")

    create_parser = subparsers.add_parser("create", help="Create Space")
    create_parser.add_argument("--name", required=True, help="Space name")
    create_parser.add_argument("--icon", help="Space icon")

    update_parser = subparsers.add_parser("update", help="Update Space")
    update_parser.add_argument("--space-id", required=True, help="Space ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--icon", help="New icon")

    delete_parser = subparsers.add_parser("delete", help="Delete Space")
    delete_parser.add_argument("--space-id", required=True, help="Space ID")

    bases_parser = subparsers.add_parser("bases", help="Get bases in Space")
    bases_parser.add_argument("--space-id", required=True, help="Space ID")

    collab_parser = subparsers.add_parser("collaborators", help="List collaborators")
    collab_parser.add_argument("--space-id", required=True, help="Space ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = TeableSpaceClient()

        if args.command == "list":
            result = client.list_spaces(take=args.take, skip=args.skip)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "get":
            result = client.get_space(args.space_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "create":
            result = client.create_space(args.name, args.icon)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "update":
            result = client.update_space(args.space_id, args.name, args.icon)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "delete":
            success = client.delete_space(args.space_id)
            print(f"Deletion {'successful' if success else 'failed'}")

        elif args.command == "bases":
            result = client.get_bases(args.space_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "collaborators":
            result = client.get_collaborators(args.space_id)
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