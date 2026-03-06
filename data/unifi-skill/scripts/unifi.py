#!/usr/bin/env python3
"""
UniFi Site Manager API CLI
Provides commands to query UniFi infrastructure.
"""
import argparse
import json
import sys
from typing import Dict, List, Any

import os
from pathlib import Path

import requests


def _load_config() -> Dict[str, Any]:
    """Load config.json from skill root, with env var overrides."""
    skill_root = Path(__file__).resolve().parents[1]
    cfg_path = skill_root / "config.json"
    cfg: Dict[str, Any] = {}
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    api_key = os.environ.get("UNIFI_API_KEY") or cfg.get("api_key")
    if not api_key:
        raise SystemExit(
            "Missing UniFi API key. Set UNIFI_API_KEY or create config.json (see config.json.example)."
        )

    base_url = os.environ.get("UNIFI_BASE_URL") or cfg.get("base_url") or "https://api.ui.com"

    cfg["api_key"] = api_key
    cfg["base_url"] = base_url
    return cfg


CONFIG = _load_config()
API_KEY = CONFIG["api_key"]
BASE_URL = CONFIG["base_url"]


def api_request(path: str) -> Dict[str, Any]:
    """Make an API request to the UniFi Site Manager."""
    url = f"{BASE_URL}{path}"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list_hosts(args):
    """List all UniFi controllers/hosts."""
    data = api_request("/v1/hosts")
    
    if not data.get("data"):
        print("No hosts found.")
        return
    
    if args.json:
        print(json.dumps(data, indent=2))
        return
    
    print("\n=== UniFi Hosts/Controllers ===\n")
    for host in data["data"]:
        reported = host.get("reportedState", {})
        hardware = reported.get("hardware", {})
        
        print(f"Name: {reported.get('hostname', 'N/A')}")
        print(f"  ID: {host.get('id', 'N/A')}")
        print(f"  Type: {hardware.get('name', 'N/A')}")
        print(f"  MAC: {reported.get('mac', 'N/A')}")
        print(f"  IP: {reported.get('ip', 'N/A')}")
        print(f"  State: {reported.get('state', 'N/A')}")
        print(f"  Version: {reported.get('version', 'N/A')}")
        print()


def cmd_list_sites(args):
    """List all UniFi sites with statistics."""
    data = api_request("/v1/sites")
    
    if not data.get("data"):
        print("No sites found.")
        return
    
    if args.json:
        print(json.dumps(data, indent=2))
        return
    
    print("\n=== UniFi Sites ===\n")
    for site in data["data"]:
        meta = site.get("meta", {})
        stats = site.get("statistics", {})
        counts = stats.get("counts", {})
        
        print(f"Name: {meta.get('desc', 'N/A')}")
        print(f"  Site ID: {meta.get('name', 'N/A')}")
        print(f"  Timezone: {meta.get('timezone', 'N/A')}")
        print(f"  Gateway MAC: {meta.get('gatewayMac', 'N/A')}")
        print(f"\n  Statistics:")
        print(f"    Total Devices: {counts.get('totalDevice', 0)}")
        print(f"    WiFi Devices: {counts.get('wifiDevice', 0)}")
        print(f"    WiFi Clients: {counts.get('wifiClient', 0)}")
        print(f"    Wired Clients: {counts.get('wiredClient', 0)}")
        print(f"    Offline Devices: {counts.get('offlineDevice', 0)}")
        print()


def cmd_list_devices(args):
    """List all network devices."""
    data = api_request("/v1/devices")
    
    if not data.get("data"):
        print("No devices found.")
        return
    
    if args.json:
        print(json.dumps(data, indent=2))
        return
    
    print("\n=== Network Devices ===\n")
    for host_data in data["data"]:
        devices = host_data.get("devices", [])
        
        for device in devices:
            print(f"{device.get('name', 'N/A')} ({device.get('model', 'N/A')})")
            print(f"  MAC: {device.get('mac', 'N/A')}")
            print(f"  IP: {device.get('ip', 'N/A')}")
            print(f"  Status: {device.get('status', 'N/A')}")
            print(f"  Version: {device.get('version', 'N/A')}")
            print()


def cmd_list_aps(args):
    """List access points only."""
    data = api_request("/v1/devices")
    
    if not data.get("data"):
        print("No devices found.")
        return
    
    # Filter for access points (model contains AP-related keywords)
    ap_keywords = ['AP', 'UAP', 'U6', 'AC', 'IW', 'Mesh']
    aps = []
    
    for host_data in data["data"]:
        devices = host_data.get("devices", [])
        
        for device in devices:
            model = device.get('model', '')
            # Check if this is an access point
            if any(keyword in model for keyword in ap_keywords):
                aps.append(device)
    
    if args.json:
        print(json.dumps(aps, indent=2))
        return
    
    if not aps:
        print("No access points found.")
        return
    
    print("\n=== Access Points ===\n")
    for ap in aps:
        print(f"{ap.get('name', 'N/A')} ({ap.get('model', 'N/A')})")
        print(f"  MAC: {ap.get('mac', 'N/A')}")
        print(f"  IP: {ap.get('ip', 'N/A')}")
        print(f"  Status: {ap.get('status', 'N/A')}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="UniFi Site Manager API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true",
                       help="Output raw JSON response")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # list-hosts command
    parser_hosts = subparsers.add_parser("list-hosts",
                                         help="List all UniFi controllers/hosts")
    parser_hosts.set_defaults(func=cmd_list_hosts)
    
    # list-sites command
    parser_sites = subparsers.add_parser("list-sites",
                                         help="List all sites with statistics")
    parser_sites.set_defaults(func=cmd_list_sites)
    
    # list-devices command
    parser_devices = subparsers.add_parser("list-devices",
                                           help="List all network devices")
    parser_devices.set_defaults(func=cmd_list_devices)
    
    # list-aps command
    parser_aps = subparsers.add_parser("list-aps",
                                       help="List access points only")
    parser_aps.set_defaults(func=cmd_list_aps)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
