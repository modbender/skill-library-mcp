"""
ConvoCoin Wallet — Identity and balance management.

Each bot operator gets a wallet. Wallets are identified by
a deterministic address derived from a secret key.
No external crypto libraries needed — pure hashlib.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class Wallet:
    """
    A ConvoCoin wallet.

    Addresses are derived from secret keys using SHA-256.
    This is a simplified model — not a full elliptic curve
    implementation, but sufficient for a centralized ledger.
    """

    address: str
    created_at: float = field(default_factory=time.time)
    label: str = ""
    total_mined: float = 0.0
    total_yield_proven: float = 0.0
    blocks_mined: int = 0
    staked_amount: float = 0.0

    # Private — never serialized or transmitted
    _secret_key: str = field(default="", repr=False)

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "created_at": self.created_at,
            "label": self.label,
            "total_mined": self.total_mined,
            "total_yield_proven": self.total_yield_proven,
            "blocks_mined": self.blocks_mined,
            "staked_amount": self.staked_amount,
        }


class WalletManager:
    """
    Manages ConvoCoin wallets.

    Handles wallet creation, lookup, and balance tracking.
    In a production deployment, this would be backed by a database.
    """

    ADDRESS_PREFIX = "CVC"  # ConVoCoin

    def __init__(self):
        self._wallets: dict[str, Wallet] = {}
        self._keys: dict[str, str] = {}  # secret_key -> address

    def create_wallet(self, label: str = "") -> tuple[Wallet, str]:
        """
        Create a new ConvoCoin wallet.

        Returns:
            Tuple of (wallet, secret_key). The secret key must be
            saved by the user — it cannot be recovered.
        """
        secret_key = secrets.token_hex(32)
        address = self._derive_address(secret_key)

        wallet = Wallet(
            address=address,
            label=label,
            _secret_key=secret_key,
        )

        self._wallets[address] = wallet
        self._keys[secret_key] = address

        return wallet, secret_key

    def get_wallet(self, address: str) -> Wallet | None:
        """Get a wallet by address."""
        return self._wallets.get(address)

    def authenticate(self, secret_key: str) -> Wallet | None:
        """Authenticate with a secret key and return the wallet."""
        address = self._keys.get(secret_key)
        if address:
            return self._wallets.get(address)
        return None

    def import_wallet(self, secret_key: str, label: str = "") -> Wallet:
        """Import a wallet from a secret key."""
        address = self._derive_address(secret_key)

        if address in self._wallets:
            return self._wallets[address]

        wallet = Wallet(
            address=address,
            label=label,
            _secret_key=secret_key,
        )

        self._wallets[address] = wallet
        self._keys[secret_key] = address

        return wallet

    def list_wallets(self) -> list[dict]:
        """List all wallets (public info only)."""
        return [w.to_dict() for w in self._wallets.values()]

    def record_mining(
        self,
        address: str,
        reward: float,
        yield_proven: float,
    ):
        """Record a mining event for a wallet."""
        wallet = self._wallets.get(address)
        if wallet:
            wallet.total_mined += reward
            wallet.total_yield_proven += yield_proven
            wallet.blocks_mined += 1

    def stake(self, address: str, amount: float) -> bool:
        """Stake ConvoCoin for premium features."""
        wallet = self._wallets.get(address)
        if not wallet:
            return False
        wallet.staked_amount += amount
        return True

    def unstake(self, address: str, amount: float) -> bool:
        """Unstake ConvoCoin."""
        wallet = self._wallets.get(address)
        if not wallet or wallet.staked_amount < amount:
            return False
        wallet.staked_amount -= amount
        return True

    def get_staking_tier(self, address: str) -> str:
        """
        Get the staking tier for a wallet.

        Staking tiers unlock premium features:
            - Bronze (100+ CVC): 1 premium playbook
            - Silver (500+ CVC): All playbooks + priority analytics
            - Gold (2000+ CVC): Everything + custom playbooks + white-label
        """
        wallet = self._wallets.get(address)
        if not wallet:
            return "none"

        staked = wallet.staked_amount
        if staked >= 2000:
            return "gold"
        elif staked >= 500:
            return "silver"
        elif staked >= 100:
            return "bronze"
        return "none"

    @classmethod
    def _derive_address(cls, secret_key: str) -> str:
        """Derive a wallet address from a secret key."""
        # Double-hash for address derivation (simplified RIPEMD-like scheme)
        first_hash = hashlib.sha256(secret_key.encode()).hexdigest()
        second_hash = hashlib.sha256(first_hash.encode()).hexdigest()
        # Take first 20 bytes (40 hex chars) and prefix
        short_hash = second_hash[:40]
        return f"{cls.ADDRESS_PREFIX}_{short_hash}"
