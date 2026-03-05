#!/usr/bin/env python3
"""
Simulate a transaction before execution.

Usage:
    python simulate_tx.py --to 0x... --value 0 --data 0x...
    python simulate_tx.py --to 0x... --data 0x... --output json
"""

import argparse
import json
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading.safe_vault import prepare_transaction, format_signing_request


def main():
    parser = argparse.ArgumentParser(description="Simulate Ethereum transaction")
    parser.add_argument("--to", required=True, help="Target address")
    parser.add_argument("--value", default="0", help="Value in wei")
    parser.add_argument("--data", default="0x", help="Transaction calldata")
    parser.add_argument("--gas-limit", type=int, default=300000, help="Gas limit")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")
    
    args = parser.parse_args()
    
    request = prepare_transaction(
        to=args.to,
        value=args.value,
        data=args.data,
        gas_limit=args.gas_limit
    )
    
    if args.output == "json":
        print(json.dumps(request, indent=2))
    else:
        print(format_signing_request(request))


if __name__ == "__main__":
    main()