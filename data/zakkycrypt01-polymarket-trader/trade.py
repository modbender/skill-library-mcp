
import os
import json
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs
from py_clob_client.order_builder.constants import BUY, SELL

# --- Configuration ---
HOST = "https://clob.polymarket.com"
CHAIN_ID = 137  # Polygon Mainnet

def get_clob_client():
    private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
    if not private_key:
        raise ValueError("FATAL: POLYMARKET_PRIVATE_KEY environment variable not set.")
    try:
        temp_client = ClobClient(HOST, key=private_key, chain_id=CHAIN_ID)
        api_creds = temp_client.create_or_derive_api_creds()
        client = ClobClient(
            HOST,
            key=private_key,
            chain_id=CHAIN_ID,
            creds=api_creds,
            signature_type=0,
        )
        return client
    except Exception as e:
        print(f"Error initializing client: {e}")
        return None

def place_order(market_slug: str, direction: str, price: float, size: float):
    print(f"Attempting to place order: {direction} on '{market_slug}' at {price} for size {size}...")

    try:
        print(f"Fetching market data for slug via public API: {market_slug}")
        api_url = "https://gamma-api.polymarket.com/markets"
        params = {"slug": market_slug}
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        markets = response.json()
        if not markets:
            return {"error": f"Could not find market with slug: {market_slug} via public API."}
        market_data = markets[0]
    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching market data from public API: {e}"}

    try:
        client = get_clob_client()
        if not client:
            return {"error": "Failed to initialize client."}

        clob_token_ids_str = market_data.get("clobTokenIds")
        if not clob_token_ids_str:
            return {"error": "clobTokenIds not found in market data."}
        
        token_ids = json.loads(clob_token_ids_str)
        if not token_ids or len(token_ids) < 2:
            return {"error": "Parsed token_ids list is invalid."}

        if direction.lower() == 'yes':
            token_id = token_ids[0]
            order_side = BUY
        elif direction.lower() == 'no':
            token_id = token_ids[1]
            order_side = SELL
        else:
            return {"error": "Invalid direction. Must be 'Yes' or 'No'."}

        print(f"Found Token ID: {token_id} for direction '{direction}'")

        order_args = OrderArgs(
            token_id=token_id,
            price=price,
            size=size,
            side=order_side
        )

        print("Placing order...")
        response = client.create_and_post_order(order_args)
        print("Order placement response received.")
        return response
    except Exception as e:
        return {"error": f"An error occurred while placing the order: {e}"}

if __name__ == "__main__":
    # This script is now run with environment variables, not command-line arguments.
    # This is a security best practice to prevent shell injection.
    
    # Example usage:
    # POLYMARKET_PRIVATE_KEY='key' \
    # MARKET_SLUG='slug' \
    # DIRECTION='Yes' \
    # PRICE=0.50 \
    # SIZE=10 \
    # python trade.py
    
    slug = os.getenv("MARKET_SLUG")
    direction = os.getenv("DIRECTION")
    price_str = os.getenv("PRICE")
    size_str = os.getenv("SIZE")

    if not all([slug, direction, price_str, size_str]):
        print("Error: One or more required environment variables are not set.")
        print("Required: MARKET_SLUG, DIRECTION, PRICE, SIZE")
        exit(1)

    try:
        price = float(price_str)
        size = float(size_str)
    except ValueError:
        print("Error: PRICE and SIZE must be valid numbers.")
        exit(1)

    result = place_order(slug, direction, price, size)

    print("\n--- SCRIPT RESULT ---")
    print(result)
    print("---------------------\n")
