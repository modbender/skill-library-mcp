# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx"]
# ///
"""
Venice AI Rate Limits and Balances

Get current rate limits and balance information.
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
        print("Get your API key at https://venice.ai → Settings → API Keys", file=sys.stderr)
        sys.exit(1)
    return api_key


def get_rate_limits() -> dict:
    """Get rate limits and balances."""
    api_key = get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    print("Fetching rate limits...", file=sys.stderr)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{VENICE_BASE_URL}/api_keys/rate_limits",
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            print("\n" + "=" * 60, file=sys.stderr)
            print("RATE LIMITS & BALANCES", file=sys.stderr)
            print("=" * 60, file=sys.stderr)
            
            # Rate limits
            rate_limits = data.get("rateLimits", {})
            if rate_limits:
                print("\nRate Limits:", file=sys.stderr)
                
                rpm = rate_limits.get("requestsPerMinute")
                if rpm:
                    print(f"  • Requests/minute: {rpm.get('limit', '-')} (used: {rpm.get('used', 0)}, remaining: {rpm.get('remaining', '-')})", file=sys.stderr)
                
                tpm = rate_limits.get("tokensPerMinute")
                if tpm:
                    print(f"  • Tokens/minute: {tpm.get('limit', '-')} (used: {tpm.get('used', 0)}, remaining: {tpm.get('remaining', '-')})", file=sys.stderr)
                
                tpd = rate_limits.get("tokensPerDay")
                if tpd:
                    print(f"  • Tokens/day: {tpd.get('limit', '-')} (used: {tpd.get('used', 0)}, remaining: {tpd.get('remaining', '-')})", file=sys.stderr)
            
            # Balances
            balances = data.get("balances", {})
            if balances:
                print("\nBalances:", file=sys.stderr)
                diem = balances.get("diem")
                usd = balances.get("usd")
                if diem is not None:
                    print(f"  • DIEM: {diem:.4f}", file=sys.stderr)
                if usd is not None:
                    print(f"  • USD: ${usd:.2f}", file=sys.stderr)
            
            # Consumption info
            can_consume = data.get("canConsume")
            currency = data.get("consumptionCurrency")
            if can_consume is not None:
                print(f"\nCan Consume: {'Yes' if can_consume else 'No'}", file=sys.stderr)
            if currency:
                print(f"Consumption Currency: {currency}", file=sys.stderr)
            
            print("\n" + "=" * 60 + "\n", file=sys.stderr)
            
            print(json.dumps(data, indent=2, default=str))
            
            return data

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Error: Authentication failed.", file=sys.stderr)
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
    get_rate_limits()


if __name__ == "__main__":
    main()
