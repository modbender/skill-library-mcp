# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Balance Check

Check your DIEM and USD balances.
Requires an Admin API key.
API docs: https://docs.venice.ai
"""

import json
import os
import sys

import httpx

VENICE_BASE_URL = "https://api.venice.ai/api/v1"


def get_api_key() -> str:
    """Get Venice API key from environment."""
    api_key = os.environ.get("VENICE_API_KEY")
    if not api_key:
        print("Error: VENICE_API_KEY environment variable is not set", file=sys.stderr)
        print("Get your ADMIN API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def check_balance() -> dict:
    """Check current balance."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print("Checking balance...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/billing/balance",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Pretty print the balance info
            print("\n" + "=" * 50, file=sys.stderr)
            print("VENICE AI BALANCE", file=sys.stderr)
            print("=" * 50, file=sys.stderr)
            
            can_consume = data.get("canConsume", False)
            currency = data.get("consumptionCurrency", "None")
            balances = data.get("balances", {})
            diem_allocation = data.get("diemEpochAllocation", 0)
            
            print(f"\n✓ Can Consume: {'Yes' if can_consume else 'No'}", file=sys.stderr)
            print(f"✓ Active Currency: {currency or 'None'}", file=sys.stderr)
            
            print("\nBalances:", file=sys.stderr)
            diem_balance = balances.get("diem")
            usd_balance = balances.get("usd")
            
            if diem_balance is not None:
                print(f"  • DIEM: {diem_balance:.4f}", file=sys.stderr)
            else:
                print("  • DIEM: -", file=sys.stderr)
                
            if usd_balance is not None:
                print(f"  • USD: ${usd_balance:.2f}", file=sys.stderr)
            else:
                print("  • USD: -", file=sys.stderr)
            
            if diem_allocation:
                print(f"\nDIEM Epoch Allocation: {diem_allocation:.4f}", file=sys.stderr)
            
            print("=" * 50 + "\n", file=sys.stderr)
            
            # Also output as JSON for programmatic use
            print(json.dumps(data, indent=2))
            
            return data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed. Make sure you're using an ADMIN API key.", file=sys.stderr)
        else:
            print(f"HTTP Error: {e.response.status_code}", file=sys.stderr)
        try:
            error_data = e.response.json()
            print(f"Details: {error_data}", file=sys.stderr)
        except Exception:
            print(f"Response: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"Request Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    check_balance()


if __name__ == "__main__":
    main()

