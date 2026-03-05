#!/usr/bin/env python3
"""
Shared Solana signing helpers for x402 scripts.

Builds x402-compatible X-Payment headers for Solana accepts options.
Private-key mode only (SOLANA_SECRET_KEY).
"""

import base64
import json
import os
import struct
from typing import Any, Dict, Optional

import requests

RPC_URL = "https://api.mainnet-beta.solana.com"


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:
        pass


def _load_auth_mode() -> str:
    _load_dotenv_if_available()
    if (os.getenv("X402_USE_AWAL") or "").strip() == "1":
        return "awal"
    return (os.getenv("X402_AUTH_MODE") or "auto").strip().lower()


def _import_solders() -> Dict[str, Any]:
    try:
        from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price  # type: ignore
        from solders.hash import Hash  # type: ignore
        from solders.instruction import AccountMeta, Instruction  # type: ignore
        from solders.keypair import Keypair  # type: ignore
        from solders.message import MessageV0  # type: ignore
        from solders.null_signer import NullSigner  # type: ignore
        from solders.pubkey import Pubkey  # type: ignore
        from solders.transaction import VersionedTransaction  # type: ignore
    except ImportError as exc:
        raise ValueError("Solana signing requires solders. Install solders>=0.20.0") from exc

    return {
        "Keypair": Keypair,
        "Pubkey": Pubkey,
        "VersionedTransaction": VersionedTransaction,
        "MessageV0": MessageV0,
        "Instruction": Instruction,
        "AccountMeta": AccountMeta,
        "Hash": Hash,
        "NullSigner": NullSigner,
        "set_compute_unit_limit": set_compute_unit_limit,
        "set_compute_unit_price": set_compute_unit_price,
    }


def has_solana_credentials() -> bool:
    mode = _load_auth_mode()
    if mode == "awal":
        return False
    _load_dotenv_if_available()
    return bool(os.getenv("SOLANA_SECRET_KEY"))


def _load_keypair(keypair_cls: Any) -> Any:
    _load_dotenv_if_available()
    secret_key_json = os.getenv("SOLANA_SECRET_KEY")
    if not secret_key_json:
        raise ValueError("Set SOLANA_SECRET_KEY for Solana private-key signing")
    secret_bytes = bytes(json.loads(secret_key_json))
    return keypair_cls.from_bytes(secret_bytes)


def _derive_local_solana_wallet_address() -> Optional[str]:
    if not has_solana_credentials():
        return None
    solders = _import_solders()
    keypair = _load_keypair(solders["Keypair"])
    return str(keypair.pubkey())


def load_solana_wallet_address() -> Optional[str]:
    _load_dotenv_if_available()
    explicit = os.getenv("SOLANA_WALLET_ADDRESS") or os.getenv("WALLET_ADDRESS_SECONDARY")
    local_derived = _derive_local_solana_wallet_address()
    return explicit or local_derived


def _get_recent_blockhash(hash_cls: Any) -> Any:
    response = requests.post(
        RPC_URL,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getLatestBlockhash",
            "params": [{"commitment": "finalized"}],
        },
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()
    return hash_cls.from_string(result["result"]["value"]["blockhash"])


def _build_transaction_base64(accept_option: Dict[str, Any], payer_wallet_address: str) -> str:
    solders = _import_solders()
    Keypair = solders["Keypair"]
    Pubkey = solders["Pubkey"]
    VersionedTransaction = solders["VersionedTransaction"]
    MessageV0 = solders["MessageV0"]
    Instruction = solders["Instruction"]
    AccountMeta = solders["AccountMeta"]
    Hash = solders["Hash"]
    NullSigner = solders["NullSigner"]
    set_compute_unit_limit = solders["set_compute_unit_limit"]
    set_compute_unit_price = solders["set_compute_unit_price"]

    token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
    ata_program_id = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    usdc_mint_default = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    payer_pubkey = Pubkey.from_string(payer_wallet_address)

    def get_ata(owner: Any, mint: Any) -> Any:
        seeds = [bytes(owner), bytes(token_program_id), bytes(mint)]
        ata, _ = Pubkey.find_program_address(seeds, ata_program_id)
        return ata

    def create_transfer_checked_ix(source: Any, mint: Any, dest: Any, owner: Any, amount: int, decimals: int) -> Any:
        data = bytes([12]) + struct.pack("<Q", amount) + bytes([decimals])
        keys = [
            AccountMeta(source, False, True),
            AccountMeta(mint, False, False),
            AccountMeta(dest, False, True),
            AccountMeta(owner, True, False),
        ]
        return Instruction(token_program_id, data, keys)

    blockhash = _get_recent_blockhash(Hash)

    extra = accept_option.get("extra") or {}
    fee_payer_str = extra.get("feePayer")
    fee_payer = Pubkey.from_string(fee_payer_str) if fee_payer_str else payer_pubkey
    pay_to = Pubkey.from_string(accept_option["payTo"])
    mint = Pubkey.from_string(accept_option.get("asset") or usdc_mint_default)
    amount = int(accept_option["maxAmountRequired"])

    source_ata = get_ata(payer_pubkey, mint)
    dest_ata = get_ata(pay_to, mint)

    instructions = [
        set_compute_unit_limit(200000),
        set_compute_unit_price(1000),
        create_transfer_checked_ix(source_ata, mint, dest_ata, payer_pubkey, amount, 6),
    ]

    message = MessageV0.try_compile(
        fee_payer,
        instructions,
        [],
        blockhash,
    )

    keypair = _load_keypair(Keypair)
    if str(keypair.pubkey()) != str(payer_pubkey):
        raise ValueError(
            "SOLANA_SECRET_KEY does not match payer wallet address. "
            "Set SOLANA_WALLET_ADDRESS to match keypair or use the correct key."
        )

    signers = [keypair]
    if str(fee_payer) != str(payer_pubkey):
        signers.append(NullSigner(fee_payer))

    tx = VersionedTransaction(message, signers)
    return base64.b64encode(bytes(tx)).decode()


def create_solana_xpayment_from_accept(accept_option: Dict[str, Any]) -> str:
    network = str(accept_option.get("network", "")).lower()
    if network != "solana":
        raise ValueError(f"Expected Solana accept option, got network={accept_option.get('network')}")

    if _load_auth_mode() == "awal":
        raise ValueError("AWAL mode currently supports Base payments only")

    if not has_solana_credentials():
        raise ValueError("No Solana signer available. Set SOLANA_SECRET_KEY.")

    payer = load_solana_wallet_address()
    if not payer:
        raise ValueError("Failed to resolve local Solana wallet address")

    signed_tx = _build_transaction_base64(accept_option, payer_wallet_address=payer)

    payload = {
        "x402Version": 1,
        "scheme": "exact",
        "network": "solana",
        "payload": {"transaction": signed_tx},
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()
