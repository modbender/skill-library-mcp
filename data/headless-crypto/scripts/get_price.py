#!/usr/bin/env python3
"""
Get token price from DEX liquidity pools.
Supports Solana (Raydium) and BNB Chain (PancakeSwap).
"""

import sys
import requests
from typing import Optional


def get_token_price_solana(token_address: str, quote_token: str = "SOL") -> float:
    """
    Get token price on Solana via Jupiter API.
    
    Args:
        token_address: Token mint address
        quote_token: Quote currency (SOL, USDC, etc.)
    
    Returns:
        Price in quote token
    """
    # Jupiter Price API
    url = f"https://price.jup.ag/v4/price?ids={token_address}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if token_address in data.get("data", {}):
            price_data = data["data"][token_address]
            return float(price_data.get("price", 0))
        else:
            raise ValueError(f"Token {token_address} not found")
    
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch price: {e}")


def get_token_price_bnb(token_address: str, quote_token: str = "BNB") -> float:
    """
    Get token price on BNB Chain via PancakeSwap API.
    
    Args:
        token_address: Token contract address
        quote_token: Quote currency (BNB, BUSD, etc.)
    
    Returns:
        Price in quote token
    """
    # PancakeSwap API v2
    url = f"https://api.pancakeswap.info/api/v2/tokens/{token_address}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and "price" in data["data"]:
            return float(data["data"]["price"])
        else:
            raise ValueError(f"Token {token_address} not found")
    
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch price: {e}")


def get_token_price(
    chain: str,
    token_address: str,
    quote_token: str = "native"
) -> Optional[float]:
    """
    Get token price across chains.
    
    Args:
        chain: Blockchain (solana, bnb)
        token_address: Token address/mint
        quote_token: Quote currency (native uses SOL/BNB)
    
    Returns:
        Token price or None if failed
    """
    chain = chain.lower()
    
    if quote_token == "native":
        quote_token = "SOL" if chain == "solana" else "BNB"
    
    try:
        if chain == "solana":
            return get_token_price_solana(token_address, quote_token)
        elif chain in ["bnb", "bsc", "bnb-chain"]:
            return get_token_price_bnb(token_address, quote_token)
        else:
            raise ValueError(f"Unsupported chain: {chain}")
    
    except Exception as e:
        print(f"Error getting price: {e}", file=sys.stderr)
        return None


def main():
    """CLI interface for get_price."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Get token price from DEX")
    parser.add_argument("--chain", required=True, help="Chain (solana, bnb)")
    parser.add_argument("--token", required=True, help="Token address/mint")
    parser.add_argument("--quote", default="native", help="Quote token (default: native)")
    
    args = parser.parse_args()
    
    price = get_token_price(args.chain, args.token, args.quote)
    
    if price is not None:
        print(f"Price: {price} {args.quote}")
        sys.exit(0)
    else:
        print("Failed to get price", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
