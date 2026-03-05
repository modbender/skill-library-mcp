#!/usr/bin/env python3
import argparse
import os
from typing import Any, Dict, List

from simmer_sdk import SimmerClient

TRADE_SOURCE = "sdk:polymarket-edge-liquidity"
SKILL_SLUG = "polymarket-edge-liquidity"

_client = None


def get_client() -> SimmerClient:
    global _client
    if _client is None:
        _client = SimmerClient(
            api_key=os.environ["SIMMER_API_KEY"],
            venue=os.getenv("TRADING_VENUE", "simmer"),
        )
    return _client


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def pick_side(prob_yes: float) -> str:
    # Mean-reversion baseline around 50/50
    return "yes" if prob_yes < 0.5 else "no"


def expected_edge(prob_yes: float, side: str) -> float:
    # Simple confidence gap from fair coin baseline (starter strategy style)
    p = prob_yes if side == "yes" else (1.0 - prob_yes)
    return abs(p - 0.5)


def candidate_markets(markets: List[Dict[str, Any]], min_liquidity: float) -> List[Dict[str, Any]]:
    out = []
    for m in markets:
        vol = to_float(m.get("volume_24h"), 0.0)
        if vol >= min_liquidity and m.get("status") == "active":
            out.append(m)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Edge+liquidity Simmer strategy")
    parser.add_argument("--live", action="store_true", help="Execute trades")
    args = parser.parse_args()

    min_edge = float(os.getenv("MIN_EDGE", "0.03"))
    min_liquidity = float(os.getenv("MIN_LIQUIDITY", "3000"))
    scan_limit = int(os.getenv("SCAN_LIMIT", "25"))
    trade_amount = float(os.getenv("TRADE_AMOUNT", "10"))

    client = get_client()
    markets = client.get_markets(status="active", limit=scan_limit)
    picks = candidate_markets(markets, min_liquidity)

    if not picks:
        print("No markets passed liquidity filter")
        return

    traded = 0
    for m in picks[:5]:
        market_id = m["id"]
        question = m.get("question", market_id)
        prob_yes = to_float(m.get("current_probability"), 0.5)
        side = pick_side(prob_yes)
        edge = expected_edge(prob_yes, side)

        if edge < min_edge:
            continue

        ctx = client.get_market_context(market_id)
        if ctx.get("warnings"):
            print(f"Skip {question} (warnings: {ctx['warnings']})")
            continue

        reasoning = (
            f"Starter edge/liquidity strategy: side={side}, prob_yes={prob_yes:.3f}, "
            f"edge={edge:.3f} >= {min_edge:.3f}, liquidity>= {min_liquidity:.0f}."
        )

        if not args.live:
            print(f"[DRY RUN] {question} | {side.upper()} | {trade_amount} | {reasoning}")
            continue

        result = client.trade(
            market_id,
            side,
            trade_amount,
            source=TRADE_SOURCE,
            skill_slug=SKILL_SLUG,
            reasoning=reasoning,
        )
        traded += 1
        print(f"TRADE OK {question} -> {side.upper()} shares={getattr(result, 'shares_bought', 'n/a')}")

    if args.live:
        print(f"Live mode complete. trades={traded}")


if __name__ == "__main__":
    main()
