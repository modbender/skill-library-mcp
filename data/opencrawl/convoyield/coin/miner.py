"""
Proof-of-Yield Mining — The ConvoCoin consensus mechanism.

Instead of burning electricity (PoW) or locking capital (PoS),
ConvoCoin uses Proof-of-Yield: you mine tokens by demonstrating
that your bot captured real conversational value.

Mining flow:
    1. Your bot processes conversations using ConvoYield
    2. Each yield capture is recorded as a "yield proof"
    3. When enough yield accumulates, a block is mined
    4. You receive ConvoCoin proportional to the yield captured

This creates a direct link between token value and real economic
activity — ConvoCoin is backed by actual conversational yield.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from convoyield.coin.blockchain import Blockchain, Transaction
from convoyield.coin.wallet import WalletManager
from convoyield.coin.tokenomics import Tokenomics


@dataclass
class YieldProof:
    """A proof that conversational yield was captured."""

    session_id: str
    yield_amount: float
    captured_yield: float
    arbitrage_value: float
    micro_conversion_value: float
    plays_executed: int
    timestamp: float = field(default_factory=time.time)

    @property
    def total_proven_value(self) -> float:
        return self.captured_yield + self.arbitrage_value + self.micro_conversion_value


class ProofOfYieldMiner:
    """
    The ConvoCoin miner.

    Collects yield proofs from bot conversations and mines blocks
    when enough yield has accumulated. This is the bridge between
    the ConvoYield engine and the ConvoCoin blockchain.

    Usage:
        miner = ProofOfYieldMiner(blockchain, wallet_manager, tokenomics)
        miner.set_miner_address("CVC_abc123...")

        # After each conversation turn:
        miner.submit_yield_proof(proof)

        # Mining happens automatically when threshold is reached
    """

    def __init__(
        self,
        blockchain: Blockchain,
        wallet_manager: WalletManager,
        tokenomics: Tokenomics,
    ):
        self.blockchain = blockchain
        self.wallet_manager = wallet_manager
        self.tokenomics = tokenomics
        self.miner_address: str = ""
        self.pending_proofs: list[YieldProof] = []
        self.accumulated_yield: float = 0.0
        self.total_blocks_mined: int = 0
        self.total_coins_earned: float = 0.0
        self.mining_history: list[dict] = []

    def set_miner_address(self, address: str):
        """Set the wallet address that receives mining rewards."""
        self.miner_address = address

    def submit_yield_proof(self, proof: YieldProof) -> dict | None:
        """
        Submit a yield proof from a conversation.

        If enough yield has accumulated, a block is automatically mined.

        Returns:
            Mining result dict if a block was mined, None otherwise.
        """
        self.pending_proofs.append(proof)
        self.accumulated_yield += proof.total_proven_value

        # Check if we've accumulated enough yield to mine a block
        threshold = self.tokenomics.get_mining_threshold(
            self.blockchain.height
        )

        if self.accumulated_yield >= threshold:
            return self._mine()

        return None

    def force_mine(self) -> dict | None:
        """Force-mine a block with whatever yield has accumulated."""
        if self.accumulated_yield >= self.blockchain.MIN_YIELD_PER_BLOCK:
            return self._mine()
        return None

    def _mine(self) -> dict | None:
        """Execute the mining operation."""
        if not self.miner_address:
            return None

        # Record yield proof transactions
        for proof in self.pending_proofs:
            self.blockchain.add_transaction(Transaction(
                tx_type="yield_proof",
                sender="NETWORK",
                recipient=self.miner_address,
                amount=0,  # Proof transactions don't transfer coins
                metadata={
                    "session_id": proof.session_id,
                    "yield_amount": proof.yield_amount,
                    "captured_yield": proof.captured_yield,
                    "arbitrage_value": proof.arbitrage_value,
                    "micro_conversion_value": proof.micro_conversion_value,
                    "plays_executed": proof.plays_executed,
                },
            ))

        # Mine the block
        block = self.blockchain.mine_block(
            miner_address=self.miner_address,
            yield_proof=self.accumulated_yield,
        )

        if block:
            # Find the reward from the mining transaction
            reward = 0.0
            for tx in block.transactions:
                if tx.tx_type == "mine" and tx.recipient == self.miner_address:
                    reward = tx.amount
                    break

            # Update wallet stats
            self.wallet_manager.record_mining(
                self.miner_address,
                reward,
                self.accumulated_yield,
            )

            # Track mining history
            result = {
                "block_index": block.index,
                "block_hash": block.hash[:16],
                "reward": reward,
                "yield_proven": round(self.accumulated_yield, 2),
                "proofs_included": len(self.pending_proofs),
                "transactions": len(block.transactions),
                "timestamp": block.timestamp,
                "total_supply": round(self.blockchain.total_supply_mined, 8),
            }

            self.mining_history.append(result)
            self.total_blocks_mined += 1
            self.total_coins_earned += reward

            # Reset accumulators
            self.pending_proofs.clear()
            self.accumulated_yield = 0.0

            return result

        return None

    def get_mining_status(self) -> dict:
        """Get current mining status."""
        threshold = self.tokenomics.get_mining_threshold(
            self.blockchain.height
        )

        return {
            "miner_address": self.miner_address,
            "accumulated_yield": round(self.accumulated_yield, 2),
            "mining_threshold": round(threshold, 2),
            "progress_percent": round(
                min(100, self.accumulated_yield / threshold * 100), 1
            ) if threshold > 0 else 0,
            "pending_proofs": len(self.pending_proofs),
            "total_blocks_mined": self.total_blocks_mined,
            "total_coins_earned": round(self.total_coins_earned, 8),
            "current_block_reward": round(
                self.blockchain._calculate_reward(threshold), 8
            ),
            "chain_height": self.blockchain.height,
        }

    def get_earnings_summary(self) -> dict:
        """Get lifetime earnings summary."""
        wallet = self.wallet_manager.get_wallet(self.miner_address)

        return {
            "total_coins_earned": round(self.total_coins_earned, 8),
            "total_blocks_mined": self.total_blocks_mined,
            "total_yield_proven": round(
                wallet.total_yield_proven if wallet else 0, 2
            ),
            "coins_per_block_avg": round(
                self.total_coins_earned / self.total_blocks_mined, 8
            ) if self.total_blocks_mined > 0 else 0,
            "yield_per_block_avg": round(
                (wallet.total_yield_proven if wallet else 0)
                / self.total_blocks_mined, 2
            ) if self.total_blocks_mined > 0 else 0,
            "staking_tier": self.wallet_manager.get_staking_tier(
                self.miner_address
            ),
            "mining_history": self.mining_history[-10:],  # Last 10 blocks
        }
