"""
#7 Weather Forecast Arbitrage — NOAA/ECMWF forecast vs market price.

From the article: "Эксплуатация разрыва вероятностей между официальными
прогнозами NOAA и ценами толпы."

Logic:
1. Search for weather-related markets on prob.trade
2. Fetch official forecast data from NOAA API
3. Compare forecast probability vs market price
4. Trade when delta exceeds threshold (15%+)

IMPORTANT: Requires NOAA API access. Get a free token at:
https://www.weather.gov/documentation/services-web-api

Parameters (config.strategy_params):
    min_delta:        0.15   Minimum divergence to trade
    search_keywords:  temperature,weather,heat,cold,snow,hurricane
    noaa_api_token:   ""     NOAA API token (or set NOAA_API_TOKEN env var)
    order_size:       5      USDC per order

Ref: https://blog.devgenius.io/found-the-weather-trading-bots-quietly-making-24-000-on-polymarket
"""

import json
import logging
import os
import sys
import urllib.request
from typing import List, Optional

sys.path.insert(0, os.environ.get(
    "PROBTRADE_SKILL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "openclaw-skill", "lib"),
))

from ..strategy_base import (
    Strategy, Signal,
    get_yes_price,
)

logger = logging.getLogger("bot.weather_arb")


def _safe_fetch(endpoint, params=None):
    try:
        from api_client import fetch
        return fetch(endpoint, params)
    except SystemExit:
        return None


class WeatherArbStrategy(Strategy):
    name = "weather_arb"

    def initialize(self, config: dict) -> None:
        self.min_delta = config.get("min_delta", 0.15)
        keywords = config.get("search_keywords", "temperature,weather,heat,cold,snow,hurricane")
        self.keywords = [k.strip() for k in keywords.split(",")]
        self.noaa_token = config.get("noaa_api_token", "") or os.environ.get("NOAA_API_TOKEN", "")
        self.order_size = config.get("order_size", 5)

    def scan(self, markets: list, positions: list, balance: float) -> List[Signal]:
        signals = []
        held = {p.get("conditionId") for p in positions}

        # Search for weather markets
        weather_markets = self._find_weather_markets()
        if not weather_markets:
            logger.info("No weather markets found")
            return []

        for m in weather_markets:
            cid = m.get("condition_id")
            if not cid or cid in held:
                continue
            if not m.get("active") or not m.get("accepting_orders"):
                continue

            yes_price = get_yes_price(m)
            if yes_price is None:
                continue

            question = m.get("question", "")

            # Get forecast probability
            forecast_prob = self._get_forecast_probability(question)
            if forecast_prob is None:
                continue

            delta = forecast_prob - yes_price

            if abs(delta) < self.min_delta:
                continue

            if delta > 0:
                # Market undervalues — buy YES
                signals.append(Signal(
                    market=cid,
                    side="BUY",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=yes_price,
                    confidence=min(abs(delta) / 0.30, 1.0),
                    reason=f"Weather: forecast={forecast_prob:.0%} vs market={yes_price:.0%} (+{delta:.0%})",
                ))
            else:
                # Market overvalues — buy NO
                no_price = 1.0 - yes_price
                signals.append(Signal(
                    market=cid,
                    side="BUY",
                    outcome="No",
                    order_type="LIMIT",
                    amount=self.order_size,
                    price=round(no_price, 2),
                    confidence=min(abs(delta) / 0.30, 1.0),
                    reason=f"Weather: forecast={forecast_prob:.0%} vs market={yes_price:.0%} ({delta:.0%})",
                ))

        signals.sort(key=lambda s: s.confidence, reverse=True)
        return signals

    def _find_weather_markets(self) -> list:
        """Search prob.trade for weather-related markets."""
        all_markets = []
        for keyword in self.keywords[:3]:  # Limit API calls
            data = _safe_fetch("/markets/search", {"q": keyword, "limit": "10"})
            if data:
                all_markets.extend(data.get("markets", []))

        # Deduplicate by condition_id
        seen = set()
        unique = []
        for m in all_markets:
            cid = m.get("condition_id")
            if cid and cid not in seen:
                seen.add(cid)
                unique.append(m)
        return unique

    def _get_forecast_probability(self, question: str) -> Optional[float]:
        """
        Get forecast probability from NOAA API based on market question.

        Override this method with your own forecast data source.
        Default: returns None (no NOAA integration — set NOAA_API_TOKEN).

        Example integration:
            1. Parse location and metric from question
            2. Call NOAA API: https://api.weather.gov/gridpoints/{office}/{x},{y}/forecast
            3. Extract probability from forecast data
            4. Return as float 0.0-1.0
        """
        if not self.noaa_token:
            logger.debug("No NOAA token configured — skipping forecast lookup")
            return None

        # TODO: Implement NOAA API integration
        # This is intentionally left as a stub for users to implement
        # based on their specific weather market interests.
        #
        # See: https://www.weather.gov/documentation/services-web-api
        # Example: GET https://api.weather.gov/gridpoints/OKX/33,37/forecast
        #
        # Parse the question to extract:
        # - Location (city, state)
        # - Metric (temperature, precipitation, etc.)
        # - Threshold (above 90°F, etc.)
        # - Time window (this week, tomorrow, etc.)
        #
        # Then compare forecast data against the threshold.

        return None
