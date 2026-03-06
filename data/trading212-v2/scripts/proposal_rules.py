"""
Rule engine for generating trade proposals.

Rules are driven by ``config/rules.yaml``.  Each rule is a simple callable
that inspects a position (+ portfolio context) and optionally returns a
proposal dict.  New rules can be added by appending to ``RULES``.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

# ------------------------------------------------------------------
# Config loading
# ------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "rules.yaml"

RISK_MULTIPLIERS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 1.00,
}


def _load_config() -> Dict[str, Any]:
    path = Path(os.environ.get("TRADING212_RULES_PATH", str(_CONFIG_PATH)))
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("proposal_rules", {})


# ------------------------------------------------------------------
# Rule type
# ------------------------------------------------------------------

# A rule function receives the position dict, the full portfolio context,
# and the loaded config.  It returns a proposal dict or None.
RuleFn = Callable[
    [Dict[str, Any], Dict[str, Any], Dict[str, Any]],
    Optional[Dict[str, Any]],
]


# ------------------------------------------------------------------
# Individual rules
# ------------------------------------------------------------------


def rule_reduce_on_drop(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Propose reducing a position that dropped significantly today and
    has a large portfolio weight."""
    drop_threshold = cfg.get("drop_threshold_pct", 3.0)
    min_weight = cfg.get("min_weight_pct", 5.0)
    risk_mult = ctx["risk_multiplier"]

    daily_pct = pos.get("daily_change_pct")
    if daily_pct is None:
        return None

    total_value = ctx["total_value"]
    if total_value <= 0:
        return None

    weight_pct = (pos["value"] / total_value) * 100

    if daily_pct <= -drop_threshold and weight_pct >= min_weight:
        reduce_qty = math.floor(pos["quantity"] * risk_mult)
        if reduce_qty < 1:
            reduce_qty = 1
        reduce_qty = min(reduce_qty, pos["quantity"])
        return {
            "symbol": pos["ticker"],
            "action": "reduce",
            "quantity": reduce_qty,
            "reason": (
                f"Position dropped {abs(daily_pct):.1f}% today and represents "
                f"{weight_pct:.1f}% of portfolio (threshold: -{drop_threshold}% / "
                f"{min_weight}% weight). Suggesting to sell {reduce_qty} shares."
            ),
        }
    return None


def rule_take_profit(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Propose taking profit on a small position that is up significantly."""
    small_pct = cfg.get("small_position_pct", 2.0)
    min_gain = cfg.get("min_gain_pct", 5.0)
    risk_mult = ctx["risk_multiplier"]

    total_value = ctx["total_value"]
    if total_value <= 0:
        return None

    weight_pct = (pos["value"] / total_value) * 100
    total_cost = pos.get("total_cost", 0)
    if total_cost <= 0:
        return None

    gain_pct = ((pos["value"] - total_cost) / total_cost) * 100

    if weight_pct < small_pct and gain_pct >= min_gain:
        sell_qty = math.floor(pos["quantity"] * risk_mult)
        if sell_qty < 1:
            sell_qty = 1
        sell_qty = min(sell_qty, pos["quantity"])
        return {
            "symbol": pos["ticker"],
            "action": "sell",
            "quantity": sell_qty,
            "reason": (
                f"Small position ({weight_pct:.1f}% of portfolio) with "
                f"{gain_pct:.1f}% unrealised gain. Suggesting to take profit "
                f"on {sell_qty} shares."
            ),
        }
    return None


def rule_dca_buy(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Propose a DCA buy if enough cash is available and the ticker is on
    the DCA list.  This rule only fires once per ticker (tracked via
    ``ctx['dca_proposed']``)."""
    dca_tickers: List[str] = cfg.get("dca_tickers", [])
    dca_min_cash: float = cfg.get("dca_min_cash", 100.0)
    dca_amount: float = cfg.get("dca_amount", 50.0)

    # This rule is not position-specific; we attach it to the first
    # matching position we encounter.
    ticker = pos["ticker"]
    if ticker not in dca_tickers:
        return None
    if ctx["cash"] < dca_min_cash:
        return None
    if ticker in ctx.get("dca_proposed", set()):
        return None

    current_price = pos.get("current_price", 0)
    if current_price <= 0:
        return None

    buy_qty = math.floor(dca_amount / current_price)
    if buy_qty < 1:
        # Fractional shares are supported on Trading212.
        buy_qty_frac = round(dca_amount / current_price, 4)
        if buy_qty_frac <= 0:
            return None
        buy_qty = buy_qty_frac

    ctx.setdefault("dca_proposed", set()).add(ticker)

    return {
        "symbol": ticker,
        "action": "buy",
        "quantity": buy_qty,
        "reason": (
            f"DCA buy: {ticker} is on your DCA list.  Cash available "
            f"({ctx['cash']:.2f}) exceeds minimum ({dca_min_cash:.2f}).  "
            f"Suggesting to buy ~{dca_amount:.2f} worth ({buy_qty} shares at "
            f"{current_price:.2f})."
        ),
    }


# ------------------------------------------------------------------
# NEW: Stop-loss rule
# ------------------------------------------------------------------


def rule_stop_loss(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Propose selling a position that has dropped below the stop-loss
    threshold relative to the average purchase price."""
    stop_loss_pct = cfg.get("stop_loss_pct", 10.0)
    risk_mult = ctx["risk_multiplier"]

    avg_price = pos.get("avg_price", 0)
    current_price = pos.get("current_price", 0)
    if avg_price <= 0 or current_price <= 0:
        return None

    drop_pct = ((avg_price - current_price) / avg_price) * 100

    if drop_pct >= stop_loss_pct:
        sell_qty = math.ceil(pos["quantity"] * risk_mult)
        sell_qty = min(sell_qty, pos["quantity"])
        if sell_qty <= 0:
            sell_qty = pos["quantity"]
        return {
            "symbol": pos["ticker"],
            "action": "sell",
            "quantity": sell_qty,
            "reason": (
                f"Stop-loss: current price ({current_price:.2f}) is "
                f"{drop_pct:.1f}% below average purchase price ({avg_price:.2f}). "
                f"Threshold: {stop_loss_pct}%. "
                f"Suggesting to sell {sell_qty} of {pos['quantity']} shares."
            ),
        }
    return None


# ------------------------------------------------------------------
# NEW: Max exposure rule
# ------------------------------------------------------------------


def rule_max_exposure(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Propose reducing a position that exceeds the maximum allowed
    portfolio weight."""
    max_exposure_pct = cfg.get("max_exposure_pct", 20.0)
    target_pct = cfg.get("max_exposure_target_pct", 15.0)

    total_value = ctx["total_value"]
    if total_value <= 0:
        return None

    weight_pct = (pos["value"] / total_value) * 100

    if weight_pct > max_exposure_pct:
        # Calculate how many shares to sell to bring weight to target.
        target_value = (target_pct / 100.0) * total_value
        excess_value = pos["value"] - target_value
        current_price = pos.get("current_price", 0)

        if current_price <= 0 or excess_value <= 0:
            return None

        reduce_qty = math.floor(excess_value / current_price)
        if reduce_qty < 1:
            reduce_qty = 1
        reduce_qty = min(reduce_qty, pos["quantity"])

        return {
            "symbol": pos["ticker"],
            "action": "reduce",
            "quantity": reduce_qty,
            "reason": (
                f"Max exposure: {pos['ticker']} represents {weight_pct:.1f}% "
                f"of portfolio (max allowed: {max_exposure_pct}%). "
                f"Suggesting to reduce by {reduce_qty} shares to bring "
                f"weight closer to {target_pct}%."
            ),
        }
    return None


# ------------------------------------------------------------------
# NEW: Cost averaging rule
# ------------------------------------------------------------------


def rule_cost_avg_buy(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Propose buying more of a position whose current price is
    significantly below the average purchase price (cost averaging)."""
    threshold_pct = cfg.get("cost_avg_threshold_pct", 10.0)
    cost_avg_amount: float = cfg.get("cost_avg_amount", 50.0)
    cost_avg_tickers: List[str] = cfg.get("cost_avg_tickers", [])
    dca_min_cash: float = cfg.get("dca_min_cash", 100.0)

    ticker = pos["ticker"]

    # Only apply to tickers on the cost-avg list (if configured).
    if cost_avg_tickers and ticker not in cost_avg_tickers:
        return None

    # Skip if already proposed via this rule (tracked via context).
    if ticker in ctx.get("cost_avg_proposed", set()):
        return None

    avg_price = pos.get("avg_price", 0)
    current_price = pos.get("current_price", 0)
    if avg_price <= 0 or current_price <= 0:
        return None

    # Only trigger if the price has dropped below avg by the threshold.
    drop_pct = ((avg_price - current_price) / avg_price) * 100
    if drop_pct < threshold_pct:
        return None

    # Need enough cash.
    if ctx["cash"] < dca_min_cash:
        return None

    buy_qty = math.floor(cost_avg_amount / current_price)
    if buy_qty < 1:
        buy_qty_frac = round(cost_avg_amount / current_price, 4)
        if buy_qty_frac <= 0:
            return None
        buy_qty = buy_qty_frac

    ctx.setdefault("cost_avg_proposed", set()).add(ticker)

    return {
        "symbol": ticker,
        "action": "buy",
        "quantity": buy_qty,
        "reason": (
            f"Cost averaging: {ticker} current price ({current_price:.2f}) is "
            f"{drop_pct:.1f}% below average ({avg_price:.2f}). "
            f"Threshold: {threshold_pct}%. Cash available: {ctx['cash']:.2f}. "
            f"Suggesting to buy ~{cost_avg_amount:.2f} worth ({buy_qty} shares)."
        ),
    }


# ------------------------------------------------------------------
# NEW: Cash reserve rule
# ------------------------------------------------------------------


def rule_cash_reserve(
    pos: Dict[str, Any],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Warn when cash reserves fall below the configured minimum percentage
    of the total portfolio.  This is a portfolio-level rule that fires
    only once (tracked via ``ctx['cash_reserve_warned']``)."""
    cash_reserve_pct = cfg.get("cash_reserve_pct", 5.0)

    # Only fire once per proposal run.
    if ctx.get("cash_reserve_warned"):
        return None

    total_value = ctx["total_value"]
    if total_value <= 0:
        return None

    cash_pct = (ctx["cash"] / total_value) * 100

    if cash_pct < cash_reserve_pct:
        ctx["cash_reserve_warned"] = True

        # Suggest selling the smallest position to free up cash.
        positions = ctx.get("positions", [])
        if positions:
            smallest = min(positions, key=lambda p: p.get("value", 0))
            return {
                "symbol": smallest["ticker"],
                "action": "sell",
                "quantity": smallest.get("quantity", 0),
                "reason": (
                    f"Cash reserve warning: cash is {cash_pct:.1f}% of portfolio "
                    f"(minimum: {cash_reserve_pct}%). "
                    f"Consider selling smallest position ({smallest['ticker']}, "
                    f"value: {smallest.get('value', 0):.2f}) or depositing "
                    f"additional funds."
                ),
            }
        else:
            return {
                "symbol": "",
                "action": "hold",
                "quantity": 0,
                "reason": (
                    f"Cash reserve warning: cash is {cash_pct:.1f}% of portfolio "
                    f"(minimum: {cash_reserve_pct}%). "
                    f"Consider depositing additional funds."
                ),
            }
    return None


# ------------------------------------------------------------------
# DCA for tickers NOT currently in portfolio
# ------------------------------------------------------------------

def _dca_proposals_for_missing_tickers(
    positions: List[Dict[str, Any]],
    ctx: Dict[str, Any],
    cfg: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Generate DCA proposals for tickers on the DCA list that the user
    does not currently hold (so rule_dca_buy never fires for them)."""
    dca_tickers: List[str] = cfg.get("dca_tickers", [])
    dca_min_cash: float = cfg.get("dca_min_cash", 100.0)
    dca_amount: float = cfg.get("dca_amount", 50.0)

    held = {p["ticker"] for p in positions}
    proposals: List[Dict[str, Any]] = []

    for ticker in dca_tickers:
        if ticker in held:
            continue  # handled by rule_dca_buy
        if ticker in ctx.get("dca_proposed", set()):
            continue
        if ctx["cash"] < dca_min_cash:
            break

        ctx.setdefault("dca_proposed", set()).add(ticker)
        proposals.append({
            "symbol": ticker,
            "action": "buy",
            "quantity": None,  # Price unknown (not in portfolio); agent may look it up.
            "reason": (
                f"DCA buy: {ticker} is on your DCA list but you do not currently "
                f"hold it.  Cash ({ctx['cash']:.2f}) is above minimum "
                f"({dca_min_cash:.2f}).  Consider buying ~{dca_amount:.2f} worth."
            ),
        })

    return proposals


# ------------------------------------------------------------------
# Rule registry
# ------------------------------------------------------------------

RULES: List[RuleFn] = [
    rule_reduce_on_drop,
    rule_take_profit,
    rule_dca_buy,
    rule_stop_loss,
    rule_max_exposure,
    rule_cost_avg_buy,
    rule_cash_reserve,
]


# ------------------------------------------------------------------
# Public interface
# ------------------------------------------------------------------

def generate_proposals(
    positions: List[Dict[str, Any]],
    cash: float,
    total_value: float,
    risk_override: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Run all rules against every position and return a list of proposals.

    Parameters
    ----------
    positions:
        Normalised position dicts (as produced by the entrypoint).
    cash:
        Available cash.
    total_value:
        Portfolio total value.
    risk_override:
        If set, overrides the risk_mode from config.
    """
    cfg = _load_config()

    risk_mode = risk_override or cfg.get("risk_mode", "medium")
    risk_mult = RISK_MULTIPLIERS.get(risk_mode, 0.5)

    ctx: Dict[str, Any] = {
        "total_value": total_value,
        "cash": cash,
        "risk_mode": risk_mode,
        "risk_multiplier": risk_mult,
        "positions": positions,
    }

    proposals: List[Dict[str, Any]] = []

    for pos in positions:
        for rule_fn in RULES:
            proposal = rule_fn(pos, ctx, cfg)
            if proposal is not None:
                proposals.append(proposal)

    # DCA proposals for tickers not in the portfolio.
    proposals.extend(_dca_proposals_for_missing_tickers(positions, ctx, cfg))

    return proposals
