#!/usr/bin/env python3
"""
Monitor liquidity pools on DEXs.
Get pool stats, liquidity, volume, and APY.
"""

import sys
import requests
from typing import Dict, Any, Optional


def get_pool_info_solana(token_a: str, token_b: str) -> Dict[str, Any]:
    """
    Get liquidity pool info on Solana (Raydium).
    
    Args:
        token_a: First token mint address
        token_b: Second token mint address
    
    Returns:
        Pool stats dictionary
    """
    # Use DexScreener API for pool data
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_a},{token_b}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pairs = data.get("pairs", [])
        if not pairs:
            raise ValueError("No pool found for this pair")
        
        # Get the largest pool by liquidity
        pool = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0)))
        
        return {
            "pool_address": pool.get("pairAddress"),
            "dex": pool.get("dexId"),
            "liquidity": float(pool.get("liquidity", {}).get("usd", 0)),
            "volume_24h": float(pool.get("volume", {}).get("h24", 0)),
            "price_usd": float(pool.get("priceUsd", 0)),
            "price_change_24h": float(pool.get("priceChange", {}).get("h24", 0)),
            "txns_24h": pool.get("txns", {}).get("h24", {}),
            "fdv": float(pool.get("fdv", 0))
        }
    
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch pool info: {e}")


def get_pool_info_bnb(token_a: str, token_b: str) -> Dict[str, Any]:
    """
    Get liquidity pool info on BNB Chain (PancakeSwap).
    
    Args:
        token_a: First token address
        token_b: Second token address
    
    Returns:
        Pool stats dictionary
    """
    # Use DexScreener API
    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_a},{token_b}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pairs = data.get("pairs", [])
        if not pairs:
            raise ValueError("No pool found for this pair")
        
        # Filter for BSC/BNB Chain
        bsc_pairs = [p for p in pairs if p.get("chainId") == "bsc"]
        
        if not bsc_pairs:
            raise ValueError("No BSC pool found for this pair")
        
        pool = max(bsc_pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0)))
        
        return {
            "pool_address": pool.get("pairAddress"),
            "dex": pool.get("dexId"),
            "liquidity": float(pool.get("liquidity", {}).get("usd", 0)),
            "volume_24h": float(pool.get("volume", {}).get("h24", 0)),
            "price_usd": float(pool.get("priceUsd", 0)),
            "price_change_24h": float(pool.get("priceChange", {}).get("h24", 0)),
            "txns_24h": pool.get("txns", {}).get("h24", {}),
            "fdv": float(pool.get("fdv", 0))
        }
    
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch pool info: {e}")


def get_pool_info(
    chain: str,
    token_a: str,
    token_b: str
) -> Optional[Dict[str, Any]]:
    """
    Get liquidity pool info across chains.
    
    Args:
        chain: Blockchain (solana, bnb)
        token_a: First token address
        token_b: Second token address
    
    Returns:
        Pool stats or None if failed
    """
    chain = chain.lower()
    
    try:
        if chain == "solana":
            return get_pool_info_solana(token_a, token_b)
        elif chain in ["bnb", "bsc", "bnb-chain"]:
            return get_pool_info_bnb(token_a, token_b)
        else:
            raise ValueError(f"Unsupported chain: {chain}")
    
    except Exception as e:
        print(f"Error getting pool info: {e}", file=sys.stderr)
        return None


def main():
    """CLI interface for monitor_pool."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor liquidity pool")
    parser.add_argument("--chain", required=True, help="Chain (solana, bnb)")
    parser.add_argument("--token-a", required=True, help="First token address")
    parser.add_argument("--token-b", required=True, help="Second token address")
    
    args = parser.parse_args()
    
    pool_info = get_pool_info(args.chain, args.token_a, args.token_b)
    
    if pool_info:
        print(f"\n📊 Pool Info ({args.chain.upper()})")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"DEX: {pool_info['dex']}")
        print(f"Pool Address: {pool_info['pool_address']}")
        print(f"\n💰 Liquidity: ${pool_info['liquidity']:,.2f}")
        print(f"📈 24h Volume: ${pool_info['volume_24h']:,.2f}")
        print(f"💵 Price: ${pool_info['price_usd']:.6f}")
        print(f"📊 24h Change: {pool_info['price_change_24h']:.2f}%")
        
        txns = pool_info.get('txns_24h', {})
        if txns:
            print(f"\n🔄 24h Transactions:")
            print(f"  Buys: {txns.get('buys', 0)}")
            print(f"  Sells: {txns.get('sells', 0)}")
        
        if pool_info.get('fdv'):
            print(f"\n💎 FDV: ${pool_info['fdv']:,.2f}")
        
        sys.exit(0)
    else:
        print("❌ Failed to get pool info", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
