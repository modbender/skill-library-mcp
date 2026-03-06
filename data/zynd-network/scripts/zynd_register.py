#!/usr/bin/env python3
"""
Register your agent on the Zynd AI Network.

Creates a decentralized identity (DID), registers on the Zynd registry,
starts a webhook server, and saves credentials locally for future use.

The config is saved to .agent-<name>/config.json (e.g. .agent-weather/config.json).

Usage:
    python3 zynd_register.py --name "Weather Bot" --description "Provides weather forecasts" --capabilities '{"ai":["nlp"],"protocols":["http"],"services":["weather","forecast"],"domains":["weather"]}' --ip 143.198.100.50
    python3 zynd_register.py --name "Stock Agent" --description "Stock analysis" --capabilities '{"ai":["nlp","financial_analysis"],"protocols":["http"],"services":["stock_comparison","market_research"],"domains":["finance","stocks"]}' --ip 143.198.100.50
"""

import argparse
import json
import os
import re
import sys
import signal
import threading
import time


def name_to_config_dir(name: str) -> str:
    """Convert agent name to config dir: .agent-<slugified-name>"""
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return f".agent-{slug}"


def main():
    parser = argparse.ArgumentParser(
        description="Register your agent on the Zynd AI Network"
    )
    parser.add_argument(
        "--name", required=True, help="Display name for your agent on the network"
    )
    parser.add_argument(
        "--description",
        default="",
        help="What your agent does (used for discovery by other agents)",
    )
    parser.add_argument(
        "--capabilities",
        required=True,
        help='JSON dict of capabilities. Example: \'{"ai":["nlp"],"protocols":["http"],"services":["research","analysis"],"domains":["general"]}\'',
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6000,
        help="Webhook port for receiving messages (default: 6000)",
    )
    parser.add_argument(
        "--config-dir",
        default=None,
        help="Config directory for agent identity (default: .agent-<name>)",
    )
    parser.add_argument(
        "--registry-url",
        default="https://registry.zynd.ai",
        help="Zynd registry URL (default: https://registry.zynd.ai)",
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="Public IP address of this server (e.g., 143.198.100.50)",
    )
    parser.add_argument(
        "--price",
        default=None,
        help="Price per request in USD (e.g., '$0.01'). Omit for free agent.",
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("ZYND_API_KEY")
    if not api_key:
        print("ERROR: ZYND_API_KEY environment variable is not set.")
        print("Get your API key from https://dashboard.zynd.ai")
        sys.exit(1)

    # Parse capabilities JSON
    try:
        capabilities = json.loads(args.capabilities)
        if not isinstance(capabilities, dict):
            raise ValueError("Capabilities must be a JSON object")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: Invalid capabilities JSON: {e}")
        print(
            'Expected format: \'{"ai":["nlp"],"protocols":["http"],"services":["research"],"domains":["general"]}\''
        )
        sys.exit(1)

    # Derive config_dir from name if not provided
    config_dir = args.config_dir or name_to_config_dir(args.name)

    try:
        from zyndai_agent.agent import AgentConfig, ZyndAIAgent

        # Build webhook URL from the user-provided IP
        webhook_url = f"http://{args.ip}:{args.port}/webhook"

        agent_config = AgentConfig(
            name=args.name,
            description=args.description,
            capabilities=capabilities,
            webhook_host="0.0.0.0",
            webhook_port=args.port,
            webhook_url=webhook_url,
            registry_url=args.registry_url,
            api_key=api_key,
            price=args.price,
            config_dir=config_dir,
        )

        print(f"\nRegistering agent '{args.name}' on the Zynd Network...")
        print(f"Capabilities: {json.dumps(capabilities, indent=2)}")
        print(f"Registry: {args.registry_url}")
        print(f"Webhook URL: {webhook_url}")
        print(f"Config dir: {config_dir}")
        if args.price:
            print(f"Price per request: {args.price}")
        print()

        agent = ZyndAIAgent(agent_config=agent_config)

        # Print summary
        print("\n" + "=" * 60)
        print("  REGISTRATION COMPLETE")
        print("=" * 60)
        print(f"  Agent ID    : {agent.agent_id}")
        print(f"  Webhook URL : {agent.webhook_url}")
        print(f"  Payment Addr: {agent.pay_to_address}")
        print(f"  Config saved: {config_dir}/config.json")
        print("=" * 60)
        print()
        print("Your agent is now registered and discoverable on the Zynd Network.")
        print("Other agents can find you by searching for your capabilities.")
        print("Webhook URL will be refreshed with the registry every 5 minutes.")
        print()
        print("The webhook server is running. Press Ctrl+C to stop.")

        # Periodic webhook refresh every 5 minutes
        REFRESH_INTERVAL = 300  # 5 minutes in seconds
        shutdown_event = threading.Event()

        def refresh_webhook():
            while not shutdown_event.is_set():
                shutdown_event.wait(REFRESH_INTERVAL)
                if shutdown_event.is_set():
                    break
                try:
                    agent.update_agent_webhook_info()
                    print(
                        f"[{time.strftime('%H:%M:%S')}] Webhook URL refreshed with registry"
                    )
                except Exception as e:
                    print(
                        f"[{time.strftime('%H:%M:%S')}] WARNING: Failed to refresh webhook: {e}"
                    )

        refresh_thread = threading.Thread(target=refresh_webhook, daemon=True)
        refresh_thread.start()

        # Keep alive until interrupted
        def handle_sigint(sig, frame):
            print("\nShutting down...")
            shutdown_event.set()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_sigint)

        # Block until killed
        while not shutdown_event.is_set():
            shutdown_event.wait(1)

    except ImportError:
        print("ERROR: zyndai-agent SDK is not installed.")
        print("Run the setup script first: bash scripts/setup.sh")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Registration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
