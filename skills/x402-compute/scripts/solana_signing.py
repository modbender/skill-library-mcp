#!/usr/bin/env python3
"""
Solana x402 payment helpers for x402-compute scripts.

Builds x402-compatible X-Payment headers for Solana accepts options.
Supports SOLANA_SECRET_KEY as:
- JSON array of keypair bytes, or
- base58 keypair string.
"""

import base64
import json
import os
import struct
import time
from typing import Any, Dict, Tuple

import requests

RPC_URL = "https://api.mainnet-beta.solana.com"
USDC_MINT_SOLANA = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
ATA_PROGRAM_ID = "ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL"
SYSTEM_PROGRAM_ID = "11111111111111111111111111111111"
RENT_SYSVAR_ID = "SysvarRent111111111111111111111111111111111"


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:
        pass


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
        raise ValueError("Solana signing requires solders>=0.20.0") from exc

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


def _load_keypair(keypair_cls: Any) -> Any:
    _load_dotenv_if_available()
    raw = (os.getenv("SOLANA_SECRET_KEY") or "").strip()
    if not raw:
        raise ValueError("Set SOLANA_SECRET_KEY for Solana payment signing")

    if raw.startswith("["):
        try:
            return keypair_cls.from_bytes(bytes(json.loads(raw)))
        except Exception as exc:
            raise ValueError("Invalid SOLANA_SECRET_KEY JSON array format") from exc

    try:
        return keypair_cls.from_base58_string(raw)
    except Exception as exc:
        raise ValueError("Invalid SOLANA_SECRET_KEY base58 format") from exc


def load_solana_wallet_address() -> str:
    _load_dotenv_if_available()
    explicit = (os.getenv("SOLANA_WALLET_ADDRESS") or os.getenv("WALLET_ADDRESS_SECONDARY") or "").strip()
    if explicit:
        return explicit

    solders = _import_solders()
    keypair = _load_keypair(solders["Keypair"])
    return str(keypair.pubkey())


def _get_recent_blockhash(hash_cls: Any) -> Any:
    result = _rpc_call("getLatestBlockhash", [{"commitment": "finalized"}])
    return hash_cls.from_string(result["value"]["blockhash"])


def _account_exists(pubkey: str) -> bool:
    value = _rpc_call("getAccountInfo", [pubkey, {"encoding": "base64"}]).get("value")
    return value is not None


def _rpc_call(method: str, params: list[Any]) -> Dict[str, Any]:
    response = requests.post(
        RPC_URL,
        json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise ValueError(f"Solana RPC {method} failed: {data['error']}")
    return data.get("result", {})


def _get_ata(owner: Any, mint: Any, token_program_id: Any, ata_program_id: Any, pubkey_cls: Any) -> Any:
    seeds = [bytes(owner), bytes(token_program_id), bytes(mint)]
    ata, _ = pubkey_cls.find_program_address(seeds, ata_program_id)
    return ata


def _resolve_destination_token_account(
    accept_option: Dict[str, Any],
    pubkey_cls: Any,
    token_program_id: Any,
    ata_program_id: Any,
) -> Tuple[Any, bool]:
    pay_to_str = accept_option["payTo"]
    mint_str = accept_option.get("asset") or USDC_MINT_SOLANA
    pay_to = pubkey_cls.from_string(pay_to_str)
    mint = pubkey_cls.from_string(mint_str)

    pay_to_info = _rpc_call("getAccountInfo", [pay_to_str, {"encoding": "jsonParsed"}]).get("value")
    if pay_to_info and pay_to_info.get("owner") == TOKEN_PROGRAM_ID:
        parsed = (((pay_to_info.get("data") or {}).get("parsed") or {}).get("info") or {})
        if parsed.get("mint") == mint_str:
            return pay_to, False
        raise ValueError("Solana payTo token account mint does not match required asset")

    destination_ata = _get_ata(pay_to, mint, token_program_id, ata_program_id, pubkey_cls)
    return destination_ata, True


def _send_and_confirm_transaction(tx_bytes: bytes) -> str:
    tx_b64 = base64.b64encode(tx_bytes).decode()
    signature = _rpc_call(
        "sendTransaction",
        [tx_b64, {"encoding": "base64", "skipPreflight": False, "preflightCommitment": "confirmed"}],
    )
    if not signature:
        raise ValueError("Solana sendTransaction did not return signature")

    deadline = time.time() + 45
    while time.time() < deadline:
        status = _rpc_call("getSignatureStatuses", [[signature], {"searchTransactionHistory": True}])
        value = (status.get("value") or [None])[0] or {}
        confirmation = value.get("confirmationStatus")
        err = value.get("err")
        if err:
            raise ValueError(f"Solana setup transaction failed: {err}")
        if confirmation in ("confirmed", "finalized"):
            return signature
        time.sleep(1.0)

    return signature


def ensure_solana_destination_ready(accept_option: Dict[str, Any]) -> None:
    solders = _import_solders()
    Keypair = solders["Keypair"]
    Pubkey = solders["Pubkey"]
    VersionedTransaction = solders["VersionedTransaction"]
    MessageV0 = solders["MessageV0"]
    Instruction = solders["Instruction"]
    AccountMeta = solders["AccountMeta"]
    Hash = solders["Hash"]

    token_program_id = Pubkey.from_string(TOKEN_PROGRAM_ID)
    ata_program_id = Pubkey.from_string(ATA_PROGRAM_ID)
    system_program_id = Pubkey.from_string(SYSTEM_PROGRAM_ID)
    rent_sysvar_id = Pubkey.from_string(RENT_SYSVAR_ID)

    payer_wallet = load_solana_wallet_address()
    payer = Pubkey.from_string(payer_wallet)
    mint = Pubkey.from_string(accept_option.get("asset") or USDC_MINT_SOLANA)
    destination, setup_needed = _resolve_destination_token_account(accept_option, Pubkey, token_program_id, ata_program_id)

    if not setup_needed or _account_exists(str(destination)):
        return

    blockhash = _get_recent_blockhash(Hash)
    create_ata_data = bytes([1])  # CreateIdempotent
    create_ata_ix = Instruction(
        ata_program_id,
        create_ata_data,
        [
            AccountMeta(payer, True, True),
            AccountMeta(destination, False, True),
            AccountMeta(Pubkey.from_string(accept_option["payTo"]), False, False),
            AccountMeta(mint, False, False),
            AccountMeta(system_program_id, False, False),
            AccountMeta(token_program_id, False, False),
            AccountMeta(rent_sysvar_id, False, False),
        ],
    )
    message = MessageV0.try_compile(payer, [create_ata_ix], [], blockhash)

    keypair = _load_keypair(Keypair)
    if str(keypair.pubkey()) != str(payer):
        raise ValueError("SOLANA_SECRET_KEY does not match payer wallet address")

    setup_tx = VersionedTransaction(message, [keypair])
    sig = _send_and_confirm_transaction(bytes(setup_tx))
    print(f"Created recipient USDC token account (setup tx: {sig})")


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

    token_program_id = Pubkey.from_string(TOKEN_PROGRAM_ID)
    ata_program_id = Pubkey.from_string(ATA_PROGRAM_ID)

    payer_pubkey = Pubkey.from_string(payer_wallet_address)

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
    mint = Pubkey.from_string(accept_option.get("asset") or USDC_MINT_SOLANA)
    amount = int(accept_option["maxAmountRequired"])

    source_ata = _get_ata(payer_pubkey, mint, token_program_id, ata_program_id, Pubkey)
    dest_ata, _ = _resolve_destination_token_account(accept_option, Pubkey, token_program_id, ata_program_id)
    if not _account_exists(str(dest_ata)):
        raise ValueError(
            "Recipient USDC token account is missing. "
            "Run ensure_solana_destination_ready() before creating X-Payment."
        )

    # Keep exactly 3 instructions for x402 exact-scheme Solana verification.
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
            "Set SOLANA_WALLET_ADDRESS or use matching key."
        )

    signers = [keypair]
    if str(fee_payer) != str(payer_pubkey):
        signers.append(NullSigner(fee_payer))

    tx = VersionedTransaction(message, signers)
    return base64.b64encode(bytes(tx)).decode()


def create_solana_xpayment_from_accept(accept_option: Dict[str, Any]) -> str:
    network = str(accept_option.get("network", "")).lower()
    if network != "solana" and not network.startswith("solana:"):
        raise ValueError(f"Expected Solana accept option, got network={accept_option.get('network')}")

    payer = load_solana_wallet_address()
    signed_tx = _build_transaction_base64(accept_option, payer_wallet_address=payer)
    payload_network = str(accept_option.get("network") or "solana")
    x402_version = int(accept_option.get("x402Version") or 1)

    payload = {
        "x402Version": x402_version,
        "scheme": "exact",
        "network": payload_network,
        "payload": {"transaction": signed_tx},
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()
