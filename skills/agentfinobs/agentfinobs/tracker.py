"""
SpendTracker — the core recording engine.

Every agent payment flows through here. The tracker stores transactions
in-memory with periodic persistence to disk, and notifies listeners
(BudgetManager, AnomalyDetector, etc.) on each new tx.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Callable, TYPE_CHECKING

from .types import AgentTx, TxStatus

if TYPE_CHECKING:
    from .exporters import BaseExporter

logger = logging.getLogger("agentfinobs.tracker")

# Type alias for listeners that react to new transactions
TxListener = Callable[[AgentTx], None]


class SpendTracker:
    """
    Thread-safe transaction recorder.

    Usage::

        tracker = SpendTracker(agent_id="arb-bot-01")
        tx = tracker.record(amount=12.50, task_id="trade-42",
                            description="Buy YES tokens")
        # ... later, when outcome is known ...
        tracker.settle(tx.tx_id, revenue=13.00)

    With exporters::

        from agentfinobs.exporters import JsonlExporter, WebhookExporter

        tracker = SpendTracker(
            agent_id="my-agent",
            exporters=[
                JsonlExporter("data/txs.jsonl"),
                WebhookExporter("https://my-saas.com/ingest"),
            ],
        )
    """

    def __init__(
        self,
        agent_id: str = "default",
        persist_dir: str | Path | None = None,
        max_history: int = 10_000,
        exporters: list["BaseExporter"] | None = None,
    ):
        self.agent_id = agent_id
        self._txs: dict[str, AgentTx] = {}  # tx_id -> AgentTx
        self._ordered_ids: list[str] = []    # insertion order
        self._lock = threading.Lock()
        self._listeners: list[TxListener] = []
        self._exporters: list["BaseExporter"] = list(exporters or [])
        self._max_history = max_history

        self._persist_path: Path | None = None
        if persist_dir:
            p = Path(persist_dir)
            p.mkdir(parents=True, exist_ok=True)
            self._persist_path = p / f"txs_{agent_id}.jsonl"

    # ── Recording ──────────────────────────────────────────────────────

    def record(self, **kwargs) -> AgentTx:
        """
        Record a new transaction. Accepts any AgentTx field as kwarg.
        Returns the created AgentTx.
        """
        kwargs.setdefault("agent_id", self.agent_id)
        tx = AgentTx(**kwargs)

        with self._lock:
            self._txs[tx.tx_id] = tx
            self._ordered_ids.append(tx.tx_id)
            self._trim()

        if self._persist_path:
            self._append_to_disk(tx)

        self._export(tx)

        # Notify listeners (budget checks, anomaly detection, etc.)
        for listener in self._listeners:
            try:
                listener(tx)
            except Exception as e:
                logger.warning(f"Listener error: {e}")

        logger.debug(
            f"[TX] {tx.tx_id} agent={tx.agent_id} "
            f"amount=${tx.amount:.4f} task={tx.task_id}"
        )
        return tx

    def settle(
        self,
        tx_id: str,
        revenue: float,
        status: TxStatus = TxStatus.CONFIRMED,
    ) -> AgentTx | None:
        """Mark a transaction as settled with its outcome."""
        with self._lock:
            tx = self._txs.get(tx_id)
            if tx is None:
                logger.warning(f"settle: tx_id {tx_id} not found")
                return None
            tx.settle(revenue, status)

        if self._persist_path:
            self._append_to_disk(tx)

        self._export(tx)

        logger.debug(
            f"[SETTLE] {tx.tx_id} revenue=${revenue:.4f} "
            f"pnl=${tx.pnl:+.4f} status={status.value}"
        )
        return tx

    # ── Queries ────────────────────────────────────────────────────────

    def get(self, tx_id: str) -> AgentTx | None:
        with self._lock:
            return self._txs.get(tx_id)

    def recent(self, n: int = 50) -> list[AgentTx]:
        """Return the N most recent transactions."""
        with self._lock:
            ids = self._ordered_ids[-n:]
            return [self._txs[tid] for tid in ids if tid in self._txs]

    def query(
        self,
        since: float | None = None,
        task_id: str | None = None,
        agent_id: str | None = None,
        status: TxStatus | None = None,
    ) -> list[AgentTx]:
        """Filter transactions by criteria."""
        with self._lock:
            txs = list(self._txs.values())

        if since is not None:
            txs = [t for t in txs if t.created_at >= since]
        if task_id is not None:
            txs = [t for t in txs if t.task_id == task_id]
        if agent_id is not None:
            txs = [t for t in txs if t.agent_id == agent_id]
        if status is not None:
            txs = [t for t in txs if t.status == status]
        return txs

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._txs)

    # ── Listeners & Exporters ─────────────────────────────────────────

    def add_listener(self, fn: TxListener):
        self._listeners.append(fn)

    def add_exporter(self, exporter: "BaseExporter"):
        self._exporters.append(exporter)

    def _export(self, tx: AgentTx):
        """Push tx to all registered exporters."""
        for exp in self._exporters:
            try:
                exp.export_tx(tx)
            except Exception as e:
                logger.warning(f"Exporter {exp.__class__.__name__} error: {e}")

    # ── Persistence ────────────────────────────────────────────────────

    def _append_to_disk(self, tx: AgentTx):
        try:
            with open(self._persist_path, "a") as f:
                f.write(json.dumps(tx.to_dict()) + "\n")
        except Exception as e:
            logger.warning(f"Persist failed: {e}")

    def load_from_disk(self) -> int:
        """Load historical transactions from the JSONL file. Returns count loaded."""
        if not self._persist_path or not self._persist_path.exists():
            return 0
        count = 0
        with open(self._persist_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    tx = AgentTx(
                        tx_id=d["tx_id"],
                        agent_id=d.get("agent_id", ""),
                        task_id=d.get("task_id", ""),
                        amount=d.get("amount", 0),
                        currency=d.get("currency", "USD"),
                        counterparty=d.get("counterparty", ""),
                        description=d.get("description", ""),
                        tags=d.get("tags", {}),
                        revenue=d.get("revenue", 0),
                        status=TxStatus(d.get("status", "pending")),
                        created_at=d.get("created_at", 0),
                        settled_at=d.get("settled_at"),
                    )
                    with self._lock:
                        self._txs[tx.tx_id] = tx
                        self._ordered_ids.append(tx.tx_id)
                    count += 1
                except Exception:
                    continue
        self._trim()
        logger.info(f"Loaded {count} historical transactions")
        return count

    # ── Internal ───────────────────────────────────────────────────────

    def _trim(self):
        """Keep only max_history most recent txs."""
        while len(self._ordered_ids) > self._max_history:
            old_id = self._ordered_ids.pop(0)
            self._txs.pop(old_id, None)
