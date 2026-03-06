"""Futu OpenAPI adapter (quotes + healthcheck only).

Notes:
- No order placement.
- Designed to fail gracefully when permissions or OpenD are missing.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

try:
    from futu import OpenQuoteContext, RET_OK
except Exception as exc:  # pragma: no cover - import error surfaced at runtime
    OpenQuoteContext = None  # type: ignore
    RET_OK = 0  # type: ignore
    _FUTU_IMPORT_ERROR = exc
else:
    _FUTU_IMPORT_ERROR = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FutuAdapter:
    def __init__(self, host: str, port: int, market: str = "US") -> None:
        self.host = host
        self.port = int(port)
        self.market = (market or "US").upper()
        self._quote_ctx = None

    def _ensure_ctx(self) -> None:
        if self._quote_ctx is not None:
            return
        if OpenQuoteContext is None:
            raise RuntimeError(
                "futu-api is not installed. Install with: pip install futu-api"
            ) from _FUTU_IMPORT_ERROR
        # Avoid long hangs when OpenD is down by disabling auto-reconnect.
        # If futu-api changes signature, fall back gracefully.
        try:
            self._quote_ctx = OpenQuoteContext(host=self.host, port=self.port, is_encrypt=False)
        except TypeError:
            self._quote_ctx = OpenQuoteContext(host=self.host, port=self.port)

    def _normalize_code(self, ticker: str) -> str:
        if not ticker:
            return ticker
        if "." in ticker:
            return ticker
        return f"{self.market}.{ticker}"

    def healthcheck(self, timeout_s: float = 2.0) -> Dict[str, Any]:
        start = time.perf_counter()
        timestamp = _utc_now_iso()
        result: Dict[str, Any] = {
            "ok": False,
            "latency_ms": None,
            "source": "futu",
            "timestamp": timestamp,
        }
        try:
            # Fast-fail: if OpenD isn't listening, don't let futu-api retry for ~minutes.
            if not _tcp_ping(self.host, self.port, timeout_s=timeout_s):
                raise RuntimeError(
                    f"OpenD not reachable at {self.host}:{self.port} (connection refused/timeout)."
                )
            self._ensure_ctx()
            server_info: Optional[Dict[str, Any]] = None
            # Prefer lightweight endpoints if available.
            if hasattr(self._quote_ctx, "get_global_state"):
                ret, data = self._quote_ctx.get_global_state()
                if ret == RET_OK:
                    server_info = _to_dict(data)
                else:
                    raise RuntimeError(str(data))
            elif hasattr(self._quote_ctx, "get_server_info"):
                ret, data = self._quote_ctx.get_server_info()
                if ret == RET_OK:
                    server_info = _to_dict(data)
                else:
                    raise RuntimeError(str(data))
            else:
                # Fallback: request basic stock info to validate connectivity.
                ret, data = self._quote_ctx.get_stock_basicinfo(
                    market=self.market, stock_type="STOCK"
                )
                if ret == RET_OK:
                    server_info = {"market": self.market, "rows": len(data)}
                else:
                    raise RuntimeError(str(data))

            result["ok"] = True
            if server_info is not None:
                result["server_info"] = server_info
        except Exception as exc:  # pragma: no cover - depends on runtime env
            result["error"] = f"Futu OpenD healthcheck failed: {exc}"
        finally:
            result["latency_ms"] = round((time.perf_counter() - start) * 1000, 2)
        return result

    def get_quotes(self, tickers: Iterable[str]) -> List[Dict[str, Any]]:
        tickers_list = list(tickers or [])
        timestamp = _utc_now_iso()
        if not tickers_list:
            return []
        try:
            self._ensure_ctx()
            codes = [self._normalize_code(t) for t in tickers_list]
            ret, data = self._quote_ctx.get_market_snapshot(codes)
            if ret != RET_OK:
                raise RuntimeError(str(data))

            rows = _frame_to_rows(data)
            by_code = {row.get("code") or row.get("ticker") or row.get("symbol"): row for row in rows}

            results: List[Dict[str, Any]] = []
            for ticker, code in zip(tickers_list, codes):
                row = by_code.get(code)
                if not row:
                    results.append(
                        {
                            "ticker": ticker,
                            "price": None,
                            "day_range": None,
                            "timestamp": timestamp,
                            "source": "futu",
                            "error": "No snapshot data returned for ticker",
                        }
                    )
                    continue
                price = _pick_first(row, ["last_price", "price", "last"])
                low = _pick_first(row, ["low_price", "low"])
                high = _pick_first(row, ["high_price", "high"])
                day_range = None
                if low is not None or high is not None:
                    day_range = {"low": low, "high": high}

                quote_ts = _pick_first(
                    row,
                    [
                        "update_time",
                        "data_time",
                        "time",
                        "quote_time",
                    ],
                ) or timestamp

                results.append(
                    {
                        "ticker": ticker,
                        "price": price,
                        "day_range": day_range,
                        "timestamp": quote_ts,
                        "source": "futu",
                    }
                )
            return results
        except Exception as exc:  # pragma: no cover - depends on runtime env
            error_msg = f"Futu OpenD quote fetch failed: {exc}"
            return [
                {
                    "ticker": ticker,
                    "price": None,
                    "day_range": None,
                    "timestamp": timestamp,
                    "source": "futu",
                    "error": error_msg,
                }
                for ticker in tickers_list
            ]

    def get_options_chain_summary(
        self, ticker: str, dte_min: int = 30, dte_max: int = 45
    ) -> Dict[str, Any]:
        """Best-effort options chain summary.

        We keep this lightweight and permission-tolerant:
        - If the relevant Futu endpoints are unavailable or permission is missing,
          we return a structured summary with an error field instead of raising.

        Output fields align with Data.snapshot.options_chain_summary entry.
        """
        timestamp = _utc_now_iso()
        code = self._normalize_code(ticker)
        summary: Dict[str, Any] = {
            "ticker": ticker,
            "dte": {"min": int(dte_min), "max": int(dte_max)},
            "atm_iv": None,
            "put_skew_note": None,
            "bid_ask_spread_typical": None,
            "oi_volume_note": None,
            "source": "futu",
            "timestamp": timestamp,
        }
        try:
            self._ensure_ctx()

            if not hasattr(self._quote_ctx, "get_option_chain"):
                summary["error"] = "get_option_chain not available in this futu-api version"
                summary["put_skew_note"] = "unknown"
                summary["bid_ask_spread_typical"] = "unknown"
                return summary

            # 1) Get option contract list in DTE window
            from datetime import date, timedelta

            start = (date.today() + timedelta(days=int(dte_min))).strftime("%Y-%m-%d")
            end = (date.today() + timedelta(days=int(dte_max))).strftime("%Y-%m-%d")
            ret, chain = self._quote_ctx.get_option_chain(code, start=start, end=end)
            if ret != RET_OK:
                summary["error"] = f"get_option_chain failed: {chain}"
                summary["put_skew_note"] = "unknown"
                summary["bid_ask_spread_typical"] = "unknown"
                return summary

            if chain is None or getattr(chain, "empty", True):
                summary["error"] = "option chain empty"
                summary["put_skew_note"] = "unknown"
                summary["bid_ask_spread_typical"] = "unknown"
                return summary

            # Choose expiry closest to mid of window
            target_dte = (int(dte_min) + int(dte_max)) / 2
            # strike_time column is expiry date for options
            exp_dates = sorted(set(chain["strike_time"].astype(str).tolist()))
            chosen_exp = None
            best_diff = 10**9
            for exp in exp_dates:
                try:
                    y, m, d = exp.split("-")
                    dd = (date(int(y), int(m), int(d)) - date.today()).days
                    diff = abs(dd - target_dte)
                    if diff < best_diff:
                        best_diff = diff
                        chosen_exp = exp
                except Exception:
                    continue
            chosen_exp = chosen_exp or exp_dates[0]
            summary["dte"] = chosen_exp

            chain_exp = chain[chain["strike_time"].astype(str) == str(chosen_exp)]
            codes = chain_exp["code"].astype(str).tolist()

            # 2) Market snapshot for those option codes
            ret2, snap = self._quote_ctx.get_market_snapshot(codes)
            if ret2 != RET_OK:
                summary["error"] = f"get_market_snapshot failed: {snap}"
                summary["put_skew_note"] = "unknown"
                summary["bid_ask_spread_typical"] = "unknown"
                return summary

            # 3) Compute metrics (best-effort)
            # spot: try snapshot stock_owner is available, but easiest: quote stock_owner via get_market_snapshot
            spot = None
            try:
                ret_spot, spot_snap = self._quote_ctx.get_market_snapshot([code])
                if ret_spot == RET_OK and spot_snap is not None and not spot_snap.empty:
                    lp = spot_snap.iloc[0].get("last_price")
                    spot = float(lp) if lp is not None else None
            except Exception:
                spot = None
            if spot is None:
                # Fallback to public yfinance to enable ATM/skew computation when broker spot is missing.
                try:
                    from invest_agent.integrations.public.yfinance_fallback import get_quote as _yq

                    q = _yq(ticker)
                    spot = float(q.get("price")) if q.get("price") is not None else None
                except Exception:
                    spot = None

            # Typical spread: median ask-bid for options with reasonable delta range
            try:
                df = snap.copy()
                if "ask_price" in df.columns and "bid_price" in df.columns:
                    df = df[(df["ask_price"].notna()) & (df["bid_price"].notna())]
                    df["spread"] = (df["ask_price"].astype(float) - df["bid_price"].astype(float))
                    if "option_delta" in df.columns:
                        # focus on tradable deltas
                        d = df["option_delta"].astype(float)
                        df = df[(d.abs() >= 0.1) & (d.abs() <= 0.4)]
                    spread_med = float(df["spread"].median()) if not df.empty else None
                else:
                    spread_med = None
            except Exception:
                spread_med = None
            summary["bid_ask_spread_typical"] = spread_med

            # OI/volume notes
            try:
                oi_sum = int(snap.get("option_open_interest").fillna(0).astype(float).sum()) if "option_open_interest" in snap.columns else None
                vol_sum = int(snap.get("volume").fillna(0).astype(float).sum()) if "volume" in snap.columns else None
                summary["oi_volume_note"] = f"OI_sum={oi_sum}, vol_sum={vol_sum}"
            except Exception:
                summary["oi_volume_note"] = "unknown"

            # ATM IV (nearest strike to spot) + skew (delta25 put - delta25 call)
            atm_iv = None
            skew = None
            try:
                if spot is not None and "option_strike_price" in snap.columns and "option_implied_volatility" in snap.columns:
                    df = snap.copy()
                    df = df[df["option_implied_volatility"].notna()]
                    df["k"] = df["option_strike_price"].astype(float)
                    df["iv"] = df["option_implied_volatility"].astype(float)
                    # ATM strike
                    df["dist"] = (df["k"] - float(spot)).abs()
                    atm_row = df.sort_values("dist").head(1)
                    if not atm_row.empty:
                        atm_iv = float(atm_row.iloc[0]["iv"])

                    if "option_delta" in df.columns and "option_type" in df.columns:
                        df["delta"] = df["option_delta"].astype(float)
                        puts = df[df["option_type"].astype(str).str.upper() == "PUT"]
                        calls = df[df["option_type"].astype(str).str.upper() == "CALL"]
                        put25 = puts.iloc[(puts["delta"] + 0.25).abs().argsort()[:1]] if not puts.empty else None
                        call25 = calls.iloc[(calls["delta"] - 0.25).abs().argsort()[:1]] if not calls.empty else None
                        if put25 is not None and call25 is not None and not put25.empty and not call25.empty:
                            skew = float(put25.iloc[0]["iv"] - call25.iloc[0]["iv"])
            except Exception:
                pass

            summary["atm_iv"] = atm_iv
            summary["put_skew_note"] = (
                f"delta25_put_minus_call_iv={skew:.4f}" if skew is not None else "unknown"
            )

        except Exception as exc:  # pragma: no cover
            summary["error"] = f"Options summary failed: {exc}"
            summary.setdefault("put_skew_note", "unknown")
            summary.setdefault("bid_ask_spread_typical", "unknown")
        return summary

    def close(self) -> None:
        if self._quote_ctx is not None:
            try:
                self._quote_ctx.close()
            finally:
                self._quote_ctx = None


def _tcp_ping(host: str, port: int, timeout_s: float = 2.0) -> bool:
    import socket

    try:
        with socket.create_connection((host, int(port)), timeout=timeout_s):
            return True
    except OSError:
        return False


def _to_dict(data: Any) -> Dict[str, Any]:
    if isinstance(data, dict):
        return data
    try:
        return data.to_dict()  # type: ignore[no-any-return]
    except Exception:
        return {"data": str(data)}


def _frame_to_rows(data: Any) -> List[Dict[str, Any]]:
    if data is None:
        return []
    if isinstance(data, list):
        return [row if isinstance(row, dict) else {"data": row} for row in data]
    if isinstance(data, dict):
        return [data]
    try:
        return data.to_dict(orient="records")  # type: ignore[no-any-return]
    except Exception:
        return []


def _pick_first(row: Dict[str, Any], keys: List[str]) -> Any:
    for key in keys:
        if key in row and row[key] is not None:
            return row[key]
    return None


def load_from_env() -> "FutuAdapter":
    host = os.getenv("FUTU_OPEND_HOST", "127.0.0.1")
    port = int(os.getenv("FUTU_OPEND_PORT", "11111"))
    market = os.getenv("FUTU_MARKET", "US")
    return FutuAdapter(host=host, port=port, market=market)
