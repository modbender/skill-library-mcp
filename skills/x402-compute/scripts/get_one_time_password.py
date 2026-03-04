#!/usr/bin/env python3
"""
x402Compute - Retrieve one-time root password fallback for an instance.

Usage:
  python get_one_time_password.py <instance_id>

Notes:
- This works only once per instance.
- Prefer SSH key access whenever possible.
"""

import json
import sys

import requests

from wallet_signing import create_compute_auth_headers

BASE_URL = "https://compute.x402layer.cc"


def get_one_time_password(instance_id: str) -> dict:
    path = f"/compute/instances/{instance_id}/password"
    auth_headers = create_compute_auth_headers("POST", path, "")

    response = requests.post(
        f"{BASE_URL}{path}",
        headers={
            "Content-Type": "application/json",
            **auth_headers,
        },
        timeout=30,
    )

    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}

    data = response.json()
    access = data.get("access", {})

    print("One-time access credentials:")
    print(f"  Username: {access.get('username', 'root')}")
    print(f"  IP:       {access.get('ip_address', 'pending')}")
    print(f"  Password: {access.get('password', 'N/A')}")
    print("This password is shown once by API. Store it securely.")

    return data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_one_time_password.py <instance_id>")
        sys.exit(1)

    result = get_one_time_password(sys.argv[1])
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
