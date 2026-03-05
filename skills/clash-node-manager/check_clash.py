#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Clash proxy nodes status
"""
import sys
import requests
from typing import Dict, Optional

# Default Clash API endpoint
DEFAULT_API_URL = "http://127.0.0.1:9090"
DEFAULT_SECRET = None  # Set if you have secret configured

def get_clash_api_url(api_url: str = None, secret: str = None) -> tuple:
    """Get Clash API base URL and headers"""
    base_url = api_url or DEFAULT_API_URL
    headers = {"Content-Type": "application/json"}
    
    if secret:
        headers["Authorization"] = f"Bearer {secret}"
    
    return base_url.rstrip('/'), headers

def check_clash_connection(base_url: str, headers: Dict) -> bool:
    """Check if Clash API is accessible"""
    try:
        response = requests.get(f"{base_url}/version", headers=headers, timeout=3)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✓ Clash API connected")
            print(f"  Version: {version_info.get('version', 'unknown')}")
            return True
        else:
            print(f"✗ Clash API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Clash API at {base_url}")
        print(f"  Make sure Clash is running and API is enabled")
        return False
    except Exception as e:
        print(f"✗ Error connecting to Clash API: {e}")
        return False

def get_proxies(base_url: str, headers: Dict) -> Optional[Dict]:
    """Get all proxies from Clash"""
    try:
        response = requests.get(f"{base_url}/proxies", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Failed to get proxies: status {response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error getting proxies: {e}")
        return None

def get_connections(base_url: str, headers: Dict) -> Optional[Dict]:
    """Get current active connections from Clash"""
    try:
        response = requests.get(f"{base_url}/connections", headers=headers, timeout=3)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def get_current_proxy(base_url: str, headers: Dict, group: str = "GLOBAL") -> Optional[str]:
    """Get current proxy name from specified group"""
    try:
        response = requests.get(f"{base_url}/proxies/{group}", headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("now")
        return None
    except Exception as e:
        return None

def switch_proxy(base_url: str, headers: Dict, group: str, proxy_name: str) -> bool:
    """Switch proxy in specified group"""
    try:
        url = f"{base_url}/proxies/{group}"
        data = {"name": proxy_name}
        response = requests.put(url, headers=headers, json=data, timeout=5)
        
        if response.status_code == 204:
            return True
        elif response.status_code == 400:
            error_msg = response.text
            print(f"✗ Failed to switch: {error_msg}")
            return False
        else:
            print(f"✗ Failed to switch: status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error switching proxy: {e}")
        return False

def list_available_proxies(base_url: str, headers: Dict, group: str = "GLOBAL") -> Optional[list]:
    """List available proxies in a group"""
    try:
        response = requests.get(f"{base_url}/proxies/{group}", headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            return data.get("all", [])
        return None
    except Exception as e:
        return None

def get_proxy_delay_from_history(proxy_info: Dict) -> Optional[int]:
    """Get delay from proxy history (Clash built-in delay info)"""
    history = proxy_info.get("history", [])
    if not history:
        return None
    
    # Get the latest delay from history
    # History format: [{"delay": 123, "time": "..."}, ...]
    latest = history[-1] if history else {}
    delay = latest.get("delay")
    
    # Delay might be 0 for timeout, None for untested
    if delay is None or delay == 0:
        return None
    
    return delay

def format_delay(delay: Optional[int]) -> str:
    """Format delay for display"""
    if delay is None:
        return "N/A"
    elif delay == 0:
        return "timeout"
    else:
        return f"{delay}ms"

def check_clash_nodes(api_url: str = None, secret: str = None):
    """Check Clash nodes status"""
    print("=" * 60)
    print("Clash Nodes Check")
    print("=" * 60)
    print()
    
    base_url, headers = get_clash_api_url(api_url, secret)
    
    # Step 1: Check connection
    print("[1/4] Checking Clash API connection...")
    if not check_clash_connection(base_url, headers):
        return False
    print()
    
    # Step 2: Get current connection info
    print("[2/4] Checking current connection...")
    current_proxy = get_current_proxy(base_url, headers)
    connections = get_connections(base_url, headers)
    
    if current_proxy:
        print(f"✓ Current proxy: {current_proxy}")
        if connections:
            conns = connections.get("connections", {})
            active_count = len(conns)
            if active_count > 0:
                print(f"  Active connections: {active_count}")
        print()
    else:
        print("  No proxy selected or using DIRECT")
        print()
    
    # Step 3: Get proxies
    print("[3/4] Fetching proxy nodes...")
    proxies_data = get_proxies(base_url, headers)
    if not proxies_data:
        return False
    
    proxies = proxies_data.get("proxies", {})
    if not proxies:
        print("✗ No proxies found")
        return False
    
    print(f"✓ Found {len(proxies)} proxy groups/nodes")
    print()
    
    # Step 4: Display nodes
    print("[4/4] Analyzing nodes...")
    print()
    
    # Group proxies by type
    proxy_groups = {}
    direct_proxies = []
    
    for name, proxy_info in proxies.items():
        proxy_type = proxy_info.get("type", "unknown")
        
        if proxy_type == "Selector":
            # This is a proxy group
            proxy_groups[name] = proxy_info
        elif proxy_type in ["Shadowsocks", "VMess", "Trojan", "Snell", "HTTP", "SOCKS5"]:
            # This is a direct proxy node
            direct_proxies.append((name, proxy_info))
    
    # Display proxy groups
    if proxy_groups:
        print("Proxy Groups:")
        print("-" * 60)
        for group_name, group_info in sorted(proxy_groups.items()):
            now_proxy = group_info.get("now", "N/A")
            proxies_list = group_info.get("all", [])
            
            # Highlight if this is the current proxy
            current_marker = " ← CURRENT" if now_proxy == current_proxy else ""
            
            print(f"  {group_name}")
            print(f"    Current: {now_proxy}{current_marker}")
            print(f"    Nodes: {len(proxies_list)}")
            if proxies_list:
                print(f"    List: {', '.join(proxies_list[:5])}{'...' if len(proxies_list) > 5 else ''}")
        print()
    
    # Display direct proxy nodes
    if direct_proxies:
        print("Direct Proxy Nodes:")
        print("-" * 60)
        
        for name, proxy_info in sorted(direct_proxies):
            proxy_type = proxy_info.get("type", "unknown")
            server = proxy_info.get("server", "N/A")
            
            # Get delay from Clash built-in history
            delay = get_proxy_delay_from_history(proxy_info)
            delay_str = f" [{format_delay(delay)}]" if delay is not None else ""
            
            # Highlight if this is the current proxy
            current_marker = " ← CURRENT" if name == current_proxy else ""
            
            print(f"  {name}{current_marker}")
            print(f"    Type: {proxy_type}")
            print(f"    Server: {server}{delay_str}")
        
        print()
    
    # Summary
    total_nodes = len(direct_proxies)
    total_groups = len(proxy_groups)
    
    print("=" * 60)
    print(f"Summary: {total_groups} groups, {total_nodes} direct nodes")
    if current_proxy:
        print(f"Current connection: {current_proxy}")
    print("=" * 60)
    
    return True

def switch_node(api_url: str = None, secret: str = None, group: str = "GLOBAL", proxy_name: str = None, list_only: bool = False):
    """Switch to a proxy node"""
    print("=" * 60)
    print("Clash Proxy Switcher")
    print("=" * 60)
    print()
    
    base_url, headers = get_clash_api_url(api_url, secret)
    
    # Check connection
    if not check_clash_connection(base_url, headers):
        return False
    
    print()
    
    # Get current proxy
    current = get_current_proxy(base_url, headers, group)
    if current:
        print(f"Current proxy in '{group}': {current}")
    else:
        print(f"No proxy selected in '{group}'")
    print()
    
    # List available proxies
    available = list_available_proxies(base_url, headers, group)
    if not available:
        print(f"✗ No proxies available in group '{group}'")
        return False
    
    print(f"Available proxies in '{group}':")
    print("-" * 60)
    for i, proxy in enumerate(available, 1):
        marker = " ← CURRENT" if proxy == current else ""
        print(f"  {i}. {proxy}{marker}")
    print()
    
    if list_only:
        return True
    
    # Switch proxy
    if proxy_name is None:
        print("Usage: --switch <proxy-name> or --switch-by-index <number>")
        print("Example: --switch node-name-123")
        print("Example: --switch-by-index 5")
        return False
    
    print(f"Switching to: {proxy_name}")
    if switch_proxy(base_url, headers, group, proxy_name):
        print(f"✓ Successfully switched to '{proxy_name}'")
        
        # Verify
        new_current = get_current_proxy(base_url, headers, group)
        if new_current == proxy_name:
            print(f"✓ Verified: Current proxy is now '{new_current}'")
        return True
    else:
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Check and switch Clash proxy nodes")
    parser.add_argument("--api-url", default=None, help="Clash API URL (default: http://127.0.0.1:9090)")
    parser.add_argument("--secret", default=None, help="Clash API secret")
    
    # Switch options
    parser.add_argument("--switch", metavar="PROXY_NAME", help="Switch to specified proxy node")
    parser.add_argument("--switch-by-index", type=int, metavar="INDEX", help="Switch by index number (from list)")
    parser.add_argument("--group", default="GLOBAL", help="Proxy group name (default: GLOBAL)")
    parser.add_argument("--list", action="store_true", help="List available proxies only")
    
    args = parser.parse_args()
    
    # Handle switch operations
    if args.switch or args.switch_by_index is not None or args.list:
        proxy_name = args.switch
        
        # If switching by index, get the proxy name from the list
        if args.switch_by_index is not None:
            base_url, headers = get_clash_api_url(args.api_url, args.secret)
            if check_clash_connection(base_url, headers):
                available = list_available_proxies(base_url, headers, args.group)
                if available and 1 <= args.switch_by_index <= len(available):
                    proxy_name = available[args.switch_by_index - 1]
                else:
                    print(f"✗ Invalid index. Available: 1-{len(available) if available else 0}")
                    sys.exit(1)
            else:
                sys.exit(1)
        
        success = switch_node(
            api_url=args.api_url,
            secret=args.secret,
            group=args.group,
            proxy_name=proxy_name,
            list_only=args.list
        )
        sys.exit(0 if success else 1)
    else:
        # Default: check nodes
        success = check_clash_nodes(
            api_url=args.api_url,
            secret=args.secret
        )
        sys.exit(0 if success else 1)
