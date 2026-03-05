"""
UTXO Model — Unspent Transaction Output tracking, like Bitcoin.

Bitcoin doesn't track "balances." It tracks unspent outputs.
When you "have 5 BTC," what you actually have is a set of
unspent outputs from previous transactions that sum to 5 BTC.

To spend, you consume one or more UTXOs as inputs, and create
new UTXOs as outputs. The difference is the transaction fee.

This is more secure than an account model because:
- No double-spending possible (UTXOs are consumed atomically)
- Parallel transaction processing (independent UTXO sets)
- Privacy (new addresses for change outputs)

Example:
    Alice has UTXO worth 10 CVC
    Alice wants to send 3 CVC to Bob
    Transaction:
        Input:  Alice's 10 CVC UTXO (consumed/destroyed)
        Output 1: 3 CVC to Bob (new UTXO)
        Output 2: 6.99 CVC back to Alice (change UTXO)
        Fee: 0.01 CVC (goes to miner)
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class TransactionOutput:
    """
    An unspent transaction output (UTXO).

    This represents a "coin" on the blockchain — a specific amount
    of CVC locked to a specific address, created by a specific
    transaction.
    """

    tx_hash: str       # Hash of the transaction that created this output
    output_index: int  # Index within that transaction's outputs
    amount: float      # CVC amount
    recipient: str     # Address that can spend this output
    timestamp: float = field(default_factory=time.time)

    @property
    def utxo_id(self) -> str:
        """Unique identifier for this UTXO: tx_hash:output_index."""
        return f"{self.tx_hash}:{self.output_index}"

    def to_dict(self) -> dict:
        return {
            "utxo_id": self.utxo_id,
            "tx_hash": self.tx_hash,
            "output_index": self.output_index,
            "amount": self.amount,
            "recipient": self.recipient,
            "timestamp": self.timestamp,
        }


@dataclass
class TransactionInput:
    """
    A reference to a UTXO being spent.

    To spend a UTXO, you reference it by tx_hash:output_index
    and provide a signature proving you own the address.
    """

    tx_hash: str       # Hash of the transaction containing the UTXO
    output_index: int  # Which output in that transaction
    signature: str     # Proof that the spender owns the UTXO

    @property
    def utxo_id(self) -> str:
        return f"{self.tx_hash}:{self.output_index}"

    def to_dict(self) -> dict:
        return {
            "tx_hash": self.tx_hash,
            "output_index": self.output_index,
            "signature": self.signature,
        }


@dataclass
class UTXOTransaction:
    """
    A UTXO-based transaction.

    Inputs consume existing UTXOs.
    Outputs create new UTXOs.
    The difference (input_sum - output_sum) is the miner fee.
    """

    tx_hash: str
    inputs: list[TransactionInput]
    outputs: list[TransactionOutput]
    timestamp: float = field(default_factory=time.time)
    tx_type: str = "transfer"  # transfer, coinbase, yield_proof

    @property
    def fee(self) -> float:
        """Transaction fee = total inputs - total outputs."""
        # Coinbase transactions have no inputs
        if self.tx_type == "coinbase":
            return 0.0
        input_total = sum(
            self._resolved_inputs.get(inp.utxo_id, 0)
            for inp in self.inputs
        )
        output_total = sum(out.amount for out in self.outputs)
        return max(0, input_total - output_total)

    def __post_init__(self):
        self._resolved_inputs: dict[str, float] = {}

    def resolve_inputs(self, utxo_set: "UTXOSet"):
        """Resolve input amounts from the UTXO set."""
        for inp in self.inputs:
            utxo = utxo_set.get(inp.utxo_id)
            if utxo:
                self._resolved_inputs[inp.utxo_id] = utxo.amount

    def to_dict(self) -> dict:
        return {
            "tx_hash": self.tx_hash,
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "timestamp": self.timestamp,
            "tx_type": self.tx_type,
        }


class UTXOSet:
    """
    The UTXO set — the complete state of who owns what.

    This is the Bitcoin equivalent of a "database of all balances."
    But instead of mapping address -> balance, it maps
    utxo_id -> TransactionOutput.

    At any point in time, the UTXO set represents ALL spendable
    coins in the system.
    """

    def __init__(self):
        self._utxos: dict[str, TransactionOutput] = {}
        self._spent: set[str] = set()  # Track spent UTXOs for validation

    def add(self, utxo: TransactionOutput):
        """Add a new UTXO to the set (created by a transaction output)."""
        self._utxos[utxo.utxo_id] = utxo

    def spend(self, utxo_id: str) -> TransactionOutput | None:
        """
        Spend (consume) a UTXO.

        Returns the spent UTXO, or None if it doesn't exist.
        Once spent, the UTXO is removed from the set permanently.
        """
        utxo = self._utxos.pop(utxo_id, None)
        if utxo:
            self._spent.add(utxo_id)
        return utxo

    def get(self, utxo_id: str) -> TransactionOutput | None:
        """Look up a UTXO by its ID."""
        return self._utxos.get(utxo_id)

    def is_spent(self, utxo_id: str) -> bool:
        """Check if a UTXO has been spent."""
        return utxo_id in self._spent

    def get_balance(self, address: str) -> float:
        """
        Get the balance of an address by summing its UTXOs.

        Unlike an account model, this requires scanning all UTXOs.
        In Bitcoin, this is why balance queries are expensive.
        """
        return sum(
            utxo.amount
            for utxo in self._utxos.values()
            if utxo.recipient == address
        )

    def get_utxos_for_address(self, address: str) -> list[TransactionOutput]:
        """Get all unspent outputs belonging to an address."""
        return [
            utxo for utxo in self._utxos.values()
            if utxo.recipient == address
        ]

    def select_utxos(
        self,
        address: str,
        target_amount: float,
    ) -> tuple[list[TransactionOutput], float]:
        """
        Coin selection — choose UTXOs to cover a target amount.

        Uses a simple largest-first strategy. Bitcoin Core uses
        more sophisticated algorithms (Branch and Bound, etc.)
        to minimize change outputs.

        Returns:
            (selected_utxos, total_selected)
        """
        available = sorted(
            self.get_utxos_for_address(address),
            key=lambda u: u.amount,
            reverse=True,
        )

        selected = []
        total = 0.0

        for utxo in available:
            selected.append(utxo)
            total += utxo.amount
            if total >= target_amount:
                break

        return selected, total

    def apply_transaction(self, tx: UTXOTransaction) -> bool:
        """
        Apply a transaction to the UTXO set.

        1. Verify all inputs reference valid, unspent UTXOs
        2. Remove input UTXOs (spend them)
        3. Add output UTXOs (create new ones)

        Returns True if successful.
        """
        # Coinbase transactions have no inputs to validate
        if tx.tx_type != "coinbase":
            # Verify all inputs exist and are unspent
            for inp in tx.inputs:
                if inp.utxo_id not in self._utxos:
                    return False  # Input doesn't exist or already spent

            # Verify input sum >= output sum
            input_sum = sum(
                self._utxos[inp.utxo_id].amount
                for inp in tx.inputs
            )
            output_sum = sum(out.amount for out in tx.outputs)

            if input_sum < output_sum:
                return False  # Trying to spend more than available

            # Spend inputs
            for inp in tx.inputs:
                self.spend(inp.utxo_id)

        # Create outputs
        for output in tx.outputs:
            self.add(output)

        return True

    @property
    def size(self) -> int:
        """Number of unspent outputs in the set."""
        return len(self._utxos)

    @property
    def total_value(self) -> float:
        """Total value of all unspent outputs."""
        return sum(u.amount for u in self._utxos.values())

    def get_stats(self) -> dict:
        """Get UTXO set statistics."""
        addresses = set(u.recipient for u in self._utxos.values())
        return {
            "total_utxos": self.size,
            "total_value": round(self.total_value, 8),
            "total_spent": len(self._spent),
            "unique_addresses": len(addresses),
        }

    def to_dict(self) -> dict:
        return {
            "utxos": {k: v.to_dict() for k, v in self._utxos.items()},
            "stats": self.get_stats(),
        }


def create_coinbase_tx(
    miner_address: str,
    reward: float,
    block_height: int,
    fees: float = 0.0,
) -> UTXOTransaction:
    """
    Create a coinbase transaction — the miner's reward.

    In Bitcoin, the first transaction of every block is a coinbase
    that creates new coins from nothing. It has no inputs.

    The reward = block_reward + sum(transaction_fees_in_block).
    """
    tx_data = f"coinbase:{block_height}:{miner_address}:{reward + fees}:{time.time()}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()

    output = TransactionOutput(
        tx_hash=tx_hash,
        output_index=0,
        amount=reward + fees,
        recipient=miner_address,
    )

    return UTXOTransaction(
        tx_hash=tx_hash,
        inputs=[],
        outputs=[output],
        tx_type="coinbase",
    )


def create_transfer_tx(
    sender_address: str,
    recipient_address: str,
    amount: float,
    utxo_set: UTXOSet,
    fee: float = 0.01,
    signature: str = "",
) -> UTXOTransaction | None:
    """
    Create a transfer transaction using the UTXO model.

    1. Select UTXOs from sender to cover amount + fee
    2. Create output for recipient
    3. Create change output back to sender (if any)
    """
    total_needed = amount + fee
    selected, total_selected = utxo_set.select_utxos(
        sender_address, total_needed
    )

    if total_selected < total_needed:
        return None  # Insufficient funds

    # Create inputs from selected UTXOs
    inputs = [
        TransactionInput(
            tx_hash=utxo.tx_hash,
            output_index=utxo.output_index,
            signature=signature or "unsigned",
        )
        for utxo in selected
    ]

    # Create transaction hash
    tx_data = (
        f"transfer:{sender_address}:{recipient_address}:"
        f"{amount}:{fee}:{time.time()}"
    )
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()

    # Create outputs
    outputs = [
        TransactionOutput(
            tx_hash=tx_hash,
            output_index=0,
            amount=amount,
            recipient=recipient_address,
        )
    ]

    # Change output (send remainder back to sender)
    change = total_selected - total_needed
    if change > 0.00000001:  # Dust threshold
        outputs.append(TransactionOutput(
            tx_hash=tx_hash,
            output_index=1,
            amount=round(change, 8),
            recipient=sender_address,
        ))

    return UTXOTransaction(
        tx_hash=tx_hash,
        inputs=inputs,
        outputs=outputs,
        tx_type="transfer",
    )
