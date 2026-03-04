"""
Lighter Protocol - Account balance (requires API key)
"""
import os
import requests

API_BASE = "https://mainnet.zklighter.elliot.ai/api/v1"

API_KEY = os.environ.get("LIGHTER_API_KEY", "")
ACCOUNT_INDEX = os.environ.get("LIGHTER_ACCOUNT_INDEX", "0")

if not API_KEY:
    print("Error: Set LIGHTER_API_KEY environment variable")
    print("  export LIGHTER_API_KEY=your-api-key")
    exit(1)

headers = {"x-api-key": API_KEY}

response = requests.get(
    f"{API_BASE}/account?by=index&value={ACCOUNT_INDEX}",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    account = data.get("accounts", [{}])[0]
    print(f"Account {account.get('account_index')}")
    print(f"Balance: ${account.get('available_balance')}")
    print(f"Collateral: ${account.get('collateral')}")
else:
    print(f"Error: {response.status_code}")
