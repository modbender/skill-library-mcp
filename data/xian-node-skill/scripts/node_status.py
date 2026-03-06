#!/usr/bin/env python3
"""Check Xian node sync status and display progress."""

import argparse
import json
import sys
from urllib.request import urlopen
from urllib.error import URLError


def get_status(rpc_url: str) -> dict:
    """Fetch node status from RPC endpoint."""
    try:
        with urlopen(f"{rpc_url}/status", timeout=5) as resp:
            return json.load(resp)["result"]
    except URLError as e:
        print(f"Error connecting to {rpc_url}: {e}")
        sys.exit(1)


def format_height(height: int) -> str:
    """Format block height with commas."""
    return f"{height:,}"


def main():
    parser = argparse.ArgumentParser(description="Check Xian node status")
    parser.add_argument(
        "--rpc", 
        default="http://localhost:26657",
        help="RPC endpoint (default: http://localhost:26657)"
    )
    parser.add_argument(
        "--json", 
        action="store_true",
        help="Output raw JSON"
    )
    args = parser.parse_args()

    status = get_status(args.rpc)
    
    if args.json:
        print(json.dumps(status, indent=2))
        return

    node_info = status["node_info"]
    sync_info = status["sync_info"]
    
    current = int(sync_info["latest_block_height"])
    catching_up = sync_info["catching_up"]
    
    print(f"Node:     {node_info['moniker']} ({node_info['id'][:8]}...)")
    print(f"Network:  {node_info['network']}")
    print(f"Height:   {format_height(current)}")
    print(f"Syncing:  {'Yes' if catching_up else 'No (fully synced)'}")
    print(f"Time:     {sync_info['latest_block_time']}")
    
    if catching_up:
        # Try to get peer info for max height estimation
        try:
            with urlopen(f"{args.rpc}/net_info", timeout=5) as resp:
                net = json.load(resp)["result"]
                peers = int(net["n_peers"])
                print(f"Peers:    {peers}")
        except:
            pass


if __name__ == "__main__":
    main()
