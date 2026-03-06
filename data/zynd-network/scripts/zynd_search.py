#!/usr/bin/env python3
"""
Search for AI agents on the Zynd Network by capability.

Uses semantic search across agent names, descriptions, and capabilities.
Returns agent details including webhook URLs for calling them.

Usage:
    python3 zynd_search.py "stock analysis"
    python3 zynd_search.py "weather forecast" --limit 5
    python3 zynd_search.py "KYC verification" --limit 3
"""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Search for AI agents on the Zynd Network"
    )
    parser.add_argument(
        "query",
        help="Search query (semantic search across name, description, capabilities)",
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of results (default: 10)"
    )
    parser.add_argument(
        "--registry-url",
        default="https://registry.zynd.ai",
        help="Zynd registry URL (default: https://registry.zynd.ai)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output raw JSON instead of formatted text",
    )

    args = parser.parse_args()

    try:
        from zyndai_agent.search import SearchAndDiscoveryManager

        search_manager = SearchAndDiscoveryManager(registry_url=args.registry_url)

        print(f'Searching Zynd Network for: "{args.query}"')
        print(f"Registry: {args.registry_url}")
        print()

        agents = search_manager.search_agents_by_keyword(
            keyword=args.query, limit=args.limit
        )

        if not agents:
            print("No agents found matching your query.")
            print("\nTry:")
            print("  - Using different keywords")
            print("  - Broadening your search terms")
            print("  - Checking https://dashboard.zynd.ai for available agents")
            sys.exit(0)

        if args.output_json:
            # Raw JSON output for programmatic use
            print(json.dumps(agents, indent=2, default=str))
            sys.exit(0)

        # Formatted output
        print(f"Found {len(agents)} agent(s):\n")
        print("-" * 70)

        for i, agent in enumerate(agents, 1):
            name = agent.get("name", "Unknown")
            description = agent.get("description", "No description")
            webhook_url = agent.get("httpWebhookUrl", "N/A")
            status = agent.get("status", "UNKNOWN")
            did_id = agent.get("didIdentifier", "N/A")
            capabilities = agent.get("capabilities", {})
            agent_id = agent.get("id", "N/A")

            print(f"\n  [{i}] {name}")
            print(f"      Description : {description[:120]}")
            print(f"      Status      : {status}")
            print(f"      Webhook URL : {webhook_url}")
            print(f"      Agent ID    : {agent_id}")
            print(
                f"      DID         : {did_id[:50]}..."
                if len(str(did_id)) > 50
                else f"      DID         : {did_id}"
            )

            if capabilities:
                if isinstance(capabilities, dict):
                    services = capabilities.get("services", [])
                    if services:
                        print(f"      Capabilities: {', '.join(services[:5])}")
                elif isinstance(capabilities, list):
                    print(
                        f"      Capabilities: {', '.join(str(c) for c in capabilities[:5])}"
                    )

        print("\n" + "-" * 70)
        print(f"\nTo call an agent, use:")
        print(f'  python3 zynd_call.py --webhook <webhook_url> --message "your task"')
        print()

    except ImportError:
        print("ERROR: zyndai-agent SDK is not installed.")
        print("Run the setup script first: bash scripts/setup.sh")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Search failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
