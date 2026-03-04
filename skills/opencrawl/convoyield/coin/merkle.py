"""
Merkle Tree — Cryptographic proof of transaction integrity.

Bitcoin uses Merkle trees so any node can verify that a transaction
is included in a block without downloading the entire block.

Our Merkle tree is identical to Bitcoin's:
- Leaves are double-SHA256 hashes of transactions
- Interior nodes are double-SHA256 of their children concatenated
- If odd number of leaves, the last one is duplicated
- Root hash is stored in the block header

This enables Simplified Payment Verification (SPV):
a lightweight client can verify a transaction with just a
Merkle proof (O(log n) hashes) instead of the full block.
"""

from __future__ import annotations

import hashlib
from typing import Optional


def double_sha256(data: bytes) -> bytes:
    """Bitcoin-style double SHA-256 hash."""
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def double_sha256_hex(data: str) -> str:
    """Double SHA-256 returning hex string."""
    return double_sha256(data.encode()).hex()


class MerkleTree:
    """
    A Bitcoin-compatible Merkle tree.

    Provides:
    - Tamper-evident root hash for block headers
    - O(log n) inclusion proofs for any transaction
    - SPV-compatible verification
    """

    def __init__(self, tx_hashes: list[str]):
        """
        Build a Merkle tree from a list of transaction hashes.

        Args:
            tx_hashes: List of hex-encoded transaction hashes
        """
        if not tx_hashes:
            self.root = "0" * 64
            self._levels: list[list[str]] = []
            self._tx_hashes = []
            return

        self._tx_hashes = list(tx_hashes)
        self._levels = self._build(self._tx_hashes)
        self.root = self._levels[-1][0]

    def _build(self, leaves: list[str]) -> list[list[str]]:
        """Build the tree bottom-up, returning all levels."""
        levels = [leaves]
        current = leaves

        while len(current) > 1:
            next_level = []

            # If odd, duplicate the last hash (Bitcoin behavior)
            if len(current) % 2 == 1:
                current = current + [current[-1]]

            for i in range(0, len(current), 2):
                combined = bytes.fromhex(current[i]) + bytes.fromhex(current[i + 1])
                parent = double_sha256(combined).hex()
                next_level.append(parent)

            levels.append(next_level)
            current = next_level

        return levels

    def get_proof(self, tx_hash: str) -> Optional[list[dict]]:
        """
        Get a Merkle proof for a transaction.

        Returns a list of proof steps, each containing:
        - hash: The sibling hash needed for verification
        - position: "left" or "right" (where the sibling sits)

        With this proof + the tx_hash + the known root, anyone can
        verify the transaction's inclusion in O(log n) time.
        """
        if not self._levels or tx_hash not in self._tx_hashes:
            return None

        proof = []
        current = self._levels[0]

        # Find the index of our transaction
        try:
            idx = current.index(tx_hash)
        except ValueError:
            return None

        for level in self._levels[:-1]:
            # Duplicate last if odd (matching build behavior)
            working = list(level)
            if len(working) % 2 == 1:
                working.append(working[-1])

            # Find our sibling
            if idx % 2 == 0:
                sibling_idx = idx + 1
                position = "right"
            else:
                sibling_idx = idx - 1
                position = "left"

            if sibling_idx < len(working):
                proof.append({
                    "hash": working[sibling_idx],
                    "position": position,
                })

            # Move up to parent index
            idx = idx // 2

        return proof

    @staticmethod
    def verify_proof(
        tx_hash: str,
        proof: list[dict],
        expected_root: str,
    ) -> bool:
        """
        Verify a Merkle proof — SPV verification.

        This is how lightweight Bitcoin wallets verify transactions
        without downloading the full blockchain. They just need:
        1. The transaction hash
        2. The Merkle proof (O(log n) hashes)
        3. The block header (which contains the Merkle root)

        Args:
            tx_hash: The hash of the transaction to verify
            proof: The Merkle proof from get_proof()
            expected_root: The Merkle root from the block header

        Returns:
            True if the transaction is verified in the tree
        """
        current = tx_hash

        for step in proof:
            sibling = step["hash"]
            if step["position"] == "right":
                combined = bytes.fromhex(current) + bytes.fromhex(sibling)
            else:
                combined = bytes.fromhex(sibling) + bytes.fromhex(current)

            current = double_sha256(combined).hex()

        return current == expected_root

    @property
    def leaf_count(self) -> int:
        return len(self._tx_hashes)

    @property
    def depth(self) -> int:
        return len(self._levels)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "leaf_count": self.leaf_count,
            "depth": self.depth,
            "leaves": self._tx_hashes,
        }
