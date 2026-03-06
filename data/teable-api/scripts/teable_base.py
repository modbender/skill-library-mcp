#!/usr/bin/env python3
"""
Teable Base API Client
Complete management for Teable databases (Bases) with security validations
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
    """
    Validate URL to prevent SSRF and credential exfiltration.
    
    Args:
        url: URL to validate
        
    Returns:
        Validated URL
        
    Raises:
        ValueError: If URL is invalid or potentially malicious
    """
    if not url:
        return url
    
    try:
        parsed = urlparse(url)
        
        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            raise ValueError(
                f"Invalid URL scheme: '{parsed.scheme}'. "
                f"Only {ALLOWED_SCHEMES} are allowed."
            )
        
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: missing domain in '{url}'")
        
        if parsed.scheme.lower() == "http":
            print(
                "WARNING: Using HTTP instead of HTTPS. "
                "Your API key will be transmitted in plaintext!",
                file=sys.stderr
            )
        
        return url.rstrip("/")
        
    except Exception as e:
        raise ValueError(f"Invalid TEABLE_URL '{url}': {e}")


def validate_output_path(path: str, base_dir: Optional[str] = None) -> str:
    """
    Validate output file path to prevent path traversal attacks.
    
    Args:
        path: Output file path
        base_dir: Base directory (defaults to current working directory)
        
    Returns:
        Absolute path if valid
        
    Raises:
        ValueError: If path attempts directory traversal
    """
    if not path:
        raise ValueError("Output path cannot be empty")
    
    if base_dir is None:
        base_dir = os.getcwd()
    
    abs_base = os.path.abspath(base_dir)
    abs_path = os.path.abspath(path)
    
    if not abs_path.startswith(abs_base):
        raise ValueError(
            f"Security error: Output path '{path}' is outside allowed directory. "
            f"Files can only be written to '{abs_base}' or its subdirectories."
        )
    
    return abs_path


class TeableBaseClient:
    """Teable Base API Client with security validations"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize client with security validations.
        
        Args:
            base_url: Teable instance URL (validated for security)
            api_key: Teable API Token
        """
        raw_url = base_url or os.getenv("TEABLE_URL") or DEFAULT_BASE_URL
        self.base_url = validate_url(raw_url)
        self.api_key = api_key or os.getenv("TEABLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Teable API Key is not set! Please set TEABLE_API_KEY environment variable."
            )

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Send HTTP request"""
        url = urljoin(self.base_url + API_PREFIX, path.lstrip("/"))
        response = self.session.request(method, url, **kwargs)
        return response

    # ==================== Read Base ====================

    def get_base(self, base_id: str) -> Dict[str, Any]:
        """Get Base details"""
        response = self._request("GET", f"/base/{base_id}")
        response.raise_for_status()
        return response.json()

    def list_bases(
        self,
        space_id: Optional[str] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get Base list"""
        params = {}
        if space_id:
            params["spaceId"] = space_id
        if take:
            params["take"] = take
        if skip:
            params["skip"] = skip

        if space_id:
            response = self._request("GET", f"/space/{space_id}/base", params=params)
        else:
            response = self._request("GET", "/base", params=params)

        response.raise_for_status()
        return response.json()

    # ==================== Create Base ====================

    def create_base(
        self,
        space_id: str,
        name: str,
        icon: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create Base"""
        payload = {
            "spaceId": space_id,
            "name": name
        }
        if icon:
            payload["icon"] = icon

        response = self._request("POST", "/base", json=payload)
        response.raise_for_status()
        return response.json()

    # ==================== Update Base ====================

    def update_base(
        self,
        base_id: str,
        name: Optional[str] = None,
        icon: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update Base"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if icon is not None:
            payload["icon"] = icon

        response = self._request("PATCH", f"/base/{base_id}", json=payload)
        response.raise_for_status()
        return response.json()

    # ==================== Delete Base ====================

    def delete_base(self, base_id: str, permanent: bool = False) -> bool:
        """Delete Base"""
        endpoint = f"/base/{base_id}/permanent" if permanent else f"/base/{base_id}"
        response = self._request("DELETE", endpoint)
        response.raise_for_status()
        return response.status_code == 200

    # ==================== Duplicate Base ====================

    def duplicate_base(
        self,
        base_id: str,
        space_id: Optional[str] = None,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Duplicate Base"""
        payload = {}
        if space_id:
            payload["spaceId"] = space_id
        if name:
            payload["name"] = name

        response = self._request("POST", f"/base/{base_id}/duplicate", json=payload)
        response.raise_for_status()
        return response.json()

    # ==================== Export Base ====================

    def export_base(self, base_id: str, include_data: bool = True) -> bytes:
        """
        Export Base
        
        Note: Export data is returned as bytes for caller to handle safely.
        """
        params = {"includeData": str(include_data).lower()}
        response = self._request("GET", f"/base/{base_id}/export", params=params)
        response.raise_for_status()
        return response.content

    # ==================== Collaborators ====================

    def get_collaborators(self, base_id: str) -> List[Dict[str, Any]]:
        """Get Base collaborators list"""
        response = self._request("GET", f"/base/{base_id}/collaborators")
        response.raise_for_status()
        return response.json()

    def add_collaborator(
        self,
        base_id: str,
        user_id: str,
        role: str
    ) -> Dict[str, Any]:
        """Add collaborator"""
        payload = {
            "userId": user_id,
            "role": role
        }
        response = self._request("POST", f"/base/{base_id}/collaborator", json=payload)
        response.raise_for_status()
        return response.json()

    def update_collaborator(
        self,
        base_id: str,
        user_id: str,
        role: str
    ) -> Dict[str, Any]:
        """Update collaborator permissions"""
        payload = {"role": role}
        response = self._request("PATCH", f"/base/{base_id}/collaborators/{user_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def remove_collaborator(self, base_id: str, user_id: str) -> bool:
        """Remove collaborator"""
        response = self._request("DELETE", f"/base/{base_id}/collaborators/{user_id}")
        response.raise_for_status()
        return response.status_code == 200

    # ==================== Invitation Links ====================

    def create_invitation_link(
        self,
        base_id: str,
        role: str,
        expires_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create invitation link"""
        payload = {"role": role}
        if expires_time:
            payload["expiresTime"] = expires_time

        response = self._request("POST", f"/base/{base_id}/invitationLink", json=payload)
        response.raise_for_status()
        return response.json()

    def get_invitation_links(self, base_id: str) -> List[Dict[str, Any]]:
        """Get invitation link list"""
        response = self._request("GET", f"/base/{base_id}/invitationLink")
        response.raise_for_status()
        return response.json()

    def delete_invitation_link(self, base_id: str, link_id: str) -> bool:
        """Delete invitation link"""
        response = self._request("DELETE", f"/base/{base_id}/invitationLink/{link_id}")
        response.raise_for_status()
        return response.status_code == 200

    # ==================== Permissions ====================

    def get_permission(self, base_id: str) -> Dict[str, Any]:
        """Get Base permissions"""
        response = self._request("GET", f"/base/{base_id}/permission")
        response.raise_for_status()
        return response.json()

    # ==================== ERD ====================

    def get_erd(self, base_id: str) -> Dict[str, Any]:
        """Get Base ERD (Entity Relationship Diagram)"""
        response = self._request("GET", f"/base/{base_id}/erd")
        response.raise_for_status()
        return response.json()


# ==================== CLI Interface ====================

def main():
    parser = argparse.ArgumentParser(description="Teable Base API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List bases")
    list_parser.add_argument("--space-id", help="Space ID")
    list_parser.add_argument("--take", type=int, help="Number of results")
    list_parser.add_argument("--skip", type=int, help="Skip count")

    # get command
    get_parser = subparsers.add_parser("get", help="Get Base details")
    get_parser.add_argument("--base-id", required=True, help="Base ID")

    # create command
    create_parser = subparsers.add_parser("create", help="Create Base")
    create_parser.add_argument("--space-id", required=True, help="Space ID")
    create_parser.add_argument("--name", required=True, help="Base name")
    create_parser.add_argument("--icon", help="Base icon")

    # update command
    update_parser = subparsers.add_parser("update", help="Update Base")
    update_parser.add_argument("--base-id", required=True, help="Base ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--icon", help="New icon")

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete Base")
    delete_parser.add_argument("--base-id", required=True, help="Base ID")
    delete_parser.add_argument("--permanent", action="store_true", help="Permanent delete")

    # duplicate command
    dup_parser = subparsers.add_parser("duplicate", help="Duplicate Base")
    dup_parser.add_argument("--base-id", required=True, help="Base ID to duplicate")
    dup_parser.add_argument("--space-id", help="Target Space ID")
    dup_parser.add_argument("--name", help="New Base name")

    # export command
    export_parser = subparsers.add_parser("export", help="Export Base")
    export_parser.add_argument("--base-id", required=True, help="Base ID")
    export_parser.add_argument("--output", "-o", required=True, 
                               help="Output file path (must be in current directory or subdirectory)")
    export_parser.add_argument("--no-data", action="store_true", help="Exclude data")

    # collaborators command
    collab_parser = subparsers.add_parser("collaborators", help="List collaborators")
    collab_parser.add_argument("--base-id", required=True, help="Base ID")

    # add-collaborator command
    add_collab_parser = subparsers.add_parser("add-collaborator", help="Add collaborator")
    add_collab_parser.add_argument("--base-id", required=True, help="Base ID")
    add_collab_parser.add_argument("--user-id", required=True, help="User ID")
    add_collab_parser.add_argument("--role", required=True,
                                   choices=["owner", "creator", "editor", "commenter", "viewer"])

    # remove-collaborator command
    remove_collab_parser = subparsers.add_parser("remove-collaborator", help="Remove collaborator")
    remove_collab_parser.add_argument("--base-id", required=True, help="Base ID")
    remove_collab_parser.add_argument("--user-id", required=True, help="User ID")

    # invitation-link command
    invite_parser = subparsers.add_parser("invitation-link", help="Create invitation link")
    invite_parser.add_argument("--base-id", required=True, help="Base ID")
    invite_parser.add_argument("--role", required=True,
                               choices=["owner", "creator", "editor", "commenter", "viewer"])

    # erd command
    erd_parser = subparsers.add_parser("erd", help="Get ERD")
    erd_parser.add_argument("--base-id", required=True, help="Base ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = TeableBaseClient()

        if args.command == "list":
            result = client.list_bases(
                space_id=args.space_id,
                take=args.take,
                skip=args.skip
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "get":
            result = client.get_base(args.base_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "create":
            result = client.create_base(
                space_id=args.space_id,
                name=args.name,
                icon=args.icon
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "update":
            result = client.update_base(
                base_id=args.base_id,
                name=args.name,
                icon=args.icon
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "delete":
            success = client.delete_base(args.base_id, permanent=args.permanent)
            print(f"Deletion {'successful' if success else 'failed'}")

        elif args.command == "duplicate":
            result = client.duplicate_base(
                base_id=args.base_id,
                space_id=args.space_id,
                name=args.name
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "export":
            data = client.export_base(args.base_id, include_data=not args.no_data)
            # Validate output path for security
            safe_path = validate_output_path(args.output)
            with open(safe_path, "wb") as f:
                f.write(data)
            print(f"Exported to {safe_path}")

        elif args.command == "collaborators":
            result = client.get_collaborators(args.base_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "add-collaborator":
            result = client.add_collaborator(args.base_id, args.user_id, args.role)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "remove-collaborator":
            success = client.remove_collaborator(args.base_id, args.user_id)
            print(f"Removal {'successful' if success else 'failed'}")

        elif args.command == "invitation-link":
            result = client.create_invitation_link(args.base_id, args.role)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "erd":
            result = client.get_erd(args.base_id)
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