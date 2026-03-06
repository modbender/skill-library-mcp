"""
Mempool — Transaction pool with validation and fee-priority ordering.

Like Bitcoin's mempool, this is the waiting room for transactions.
When a miner creates a block, they select transactions from the
mempool, prioritized by fee rate (fee per byte, roughly).

Transactions sit in the mempool until:
1. A miner includes them in a block (confirmed)
2. They expire (default: 72 hours)
3. Their inputs get spent by another transaction (conflict)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from convoyield.coin.utxo import UTXOTransaction, UTXOSet


@dataclass
class MempoolEntry:
    """A transaction waiting in the mempool."""

    transaction: UTXOTransaction
    added_at: float = field(default_factory=time.time)
    fee: float = 0.0
    size_bytes: int = 0  # Approximate serialized size
    priority: float = 0.0  # Fee rate for ordering

    def __post_init__(self):
        # Estimate transaction size (simplified)
        self.size_bytes = (
            len(self.transaction.inputs) * 148 +  # ~148 bytes per input
            len(self.transaction.outputs) * 34 +   # ~34 bytes per output
            10  # Header overhead
        )
        # Priority = fee per byte (like Bitcoin's sat/vbyte)
        if self.size_bytes > 0:
            self.priority = self.fee / self.size_bytes

    @property
    def age_seconds(self) -> float:
        return time.time() - self.added_at

    def is_expired(self, max_age: float = 259200) -> bool:
        """Check if transaction has expired (default: 72 hours)."""
        return self.age_seconds > max_age


class Mempool:
    """
    The transaction mempool.

    Validates, stores, and prioritizes unconfirmed transactions.
    """

    MAX_SIZE = 5000  # Maximum transactions in mempool
    MIN_FEE = 0.0001  # Minimum fee to accept
    MAX_AGE = 259200  # 72 hours in seconds

    def __init__(self, utxo_set: UTXOSet):
        self._pool: dict[str, MempoolEntry] = {}
        self._utxo_set = utxo_set
        self._spent_outputs: set[str] = set()  # Track outputs claimed by mempool txs

    def add_transaction(self, tx: UTXOTransaction) -> tuple[bool, str]:
        """
        Validate and add a transaction to the mempool.

        Validation checks:
        1. Transaction not already in mempool
        2. All inputs reference unspent UTXOs
        3. Input sum >= output sum
        4. No double-spends within the mempool
        5. Fee meets minimum threshold
        6. Mempool isn't full

        Returns:
            (success: bool, reason: str)
        """
        # Check: not a duplicate
        if tx.tx_hash in self._pool:
            return False, "Transaction already in mempool"

        # Check: mempool capacity
        if len(self._pool) >= self.MAX_SIZE:
            self._evict_lowest_fee()

        # Coinbase transactions don't go in the mempool
        if tx.tx_type == "coinbase":
            return False, "Coinbase transactions are not mempoolable"

        # Check: all inputs exist and are unspent
        input_sum = 0.0
        for inp in tx.inputs:
            utxo = self._utxo_set.get(inp.utxo_id)
            if utxo is None:
                return False, f"Input {inp.utxo_id} does not exist"

            if inp.utxo_id in self._spent_outputs:
                return False, f"Double-spend: {inp.utxo_id} already claimed"

            input_sum += utxo.amount

        # Check: outputs don't exceed inputs
        output_sum = sum(out.amount for out in tx.outputs)
        if input_sum < output_sum:
            return False, "Outputs exceed inputs"

        # Check: minimum fee
        fee = input_sum - output_sum
        if fee < self.MIN_FEE:
            return False, f"Fee too low: {fee} < {self.MIN_FEE}"

        # All checks pass — add to mempool
        entry = MempoolEntry(transaction=tx, fee=fee)
        self._pool[tx.tx_hash] = entry

        # Mark inputs as claimed
        for inp in tx.inputs:
            self._spent_outputs.add(inp.utxo_id)

        return True, "Accepted"

    def remove_transaction(self, tx_hash: str):
        """Remove a transaction from the mempool (e.g., after mining)."""
        entry = self._pool.pop(tx_hash, None)
        if entry:
            for inp in entry.transaction.inputs:
                self._spent_outputs.discard(inp.utxo_id)

    def select_for_block(self, max_transactions: int = 100) -> list[UTXOTransaction]:
        """
        Select transactions for inclusion in a new block.

        Prioritized by fee rate (highest fee per byte first).
        This is how miners maximize their revenue — they pick
        the transactions that pay the most per unit of block space.
        """
        # Remove expired transactions first
        self._purge_expired()

        # Sort by priority (fee rate) descending
        sorted_entries = sorted(
            self._pool.values(),
            key=lambda e: e.priority,
            reverse=True,
        )

        selected = []
        for entry in sorted_entries[:max_transactions]:
            selected.append(entry.transaction)

        return selected

    def confirm_block(self, tx_hashes: list[str]):
        """
        Remove transactions that were confirmed in a block.

        Called after a block is mined and added to the chain.
        """
        for tx_hash in tx_hashes:
            self.remove_transaction(tx_hash)

    def _evict_lowest_fee(self):
        """Evict the lowest-fee transaction to make room."""
        if not self._pool:
            return

        lowest = min(self._pool.values(), key=lambda e: e.priority)
        self.remove_transaction(lowest.transaction.tx_hash)

    def _purge_expired(self):
        """Remove all expired transactions."""
        expired = [
            tx_hash for tx_hash, entry in self._pool.items()
            if entry.is_expired(self.MAX_AGE)
        ]
        for tx_hash in expired:
            self.remove_transaction(tx_hash)

    @property
    def size(self) -> int:
        return len(self._pool)

    @property
    def total_fees(self) -> float:
        return sum(e.fee for e in self._pool.values())

    def get_stats(self) -> dict:
        """Get mempool statistics."""
        fees = [e.fee for e in self._pool.values()]
        return {
            "size": self.size,
            "total_fees": round(self.total_fees, 8),
            "avg_fee": round(sum(fees) / len(fees), 8) if fees else 0,
            "max_fee": round(max(fees), 8) if fees else 0,
            "min_fee": round(min(fees), 8) if fees else 0,
            "claimed_outputs": len(self._spent_outputs),
        }

    def get_transaction(self, tx_hash: str) -> Optional[MempoolEntry]:
        """Look up a transaction in the mempool."""
        return self._pool.get(tx_hash)

    def to_dict(self) -> dict:
        return {
            "transactions": {
                k: {
                    "tx": v.transaction.to_dict(),
                    "fee": v.fee,
                    "priority": v.priority,
                    "age_seconds": v.age_seconds,
                }
                for k, v in self._pool.items()
            },
            "stats": self.get_stats(),
        }
