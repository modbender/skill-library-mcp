#!/usr/bin/env python3
"""
Minimal example calls for the Alpaca skill.

Environment variables:
  ALPACA_API_KEY
  ALPACA_API_SECRET
  ALPACA_BASE_URL (optional)
"""

from alpaca_api import make_request


def main():
    print("Account:")
    make_request("GET", "/v2/account")
    print("\nRecent orders:")
    make_request("GET", "/v2/orders", params={"status": "all", "limit": 5})


if __name__ == "__main__":
    main()
