#!/usr/bin/env python3
"""
x402Compute — Destroy a compute instance.

Usage:
  python destroy_instance.py <instance_id>
"""

import json
import sys

import requests

from wallet_signing import create_compute_auth_headers

BASE_URL = "https://compute.x402layer.cc"


def destroy_instance(instance_id: str) -> dict:
    """Destroy a compute instance."""
    print(f"Destroying instance {instance_id}...")

    path = f"/compute/instances/{instance_id}"
    auth_headers = create_compute_auth_headers("DELETE", path)
    response = requests.delete(
        f"{BASE_URL}/compute/instances/{instance_id}",
        headers=auth_headers,
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        print("✅ Instance destroyed successfully")
        return data

    return {"error": f"HTTP {response.status_code}", "response": response.text[:500]}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python destroy_instance.py <instance_id>")
        sys.exit(1)

    result = destroy_instance(sys.argv[1])
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
