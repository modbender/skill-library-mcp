#!/usr/bin/env python3
"""
Execute token swaps on DEXs.
Supports Solana (Raydium/Jupiter) and BNB Chain (PancakeSwap).
"""

import sys
import os
from typing import Optional, Dict, Any


class InsufficientFundsError(Exception):
    """Raised when wallet has insufficient balance."""
    pass


class SlippageExceededError(Exception):
    """Raised when price slippage exceeds tolerance."""
    pass


class RPCError(Exception):
    """Raised when RPC request fails."""
    pass


def swap_solana(
    input_token: str,
    output_token: str,
    amount: float,
    slippage: float,
    private_key: str,
    simulate: bool = False
) -> Dict[str, Any]:
    """
    Execute swap on Solana via Jupiter aggregator.
    
    Args:
        input_token: Input token mint or symbol (SOL, USDC, etc.)
        output_token: Output token mint or symbol
        amount: Amount to swap (in input token)
        slippage: Slippage tolerance (percentage)
        private_key: Wallet private key (base58)
        simulate: If True, only simulate (don't execute)
    
    Returns:
        Transaction result with signature
    """
    import requests
    from solana.rpc.api import Client
    from solana.transaction import Transaction
    import base58
    
    # Jupiter API
    JUPITER_API = "https://quote-api.jup.ag/v6"
    RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
    
    client = Client(RPC_URL)
    
    try:
        # 1. Get quote
        quote_params = {
            "inputMint": input_token,
            "outputMint": output_token,
            "amount": int(amount * 1e9),  # Convert to lamports/smallest unit
            "slippageBps": int(slippage * 100)  # Convert to basis points
        }
        
        quote_response = requests.get(f"{JUPITER_API}/quote", params=quote_params, timeout=10)
        quote_response.raise_for_status()
        quote = quote_response.json()
        
        if "error" in quote:
            raise ValueError(f"Quote error: {quote['error']}")
        
        # 2. Get swap transaction
        swap_payload = {
            "quoteResponse": quote,
            "userPublicKey": base58.b58decode(private_key).hex(),
            "wrapUnwrapSOL": True
        }
        
        swap_response = requests.post(f"{JUPITER_API}/swap", json=swap_payload, timeout=10)
        swap_response.raise_for_status()
        swap_data = swap_response.json()
        
        if "error" in swap_data:
            raise ValueError(f"Swap error: {swap_data['error']}")
        
        # 3. Simulate or execute
        if simulate:
            return {
                "success": True,
                "simulated": True,
                "input_amount": amount,
                "output_amount": float(quote.get("outAmount", 0)) / 1e9,
                "price_impact": quote.get("priceImpactPct", 0)
            }
        
        # Decode and sign transaction
        tx_data = swap_data["swapTransaction"]
        transaction = Transaction.deserialize(bytes.fromhex(tx_data))
        
        # Send transaction
        response = client.send_transaction(transaction, private_key)
        signature = response.value
        
        return {
            "success": True,
            "signature": signature,
            "input_amount": amount,
            "output_amount": float(quote.get("outAmount", 0)) / 1e9
        }
    
    except requests.RequestException as e:
        raise RPCError(f"RPC request failed: {e}")
    except Exception as e:
        raise RuntimeError(f"Swap failed: {e}")


def swap_bnb(
    input_token: str,
    output_token: str,
    amount: float,
    slippage: float,
    private_key: str,
    simulate: bool = False
) -> Dict[str, Any]:
    """
    Execute swap on BNB Chain via PancakeSwap.
    
    Args:
        input_token: Input token address or symbol (BNB, BUSD, etc.)
        output_token: Output token address or symbol
        amount: Amount to swap (in input token)
        slippage: Slippage tolerance (percentage)
        private_key: Wallet private key (hex)
        simulate: If True, only simulate (don't execute)
    
    Returns:
        Transaction result with hash
    """
    from web3 import Web3
    
    RPC_URL = os.getenv("BNB_RPC_URL", "https://bsc-dataseed1.binance.org")
    ROUTER_ADDRESS = "0x10ED43C718714eb63d5aA57B78B54704E256024E"  # PancakeSwap V2
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    # PancakeSwap Router ABI (simplified)
    ROUTER_ABI = [
        {
            "inputs": [
                {"name": "amountIn", "type": "uint256"},
                {"name": "amountOutMin", "type": "uint256"},
                {"name": "path", "type": "address[]"},
                {"name": "to", "type": "address"},
                {"name": "deadline", "type": "uint256"}
            ],
            "name": "swapExactTokensForTokens",
            "outputs": [{"name": "amounts", "type": "uint256[]"}],
            "type": "function"
        },
        {
            "inputs": [
                {"name": "amountIn", "type": "uint256"},
                {"name": "path", "type": "address[]"}
            ],
            "name": "getAmountsOut",
            "outputs": [{"name": "amounts", "type": "uint256[]"}],
            "type": "function"
        }
    ]
    
    try:
        router = w3.eth.contract(address=ROUTER_ADDRESS, abi=ROUTER_ABI)
        account = w3.eth.account.from_key(private_key)
        
        # Build swap path
        path = [input_token, output_token]
        amount_in = w3.to_wei(amount, 'ether')
        
        # Get expected output
        amounts_out = router.functions.getAmountsOut(amount_in, path).call()
        expected_output = amounts_out[-1]
        
        # Calculate minimum output with slippage
        min_output = int(expected_output * (1 - slippage / 100))
        
        if simulate:
            return {
                "success": True,
                "simulated": True,
                "input_amount": amount,
                "output_amount": w3.from_wei(expected_output, 'ether'),
                "min_output": w3.from_wei(min_output, 'ether')
            }
        
        # Build transaction
        import time
        deadline = int(time.time()) + 300  # 5 minutes
        
        tx = router.functions.swapExactTokensForTokens(
            amount_in,
            min_output,
            path,
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {
            "success": True,
            "hash": tx_hash.hex(),
            "input_amount": amount,
            "output_amount": w3.from_wei(expected_output, 'ether')
        }
    
    except Exception as e:
        raise RuntimeError(f"Swap failed: {e}")


def execute_swap(
    chain: str,
    input_token: str,
    output_token: str,
    amount: float,
    slippage: float = 1.0,
    private_key: Optional[str] = None,
    simulate: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Execute swap across chains.
    
    Args:
        chain: Blockchain (solana, bnb)
        input_token: Input token address/symbol
        output_token: Output token address/symbol
        amount: Amount to swap
        slippage: Slippage tolerance (percentage, default 1%)
        private_key: Wallet private key (from env if not provided)
        simulate: If True, only simulate
    
    Returns:
        Transaction result or None if failed
    """
    chain = chain.lower()
    
    # Get private key from env if not provided
    if private_key is None:
        env_var = "SOLANA_PRIVATE_KEY" if chain == "solana" else "BNB_PRIVATE_KEY"
        private_key = os.getenv(env_var)
        
        if not private_key:
            raise ValueError(f"Private key not provided and {env_var} not set")
    
    try:
        if chain == "solana":
            return swap_solana(input_token, output_token, amount, slippage, private_key, simulate)
        elif chain in ["bnb", "bsc", "bnb-chain"]:
            return swap_bnb(input_token, output_token, amount, slippage, private_key, simulate)
        else:
            raise ValueError(f"Unsupported chain: {chain}")
    
    except Exception as e:
        print(f"Error executing swap: {e}", file=sys.stderr)
        return None


def main():
    """CLI interface for swap."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute token swap on DEX")
    parser.add_argument("--chain", required=True, help="Chain (solana, bnb)")
    parser.add_argument("--input", required=True, help="Input token address/symbol")
    parser.add_argument("--output", required=True, help="Output token address/symbol")
    parser.add_argument("--amount", type=float, required=True, help="Amount to swap")
    parser.add_argument("--slippage", type=float, default=1.0, help="Slippage tolerance (%%)")
    parser.add_argument("--simulate", action="store_true", help="Simulate only (dry run)")
    
    args = parser.parse_args()
    
    result = execute_swap(
        args.chain,
        args.input,
        args.output,
        args.amount,
        args.slippage,
        simulate=args.simulate
    )
    
    if result and result["success"]:
        print(f"✅ Swap successful!")
        print(f"Input: {result['input_amount']} {args.input}")
        print(f"Output: {result['output_amount']} {args.output}")
        
        if not args.simulate:
            sig_key = "signature" if args.chain == "solana" else "hash"
            print(f"Transaction: {result.get(sig_key)}")
        
        sys.exit(0)
    else:
        print("❌ Swap failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
