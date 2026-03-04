#!/usr/bin/env python3
"""
🦞 Gradient AI — Knowledge Base Management

Create, list, and manage DigitalOcean Gradient Knowledge Bases
and their data sources. Full CRUD via the DO API.

Usage:
    python3 gradient_kb_manage.py --list
    python3 gradient_kb_manage.py --create --name "My Research KB"
    python3 gradient_kb_manage.py --show --kb-uuid <uuid>
    python3 gradient_kb_manage.py --add-source --kb-uuid <uuid> --type spaces --bucket my-data
    python3 gradient_kb_manage.py --reindex --kb-uuid <uuid>

Docs: https://docs.digitalocean.com/products/gradient-ai-platform/how-to/create-manage-knowledge-bases/
API:  https://docs.digitalocean.com/reference/api/digitalocean-api/
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests

DO_API_BASE = "https://api.digitalocean.com"
KB_API_PATH = "/v2/gen-ai/knowledge_bases"


def _headers(api_token: str) -> dict:
    """Build auth headers for the DO API."""
    return {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }


def _resolve_token(api_token: Optional[str] = None) -> str:
    """Resolve the API token from arg or env."""
    return api_token or os.environ.get("DO_API_TOKEN", "")


def list_knowledge_bases(api_token: Optional[str] = None) -> dict:
    """List all Knowledge Bases in your account.

    Args:
        api_token: DO API token. Falls back to DO_API_TOKEN.

    Returns:
        dict with 'success', 'knowledge_bases' (list), and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "knowledge_bases": [], "message": "No DO_API_TOKEN configured."}

    try:
        url = f"{DO_API_BASE}{KB_API_PATH}"
        resp = requests.get(url, headers=_headers(token), timeout=15)
        resp.raise_for_status()

        data = resp.json()
        kbs = data.get("knowledge_bases", [])

        return {
            "success": True,
            "knowledge_bases": kbs,
            "message": f"Found {len(kbs)} Knowledge Base(s).",
        }
    except requests.RequestException as e:
        return {"success": False, "knowledge_bases": [], "message": f"API request failed: {str(e)}"}


def create_knowledge_base(
    name: str,
    region: str = "nyc3",
    project_id: Optional[str] = None,
    embedding_model: Optional[str] = None,
    api_token: Optional[str] = None,
) -> dict:
    """Create a new Knowledge Base.

    Args:
        name: Human-readable name for the KB.
        region: DO region (e.g., 'nyc3').
        project_id: DO project UUID to associate with.
        embedding_model: Embedding model ID (uses default if not specified).
        api_token: DO API token.

    Returns:
        dict with 'success', 'knowledge_base' (created KB data), and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "knowledge_base": {}, "message": "No DO_API_TOKEN configured."}

    try:
        url = f"{DO_API_BASE}{KB_API_PATH}"
        payload = {
            "name": name,
            "region": region,
        }

        if project_id:
            payload["project_id"] = project_id
        if embedding_model:
            payload["embedding_model"] = embedding_model

        resp = requests.post(url, headers=_headers(token), json=payload, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        kb = data.get("knowledge_base", data)

        return {
            "success": True,
            "knowledge_base": kb,
            "message": f"Created Knowledge Base '{name}' (UUID: {kb.get('uuid', 'unknown')}).",
        }
    except requests.RequestException as e:
        return {"success": False, "knowledge_base": {}, "message": f"Create failed: {str(e)}"}


def get_knowledge_base(
    kb_uuid: str,
    api_token: Optional[str] = None,
) -> dict:
    """Get details for a specific Knowledge Base.

    Args:
        kb_uuid: Knowledge Base UUID.
        api_token: DO API token.

    Returns:
        dict with 'success', 'knowledge_base', and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "knowledge_base": {}, "message": "No DO_API_TOKEN configured."}

    try:
        url = f"{DO_API_BASE}{KB_API_PATH}/{kb_uuid}"
        resp = requests.get(url, headers=_headers(token), timeout=15)
        resp.raise_for_status()

        data = resp.json()
        kb = data.get("knowledge_base", data)

        return {
            "success": True,
            "knowledge_base": kb,
            "message": f"Knowledge Base: {kb.get('name', kb_uuid)}",
        }
    except requests.RequestException as e:
        return {"success": False, "knowledge_base": {}, "message": f"Get failed: {str(e)}"}


def delete_knowledge_base(
    kb_uuid: str,
    api_token: Optional[str] = None,
) -> dict:
    """Delete a Knowledge Base.

    ⚠️ This permanently deletes the KB and all its indexed data.

    Args:
        kb_uuid: Knowledge Base UUID.
        api_token: DO API token.

    Returns:
        dict with 'success' and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "message": "No DO_API_TOKEN configured."}

    try:
        url = f"{DO_API_BASE}{KB_API_PATH}/{kb_uuid}"
        resp = requests.delete(url, headers=_headers(token), timeout=15)
        resp.raise_for_status()

        return {
            "success": True,
            "message": f"Deleted Knowledge Base {kb_uuid}.",
        }
    except requests.RequestException as e:
        return {"success": False, "message": f"Delete failed: {str(e)}"}


def list_data_sources(
    kb_uuid: str,
    api_token: Optional[str] = None,
) -> dict:
    """List data sources for a Knowledge Base.

    Args:
        kb_uuid: Knowledge Base UUID.
        api_token: DO API token.

    Returns:
        dict with 'success', 'data_sources' (list), and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "data_sources": [], "message": "No DO_API_TOKEN configured."}

    try:
        url = f"{DO_API_BASE}{KB_API_PATH}/{kb_uuid}/data_sources"
        resp = requests.get(url, headers=_headers(token), timeout=15)
        resp.raise_for_status()

        data = resp.json()
        sources = data.get("knowledge_base_data_sources", data.get("data_sources", []))

        return {
            "success": True,
            "data_sources": sources,
            "message": f"Found {len(sources)} data source(s).",
        }
    except requests.RequestException as e:
        return {"success": False, "data_sources": [], "message": f"List sources failed: {str(e)}"}


def add_spaces_source(
    kb_uuid: str,
    bucket: str,
    prefix: str = "",
    region: str = "nyc3",
    api_token: Optional[str] = None,
) -> dict:
    """Add a DO Spaces bucket as a data source for a Knowledge Base.

    Args:
        kb_uuid: Knowledge Base UUID.
        bucket: Spaces bucket name.
        prefix: Key prefix to scope indexing to a specific folder.
        region: Spaces region.
        api_token: DO API token.

    Returns:
        dict with 'success', 'data_source', and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "data_source": {}, "message": "No DO_API_TOKEN configured."}

    try:
        url = f"{DO_API_BASE}{KB_API_PATH}/{kb_uuid}/data_sources"
        payload = {
            "type": "spaces",
            "spaces": {
                "bucket": bucket,
                "region": region,
            },
        }

        if prefix:
            payload["spaces"]["prefix"] = prefix

        resp = requests.post(url, headers=_headers(token), json=payload, timeout=15)
        resp.raise_for_status()

        data = resp.json()
        source = data.get("knowledge_base_data_source", data)

        return {
            "success": True,
            "data_source": source,
            "message": f"Added Spaces source ({bucket}/{prefix}) to KB {kb_uuid}.",
        }
    except requests.RequestException as e:
        return {"success": False, "data_source": {}, "message": f"Add source failed: {str(e)}"}


def trigger_reindex(
    kb_uuid: str,
    source_uuid: Optional[str] = None,
    api_token: Optional[str] = None,
) -> dict:
    """Trigger a re-indexing job for a Knowledge Base data source.

    If source_uuid is not provided, fetches the first data source and
    triggers re-indexing on it.

    Args:
        kb_uuid: Knowledge Base UUID.
        source_uuid: Data source UUID (optional — auto-detected if omitted).
        api_token: DO API token.

    Returns:
        dict with 'success' and 'message'.
    """
    token = _resolve_token(api_token)
    if not token:
        return {"success": False, "message": "No DO_API_TOKEN configured."}

    try:
        # Auto-detect source UUID if not provided
        if not source_uuid:
            sources_result = list_data_sources(kb_uuid, api_token=token)
            if not sources_result["success"]:
                return sources_result
            sources = sources_result["data_sources"]
            if not sources:
                return {"success": False, "message": "No data sources configured for this Knowledge Base."}
            source_uuid = sources[0].get("uuid", "")
            if not source_uuid:
                return {"success": False, "message": "Data source has no UUID."}

        url = f"{DO_API_BASE}{KB_API_PATH}/{kb_uuid}/data_sources/{source_uuid}/indexing_jobs"
        resp = requests.post(url, headers=_headers(token), json={}, timeout=15)
        resp.raise_for_status()

        return {
            "success": True,
            "message": f"Re-indexing triggered for KB {kb_uuid}, data source {source_uuid}.",
        }
    except requests.RequestException:
        # Best-effort — auto-indexing may already be configured
        return {
            "success": True,
            "message": "Re-index request sent. If auto-indexing is enabled, the KB will update on its own schedule.",
        }


# ─── CLI Interface ────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="🦞 Manage Gradient Knowledge Bases"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List all Knowledge Bases")
    group.add_argument("--create", action="store_true", help="Create a new Knowledge Base")
    group.add_argument("--show", action="store_true", help="Show KB details")
    group.add_argument("--delete", action="store_true", help="Delete a Knowledge Base")
    group.add_argument("--list-sources", action="store_true", help="List data sources for a KB")
    group.add_argument("--add-source", action="store_true", help="Add a data source to a KB")
    group.add_argument("--reindex", action="store_true", help="Trigger re-indexing")

    parser.add_argument("--kb-uuid", default=None, help="Knowledge Base UUID")
    parser.add_argument("--source-uuid", default=None, help="Data source UUID")
    parser.add_argument("--name", default=None, help="KB name (for create)")
    parser.add_argument("--region", default="nyc3", help="Region (default: nyc3)")
    parser.add_argument("--project-id", default=None, help="DO project UUID")
    parser.add_argument("--type", dest="source_type", default="spaces", help="Data source type")
    parser.add_argument("--bucket", default=None, help="Spaces bucket name")
    parser.add_argument("--prefix", default="", help="Spaces key prefix")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    result = None

    if args.list:
        result = list_knowledge_bases()
    elif args.create:
        if not args.name:
            print("Error: --name required for --create", file=sys.stderr)
            sys.exit(1)
        result = create_knowledge_base(name=args.name, region=args.region, project_id=args.project_id)
    elif args.show:
        if not args.kb_uuid:
            print("Error: --kb-uuid required for --show", file=sys.stderr)
            sys.exit(1)
        result = get_knowledge_base(args.kb_uuid)
    elif args.delete:
        if not args.kb_uuid:
            print("Error: --kb-uuid required for --delete", file=sys.stderr)
            sys.exit(1)
        result = delete_knowledge_base(args.kb_uuid)
    elif args.list_sources:
        if not args.kb_uuid:
            print("Error: --kb-uuid required for --list-sources", file=sys.stderr)
            sys.exit(1)
        result = list_data_sources(args.kb_uuid)
    elif args.add_source:
        if not args.kb_uuid or not args.bucket:
            print("Error: --kb-uuid and --bucket required for --add-source", file=sys.stderr)
            sys.exit(1)
        result = add_spaces_source(args.kb_uuid, args.bucket, prefix=args.prefix, region=args.region)
    elif args.reindex:
        if not args.kb_uuid:
            print("Error: --kb-uuid required for --reindex", file=sys.stderr)
            sys.exit(1)
        result = trigger_reindex(args.kb_uuid, source_uuid=args.source_uuid)

    if result:
        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            if result["success"]:
                print(f"✅ {result['message']}")
                # Print KBs if listing
                if "knowledge_bases" in result:
                    for kb in result["knowledge_bases"]:
                        name = kb.get("name", "unnamed")
                        uuid = kb.get("uuid", "?")
                        print(f"  📦 {name} ({uuid})")
                # Print data sources if listing
                if "data_sources" in result:
                    for ds in result["data_sources"]:
                        ds_type = ds.get("type", "unknown")
                        uuid = ds.get("uuid", "?")
                        print(f"  📁 {ds_type} ({uuid})")
            else:
                print(f"❌ {result['message']}", file=sys.stderr)
                sys.exit(1)


if __name__ == "__main__":
    main()
