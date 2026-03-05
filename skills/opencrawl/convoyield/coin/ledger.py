"""
ConvoCoin Ledger — Persistent transaction storage.

Saves and loads the entire blockchain state to/from JSON files.
This allows ConvoCoin state to persist across bot restarts.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from convoyield.coin.blockchain import Blockchain, Block, Transaction


class Ledger:
    """
    Persistent ledger for ConvoCoin blockchain state.

    Handles serialization/deserialization of the blockchain
    to a local JSON file for persistence across sessions.
    """

    DEFAULT_PATH = Path.home() / ".convoyield" / "ledger.json"

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else self.DEFAULT_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, blockchain: Blockchain) -> str:
        """
        Save the blockchain state to disk.

        Returns the file path where the ledger was saved.
        """
        state = {
            "version": "1.0.0",
            "saved_at": time.time(),
            "chain": [self._serialize_block(b) for b in blockchain.chain],
            "pending_transactions": [
                t.to_dict() for t in blockchain.pending_transactions
            ],
            "total_supply_mined": blockchain.total_supply_mined,
        }

        # Atomic write: write to temp file, then rename
        tmp_path = self.path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(state, f, indent=2)
        tmp_path.rename(self.path)

        return str(self.path)

    def load(self) -> Blockchain | None:
        """
        Load blockchain state from disk.

        Returns a Blockchain instance, or None if no ledger exists.
        """
        if not self.path.exists():
            return None

        with open(self.path) as f:
            state = json.load(f)

        blockchain = Blockchain.__new__(Blockchain)
        blockchain.chain = []
        blockchain.pending_transactions = []
        blockchain.total_supply_mined = state.get("total_supply_mined", 0.0)

        # Reconstruct chain
        for block_data in state["chain"]:
            block = self._deserialize_block(block_data)
            blockchain.chain.append(block)

        # Reconstruct pending transactions
        for tx_data in state.get("pending_transactions", []):
            tx = self._deserialize_transaction(tx_data)
            blockchain.pending_transactions.append(tx)

        # Validate chain integrity
        if not blockchain.validate_chain():
            return None  # Tampered ledger — refuse to load

        return blockchain

    def exists(self) -> bool:
        """Check if a ledger file exists."""
        return self.path.exists()

    def backup(self) -> str | None:
        """Create a backup of the current ledger."""
        if not self.path.exists():
            return None

        backup_name = f"ledger_backup_{int(time.time())}.json"
        backup_path = self.path.parent / backup_name

        with open(self.path) as src, open(backup_path, "w") as dst:
            dst.write(src.read())

        return str(backup_path)

    def get_info(self) -> dict:
        """Get ledger file info without loading the full chain."""
        if not self.path.exists():
            return {"exists": False, "path": str(self.path)}

        stat = os.stat(self.path)
        with open(self.path) as f:
            state = json.load(f)

        return {
            "exists": True,
            "path": str(self.path),
            "size_bytes": stat.st_size,
            "saved_at": state.get("saved_at"),
            "version": state.get("version"),
            "chain_length": len(state.get("chain", [])),
            "total_supply_mined": state.get("total_supply_mined", 0),
        }

    @staticmethod
    def _serialize_block(block: Block) -> dict:
        return {
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": [t.to_dict() for t in block.transactions],
            "proof_of_yield": block.proof_of_yield,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "hash": block.hash,
        }

    @staticmethod
    def _deserialize_block(data: dict) -> Block:
        transactions = [
            Ledger._deserialize_transaction(t)
            for t in data["transactions"]
        ]

        block = Block.__new__(Block)
        block.index = data["index"]
        block.timestamp = data["timestamp"]
        block.transactions = transactions
        block.proof_of_yield = data["proof_of_yield"]
        block.previous_hash = data["previous_hash"]
        block.nonce = data.get("nonce", 0)
        block.hash = data["hash"]

        return block

    @staticmethod
    def _deserialize_transaction(data: dict) -> Transaction:
        tx = Transaction.__new__(Transaction)
        tx.tx_type = data["tx_type"]
        tx.sender = data["sender"]
        tx.recipient = data["recipient"]
        tx.amount = data["amount"]
        tx.timestamp = data["timestamp"]
        tx.metadata = data.get("metadata", {})
        tx.tx_hash = data.get("tx_hash", "")
        return tx
