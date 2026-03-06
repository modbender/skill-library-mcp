"""
Core data types for Agent Financial Observability.

These types are protocol-agnostic — they work whether the agent is paying
via x402/USDC, Stripe/ACP, Visa TAP, or any future rail.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PaymentRail(str, Enum):
    """Known payment rails in the agent commerce ecosystem."""
    X402_USDC = "x402_usdc"
    STRIPE_ACP = "stripe_acp"
    VISA_TAP = "visa_tap"
    MC_AGENT_PAY = "mc_agent_pay"
    CIRCLE_NANO = "circle_nano"
    POLYMARKET_CLOB = "polymarket_clob"
    INTERNAL = "internal"          # intra-org transfers
    UNKNOWN = "unknown"


class TxStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AgentTx:
    """
    A single financial transaction initiated by an agent.

    This is the atomic unit of observability — every time an agent
    spends or receives money, one AgentTx is created.
    """
    # Identity
    tx_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    agent_id: str = ""
    task_id: str = ""              # which task triggered this spend

    # Money
    amount: float = 0.0            # in base currency (USD)
    currency: str = "USD"
    rail: PaymentRail = PaymentRail.UNKNOWN

    # Context
    counterparty: str = ""         # who received the payment
    description: str = ""
    tags: dict[str, str] = field(default_factory=dict)

    # Outcome (filled after task completion)
    revenue: float = 0.0           # what the task earned back
    status: TxStatus = TxStatus.PENDING

    # Timestamps
    created_at: float = field(default_factory=time.time)
    settled_at: float | None = None

    @property
    def pnl(self) -> float:
        return self.revenue - self.amount

    @property
    def roi(self) -> float | None:
        if self.amount == 0:
            return None
        return self.pnl / self.amount

    def settle(self, revenue: float, status: TxStatus = TxStatus.CONFIRMED):
        self.revenue = revenue
        self.status = status
        self.settled_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "amount": self.amount,
            "currency": self.currency,
            "rail": self.rail.value,
            "counterparty": self.counterparty,
            "description": self.description,
            "tags": self.tags,
            "revenue": self.revenue,
            "pnl": self.pnl,
            "roi": self.roi,
            "status": self.status.value,
            "created_at": self.created_at,
            "settled_at": self.settled_at,
        }


@dataclass
class BudgetRule:
    """A spending limit that triggers alerts or halts."""
    name: str
    max_amount: float
    window_seconds: float          # 0 = lifetime
    severity: AlertSeverity = AlertSeverity.WARNING
    halt_on_breach: bool = False   # hard-stop the agent?


@dataclass
class Alert:
    """An observability alert."""
    alert_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    severity: AlertSeverity = AlertSeverity.INFO
    rule_name: str = ""
    message: str = ""
    agent_id: str = ""
    timestamp: float = field(default_factory=time.time)
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "severity": self.severity.value,
            "rule_name": self.rule_name,
            "message": self.message,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "context": self.context,
        }
