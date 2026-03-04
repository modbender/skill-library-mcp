"""
Lighter Protocol - Get positions
"""
import os
import sys
import requests

# Configuration
API_BASE = "https://mainnet.zklighter.elliot.ai/api/v1"

# Load environment
LIGHTER_API_KEY = os.environ.get("LIGHTER_API_KEY", "")
LIGHTER_ACCOUNT_INDEX = int(os.environ.get("LIGHTER_ACCOUNT_INDEX", "0"))

def get_positions():
    if not LIGHTER_API_KEY:
        print("Error: LIGHTER_API_KEY environment variable required")
        print("Set it with: export LIGHTER_API_KEY='your-api-key'")
        sys.exit(1)
    
    headers = {"x-api-key": LIGHTER_API_KEY}
    
    try:
        response = requests.get(
            f"{API_BASE}/account?by=index&value={LIGHTER_ACCOUNT_INDEX}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            account = data.get("accounts", [{}])[0]
            positions = account.get("positions", [])
            
            if not positions:
                print("No open positions")
                return
            
            print(f"Open positions: {len(positions)}\n")
            
            for pos in positions:
                print(f"Market ID: {pos.get('market_index')}")
                print(f"  Side: {'Ask' if pos.get('is_ask') else 'Bid'}")
                print(f"  Size: {pos.get('size')}")
                print(f"  Entry Price: {pos.get('entry_price')}")
                print(f"  Notional Value: {pos.get('notional_value')}")
                print()
            
            return positions
        else:
            print(f"Error: {response.status_code} - {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_positions()
