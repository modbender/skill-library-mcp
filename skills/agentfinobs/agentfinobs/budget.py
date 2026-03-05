"""
BudgetManager — spending limits and alerts.

Enforces BudgetRules (e.g. "$100/hour", "$500/day") by listening to
the SpendTracker's transaction stream. When a rule is breached, it
fires alerts and optionally halts the agent.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from .types import AgentTx, Alert, AlertSeverity, BudgetRule

logger = logging.getLogger("agentfinobs.budget")

AlertCallback = Callable[[Alert], None]


class BudgetManager:
    """
    Real-time budget enforcement.

    Usage::

        budget = BudgetManager()
        budget.add_rule(BudgetRule(
            name="hourly_cap",
            max_amount=100.0,
            window_seconds=3600,
            severity=AlertSeverity.WARNING,
        ))
        budget.add_rule(BudgetRule(
            name="daily_hard_limit",
            max_amount=500.0,
            window_seconds=86400,
            halt_on_breach=True,
            severity=AlertSeverity.CRITICAL,
        ))

        # Wire it up
        tracker.add_listener(budget.on_tx)
    """

    def __init__(self):
        self._rules: list[BudgetRule] = []
        self._alert_callbacks: list[AlertCallback] = []
        self._tx_history: list[AgentTx] = []
        self._halted: bool = False
        self._halt_reason: str = ""
        self._alerts: list[Alert] = []

    @property
    def is_halted(self) -> bool:
        return self._halted

    @property
    def halt_reason(self) -> str:
        return self._halt_reason

    def add_rule(self, rule: BudgetRule):
        self._rules.append(rule)
        logger.info(
            f"Budget rule added: {rule.name} "
            f"max=${rule.max_amount:.2f} window={rule.window_seconds}s"
        )

    def add_alert_callback(self, fn: AlertCallback):
        self._alert_callbacks.append(fn)

    def on_tx(self, tx: AgentTx):
        """Called by SpendTracker on each new transaction. Checks all rules."""
        self._tx_history.append(tx)
        now = time.time()

        for rule in self._rules:
            spent = self._window_spend(rule.window_seconds, now)
            if spent > rule.max_amount:
                self._fire_alert(rule, spent, tx)

    def check_can_spend(self, amount: float) -> tuple[bool, str]:
        """Pre-check: would spending `amount` breach any rule?"""
        if self._halted:
            return False, f"Agent halted: {self._halt_reason}"

        now = time.time()
        for rule in self._rules:
            current = self._window_spend(rule.window_seconds, now)
            if current + amount > rule.max_amount:
                headroom = max(0, rule.max_amount - current)
                return False, (
                    f"Would breach '{rule.name}': "
                    f"current ${current:.2f} + ${amount:.2f} "
                    f"> limit ${rule.max_amount:.2f} "
                    f"(headroom: ${headroom:.2f})"
                )
        return True, "OK"

    def headroom(self) -> dict[str, float]:
        """Return remaining budget per rule."""
        now = time.time()
        result = {}
        for rule in self._rules:
            spent = self._window_spend(rule.window_seconds, now)
            result[rule.name] = max(0, rule.max_amount - spent)
        return result

    def get_alerts(self, last_n: int = 20) -> list[Alert]:
        return self._alerts[-last_n:]

    def reset_halt(self):
        """Manually clear the halt state."""
        self._halted = False
        self._halt_reason = ""
        logger.info("Budget halt cleared manually")

    # ── Internal ───────────────────────────────────────────────────────

    def _window_spend(self, window_seconds: float, now: float) -> float:
        """Total spend within a time window. 0 = all time."""
        if window_seconds <= 0:
            return sum(tx.amount for tx in self._tx_history)
        cutoff = now - window_seconds
        return sum(
            tx.amount for tx in self._tx_history
            if tx.created_at >= cutoff
        )

    def _fire_alert(self, rule: BudgetRule, spent: float, trigger_tx: AgentTx):
        alert = Alert(
            severity=rule.severity,
            rule_name=rule.name,
            message=(
                f"Budget rule '{rule.name}' breached: "
                f"${spent:.2f} > ${rule.max_amount:.2f}"
            ),
            agent_id=trigger_tx.agent_id,
            context={
                "spent": spent,
                "limit": rule.max_amount,
                "trigger_tx_id": trigger_tx.tx_id,
                "trigger_amount": trigger_tx.amount,
            },
        )
        self._alerts.append(alert)

        if rule.halt_on_breach:
            self._halted = True
            self._halt_reason = alert.message
            logger.critical(f"[HALT] {alert.message}")
        else:
            logger.warning(f"[ALERT] {alert.message}")

        for cb in self._alert_callbacks:
            try:
                cb(alert)
            except Exception as e:
                logger.warning(f"Alert callback error: {e}")
