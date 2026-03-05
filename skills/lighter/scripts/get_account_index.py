"""
Lighter Protocol - Get Account Index from ETH Address
"""
import os
import sys
import requests

API_BASE = "https://mainnet.zklighter.elliot.ai/api/v1"

# Get address from env - NOT from CLI to avoid accidental key exposure
ETH_ADDRESS = os.environ.get("LIGHTER_L1_ADDRESS", "")

if not ETH_ADDRESS:
    print("Error: Set LIGHTER_L1_ADDRESS environment variable")
    print("  export LIGHTER_L1_ADDRESS=your_eth_address")
    sys.exit(1)

# Query account
response = requests.get(
    f"{API_BASE}/accountsByL1Address",
    params={"l1_address": ETH_ADDRESS}
)

if response.status_code == 200:
    data = response.json()
    accounts = data.get("sub_accounts", [])
    if accounts:
        print(f"Account Index: {accounts[0]['index']}")
    else:
        print("No Lighter account found")
else:
    print(f"Error: {response.status_code}")
