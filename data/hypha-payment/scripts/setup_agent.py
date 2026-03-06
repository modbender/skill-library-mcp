#!/usr/bin/env python3
"""
Quick setup for a new Hypha agent.
Generates a seed, derives identity + wallet, and announces on the mesh.

Usage:
    python3 scripts/setup_agent.py "my-unique-agent-name"
"""

import sys
import asyncio

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 setup_agent.py <agent-seed-phrase>")
        print("Example: python3 setup_agent.py 'my-cool-agent-v1'")
        sys.exit(1)

    seed_phrase = sys.argv[1]

    try:
        from hypha_sdk import SeedManager
    except ImportError:
        print("hypha-sdk not installed. Run: pip install hypha-sdk")
        sys.exit(1)

    sm = SeedManager.from_string(seed_phrase)

    print("=" * 50)
    print("  HYPHA Agent Identity")
    print("=" * 50)
    print(f"  Seed Phrase:  {seed_phrase}")
    print(f"  Node ID:      {sm.node_id_hex}")
    print(f"  Wallet:       {sm.wallet_address}")
    print(f"  Full Node ID: {sm.node_id.hex()}")
    print("=" * 50)
    print()
    print("Add to your agent config:")
    print(f'  agent = Agent(seed="{seed_phrase}")')
    print()
    print("Your wallet address (for receiving USDT):")
    print(f"  {sm.wallet_address}")


if __name__ == "__main__":
    main()
