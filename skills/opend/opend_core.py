#!/usr/bin/env python3
"""Shared OpenD helpers for quote/trade scripts."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Optional

from credentials import get_password


def load_sdk():
    """Load moomoo/futu SDK with optional explicit path support."""
    sdk_path = os.getenv("OPEND_SDK_PATH")
    if sdk_path and sdk_path not in sys.path:
        print(
            "Warning: OPEND_SDK_PATH is set. Only load SDK code from a trusted location.",
            file=sys.stderr,
        )
        sys.path.insert(0, sdk_path)

    try:
        import moomoo as ft  # type: ignore

        return ft
    except Exception:
        pass

    try:
        import futu as ft  # type: ignore

        return ft
    except Exception as exc:
        raise RuntimeError(
            "Unable to import 'moomoo' or 'futu'. Install one SDK, or set OPEND_SDK_PATH."
        ) from exc


def _ret_ok(ft: Any, ret: Any) -> bool:
    return ret == getattr(ft, "RET_OK", 0)


def as_records(data: Any) -> Any:
    if hasattr(data, "to_dict"):
        try:
            return data.to_dict(orient="records")
        except Exception:
            pass
    return data


@dataclass
class OpenDSettings:
    host: str = "127.0.0.1"
    port: int = 11111
    market: str = "HK"
    security_firm: str = "FUTUSECURITIES"
    trd_env: str = "SIMULATE"
    credential_method: str = "openclaw"


class OpenDClient:
    def __init__(self, settings: OpenDSettings):
        self.settings = settings
        self.ft = load_sdk()

    def _enum(self, enum_name: str, value: str):
        enum_obj = getattr(self.ft, enum_name)
        return getattr(enum_obj, value.upper())

    def quote_context(self):
        return self.ft.OpenQuoteContext(host=self.settings.host, port=self.settings.port)

    def trade_context(self):
        return self.ft.OpenSecTradeContext(
            filter_trdmarket=self._enum("TrdMarket", self.settings.market),
            host=self.settings.host,
            port=self.settings.port,
            security_firm=self._enum("SecurityFirm", self.settings.security_firm),
        )

    def unlock_trade(self, trade_ctx, trd_env, method: Optional[str] = None):
        if trd_env == self._enum("TrdEnv", "SIMULATE"):
            return
        credential_method = method or self.settings.credential_method
        if credential_method == "none":
            return
        password = get_password(credential_method)
        if not password:
            raise RuntimeError("No trade password found for unlock")
        ret, msg = trade_ctx.unlock_trade(password=password)
        if not _ret_ok(self.ft, ret):
            raise RuntimeError(f"unlock_trade failed: {msg}")

    def resolve_acc_id(self, trade_ctx, trd_env, explicit_acc_id: Optional[int] = None):
        if explicit_acc_id is not None:
            return explicit_acc_id

        ret, data = trade_ctx.get_acc_list()
        if not _ret_ok(self.ft, ret):
            raise RuntimeError(f"get_acc_list failed: {data}")

        if not hasattr(data, "iterrows"):
            return None

        for _, row in data.iterrows():
            if row.get("trd_env") != trd_env:
                continue
            # Use ACTIVE universal account when available, fallback to first env match.
            if row.get("acc_status") == getattr(self.ft.TrdAccStatus, "ACTIVE", None):
                return int(row["acc_id"])

        for _, row in data.iterrows():
            if row.get("trd_env") == trd_env:
                return int(row["acc_id"])

        return None

    def get_snapshot(self, codes: Iterable[str]):
        quote_ctx = self.quote_context()
        try:
            ret, data = quote_ctx.get_market_snapshot(list(codes))
            if not _ret_ok(self.ft, ret):
                raise RuntimeError(f"get_market_snapshot failed: {data}")
            return as_records(data)
        finally:
            quote_ctx.close()

    def get_accounts(self):
        trade_ctx = self.trade_context()
        try:
            ret, data = trade_ctx.get_acc_list()
            if not _ret_ok(self.ft, ret):
                raise RuntimeError(f"get_acc_list failed: {data}")
            return as_records(data)
        finally:
            trade_ctx.close()

    def get_positions(self, trd_env: str, acc_id: Optional[int] = None):
        trade_ctx = self.trade_context()
        env = self._enum("TrdEnv", trd_env)
        try:
            selected_acc_id = self.resolve_acc_id(trade_ctx, env, explicit_acc_id=acc_id)
            kwargs = {"trd_env": env}
            if selected_acc_id is not None:
                kwargs["acc_id"] = selected_acc_id
            ret, data = trade_ctx.position_list_query(**kwargs)
            if not _ret_ok(self.ft, ret):
                raise RuntimeError(f"position_list_query failed: {data}")
            return as_records(data)
        finally:
            trade_ctx.close()

    def place_order(
        self,
        code: str,
        price: float,
        qty: float,
        side: str,
        order_type: str,
        trd_env: str,
        acc_id: Optional[int] = None,
        unlock_method: Optional[str] = None,
    ):
        trade_ctx = self.trade_context()
        env = self._enum("TrdEnv", trd_env)
        try:
            self.unlock_trade(trade_ctx, env, method=unlock_method)
            selected_acc_id = self.resolve_acc_id(trade_ctx, env, explicit_acc_id=acc_id)
            kwargs = {
                "price": float(price),
                "qty": float(qty),
                "code": code,
                "trd_side": self._enum("TrdSide", side),
                "order_type": self._enum("OrderType", order_type),
                "trd_env": env,
            }
            if selected_acc_id is not None:
                kwargs["acc_id"] = selected_acc_id
            ret, data = trade_ctx.place_order(**kwargs)
            if not _ret_ok(self.ft, ret):
                raise RuntimeError(f"place_order failed: {data}")
            return as_records(data)
        finally:
            trade_ctx.close()

    def cancel_order(
        self,
        order_id: str,
        trd_env: str,
        acc_id: Optional[int] = None,
        unlock_method: Optional[str] = None,
    ):
        trade_ctx = self.trade_context()
        env = self._enum("TrdEnv", trd_env)
        try:
            self.unlock_trade(trade_ctx, env, method=unlock_method)
            selected_acc_id = self.resolve_acc_id(trade_ctx, env, explicit_acc_id=acc_id)
            kwargs = {
                "modify_order_op": self._enum("ModifyOrderOp", "CANCEL"),
                "order_id": str(order_id),
                "qty": 0,
                "price": 0,
                "trd_env": env,
            }
            if selected_acc_id is not None:
                kwargs["acc_id"] = selected_acc_id
            ret, data = trade_ctx.modify_order(**kwargs)
            if not _ret_ok(self.ft, ret):
                raise RuntimeError(f"cancel_order failed: {data}")
            return as_records(data)
        finally:
            trade_ctx.close()
