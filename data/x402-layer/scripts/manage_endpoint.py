#!/usr/bin/env python3
"""
x402 Endpoint Management

Manage agentic endpoints created via worker API.

Usage:
    python manage_endpoint.py list [slug ...]
    python manage_endpoint.py info <slug>
    python manage_endpoint.py stats <slug>
    python manage_endpoint.py update <slug> --price 0.02
    python manage_endpoint.py delete <slug>

Notes:
- Public worker API supports info/stats/topup/delete for agent endpoints.
- Price/name/origin updates are not exposed on /agent/endpoints today.
"""

import argparse
import json
import os
import sys
from typing import List, Optional

import requests

API_BASE = "https://api.x402layer.cc"


def _load_api_key(optional: bool = True) -> Optional[str]:
    api_key = os.getenv("X_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
            api_key = os.getenv("X_API_KEY") or os.getenv("API_KEY")
        except Exception:
            pass

    if not optional and not api_key:
        raise ValueError("Set X_API_KEY (or API_KEY) environment variable")
    return api_key


def _build_headers(api_key: Optional[str] = None) -> dict:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    return headers


def get_endpoint_info(slug: str, api_key: Optional[str] = None) -> dict:
    response = requests.get(
        f"{API_BASE}/agent/endpoints",
        params={"slug": slug},
        headers=_build_headers(api_key),
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()
    return {"error": f"Status {response.status_code}", "response": response.text}


def list_endpoints(slugs: Optional[List[str]] = None, api_key: Optional[str] = None) -> dict:
    """
    Worker API has no owner-wide list route.
    We support listing known slugs from args or ENDPOINT_SLUGS env.
    """
    resolved_slugs = list(slugs or [])

    if not resolved_slugs:
        env_slugs = os.getenv("ENDPOINT_SLUGS", "").strip()
        if env_slugs:
            resolved_slugs = [s.strip() for s in env_slugs.split(",") if s.strip()]

    if not resolved_slugs:
        return {
            "error": (
                "Worker API does not provide 'list all my endpoints' by wallet. "
                "Pass slugs explicitly (manage_endpoint.py list slug1 slug2) "
                "or set ENDPOINT_SLUGS=slug1,slug2"
            )
        }

    endpoints = []
    for slug in resolved_slugs:
        endpoints.append({"slug": slug, "details": get_endpoint_info(slug, api_key)})

    return {"endpoints": endpoints, "count": len(endpoints)}


def get_endpoint_stats(slug: str, api_key: Optional[str] = None) -> dict:
    """Get aggregate stats for an endpoint slug via endpoint id lookup."""
    details = get_endpoint_info(slug, api_key)
    endpoint = details.get("endpoint", {}) if isinstance(details, dict) else {}
    endpoint_id = endpoint.get("id")

    if not endpoint_id:
        return {
            "error": (
                "Could not resolve endpoint id for stats. "
                "Provide X_API_KEY/API_KEY so /agent/endpoints can return full details with id."
            ),
            "details": details,
        }

    response = requests.get(
        f"{API_BASE}/agent/endpoints",
        params={"action": "stats", "endpoint_ids": endpoint_id},
        headers={"Accept": "application/json"},
        timeout=30,
    )

    if response.status_code == 200:
        stats = response.json()
        return {
            "slug": slug,
            "endpoint_id": endpoint_id,
            "stats": stats,
        }

    return {"error": f"Status {response.status_code}", "response": response.text}


def update_endpoint(slug: str, price: float = None, name: str = None, origin_url: str = None) -> dict:
    """
    Keep command backward compatible, but current worker API does not expose PATCH updates.
    """
    updates = {}
    if price is not None:
        updates["price"] = price
    if name is not None:
        updates["name"] = name
    if origin_url is not None:
        updates["origin_url"] = origin_url

    if not updates:
        return {"error": "No updates specified"}

    return {
        "error": (
            "Update is not available on current /agent/endpoints API. "
            "Use Studio dashboard for endpoint edits, then use this script for info/stats/topup/listing."
        ),
        "requested_updates": updates,
        "slug": slug,
    }


def delete_endpoint(slug: str, api_key: Optional[str] = None) -> dict:
    """Delete endpoint via worker API."""
    if not api_key:
        return {
            "error": (
                "Delete requires endpoint API key. "
                "Set X_API_KEY/API_KEY before running delete."
            )
        }

    response = requests.delete(
        f"{API_BASE}/agent/endpoints",
        params={"slug": slug},
        headers=_build_headers(api_key),
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()
    return {"error": f"Status {response.status_code}", "response": response.text}


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage x402 agent endpoints")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    list_parser = subparsers.add_parser("list", help="List known endpoint slugs")
    list_parser.add_argument("slugs", nargs="*", help="Optional list of endpoint slugs")

    info_parser = subparsers.add_parser("info", help="Get endpoint info")
    info_parser.add_argument("slug", help="Endpoint slug")

    stats_parser = subparsers.add_parser("stats", help="Get endpoint statistics")
    stats_parser.add_argument("slug", help="Endpoint slug")

    update_parser = subparsers.add_parser("update", help="Update endpoint (not supported on current worker API)")
    update_parser.add_argument("slug", help="Endpoint slug")
    update_parser.add_argument("--price", type=float, help="New price in USD")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--origin-url", help="New origin URL")

    delete_parser = subparsers.add_parser("delete", help="Delete endpoint (requires API key)")
    delete_parser.add_argument("slug", help="Endpoint slug")

    args = parser.parse_args()
    api_key = _load_api_key(optional=True)

    if args.command == "list":
        result = list_endpoints(args.slugs, api_key)
    elif args.command == "info":
        result = get_endpoint_info(args.slug, api_key)
    elif args.command == "stats":
        result = get_endpoint_stats(args.slug, api_key)
    elif args.command == "update":
        result = update_endpoint(args.slug, args.price, args.name, getattr(args, "origin_url", None))
    elif args.command == "delete":
        result = delete_endpoint(args.slug, api_key)
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        sys.exit(1)
