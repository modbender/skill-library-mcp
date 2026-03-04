#!/usr/bin/env python3
"""
Teable Dashboard API Client
Complete management for Teable dashboards with security validations
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


class TeableDashboardClient:
    """Teable Dashboard API Client with security validations"""

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

    def list_dashboards(self, base_id: str) -> List[Dict[str, Any]]:
        """Get Dashboard list"""
        response = self._request("GET", f"/base/{base_id}/dashboard")
        response.raise_for_status()
        return response.json()

    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Get Dashboard details"""
        response = self._request("GET", f"/dashboard/{dashboard_id}")
        response.raise_for_status()
        return response.json()

    def create_dashboard(self, base_id: str, name: str, layout: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Create Dashboard"""
        payload = {"baseId": base_id, "name": name}
        if layout:
            payload["layout"] = layout

        response = self._request("POST", f"/base/{base_id}/dashboard", json=payload)
        response.raise_for_status()
        return response.json()

    def update_dashboard(self, dashboard_id: str, name: Optional[str] = None,
                         layout: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Update Dashboard"""
        payload = {}
        if name is not None:
            payload["name"] = name
        if layout is not None:
            payload["layout"] = layout

        response = self._request("PATCH", f"/dashboard/{dashboard_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def rename_dashboard(self, dashboard_id: str, name: str) -> Dict[str, Any]:
        """Rename Dashboard"""
        return self.update_dashboard(dashboard_id, name=name)

    def update_dashboard_layout(self, dashboard_id: str, layout: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update Dashboard layout"""
        return self.update_dashboard(dashboard_id, layout=layout)

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete Dashboard"""
        response = self._request("DELETE", f"/dashboard/{dashboard_id}")
        response.raise_for_status()
        return response.status_code == 200

    def duplicate_dashboard(self, dashboard_id: str, base_id: Optional[str] = None,
                           name: Optional[str] = None) -> Dict[str, Any]:
        """Duplicate Dashboard"""
        payload = {}
        if base_id:
            payload["baseId"] = base_id
        if name:
            payload["name"] = name

        response = self._request("POST", f"/dashboard/{dashboard_id}/duplicate", json=payload)
        response.raise_for_status()
        return response.json()

    # ==================== Plugin Management ====================

    def install_plugin(self, dashboard_id: str, plugin_id: str, name: Optional[str] = None,
                      storage: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Install plugin to Dashboard"""
        payload = {"pluginId": plugin_id}
        if name:
            payload["name"] = name
        if storage:
            payload["storage"] = storage

        response = self._request("POST", f"/dashboard/{dashboard_id}/plugin", json=payload)
        response.raise_for_status()
        return response.json()

    def get_plugin(self, dashboard_id: str, plugin_install_id: str) -> Dict[str, Any]:
        """Get installed plugin details"""
        response = self._request("GET", f"/dashboard/{dashboard_id}/plugin/{plugin_install_id}")
        response.raise_for_status()
        return response.json()

    def list_plugins(self, dashboard_id: str) -> List[Dict[str, Any]]:
        """Get installed plugin list"""
        response = self._request("GET", f"/dashboard/{dashboard_id}/plugin")
        response.raise_for_status()
        return response.json()

    def rename_plugin(self, dashboard_id: str, plugin_install_id: str, name: str) -> Dict[str, Any]:
        """Rename installed plugin"""
        payload = {"name": name}
        response = self._request("PATCH", f"/dashboard/{dashboard_id}/plugin/{plugin_install_id}/rename", json=payload)
        response.raise_for_status()
        return response.json()

    def update_plugin_storage(self, dashboard_id: str, plugin_install_id: str,
                             storage: Dict[str, Any]) -> Dict[str, Any]:
        """Update plugin storage config"""
        payload = {"storage": storage}
        response = self._request("PATCH", f"/dashboard/{dashboard_id}/plugin/{plugin_install_id}/update-storage", json=payload)
        response.raise_for_status()
        return response.json()

    def remove_plugin(self, dashboard_id: str, plugin_install_id: str) -> bool:
        """Remove plugin from Dashboard"""
        response = self._request("DELETE", f"/dashboard/{dashboard_id}/plugin/{plugin_install_id}")
        response.raise_for_status()
        return response.status_code == 200

    def duplicate_plugin(self, dashboard_id: str, plugin_install_id: str) -> Dict[str, Any]:
        """Duplicate installed plugin"""
        response = self._request("POST", f"/dashboard/{dashboard_id}/plugin/{plugin_install_id}/duplicate")
        response.raise_for_status()
        return response.json()


def main():
    parser = argparse.ArgumentParser(description="Teable Dashboard API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    list_parser = subparsers.add_parser("list", help="List dashboards")
    list_parser.add_argument("--base-id", required=True, help="Base ID")

    get_parser = subparsers.add_parser("get", help="Get Dashboard details")
    get_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")

    create_parser = subparsers.add_parser("create", help="Create Dashboard")
    create_parser.add_argument("--base-id", required=True, help="Base ID")
    create_parser.add_argument("--name", required=True, help="Dashboard name")
    create_parser.add_argument("--layout", help="Layout config (JSON)")

    update_parser = subparsers.add_parser("update", help="Update Dashboard")
    update_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")
    update_parser.add_argument("--name", help="New name")
    update_parser.add_argument("--layout", help="New layout (JSON)")

    delete_parser = subparsers.add_parser("delete", help="Delete Dashboard")
    delete_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")

    dup_parser = subparsers.add_parser("duplicate", help="Duplicate Dashboard")
    dup_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")
    dup_parser.add_argument("--base-id", help="Target Base ID")
    dup_parser.add_argument("--name", help="New Dashboard name")

    install_plugin_parser = subparsers.add_parser("install-plugin", help="Install plugin")
    install_plugin_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")
    install_plugin_parser.add_argument("--plugin-id", required=True, help="Plugin ID")
    install_plugin_parser.add_argument("--name", help="Plugin name")
    install_plugin_parser.add_argument("--storage", help="Storage config (JSON)")

    list_plugins_parser = subparsers.add_parser("list-plugins", help="List installed plugins")
    list_plugins_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")

    remove_plugin_parser = subparsers.add_parser("remove-plugin", help="Remove plugin")
    remove_plugin_parser.add_argument("--dashboard-id", required=True, help="Dashboard ID")
    remove_plugin_parser.add_argument("--plugin-install-id", required=True, help="Plugin install ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        client = TeableDashboardClient()

        if args.command == "list":
            result = client.list_dashboards(args.base_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "get":
            result = client.get_dashboard(args.dashboard_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "create":
            layout = json.loads(args.layout) if args.layout else None
            result = client.create_dashboard(args.base_id, args.name, layout)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "update":
            layout = json.loads(args.layout) if args.layout else None
            result = client.update_dashboard(args.dashboard_id, args.name, layout)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "delete":
            success = client.delete_dashboard(args.dashboard_id)
            print(f"Deletion {'successful' if success else 'failed'}")

        elif args.command == "duplicate":
            result = client.duplicate_dashboard(args.dashboard_id, args.base_id, args.name)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "install-plugin":
            storage = json.loads(args.storage) if args.storage else None
            result = client.install_plugin(args.dashboard_id, args.plugin_id, args.name, storage)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "list-plugins":
            result = client.list_plugins(args.dashboard_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))

        elif args.command == "remove-plugin":
            success = client.remove_plugin(args.dashboard_id, args.plugin_install_id)
            print(f"Removal {'successful' if success else 'failed'}")

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