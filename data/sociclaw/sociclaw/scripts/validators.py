"""
Input validators used across CLI and clients.
"""

from __future__ import annotations

import re

PROVIDER_PATTERN = re.compile(r"^[a-z0-9_-]{2,32}$", re.IGNORECASE)
PROVIDER_USER_ID_PATTERN = re.compile(r"^[a-zA-Z0-9:_@.\-]{1,128}$")
TX_HASH_PATTERN = re.compile(r"^0x[a-fA-F0-9]{64}$")


def validate_provider(value: str) -> str:
    data = str(value or "").strip()
    if not PROVIDER_PATTERN.fullmatch(data):
        raise ValueError("Invalid provider format. Allowed: letters, numbers, _ and -, length 2-32.")
    return data


def validate_provider_user_id(value: str) -> str:
    data = str(value or "").strip()
    if not PROVIDER_USER_ID_PATTERN.fullmatch(data):
        raise ValueError("Invalid provider_user_id format. Allowed length 1-128.")
    return data


def validate_tx_hash(value: str) -> str:
    data = str(value or "").strip()
    if not TX_HASH_PATTERN.fullmatch(data):
        raise ValueError("Invalid tx hash format. Expected 0x + 64 hex chars.")
    return data
