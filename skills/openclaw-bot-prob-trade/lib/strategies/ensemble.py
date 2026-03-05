"""
#6 Multi-Agent Ensemble (Swarm) — Byzantine consensus voting.

From the article: "Оркестрация 7 агентов с византийским консенсусом
(требуется кворум 5/7 для входа в сделку)."

Logic:
1. Run multiple sub-strategies independently
2. Each sub-strategy votes on each market
3. Only trade when quorum is reached (e.g. 3/5 or 5/7 agree)
4. Protects against LLM hallucinations and single-strategy failures

This meta-strategy combines other strategies already in this repo.
Configure which sub-strategies to use and the quorum threshold.

Parameters (config.strategy_params):
    sub_strategies:   momentum,trend_breakout,value_investor
    quorum:           0.6    Fraction of strategies that must agree (3/5 = 0.6)
    order_size:       5      USDC per order (overrides sub-strategy sizes)

Ref: https://www.npmjs.com/package/neural-trader
"""

import logging
from typing import List, Dict

from ..strategy_base import Strategy, Signal
from . import get_strategy

logger = logging.getLogger("bot.ensemble")


class EnsembleStrategy(Strategy):
    name = "ensemble"

    def initialize(self, config: dict) -> None:
        names_str = config.get("sub_strategies", "momentum,trend_breakout,value_investor")
        self.strategy_names = [n.strip() for n in names_str.split(",") if n.strip()]
        self.quorum = config.get("quorum", 0.6)
        self.order_size = config.get("order_size", 5)

        # Initialize sub-strategies
        self.sub_strategies: List[Strategy] = []
        for name in self.strategy_names:
            if name == "ensemble":  # prevent recursion
                continue
            try:
                s = get_strategy(name)
                s.initialize(config)
                self.sub_strategies.append(s)
                logger.info(f"Ensemble member: {name}")
            except ValueError as e:
                logger.warning(f"Could not load sub-strategy '{name}': {e}")

        if not self.sub_strategies:
            logger.warning("No sub-strategies loaded for ensemble")

        logger.info(
            f"Ensemble: {len(self.sub_strategies)} strategies, "
            f"quorum={self.quorum:.0%}"
        )

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        if not self.sub_strategies:
            return []

        # Collect votes from each sub-strategy
        # Key: (market, side, outcome) → list of signals
        votes: Dict[tuple, List[Signal]] = {}

        for strategy in self.sub_strategies:
            try:
                signals = strategy.scan(markets, positions, balance)
                for sig in signals:
                    key = (sig.market, sig.side, sig.outcome)
                    if key not in votes:
                        votes[key] = []
                    votes[key].append(sig)
            except Exception as e:
                logger.warning(f"Sub-strategy {strategy.name} failed: {e}")

        # Apply quorum filter
        min_votes = max(1, int(len(self.sub_strategies) * self.quorum))
        consensus_signals = []

        for key, sigs in votes.items():
            if len(sigs) >= min_votes:
                # Aggregate: average confidence, best price, combined reasons
                avg_confidence = sum(s.confidence for s in sigs) / len(sigs)

                # Use the best (lowest for BUY) price
                prices = [s.price for s in sigs if s.price is not None]
                best_price = min(prices) if prices else None

                # Combine reasons
                voters = [s.reason.split(":")[0] if ":" in s.reason else s.reason[:20] for s in sigs]
                reason = f"Consensus {len(sigs)}/{len(self.sub_strategies)}: {', '.join(voters)}"

                market, side, outcome = key
                consensus_signals.append(Signal(
                    market=market,
                    side=side,
                    outcome=outcome,
                    order_type="LIMIT" if best_price else "MARKET",
                    amount=self.order_size,
                    price=best_price,
                    confidence=avg_confidence,
                    reason=reason,
                ))

        consensus_signals.sort(key=lambda s: s.confidence, reverse=True)

        if consensus_signals:
            logger.info(
                f"Ensemble: {len(votes)} total votes, "
                f"{len(consensus_signals)} passed quorum ({min_votes}/{len(self.sub_strategies)})"
            )

        return consensus_signals
