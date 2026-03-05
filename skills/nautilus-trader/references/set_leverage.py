#!/usr/bin/env python3
"""
One-time leverage setup for Hyperliquid.
Run this ONCE before live trading to configure leverage.
"""

import os
from dotenv import load_dotenv
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

load_dotenv()

# Config
SYMBOL = "SOL"
LEVERAGE = 10
IS_CROSS = True  # True for cross margin, False for isolated

def main():
    pk = os.getenv("HYPERLIQUID_PK")
    if not pk:
        print("Set HYPERLIQUID_PK in environment or .env")
        return

    if not pk.startswith("0x"):
        pk = "0x" + pk

    account = Account.from_key(pk)
    exchange = Exchange(account, constants.MAINNET_API_URL)

    result = exchange.update_leverage(LEVERAGE, SYMBOL, is_cross=IS_CROSS)
    print(f"Set {SYMBOL} leverage to {LEVERAGE}x ({'cross' if IS_CROSS else 'isolated'})")
    print(f"Result: {result}")

if __name__ == "__main__":
    main()
