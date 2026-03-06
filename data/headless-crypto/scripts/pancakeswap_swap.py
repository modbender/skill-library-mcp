#!/usr/bin/env python3
"""
PancakeSwap-specific swap implementation.
Direct integration with PancakeSwap V2 router.
"""

import sys
from typing import Dict, Any
from swap import swap_bnb


def swap_on_pancakeswap(
    input_token: str,
    output_token: str,
    amount: float,
    slippage: float = 1.0,
    private_key: str = None,
    simulate: bool = False
) -> Dict[str, Any]:
    """
    Execute swap on PancakeSwap DEX.
    
    Wrapper around generic BNB swap with PancakeSwap-specific optimizations.
    
    Args:
        input_token: Input token address or symbol
        output_token: Output token address or symbol
        amount: Amount to swap
        slippage: Slippage tolerance (percentage)
        private_key: Wallet private key
        simulate: If True, only simulate
    
    Returns:
        Transaction result
    """
    # Use generic BNB swap (targets PancakeSwap router)
    return swap_bnb(
        input_token=input_token,
        output_token=output_token,
        amount=amount,
        slippage=slippage,
        private_key=private_key,
        simulate=simulate
    )


def main():
    """CLI interface for PancakeSwap swap."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute swap on PancakeSwap")
    parser.add_argument("--input", required=True, help="Input token address/symbol")
    parser.add_argument("--output", required=True, help="Output token address/symbol")
    parser.add_argument("--amount", type=float, required=True, help="Amount to swap")
    parser.add_argument("--slippage", type=float, default=1.0, help="Slippage (%)")
    parser.add_argument("--simulate", action="store_true", help="Simulate only")
    
    args = parser.parse_args()
    
    try:
        result = swap_on_pancakeswap(
            input_token=args.input,
            output_token=args.output,
            amount=args.amount,
            slippage=args.slippage,
            simulate=args.simulate
        )
        
        if result and result["success"]:
            print(f"✅ PancakeSwap swap successful!")
            print(f"Input: {result['input_amount']} {args.input}")
            print(f"Output: {result['output_amount']} {args.output}")
            
            if not args.simulate:
                print(f"Transaction: {result['hash']}")
            
            sys.exit(0)
        else:
            print("❌ Swap failed", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
