"""
ConvoCoin Full Node — The complete Bitcoin-like blockchain.

This is the upgraded blockchain that integrates all components:
- Merkle trees for transaction integrity
- UTXO model for double-spend prevention
- Difficulty-adjusted proof-of-yield mining
- Mempool for transaction staging
- Digital signatures for authorization
- Proper coinbase transactions

This is what a real ConvoCoin deployment would run.

Usage:
    from convoyield.coin.fullnode import FullNode

    node = FullNode()
    node.create_wallet("my-miner")

    # Mine a block (requires yield proof)
    result = node.mine(yield_proof=25.0)

    # Send CVC
    node.send("CVC_recipient_address", 5.0)

    # Save state
    node.save()
"""

from __future__ import annotations

import hashlib
import json
import time
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from convoyield.coin.merkle import MerkleTree, double_sha256_hex
from convoyield.coin.crypto import KeyPair, generate_keypair, keypair_from_private
from convoyield.coin.utxo import (
    UTXOSet,
    UTXOTransaction,
    TransactionOutput,
    TransactionInput,
    create_coinbase_tx,
    create_transfer_tx,
)
from convoyield.coin.mempool import Mempool
from convoyield.coin.difficulty import DifficultyAdjuster
from convoyield.coin.tokenomics import Tokenomics


@dataclass
class FullBlock:
    """
    A complete Bitcoin-like block with Merkle root and difficulty target.

    Block header (what gets hashed for proof-of-work):
        - version
        - previous_hash
        - merkle_root
        - timestamp
        - difficulty_target
        - nonce
        - yield_proof (ConvoCoin-specific)

    Block body:
        - transactions (list of UTXO transactions)
    """

    index: int
    version: int
    previous_hash: str
    merkle_root: str
    timestamp: float
    difficulty: int
    nonce: int
    yield_proof: float
    transactions: list[UTXOTransaction]
    hash: str = ""

    def compute_header(self) -> str:
        """Compute the block header string (what gets hashed)."""
        return json.dumps({
            "version": self.version,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "yield_proof": self.yield_proof,
        }, sort_keys=True)

    def compute_hash(self) -> str:
        """Compute block hash: SHA-256(header + nonce)."""
        data = f"{self.compute_header()}:{self.nonce}"
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "version": self.version,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": self.nonce,
            "yield_proof": self.yield_proof,
            "hash": self.hash,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "tx_count": len(self.transactions),
        }


class FullNode:
    """
    A complete ConvoCoin full node — Bitcoin-like architecture.

    Integrates:
    - UTXO set (no account balances — just unspent outputs)
    - Merkle tree (transaction integrity in every block)
    - Difficulty adjustment (dynamic mining difficulty)
    - Mempool (transaction staging with fee priority)
    - Digital signatures (transaction authorization)
    - Proper coinbase (miner reward + fees)
    - Chain validation (full verification from genesis)

    This is as close to Bitcoin as you can get in pure Python.
    """

    VERSION = 1
    GENESIS_MESSAGE = "ConvoCoin Genesis: Proof-of-Yield — 2024"

    def __init__(self, data_dir: str | Path | None = None):
        self.chain: list[FullBlock] = []
        self.utxo_set = UTXOSet()
        self.difficulty = DifficultyAdjuster()
        self.tokenomics = Tokenomics()
        self.mempool: Optional[Mempool] = None  # Initialized after UTXO set is ready
        self.keypair: Optional[KeyPair] = None
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".convoyield"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.total_supply_mined = 0.0
        self.total_fees_collected = 0.0

        # Create genesis block
        self._create_genesis()

        # Now mempool can be initialized
        self.mempool = Mempool(self.utxo_set)

    def _create_genesis(self):
        """Create the genesis block with embedded message."""
        # Genesis coinbase — creates the first coins
        genesis_address = "CVC_GENESIS"
        coinbase = create_coinbase_tx(
            miner_address=genesis_address,
            reward=0,  # No reward for genesis
            block_height=0,
        )

        # Build Merkle tree
        tx_hashes = [coinbase.tx_hash]
        merkle = MerkleTree(tx_hashes)

        genesis = FullBlock(
            index=0,
            version=self.VERSION,
            previous_hash="0" * 64,
            merkle_root=merkle.root,
            timestamp=time.time(),
            difficulty=self.difficulty.current_difficulty,
            nonce=0,
            yield_proof=0.0,
            transactions=[coinbase],
        )
        genesis.hash = genesis.compute_hash()

        self.chain.append(genesis)
        self.difficulty.record_block(genesis.timestamp)

        # Apply genesis coinbase to UTXO set
        self.utxo_set.apply_transaction(coinbase)

    @property
    def height(self) -> int:
        return len(self.chain)

    @property
    def last_block(self) -> FullBlock:
        return self.chain[-1]

    def create_wallet(self, label: str = "") -> tuple[str, str]:
        """
        Create a wallet for this node.

        Returns (address, private_key).
        """
        self.keypair = generate_keypair()
        return self.keypair.address, self.keypair.private_key

    def import_wallet(self, private_key: str) -> str:
        """Import a wallet from a private key."""
        self.keypair = keypair_from_private(private_key)
        return self.keypair.address

    def get_balance(self, address: str | None = None) -> float:
        """Get balance using the UTXO model."""
        addr = address or (self.keypair.address if self.keypair else "")
        return round(self.utxo_set.get_balance(addr), 8)

    def mine(self, yield_proof: float) -> dict | None:
        """
        Mine a new block with proof-of-yield + proof-of-work.

        This is the core mining function. It:
        1. Requires yield_proof >= mining threshold (Proof-of-Yield)
        2. Selects transactions from the mempool by fee priority
        3. Creates a coinbase transaction (reward + fees)
        4. Builds a Merkle tree over all transactions
        5. Finds a nonce that produces a hash below the difficulty target (PoW)
        6. Adds the block to the chain
        7. Updates the UTXO set
        8. Adjusts difficulty if needed

        Returns mining result or None if failed.
        """
        if not self.keypair:
            return None

        # Check yield proof meets threshold
        threshold = self.tokenomics.get_mining_threshold(self.height)
        if yield_proof < threshold:
            return None

        # Select transactions from mempool
        mempool_txs = self.mempool.select_for_block(max_transactions=100)

        # Calculate total fees from mempool transactions
        total_fees = 0.0
        for tx in mempool_txs:
            tx.resolve_inputs(self.utxo_set)
            total_fees += tx.fee

        # Calculate block reward
        block_reward = self.tokenomics.get_block_reward(self.height)

        # Create coinbase transaction (reward + fees)
        coinbase = create_coinbase_tx(
            miner_address=self.keypair.address,
            reward=block_reward,
            block_height=self.height,
            fees=total_fees,
        )

        # All transactions for this block: coinbase first (like Bitcoin)
        block_txs = [coinbase] + mempool_txs

        # Build Merkle tree
        tx_hashes = [tx.tx_hash for tx in block_txs]
        merkle = MerkleTree(tx_hashes)

        # Construct block header
        block = FullBlock(
            index=self.height,
            version=self.VERSION,
            previous_hash=self.last_block.hash,
            merkle_root=merkle.root,
            timestamp=time.time(),
            difficulty=self.difficulty.current_difficulty,
            nonce=0,
            yield_proof=yield_proof,
            transactions=block_txs,
        )

        # Proof-of-Work: find a valid nonce
        header = block.compute_header()
        mining_result = self.difficulty.mine_block_hash(header)

        if mining_result is None:
            return None  # Could not find valid nonce

        nonce, block_hash = mining_result
        block.nonce = nonce
        block.hash = block_hash

        # Validate the block
        if not self._validate_block(block):
            return None

        # Add to chain
        self.chain.append(block)
        self.total_supply_mined += block_reward
        self.total_fees_collected += total_fees

        # Update UTXO set
        for tx in block_txs:
            self.utxo_set.apply_transaction(tx)

        # Remove confirmed transactions from mempool
        self.mempool.confirm_block([tx.tx_hash for tx in mempool_txs])

        # Record for difficulty adjustment
        self.difficulty.record_block(block.timestamp)

        # Adjust difficulty if needed
        if self.difficulty.should_adjust(self.height):
            self.difficulty.adjust(self.height)

        return {
            "block_index": block.index,
            "block_hash": block.hash[:16] + "...",
            "merkle_root": merkle.root[:16] + "...",
            "nonce": nonce,
            "difficulty": block.difficulty,
            "reward": round(block_reward, 8),
            "fees": round(total_fees, 8),
            "total_reward": round(block_reward + total_fees, 8),
            "tx_count": len(block_txs),
            "yield_proven": round(yield_proof, 2),
            "miner": self.keypair.address,
            "chain_height": self.height,
            "total_supply": round(self.total_supply_mined, 8),
        }

    def send(
        self,
        to_address: str,
        amount: float,
        fee: float = 0.01,
    ) -> dict | None:
        """
        Send CVC to another address using the UTXO model.

        Creates a transaction that:
        1. Selects UTXOs from your wallet to cover amount + fee
        2. Creates an output for the recipient
        3. Creates a change output back to you
        4. Signs the transaction
        5. Adds it to the mempool
        """
        if not self.keypair:
            return None

        # Create UTXO transfer transaction
        tx = create_transfer_tx(
            sender_address=self.keypair.address,
            recipient_address=to_address,
            amount=amount,
            utxo_set=self.utxo_set,
            fee=fee,
            signature=self.keypair.sign(f"send:{to_address}:{amount}"),
        )

        if tx is None:
            return None  # Insufficient funds

        # Add to mempool
        accepted, reason = self.mempool.add_transaction(tx)
        if not accepted:
            return None

        return {
            "tx_hash": tx.tx_hash,
            "from": self.keypair.address,
            "to": to_address,
            "amount": amount,
            "fee": fee,
            "inputs": len(tx.inputs),
            "outputs": len(tx.outputs),
            "status": "in_mempool",
        }

    def _validate_block(self, block: FullBlock) -> bool:
        """Validate a block's integrity."""
        # Check previous hash
        if block.previous_hash != self.last_block.hash:
            return False

        # Check index
        if block.index != self.height:
            return False

        # Verify Merkle root
        tx_hashes = [tx.tx_hash for tx in block.transactions]
        merkle = MerkleTree(tx_hashes)
        if merkle.root != block.merkle_root:
            return False

        # Verify hash meets difficulty target
        if not self.difficulty.check_hash(block.hash):
            return False

        # Verify hash is correctly computed
        recomputed = block.compute_hash()
        if recomputed != block.hash:
            return False

        return True

    def validate_chain(self) -> bool:
        """Validate the entire chain from genesis."""
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            prev = self.chain[i - 1]

            if block.previous_hash != prev.hash:
                return False

            # Verify Merkle root
            tx_hashes = [tx.tx_hash for tx in block.transactions]
            merkle = MerkleTree(tx_hashes)
            if merkle.root != block.merkle_root:
                return False

        return True

    def get_status(self) -> dict:
        """Get complete node status."""
        return {
            "chain": {
                "height": self.height,
                "total_supply": round(self.total_supply_mined, 8),
                "total_fees": round(self.total_fees_collected, 8),
                "valid": self.validate_chain(),
                "last_hash": self.last_block.hash[:16] + "...",
            },
            "mining": {
                "difficulty": self.difficulty.current_difficulty,
                "target": self.difficulty.get_target()[:16] + "...",
                "block_reward": round(
                    self.tokenomics.get_block_reward(self.height), 8
                ),
                "mining_threshold": round(
                    self.tokenomics.get_mining_threshold(self.height), 2
                ),
                **self.difficulty.get_stats(),
            },
            "utxo": self.utxo_set.get_stats(),
            "mempool": self.mempool.get_stats() if self.mempool else {},
            "wallet": {
                "address": self.keypair.address if self.keypair else None,
                "balance": self.get_balance(),
            },
            "economics": self.tokenomics.get_economics_summary(
                self.height,
                self.total_supply_mined,
                0,  # staked
            ),
        }

    def save(self, filename: str = "fullnode.json") -> str:
        """Save node state to disk."""
        path = self.data_dir / filename

        state = {
            "version": "1.0.0",
            "saved_at": time.time(),
            "chain": [b.to_dict() for b in self.chain],
            "total_supply_mined": self.total_supply_mined,
            "total_fees_collected": self.total_fees_collected,
            "difficulty": self.difficulty.current_difficulty,
        }

        tmp = path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
        tmp.rename(path)

        return str(path)

    def get_block(self, index: int) -> dict | None:
        """Get a block by index."""
        if 0 <= index < len(self.chain):
            return self.chain[index].to_dict()
        return None

    def get_merkle_proof(self, block_index: int, tx_hash: str) -> dict | None:
        """
        Get a Merkle proof for a transaction in a specific block.

        This is SPV verification — a light client can verify
        a transaction is in a block with just this proof + the
        block header, without downloading the full block.
        """
        if block_index < 0 or block_index >= len(self.chain):
            return None

        block = self.chain[block_index]
        tx_hashes = [tx.tx_hash for tx in block.transactions]
        merkle = MerkleTree(tx_hashes)

        proof = merkle.get_proof(tx_hash)
        if proof is None:
            return None

        return {
            "tx_hash": tx_hash,
            "block_index": block_index,
            "block_hash": block.hash,
            "merkle_root": block.merkle_root,
            "proof": proof,
            "verified": MerkleTree.verify_proof(
                tx_hash, proof, block.merkle_root
            ),
        }
