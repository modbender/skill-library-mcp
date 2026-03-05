#!/usr/bin/env python3
"""
Attio Direct API Client for OpenClaw

Query any Attio data directly via REST API. Returns fresh data on every call.
No caching, no proxy server - just direct API access.

Usage:
    python3 attio_client.py <endpoint> [options]
    
Examples:
    python3 attio_client.py deals
    python3 attio_client.py companies
    python3 attio_client.py "deals?limit=50"
    python3 attio_client.py objects
"""

import sys
import os
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote

# Configuration - load from environment
import os

API_KEY = os.environ.get("ATTIO_API_KEY", "")
if not API_KEY:
    # Fallback: read from .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("ATTIO_API_KEY="):
                    API_KEY = line.split("=", 1)[1].strip().strip('"')
                    break

if not API_KEY:
    print(json.dumps({"error": "No API key found. Set ATTIO_API_KEY env var or create .env file"}))
    sys.exit(1)
BASE_URL = "https://api.attio.com/v2"

def make_request(endpoint: str, method: str = "GET", data: dict = None, timeout: int = 60) -> dict:
    """Make request to Attio API with proper headers and timeout."""
    
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    request = Request(url, headers=headers, method=method)
    
    if data:
        request.data = json.dumps(data).encode("utf-8")
    
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            if body:
                return json.loads(body)
            return {"success": True}
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else "{}"
        try:
            error_json = json.loads(error_body)
            return {"error": f"HTTP {e.code}", "details": error_json}
        except:
            return {"error": f"HTTP {e.code}", "message": error_body}
    except URLError as e:
        return {"error": "Connection failed", "message": str(e.reason)}
    except Exception as e:
        return {"error": str(type(e).__name__), "message": str(e)}


def list_objects():
    """List all available objects in Attio."""
    return make_request("/objects")


def query_records(object_slug: str, limit: int = 100, offset: int = 0):
    """Query records for a specific object."""
    payload = {
        "limit": limit,
        "offset": offset
    }
    return make_request(f"/objects/{object_slug}/records/query", method="POST", data=payload)


def get_record(object_slug: str, record_id: str):
    """Get a single record by ID."""
    return make_request(f"/objects/{object_slug}/records/{record_id}")


def list_deals(limit: int = 100):
    """List all deals."""
    return query_records("deals", limit=limit)


def list_companies(limit: int = 100):
    """List all companies."""
    return query_records("companies", limit=limit)


def list_people(limit: int = 100):
    """List all people/contacts."""
    return query_records("people", limit=limit)


def list_tasks(limit: int = 100):
    """List all tasks."""
    return make_request(f"/tasks?limit={limit}")


def get_pipeline():
    """Get pipeline stages."""
    return make_request("/pipelines")


# ============ CRUD Operations ============

def create_record(object_slug: str, attributes: dict):
    """Create a new record in Attio.
    
    Args:
        object_slug: e.g., 'companies', 'people'
        attributes: dict of {field_name: value}
    
    Example:
        create_record('companies', {'name': 'Acme Corp', 'domain': 'acme.com'})
    """
    # Format attributes as Attio expects: {"field": [{"value": "..."}]}
    values = {}
    for key, val in attributes.items():
        values[key] = [{"value": val}]
    
    payload = {
        "data": {
            "values": values
        }
    }
    return make_request(f"/objects/{object_slug}/records", method="POST", data=payload)


def update_record(object_slug: str, record_id: str, attributes: dict):
    """Update an existing record in Attio.
    
    Args:
        object_slug: e.g., 'companies', 'people'
        record_id: The record ID
        attributes: dict of {field_name: new_value}
    
    Example:
        update_record('companies', 'abc123', {'name': 'New Name', 'funnel_stage': 'Nurture'})
    """
    payload = {
        "data": {
            "attributes": attributes
        }
    }
    return make_request(f"/objects/{object_slug}/records/{record_id}", method="PUT", data=payload)


def delete_record(object_slug: str, record_id: str):
    """Delete a record from Attio.
    
    Args:
        object_slug: e.g., 'companies', 'people'
        record_id: The record ID to delete
    """
    return make_request(f"/objects/{object_slug}/records/{record_id}", method="DELETE")


def add_note(parent_object: str, parent_record_id: str, title: str, content: str):
    """Add a note to a company or person.
    
    Args:
        parent_object: 'companies' or 'people'
        parent_record_id: The record ID
        title: Note title
        content: Note body
    """
    payload = {
        "data": {
            "parent_object": parent_object,
            "parent_record_id": parent_record_id,
            "title": title,
            "content": content,
            "format": "plaintext"
        }
    }
    return make_request("/notes", method="POST", data=payload)


def main():
    parser = argparse.ArgumentParser(description="Attio Direct API Client")
    parser.add_argument("endpoint", help="API endpoint to query (e.g., deals, companies, people)")
    parser.add_argument("--limit", type=int, default=5000, help="Limit results (default: 5000)")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    parser.add_argument("--raw", action="store_true", help="Return raw endpoint path")
    parser.add_argument("--method", default="GET", help="HTTP method")
    parser.add_argument("--all", action="store_true", help="Fetch all records (auto-paginate)")
    parser.add_argument("--create", action="store_true", help="Create a new record (use with --data)")
    parser.add_argument("--update", action="store_true", help="Update a record (use with --id and --data)")
    parser.add_argument("--delete", action="store_true", help="Delete a record (use with --id)")
    parser.add_argument("--id", help="Record ID for update/delete operations")
    parser.add_argument("--data", help="JSON data for create/update operations")
    parser.add_argument("--note", help="Add note: 'title|content' or just content for quick notes")
    
    args = parser.parse_args()
    
    endpoint = args.endpoint
    
    # Handle common shortcuts with auto-pagination
    if args.all:
        # Auto-paginate to get all records
        all_records = []
        batch_size = 1000
        offset = 0
        
        if endpoint in ["deals", "deal"]:
            fetch_func = list_deals
        elif endpoint in ["companies", "company"]:
            fetch_func = list_companies
        elif endpoint in ["people", "person", "contacts"]:
            fetch_func = list_people
        else:
            fetch_func = lambda lim: query_records(endpoint, limit=lim)
        
        while True:
            result = fetch_func(limit=batch_size)
            if "error" in result:
                print(json.dumps(result, indent=2))
                sys.exit(1)
            
            records = result.get("data", [])
            all_records.extend(records)
            
            if len(records) < batch_size:
                break
            offset += batch_size
            print(f"Fetched {len(all_records)}...", file=sys.stderr)
        
        print(json.dumps({"data": all_records}, indent=2))
        sys.exit(0)
    
    # Handle CRUD operations
    if args.create or args.update or args.delete:
        # Parse data if provided
        attributes = {}
        if args.data:
            try:
                attributes = json.loads(args.data)
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON in --data"}))
                sys.exit(1)
        
        if args.create:
            # Create: endpoint is the object type (companies, people)
            result = create_record(endpoint, attributes)
        elif args.update and args.id:
            # Update: endpoint is object type, args.id is record ID
            result = update_record(endpoint, args.id, attributes)
        elif args.delete and args.id:
            # Delete: endpoint is object type, args.id is record ID
            result = delete_record(endpoint, args.id)
        else:
            result = {"error": "Missing required argument. Use --id for update/delete"}
        
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    # Handle note addition
    if args.note:
        if not args.id:
            print(json.dumps({"error": "Need --id for the company/person record"}))
            sys.exit(1)
        
        # Parse: title|content or just content
        if '|' in args.note:
            title, content = args.note.split('|', 1)
        else:
            title = "Quick Note"
            content = args.note
        
        result = add_note(endpoint, args.id, title, content)
        print(json.dumps(result, indent=2))
        sys.exit(0)
    
    # Handle common shortcuts
    if endpoint in ["deals", "deal"]:
        result = list_deals(args.limit)
    elif endpoint in ["companies", "company"]:
        result = list_companies(args.limit)
    elif endpoint in ["people", "person", "contacts"]:
        result = list_people(args.limit)
    elif endpoint in ["tasks", "task"]:
        result = list_tasks(args.limit)
    elif endpoint == "objects":
        result = list_objects()
    elif endpoint == "pipeline":
        result = get_pipeline()
    elif args.raw:
        # Raw endpoint with query params
        result = make_request(endpoint)
    else:
        # Try as object/records/query
        result = query_records(endpoint, limit=args.limit, offset=args.offset)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
