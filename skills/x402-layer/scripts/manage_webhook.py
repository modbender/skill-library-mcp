#!/usr/bin/env python3
"""
x402 Endpoint Webhook Management

Set, update, or remove a webhook URL on an agent-created endpoint.
When a webhook is configured, your endpoint receives payment.succeeded
events at the specified HTTPS URL.

Usage:
    python manage_webhook.py set <slug> <webhook_url>
    python manage_webhook.py remove <slug>
    python manage_webhook.py info <slug>

Examples:
    python manage_webhook.py set my-api https://my-server.com/webhook
    python manage_webhook.py remove my-api
    python manage_webhook.py info my-api

Requires: X_API_KEY or API_KEY environment variable.
"""

import argparse
import json
import os
import sys
from typing import Optional

import requests

API_BASE = "https://api.x402layer.cc"


def _load_api_key() -> str:
    api_key = os.getenv("X_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv  # type: ignore
            load_dotenv()
            api_key = os.getenv("X_API_KEY") or os.getenv("API_KEY")
        except Exception:
            pass
    if not api_key:
        raise ValueError("Set X_API_KEY (or API_KEY) environment variable")
    return api_key


def set_webhook(slug: str, webhook_url: str) -> dict:
    """Set or update the webhook URL for an endpoint."""
    api_key = _load_api_key()
    response = requests.patch(
        f"{API_BASE}/agent/endpoints",
        params={"slug": slug},
        json={"webhook_url": webhook_url},
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code == 200:
        result = response.json()
        webhook = result.get("webhook", {})
        if webhook.get("signing_secret"):
            print(f"\n⚠️  SAVE THIS SECRET — it will not be shown again:")
            print(f"   {webhook['signing_secret']}\n")
        return result
    return {"error": f"Status {response.status_code}", "response": response.text}


def remove_webhook(slug: str) -> dict:
    """Remove the webhook URL from an endpoint."""
    api_key = _load_api_key()
    response = requests.patch(
        f"{API_BASE}/agent/endpoints",
        params={"slug": slug},
        json={"webhook_url": None},
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()
    return {"error": f"Status {response.status_code}", "response": response.text}


def get_webhook_info(slug: str) -> dict:
    """Check if an endpoint has a webhook configured."""
    api_key = _load_api_key()
    response = requests.get(
        f"{API_BASE}/agent/endpoints",
        params={"slug": slug},
        headers={"X-API-Key": api_key, "Accept": "application/json"},
        timeout=30,
    )
    if response.status_code == 200:
        data = response.json()
        endpoint = data.get("endpoint", {})
        return {
            "slug": slug,
            "webhook_configured": bool(endpoint.get("webhook_url")),
            "webhook_url": endpoint.get("webhook_url"),
        }
    return {"error": f"Status {response.status_code}", "response": response.text}


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage x402 endpoint webhooks")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    set_parser = subparsers.add_parser("set", help="Set or update webhook URL")
    set_parser.add_argument("slug", help="Endpoint slug")
    set_parser.add_argument("webhook_url", help="HTTPS URL to receive events")

    remove_parser = subparsers.add_parser("remove", help="Remove webhook")
    remove_parser.add_argument("slug", help="Endpoint slug")

    info_parser = subparsers.add_parser("info", help="Check webhook status")
    info_parser.add_argument("slug", help="Endpoint slug")

    args = parser.parse_args()

    if args.command == "set":
        result = set_webhook(args.slug, args.webhook_url)
    elif args.command == "remove":
        result = remove_webhook(args.slug)
    elif args.command == "info":
        result = get_webhook_info(args.slug)
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        sys.exit(1)
