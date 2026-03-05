#!/usr/bin/env python3
"""
x402Compute — Create an API key for agent access.

Usage:
  python create_api_key.py [--label LABEL]
"""

import argparse
import json
import sys

import requests

from wallet_signing import create_compute_auth_headers

BASE_URL = "https://compute.x402layer.cc"


def create_api_key(label: str | None = None) -> dict:
    body = {"label": label} if label else {}
    body_json = json.dumps(body, separators=(",", ":")) if body else ""
    path = "/compute/api-keys"
    auth_headers = create_compute_auth_headers("POST", path, body_json)

    response = requests.post(
        f"{BASE_URL}/compute/api-keys",
        data=body_json if body_json else None,
        headers={
            "Content-Type": "application/json",
            **auth_headers,
        },
        timeout=30,
    )

    if response.status_code != 201:
        return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}

    return response.json()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a compute API key")
    parser.add_argument("--label", default=None, help="Optional key label")
    args = parser.parse_args()

    result = create_api_key(label=args.label)
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)

    print("API Key created:")
    print(f"  ID:      {result.get('id')}")
    print(f"  Label:   {result.get('label') or 'N/A'}")
    print(f"  Key:     {result.get('api_key')}")
    print(f"  Created: {result.get('created_at')}")
    print("Store this key securely; it will not be shown again.")
