#!/usr/bin/env python3
"""Approve all required Polymarket contracts for trading."""
import os, sys
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
PRIVATE_KEY = os.environ["PRIVATE_KEY"]

w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
acct = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Wallet: {acct.address}")

USDC_E = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
CTF = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"
CTF_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"
NEG_RISK_EXCHANGE = "0xC5d563A36AE78145C45a50134d48A1215220f80a"
NEG_RISK_ADAPTER = "0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296"
MAX_UINT = 2**256 - 1

ERC20_ABI = [{"inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"}]
ERC1155_ABI = [{"inputs":[{"name":"operator","type":"address"},{"name":"approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"}]

usdc = w3.eth.contract(address=Web3.to_checksum_address(USDC_E), abi=ERC20_ABI)
ctf = w3.eth.contract(address=Web3.to_checksum_address(CTF), abi=ERC1155_ABI)

def send_tx(tx):
    tx["nonce"] = w3.eth.get_transaction_count(acct.address)
    tx["gas"] = 100000
    tx["gasPrice"] = w3.eth.gas_price
    tx["chainId"] = 137
    signed = acct.sign_transaction(tx)
    h = w3.eth.send_raw_transaction(signed.raw_transaction)
    r = w3.eth.wait_for_transaction_receipt(h, timeout=60)
    return r["transactionHash"].hex(), r["status"]

approvals = [
    ("USDC.e → CTF Exchange", usdc.functions.approve(Web3.to_checksum_address(CTF_EXCHANGE), MAX_UINT)),
    ("USDC.e → Neg Risk Exchange", usdc.functions.approve(Web3.to_checksum_address(NEG_RISK_EXCHANGE), MAX_UINT)),
    ("USDC.e → Neg Risk Adapter", usdc.functions.approve(Web3.to_checksum_address(NEG_RISK_ADAPTER), MAX_UINT)),
    ("CTF → CTF Exchange", ctf.functions.setApprovalForAll(Web3.to_checksum_address(CTF_EXCHANGE), True)),
    ("CTF → Neg Risk Exchange", ctf.functions.setApprovalForAll(Web3.to_checksum_address(NEG_RISK_EXCHANGE), True)),
    ("CTF → Neg Risk Adapter", ctf.functions.setApprovalForAll(Web3.to_checksum_address(NEG_RISK_ADAPTER), True)),
]

for label, fn in approvals:
    print(f"Approving: {label}...", end=" ", flush=True)
    try:
        tx = fn.build_transaction({"from": acct.address})
        h, status = send_tx(tx)
        print(f"{'OK' if status == 1 else 'FAILED'} — {h}")
    except Exception as e:
        print(f"ERROR: {e}")

print("\nAll approvals complete. Ready to trade!")
