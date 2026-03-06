#!/usr/bin/env python3
"""
Manage Gateway via hummingbot-api.

Usage:
    # Check Gateway status
    python manage_gateway.py status

    # Start/stop/restart Gateway
    python manage_gateway.py start --passphrase mypassword
    python manage_gateway.py stop
    python manage_gateway.py restart

    # Get Gateway logs
    python manage_gateway.py logs [--limit 100]

    # List all networks
    python manage_gateway.py networks

    # Get network config
    python manage_gateway.py network solana-mainnet-beta

    # Set custom RPC node (avoid rate limits)
    python manage_gateway.py network solana-mainnet-beta --node-url https://my-rpc.example.com

Environment:
    HUMMINGBOT_API_URL - API base URL (default: http://localhost:8000)
    API_USER - API username (default: admin)
    API_PASS - API password (default: admin)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import base64


def load_env():
    """Load environment from .env files."""
    for path in ["hummingbot-api/.env", os.path.expanduser("~/.hummingbot/.env"), ".env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


def get_api_config():
    """Get API configuration from environment."""
    load_env()
    return {
        "url": os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000"),
        "user": os.environ.get("API_USER", "admin"),
        "password": os.environ.get("API_PASS", "admin"),
    }


def api_request(method: str, endpoint: str, data=None) -> dict:
    """Make authenticated API request."""
    config = get_api_config()
    url = f"{config['url']}{endpoint}"

    # Basic auth
    credentials = base64.b64encode(f"{config['user']}:{config['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        if error_body:
            try:
                print(json.dumps(json.loads(error_body), indent=2), file=sys.stderr)
            except json.JSONDecodeError:
                print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Cannot connect to API at {config['url']}: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_status(args):
    """Get Gateway status."""
    result = api_request("GET", "/gateway/status")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        is_running = result.get("running", False)
        container_id = result.get("container_id", "")
        image = result.get("image", "")
        port = result.get("port", "")

        if is_running:
            print(f"✓ Gateway is running")
            if container_id:
                print(f"  Container: {container_id[:12]}")
            if image:
                print(f"  Image: {image}")
            if port:
                print(f"  Port: {port}")
        else:
            print(f"✗ Gateway is not running")


def start_gateway(args):
    """Start Gateway."""
    # GatewayConfig requires passphrase
    data = {
        "passphrase": args.passphrase,
        "image": args.image,
        "port": args.port,
        "dev_mode": True,
    }

    print("Starting Gateway...")
    result = api_request("POST", "/gateway/start", data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print("✓ Gateway started successfully")
        else:
            print(f"Response: {result.get('message', result)}")


def stop_gateway(args):
    """Stop Gateway."""
    print("Stopping Gateway...")
    result = api_request("POST", "/gateway/stop")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print("✓ Gateway stopped")
        else:
            print(f"Response: {result.get('message', result)}")


def restart_gateway(args):
    """Restart Gateway."""
    print("Restarting Gateway...")
    # Restart can optionally take config
    data = None
    if args.passphrase:
        data = {
            "passphrase": args.passphrase,
            "image": args.image or "hummingbot/gateway:latest",
            "port": args.port or 15888,
            "dev_mode": True,
        }

    result = api_request("POST", "/gateway/restart", data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            print("✓ Gateway restarted successfully")
        else:
            print(f"Response: {result.get('message', result)}")


def get_logs(args):
    """Get Gateway logs."""
    endpoint = f"/gateway/logs?tail={args.limit}"
    result = api_request("GET", endpoint)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            logs = result.get("logs", "")
            if isinstance(logs, str):
                print(logs)
            elif isinstance(logs, list):
                for line in logs:
                    print(line)
        else:
            print(f"Error: {result.get('message', result)}")


def list_networks(args):
    """List all available networks."""
    result = api_request("GET", "/gateway/networks")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        networks = result.get("networks", [])
        count = result.get("count", len(networks))

        print(f"Available Networks ({count}):")
        print("-" * 40)

        # Group by chain
        by_chain = {}
        for net in networks:
            chain = net.get("chain", "unknown")
            if chain not in by_chain:
                by_chain[chain] = []
            by_chain[chain].append(net.get("network_id", net.get("network", "")))

        for chain, nets in sorted(by_chain.items()):
            print(f"\n{chain}:")
            for net_id in nets:
                print(f"  - {net_id}")


def get_network(args):
    """Get or update network config."""
    if args.node_url:
        # Update network config
        data = {"nodeURL": args.node_url}
        print(f"Updating network {args.network_id}...")
        result = api_request("POST", f"/gateway/networks/{args.network_id}", data)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success"):
                print(f"✓ Network {args.network_id} updated")
                print(f"  nodeURL: {args.node_url}")
                if result.get("restart_required"):
                    print(f"\n  ⚠ Restart Gateway for changes to take effect:")
                    print(f"    python manage_gateway.py restart")
            else:
                print(f"Response: {result.get('message', result)}")
    else:
        # Get network config
        result = api_request("GET", f"/gateway/networks/{args.network_id}")

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Network: {args.network_id}")
            print("-" * 40)

            for key, value in result.items():
                if key in ("node_url", "nodeURL"):
                    print(f"  Node URL: {value}")
                elif key in ("token_list_source", "tokenListSource"):
                    print(f"  Token List: {value}")
                elif key in ("native_currency_symbol", "nativeCurrencySymbol"):
                    print(f"  Native Currency: {value}")
                elif not key.startswith("_"):
                    print(f"  {key}: {value}")


def main():
    parser = argparse.ArgumentParser(description="Manage Gateway via hummingbot-api")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # status command
    status_parser = subparsers.add_parser("status", help="Get Gateway status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")
    status_parser.set_defaults(func=get_status)

    # start command
    start_parser = subparsers.add_parser("start", help="Start Gateway")
    start_parser.add_argument("--passphrase", default="hummingbot", help="Gateway passphrase (default: hummingbot)")
    start_parser.add_argument("--image", default="hummingbot/gateway:latest", help="Docker image")
    start_parser.add_argument("--port", type=int, default=15888, help="Port (default: 15888)")
    start_parser.add_argument("--json", action="store_true", help="Output as JSON")
    start_parser.set_defaults(func=start_gateway)

    # stop command
    stop_parser = subparsers.add_parser("stop", help="Stop Gateway")
    stop_parser.add_argument("--json", action="store_true", help="Output as JSON")
    stop_parser.set_defaults(func=stop_gateway)

    # restart command
    restart_parser = subparsers.add_parser("restart", help="Restart Gateway")
    restart_parser.add_argument("--passphrase", help="Gateway passphrase (optional, uses existing config if not provided)")
    restart_parser.add_argument("--image", help="Docker image")
    restart_parser.add_argument("--port", type=int, help="Port")
    restart_parser.add_argument("--json", action="store_true", help="Output as JSON")
    restart_parser.set_defaults(func=restart_gateway)

    # logs command
    logs_parser = subparsers.add_parser("logs", help="Get Gateway logs")
    logs_parser.add_argument("--limit", type=int, default=100, help="Number of log lines (default: 100)")
    logs_parser.add_argument("--json", action="store_true", help="Output as JSON")
    logs_parser.set_defaults(func=get_logs)

    # networks command (list all)
    networks_parser = subparsers.add_parser("networks", help="List all networks")
    networks_parser.add_argument("--json", action="store_true", help="Output as JSON")
    networks_parser.set_defaults(func=list_networks)

    # network command (get/update single network)
    network_parser = subparsers.add_parser("network", help="Get or update network config")
    network_parser.add_argument("network_id", help="Network ID (e.g., solana-mainnet-beta)")
    network_parser.add_argument("--node-url", help="Set custom RPC node URL")
    network_parser.add_argument("--json", action="store_true", help="Output as JSON")
    network_parser.set_defaults(func=get_network)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
