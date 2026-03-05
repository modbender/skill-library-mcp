#!/usr/bin/env python3
"""
Shared Base payment signing utilities for x402 scripts.
Uses local EVM private key signing for USDC TransferWithAuthorization.
"""

import base64
import hashlib
import json
import os
import secrets
import time
import uuid
from typing import Any, Dict, Optional

from eth_account import Account
from eth_account.messages import encode_defunct

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


def _load_solders_keypair() -> Any:
    try:
        from solders.keypair import Keypair  # type: ignore
    except ImportError as exc:
        raise ValueError("Solana signing requires solders. Install solders>=0.20.0") from exc

    load_dotenv_if_available()
    secret_key = (os.getenv("SOLANA_SECRET_KEY") or "").strip()
    if not secret_key:
        raise ValueError("Set SOLANA_SECRET_KEY for Solana signing")

    # Support either JSON array format or base58 keypair string.
    if secret_key.startswith("["):
        try:
            secret_bytes = bytes(json.loads(secret_key))
            return Keypair.from_bytes(secret_bytes)
        except Exception as exc:
            raise ValueError("Invalid SOLANA_SECRET_KEY JSON array format") from exc

    try:
        return Keypair.from_base58_string(secret_key)
    except Exception as exc:
        raise ValueError("Invalid SOLANA_SECRET_KEY base58 format") from exc


def load_solana_wallet_address(required: bool = True) -> Optional[str]:
    load_dotenv_if_available()
    explicit = (os.getenv("SOLANA_WALLET_ADDRESS") or os.getenv("WALLET_ADDRESS_SECONDARY") or "").strip()
    if explicit:
        return explicit

    try:
        keypair = _load_solders_keypair()
        return str(keypair.pubkey())
    except Exception:
        if required:
            raise ValueError("Set SOLANA_WALLET_ADDRESS or SOLANA_SECRET_KEY")
        return None


def load_wallet_address(required: bool = True) -> Optional[str]:
    load_dotenv_if_available()
    wallet = os.getenv("WALLET_ADDRESS")

    if required and not wallet:
        raise ValueError("Set WALLET_ADDRESS environment variable")
    return wallet


def load_compute_chain() -> str:
    """
    Resolve compute auth chain from env/wallet context.
    Priority:
    1) COMPUTE_AUTH_CHAIN (base|solana)
    2) WALLET_ADDRESS shape (0x... => base)
    3) SOLANA credentials present => solana
    4) default base
    """
    load_dotenv_if_available()
    explicit = (os.getenv("COMPUTE_AUTH_CHAIN") or "").strip().lower()
    if explicit in ("base", "solana"):
        return explicit

    wallet = (os.getenv("WALLET_ADDRESS") or "").strip()
    if wallet:
        return "base" if wallet.lower().startswith("0x") else "solana"

    if os.getenv("SOLANA_SECRET_KEY") or os.getenv("SOLANA_WALLET_ADDRESS"):
        return "solana"
    return "base"


class PaymentSigner:
    def __init__(self, wallet: str, private_key: str) -> None:
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

    wallet = load_wallet_address(required=True)
    private_key = os.getenv("PRIVATE_KEY")

    if not private_key or not wallet:
        raise ValueError("Set PRIVATE_KEY and WALLET_ADDRESS for Base payments")

    return PaymentSigner(wallet=wallet, private_key=private_key)


def _compute_auth_message(
    chain: str,
    address: str,
    method: str,
    path: str,
    body_hash: str,
    timestamp_ms: int,
    nonce: str,
) -> str:
    return "\n".join(
        [
            "X402-COMPUTE-AUTH",
            "v1",
            chain,
            address,
            method.upper(),
            path,
            body_hash,
            str(timestamp_ms),
            nonce,
        ]
    )


def create_compute_auth_headers(
    method: str,
    path: str,
    body_str: str = "",
    chain: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Dict[str, str]:
    """
    Create auth headers for x402 Compute management endpoints.
    Supports:
    - API key auth via COMPUTE_API_KEY
    - Base wallet message signature (EIP-191)
    - Solana wallet message signature
    """
    api_key = api_key or os.getenv("COMPUTE_API_KEY")
    if api_key:
        return {"X-API-Key": api_key}

    resolved_chain = (chain or load_compute_chain()).strip().lower()
    if resolved_chain not in ("base", "solana"):
        raise ValueError("Compute auth chain must be 'base' or 'solana'")

    body_hash = hashlib.sha256((body_str or "").encode()).hexdigest()
    timestamp_ms = int(time.time() * 1000)
    nonce = uuid.uuid4().hex

    if resolved_chain == "base":
        wallet = load_wallet_address(required=True)
        private_key = os.getenv("PRIVATE_KEY")
        if not private_key:
            raise ValueError("Set PRIVATE_KEY for Base auth signing")

        address = wallet.lower()
        message = _compute_auth_message(
            chain="base",
            address=address,
            method=method,
            path=path,
            body_hash=body_hash,
            timestamp_ms=timestamp_ms,
            nonce=nonce,
        )
        signed = Account.from_key(private_key).sign_message(encode_defunct(text=message))
        signature = signed.signature.hex()
        if not signature.startswith("0x"):
            signature = "0x" + signature

        return {
            "X-Auth-Address": address,
            "X-Auth-Chain": "base",
            "X-Auth-Signature": signature,
            "X-Auth-Timestamp": str(timestamp_ms),
            "X-Auth-Nonce": nonce,
            "X-Auth-Sig-Encoding": "hex",
        }

    # Solana auth signing
    address = load_solana_wallet_address(required=True)
    keypair = _load_solders_keypair()
    message = _compute_auth_message(
        chain="solana",
        address=address,
        method=method,
        path=path,
        body_hash=body_hash,
        timestamp_ms=timestamp_ms,
        nonce=nonce,
    )
    sig = keypair.sign_message(message.encode())
    signature = base64.b64encode(bytes(sig)).decode()

    return {
        "X-Auth-Address": address,
        "X-Auth-Chain": "solana",
        "X-Auth-Signature": signature,
        "X-Auth-Timestamp": str(timestamp_ms),
        "X-Auth-Nonce": nonce,
        "X-Auth-Sig-Encoding": "base64",
    }
