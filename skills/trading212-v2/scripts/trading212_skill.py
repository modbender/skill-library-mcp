#!/usr/bin/env python3
"""
Trading212 OpenClaw Skill -- main entrypoint.

Usage
-----
  python trading212_skill.py --mode summary
  python trading212_skill.py --mode propose [--risk low|medium|high]
  python trading212_skill.py --mode execute_trade --params '{"symbol":"AAPL_US_EQ","side":"sell","quantity":5,"order_type":"market"}'
  python trading212_skill.py --mode dividends
  python trading212_skill.py --mode history [--params '{"ticker":"AAPL_US_EQ","days":30}']
  python trading212_skill.py --mode watchlist
  python trading212_skill.py --mode allocation [--rebalance]

All output is structured JSON written to stdout so the calling agent
can parse and present it.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Load .env from project root before any Trading212 imports.
_env_path = Path(__file__).resolve().parents[3] / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)
from typing import Any, Dict, List, Optional

import yaml

# Ensure the scripts directory is on the import path.
_SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPTS_DIR))

from t212_client import Trading212Client, Trading212Error  # noqa: E402
from snapshot import (  # noqa: E402
    compute_performance,
    load_previous_snapshot,
    save_snapshot,
)
from proposal_rules import generate_proposals  # noqa: E402

# Skill root for config files (parent of scripts/).
_PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _output(data: Dict[str, Any]) -> None:
    """Print structured JSON to stdout and exit cleanly."""
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def _error(message: str, code: str = "error") -> None:
    """Print a structured error and exit with code 1."""
    _output({"status": "error", "code": code, "message": message})
    sys.exit(1)


def _build_position_record(pos: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise a raw Trading212 position into a flat dict."""
    instrument = pos.get("instrument", {})
    wallet = pos.get("walletImpact", {})
    return {
        "ticker": instrument.get("ticker", pos.get("ticker", "")),
        "name": instrument.get("name", ""),
        "isin": instrument.get("isin", ""),
        "currency": instrument.get("currency", ""),
        "quantity": pos.get("quantity", 0),
        "avg_price": pos.get("averagePricePaid", 0),
        "current_price": pos.get("currentPrice", 0),
        "value": wallet.get("currentValue", 0),
        "total_cost": wallet.get("totalCost", 0),
        "unrealized_pnl": wallet.get("unrealizedProfitLoss", 0),
        "fx_impact": wallet.get("fxImpact", 0),
        "wallet_currency": wallet.get("currency", ""),
    }


def _extract_cash(cash_data: Any) -> float:
    """Extract the cash amount from whatever the API returns."""
    if isinstance(cash_data, dict):
        return float(cash_data.get("free", cash_data.get("cash", 0.0)))
    if isinstance(cash_data, (int, float)):
        return float(cash_data)
    return 0.0


def _load_yaml_config(filename: str) -> Dict[str, Any]:
    """Load a YAML config file from the config/ directory."""
    path = _PROJECT_ROOT / "config" / filename
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# ------------------------------------------------------------------
# Mode: summary
# ------------------------------------------------------------------

def _run_summary(client: Trading212Client) -> None:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Fetch live data
    raw_positions = client.get_positions()
    cash_data = client.get_cash()

    positions = [_build_position_record(p) for p in raw_positions]
    cash = _extract_cash(cash_data)
    total_value = sum(p["value"] for p in positions) + cash

    # 2. Compare with previous snapshot
    prev = load_previous_snapshot(reference_date=today_str)
    daily_change_eur: Optional[float] = None
    daily_change_pct: Optional[float] = None

    if prev is not None:
        prev_total = prev.get("total_value", 0)
        if prev_total > 0:
            daily_change_eur = round(total_value - prev_total, 2)
            daily_change_pct = round((daily_change_eur / prev_total) * 100, 4)

    # 3. Per-position daily change (if previous snapshot has that ticker)
    prev_positions_map: Dict[str, float] = {}
    if prev is not None:
        for pp in prev.get("positions", []):
            prev_positions_map[pp["ticker"]] = pp["value"]

    for pos in positions:
        prev_val = prev_positions_map.get(pos["ticker"])
        if prev_val is not None and prev_val > 0:
            change = pos["value"] - prev_val
            pos["daily_change_eur"] = round(change, 2)
            pos["daily_change_pct"] = round((change / prev_val) * 100, 4)
        else:
            pos["daily_change_eur"] = None
            pos["daily_change_pct"] = None

    # 4. Top gainers / losers
    ranked = [p for p in positions if p["daily_change_pct"] is not None]
    ranked.sort(key=lambda p: p["daily_change_pct"], reverse=True)  # type: ignore[arg-type]

    top_n = min(5, len(ranked))
    top_gainers = [
        {
            "ticker": p["ticker"],
            "name": p["name"],
            "daily_pct": p["daily_change_pct"],
            "contribution_eur": p["daily_change_eur"],
        }
        for p in ranked[:top_n]
        if p["daily_change_pct"] is not None and p["daily_change_pct"] > 0
    ]
    top_losers = [
        {
            "ticker": p["ticker"],
            "name": p["name"],
            "daily_pct": p["daily_change_pct"],
            "contribution_eur": p["daily_change_eur"],
        }
        for p in reversed(ranked[-top_n:])
        if p["daily_change_pct"] is not None and p["daily_change_pct"] < 0
    ]

    # 5. Notable events (orders + dividends today)
    notable_events: List[Dict[str, Any]] = []
    try:
        todays_orders = client.get_todays_orders()
        for item in todays_orders:
            order = item.get("order", {})
            fill = item.get("fill", {})
            inst = order.get("instrument", {})
            side = order.get("side", "")
            qty = fill.get("quantity", order.get("filledQuantity", 0))
            notable_events.append({
                "type": side.lower(),
                "ticker": inst.get("ticker", order.get("ticker", "")),
                "desc": f"{'Koop' if side == 'BUY' else 'Verkoop'} {abs(qty)}x {inst.get('name', '')}",
            })
    except Trading212Error:
        pass  # Non-critical; skip if rate-limited.

    try:
        todays_dividends = client.get_todays_dividends()
        for div in todays_dividends:
            inst = div.get("instrument", {})
            notable_events.append({
                "type": "dividend",
                "ticker": inst.get("ticker", div.get("ticker", "")),
                "desc": f"Dividend {div.get('amount', '?')} {div.get('currency', '')} voor {inst.get('name', '')}",
            })
    except Trading212Error:
        pass

    # 6. Save today's snapshot for future comparison (enriched with prices)
    snapshot_positions = [
        {
            "ticker": p["ticker"],
            "value": p["value"],
            "quantity": p["quantity"],
            "avg_price": p.get("avg_price"),
            "current_price": p.get("current_price"),
        }
        for p in positions
    ]
    save_snapshot(snapshot_positions, cash, total_value, date_str=today_str)

    # 7. Multi-period performance
    performance = compute_performance(total_value, reference_date=today_str)

    # 8. Build output
    result: Dict[str, Any] = {
        "mode": "summary",
        "date": today_str,
        "environment": "demo" if client.demo else "live",
        "portfolio": {
            "total_value": round(total_value, 2),
            "cash": round(cash, 2),
            "invested": round(total_value - cash, 2),
            "daily_change_eur": daily_change_eur,
            "daily_change_pct": daily_change_pct,
        },
        "performance": performance,
        "positions": positions,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "notable_events": notable_events,
    }
    _output(result)


# ------------------------------------------------------------------
# Mode: propose
# ------------------------------------------------------------------

def _run_propose(client: Trading212Client, risk_mode: Optional[str] = None) -> None:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    raw_positions = client.get_positions()
    cash_data = client.get_cash()

    positions = [_build_position_record(p) for p in raw_positions]
    cash = _extract_cash(cash_data)
    total_value = sum(p["value"] for p in positions) + cash

    # Attach daily change from snapshot if available
    prev = load_previous_snapshot(reference_date=today_str)
    prev_map: Dict[str, float] = {}
    if prev is not None:
        for pp in prev.get("positions", []):
            prev_map[pp["ticker"]] = pp["value"]
    for pos in positions:
        prev_val = prev_map.get(pos["ticker"])
        if prev_val is not None and prev_val > 0:
            pos["daily_change_pct"] = round(
                ((pos["value"] - prev_val) / prev_val) * 100, 4
            )
        else:
            pos["daily_change_pct"] = None

    proposals = generate_proposals(
        positions=positions,
        cash=cash,
        total_value=total_value,
        risk_override=risk_mode,
    )

    result: Dict[str, Any] = {
        "mode": "propose",
        "date": today_str,
        "environment": "demo" if client.demo else "live",
        "portfolio_value": round(total_value, 2),
        "cash": round(cash, 2),
        "proposals": proposals,
    }
    _output(result)


# ------------------------------------------------------------------
# Mode: execute_trade (with order validation)
# ------------------------------------------------------------------

def _run_execute_trade(client: Trading212Client, params: Dict[str, Any]) -> None:
    symbol = params.get("symbol", "")
    order_type = params.get("order_type", "market")
    side = params.get("side", "")
    quantity = params.get("quantity", 0)
    limit_price = params.get("limit_price")

    if not symbol:
        _error("Missing required parameter: symbol")
    if side not in ("buy", "sell"):
        _error("Parameter 'side' must be 'buy' or 'sell'")
    if not quantity or quantity <= 0:
        _error("Parameter 'quantity' must be a positive number")

    # -- Order validation --
    if side == "buy":
        # Check if enough cash is available.
        try:
            cash_data = client.get_cash()
            cash = _extract_cash(cash_data)
            # For market orders, use current position price estimate.
            # For limit orders, use the limit price.
            estimated_price = float(limit_price) if limit_price else None
            if estimated_price is None:
                # Try to get current price from positions.
                positions = client.get_positions(ticker=symbol)
                if positions:
                    pos = positions[0]
                    estimated_price = pos.get("currentPrice", 0)
            if estimated_price and estimated_price > 0:
                estimated_cost = float(quantity) * estimated_price
                if estimated_cost > cash:
                    _error(
                        f"Onvoldoende cash voor koop. Geschatte kosten: "
                        f"{estimated_cost:.2f}, beschikbaar: {cash:.2f}.",
                        code="validation_error",
                    )
        except Trading212Error:
            pass  # Proceed anyway; the API will reject if insufficient funds.

    elif side == "sell":
        # Check if enough shares are held.
        try:
            positions = client.get_positions(ticker=symbol)
            if positions:
                held_qty = sum(p.get("quantity", 0) for p in positions)
                if float(quantity) > held_qty:
                    _error(
                        f"Onvoldoende aandelen om te verkopen. Gevraagd: "
                        f"{quantity}, in bezit: {held_qty}.",
                        code="validation_error",
                    )
            else:
                _error(
                    f"Geen positie gevonden voor {symbol}. Kan niet verkopen.",
                    code="validation_error",
                )
        except Trading212Error:
            pass

    # Trading212 convention: sell = negative quantity.
    signed_qty = float(quantity) if side == "buy" else -float(quantity)

    try:
        if order_type == "limit":
            if limit_price is None:
                _error("limit_price is required for limit orders")
            resp = client.place_limit_order(
                ticker=symbol,
                quantity=signed_qty,
                limit_price=float(limit_price),
            )
        else:
            resp = client.place_market_order(ticker=symbol, quantity=signed_qty)

        result: Dict[str, Any] = {
            "mode": "execute_trade",
            "environment": "demo" if client.demo else "live",
            "order_id": resp.get("id"),
            "status": resp.get("status", "UNKNOWN"),
            "side": resp.get("side", side.upper()),
            "ticker": resp.get("ticker", symbol),
            "quantity": abs(signed_qty),
            "order_type": resp.get("type", order_type.upper()),
            "error": None,
        }
        _output(result)

    except Trading212Error as exc:
        result = {
            "mode": "execute_trade",
            "environment": "demo" if client.demo else "live",
            "order_id": None,
            "status": "REJECTED",
            "error": exc.message,
        }
        _output(result)
        sys.exit(1)


# ------------------------------------------------------------------
# Mode: dividends
# ------------------------------------------------------------------

def _run_dividends(client: Trading212Client) -> None:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    one_year_ago = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

    all_dividends = client.get_all_dividends()

    # Group by ticker.
    per_ticker: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "ticker": "",
        "total": 0.0,
        "last_12m": 0.0,
        "last_paid": None,
        "payments": 0,
        "payments_12m": 0,
    })

    total_all = 0.0
    total_12m = 0.0
    calendar: List[Dict[str, Any]] = []

    for div in all_dividends:
        instrument = div.get("instrument", {})
        ticker = instrument.get("ticker", div.get("ticker", ""))
        amount = float(div.get("amount", 0))
        paid_on = div.get("paidOn", "")

        if not ticker:
            continue

        entry = per_ticker[ticker]
        entry["ticker"] = ticker
        entry["total"] += amount
        entry["payments"] += 1
        total_all += amount

        if paid_on >= one_year_ago:
            entry["last_12m"] += amount
            entry["payments_12m"] += 1
            total_12m += amount

        if entry["last_paid"] is None or paid_on > entry["last_paid"]:
            entry["last_paid"] = paid_on

    # Build calendar (most recent payment per ticker).
    for ticker, data in per_ticker.items():
        if data["last_paid"]:
            calendar.append({
                "ticker": ticker,
                "last_paid": data["last_paid"],
                "amount": round(data["total"] / max(data["payments"], 1), 2),
            })
    calendar.sort(key=lambda x: x["last_paid"] or "", reverse=True)

    # Build per-ticker list with estimated annual yield.
    per_ticker_list: List[Dict[str, Any]] = []
    for ticker, data in sorted(per_ticker.items()):
        estimated_annual = 0.0
        if data["payments_12m"] > 0:
            avg_payment = data["last_12m"] / data["payments_12m"]
            # Estimate based on quarterly dividends (4x/year) or frequency seen.
            estimated_annual = round(avg_payment * max(data["payments_12m"], 1), 2)

        per_ticker_list.append({
            "ticker": ticker,
            "total": round(data["total"], 2),
            "last_12m": round(data["last_12m"], 2),
            "last_paid": data["last_paid"],
            "estimated_annual": estimated_annual,
        })

    result: Dict[str, Any] = {
        "mode": "dividends",
        "date": today_str,
        "environment": "demo" if client.demo else "live",
        "total_dividends_received": round(total_all, 2),
        "last_12_months": round(total_12m, 2),
        "per_ticker": per_ticker_list,
        "calendar": calendar,
    }
    _output(result)


# ------------------------------------------------------------------
# Mode: history
# ------------------------------------------------------------------

def _run_history(client: Trading212Client, params: Optional[Dict[str, Any]] = None) -> None:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    ticker_filter = None
    period_days = None
    if params:
        ticker_filter = params.get("ticker")
        period_days = params.get("days")

    all_orders = client.get_all_historical_orders(ticker=ticker_filter)

    # Filter by date range if specified.
    if period_days:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=int(period_days))).strftime("%Y-%m-%d")
        filtered = []
        for item in all_orders:
            fill = item.get("fill", {})
            filled_at = fill.get("filledAt", "")
            order_date = item.get("order", {}).get("dateCreated", "")
            date_str = filled_at or order_date
            if date_str >= cutoff:
                filtered.append(item)
        all_orders = filtered

    # Calculate realized P&L per ticker.
    ticker_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "ticker": "",
        "buys": 0,
        "sells": 0,
        "total_buy_value": 0.0,
        "total_sell_value": 0.0,
    })

    orders_output: List[Dict[str, Any]] = []

    for item in all_orders:
        order = item.get("order", {})
        fill = item.get("fill", {})
        inst = order.get("instrument", {})

        ticker = inst.get("ticker", order.get("ticker", ""))
        side = order.get("side", "")
        status = order.get("status", "")
        fill_price = float(fill.get("price", 0))
        fill_qty = float(fill.get("quantity", 0))
        filled_at = fill.get("filledAt", "")

        if not ticker:
            continue

        stats = ticker_stats[ticker]
        stats["ticker"] = ticker

        if side == "BUY" and fill_qty > 0:
            stats["buys"] += 1
            stats["total_buy_value"] += fill_price * fill_qty
        elif side == "SELL" and fill_qty > 0:
            stats["sells"] += 1
            stats["total_sell_value"] += fill_price * fill_qty

        orders_output.append({
            "ticker": ticker,
            "side": side.lower() if side else status.lower(),
            "quantity": fill_qty if fill_qty else order.get("filledQuantity", 0),
            "price": fill_price,
            "status": status,
            "date": filled_at or order.get("dateCreated", ""),
        })

    # Calculate approximate realized P&L.
    total_realized_pnl = 0.0
    per_ticker_list: List[Dict[str, Any]] = []

    for ticker, stats in sorted(ticker_stats.items()):
        realized = stats["total_sell_value"] - (
            stats["total_buy_value"] * (stats["sells"] / max(stats["buys"], 1))
            if stats["buys"] > 0 else 0
        )
        total_realized_pnl += realized
        per_ticker_list.append({
            "ticker": ticker,
            "buys": stats["buys"],
            "sells": stats["sells"],
            "realized_pnl": round(realized, 2),
        })

    result: Dict[str, Any] = {
        "mode": "history",
        "date": today_str,
        "environment": "demo" if client.demo else "live",
        "period_days": period_days,
        "total_orders": len(all_orders),
        "realized_pnl": round(total_realized_pnl, 2),
        "per_ticker": per_ticker_list,
        "orders": orders_output,
    }
    _output(result)


# ------------------------------------------------------------------
# Mode: watchlist
# ------------------------------------------------------------------

def _run_watchlist(client: Trading212Client) -> None:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    config = _load_yaml_config("watchlist.yaml")
    watchlist_items = config.get("watchlist", [])

    if not watchlist_items:
        _output({
            "mode": "watchlist",
            "date": today_str,
            "environment": "demo" if client.demo else "live",
            "items": [],
            "message": "Watchlist is leeg. Voeg tickers toe aan config/watchlist.yaml.",
        })
        return

    # Build a map of current positions for price lookup.
    raw_positions = client.get_positions()
    positions = [_build_position_record(p) for p in raw_positions]
    price_map: Dict[str, float] = {
        p["ticker"]: p["current_price"] for p in positions
    }
    held_set = {p["ticker"] for p in positions}

    items_output: List[Dict[str, Any]] = []
    alerts: List[Dict[str, Any]] = []

    for entry in watchlist_items:
        ticker = entry.get("ticker", "")
        if not ticker:
            continue

        alert_below = entry.get("alert_below")
        alert_above = entry.get("alert_above")
        current_price = price_map.get(ticker)
        is_held = ticker in held_set

        item: Dict[str, Any] = {
            "ticker": ticker,
            "held": is_held,
            "current_price": current_price,
            "alert_below": alert_below,
            "alert_above": alert_above,
            "triggered_alerts": [],
        }

        if current_price is not None:
            if alert_below is not None and current_price < alert_below:
                alert = {
                    "ticker": ticker,
                    "type": "below",
                    "threshold": alert_below,
                    "current_price": current_price,
                    "message": (
                        f"{ticker} prijs ({current_price:.2f}) is onder de "
                        f"drempel ({alert_below:.2f})."
                    ),
                }
                item["triggered_alerts"].append(alert)
                alerts.append(alert)

            if alert_above is not None and current_price > alert_above:
                alert = {
                    "ticker": ticker,
                    "type": "above",
                    "threshold": alert_above,
                    "current_price": current_price,
                    "message": (
                        f"{ticker} prijs ({current_price:.2f}) is boven de "
                        f"drempel ({alert_above:.2f})."
                    ),
                }
                item["triggered_alerts"].append(alert)
                alerts.append(alert)

        items_output.append(item)

    result: Dict[str, Any] = {
        "mode": "watchlist",
        "date": today_str,
        "environment": "demo" if client.demo else "live",
        "items": items_output,
        "triggered_alerts": alerts,
    }
    _output(result)


# ------------------------------------------------------------------
# Mode: allocation
# ------------------------------------------------------------------

def _run_allocation(client: Trading212Client, rebalance: bool = False) -> None:
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    config = _load_yaml_config("allocation.yaml")
    target_alloc = config.get("target_allocation", {})

    raw_positions = client.get_positions()
    cash_data = client.get_cash()

    positions = [_build_position_record(p) for p in raw_positions]
    cash = _extract_cash(cash_data)
    total_value = sum(p["value"] for p in positions) + cash

    if total_value <= 0:
        _error("Portfolio waarde is 0. Kan allocatie niet berekenen.")

    # Current allocation.
    current_alloc: List[Dict[str, Any]] = []
    for pos in positions:
        weight = (pos["value"] / total_value) * 100
        target = target_alloc.get(pos["ticker"])
        deviation = round(weight - target, 2) if target is not None else None
        current_alloc.append({
            "ticker": pos["ticker"],
            "name": pos["name"],
            "value": round(pos["value"], 2),
            "current_weight_pct": round(weight, 2),
            "target_weight_pct": target,
            "deviation_pct": deviation,
        })

    # Cash allocation.
    cash_weight = (cash / total_value) * 100
    cash_target = target_alloc.get("_cash")
    cash_deviation = round(cash_weight - cash_target, 2) if cash_target is not None else None

    # Target tickers not currently held.
    held_tickers = {p["ticker"] for p in positions}
    missing_targets: List[Dict[str, Any]] = []
    for ticker, target_pct in target_alloc.items():
        if ticker == "_cash":
            continue
        if ticker not in held_tickers:
            missing_targets.append({
                "ticker": ticker,
                "target_weight_pct": target_pct,
                "current_weight_pct": 0.0,
                "deviation_pct": round(-target_pct, 2),
            })

    # Rebalancing proposals.
    rebalance_proposals: List[Dict[str, Any]] = []
    if rebalance and target_alloc:
        for entry in current_alloc:
            target = entry["target_weight_pct"]
            if target is None:
                continue
            deviation = entry["deviation_pct"]
            if deviation is None:
                continue

            ticker = entry["ticker"]
            if abs(deviation) < 1.0:
                continue  # Within 1% tolerance.

            target_value = (target / 100.0) * total_value
            diff_value = target_value - entry["value"]

            # Find current price.
            current_price = 0.0
            for pos in positions:
                if pos["ticker"] == ticker:
                    current_price = pos.get("current_price", 0)
                    break

            if current_price <= 0:
                continue

            qty = abs(math.floor(diff_value / current_price))
            if qty < 1:
                continue

            action = "buy" if diff_value > 0 else "sell"
            rebalance_proposals.append({
                "symbol": ticker,
                "action": action,
                "quantity": qty,
                "reason": (
                    f"Rebalance: {ticker} is {abs(deviation):.1f}% "
                    f"{'boven' if deviation > 0 else 'onder'} target ({target}%). "
                    f"{'Koop' if action == 'buy' else 'Verkoop'} {qty} aandelen "
                    f"om dichter bij doelallocatie te komen."
                ),
            })

        # Proposals for missing target tickers.
        for missing in missing_targets:
            ticker = missing["ticker"]
            target_pct = missing["target_weight_pct"]
            target_value = (target_pct / 100.0) * total_value
            rebalance_proposals.append({
                "symbol": ticker,
                "action": "buy",
                "quantity": None,  # Price unknown.
                "reason": (
                    f"Rebalance: {ticker} is niet in portfolio maar heeft "
                    f"target allocatie van {target_pct}%. "
                    f"Overweeg ~{target_value:.2f} te investeren."
                ),
            })

    result: Dict[str, Any] = {
        "mode": "allocation",
        "date": today_str,
        "environment": "demo" if client.demo else "live",
        "portfolio_value": round(total_value, 2),
        "cash": {
            "value": round(cash, 2),
            "current_weight_pct": round(cash_weight, 2),
            "target_weight_pct": cash_target,
            "deviation_pct": cash_deviation,
        },
        "positions": current_alloc,
        "missing_targets": missing_targets,
    }

    if rebalance:
        result["rebalance_proposals"] = rebalance_proposals

    _output(result)


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Trading212 skill for OpenClaw")
    parser.add_argument(
        "--mode",
        required=True,
        choices=[
            "summary",
            "propose",
            "execute_trade",
            "dividends",
            "history",
            "watchlist",
            "allocation",
        ],
        help="Skill mode to run",
    )
    parser.add_argument(
        "--risk",
        choices=["low", "medium", "high"],
        default=None,
        help="Risk mode override for propose mode",
    )
    parser.add_argument(
        "--params",
        type=str,
        default=None,
        help="JSON string with parameters (used by execute_trade, history)",
    )
    parser.add_argument(
        "--rebalance",
        action="store_true",
        default=False,
        help="Generate rebalancing proposals (allocation mode only)",
    )
    args = parser.parse_args()

    try:
        client = Trading212Client()
    except ValueError as exc:
        _error(str(exc), code="config_error")

    if args.mode == "summary":
        _run_summary(client)
    elif args.mode == "propose":
        _run_propose(client, risk_mode=args.risk)
    elif args.mode == "execute_trade":
        if not args.params:
            _error("--params is required for execute_trade mode")
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as exc:
            _error(f"Invalid JSON in --params: {exc}")
        _run_execute_trade(client, params)
    elif args.mode == "dividends":
        _run_dividends(client)
    elif args.mode == "history":
        params = None
        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as exc:
                _error(f"Invalid JSON in --params: {exc}")
        _run_history(client, params)
    elif args.mode == "watchlist":
        _run_watchlist(client)
    elif args.mode == "allocation":
        _run_allocation(client, rebalance=args.rebalance)


if __name__ == "__main__":
    main()
