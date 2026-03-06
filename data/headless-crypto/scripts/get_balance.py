#!/usr/bin/env python3
"""
Check wallet balances on Solana and BNB Chain.
Supports native tokens (SOL, BNB) and token balances.
"""

import sys
from typing import Optional


def get_balance_solana(wallet_address: str, token_mint: Optional[str] = None) -> float:
    """
    Get wallet balance on Solana.
    
    Args:
        wallet_address: Solana wallet public key
        token_mint: Optional SPL token mint address (None = SOL balance)
    
    Returns:
        Balance in tokens
    """
    from solana.rpc.api import Client
    
    # Use public RPC (replace with private for production)
    rpc_url = "https://api.mainnet-beta.solana.com"
    client = Client(rpc_url)
    
    try:
        if token_mint is None:
            # Get SOL balance
            response = client.get_balance(wallet_address)
            balance_lamports = response.value
            return balance_lamports / 1e9  # Convert lamports to SOL
        else:
            # Get SPL token balance
            from solana.rpc.types import TokenAccountOpts
            
            response = client.get_token_accounts_by_owner(
                wallet_address,
                TokenAccountOpts(mint=token_mint)
            )
            
            if response.value:
                # Sum all token accounts
                total = 0
                for account in response.value:
                    account_data = account.account.data
                    # Parse token amount (simplified)
                    # In production, use proper SPL token parsing
                    total += float(account_data.get("amount", 0))
                return total
            else:
                return 0.0
    
    except Exception as e:
        raise RuntimeError(f"Failed to get Solana balance: {e}")


def get_balance_bnb(wallet_address: str, token_address: Optional[str] = None) -> float:
    """
    Get wallet balance on BNB Chain.
    
    Args:
        wallet_address: BNB Chain wallet address
        token_address: Optional BEP20 token address (None = BNB balance)
    
    Returns:
        Balance in tokens
    """
    from web3 import Web3
    
    # Use public RPC (replace with private for production)
    rpc_url = "https://bsc-dataseed1.binance.org"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    try:
        if token_address is None:
            # Get BNB balance
            balance_wei = w3.eth.get_balance(wallet_address)
            return w3.from_wei(balance_wei, 'ether')
        else:
            # Get BEP20 token balance
            # Standard ERC20 ABI (balanceOf function)
            abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "_owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "balance", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                }
            ]
            
            contract = w3.eth.contract(address=token_address, abi=abi)
            balance = contract.functions.balanceOf(wallet_address).call()
            decimals = contract.functions.decimals().call()
            
            return balance / (10 ** decimals)
    
    except Exception as e:
        raise RuntimeError(f"Failed to get BNB balance: {e}")


def get_balance(
    chain: str,
    wallet_address: str,
    token_address: Optional[str] = None
) -> Optional[float]:
    """
    Get wallet balance across chains.
    
    Args:
        chain: Blockchain (solana, bnb)
        wallet_address: Wallet public address
        token_address: Optional token address (None = native token)
    
    Returns:
        Balance or None if failed
    """
    chain = chain.lower()
    
    try:
        if chain == "solana":
            return get_balance_solana(wallet_address, token_address)
        elif chain in ["bnb", "bsc", "bnb-chain"]:
            return get_balance_bnb(wallet_address, token_address)
        else:
            raise ValueError(f"Unsupported chain: {chain}")
    
    except Exception as e:
        print(f"Error getting balance: {e}", file=sys.stderr)
        return None


def main():
    """CLI interface for get_balance."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check wallet balance")
    parser.add_argument("--chain", required=True, help="Chain (solana, bnb)")
    parser.add_argument("--wallet", required=True, help="Wallet address")
    parser.add_argument("--token", help="Token address (optional, default: native)")
    
    args = parser.parse_args()
    
    balance = get_balance(args.chain, args.wallet, args.token)
    
    if balance is not None:
        token_name = args.token or ("SOL" if args.chain == "solana" else "BNB")
        print(f"Balance: {balance} {token_name}")
        sys.exit(0)
    else:
        print("Failed to get balance", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
