"""Vynn backtester plugin for OpenClaw.

Run trading strategy backtests with natural language or structured
entry/exit rules. Returns Sharpe ratio, returns, drawdown, win rate,
and equity curves via the Vynn API.

Free tier: 10 backtests/month. Pro: unlimited at $29/month.
Get a key at https://the-vynn.com
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


VYNN_BASE_URL = os.getenv("VYNN_BASE_URL", "https://the-vynn.com/v1")


@dataclass
class BacktestResult:
    """Structured result from a Vynn backtest run."""

    strategy: str
    tickers: List[str]
    sharpe_ratio: float
    total_return_pct: float
    max_drawdown_pct: float
    win_rate_pct: float
    total_trades: int
    period: str
    status: str

    def summary(self) -> str:
        """Human-readable one-line summary."""
        tickers_str = ", ".join(self.tickers)
        return (
            f"{self.strategy} on {tickers_str} | "
            f"Sharpe {self.sharpe_ratio:.2f} | "
            f"Return {self.total_return_pct:+.1f}% | "
            f"Drawdown {self.max_drawdown_pct:.1f}% | "
            f"Win rate {self.win_rate_pct:.0f}% | "
            f"{self.total_trades} trades | {self.period}"
        )


class VynnBacktesterPlugin:
    """OpenClaw plugin that runs trading backtests via the Vynn API.

    Accepts natural language strategy descriptions or structured JSON
    with explicit entry/exit rules. Returns full performance metrics.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("VYNN_API_KEY", "")
        self.base_url = VYNN_BASE_URL.rstrip("/")
        self.run_count = 0

        if not self.api_key:
            raise ValueError(
                "VYNN_API_KEY is required. "
                "Get a free key (10 backtests/month): "
                "POST https://the-vynn.com/v1/signup with {\"email\": \"you@example.com\"}"
            )

    def _post(self, endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Make an authenticated POST request to the Vynn API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            status = exc.code
            try:
                detail = json.loads(exc.read().decode("utf-8"))
                msg = detail.get("detail", detail.get("message", str(detail)))
            except Exception:
                msg = exc.reason

            if status == 401:
                raise PermissionError(
                    f"Invalid or expired VYNN_API_KEY. "
                    f"Get a new key at https://the-vynn.com ({msg})"
                ) from exc
            elif status == 429:
                raise RuntimeError(
                    f"Rate limit reached. Free tier allows 10 backtests/month. "
                    f"Upgrade to Pro at https://the-vynn.com for unlimited. ({msg})"
                ) from exc
            elif status >= 500:
                raise RuntimeError(
                    f"Vynn server error ({status}): {msg}. "
                    f"Try again shortly or check https://the-vynn.com/status"
                ) from exc
            else:
                raise RuntimeError(
                    f"Vynn API error ({status}): {msg}"
                ) from exc
        except urllib.error.URLError as exc:
            raise ConnectionError(
                f"Could not reach Vynn API at {url}: {exc.reason}"
            ) from exc

    def backtest(
        self,
        strategy: str,
        tickers: Optional[List[str]] = None,
        lookback_years: int = 2,
    ) -> BacktestResult:
        """Run a single strategy backtest.

        Args:
            strategy: Natural language description (e.g. "RSI mean reversion")
                      or a JSON string with {"entries": [...], "exits": [...]}.
            tickers: List of ticker symbols. Defaults to ["SPY"].
            lookback_years: Number of years of historical data. Defaults to 2.

        Returns:
            BacktestResult with full performance metrics.
        """
        if tickers is None:
            tickers = ["SPY"]

        body = {
            "strategy": strategy,
            "tickers": tickers,
            "lookback_years": lookback_years,
        }

        resp = self._post("backtest", body)
        self.run_count += 1

        return BacktestResult(
            strategy=resp.get("strategy", strategy),
            tickers=resp.get("tickers", tickers),
            sharpe_ratio=float(resp.get("sharpe_ratio", 0.0)),
            total_return_pct=float(resp.get("total_return_pct", 0.0)),
            max_drawdown_pct=float(resp.get("max_drawdown_pct", 0.0)),
            win_rate_pct=float(resp.get("win_rate_pct", 0.0)),
            total_trades=int(resp.get("total_trades", 0)),
            period=resp.get("period", f"{lookback_years}Y"),
            status=resp.get("status", "completed"),
        )

    def compare(
        self,
        strategies: List[str],
        tickers: Optional[List[str]] = None,
        lookback_years: int = 2,
    ) -> List[BacktestResult]:
        """Run multiple backtests and return results sorted by Sharpe ratio.

        Args:
            strategies: List of strategy descriptions to compare.
            tickers: Ticker symbols (shared across all strategies).
            lookback_years: Lookback period in years.

        Returns:
            List of BacktestResult, sorted by Sharpe ratio descending.
        """
        results: List[BacktestResult] = []
        for strat in strategies:
            result = self.backtest(
                strategy=strat,
                tickers=tickers,
                lookback_years=lookback_years,
            )
            results.append(result)

        results.sort(key=lambda r: r.sharpe_ratio, reverse=True)
        return results

    def status(self) -> Dict[str, Any]:
        """Return current plugin status and usage stats."""
        return {
            "status": "active",
            "api_url": self.base_url,
            "backtests_run": self.run_count,
        }
