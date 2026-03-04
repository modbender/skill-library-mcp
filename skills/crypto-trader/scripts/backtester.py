"""
Backtester -- historical strategy testing framework.

Fetches historical OHLCV data from exchanges via CCXT, simulates strategy
execution with realistic slippage and fees, and reports performance metrics.
Results are saved to data/backtests/ for later comparison.
"""
from __future__ import annotations

import json
import logging
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger("crypto-trader.backtester")

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_BACKTESTS_DIR = _PROJECT_ROOT / "data" / "backtests"


class SimulatedOrder:
    """Represents a simulated order during backtesting."""

    def __init__(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        timestamp: int,
        fee_pct: float = 0.1,
    ) -> None:
        self.symbol = symbol
        self.side = side
        self.amount = amount
        self.price = price
        self.timestamp = timestamp
        self.fee_pct = fee_pct
        self.fee = (amount * price) * (fee_pct / 100)
        self.cost = amount * price

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "amount": self.amount,
            "price": self.price,
            "cost": round(self.cost, 2),
            "fee": round(self.fee, 4),
            "timestamp": self.timestamp,
        }


class Backtester:
    """Run historical backtests for trading strategies."""

    def __init__(
        self,
        exchange_manager: Any,
        slippage_pct: float = 0.05,
        fee_pct: float = 0.1,
        initial_balance: float = 1000.0,
    ) -> None:
        self.exchange_manager = exchange_manager
        self.slippage_pct = slippage_pct
        self.fee_pct = fee_pct
        self.initial_balance = initial_balance

    def run(
        self,
        strategy_name: str,
        params: Dict[str, Any],
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """Run a backtest for the given strategy and date range.

        Returns a results dict with performance metrics.
        """
        symbol = params.get("symbol", "BTC/USDT")
        timeframe = params.get("timeframe", "1h")
        exchange_name = params.get("exchange", "")

        if not exchange_name:
            available = self.exchange_manager.available_exchanges
            if available:
                exchange_name = available[0]
            else:
                return {"status": "error", "message": "No exchanges available for data."}

        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)

        logger.info("Fetching historical data for %s from %s to %s...", symbol, start_date, end_date)
        ohlcv_data = self._fetch_historical_data(exchange_name, symbol, timeframe, start_ts, end_ts)

        if len(ohlcv_data) < 50:
            return {
                "status": "error",
                "message": f"Not enough historical data: {len(ohlcv_data)} candles (need at least 50).",
            }

        logger.info("Running backtest with %d candles...", len(ohlcv_data))

        if strategy_name == "grid_trading":
            results = self._backtest_grid(ohlcv_data, params)
        elif strategy_name == "dca":
            results = self._backtest_dca(ohlcv_data, params)
        elif strategy_name in ("trend_following", "trend"):
            results = self._backtest_trend(ohlcv_data, params)
        else:
            return {
                "status": "error",
                "message": f"Backtest not implemented for strategy: {strategy_name}",
            }

        results["strategy"] = strategy_name
        results["symbol"] = symbol
        results["timeframe"] = timeframe
        results["start_date"] = start_date
        results["end_date"] = end_date
        results["candles"] = len(ohlcv_data)
        results["initial_balance_usdt"] = self.initial_balance
        results["slippage_pct"] = self.slippage_pct
        results["fee_pct"] = self.fee_pct

        self._save_results(results, strategy_name)

        return {"status": "ok", **results}

    def _fetch_historical_data(
        self, exchange_name: str, symbol: str, timeframe: str,
        start_ts: int, end_ts: int,
    ) -> List[List[Any]]:
        """Fetch all OHLCV data between start and end timestamps."""
        all_data: List[List[Any]] = []
        current_ts = start_ts

        while current_ts < end_ts:
            try:
                batch = self.exchange_manager.get_ohlcv(
                    exchange_name, symbol, timeframe, limit=1000, since=current_ts,
                )
            except Exception as exc:
                logger.error("Failed to fetch OHLCV batch: %s", exc)
                break

            if not batch:
                break

            for candle in batch:
                if candle[0] <= end_ts:
                    all_data.append(candle)

            last_ts = batch[-1][0]
            if last_ts <= current_ts:
                break
            current_ts = last_ts + 1

        return all_data

    # ------------------------------------------------------------------
    # Strategy-specific backtests
    # ------------------------------------------------------------------

    def _backtest_grid(self, ohlcv: List[List[Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate grid trading on historical data."""
        price_range = params.get("price_range", [0, 0])
        num_grids = params.get("num_grids", 10)
        order_amount = params.get("order_amount_usdt", 10.0)

        lower = price_range[0]
        upper = price_range[1]
        spacing = (upper - lower) / num_grids
        grid_levels = [round(lower + i * spacing, 2) for i in range(num_grids + 1)]

        balance_usdt = self.initial_balance
        balance_crypto = 0.0
        orders: List[Dict[str, Any]] = []
        total_fees = 0.0
        wins = 0
        losses = 0

        bought_at: Dict[str, float] = {}

        for candle in ohlcv:
            ts, o, h, l, c, v = candle
            for level in grid_levels:
                if l <= level <= h:
                    slipped_price = level * (1 + self.slippage_pct / 100)
                    level_key = f"{level:.2f}"

                    if level < c and balance_usdt >= order_amount:
                        amount = order_amount / slipped_price
                        fee = order_amount * (self.fee_pct / 100)
                        balance_usdt -= (order_amount + fee)
                        balance_crypto += amount
                        total_fees += fee
                        bought_at[level_key] = slipped_price
                        orders.append(SimulatedOrder(
                            params.get("symbol", "BTC/USDT"), "buy",
                            amount, slipped_price, ts, self.fee_pct,
                        ).to_dict())

                    elif level > c and level_key in bought_at:
                        entry = bought_at.pop(level_key)
                        sell_price = level * (1 - self.slippage_pct / 100)
                        amount = order_amount / entry
                        if balance_crypto >= amount:
                            revenue = amount * sell_price
                            fee = revenue * (self.fee_pct / 100)
                            balance_crypto -= amount
                            balance_usdt += (revenue - fee)
                            total_fees += fee
                            if sell_price > entry:
                                wins += 1
                            else:
                                losses += 1
                            orders.append(SimulatedOrder(
                                params.get("symbol", "BTC/USDT"), "sell",
                                amount, sell_price, ts, self.fee_pct,
                            ).to_dict())

        final_price = ohlcv[-1][4]
        final_value = balance_usdt + (balance_crypto * final_price)

        return self._compute_metrics(final_value, orders, total_fees, wins, losses, ohlcv)

    def _backtest_dca(self, ohlcv: List[List[Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate DCA on historical data."""
        amount_per_buy = params.get("amount_per_buy_usdt", 10.0)
        interval = params.get("interval", "daily")

        interval_candles = {"hourly": 1, "daily": 24, "weekly": 168, "monthly": 720}
        skip = interval_candles.get(interval, 24)

        balance_usdt = self.initial_balance
        balance_crypto = 0.0
        orders: List[Dict[str, Any]] = []
        total_fees = 0.0
        total_invested = 0.0

        for i in range(0, len(ohlcv), skip):
            candle = ohlcv[i]
            ts, o, h, l, c, v = candle
            price = c * (1 + self.slippage_pct / 100)

            if balance_usdt >= amount_per_buy:
                amount = amount_per_buy / price
                fee = amount_per_buy * (self.fee_pct / 100)
                balance_usdt -= (amount_per_buy + fee)
                balance_crypto += amount
                total_fees += fee
                total_invested += amount_per_buy
                orders.append(SimulatedOrder(
                    params.get("symbol", "BTC/USDT"), "buy",
                    amount, price, ts, self.fee_pct,
                ).to_dict())

        final_price = ohlcv[-1][4]
        final_value = balance_usdt + (balance_crypto * final_price)

        metrics = self._compute_metrics(final_value, orders, total_fees, len(orders), 0, ohlcv)
        metrics["total_invested_usdt"] = round(total_invested, 2)
        metrics["total_crypto_bought"] = round(balance_crypto, 8)
        if balance_crypto > 0:
            metrics["avg_buy_price"] = round(total_invested / balance_crypto, 2)
        return metrics

    def _backtest_trend(self, ohlcv: List[List[Any]], params: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate trend following on historical data."""
        ema_short_p = params.get("ema_short", 9)
        ema_long_p = params.get("ema_long", 21)
        rsi_period = params.get("rsi_period", 14)
        rsi_overbought = params.get("rsi_overbought", 70)
        order_amount = params.get("order_amount_usdt", 25.0)

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["ema_short"] = df["close"].ewm(span=ema_short_p, adjust=False).mean()
        df["ema_long"] = df["close"].ewm(span=ema_long_p, adjust=False).mean()

        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
        avg_loss = loss.ewm(com=rsi_period - 1, min_periods=rsi_period).mean()
        rs = avg_gain / avg_loss.replace(0, float("inf"))
        df["rsi"] = 100.0 - (100.0 / (1.0 + rs))

        balance_usdt = self.initial_balance
        balance_crypto = 0.0
        orders: List[Dict[str, Any]] = []
        total_fees = 0.0
        wins = 0
        losses = 0
        position = None
        entry_price = 0.0

        for i in range(max(ema_long_p, rsi_period) + 1, len(df)):
            row = df.iloc[i]
            prev = df.iloc[i - 1]
            price = row["close"]
            ts = int(row["timestamp"])

            bullish_cross = prev["ema_short"] <= prev["ema_long"] and row["ema_short"] > row["ema_long"]
            bearish_cross = prev["ema_short"] >= prev["ema_long"] and row["ema_short"] < row["ema_long"]

            if bullish_cross and row["rsi"] < rsi_overbought and position is None:
                buy_price = price * (1 + self.slippage_pct / 100)
                if balance_usdt >= order_amount:
                    amount = order_amount / buy_price
                    fee = order_amount * (self.fee_pct / 100)
                    balance_usdt -= (order_amount + fee)
                    balance_crypto += amount
                    total_fees += fee
                    position = "long"
                    entry_price = buy_price
                    orders.append(SimulatedOrder(
                        params.get("symbol", "BTC/USDT"), "buy",
                        amount, buy_price, ts, self.fee_pct,
                    ).to_dict())

            elif (bearish_cross or row["rsi"] > rsi_overbought) and position == "long":
                sell_price = price * (1 - self.slippage_pct / 100)
                if balance_crypto > 0:
                    revenue = balance_crypto * sell_price
                    fee = revenue * (self.fee_pct / 100)
                    balance_usdt += (revenue - fee)
                    total_fees += fee
                    if sell_price > entry_price:
                        wins += 1
                    else:
                        losses += 1
                    orders.append(SimulatedOrder(
                        params.get("symbol", "BTC/USDT"), "sell",
                        balance_crypto, sell_price, ts, self.fee_pct,
                    ).to_dict())
                    balance_crypto = 0.0
                    position = None

        final_price = ohlcv[-1][4]
        final_value = balance_usdt + (balance_crypto * final_price)
        return self._compute_metrics(final_value, orders, total_fees, wins, losses, ohlcv)

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def _compute_metrics(
        self,
        final_value: float,
        orders: List[Dict[str, Any]],
        total_fees: float,
        wins: int,
        losses: int,
        ohlcv: List[List[Any]],
    ) -> Dict[str, Any]:
        """Compute performance metrics from backtest results."""
        total_return_pct = ((final_value - self.initial_balance) / self.initial_balance) * 100

        buy_and_hold_start = ohlcv[0][4]
        buy_and_hold_end = ohlcv[-1][4]
        buy_and_hold_return = ((buy_and_hold_end - buy_and_hold_start) / buy_and_hold_start) * 100

        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

        equity_curve = [self.initial_balance]
        running = self.initial_balance
        for order in orders:
            if order["side"] == "buy":
                running -= order["cost"]
            else:
                running += order["cost"]
            equity_curve.append(running)

        max_drawdown = 0.0
        peak = equity_curve[0]
        for val in equity_curve:
            if val > peak:
                peak = val
            dd = ((peak - val) / peak) * 100 if peak > 0 else 0
            if dd > max_drawdown:
                max_drawdown = dd

        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i - 1] > 0:
                r = (equity_curve[i] - equity_curve[i - 1]) / equity_curve[i - 1]
                returns.append(r)

        sharpe = 0.0
        if returns:
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            if std_return > 0:
                sharpe = (avg_return / std_return) * (252 ** 0.5)

        return {
            "final_value_usdt": round(final_value, 2),
            "total_return_pct": round(total_return_pct, 2),
            "buy_and_hold_return_pct": round(buy_and_hold_return, 2),
            "total_trades": total_trades,
            "wins": wins,
            "losses": losses,
            "win_rate_pct": round(win_rate, 1),
            "total_fees_usdt": round(total_fees, 2),
            "max_drawdown_pct": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe, 2),
            "orders": orders[:100],
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_results(self, results: Dict[str, Any], strategy_name: str) -> None:
        """Save backtest results to disk."""
        _BACKTESTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_{ts}.json"
        path = _BACKTESTS_DIR / filename
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2, default=str)
        logger.info("Backtest results saved to %s", path)
