#!/usr/bin/env python3
"""
Named Immortal — Vitality Assessment Tool
==========================================
Portable script that calls the Majestify API (crypto-health-hub) over HTTP
to calculate risk metrics and classify asset "vitality".

No local backend imports required — works anywhere with internet access.

Usage:
    python assess_vitality.py --coins bitcoin ethereum solana
    python assess_vitality.py --coins bitcoin --api https://custom-api.example.com
"""

import sys
import argparse
import asyncio
import json

# Handle UTF-8 output on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DEFAULT_API_BASE = "https://crypto-health-hub.onrender.com"

# ---------------------------------------------------------------------------
# HTTP Client (uses stdlib urllib — zero external dependencies)
# ---------------------------------------------------------------------------
try:
    import httpx

    async def _fetch_json(url: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

except ImportError:
    # Fallback: use stdlib so the skill works without pip installs
    import urllib.request
    import urllib.error

    async def _fetch_json(url: str) -> dict:
        loop = asyncio.get_running_loop()
        def _blocking():
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        return await loop.run_in_executor(None, _blocking)


# ---------------------------------------------------------------------------
# Vitality Classification
# ---------------------------------------------------------------------------
def classify_vitality(metrics: dict) -> tuple[str, str]:
    """
    Classifies an asset's vitality and returns (status, rationale).
    """
    if not metrics:
        return ("UNKNOWN ❓", "No metrics available.")

    sharpe = metrics.get("sharpeRatio", 0)
    max_dd = metrics.get("maxDrawdown", 0)
    sortino = metrics.get("sortinoRatio", 0)
    var95 = metrics.get("var95", 0)
    skew = metrics.get("skewness", 0)

    # 🛡️ IMMORTAL — strong risk-adjusted returns, manageable drawdown
    if sharpe > 1.2 and max_dd < 0.60:
        return (
            "IMMORTAL 🛡️",
            f"Strong risk-adjusted return (Sharpe {sharpe:.2f}), drawdown contained at {max_dd*100:.1f}%."
        )

    # ☠️ CRITICAL — very high drawdown or terrible risk/return
    if max_dd > 0.80 or (sharpe < -1.0 and var95 > 0.08):
        return (
            "CRITICAL ☠️",
            f"Excessive drawdown ({max_dd*100:.1f}%) or poor Sharpe ({sharpe:.2f}) with high VaR ({var95*100:.1f}%)."
        )

    # ⚠️ MORTAL — everything else
    return (
        "MORTAL ⚠️",
        f"Moderate profile: Sharpe {sharpe:.2f}, Drawdown {max_dd*100:.1f}%, Sortino {sortino:.2f}."
    )


# ---------------------------------------------------------------------------
# Core Assessment
# ---------------------------------------------------------------------------
async def assess_vitality(coins: list[str], api_base: str, days: int = 365) -> list[dict]:
    """Fetch metrics from the live API and classify each asset."""
    print(f"🔮  Named Immortal — Vitality Assessment")
    print(f"    API: {api_base}")
    print(f"    Assets: {', '.join(c.upper() for c in coins)}")
    print(f"    Window: {days} days")
    print("=" * 62)

    results = []

    for coin in coins:
        url = f"{api_base}/api/metrics/{coin}?days={days}"
        try:
            metrics = await _fetch_json(url)

            if not metrics or "sharpeRatio" not in metrics:
                print(f"\n  ❌  {coin.upper()}: API returned no usable metrics.")
                continue

            status, rationale = classify_vitality(metrics)

            result = {
                "coin": coin,
                "status": status,
                "rationale": rationale,
                "sharpeRatio": metrics.get("sharpeRatio"),
                "sortinoRatio": metrics.get("sortinoRatio"),
                "maxDrawdown": metrics.get("maxDrawdown"),
                "annualizedReturn": metrics.get("annualizedReturn"),
                "var95": metrics.get("var95"),
                "cvar95": metrics.get("cvar95"),
                "cornishFisherVar95": metrics.get("cornishFisherVar95"),
            }
            results.append(result)

            # Pretty-print
            print(f"\n  Asset: {coin.upper()}")
            print(f"  STATUS: {status}")
            print(f"    Rationale:     {rationale}")
            print(f"    Sharpe Ratio:  {metrics.get('sharpeRatio', 0):.4f}")
            print(f"    Sortino Ratio: {metrics.get('sortinoRatio', 0):.4f}")
            print(f"    Ann. Return:   {metrics.get('annualizedReturn', 0)*100:.2f}%")
            print(f"    Max Drawdown:  {metrics.get('maxDrawdown', 0)*100:.2f}%")
            print(f"    VaR (95%):     {metrics.get('var95', 0)*100:.2f}%")
            print(f"    CVaR (95%):    {metrics.get('cvar95', 0)*100:.2f}%")

        except Exception as e:
            print(f"\n  ❌  {coin.upper()}: {e}")

    print("\n" + "=" * 62)
    print(f"  Assessed {len(results)}/{len(coins)} assets.")

    # Emit machine-readable JSON to stderr for agent consumption
    if results:
        print(json.dumps(results, indent=2), file=sys.stderr)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Named Immortal — Assess Crypto Asset Vitality via Majestify API"
    )
    parser.add_argument(
        "--coins", nargs="+", default=["bitcoin", "ethereum"],
        help="CoinGecko asset IDs (e.g., bitcoin ethereum solana)"
    )
    parser.add_argument(
        "--api", default=DEFAULT_API_BASE,
        help=f"Base URL of the Majestify API (default: {DEFAULT_API_BASE})"
    )
    parser.add_argument(
        "--days", type=int, default=365,
        help="Historical window in days (default: 365)"
    )
    args = parser.parse_args()

    asyncio.run(assess_vitality(args.coins, args.api, args.days))
