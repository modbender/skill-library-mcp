"""
Pre-trade risk management: position limits, daily spend, circuit breaker.

Based on ProbablyProfit risk model from the article:
- max_position_size: per-trade limit
- max_total_exposure: % of balance in open positions
- max_drawdown_pct: circuit breaker — halts all trading
- max_consecutive_losses: circuit breaker trigger
- max_daily_spend: daily USDC limit
- min_balance: floor balance to keep
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Optional

from .strategy_base import Signal

logger = logging.getLogger("bot.risk")


@dataclass
class RiskConfig:
    max_position_size: float = 50.0
    max_total_exposure: float = 0.5
    stop_loss_pct: float = 0.20
    max_drawdown_pct: float = 0.30
    max_daily_spend: float = 50.0
    min_balance: float = 10.0
    max_consecutive_losses: int = 3
    max_open_positions: int = 5


@dataclass
class TradingState:
    balance: float = 0.0
    positions: list = field(default_factory=list)
    open_orders: list = field(default_factory=list)
    trading_ready: bool = False


class RiskManager:
    def __init__(self, config: RiskConfig):
        self.config = config
        self.daily_spent = 0.0
        self.daily_reset_date = _today()
        self.consecutive_losses = 0
        self.initial_balance: Optional[float] = None
        self.circuit_breaker_active = False

    def pre_check(self, state: TradingState) -> tuple:
        """
        Check if trading is allowed at all.
        Returns (allowed: bool, reason: str).
        """
        # Reset daily counter at midnight
        today = _today()
        if today != self.daily_reset_date:
            self.daily_spent = 0.0
            self.daily_reset_date = today
            logger.info("Daily spend counter reset")

        # Record initial balance for drawdown calc
        if self.initial_balance is None:
            self.initial_balance = state.balance
            logger.info(f"Initial balance recorded: ${self.initial_balance:.2f}")

        if not state.trading_ready:
            return False, "Trading not ready (wallet not set up)"

        if self.circuit_breaker_active:
            return False, f"Circuit breaker active ({self.consecutive_losses} consecutive losses)"

        if state.balance < self.config.min_balance:
            return False, f"Balance ${state.balance:.2f} below minimum ${self.config.min_balance:.2f}"

        # Max drawdown check
        if self.initial_balance > 0:
            drawdown = (self.initial_balance - state.balance) / self.initial_balance
            if drawdown >= self.config.max_drawdown_pct:
                self.circuit_breaker_active = True
                return False, f"Max drawdown {drawdown:.1%} >= {self.config.max_drawdown_pct:.1%} — CIRCUIT BREAKER"

        if self.daily_spent >= self.config.max_daily_spend:
            return False, f"Daily spend ${self.daily_spent:.2f} >= limit ${self.config.max_daily_spend:.2f}"

        # Max total exposure
        total_exposure = sum(
            float(p.get("size", 0)) * float(p.get("avgPrice", 0))
            for p in state.positions
        )
        if state.balance > 0 and total_exposure / state.balance > self.config.max_total_exposure:
            return False, f"Total exposure {total_exposure / state.balance:.1%} > {self.config.max_total_exposure:.1%}"

        if len(state.positions) >= self.config.max_open_positions:
            return False, f"Max open positions ({self.config.max_open_positions}) reached"

        return True, "OK"

    def validate_signal(self, signal: Signal, state: TradingState) -> tuple:
        """
        Validate a specific trade signal.
        Returns (allowed: bool, reason: str).
        """
        if signal.amount > self.config.max_position_size:
            return False, f"Amount ${signal.amount:.2f} > max position ${self.config.max_position_size:.2f}"

        if self.daily_spent + signal.amount > self.config.max_daily_spend:
            return False, f"Would exceed daily limit: ${self.daily_spent:.2f} + ${signal.amount:.2f} > ${self.config.max_daily_spend:.2f}"

        if signal.amount > state.balance:
            return False, f"Amount ${signal.amount:.2f} > balance ${state.balance:.2f}"

        if signal.order_type == "LIMIT" and signal.price is None:
            return False, "LIMIT order requires price"

        if signal.price is not None and (signal.price < 0.01 or signal.price > 0.99):
            return False, f"Price {signal.price} outside valid range (0.01-0.99)"

        return True, "OK"

    def record_order(self, signal: Signal):
        """Record a placed order for daily tracking."""
        self.daily_spent += signal.amount
        logger.info(f"Daily spend: ${self.daily_spent:.2f} / ${self.config.max_daily_spend:.2f}")

    def record_loss(self):
        """Record a losing trade. Triggers circuit breaker after N consecutive."""
        self.consecutive_losses += 1
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            self.circuit_breaker_active = True
            logger.warning(
                f"CIRCUIT BREAKER: {self.consecutive_losses} consecutive losses"
            )

    def record_win(self):
        """Record a winning trade. Resets consecutive loss counter."""
        self.consecutive_losses = 0

    def reset_circuit_breaker(self):
        """Manual reset of circuit breaker."""
        self.circuit_breaker_active = False
        self.consecutive_losses = 0
        logger.info("Circuit breaker reset manually")


def _today() -> str:
    return time.strftime("%Y-%m-%d")
