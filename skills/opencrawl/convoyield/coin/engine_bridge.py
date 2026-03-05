"""
ConvoCoin Engine Bridge — Connects ConvoYield to the blockchain.

This is the integration layer that automatically mines ConvoCoin
whenever the ConvoYield engine captures yield. Just plug it in
and your bot starts mining.

Usage:
    from convoyield import ConvoYield
    from convoyield.coin.engine_bridge import CoinBridge

    engine = ConvoYield(base_conversation_value=50.0)
    bridge = CoinBridge()  # Auto-creates wallet if needed
    bridge.attach(engine)

    # Now every process_user_message() automatically mines CVC
    result = engine.process_user_message("I need help choosing a plan")
    print(bridge.status())  # See your mining progress
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional

from convoyield.coin.blockchain import Blockchain
from convoyield.coin.wallet import WalletManager, Wallet
from convoyield.coin.miner import ProofOfYieldMiner, YieldProof
from convoyield.coin.tokenomics import Tokenomics
from convoyield.coin.marketplace import Marketplace
from convoyield.coin.ledger import Ledger
from convoyield.models.yield_result import YieldResult


class CoinBridge:
    """
    Bridge between ConvoYield engine and ConvoCoin blockchain.

    Handles automatic mining, wallet management, and marketplace
    access — all from a single integration point.
    """

    def __init__(
        self,
        ledger_path: str | Path | None = None,
        auto_mine: bool = True,
    ):
        # Initialize or load blockchain
        self.ledger = Ledger(ledger_path)
        existing = self.ledger.load()

        if existing:
            self.blockchain = existing
        else:
            self.blockchain = Blockchain()

        self.wallet_manager = WalletManager()
        self.tokenomics = Tokenomics()
        self.marketplace = Marketplace(
            self.blockchain, self.wallet_manager, self.tokenomics
        )
        self.miner = ProofOfYieldMiner(
            self.blockchain, self.wallet_manager, self.tokenomics
        )

        self.auto_mine = auto_mine
        self.wallet: Optional[Wallet] = None
        self.secret_key: Optional[str] = None
        self._session_id = str(uuid.uuid4())[:8]
        self._attached_engine = None
        self._original_process = None
        self._mining_events: list[dict] = []

    def create_wallet(self, label: str = "default") -> tuple[str, str]:
        """
        Create a new ConvoCoin wallet.

        Returns:
            (address, secret_key) — Save the secret key!
        """
        self.wallet, self.secret_key = self.wallet_manager.create_wallet(label)
        self.miner.set_miner_address(self.wallet.address)
        return self.wallet.address, self.secret_key

    def import_wallet(self, secret_key: str, label: str = "") -> str:
        """Import an existing wallet from a secret key."""
        self.secret_key = secret_key
        self.wallet = self.wallet_manager.import_wallet(secret_key, label)
        self.miner.set_miner_address(self.wallet.address)
        return self.wallet.address

    def attach(self, engine) -> None:
        """
        Attach to a ConvoYield engine for automatic mining.

        This wraps the engine's process_user_message method to
        automatically submit yield proofs after each turn.
        """
        if not self.wallet:
            self.create_wallet("auto")

        self._attached_engine = engine
        self._original_process = engine.process_user_message

        def mining_wrapper(text: str, *args, **kwargs) -> YieldResult:
            result = self._original_process(text, *args, **kwargs)
            self._on_yield_captured(result)
            return result

        engine.process_user_message = mining_wrapper

    def detach(self) -> None:
        """Detach from the engine and restore original behavior."""
        if self._attached_engine and self._original_process:
            self._attached_engine.process_user_message = self._original_process
            self._attached_engine = None
            self._original_process = None

    def _on_yield_captured(self, result: YieldResult) -> None:
        """Called after each yield analysis — submits proof and maybe mines."""
        if not self.auto_mine:
            return

        # Build yield proof from the result
        proof = YieldProof(
            session_id=self._session_id,
            yield_amount=result.estimated_yield,
            captured_yield=result.yield_captured_so_far,
            arbitrage_value=sum(
                a.estimated_value for a in result.arbitrage_opportunities
            ),
            micro_conversion_value=sum(
                m.value for m in result.micro_conversions
            ),
            plays_executed=1 if result.recommended_play else 0,
        )

        # Submit to miner
        mining_result = self.miner.submit_yield_proof(proof)

        if mining_result:
            self._mining_events.append(mining_result)
            # Auto-save after mining
            self.save()

    def manual_mine(self) -> dict | None:
        """Manually trigger mining with accumulated yield."""
        result = self.miner.force_mine()
        if result:
            self._mining_events.append(result)
            self.save()
        return result

    def save(self) -> str:
        """Save blockchain state to disk."""
        return self.ledger.save(self.blockchain)

    def status(self) -> dict:
        """Get complete ConvoCoin status."""
        mining_status = self.miner.get_mining_status()
        chain_stats = self.blockchain.get_stats()

        wallet_balance = 0.0
        staking_tier = "none"
        if self.wallet:
            wallet_balance = self.blockchain.get_balance(self.wallet.address)
            staking_tier = self.wallet_manager.get_staking_tier(
                self.wallet.address
            )

        return {
            "wallet": {
                "address": self.wallet.address if self.wallet else None,
                "balance_cvc": round(wallet_balance, 8),
                "staking_tier": staking_tier,
                "staked_amount": round(
                    self.wallet.staked_amount if self.wallet else 0, 8
                ),
            },
            "mining": mining_status,
            "blockchain": chain_stats,
            "marketplace": self.marketplace.get_marketplace_stats(),
            "economics": self.tokenomics.get_economics_summary(
                chain_stats["chain_height"],
                chain_stats["total_supply_mined"],
                self.wallet.staked_amount if self.wallet else 0,
            ),
        }

    def stake(self, amount: float) -> bool:
        """Stake CVC for premium features."""
        if not self.wallet:
            return False

        balance = self.blockchain.get_balance(self.wallet.address)
        if balance < amount:
            return False

        from convoyield.coin.blockchain import Transaction
        self.blockchain.add_transaction(Transaction(
            tx_type="stake",
            sender=self.wallet.address,
            recipient="STAKING_POOL",
            amount=amount,
            metadata={"action": "stake"},
        ))

        self.wallet_manager.stake(self.wallet.address, amount)
        return True

    def unstake(self, amount: float) -> bool:
        """Unstake CVC."""
        if not self.wallet:
            return False

        from convoyield.coin.blockchain import Transaction
        self.blockchain.add_transaction(Transaction(
            tx_type="unstake",
            sender="STAKING_POOL",
            recipient=self.wallet.address,
            amount=amount,
            metadata={"action": "unstake"},
        ))

        return self.wallet_manager.unstake(self.wallet.address, amount)

    def buy_playbook(self, listing_id: str) -> dict | None:
        """Buy a playbook from the marketplace."""
        if not self.wallet:
            return None
        return self.marketplace.purchase(self.wallet.address, listing_id)

    def list_marketplace(self) -> list[dict]:
        """List marketplace items."""
        return self.marketplace.get_listings()

    def transfer(self, to_address: str, amount: float) -> bool:
        """Transfer CVC to another wallet."""
        if not self.wallet:
            return False

        balance = self.blockchain.get_balance(self.wallet.address)
        if balance < amount:
            return False

        from convoyield.coin.blockchain import Transaction
        self.blockchain.add_transaction(Transaction(
            tx_type="transfer",
            sender=self.wallet.address,
            recipient=to_address,
            amount=amount,
        ))

        return True

    def get_recent_mining(self, limit: int = 10) -> list[dict]:
        """Get recent mining events."""
        return self._mining_events[-limit:]
