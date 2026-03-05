#!/usr/bin/env python3
"""
Teable Record API Client
Complete CRUD management for Teable records with security validations
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
ALLOWED_SCHEMES = ["https", "http"]  # Only allow HTTP/HTTPS


def validate_url(url: str) -> str:
    """
    Validate and sanitize URL to prevent SSRF and credential exfiltration.
    
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
        
        # Only allow HTTP/HTTPS schemes
        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            raise ValueError(
                f"Invalid URL scheme: '{parsed.scheme}'. "
                f"Only {ALLOWED_SCHEMES} are allowed for security reasons."
            )
        
        # Ensure there's a netloc (domain)
        if not parsed.netloc:
            raise ValueError(f"Invalid URL: missing domain in '{url}'")
        
        # Warn if using HTTP instead of HTTPS
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
        base_dir: Base directory to restrict output (defaults to current working directory)
        
    Returns:
        Absolute path if valid
        
    Raises:
        ValueError: If path attempts directory traversal
    """
    if not path:
        raise ValueError("Output path cannot be empty")
    
    # Use current working directory as base if not specified
    if base_dir is None:
        base_dir = os.getcwd()
    
    # Resolve to absolute paths
    abs_base = os.path.abspath(base_dir)
    abs_path = os.path.abspath(path)
    
    # Check for path traversal
    if not abs_path.startswith(abs_base):
        raise ValueError(
            f"Security error: Output path '{path}' is outside the allowed directory. "
            f"Files can only be written to '{abs_base}' or its subdirectories."
        )
    
    return abs_path


class TeableRecordClient:
    """Teable Record API Client with security validations"""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize client with security validations.
        
        Args:
            base_url: Teable instance URL (validated for security)
            api_key: Teable API Token
            
        Raises:
            ValueError: If URL is invalid or API key is missing
        """
        # Priority: parameter > TEABLE_URL env > default official API
        raw_url = base_url or os.getenv("TEABLE_URL") or DEFAULT_BASE_URL
        
        # Validate URL for security
        self.base_url = validate_url(raw_url)
        self.api_key = api_key or os.getenv("TEABLE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Teable API Key is not set! Please set TEABLE_API_KEY environment variable.\n"
                "Usage:\n"
                '  export TEABLE_API_KEY="your_token_here"\n'
                "Or pass it in code:\n"
                '  client = TeableRecordClient(api_key="your_token_here")'
            )

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Send HTTP request with validated URL"""
        url = urljoin(self.base_url + API_PREFIX, path.lstrip("/"))
        response = self.session.request(method, url, **kwargs)
        return response

    # ==================== Read Records ====================

    def list_records(
        self,
        table_id: str,
        view_id: Optional[str] = None,
        take: Optional[int] = None,
        skip: Optional[int] = None,
        field_key_type: str = "name",
        cell_format: str = "json",
        projection: Optional[List[str]] = None,
        order_by: Optional[List[Dict[str, Any]]] = None,
        filter_cond: Optional[Dict[str, Any]] = None,
        group_by: Optional[List[Dict[str, Any]]] = None,
        ignore_view_query: bool = False
    ) -> Dict[str, Any]:
        """Get list of records"""
        params = {
            "fieldKeyType": field_key_type,
            "cellFormat": cell_format,
            "ignoreViewQuery": str(ignore_view_query).lower()
        }

        if view_id:
            params["viewId"] = view_id
        if take:
            params["take"] = min(take, 1000)
        if skip:
            params["skip"] = skip
        if projection:
            params["projection"] = projection
        if order_by:
            params["orderBy"] = json.dumps(order_by)
        if filter_cond:
            params["filter"] = json.dumps(filter_cond)
        if group_by:
            params["groupBy"] = json.dumps(group_by)

        response = self._request("GET", f"/table/{table_id}/record", params=params)
        response.raise_for_status()
        return response.json()

    def get_record(
        self,
        table_id: str,
        record_id: str,
        field_key_type: str = "name",
        cell_format: str = "json"
    ) -> Dict[str, Any]:
        """Get single record"""
        params = {
            "fieldKeyType": field_key_type,
            "cellFormat": cell_format
        }
        response = self._request("GET", f"/table/{table_id}/record/{record_id}", params=params)
        response.raise_for_status()
        return response.json()

    # ==================== Create Records ====================

    def create_records(
        self,
        table_id: str,
        records: List[Dict[str, Any]],
        field_key_type: str = "name",
        typecast: bool = False,
        order: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create one or more records"""
        payload = {
            "records": records,
            "fieldKeyType": field_key_type,
            "typecast": typecast
        }
        if order:
            payload["order"] = order

        response = self._request("POST", f"/table/{table_id}/record", json=payload)
        response.raise_for_status()
        return response.json()

    def create_record(
        self,
        table_id: str,
        fields: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Create single record (convenience method)"""
        result = self.create_records(table_id, [{"fields": fields}], **kwargs)
        return result["records"][0] if "records" in result else result

    # ==================== Update Records ====================

    def update_record(
        self,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any],
        field_key_type: str = "name",
        typecast: bool = False
    ) -> Dict[str, Any]:
        """Update single record"""
        payload = {
            "record": {"fields": fields},
            "fieldKeyType": field_key_type,
            "typecast": typecast
        }

        response = self._request("PATCH", f"/table/{table_id}/record/{record_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def update_records(
        self,
        table_id: str,
        records: List[Dict[str, Any]],
        field_key_type: str = "name",
        typecast: bool = False
    ) -> List[Dict[str, Any]]:
        """Batch update records"""
        payload = {
            "records": records,
            "fieldKeyType": field_key_type,
            "typecast": typecast
        }

        response = self._request("PUT", f"/table/{table_id}/record", json=payload)
        response.raise_for_status()
        return response.json().get("records", [])

    # ==================== Delete Records ====================

    def delete_records(
        self,
        table_id: str,
        record_ids: List[str]
    ) -> bool:
        """Batch delete records"""
        params = {"recordIds": record_ids}
        response = self._request("DELETE", f"/table/{table_id}/record", params=params)
        response.raise_for_status()
        return response.status_code == 200

    def delete_record(
        self,
        table_id: str,
        record_id: str
    ) -> bool:
        """Delete single record"""
        return self.delete_records(table_id, [record_id])

    # ==================== Duplicate Record ====================

    def duplicate_record(
        self,
        table_id: str,
        record_id: str,
        order: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Duplicate record"""
        payload = {}
        if order:
            payload["order"] = order

        response = self._request("POST", f"/table/{table_id}/record/{record_id}/duplicate", json=payload)
        response.raise_for_status()
        return response.json()

    # ==================== Record History ====================

    def get_record_history(
        self,
        table_id: str,
        record_id: str,
        take: Optional[int] = None,
        skip: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get record change history"""
        params = {}
        if take:
            params["take"] = take
        if skip:
            params["skip"] = skip

        response = self._request("GET", f"/table/{table_id}/record/{record_id}/history", params=params)
        response.raise_for_status()
        return response.json()


# ==================== CLI Interface ====================

def main():
    parser = argparse.ArgumentParser(
        description="Teable Record API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    list_parser = subparsers.add_parser("list", help="List records")
    list_parser.add_argument("--table-id", required=True, help="Table ID")
    list_parser.add_argument("--view-id", help="View ID")
    list_parser.add_argument("--take", type=int, help="Number of records (max 1000)")
    list_parser.add_argument("--skip", type=int, help="Skip count")
    list_parser.add_argument("--field-key-type", default="name", choices=["name", "id", "dbFieldName"])
    list_parser.add_argument("--cell-format", default="json", choices=["json", "text"])
    list_parser.add_argument("--projection", help="Specific fields only (comma-separated)")
    list_parser.add_argument("--output", "-o", help="Output file path (must be in current directory or subdirectory)")

    # get command
    get_parser = subparsers.add_parser("get", help="Get single record")
    get_parser.add_argument("--table-id", required=True, help="Table ID")
    get_parser.add_argument("--record-id", required=True, help="Record ID")
    get_parser.add_argument("--field-key-type", default="name", choices=["name", "id", "dbFieldName"])
    get_parser.add_argument("--cell-format", default="json", choices=["json", "text"])

    # create command
    create_parser = subparsers.add_parser("create", help="Create record")
    create_parser.add_argument("--table-id", required=True, help="Table ID")
    create_parser.add_argument("--fields", required=True, help="Field values (JSON format)")
    create_parser.add_argument("--typecast", action="store_true", help="Auto type conversion")

    # update command
    update_parser = subparsers.add_parser("update", help="Update record")
    update_parser.add_argument("--table-id", required=True, help="Table ID")
    update_parser.add_argument("--record-id", required=True, help="Record ID")
    update_parser.add_argument("--fields", required=True, help="Field values (JSON format)")
    update_parser.add_argument("--typecast", action="store_true", help="Auto type conversion")

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete records")
    delete_parser.add_argument("--table-id", required=True, help="Table ID")
    delete_parser.add_argument("--record-ids", required=True, help="Record ID list (JSON array)")

    # duplicate command
    dup_parser = subparsers.add_parser("duplicate", help="Duplicate record")
    dup_parser.add_argument("--table-id", required=True, help="Table ID")
    dup_parser.add_argument("--record-id", required=True, help="Record ID to duplicate")

    # history command
    hist_parser = subparsers.add_parser("history", help="Get record history")
    hist_parser.add_argument("--table-id", required=True, help="Table ID")
    hist_parser.add_argument("--record-id", required=True, help="Record ID")
    hist_parser.add_argument("--take", type=int, help="Number of results")
    hist_parser.add_argument("--skip", type=int, help="Skip count")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = TeableRecordClient()

        if args.command == "list":
            result = client.list_records(
                table_id=args.table_id,
                view_id=args.view_id,
                take=args.take,
                skip=args.skip,
                field_key_type=args.field_key_type,
                cell_format=args.cell_format,
                projection=args.projection.split(",") if args.projection else None
            )
            output = json.dumps(result, indent=2, ensure_ascii=False)
            
            if args.output:
                # Validate output path for security
                safe_path = validate_output_path(args.output)
                with open(safe_path, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"Saved to {safe_path}")
            else:
                print(output)

        elif args.command == "get":
            result = client.get_record(
                table_id=args.table_id,
                record_id=args.record_id,
                field_key_type=args.field_key_type,
                cell_format=args.cell_format
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "create":
            fields = json.loads(args.fields)
            result = client.create_record(
                table_id=args.table_id,
                fields=fields,
                typecast=args.typecast
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "update":
            fields = json.loads(args.fields)
            result = client.update_record(
                table_id=args.table_id,
                record_id=args.record_id,
                fields=fields,
                typecast=args.typecast
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "delete":
            record_ids = json.loads(args.record_ids)
            success = client.delete_records(args.table_id, record_ids)
            print(f"Deletion {'successful' if success else 'failed'}")

        elif args.command == "duplicate":
            result = client.duplicate_record(
                table_id=args.table_id,
                record_id=args.record_id
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "history":
            result = client.get_record_history(
                table_id=args.table_id,
                record_id=args.record_id,
                take=args.take,
                skip=args.skip
            )
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