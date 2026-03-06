"""
Lighter Protocol - Place orders
"""
import os
import sys
import asyncio
import lighter
from lighter import Configuration

# Configuration
API_URL = "https://mainnet.zklighter.elliot.ai"

# Load environment
LIGHTER_API_KEY = os.environ.get("LIGHTER_API_KEY", "")
LIGHTER_ACCOUNT_INDEX = int(os.environ.get("LIGHTER_ACCOUNT_INDEX", "0"))

# Decimal places for atomic units
DECIMALS = 8

async def place_order(market_id: int, side: str, amount: float, price: float = None, order_type: str = "LIMIT"):
    if not LIGHTER_API_KEY:
        print("Error: LIGHTER_API_KEY environment variable required")
        print("Set it with: export LIGHTER_API_KEY='your-api-key-from-system-setup'")
        sys.exit(1)
    
    # Initialize signer
    signer = lighter.SignerClient(
        url=API_URL,
        account_index=LIGHTER_ACCOUNT_INDEX,
        api_private_keys={3: LIGHTER_API_KEY}
    )
    
    print(f"Signer initialized for account index {LIGHTER_ACCOUNT_INDEX}")
    
    # Convert to atomic units
    amount_atomic = int(amount * 10**DECIMALS)
    price_atomic = int(price * 10**DECIMALS) if price else 0
    
    # Map order types and sides
    order_type_map = {"LIMIT": 0, "MARKET": 1, "IOC": 2, "FOK": 3}
    time_in_force_map = {"GTC": 0, "IOC": 1, "FOK": 2, "GTX": 3}
    
    is_ask = side.lower() == "sell"
    order_type_int = order_type_map.get(order_type.upper(), 0)
    time_in_force_int = time_in_force_map.get("GTC", 0)
    
    # Place order
    try:
        result = await signer.create_order(
            market_index=market_id,
            client_order_index=1,
            base_amount=amount_atomic,  # Atomic units!
            price=price_atomic,         # Atomic units!
            is_ask=is_ask,
            order_type=order_type_int,  # Integer!
            time_in_force=time_in_force_int  # Integer!
        )
        
        if result[2]:  # Error message
            print(f"Order error: {result[2]}")
        else:
            print(f"✅ Order placed! TX: {result[1].tx_hash if result[1] else 'pending'}")
        
        return result
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Place order on Lighter")
    parser.add_argument("--market-id", type=int, required=True, help="Market ID (e.g., 1 for ETH-USD)")
    parser.add_argument("--side", required=True, choices=["buy", "sell"], help="Order side")
    parser.add_argument("--amount", type=float, required=True, help="Order amount")
    parser.add_argument("--price", type=float, help="Order price (for limit orders)")
    parser.add_argument("--type", dest="order_type", default="LIMIT", help="Order type")
    
    args = parser.parse_args()
    asyncio.run(place_order(args.market_id, args.side, args.amount, args.price, args.order_type))

if __name__ == "__main__":
    main()
