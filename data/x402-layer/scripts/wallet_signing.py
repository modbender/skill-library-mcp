#!/usr/bin/env python3
"""
Shared Base payment signing utilities for x402 scripts.

Modes:
- private-key: local EVM private key signing (existing behavior)
- awal: use Coinbase Agentic Wallet CLI (AWAL) from wrapper helpers
"""

import base64
import json
import os
import secrets
import time
from typing import Any, Dict, Optional

from eth_account import Account

USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_NAME = "USD Coin"
USDC_VERSION = "2"
BASE_CHAIN_ID = 8453


def load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:
        pass


def load_auth_mode() -> str:
    """
    Supported values:
    - auto (default): private-key if creds exist, otherwise error
    - private-key: force local EVM key signing
    - awal: force AWAL mode for Base payments
    """
    load_dotenv_if_available()
    if (os.getenv("X402_USE_AWAL") or "").strip() == "1":
        return "awal"
    return (os.getenv("X402_AUTH_MODE") or "auto").strip().lower()


def is_awal_mode() -> bool:
    return load_auth_mode() == "awal"


def load_wallet_address(required: bool = True, allow_awal_fallback: bool = True) -> Optional[str]:
    load_dotenv_if_available()
    wallet = os.getenv("WALLET_ADDRESS")

    if not wallet and allow_awal_fallback and is_awal_mode():
        try:
            from awal_bridge import get_awal_evm_address  # type: ignore

            wallet = get_awal_evm_address(required=False)
        except Exception:
            wallet = None

    if required and not wallet:
        if is_awal_mode() and allow_awal_fallback:
            raise ValueError(
                "Set WALLET_ADDRESS or authenticate AWAL so address can be resolved"
            )
        raise ValueError("Set WALLET_ADDRESS environment variable")
    return wallet


def has_private_key_credentials() -> bool:
    load_dotenv_if_available()
    return bool(os.getenv("PRIVATE_KEY") and os.getenv("WALLET_ADDRESS"))


class PaymentSigner:
    def __init__(self, wallet: str, private_key: str) -> None:
        self.mode = "private-key"
        self.wallet = wallet
        self.private_key = private_key

    def sign_typed_data(self, typed_data: Dict[str, Any]) -> str:
        signed = Account.from_key(self.private_key).sign_typed_data(
            typed_data["domain"],
            {"TransferWithAuthorization": typed_data["types"]["TransferWithAuthorization"]},
            typed_data["message"],
        )
        sig = signed.signature.hex()
        # Ensure 0x prefix for EVM compatibility
        if not sig.startswith("0x"):
            sig = "0x" + sig
        return sig

    def create_x402_payment_payload(
        self,
        pay_to: str,
        amount: int,
        valid_after: int = 0,
        valid_before: Optional[int] = None,
        nonce: Optional[str] = None,
    ) -> Dict[str, Any]:
        if valid_before is None:
            valid_before = int(time.time()) + 3600
        if nonce is None:
            nonce = "0x" + secrets.token_hex(32)

        typed_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "TransferWithAuthorization": [
                    {"name": "from", "type": "address"},
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                    {"name": "validAfter", "type": "uint256"},
                    {"name": "validBefore", "type": "uint256"},
                    {"name": "nonce", "type": "bytes32"},
                ],
            },
            "primaryType": "TransferWithAuthorization",
            "domain": {
                "name": USDC_NAME,
                "version": USDC_VERSION,
                "chainId": BASE_CHAIN_ID,
                "verifyingContract": USDC_ADDRESS,
            },
            "message": {
                "from": self.wallet,
                "to": pay_to,
                "value": amount,
                "validAfter": valid_after,
                "validBefore": valid_before,
                "nonce": nonce,
            },
        }

        signature = self.sign_typed_data(typed_data)

        return {
            "x402Version": 1,
            "scheme": "exact",
            "network": "base",
            "payload": {
                "signature": signature,
                "authorization": {
                    "from": self.wallet,
                    "to": pay_to,
                    "value": str(amount),
                    "validAfter": str(valid_after),
                    "validBefore": str(valid_before),
                    "nonce": nonce,
                },
            },
        }

    def create_x402_payment_header(self, pay_to: str, amount: int) -> str:
        payload = self.create_x402_payment_payload(pay_to=pay_to, amount=amount)
        return base64.b64encode(json.dumps(payload).encode()).decode()


def load_payment_signer() -> PaymentSigner:
    load_dotenv_if_available()

    mode = load_auth_mode()
    if mode == "awal":
        raise ValueError("AWAL mode does not use local Base signer")

    if mode not in ("auto", "private-key"):
        raise ValueError("X402_AUTH_MODE must be one of: auto, private-key, awal")

    wallet = load_wallet_address(required=True, allow_awal_fallback=False)
    private_key = os.getenv("PRIVATE_KEY")

    if not private_key or not wallet:
        raise ValueError("Set PRIVATE_KEY and WALLET_ADDRESS for private-key mode")

    return PaymentSigner(wallet=wallet, private_key=private_key)
