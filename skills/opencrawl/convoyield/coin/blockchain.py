"""
ConvoCoin Blockchain — Immutable chain of yield-backed blocks.

Each block records yield captures, conversions, and token transfers.
Integrity is guaranteed by SHA-256 hash chains. No external dependencies.

This is NOT a distributed consensus blockchain — it's a local ledger
with cryptographic integrity, designed for a single operator or
a centralized ConvoYield Cloud deployment. Think of it as a
tamper-evident audit trail for conversational value.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Transaction:
    """A single token transfer or yield event on the chain."""

    tx_type: str  # "mine", "transfer", "purchase", "reward", "stake", "unstake"
    sender: str  # wallet address or "NETWORK" for mining rewards
    recipient: str  # wallet address
    amount: float  # ConvoCoin amount
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)
    tx_hash: str = ""

    def __post_init__(self):
        if not self.tx_hash:
            self.tx_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        data = f"{self.tx_type}:{self.sender}:{self.recipient}:{self.amount}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Block:
    """
    A block in the ConvoCoin chain.

    Each block contains:
    - A set of transactions (yield captures, transfers, purchases)
    - A proof-of-yield score (how much conversational value was captured)
    - A SHA-256 link to the previous block
    """

    index: int
    timestamp: float
    transactions: list[Transaction]
    proof_of_yield: float  # Total yield captured to produce this block
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_data = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "proof_of_yield": self.proof_of_yield,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_data.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "proof_of_yield": self.proof_of_yield,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }


class Blockchain:
    """
    The ConvoCoin blockchain.

    A tamper-evident chain of blocks where each block is backed by
    real conversational yield. Mining requires proof-of-yield —
    you must demonstrate that actual value was captured in
    conversations to earn ConvoCoin.
    """

    GENESIS_HASH = "0" * 64
    BLOCK_REWARD_BASE = 10.0  # Initial mining reward per block
    MIN_YIELD_PER_BLOCK = 1.0  # Minimum yield to mine a block

    def __init__(self):
        self.chain: list[Block] = []
        self.pending_transactions: list[Transaction] = []
        self.total_supply_mined: float = 0.0
        self._create_genesis_block()

    def _create_genesis_block(self):
        """Create the genesis block — the beginning of ConvoCoin."""
        genesis = Block(
            index=0,
            timestamp=time.time(),
            transactions=[
                Transaction(
                    tx_type="genesis",
                    sender="NETWORK",
                    recipient="NETWORK",
                    amount=0,
                    metadata={"message": "ConvoCoin Genesis — Proof of Yield"},
                )
            ],
            proof_of_yield=0.0,
            previous_hash=self.GENESIS_HASH,
        )
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    @property
    def height(self) -> int:
        return len(self.chain)

    @property
    def total_transactions(self) -> int:
        return sum(len(b.transactions) for b in self.chain)

    def add_transaction(self, transaction: Transaction) -> str:
        """Add a transaction to the pending pool."""
        self.pending_transactions.append(transaction)
        return transaction.tx_hash

    def mine_block(self, miner_address: str, yield_proof: float) -> Optional[Block]:
        """
        Mine a new block with proof-of-yield.

        Unlike proof-of-work (burn electricity) or proof-of-stake (lock capital),
        proof-of-yield requires demonstrating that real conversational value
        was captured. The yield_proof is the total dollar value of yield
        captured since the last block.

        Args:
            miner_address: Wallet address of the miner (bot operator)
            yield_proof: Total yield captured to justify this block

        Returns:
            The new block, or None if insufficient yield
        """
        if yield_proof < self.MIN_YIELD_PER_BLOCK:
            return None

        # Calculate block reward based on tokenomics
        reward = self._calculate_reward(yield_proof)

        # Add mining reward transaction
        reward_tx = Transaction(
            tx_type="mine",
            sender="NETWORK",
            recipient=miner_address,
            amount=reward,
            metadata={
                "yield_proof": yield_proof,
                "block_height": self.height,
            },
        )

        # Collect pending transactions + reward
        block_transactions = [reward_tx] + self.pending_transactions.copy()

        # Create the new block
        new_block = Block(
            index=self.height,
            timestamp=time.time(),
            transactions=block_transactions,
            proof_of_yield=yield_proof,
            previous_hash=self.last_block.hash,
        )

        # Validate and add to chain
        if self._validate_block(new_block):
            self.chain.append(new_block)
            self.pending_transactions.clear()
            self.total_supply_mined += reward
            return new_block

        return None

    def _calculate_reward(self, yield_proof: float) -> float:
        """
        Calculate mining reward using yield-proportional + halving schedule.

        Reward = base_reward * yield_multiplier * halving_factor

        The reward scales with how much yield was captured (incentivizing
        better bots) but also halves every 1000 blocks (limiting supply).
        """
        # Halving: reward halves every 1000 blocks
        halvings = self.height // 1000
        halving_factor = 0.5 ** halvings

        # Yield multiplier: more yield = slightly more reward (capped)
        # This incentivizes capturing value, not just processing volume
        yield_multiplier = min(2.0, 1.0 + (yield_proof / 100.0))

        reward = self.BLOCK_REWARD_BASE * halving_factor * yield_multiplier
        return round(reward, 8)

    def _validate_block(self, block: Block) -> bool:
        """Validate a block's integrity."""
        # Check hash chain
        if block.previous_hash != self.last_block.hash:
            return False

        # Check index
        if block.index != self.height:
            return False

        # Verify hash
        computed = block.compute_hash()
        if computed != block.hash:
            return False

        return True

    def validate_chain(self) -> bool:
        """Validate the entire chain's integrity."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Verify hash chain
            if current.previous_hash != previous.hash:
                return False

            # Verify block hash
            if current.compute_hash() != current.hash:
                return False

        return True

    def get_balance(self, address: str) -> float:
        """Get the ConvoCoin balance of an address."""
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return round(balance, 8)

    def get_transaction_history(self, address: str) -> list[dict]:
        """Get all transactions involving an address."""
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.recipient == address:
                    entry = tx.to_dict()
                    entry["block_index"] = block.index
                    entry["direction"] = "in" if tx.recipient == address else "out"
                    history.append(entry)
        return history

    def get_stats(self) -> dict:
        """Get blockchain statistics."""
        total_yield = sum(b.proof_of_yield for b in self.chain)
        total_txs = sum(len(b.transactions) for b in self.chain)

        return {
            "chain_height": self.height,
            "total_supply_mined": round(self.total_supply_mined, 8),
            "total_yield_proven": round(total_yield, 2),
            "total_transactions": total_txs,
            "pending_transactions": len(self.pending_transactions),
            "chain_valid": self.validate_chain(),
            "current_block_reward": round(
                self._calculate_reward(self.MIN_YIELD_PER_BLOCK), 8
            ),
            "next_halving_block": ((self.height // 1000) + 1) * 1000,
            "halvings_occurred": self.height // 1000,
        }

    def to_dict(self) -> dict:
        return {
            "chain": [b.to_dict() for b in self.chain],
            "stats": self.get_stats(),
        }
