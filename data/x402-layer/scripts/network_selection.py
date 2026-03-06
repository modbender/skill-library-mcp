#!/usr/bin/env python3
"""
Shared multi-network payment option selection for x402 scripts.

Selects the best payment option (Base or Solana) from a 402 challenge based on:
- X402_PREFER_NETWORK (base/solana)
- auth mode (private-key or awal)
- available credentials
"""

import os
from typing import Any, Dict, Optional, Tuple

from solana_signing import has_solana_credentials
from wallet_signing import is_awal_mode, load_payment_signer


def is_base_network(value: str) -> bool:
    network = str(value or "").lower()
    return network == "base" or "8453" in network


def is_solana_network(value: str) -> bool:
    return str(value or "").lower() == "solana"


def pick_payment_option(
    challenge: Dict[str, Any],
    context: str = "payment",
) -> Tuple[str, Dict[str, Any], Optional[Any]]:
    """
    Returns (network, accept_option, signer_or_none).

    - Base + private-key mode: signer is PaymentSigner
    - Base + AWAL mode: signer is None (call AWAL pay wrapper)
    - Solana: signer is None (use solana_signing)
    """
    accepts = challenge.get("accepts", []) or []
    base_option = next((opt for opt in accepts if is_base_network(opt.get("network"))), None)
    solana_option = next((opt for opt in accepts if is_solana_network(opt.get("network"))), None)

    prefer = (os.getenv("X402_PREFER_NETWORK") or "base").strip().lower()
    order = ["solana", "base"] if prefer == "solana" else ["base", "solana"]

    errors = []
    for candidate in order:
        if candidate == "base" and base_option is not None:
            if is_awal_mode():
                return "base", base_option, None
            try:
                signer = load_payment_signer()
                return "base", base_option, signer
            except Exception as exc:
                errors.append(f"base unavailable: {exc}")

        if candidate == "solana" and solana_option is not None:
            if has_solana_credentials():
                return "solana", solana_option, None
            errors.append("solana unavailable: set SOLANA_SECRET_KEY")

    available = sorted({str(opt.get("network", "unknown")) for opt in accepts})
    raise ValueError(
        f"No usable payment option for {context}. "
        f"Available networks: {available}. Details: {errors}"
    )
