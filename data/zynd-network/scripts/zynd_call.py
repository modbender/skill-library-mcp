#!/usr/bin/env python3
"""
Call another AI agent on the Zynd Network.

Sends a message to a target agent's webhook endpoint and waits for a response.
Supports automatic x402 micropayments for paid agents.

Usage:
    python3 zynd_call.py --webhook "http://host:5003/webhook/sync" --message "Compare AAPL vs GOOGL"
    python3 zynd_call.py --webhook "http://host:5003/webhook/sync" --message "Analyze data" --pay
    python3 zynd_call.py --webhook "http://host:5003/webhook/sync" --message "Hello" --timeout 30
"""

import argparse
import json
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Call another AI agent on the Zynd Network"
    )
    parser.add_argument(
        "--webhook",
        required=True,
        help="Target agent's webhook URL (from search results)",
    )
    parser.add_argument(
        "--message", required=True, help="The task or question to send to the agent"
    )
    parser.add_argument(
        "--pay",
        action="store_true",
        help="Enable x402 micropayment (required for paid agents)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Response timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--config-dir",
        required=True,
        help="Config directory with agent identity (e.g., .agent-my-bot)",
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
        help="Output raw JSON response",
    )

    args = parser.parse_args()

    # Get API key
    api_key = os.environ.get("ZYND_API_KEY")
    if not api_key:
        print("ERROR: ZYND_API_KEY environment variable is not set.")
        print("Get your API key from https://dashboard.zynd.ai")
        sys.exit(1)

    # Ensure webhook URL points to sync endpoint
    webhook_url = args.webhook
    if not webhook_url.endswith("/sync"):
        if webhook_url.endswith("/webhook"):
            webhook_url = webhook_url + "/sync"
        elif not "/webhook" in webhook_url:
            webhook_url = webhook_url.rstrip("/") + "/webhook/sync"

    try:
        from zyndai_agent.config_manager import ConfigManager
        from zyndai_agent.message import AgentMessage
        from zyndai_agent.payment import X402PaymentProcessor
        import requests

        # Load agent config (must have registered first)
        config = ConfigManager.load_config(args.config_dir)
        if config is None:
            print("ERROR: No agent identity found.")
            print(
                f'Register first with: python3 zynd_register.py --name \'My Agent\' --capabilities \'{{"ai":["nlp"],"protocols":["http"],"services":["general"]}}\''
            )
            print(f"(Looking in: {args.config_dir}/config.json)")
            sys.exit(1)

        agent_id = config["id"]
        identity_credential = config["did"]
        secret_seed = config["seed"]

        # Create message
        message = AgentMessage(
            content=args.message,
            sender_id=agent_id,
            message_type="query",
            sender_did=identity_credential,
        )

        print(f"Calling agent at: {webhook_url}")
        print(
            f"Message: {args.message[:100]}{'...' if len(args.message) > 100 else ''}"
        )
        if args.pay:
            print(f"Payment: x402 enabled")
        print(f"Timeout: {args.timeout}s")
        print()

        # Send the request
        if args.pay:
            # Use x402 payment processor
            processor = X402PaymentProcessor(secret_seed)
            response = processor.post(
                webhook_url,
                json=message.to_dict(),
                headers={"Content-Type": "application/json"},
                timeout=args.timeout,
            )

            # Check for payment info
            payment_response = response.headers.get("x-payment-response")
            if payment_response:
                print(f"Payment processed: {payment_response}")

            processor.close()
        else:
            # Direct HTTP POST (no payment)
            response = requests.post(
                webhook_url,
                json=message.to_dict(),
                headers={"Content-Type": "application/json"},
                timeout=args.timeout,
            )

        # Handle response
        if response.status_code == 200:
            result = response.json()

            if args.output_json:
                print(json.dumps(result, indent=2, default=str))
            else:
                agent_response = result.get(
                    "response", result.get("content", "No response content")
                )
                status = result.get("status", "unknown")
                message_id = result.get("message_id", "N/A")

                print("=" * 60)
                print("  AGENT RESPONSE")
                print("=" * 60)
                print()
                print(agent_response)
                print()
                print("=" * 60)
                print(f"  Status: {status} | Message ID: {message_id}")
                print("=" * 60)

        elif response.status_code == 402:
            print("ERROR: Payment required.")
            print("This agent charges for its services. Use --pay flag:")
            print(
                f'  python3 zynd_call.py --webhook "{args.webhook}" --message "{args.message}" --pay'
            )
            print()
            print("Make sure your agent has USDC on Base Sepolia.")
            print("Get test tokens from https://dashboard.zynd.ai")
            sys.exit(1)

        elif response.status_code == 408:
            print("ERROR: Agent did not respond within the timeout period.")
            print("Try increasing the timeout: --timeout 120")
            sys.exit(1)

        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            sys.exit(1)

    except ImportError:
        print("ERROR: zyndai-agent SDK is not installed.")
        print("Run the setup script first: bash scripts/setup.sh")
        sys.exit(1)
    except Exception as e:
        if "ConnectionError" in type(e).__name__ or "Connection refused" in str(e):
            print(f"ERROR: Could not connect to agent at {webhook_url}")
            print("The target agent may be offline.")
        elif "Timeout" in type(e).__name__:
            print(f"ERROR: Request timed out after {args.timeout} seconds.")
            print("The agent may be busy. Try again or increase --timeout.")
        else:
            print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
