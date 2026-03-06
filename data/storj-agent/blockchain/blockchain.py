import requests
import base58
import base64
from typing import List, Dict
import json
import os

from bitcoinlib.keys import Key

from solders.keypair import Keypair
from solders.pubkey import Pubkey

from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams
from solders.signature import Signature

# =========================
# Constants
# =========================

BITCOIN = 1
SOLANA = 0

BTC_API = "https://blockstream.info/api"
SOL_RPC = "https://api.mainnet-beta.solana.com"

def generate_wallets(filename: str = "storjwallet.json") -> Dict:
    """
    Generates:
    - 1 Bitcoin SegWit wallet
    - 1 Solana wallet

    Saves them into a JSON file.
    FOR TESTING ONLY.
    """

    # -------- BITCOIN --------
    btc_key = Key(network="bitcoin")
    btc_private_wif = btc_key.wif()
    btc_address = btc_key.address()

    # -------- SOLANA --------
    sol_keypair = Keypair()
    sol_secret_bytes = sol_keypair.to_bytes()

    # Encode to base58
    sol_private_key = base58.b58encode(sol_secret_bytes).decode()

    # Public key (address)
    sol_address = str(sol_keypair.pubkey())

    wallets = {
        "bitcoin": {
            "address": btc_address,
            "private_key": btc_private_wif
        },
        "solana": {
            "address": sol_address,
            "private_key": sol_private_key
        }
    }

    with open(filename, "w") as f:
        json.dump(wallets, f, indent=4)

    return wallets


# =========================
# Balance
# =========================

def get_balance(address: str, chain: int) -> float:
    """
    Returns balance in:
    - BTC if chain=1
    - SOL if chain=0
    """

    if chain == BITCOIN:
        url = f"{BTC_API}/address/{address}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()

        # Balance in satoshis
        balance = (
            data["chain_stats"]["funded_txo_sum"]
            - data["chain_stats"]["spent_txo_sum"]
        )

        return balance / 1e8  # Convert satoshis → BTC

    elif chain == SOLANA:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getBalance",
            "params": [address],
        }

        r = requests.post(SOL_RPC, json=payload)
        r.raise_for_status()

        result = r.json()["result"]["value"]

        return result / 1e9  # Lamports → SOL

    else:
        raise ValueError("Invalid chain value. Use 1 for BTC or 0 for SOL.")


# =========================
# Send Transaction
# =========================

def send_transaction(
    private_key: str,
    to_address: str,
    amount: float,
    chain: int,
) -> str:
    """
    Sends a transaction.
    Returns transaction ID.
    NOTE: This example assumes mainnet and simple transfer.
    """

    if chain == BITCOIN:
        from bitcoinlib.wallets import Wallet

        # Create temporary wallet from private key
        wallet = Wallet.create(
            name="temp_wallet",
            keys=private_key,
            network="bitcoin",
            witness_type="segwit",
        )

        tx = wallet.send_to(to_address, amount, network="bitcoin")
        wallet.delete()

        return tx.txid

    elif chain == SOLANA:
        client = Client(SOL_RPC)

        # Private key expected as base58 encoded 64-byte key
        keypair = Keypair.from_secret_key(
            base58.b58decode(private_key)
        )

        txn = VersionedTransaction().add(
            transfer(
                TransferParams(
                    from_pubkey=keypair.public_key,
                    to_pubkey=Pubkey(to_address),
                    lamports=int(amount * 1e9),
                )
            )
        )

        response = client.send_transaction(txn, keypair)

        return response["result"]

    else:
        raise ValueError("Invalid chain value. Use 1 for BTC or 0 for SOL.")


# =========================
# Transaction History
# =========================

def get_transaction_history(address: str, chain: int) -> List[Dict]:
    """
    Returns a simplified transaction history list.
    """

    if chain == BITCOIN:
        url = f"{BTC_API}/address/{address}/txs"
        r = requests.get(url)
        r.raise_for_status()
        txs = r.json()

        history = []

        for tx in txs:
            history.append(
                {
                    "txid": tx["txid"],
                    "confirmed": tx["status"]["confirmed"],
                    "block_height": tx["status"].get("block_height"),
                }
            )

        return history

    elif chain == SOLANA:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignaturesForAddress",
            "params": [address],
        }

        r = requests.post(SOL_RPC, json=payload)
        r.raise_for_status()
        txs = r.json()["result"]

        history = []

        for tx in txs:
            history.append(
                {
                    "signature": tx["signature"],
                    "slot": tx["slot"],
                    "confirmed": tx["confirmationStatus"] == "finalized",
                }
            )

        return history

    else:
        raise ValueError("Invalid chain value. Use 1 for BTC or 0 for SOL.")
    
def verify_sol_payment(signature_str, expected_receiver, expected_amount_sol):
    try:
        client = Client("https://api.mainnet-beta.solana.com")

        # 2. Fetch Transaction Details
        signature = Signature.from_string(signature_str)
        transaction = client.get_transaction(signature, commitment="finalized", encoding="jsonParsed")
        
        if not transaction.value:
            return False, "Transaction not found or not finalized."

        # 3. Parse Transaction (simplified Example)
        meta = transaction.value.transaction.meta
        pre_balances = meta.pre_balances
        post_balances = meta.post_balances
        account_keys = transaction.value.transaction.transaction.message.account_keys
        
        # 4. Find Receiver and Calculate Change
        receiver_pubkey = str(account_keys[1]) # Example index, usually 1 is receiver
        
        if receiver_pubkey != expected_receiver:
            return False, "Receiver address does not match."
        
        # Calculate lamport difference
        amount_received = post_balances[1] - pre_balances[1]
        print(f"amtrec :  {amount_received}",flush=True)
        expected_lamports = expected_amount_sol * 10**9
        
        if amount_received >= expected_lamports:
            return True, "Payment verified."
        else:
            return False, "Insufficient amount received."

    except Exception as e:
        return False, str(e)