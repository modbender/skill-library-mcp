#!/usr/bin/env python3
"""
UniFi Site Manager API CLI
Provides commands to query UniFi infrastructure via Cloud API, Cloud Connector, or local gateway.
"""
import argparse
import json
import sys
from typing import Dict, List, Any, Optional, Tuple

import os
from pathlib import Path

import requests
import re


def _sanitize_path_param(value: str) -> str:
    """Validate and sanitize a path parameter to prevent path traversal/injection."""
    # Allow alphanumeric, hyphens, underscores, colons, dots (for MACs, UUIDs, IDs)
    if not re.match(r'^[a-zA-Z0-9\-_:\.]+$', value):
        raise SystemExit(f"Error: Invalid path parameter: {value!r}")
    return value


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

    cfg["api_key"] = api_key
    return cfg


CONFIG = _load_config()
API_KEY = CONFIG["api_key"]
BASE_URL = "https://api.ui.com"


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _handle_api_error(resp: requests.Response, url: str) -> None:
    """Parse and display structured API errors, then exit."""
    try:
        err = resp.json()
        code = err.get("code", "")
        message = err.get("message", resp.reason)
        status = err.get("statusName", resp.status_code)
        path = err.get("requestPath", "")
        parts = [f"Error: {status}"]
        if code:
            parts.append(f"({code})")
        parts.append(f"— {message}")
        if path:
            parts.append(f"[{path}]")
        print(" ".join(parts), file=sys.stderr)
    except (ValueError, KeyError):
        print(f"Error: HTTP {resp.status_code} {resp.reason} for {url}", file=sys.stderr)
    sys.exit(1)


def api_request(path: str) -> Dict[str, Any]:
    """Make an API request to the UniFi Site Manager (cloud)."""
    url = f"{BASE_URL}{path}"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if not resp.ok:
            _handle_api_error(resp, url)
        return resp.json()
    except requests.ConnectionError:
        print(f"Error: Could not connect to {BASE_URL}", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Request timed out for {url}", file=sys.stderr)
        sys.exit(1)


def _local_api_request(path: str, gateway_ip: str, api_key: str) -> Dict[str, Any]:
    """Make an integration API request to the local UniFi gateway."""
    session, base = _get_local_session(gateway_ip)
    url = f"{base}/proxy/network/integration{path}"
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
    }
    try:
        resp = session.get(url, headers=headers, timeout=15)
        if not resp.ok:
            _handle_api_error(resp, url)
        return resp.json()
    except requests.ConnectionError:
        print(f"Error: Could not connect to gateway at {gateway_ip}", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Request to gateway timed out", file=sys.stderr)
        sys.exit(1)


def _local_classic_request(path: str, gateway_ip: str, api_key: str, method: str = "GET",
                           payload: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a classic API request to the local UniFi gateway."""
    session, base = _get_local_session(gateway_ip)
    url = f"{base}/proxy/network/api/s/default/{path}"
    headers = {
        "X-API-KEY": api_key,
        "Accept": "application/json",
    }
    try:
        if method == "PUT" and payload is not None:
            headers["Content-Type"] = "application/json"
            resp = session.put(url, headers=headers, json=payload, timeout=15)
        elif method == "POST" and payload is not None:
            headers["Content-Type"] = "application/json"
            resp = session.post(url, headers=headers, json=payload, timeout=15)
        else:
            resp = session.get(url, headers=headers, timeout=15)
        if not resp.ok:
            _handle_api_error(resp, url)
        return resp.json()
    except requests.ConnectionError:
        print(f"Error: Could not connect to gateway at {gateway_ip}", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Request to gateway timed out", file=sys.stderr)
        sys.exit(1)


def _resolve_local_gateway() -> Tuple[str, str]:
    """Resolve local gateway IP and API key from config."""
    gateway_ip = os.environ.get("UNIFI_GATEWAY_IP") or CONFIG.get("gateway_ip")
    local_api_key = os.environ.get("UNIFI_LOCAL_API_KEY") or CONFIG.get("local_api_key")
    if not gateway_ip or not local_api_key:
        return None, None
    return gateway_ip, local_api_key


def _local_gateway_fingerprint() -> Optional[str]:
    """Return the SHA-256 fingerprint of the gateway TLS certificate from config, else None."""
    return CONFIG.get("gateway_fingerprint") or None


# Shared session with fingerprint-pinning adapter (created once per process)
_local_session: Optional[requests.Session] = None


def _get_local_session(gateway_ip: str) -> Tuple[requests.Session, str]:
    """Return (session, base_url) for local gateway HTTPS requests.

    When a gateway certificate fingerprint is stored, the session pins TLS to that
    exact SHA-256 fingerprint — more secure than CA-based verification.
    Without a fingerprint, falls back to unverified HTTPS.
    """
    global _local_session
    base = f"https://{gateway_ip}"
    fingerprint = _local_gateway_fingerprint()

    if _local_session is None:
        if not fingerprint:
            print(
                "Error: No gateway_fingerprint configured. Local HTTPS requires certificate pinning.\n"
                "Without a pinned fingerprint, connections are vulnerable to MITM attacks.\n"
                "See SETUP.md for instructions on obtaining and configuring the gateway fingerprint.",
                file=sys.stderr,
            )
            sys.exit(1)

        _local_session = requests.Session()
        from requests.adapters import HTTPAdapter

        class _FingerprintAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                kwargs["assert_fingerprint"] = fingerprint
                super().init_poolmanager(*args, **kwargs)

        _local_session.mount("https://", _FingerprintAdapter())
        # CA verification is replaced by fingerprint assertion at the TLS level;
        # disable the default CA check to avoid rejecting self-signed certs.
        _local_session.verify = False

    return _local_session, base


def _get_console_id() -> Optional[str]:
    """Get the active (connected) console ID from the hosts API."""
    try:
        data = api_request("/v1/hosts")
        for host in data.get("data", []):
            rs = host.get("reportedState", {})
            if rs.get("state") == "connected":
                return host.get("id")
        # Fall back to first host if none explicitly connected
        hosts = data.get("data", [])
        if hosts:
            return hosts[0].get("id")
    except SystemExit:
        pass
    return None


def _connector_request(path: str, console_id: str) -> Dict[str, Any]:
    """Make an integration API request via the cloud connector proxy."""
    url = f"{BASE_URL}/v1/connector/consoles/{console_id}/proxy/network/integration{path}"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if not resp.ok:
            _handle_api_error(resp, url)
        return resp.json()
    except requests.ConnectionError:
        print(f"Error: Could not connect via cloud connector", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Cloud connector request timed out", file=sys.stderr)
        sys.exit(1)


def _connector_classic_request(path: str, console_id: str, method: str = "GET",
                               payload: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a classic API request via the cloud connector proxy."""
    url = f"{BASE_URL}/v1/connector/consoles/{console_id}/proxy/network/api/s/default/{path}"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
    }
    try:
        if method == "PUT" and payload is not None:
            headers["Content-Type"] = "application/json"
            resp = requests.put(url, headers=headers, json=payload, timeout=30)
        else:
            resp = requests.get(url, headers=headers, timeout=30)
        if not resp.ok:
            _handle_api_error(resp, url)
        return resp.json()
    except requests.ConnectionError:
        print(f"Error: Could not connect via cloud connector", file=sys.stderr)
        sys.exit(1)
    except requests.Timeout:
        print(f"Error: Cloud connector request timed out", file=sys.stderr)
        sys.exit(1)


def _is_local_reachable() -> bool:
    """Quick check if the local gateway is reachable (cached per run)."""
    if hasattr(_is_local_reachable, '_cached'):
        return _is_local_reachable._cached
    gateway_ip, local_api_key = _resolve_local_gateway()
    if not gateway_ip or not local_api_key:
        _is_local_reachable._cached = False
        return False
    if not _local_gateway_fingerprint():
        # No fingerprint configured — can't connect securely
        _is_local_reachable._cached = False
        return False
    try:
        session, base = _get_local_session(gateway_ip)
        resp = session.get(f"{base}/proxy/network/api/s/default/self",
                           headers={"X-API-KEY": local_api_key, "Accept": "application/json"},
                           timeout=3)
        _is_local_reachable._cached = resp.ok
    except (requests.ConnectionError, requests.Timeout):
        _is_local_reachable._cached = False
    return _is_local_reachable._cached


def _classic_request(path: str, local: bool = False, method: str = "GET",
                     payload: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Make a classic API request (/api/s/default/...), choosing the best transport:
    - If --local or gateway reachable: use local gateway with local_api_key
    - Otherwise: use cloud connector with cloud api_key
    """
    if local or _is_local_reachable():
        gateway_ip, local_api_key = _resolve_local_gateway()
        if gateway_ip and local_api_key:
            return _local_classic_request(path, gateway_ip, local_api_key, method=method, payload=payload)
        if local:
            print("Error: --local specified but gateway_ip/local_api_key not configured", file=sys.stderr)
            sys.exit(1)

    # Cloud connector
    console_id = _get_console_id()
    if console_id:
        return _connector_classic_request(path, console_id, method=method, payload=payload)

    print("Error: No local gateway or cloud connector available.", file=sys.stderr)
    sys.exit(1)


def _integration_request(path: str, local: bool = False) -> Dict[str, Any]:
    """
    Make an integration API request, choosing the best transport:
    - If --local or gateway reachable: use local gateway with local_api_key
    - Otherwise: use cloud connector with cloud api_key
    """
    if local or _is_local_reachable():
        gateway_ip, local_api_key = _resolve_local_gateway()
        if gateway_ip and local_api_key:
            return _local_api_request(path, gateway_ip, local_api_key)
        if local:
            print("Error: --local specified but gateway_ip/local_api_key not configured", file=sys.stderr)
            sys.exit(1)

    # Cloud connector
    console_id = _get_console_id()
    if console_id:
        try:
            return _connector_request(path, console_id)
        except SystemExit:
            pass  # Fall through to local

    # Last resort: try local anyway
    gateway_ip, local_api_key = _resolve_local_gateway()
    if gateway_ip and local_api_key:
        return _local_api_request(path, gateway_ip, local_api_key)

    print("Error: No cloud connector or local gateway available.", file=sys.stderr)
    sys.exit(1)


def _integration_request_paginated(path: str, local: bool = False, limit: int = 200) -> List[Dict[str, Any]]:
    """Fetch all items from a paginated integration endpoint."""
    all_items: List[Dict[str, Any]] = []
    offset = 0
    sep = '&' if '?' in path else '?'
    while True:
        paged_path = f"{path}{sep}offset={offset}&limit={limit}"
        data = _integration_request(paged_path, local=local)
        items = data.get("data", [])
        all_items.extend(items)
        total = data.get("totalCount", 0)
        if offset + limit >= total or not items:
            break
        offset += limit
    return all_items


def _resolve_site_id(args) -> str:
    """Resolve site ID from args or auto-detect."""
    if hasattr(args, 'site') and args.site:
        return _sanitize_path_param(args.site)

    # Check config for site_id
    site_id = CONFIG.get("site_id")
    if site_id:
        return site_id

    # Auto-detect from integration API
    local = getattr(args, 'local', False)
    data = _integration_request("/v1/sites", local=local)
    sites = data.get("data", [])
    if not sites:
        print("No sites found.", file=sys.stderr)
        sys.exit(1)
    if len(sites) == 1:
        return sites[0].get("id")
    else:
        print("Multiple sites found. Use --site <siteId> to specify:", file=sys.stderr)
        for s in sites:
            print(f"  {s.get('id')}  ({s.get('name', 'N/A')})", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _format_bytes(b: int) -> str:
    """Format byte count to human-readable string."""
    if b >= 1_000_000_000:
        return f"{b / 1_000_000_000:.1f} GB"
    if b >= 1_000_000:
        return f"{b / 1_000_000:.1f} MB"
    if b >= 1_000:
        return f"{b / 1_000:.1f} KB"
    return f"{b} B"


def _format_uptime(seconds: int) -> str:
    """Format seconds to human-readable uptime."""
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes and not days:
        parts.append(f"{minutes}m")
    return " ".join(parts) or "<1m"


# ---------------------------------------------------------------------------
# Commands: Cloud API (unchanged)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Commands: Integration API (cloud connector + local gateway)
# ---------------------------------------------------------------------------

def cmd_list_clients(args):
    """List connected clients on a site (via cloud connector or local gateway)."""
    if args.detailed:
        _list_clients_detailed(args)
        return

    local = getattr(args, 'local', False)
    site_id = _resolve_site_id(args)

    all_clients = _integration_request_paginated(f"/v1/sites/{site_id}/clients", local=local)

    if not all_clients:
        print("No connected clients found.")
        return

    if args.json:
        print(json.dumps(all_clients, indent=2))
        return

    print(f"\n=== Connected Clients ({len(all_clients)}) ===\n")

    # Sort by name (unnamed last)
    all_clients.sort(key=lambda c: (c.get("name") or "\xff").lower())

    for client in all_clients:
        name = client.get("name") or client.get("hostname") or "(unnamed)"
        client_type = client.get("type", "")
        ip = client.get("ipAddress", "—")
        mac = client.get("macAddress", "—")
        connected_at = client.get("connectedAt", "")

        access = client.get("access") or {}
        access_type = access.get("type", "")

        label = f"{name}"
        if client_type:
            label += f" [{client_type}]"
        if access_type:
            label += f" via {access_type}"

        print(f"{label}")
        print(f"  IP: {ip}  MAC: {mac}")
        if connected_at:
            print(f"  Connected: {connected_at}")
        print()


def _list_clients_detailed(args):
    """List connected clients with detailed stats from classic API."""
    local = getattr(args, 'local', False)
    data = _classic_request("stat/sta", local=local)
    all_clients = data.get("data", [])
    if not all_clients:
        print("No connected clients found.")
        return

    if args.json:
        print(json.dumps(all_clients, indent=2))
        return

    # Sort by name (unnamed last)
    all_clients.sort(key=lambda c: (c.get("name") or c.get("hostname") or "\xff").lower())

    wired = [c for c in all_clients if c.get("is_wired")]
    wireless = [c for c in all_clients if not c.get("is_wired")]

    print(f"\n=== Connected Clients ({len(all_clients)}: {len(wired)} wired, {len(wireless)} wireless) ===\n")

    for client in all_clients:
        name = client.get("name") or client.get("hostname") or "(unnamed)"
        oui = client.get("oui", "")
        ip = client.get("ip") or client.get("last_ip") or "—"
        mac = client.get("mac", "—")
        is_wired = client.get("is_wired", False)
        network = client.get("network", "")
        uptime = client.get("uptime", 0)
        satisfaction = client.get("satisfaction")

        # Traffic
        if is_wired:
            tx = client.get("wired-tx_bytes", 0)
            rx = client.get("wired-rx_bytes", 0)
            rate = client.get("wired_rate_mbps")
        else:
            tx = client.get("tx_bytes", 0)
            rx = client.get("rx_bytes", 0)
            raw_rate = client.get("tx_rate", client.get("rx_rate"))
            rate = round(raw_rate / 1000) if raw_rate and raw_rate > 1000 else raw_rate

        # Connection info
        uplink = client.get("last_uplink_name", "")
        channel = client.get("channel", "")
        radio = client.get("radio", "")
        signal = client.get("signal")
        ssid = client.get("essid", "")

        conn_type = "Wired" if is_wired else "WiFi"
        label = f"{name}"
        if oui:
            label += f" ({oui})"

        print(f"{label}")
        print(f"  {conn_type}  IP: {ip}  MAC: {mac}")

        detail_parts = []
        if network:
            detail_parts.append(f"Network: {network}")
        if uplink:
            detail_parts.append(f"Uplink: {uplink}")
        if rate:
            detail_parts.append(f"Rate: {rate} Mbps")
        if detail_parts:
            print(f"  {' · '.join(detail_parts)}")

        if not is_wired:
            wifi_parts = []
            if ssid:
                wifi_parts.append(f"SSID: {ssid}")
            if channel:
                wifi_parts.append(f"Ch: {channel}")
            if radio:
                wifi_parts.append(f"Radio: {radio}")
            if signal is not None:
                wifi_parts.append(f"Signal: {signal} dBm")
            if wifi_parts:
                print(f"  {' · '.join(wifi_parts)}")

        stats_parts = []
        if uptime:
            stats_parts.append(f"Uptime: {_format_uptime(uptime)}")
        if tx or rx:
            stats_parts.append(f"TX: {_format_bytes(tx)}  RX: {_format_bytes(rx)}")
        if satisfaction is not None:
            stats_parts.append(f"Satisfaction: {satisfaction}%")
        if stats_parts:
            print(f"  {' · '.join(stats_parts)}")

        print()


def cmd_list_networks(args):
    """List networks configured on a site."""
    local = getattr(args, 'local', False)
    site_id = _resolve_site_id(args)

    all_networks = _integration_request_paginated(f"/v1/sites/{site_id}/networks", local=local)

    if not all_networks:
        print("No networks found.")
        return

    if args.json:
        print(json.dumps(all_networks, indent=2))
        return

    print(f"\n=== Networks ({len(all_networks)}) ===\n")

    for net in all_networks:
        name = net.get("name", "N/A")
        net_id = net.get("id", "N/A")
        vlan = net.get("vlanId", "—")
        enabled = "✓" if net.get("enabled") else "✗"
        default = " (default)" if net.get("default") else ""
        management = net.get("management", "")
        meta = net.get("metadata", {})
        origin = meta.get("origin", "")

        print(f"{name}{default} [{enabled}]")
        print(f"  ID: {net_id}")
        print(f"  VLAN: {vlan}  Management: {management}")
        if origin:
            print(f"  Origin: {origin}")
        print()


def cmd_get_device(args):
    """Get detailed info about a specific device."""
    local = getattr(args, 'local', False)
    site_id = _resolve_site_id(args)
    device_id = _sanitize_path_param(args.device_id)

    data = _integration_request(f"/v1/sites/{site_id}/devices/{device_id}", local=local)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    name = data.get("name", "N/A")
    model = data.get("model", "N/A")
    state = data.get("state", "N/A")
    mac = data.get("macAddress", "N/A")
    ip = data.get("ipAddress", "N/A")
    fw = data.get("firmwareVersion", "N/A")
    updatable = data.get("firmwareUpdatable", False)
    provisioned = data.get("provisionedAt", "")

    print(f"\n=== Device: {name} ===\n")
    print(f"  Model: {model}")
    print(f"  State: {state}")
    print(f"  MAC: {mac}")
    print(f"  IP: {ip}")
    print(f"  Firmware: {fw}" + (" (update available)" if updatable else ""))
    if provisioned:
        print(f"  Provisioned: {provisioned}")

    # Features
    features = data.get("features", {})
    if isinstance(features, dict) and features:
        print(f"  Features: {', '.join(features.keys())}")
    elif isinstance(features, list) and features:
        print(f"  Features: {', '.join(features)}")

    # Uplink
    uplink = data.get("uplink", {})
    if uplink:
        print(f"  Uplink Device: {uplink.get('deviceId', 'N/A')}")

    # Interfaces
    interfaces = data.get("interfaces", {})
    if isinstance(interfaces, dict):
        # Ports
        ports = interfaces.get("ports", [])
        if ports:
            print(f"\n  Ports ({len(ports)}):")
            for port in ports:
                idx = port.get("idx", "?")
                pstate = port.get("state", "?")
                speed = port.get("speedMbps", "?")
                max_speed = port.get("maxSpeedMbps", "?")
                print(f"    Port {idx}: {pstate} — {speed}/{max_speed} Mbps")

        # Radios
        radios = interfaces.get("radios", [])
        if radios:
            print(f"\n  Radios ({len(radios)}):")
            for radio in radios:
                std = radio.get("wlanStandard", "?")
                freq = radio.get("frequencyGHz", "?")
                ch = radio.get("channel", "?")
                width = radio.get("channelWidthMHz", "?")
                print(f"    {std} @ {freq} GHz — Ch {ch} ({width} MHz)")

    print()


def cmd_get_client(args):
    """Get detailed info about a specific client."""
    local = getattr(args, 'local', False)
    site_id = _resolve_site_id(args)
    client_id = _sanitize_path_param(args.client_id)

    data = _integration_request(f"/v1/sites/{site_id}/clients/{client_id}", local=local)

    if args.json:
        print(json.dumps(data, indent=2))
        return

    name = data.get("name") or data.get("hostname") or "(unnamed)"
    client_type = data.get("type", "N/A")
    ip = data.get("ipAddress", "N/A")
    mac = data.get("macAddress", "N/A")
    connected = data.get("connectedAt", "")
    uplink_device = data.get("uplinkDeviceId", "")
    access = data.get("access", {})

    print(f"\n=== Client: {name} ===\n")
    print(f"  Type: {client_type}")
    print(f"  IP: {ip}")
    print(f"  MAC: {mac}")
    if connected:
        print(f"  Connected: {connected}")
    if uplink_device:
        print(f"  Uplink Device: {uplink_device}")
    if access:
        print(f"  Access Type: {access.get('type', 'N/A')}")
    print()


def cmd_list_known_clients(args):
    """List all known clients (current + historical) from classic API."""
    local = getattr(args, 'local', False)
    data = _classic_request("rest/user", local=local)
    all_clients = data.get("data", [])

    if not all_clients:
        print("No known clients found.")
        return

    if args.json:
        print(json.dumps(all_clients, indent=2))
        return

    # Filter options
    named_only = getattr(args, 'named', False)
    if named_only:
        all_clients = [c for c in all_clients if c.get("name")]

    # Sort by name (unnamed last)
    all_clients.sort(key=lambda c: (c.get("name") or c.get("hostname") or "\xff").lower())

    print(f"\n=== Known Clients ({len(all_clients)}) ===\n")

    from datetime import datetime, timezone, timedelta
    tz_offset = timedelta(hours=1)  # CET

    for client in all_clients:
        name = client.get("name") or ""
        hostname = client.get("hostname") or ""
        mac = client.get("mac", "?")
        oui = client.get("oui", "")
        last_ip = client.get("last_ip") or "—"
        noted = "📌" if client.get("noted") else ""

        last_seen = client.get("last_seen")
        last_seen_str = ""
        if last_seen:
            dt = datetime.fromtimestamp(last_seen, tz=timezone.utc) + tz_offset
            last_seen_str = dt.strftime("%Y-%m-%d %H:%M")

        display_name = name or hostname or "(unnamed)"
        label = f"{display_name}"
        if name and hostname and hostname != name:
            label += f" ({hostname})"
        if oui:
            label += f" [{oui}]"

        print(f"{noted} {label}")
        print(f"    MAC: {mac}  IP: {last_ip}")
        if last_seen_str:
            print(f"    Last seen: {last_seen_str}")
        print()


def cmd_list_events(args):
    """List site events from classic API (roaming, AP events, etc.)."""
    local = getattr(args, 'local', False)
    data = _classic_request("stat/event", local=local)
    events = data.get("data", [])

    if not events:
        print("No events found.")
        return

    if args.json:
        print(json.dumps(events, indent=2))
        return

    # Optional filter by event key
    event_filter = getattr(args, 'filter', None)
    if event_filter:
        events = [e for e in events if event_filter.lower() in e.get("key", "").lower()]

    # Optional filter by MAC
    mac_filter = getattr(args, 'mac', None)
    if mac_filter:
        mac_filter = mac_filter.lower()
        events = [e for e in events if mac_filter in (e.get("user") or "").lower()
                  or mac_filter in (e.get("ap") or "").lower()]

    # Build AP name lookup
    ap_names: Dict[str, str] = {}
    try:
        dev_data = _classic_request("stat/device", local=local)
        for d in dev_data.get("data", []):
            if d.get("type") == "uap":
                ap_names[d.get("mac", "").lower()] = d.get("name") or d.get("hostname") or d.get("mac", "")
    except SystemExit:
        pass

    # Build client name lookup
    client_names: Dict[str, str] = {}
    try:
        user_data = _classic_request("rest/user", local=local)
        for u in user_data.get("data", []):
            client_names[u.get("mac", "").lower()] = u.get("name") or u.get("hostname") or u.get("mac", "")
    except SystemExit:
        pass

    from datetime import datetime, timezone, timedelta
    tz_offset = timedelta(hours=1)  # CET

    print(f"\n=== Events ({len(events)}) ===\n")

    for e in events:
        ts = e.get("time", 0)
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc) + tz_offset
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")

        key = e.get("key", "?")
        msg = e.get("msg", "")

        # Resolve names in message
        user_mac = (e.get("user") or "").lower()
        ap_mac = (e.get("ap") or "").lower()
        user_name = client_names.get(user_mac, "")
        ap_name = ap_names.get(ap_mac, e.get("ap_name", ""))

        # Build readable line
        parts = [f"{time_str}  {key}"]
        if user_name:
            parts.append(f"  Client: {user_name}")
        elif user_mac:
            parts.append(f"  Client: {user_mac}")
        if ap_name:
            parts.append(f"  AP: {ap_name}")

        # Extra detail for roaming
        if "Roam" in key:
            ch_from = e.get("channel_from", "")
            ch_to = e.get("channel_to", "")
            radio_from = e.get("radio_from", "")
            radio_to = e.get("radio_to", "")
            band_from = "5G" if radio_from == "na" else "2.4G" if radio_from == "ng" else radio_from
            band_to = "5G" if radio_to == "na" else "2.4G" if radio_to == "ng" else radio_to
            if ch_from and ch_to:
                parts.append(f"  ch{ch_from}({band_from}) → ch{ch_to}({band_to})")

        print("  ".join(parts))

    if events:
        first_ts = events[-1].get("time", 0)
        last_ts = events[0].get("time", 0)
        from_dt = datetime.fromtimestamp(first_ts / 1000, tz=timezone.utc) + tz_offset
        to_dt = datetime.fromtimestamp(last_ts / 1000, tz=timezone.utc) + tz_offset
        print(f"\nTime range: {from_dt.strftime('%Y-%m-%d')} → {to_dt.strftime('%Y-%m-%d')}")


def cmd_get_wlan_config(args):
    """Show WLAN configuration for all SSIDs or a specific one."""
    local = getattr(args, 'local', False)
    data = _classic_request("rest/wlanconf", local=local)
    wlans = data.get("data", [])

    if not wlans:
        print("No WLAN configurations found.")
        return

    # Filter by SSID if specified
    ssid_filter = getattr(args, 'ssid', None)
    if ssid_filter:
        wlans = [w for w in wlans if w.get("name", "").lower() == ssid_filter.lower()]
        if not wlans:
            print(f"No WLAN found with SSID '{ssid_filter}'")
            return

    if args.json:
        print(json.dumps(wlans, indent=2))
        return

    print(f"\n=== WLAN Configurations ({len(wlans)}) ===\n")

    for wlan in wlans:
        name = wlan.get("name", "N/A")
        enabled = "✓" if wlan.get("enabled") else "✗"
        security = wlan.get("security", "N/A")
        fast_roaming = "✓" if wlan.get("fast_roaming_enabled") else "✗"
        bss_transition = "✓" if wlan.get("bss_transition") else "✗"
        pmf_mode = wlan.get("pmf_mode", "N/A")
        wlan_bands = wlan.get("wlan_bands", [])
        if isinstance(wlan_bands, list):
            wlan_bands = ", ".join(wlan_bands)
        band_steering = wlan.get("band_steering_mode", "N/A")
        uapsd = "✓" if wlan.get("uapsd_enabled") else "✗"

        print(f"{name} [{enabled}]")
        print(f"  Security: {security}")
        print(f"  Fast Roaming: {fast_roaming}  BSS Transition: {bss_transition}  PMF: {pmf_mode}")
        print(f"  Bands: {wlan_bands}  Band Steering: {band_steering}  U-APSD: {uapsd}")
        print()


def cmd_set_wlan(args):
    """Set WLAN properties."""
    local = getattr(args, 'local', False)
    
    # Find the WLAN by SSID
    data = _classic_request("rest/wlanconf", local=local)
    wlans = data.get("data", [])
    
    target_wlan = None
    for w in wlans:
        if w.get("name", "").lower() == args.ssid.lower():
            target_wlan = w
            break
    
    if not target_wlan:
        print(f"Error: WLAN '{args.ssid}' not found", file=sys.stderr)
        sys.exit(1)
    
    wlan_id = target_wlan.get("_id")
    
    # Build update payload with only changed fields
    payload = {}
    bool_map = {"on": True, "off": False}
    
    if args.fast_roaming:
        payload["fast_roaming_enabled"] = bool_map.get(args.fast_roaming.lower())
    if args.bss_transition:
        payload["bss_transition"] = bool_map.get(args.bss_transition.lower())
    if args.pmf:
        payload["pmf_mode"] = args.pmf.lower()
    if args.band_steering:
        payload["band_steering_mode"] = args.band_steering.lower()
    
    if not payload:
        print("Error: No properties specified to update", file=sys.stderr)
        sys.exit(1)
    
    # Show before values
    print(f"\n=== Updating WLAN: {args.ssid} ===\n")
    print("Before:")
    if "fast_roaming_enabled" in payload:
        print(f"  Fast Roaming: {'✓' if target_wlan.get('fast_roaming_enabled') else '✗'}")
    if "bss_transition" in payload:
        print(f"  BSS Transition: {'✓' if target_wlan.get('bss_transition') else '✗'}")
    if "pmf_mode" in payload:
        print(f"  PMF: {target_wlan.get('pmf_mode', 'N/A')}")
    if "band_steering_mode" in payload:
        print(f"  Band Steering: {target_wlan.get('band_steering_mode', 'N/A')}")
    
    # Update
    _classic_request(f"rest/wlanconf/{wlan_id}", local=local, method="PUT", payload=payload)
    
    # Fetch updated config
    updated_data = _classic_request("rest/wlanconf", local=local)
    updated_wlan = None
    for w in updated_data.get("data", []):
        if w.get("_id") == wlan_id:
            updated_wlan = w
            break
    
    # Show after values
    print("\nAfter:")
    if updated_wlan:
        if "fast_roaming_enabled" in payload:
            print(f"  Fast Roaming: {'✓' if updated_wlan.get('fast_roaming_enabled') else '✗'}")
        if "bss_transition" in payload:
            print(f"  BSS Transition: {'✓' if updated_wlan.get('bss_transition') else '✗'}")
        if "pmf_mode" in payload:
            print(f"  PMF: {updated_wlan.get('pmf_mode', 'N/A')}")
        if "band_steering_mode" in payload:
            print(f"  Band Steering: {updated_wlan.get('band_steering_mode', 'N/A')}")
    print()


def cmd_get_radio_config(args):
    """Show radio configuration for all APs or a specific one."""
    local = getattr(args, 'local', False)
    data = _classic_request("stat/device", local=local)
    devices = data.get("data", [])
    
    # Filter for APs only
    aps = [d for d in devices if d.get("type") == "uap"]
    
    if not aps:
        print("No access points found.")
        return
    
    # Filter by AP name if specified
    ap_filter = getattr(args, 'ap', None)
    if ap_filter:
        aps = [ap for ap in aps if (ap.get("name") or ap.get("hostname") or "").lower() == ap_filter.lower()]
        if not aps:
            print(f"No AP found with name '{ap_filter}'")
            return
    
    if args.json:
        print(json.dumps(aps, indent=2))
        return
    
    print(f"\n=== Access Point Radio Configuration ({len(aps)}) ===\n")
    
    for ap in aps:
        name = ap.get("name") or ap.get("hostname") or "N/A"
        model = ap.get("model", "N/A")
        uplink_type = ap.get("uplink", {}).get("type", "N/A")
        
        print(f"{name} ({model})")
        print(f"  Uplink: {uplink_type}")
        
        # Mesh info if wireless uplink
        if uplink_type == "wireless":
            mesh_parent = ap.get("mesh_uplink_1", "")
            mesh_rssi = ap.get("mesh_sta_vap_0_rssi")
            if mesh_parent:
                print(f"  Mesh Parent: {mesh_parent}", end="")
                if mesh_rssi is not None:
                    print(f"  RSSI: {mesh_rssi} dBm")
                else:
                    print()
        
        # Radio configuration
        radio_table = ap.get("radio_table", [])
        for radio in radio_table:
            radio_name = radio.get("name", "?")
            band = "2.4 GHz" if radio_name == "ng" else "5 GHz" if radio_name == "na" else radio_name
            channel = radio.get("channel", "?")
            tx_power = radio.get("tx_power", "?")
            ht = radio.get("ht", "?")
            channel_width = radio.get("channel_width", "?")
            min_rssi = radio.get("min_rssi", "N/A")
            
            print(f"  Radio {band}:")
            print(f"    Channel: {channel}  Width: {channel_width} MHz  HT: {ht}")
            print(f"    TX Power: {tx_power}  Min RSSI: {min_rssi}")
        
        # Radio stats
        radio_table_stats = ap.get("radio_table_stats", [])
        if radio_table_stats:
            print(f"  Radio Stats:")
            for stats in radio_table_stats:
                radio_name = stats.get("name", "?")
                band = "2.4 GHz" if radio_name == "ng" else "5 GHz" if radio_name == "na" else radio_name
                satisfaction = stats.get("satisfaction", "N/A")
                num_sta = stats.get("num_sta", 0)
                cu_total = stats.get("cu_total", "N/A")
                print(f"    {band}: Satisfaction: {satisfaction}%  Clients: {num_sta}  Channel Utilization: {cu_total}%")
        
        print()


def cmd_set_radio(args):
    """Set radio properties on an AP."""
    local = getattr(args, 'local', False)
    
    # Find the AP
    data = _classic_request("stat/device", local=local)
    devices = data.get("data", [])
    aps = [d for d in devices if d.get("type") == "uap"]
    
    target_ap = None
    for ap in aps:
        if (ap.get("name") or ap.get("hostname") or "").lower() == args.ap.lower():
            target_ap = ap
            break
    
    if not target_ap:
        print(f"Error: AP '{args.ap}' not found", file=sys.stderr)
        sys.exit(1)
    
    ap_id = target_ap.get("_id")
    
    # Find the radio in radio_table
    radio_table = target_ap.get("radio_table", [])
    band_map = {"2.4": "ng", "5": "na"}
    target_radio_name = band_map.get(args.band)
    
    target_radio = None
    radio_idx = None
    for idx, radio in enumerate(radio_table):
        if radio.get("name") == target_radio_name:
            target_radio = radio
            radio_idx = idx
            break
    
    if not target_radio:
        print(f"Error: Radio for band {args.band} GHz not found on AP '{args.ap}'", file=sys.stderr)
        sys.exit(1)
    
    # Show before values
    print(f"\n=== Updating Radio on AP: {args.ap} ({args.band} GHz) ===\n")
    print("Before:")
    print(f"  Channel: {target_radio.get('channel', '?')}")
    print(f"  Channel Width: {target_radio.get('channel_width', '?')} MHz")
    print(f"  TX Power: {target_radio.get('tx_power', '?')}")
    
    # Build updated radio config
    updated_radio = dict(target_radio)
    
    if args.channel:
        if args.channel.lower() == "auto":
            updated_radio["channel"] = "auto"
        else:
            updated_radio["channel"] = int(args.channel)
    
    if args.width:
        updated_radio["channel_width"] = int(args.width)
    
    if args.power:
        power_map = {"low": "low", "medium": "medium", "high": "high", "auto": "auto"}
        updated_radio["tx_power_mode"] = power_map.get(args.power.lower(), "auto")
    
    # Build payload with updated radio_table
    updated_radio_table = list(radio_table)
    updated_radio_table[radio_idx] = updated_radio
    
    payload = {
        "radio_table": updated_radio_table
    }
    
    # Update
    _classic_request(f"rest/device/{ap_id}", local=local, method="PUT", payload=payload)
    
    # Fetch updated config
    updated_data = _classic_request("stat/device", local=local)
    updated_ap = None
    for d in updated_data.get("data", []):
        if d.get("_id") == ap_id:
            updated_ap = d
            break
    
    # Show after values
    print("\nAfter:")
    if updated_ap:
        updated_radio_table = updated_ap.get("radio_table", [])
        for radio in updated_radio_table:
            if radio.get("name") == target_radio_name:
                print(f"  Channel: {radio.get('channel', '?')}")
                print(f"  Channel Width: {radio.get('channel_width', '?')} MHz")
                print(f"  TX Power: {radio.get('tx_power', '?')}")
                break
    print()


def _find_client_by_mac(mac: str, local: bool = False) -> Dict[str, Any]:
    """Look up a client record by MAC address. Returns the client dict or exits with error."""
    mac = mac.lower()
    data = _classic_request("rest/user", local=local)
    for c in data.get("data", []):
        if c.get("mac", "").lower() == mac:
            return c
    print(f"Error: Client with MAC '{mac}' not found", file=sys.stderr)
    sys.exit(1)


def cmd_set_client(args):
    """Set one or more properties on a client by MAC."""
    local = getattr(args, 'local', False)
    client = _find_client_by_mac(args.mac, local=local)
    client_id = _sanitize_path_param(client["_id"])

    payload: Dict[str, Any] = {}
    changes: List[str] = []

    if args.name is not None:
        old_name = client.get("name") or client.get("hostname") or "(unnamed)"
        payload["name"] = args.name
        payload["noted"] = True
        changes.append(f"  Name: {old_name} → {args.name}")

    if args.fixed_ip is not None:
        if args.fixed_ip == "off":
            payload["use_fixedip"] = False
            changes.append("  Fixed IP: disabled")
        else:
            payload["use_fixedip"] = True
            payload["fixed_ip"] = args.fixed_ip
            changes.append(f"  Fixed IP: {args.fixed_ip}")

    if args.dns_record is not None:
        if args.dns_record == "off":
            payload["local_dns_record_enabled"] = False
            payload["local_dns_record"] = ""
            changes.append("  DNS record: disabled")
        else:
            payload["local_dns_record_enabled"] = True
            payload["local_dns_record"] = args.dns_record
            changes.append(f"  DNS record: {args.dns_record}")

    if args.pin_ap is not None:
        if args.pin_ap == "off":
            payload["fixed_ap_enabled"] = False
            changes.append("  AP pinning: disabled")
        else:
            # Resolve AP name to MAC
            devices = _integration_request_paginated(
                f"/v2/sites/{_load_config()['site_id']}/devices", local=local
            )
            ap_mac = None
            for d in devices:
                if (d.get("name") or "").lower() == args.pin_ap.lower():
                    ap_mac = d.get("mac")
                    break
            if not ap_mac:
                print(f"Error: AP '{args.pin_ap}' not found", file=sys.stderr)
                sys.exit(1)
            payload["fixed_ap_enabled"] = True
            payload["fixed_ap_mac"] = ap_mac
            changes.append(f"  Pinned to AP: {args.pin_ap} ({ap_mac})")

    if not payload:
        print("Error: No changes specified. Use --name, --fixed-ip, --dns-record, or --pin-ap",
              file=sys.stderr)
        sys.exit(1)

    _classic_request(f"rest/user/{client_id}", local=local, method="PUT", payload=payload)

    print(f"\n✓ Client updated ({args.mac}):")
    for change in changes:
        print(change)
    print()


def cmd_get_network_dns(args):
    """Show DHCP DNS config for one or all networks."""
    local = getattr(args, 'local', False)
    networks = _classic_request("rest/networkconf", local=local)

    results = []
    for net in networks["data"]:
        purpose = net.get("purpose", "")
        if purpose in ("wan", "remote-user-vpn"):
            continue
        name = net.get("name", "?")
        if args.network and name.lower() != args.network.lower():
            continue
        enabled = net.get("dhcpd_dns_enabled", False)
        dns_servers = {}
        for i in range(1, 5):
            v = net.get(f"dhcpd_dns_{i}", "")
            if v:
                dns_servers[f"dns_{i}"] = v
        results.append({
            "network": name,
            "subnet": net.get("ip_subnet", ""),
            "dhcpd_dns_enabled": enabled,
            **dns_servers,
        })

    if not results and args.network:
        print(f"Error: Network '{args.network}' not found", file=sys.stderr)
        sys.exit(1)

    if getattr(args, 'json', False):
        print(json.dumps(results if len(results) != 1 else results[0], indent=2))
    else:
        for r in results:
            print(f"\n=== {r['network']} ({r['subnet']}) ===\n")
            print(f"  Override: {'enabled' if r['dhcpd_dns_enabled'] else 'disabled (using gateway)'}")
            for i in range(1, 5):
                v = r.get(f"dns_{i}")
                if v:
                    print(f"  DNS {i}: {v}")
        print()


def cmd_set_network_dns(args):
    """Set or show DHCP DNS servers for a network by name."""
    local = getattr(args, 'local', False)
    networks = _classic_request("rest/networkconf", local=local)

    net = None
    for n in networks["data"]:
        if n.get("name", "").lower() == args.network.lower():
            net = n
            break
    if not net:
        print(f"Error: Network '{args.network}' not found", file=sys.stderr)
        sys.exit(1)

    net_id = _sanitize_path_param(net["_id"])
    payload: Dict[str, Any] = {}
    changes: List[str] = []

    if args.dns1 == "auto":
        payload["dhcpd_dns_enabled"] = False
        changes.append("  DNS override: disabled (using gateway)")
    elif args.dns1 is not None:
        payload["dhcpd_dns_enabled"] = True
        payload["dhcpd_dns_1"] = args.dns1
        old = net.get("dhcpd_dns_1", "(none)")
        changes.append(f"  DNS 1: {old} → {args.dns1}")

    for i, arg in [(2, args.dns2), (3, args.dns3), (4, args.dns4)]:
        if arg is not None:
            val = "" if arg == "off" else arg
            payload[f"dhcpd_dns_{i}"] = val
            old = net.get(f"dhcpd_dns_{i}") or "(none)"
            changes.append(f"  DNS {i}: {old} → {arg}")

    if not payload:
        print("Error: No changes specified. Use --dns1, --dns2, --dns3, --dns4",
              file=sys.stderr)
        sys.exit(1)

    result = _classic_request(f"rest/networkconf/{net_id}", local=local,
                              method="PUT", payload=payload)

    if getattr(args, 'json', False):
        print(json.dumps(result, indent=2))
    else:
        print(f"\n✓ Network DNS updated ({net.get('name')}):")
        for change in changes:
            print(change)
        print()


def cmd_label_client(args):
    """Set custom name for a client by MAC. (Shorthand for set-client --name)"""
    args.fixed_ip = None
    args.dns_record = None
    args.pin_ap = None
    # Map positional 'name' to the --name flag for set_client
    setattr(args, 'name', args.label_name)
    cmd_set_client(args)


def cmd_list_ap_clients(args):
    """List wireless clients grouped by their connected AP."""
    local = getattr(args, 'local', False)
    
    # Get all wireless clients
    sta_data = _classic_request("stat/sta", local=local)
    clients = [c for c in sta_data.get("data", []) if not c.get("is_wired")]
    
    if not clients:
        print("No wireless clients found.")
        return
    
    # Get all APs for name lookup
    dev_data = _classic_request("stat/device", local=local)
    ap_lookup = {}
    for d in dev_data.get("data", []):
        if d.get("type") == "uap":
            ap_lookup[d.get("mac", "").lower()] = d.get("name") or d.get("hostname") or d.get("mac", "")
    
    # Group clients by AP
    ap_clients: Dict[str, List[Dict]] = {}
    for client in clients:
        ap_mac = (client.get("ap_mac") or "").lower()
        ap_name = ap_lookup.get(ap_mac, ap_mac or "Unknown")
        
        if ap_name not in ap_clients:
            ap_clients[ap_name] = []
        ap_clients[ap_name].append(client)
    
    # Filter by AP name if specified
    ap_filter = getattr(args, 'ap', None)
    if ap_filter:
        filtered = {}
        for ap_name, clients_list in ap_clients.items():
            if ap_filter.lower() in ap_name.lower():
                filtered[ap_name] = clients_list
        ap_clients = filtered
        
        if not ap_clients:
            print(f"No AP matching '{ap_filter}' found with connected clients")
            return
    
    if args.json:
        print(json.dumps(ap_clients, indent=2))
        return
    
    # Display
    total_clients = sum(len(clients) for clients in ap_clients.values())
    print(f"\n=== Wireless Clients by AP ({total_clients} total) ===\n")
    
    for ap_name in sorted(ap_clients.keys()):
        clients_list = ap_clients[ap_name]
        print(f"{ap_name} ({len(clients_list)} clients)")
        
        # Sort by signal strength
        clients_list.sort(key=lambda c: c.get("signal", -100), reverse=True)
        
        for client in clients_list:
            name = client.get("name") or client.get("hostname") or "(unnamed)"
            ip = client.get("ip", "—")
            signal = client.get("signal")
            channel = client.get("channel", "?")
            radio = client.get("radio", "")
            band = "5 GHz" if radio == "na" else "2.4 GHz" if radio == "ng" else radio
            
            raw_rate = client.get("tx_rate") or client.get("rx_rate")
            rate = round(raw_rate / 1000) if raw_rate and raw_rate > 1000 else raw_rate
            
            signal_str = f"{signal} dBm" if signal is not None else "—"
            rate_str = f"{rate} Mbps" if rate else "—"
            
            print(f"  {name}")
            print(f"    IP: {ip}  Signal: {signal_str}  Ch: {channel} ({band})  Rate: {rate_str}")
        
        print()


def cmd_firmware_status(args):
    """Show firmware versions and update availability."""
    local = getattr(args, 'local', False)
    
    # Get all devices
    data = _classic_request("stat/device", local=local)
    devices = data.get("data", [])
    
    if args.json:
        print(json.dumps(devices, indent=2))
        return
    
    print(f"\n=== Firmware Status ({len(devices)} devices) ===\n")
    
    # Check for auto-upgrade setting
    # Note: This is typically in site settings, not easily accessible via classic API
    # We'll show device-level info only
    
    for device in devices:
        name = device.get("name") or device.get("hostname") or "N/A"
        model = device.get("model", "N/A")
        version = device.get("version", "N/A")
        upgradable = device.get("upgradable", False)
        upgrade_to = device.get("upgrade_to_firmware", "")
        
        status_icon = "⬆" if upgradable else "✓"
        
        print(f"{status_icon} {name} ({model})")
        print(f"  Current: {version}")
        if upgradable and upgrade_to:
            print(f"  Available: {upgrade_to}")
        print()
    
    # Try to get Cloud Key firmware from hosts API (if available)
    try:
        hosts_data = api_request("/v1/hosts")
        print("=== Cloud Key / Controller ===\n")
        for host in hosts_data.get("data", []):
            reported = host.get("reportedState", {})
            hostname = reported.get("hostname", "N/A")
            hw_name = reported.get("hardware", {}).get("name", "N/A")
            version = reported.get("version", "N/A")
            
            print(f"{hostname} ({hw_name})")
            print(f"  Firmware: {version}")
            print()
    except (SystemExit, Exception):
        pass  # Cloud API not available or failed


def cmd_list_devices_integration(args):
    """List devices via integration API (cloud connector or local)."""
    local = getattr(args, 'local', False)
    site_id = _resolve_site_id(args)

    all_devices = _integration_request_paginated(f"/v1/sites/{site_id}/devices", local=local)

    if not all_devices:
        print("No devices found.")
        return

    if args.json:
        print(json.dumps(all_devices, indent=2))
        return

    print(f"\n=== Site Devices ({len(all_devices)}) ===\n")

    for device in all_devices:
        name = device.get("name", "N/A")
        model = device.get("model", "N/A")
        state = device.get("state", "N/A")
        ip = device.get("ipAddress", "N/A")
        mac = device.get("macAddress", "N/A")
        fw = device.get("firmwareVersion", "N/A")
        updatable = device.get("firmwareUpdatable", False)
        features = device.get("features", [])
        if isinstance(features, dict):
            features = list(features.keys())

        state_icon = "🟢" if state == "ONLINE" else "🔴" if state == "OFFLINE" else "🟡"
        update_note = " ⬆" if updatable else ""

        print(f"{state_icon} {name} ({model}){update_note}")
        print(f"  IP: {ip}  MAC: {mac}")
        print(f"  Firmware: {fw}  Features: {', '.join(features) if features else 'N/A'}")
        print()


# ---------------------------------------------------------------------------
# main / argparse
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="UniFi Site Manager API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true",
                        help="Output raw JSON response")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Cloud API commands ---

    parser_hosts = subparsers.add_parser("list-hosts",
                                          help="List all UniFi controllers/hosts")
    parser_hosts.set_defaults(func=cmd_list_hosts)

    parser_sites = subparsers.add_parser("list-sites",
                                          help="List all sites with statistics")
    parser_sites.set_defaults(func=cmd_list_sites)

    parser_devices = subparsers.add_parser("list-devices",
                                            help="List all network devices (cloud API)")
    parser_devices.set_defaults(func=cmd_list_devices)

    parser_aps = subparsers.add_parser("list-aps",
                                        help="List access points only (cloud API)")
    parser_aps.set_defaults(func=cmd_list_aps)

    # --- Integration API commands (cloud connector + local) ---

    parser_clients = subparsers.add_parser("list-clients",
                                            help="List connected clients")
    parser_clients.add_argument("--site", default=None,
                                 help="Site ID (auto-detected if only one site)")
    parser_clients.add_argument("--detailed", action="store_true",
                                 help="Show detailed stats via classic API (local only)")
    parser_clients.add_argument("--local", action="store_true",
                                 help="Force local gateway access")
    parser_clients.set_defaults(func=cmd_list_clients)

    parser_networks = subparsers.add_parser("list-networks",
                                             help="List networks on a site")
    parser_networks.add_argument("--site", default=None,
                                  help="Site ID (auto-detected if only one site)")
    parser_networks.add_argument("--local", action="store_true",
                                  help="Force local gateway access")
    parser_networks.set_defaults(func=cmd_list_networks)

    parser_site_devices = subparsers.add_parser("list-site-devices",
                                                  help="List devices via integration API (richer detail)")
    parser_site_devices.add_argument("--site", default=None,
                                      help="Site ID (auto-detected if only one site)")
    parser_site_devices.add_argument("--local", action="store_true",
                                      help="Force local gateway access")
    parser_site_devices.set_defaults(func=cmd_list_devices_integration)

    parser_device = subparsers.add_parser("get-device",
                                           help="Get detailed info about a specific device")
    parser_device.add_argument("device_id", help="Device ID")
    parser_device.add_argument("--site", default=None,
                                help="Site ID (auto-detected if only one site)")
    parser_device.add_argument("--local", action="store_true",
                                help="Force local gateway access")
    parser_device.set_defaults(func=cmd_get_device)

    parser_client = subparsers.add_parser("get-client",
                                           help="Get detailed info about a specific client")
    parser_client.add_argument("client_id", help="Client ID")
    parser_client.add_argument("--site", default=None,
                                help="Site ID (auto-detected if only one site)")
    parser_client.add_argument("--local", action="store_true",
                                help="Force local gateway access")
    parser_client.set_defaults(func=cmd_get_client)

    # --- Classic API commands (auto-routed: local when reachable, cloud connector when remote) ---

    parser_known = subparsers.add_parser("list-known-clients",
                                          help="List all known clients (current + historical)")
    parser_known.add_argument("--named", action="store_true",
                               help="Show only clients with custom names")
    parser_known.add_argument("--local", action="store_true",
                               help="Force local gateway access")
    parser_known.set_defaults(func=cmd_list_known_clients)

    parser_events = subparsers.add_parser("list-events",
                                           help="List site events (roaming, AP changes, etc.)")
    parser_events.add_argument("--filter", default=None,
                                help="Filter by event key (e.g. Roam, AP, Channel)")
    parser_events.add_argument("--mac", default=None,
                                help="Filter by client or AP MAC address")
    parser_events.add_argument("--local", action="store_true",
                                help="Force local gateway access")
    parser_events.set_defaults(func=cmd_list_events)

    # --- Configuration commands ---

    parser_wlan_config = subparsers.add_parser("get-wlan-config",
                                                help="Show WLAN configuration")
    parser_wlan_config.add_argument("--ssid", default=None,
                                     help="Filter by SSID name")
    parser_wlan_config.add_argument("--local", action="store_true",
                                     help="Force local gateway access")
    parser_wlan_config.set_defaults(func=cmd_get_wlan_config)

    parser_set_wlan = subparsers.add_parser("set-wlan",
                                             help="Set WLAN properties")
    parser_set_wlan.add_argument("--ssid", required=True,
                                  help="SSID name")
    parser_set_wlan.add_argument("--fast-roaming", choices=["on", "off"],
                                  help="Enable/disable fast roaming")
    parser_set_wlan.add_argument("--bss-transition", choices=["on", "off"],
                                  help="Enable/disable BSS transition")
    parser_set_wlan.add_argument("--pmf", choices=["disabled", "optional", "required"],
                                  help="Set PMF (Protected Management Frames) mode")
    parser_set_wlan.add_argument("--band-steering", choices=["off", "prefer_5g", "balance"],
                                  help="Set band steering mode")
    parser_set_wlan.add_argument("--local", action="store_true",
                                  help="Force local gateway access")
    parser_set_wlan.set_defaults(func=cmd_set_wlan)

    parser_radio_config = subparsers.add_parser("get-radio-config",
                                                 help="Show radio configuration for APs")
    parser_radio_config.add_argument("--ap", default=None,
                                      help="Filter by AP name")
    parser_radio_config.add_argument("--local", action="store_true",
                                      help="Force local gateway access")
    parser_radio_config.set_defaults(func=cmd_get_radio_config)

    parser_set_radio = subparsers.add_parser("set-radio",
                                              help="Set radio properties on an AP")
    parser_set_radio.add_argument("--ap", required=True,
                                   help="AP name")
    parser_set_radio.add_argument("--band", required=True, choices=["2.4", "5"],
                                   help="Radio band (2.4 or 5 GHz)")
    parser_set_radio.add_argument("--channel",
                                   help="Channel number or 'auto'")
    parser_set_radio.add_argument("--width", choices=["20", "40", "80", "160"],
                                   help="Channel width in MHz")
    parser_set_radio.add_argument("--power", choices=["low", "medium", "high", "auto"],
                                   help="TX power level")
    parser_set_radio.add_argument("--local", action="store_true",
                                   help="Force local gateway access")
    parser_set_radio.set_defaults(func=cmd_set_radio)

    parser_set_client = subparsers.add_parser("set-client",
                                               help="Set properties on a client")
    parser_set_client.add_argument("mac", help="Client MAC address")
    parser_set_client.add_argument("--name", default=None,
                                    help="Display name")
    parser_set_client.add_argument("--fixed-ip", default=None,
                                    help="Fixed IP address (or 'off' to disable)")
    parser_set_client.add_argument("--dns-record", default=None,
                                    help="Local DNS hostname (or 'off' to disable)")
    parser_set_client.add_argument("--pin-ap", default=None,
                                    help="Pin to AP by name (or 'off' to disable)")
    parser_set_client.add_argument("--local", action="store_true",
                                    help="Force local gateway access")
    parser_set_client.set_defaults(func=cmd_set_client)

    parser_label = subparsers.add_parser("label-client",
                                          help="Set custom name for a client (shorthand for set-client --name)")
    parser_label.add_argument("mac", help="Client MAC address")
    parser_label.add_argument("label_name", metavar="name", help="Custom name for the client")
    parser_label.add_argument("--local", action="store_true",
                               help="Force local gateway access")
    parser_label.set_defaults(func=cmd_label_client)

    parser_ap_clients = subparsers.add_parser("list-ap-clients",
                                               help="List wireless clients grouped by AP")
    parser_ap_clients.add_argument("--ap", default=None,
                                    help="Filter by AP name")
    parser_ap_clients.add_argument("--local", action="store_true",
                                    help="Force local gateway access")
    parser_ap_clients.set_defaults(func=cmd_list_ap_clients)

    parser_get_dns = subparsers.add_parser("get-network-dns",
                                              help="Show DHCP DNS config for networks")
    parser_get_dns.add_argument("network", nargs="?", default=None,
                                 help="Network name (omit for all)")
    parser_get_dns.add_argument("--local", action="store_true",
                                 help="Force local gateway access")
    parser_get_dns.set_defaults(func=cmd_get_network_dns)

    parser_set_dns = subparsers.add_parser("set-network-dns",
                                              help="Set or show DHCP DNS servers for a network")
    parser_set_dns.add_argument("network", help="Network name (e.g. 'Default', 'LAN2')")
    parser_set_dns.add_argument("--dns1", default=None,
                                 help="Primary DNS server (or 'auto' to disable override)")
    parser_set_dns.add_argument("--dns2", default=None,
                                 help="Secondary DNS (or 'off' to clear)")
    parser_set_dns.add_argument("--dns3", default=None,
                                 help="Tertiary DNS (or 'off' to clear)")
    parser_set_dns.add_argument("--dns4", default=None,
                                 help="Quaternary DNS (or 'off' to clear)")
    parser_set_dns.add_argument("--local", action="store_true",
                                 help="Force local gateway access")
    parser_set_dns.set_defaults(func=cmd_set_network_dns)

    parser_firmware = subparsers.add_parser("firmware-status",
                                             help="Show firmware versions and update availability")
    parser_firmware.add_argument("--local", action="store_true",
                                  help="Force local gateway access")
    parser_firmware.set_defaults(func=cmd_firmware_status)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
