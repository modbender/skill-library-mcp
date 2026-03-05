"""
#4 Logic Arbitrage (PolyClaw) — LLM finds correlated markets.

From the article: "LLM-анализ для поиска логических несостыковок
между коррелирующими рынками (покрывающие портфели)."

Logic:
1. Fetch active markets
2. Use LLM to find logical implications between market pairs
   (e.g. "If A wins election" implies "Party B loses majority")
3. Check if prices of correlated markets are inconsistent
4. Build covering portfolios for near-arbitrage

REQUIRES LLM API access (Claude, GPT-4, etc.)

Parameters (config.strategy_params):
    min_confidence:   0.90   LLM must be 90%+ confident in correlation
    min_spread:       0.05   Minimum price inconsistency to trade
    search_limit:     20     Markets to analyze per cycle
    order_size:       5      USDC per order
    llm_provider:     ""     "anthropic" or "openai"
    llm_api_key:      ""     API key (or set LLM_API_KEY env var)
    llm_model:        ""     Model name (e.g. claude-sonnet-4-20250514)

Ref: https://github.com/chainstacklabs/polyclaw
"""

import json
import logging
import os
import urllib.request
import sys
from typing import List, Optional, Tuple

sys.path.insert(0, os.environ.get(
    "PROBTRADE_SKILL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "openclaw-skill", "lib"),
))

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price, get_no_price,
)

logger = logging.getLogger("bot.logic_arb")


def _safe_fetch(endpoint, params=None):
    try:
        from api_client import fetch
        return fetch(endpoint, params)
    except SystemExit:
        return None


class LogicArbStrategy(Strategy):
    name = "logic_arb"

    def initialize(self, config: dict) -> None:
        self.min_confidence = config.get("min_confidence", 0.90)
        self.min_spread = config.get("min_spread", 0.05)
        self.search_limit = config.get("search_limit", 20)
        self.order_size = config.get("order_size", 5)
        self.llm_provider = config.get("llm_provider", "") or os.environ.get("LLM_PROVIDER", "")
        self.llm_api_key = config.get("llm_api_key", "") or os.environ.get("LLM_API_KEY", "")
        self.llm_model = config.get("llm_model", "") or os.environ.get("LLM_MODEL", "")

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        if not self.llm_api_key:
            logger.info("No LLM API key configured — set llm_api_key or LLM_API_KEY env var")
            return []

        signals = []

        # Get additional markets to form pairs
        hot_data = _safe_fetch("/markets/hot", {"limit": str(self.search_limit)})
        hot_markets = hot_data.get("markets", []) if hot_data else []

        # Combine with breaking markets for wider coverage
        all_markets = {m.get("condition_id"): m for m in markets + hot_markets if m.get("condition_id")}
        market_list = list(all_markets.values())

        if len(market_list) < 2:
            return []

        # Find correlated pairs using LLM
        pairs = self._find_correlations(market_list)

        for m1, m2, correlation, confidence in pairs:
            if confidence < self.min_confidence:
                continue

            p1 = get_yes_price(m1)
            p2 = get_yes_price(m2)
            if p1 is None or p2 is None:
                continue

            # Check for price inconsistency
            # If A implies B, then P(A) <= P(B)
            # If P(A) > P(B) + spread, there's an arbitrage
            if correlation == "implies" and p1 > p2 + self.min_spread:
                # A is overpriced relative to B — buy B
                signals.append(Signal(
                    market=m2["condition_id"],
                    side="BUY",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=p2,
                    confidence=confidence,
                    reason=(
                        f"Logic arb: '{m1.get('question', '')[:40]}' (YES={p1:.2f}) "
                        f"implies '{m2.get('question', '')[:40]}' (YES={p2:.2f})"
                    ),
                ))

            elif correlation == "contradicts":
                # If A contradicts B, then P(A) + P(B) <= 1
                if p1 + p2 > 1.0 + self.min_spread:
                    # Both overpriced — sell the more expensive one (buy NO)
                    target = m1 if p1 > p2 else m2
                    tp = get_yes_price(target)
                    signals.append(Signal(
                        market=target["condition_id"],
                        side="BUY",
                        outcome="No",
                        order_type="LIMIT",
                        amount=self.order_size,
                        price=round(1.0 - tp, 2) if tp else 0.50,
                        confidence=confidence,
                        reason=(
                            f"Logic arb: contradicting markets both overpriced "
                            f"({p1:.2f} + {p2:.2f} = {p1+p2:.2f} > 1.0)"
                        ),
                    ))

        return signals

    def _find_correlations(self, markets: list) -> List[Tuple[dict, dict, str, float]]:
        """
        Use LLM to find logical correlations between market pairs.

        Returns list of (market_a, market_b, correlation_type, confidence)
        where correlation_type is "implies" or "contradicts".

        Override this to use your preferred LLM.
        """
        if not self.llm_api_key or not self.llm_provider:
            return []

        # Build prompt with market questions
        questions = []
        for i, m in enumerate(markets[:self.search_limit]):
            q = m.get("question", "")
            p = get_yes_price(m)
            if q and p is not None:
                questions.append(f"{i}. [{p:.2f}] {q}")

        if len(questions) < 2:
            return []

        prompt = (
            "Analyze these prediction markets and find logical relationships.\n"
            "For each pair that has a strong logical connection, output JSON:\n"
            '{"pairs": [{"a": <index>, "b": <index>, "type": "implies"|"contradicts", '
            '"confidence": 0.0-1.0, "reasoning": "..."}]}\n\n'
            "Markets:\n" + "\n".join(questions) + "\n\n"
            "Only include pairs with confidence > 0.85. Return empty pairs array if none found."
        )

        response = self._call_llm(prompt)
        if not response:
            return []

        try:
            data = json.loads(response)
            results = []
            for pair in data.get("pairs", []):
                a_idx = pair.get("a")
                b_idx = pair.get("b")
                if a_idx is not None and b_idx is not None:
                    if 0 <= a_idx < len(markets) and 0 <= b_idx < len(markets):
                        results.append((
                            markets[a_idx],
                            markets[b_idx],
                            pair.get("type", "implies"),
                            float(pair.get("confidence", 0)),
                        ))
            return results
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to parse LLM response: {e}")
            return []

    def _call_llm(self, prompt: str) -> Optional[str]:
        """
        Call LLM API. Supports Anthropic (Claude) and OpenAI.

        Override for custom LLM integrations.
        """
        try:
            if self.llm_provider == "anthropic":
                return self._call_anthropic(prompt)
            elif self.llm_provider == "openai":
                return self._call_openai(prompt)
            else:
                logger.warning(f"Unknown LLM provider: {self.llm_provider}")
                return None
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return None

    def _call_anthropic(self, prompt: str) -> Optional[str]:
        model = self.llm_model or "claude-sonnet-4-20250514"
        body = json.dumps({
            "model": model,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }).encode()
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "x-api-key": self.llm_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["content"][0]["text"]

    def _call_openai(self, prompt: str) -> Optional[str]:
        model = self.llm_model or "gpt-4o-mini"
        body = json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
        }).encode()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
