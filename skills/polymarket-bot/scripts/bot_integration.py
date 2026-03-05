# bot_integration.py
from dotenv import load_dotenv
import os
from fetch_markets import fetch_active_markets
from auth_setup import authenticate_with_clob
from strategy_logic import PolymarketArbitrageBot
import asyncio

# Load environment variables for security
load_dotenv()
private_key = os.getenv('POLY_PRIVATE_KEY')

if __name__ == "__main__":
    if not private_key:
        print("Error: Set POLY_PRIVATE_KEY in .env file.")
        exit(1)
    
    # Step 1: Authenticate and get API creds
    try:
        api_creds = authenticate_with_clob(private_key)
    except Exception as e:
        print(f"Authentication failed: {e}")
        exit(1)
    
    # Step 2: Fetch markets
    markets = fetch_active_markets(limit=5)  # Fetch 5 markets as example
    if not markets:
        print("No markets fetched.")
        exit(1)
    
    # Step 3: Initialize and run the bot for each market
    bot = PolymarketArbitrageBot(api_creds, dry_run=False)  # Set dry_run=True for testing
    for market in markets:
        market_id = market['id']
        asyncio.run(bot.poll_market(market_id))
    
    # In a real setup, use multiprocessing for multiple markets
    print("Bot integrated and running.")
