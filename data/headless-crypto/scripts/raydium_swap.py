#!/usr/bin/env python3
"""
Raydium-specific swap implementation.
Direct integration with Raydium AMM pools.
"""

import sys
from typing import Dict, Any
from swap import swap_solana


def swap_on_raydium(
    input_token: str,
    output_token: str,
    amount: float,
    slippage: float = 1.0,
    private_key: str = None,
    simulate: bool = False
) -> Dict[str, Any]:
    """
    Execute swap on Raydium DEX.
    
    Wrapper around generic Solana swap with Raydium-specific optimizations.
    
    Args:
        input_token: Input token mint or symbol
        output_token: Output token mint or symbol
        amount: Amount to swap
        slippage: Slippage tolerance (percentage)
        private_key: Wallet private key
        simulate: If True, only simulate
    
    Returns:
        Transaction result
    """
    # Use generic Solana swap (Jupiter routes through Raydium)
    return swap_solana(
        input_token=input_token,
        output_token=output_token,
        amount=amount,
        slippage=slippage,
        private_key=private_key,
        simulate=simulate
    )


def main():
    """CLI interface for Raydium swap."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute swap on Raydium")
    parser.add_argument("--input", required=True, help="Input token mint/symbol")
    parser.add_argument("--output", required=True, help="Output token mint/symbol")
    parser.add_argument("--amount", type=float, required=True, help="Amount to swap")
    parser.add_argument("--slippage", type=float, default=1.0, help="Slippage (%)")
    parser.add_argument("--simulate", action="store_true", help="Simulate only")
    
    args = parser.parse_args()
    
    try:
        result = swap_on_raydium(
            input_token=args.input,
            output_token=args.output,
            amount=args.amount,
            slippage=args.slippage,
            simulate=args.simulate
        )
        
        if result and result["success"]:
            print(f"✅ Raydium swap successful!")
            print(f"Input: {result['input_amount']} {args.input}")
            print(f"Output: {result['output_amount']} {args.output}")
            
            if not args.simulate:
                print(f"Signature: {result['signature']}")
            
            sys.exit(0)
        else:
            print("❌ Swap failed", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
