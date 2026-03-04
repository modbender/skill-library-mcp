#!/usr/bin/env python3
"""Unified Interactive Brokers CLI built on ib_insync.

This CLI supports common TWS/Gateway API workflows:
- account summary, positions, portfolio, PnL
- quote snapshots and historical bars
- contract discovery
- order placement/cancellation/open-order listing
- executions and scanner queries

Connection defaults can be overridden via env vars:
- IBKR_HOST (default: 127.0.0.1)
- IBKR_PORT (default: 7497)
- IBKR_CLIENT_ID (default: 1)
- IBKR_ACCOUNT (optional)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Iterable, Optional

_IB_IMPORT_ERROR: Optional[Exception] = None

try:
    from ib_insync import (
        IB,
        CFD,
        Bag,
        Bond,
        Commodity,
        Contract,
        Crypto,
        Forex,
        Future,
        Index,
        LimitOrder,
        MarketOrder,
        Option,
        ScannerSubscription,
        Stock,
        StopLimitOrder,
        StopOrder,
        Trade,
    )
except Exception as exc:  # pragma: no cover - runtime dependency gate
    _IB_IMPORT_ERROR = exc


DONE_STATUSES = {
    "ApiCancelled",
    "Cancelled",
    "Filled",
    "Inactive",
}


@dataclass
class ConnectionConfig:
    host: str
    port: int
    client_id: int
    account: str
    readonly: bool
    timeout: float


def die(message: str, code: int = 2) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return code


def require_ib() -> Optional[int]:
    if _IB_IMPORT_ERROR is not None:
        return die(
            "ib_insync is required. Install with: pip install ib_insync\n"
            f"Import error: {_IB_IMPORT_ERROR}",
            3,
        )
    return None


def create_connection_config(args: argparse.Namespace) -> ConnectionConfig:
    return ConnectionConfig(
        host=args.host,
        port=args.port,
        client_id=args.client_id,
        account=args.account,
        readonly=args.readonly,
        timeout=args.timeout,
    )


def connect_ib(config: ConnectionConfig) -> Any:
    ib = IB()
    ib.connect(
        host=config.host,
        port=config.port,
        clientId=config.client_id,
        timeout=config.timeout,
        readonly=config.readonly,
        account=config.account or "",
    )
    return ib


def bool_flag(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {value}")


def print_rows(rows: Iterable[dict[str, Any]], as_json: bool) -> None:
    if as_json:
        print(json.dumps(list(rows), indent=2, default=str))
        return
    for row in rows:
        print(" ".join(f"{k}={v}" for k, v in row.items()))


def build_contract(args: argparse.Namespace) -> Any:
    sec_type = args.sec_type.upper()

    if sec_type == "STK":
        return Stock(args.symbol, args.exchange, args.currency, primaryExchange=args.primary_exchange)
    if sec_type == "CASH":
        if len(args.symbol) != 6:
            raise ValueError("CASH symbol must be a 6-letter pair like EURUSD")
        return Forex(args.symbol, exchange=args.exchange)
    if sec_type == "OPT":
        if not args.expiry or not args.strike or not args.right:
            raise ValueError("OPT requires --expiry, --strike, and --right")
        return Option(
            args.symbol,
            args.expiry,
            args.strike,
            args.right.upper(),
            args.exchange,
            args.multiplier,
            args.currency,
            args.trading_class,
        )
    if sec_type == "FUT":
        if not args.expiry:
            raise ValueError("FUT requires --expiry")
        return Future(
            args.symbol,
            args.expiry,
            args.exchange,
            args.currency,
            args.multiplier,
            args.local_symbol,
            args.trading_class,
        )
    if sec_type == "CFD":
        return CFD(args.symbol, args.exchange, args.currency)
    if sec_type == "IND":
        return Index(args.symbol, args.exchange, args.currency, localSymbol=args.local_symbol)
    if sec_type == "CRYPTO":
        return Crypto(args.symbol, args.exchange, args.currency)
    if sec_type == "BOND":
        return Bond(
            secType="BOND",
            symbol=args.symbol,
            exchange=args.exchange,
            currency=args.currency,
            localSymbol=args.local_symbol,
        )
    if sec_type == "BAG":
        return Bag(symbol=args.symbol, exchange=args.exchange, currency=args.currency)
    if sec_type == "CMDTY":
        return Commodity(args.symbol, args.exchange, args.currency)
    return Contract(
        symbol=args.symbol,
        secType=sec_type,
        exchange=args.exchange,
        currency=args.currency,
        primaryExchange=args.primary_exchange,
        localSymbol=args.local_symbol,
        tradingClass=args.trading_class,
        lastTradeDateOrContractMonth=args.expiry,
        strike=args.strike,
        right=args.right,
        multiplier=args.multiplier,
        conId=args.con_id,
    )


def normalize_what_to_show(sec_type: str, requested: str) -> str:
    if requested:
        return requested.upper()
    if sec_type.upper() == "CASH":
        return "MIDPOINT"
    return "TRADES"


def wait_for_terminal_status(ib: Any, trade: Trade, wait_seconds: float) -> None:
    remaining = wait_seconds
    seen_status = None
    while remaining > 0:
        status = trade.orderStatus.status
        if status != seen_status:
            print(f"order_status={status}")
            seen_status = status
        if status in DONE_STATUSES:
            break
        ib.sleep(0.2)
        remaining -= 0.2


def add_shared_connection_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default=os.getenv("IBKR_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("IBKR_PORT", "7497")))
    parser.add_argument("--client-id", type=int, default=int(os.getenv("IBKR_CLIENT_ID", "1")))
    parser.add_argument("--account", default=os.getenv("IBKR_ACCOUNT", ""))
    parser.add_argument("--readonly", action="store_true", help="Request read-only mode")
    parser.add_argument("--timeout", type=float, default=10.0, help="IB connect timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")


def add_contract_flags(parser: argparse.ArgumentParser, include_sec_type: bool = True) -> None:
    parser.add_argument("--symbol", required=True)
    if include_sec_type:
        parser.add_argument("--sec-type", default="STK", help="e.g. STK, CASH, OPT, FUT, CFD, IND, CRYPTO")
    parser.add_argument("--exchange", default="SMART")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--primary-exchange", default="")
    parser.add_argument("--local-symbol", default="")
    parser.add_argument("--trading-class", default="")
    parser.add_argument("--expiry", default="")
    parser.add_argument("--strike", type=float, default=0.0)
    parser.add_argument("--right", default="")
    parser.add_argument("--multiplier", default="")
    parser.add_argument("--con-id", type=int, default=0)


def cmd_account_summary(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        items = ib.accountSummary(args.account or "")
        rows = [
            {
                "account": item.account,
                "tag": item.tag,
                "value": item.value,
                "currency": item.currency,
            }
            for item in items
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_positions(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        items = ib.positions(args.account or "")
        rows = [
            {
                "account": p.account,
                "symbol": p.contract.symbol,
                "secType": p.contract.secType,
                "exchange": p.contract.exchange,
                "currency": p.contract.currency,
                "position": p.position,
                "avgCost": p.avgCost,
            }
            for p in items
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_portfolio(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        items = ib.portfolio(args.account or "")
        rows = [
            {
                "account": p.account,
                "symbol": p.contract.symbol,
                "secType": p.contract.secType,
                "position": p.position,
                "marketPrice": p.marketPrice,
                "marketValue": p.marketValue,
                "avgCost": p.averageCost,
                "unrealizedPNL": p.unrealizedPNL,
                "realizedPNL": p.realizedPNL,
            }
            for p in items
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_pnl(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        account = args.account
        if not account:
            managed = ib.managedAccounts()
            if not managed:
                return die("No managed accounts returned; pass --account explicitly", 4)
            account = managed[0]

        pnl = ib.reqPnL(account, modelCode=args.model_code)
        ib.sleep(args.wait)
        row = {
            "account": account,
            "modelCode": args.model_code,
            "dailyPnL": pnl.dailyPnL,
            "unrealizedPnL": pnl.unrealizedPnL,
            "realizedPnL": pnl.realizedPnL,
        }
        print_rows([row], args.json)
        ib.cancelPnL(account, modelCode=args.model_code)
    finally:
        ib.disconnect()
    return 0


def cmd_quote(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        contract = build_contract(args)
        qualified = ib.qualifyContracts(contract)
        if not qualified:
            return die("Contract qualification failed", 4)
        ib.reqMarketDataType(args.market_data_type)
        ticker = ib.reqTickers(qualified[0])[0]
        row = {
            "symbol": ticker.contract.symbol,
            "secType": ticker.contract.secType,
            "bid": ticker.bid,
            "ask": ticker.ask,
            "last": ticker.last,
            "close": ticker.close,
            "high": ticker.high,
            "low": ticker.low,
            "volume": ticker.volume,
            "time": ticker.time,
            "marketDataType": args.market_data_type,
        }
        print_rows([row], args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_historical(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        contract = build_contract(args)
        qualified = ib.qualifyContracts(contract)
        if not qualified:
            return die("Contract qualification failed", 4)

        what_to_show = normalize_what_to_show(args.sec_type, args.what_to_show)
        bars = ib.reqHistoricalData(
            qualified[0],
            endDateTime=args.end,
            durationStr=args.duration,
            barSizeSetting=args.bar_size,
            whatToShow=what_to_show,
            useRTH=args.use_rth,
            formatDate=1,
            keepUpToDate=False,
            timeout=args.timeout,
        )
        rows = [
            {
                "date": b.date,
                "open": b.open,
                "high": b.high,
                "low": b.low,
                "close": b.close,
                "volume": b.volume,
                "average": b.average,
                "barCount": b.barCount,
            }
            for b in bars
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def build_order(args: argparse.Namespace) -> Any:
    order_type = args.order_type.upper()
    action = args.action.upper()

    if order_type == "MKT":
        order = MarketOrder(action, args.quantity)
    elif order_type == "LMT":
        if args.limit_price is None:
            raise ValueError("LMT requires --limit-price")
        order = LimitOrder(action, args.quantity, args.limit_price)
    elif order_type == "STP":
        if args.stop_price is None:
            raise ValueError("STP requires --stop-price")
        order = StopOrder(action, args.quantity, args.stop_price)
    elif order_type in {"STP LMT", "STP-LMT", "STPLMT"}:
        if args.stop_price is None or args.limit_price is None:
            raise ValueError("STP LMT requires --stop-price and --limit-price")
        order = StopLimitOrder(action, args.quantity, args.limit_price, args.stop_price)
    else:
        raise ValueError(f"Unsupported order type: {order_type}")

    if args.tif:
        order.tif = args.tif
    if args.outside_rth:
        order.outsideRth = True
    if args.account:
        order.account = args.account

    return order


def cmd_place_order(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    errors: list[dict[str, Any]] = []

    def on_error(req_id: int, code: int, msg: str, contract: Any) -> None:
        errors.append(
            {
                "reqId": req_id,
                "code": code,
                "message": msg,
                "contract": getattr(contract, "symbol", ""),
            }
        )

    ib.errorEvent += on_error
    try:
        contract = build_contract(args)
        qualified = ib.qualifyContracts(contract)
        if not qualified:
            return die("Contract qualification failed", 4)

        order = build_order(args)
        trade = ib.placeOrder(qualified[0], order)
        wait_for_terminal_status(ib, trade, args.wait)

        row = {
            "orderId": trade.order.orderId,
            "permId": trade.order.permId,
            "clientId": trade.order.clientId,
            "symbol": qualified[0].symbol,
            "action": trade.order.action,
            "orderType": trade.order.orderType,
            "quantity": trade.order.totalQuantity,
            "status": trade.orderStatus.status,
            "filled": trade.orderStatus.filled,
            "remaining": trade.orderStatus.remaining,
            "avgFillPrice": trade.orderStatus.avgFillPrice,
            "lastFillPrice": trade.orderStatus.lastFillPrice,
        }

        if args.json:
            payload = {"trade": row, "errors": errors}
            print(json.dumps(payload, indent=2, default=str))
        else:
            print_rows([row], False)
            for err in errors:
                print_rows([err], False)
    finally:
        ib.errorEvent -= on_error
        ib.disconnect()
    return 0


def cmd_cancel_order(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        open_trades = ib.openTrades()
        matching = [t for t in open_trades if t.order.orderId == args.order_id]
        if not matching:
            return die(f"No open trade found for orderId={args.order_id}", 4)
        trade = matching[0]
        ib.cancelOrder(trade.order)
        ib.sleep(0.5)
        row = {
            "orderId": trade.order.orderId,
            "status": trade.orderStatus.status,
        }
        print_rows([row], args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_open_orders(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        rows = []
        for trade in ib.openTrades():
            rows.append(
                {
                    "orderId": trade.order.orderId,
                    "permId": trade.order.permId,
                    "symbol": trade.contract.symbol,
                    "secType": trade.contract.secType,
                    "action": trade.order.action,
                    "orderType": trade.order.orderType,
                    "quantity": trade.order.totalQuantity,
                    "status": trade.orderStatus.status,
                    "filled": trade.orderStatus.filled,
                    "remaining": trade.orderStatus.remaining,
                }
            )
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_executions(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        fills = ib.reqExecutions()
        rows = [
            {
                "time": f.time,
                "symbol": f.contract.symbol,
                "secType": f.contract.secType,
                "side": f.execution.side,
                "shares": f.execution.shares,
                "price": f.execution.price,
                "orderId": f.execution.orderId,
                "execId": f.execution.execId,
                "account": f.execution.acctNumber,
            }
            for f in fills
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_contract_details(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        contract = build_contract(args)
        details = ib.reqContractDetails(contract)
        rows = [
            {
                "conId": d.contract.conId,
                "symbol": d.contract.symbol,
                "secType": d.contract.secType,
                "exchange": d.contract.exchange,
                "primaryExchange": d.contract.primaryExchange,
                "currency": d.contract.currency,
                "longName": d.longName,
                "category": d.category,
                "subcategory": d.subcategory,
                "timeZoneId": d.timeZoneId,
                "tradingHours": d.tradingHours,
                "liquidHours": d.liquidHours,
                "minTick": d.minTick,
            }
            for d in details
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def cmd_scanner(args: argparse.Namespace) -> int:
    ib = connect_ib(create_connection_config(args))
    try:
        subscription = ScannerSubscription(
            instrument=args.instrument,
            locationCode=args.location_code,
            scanCode=args.scan_code,
            abovePrice=args.above_price,
            belowPrice=args.below_price,
            aboveVolume=args.above_volume,
            numberOfRows=args.rows,
        )
        scan_data = ib.reqScannerData(subscription)
        rows = [
            {
                "rank": item.rank,
                "symbol": item.contractDetails.contract.symbol,
                "secType": item.contractDetails.contract.secType,
                "exchange": item.contractDetails.contract.exchange,
                "distance": item.distance,
                "benchmark": item.benchmark,
                "projection": item.projection,
            }
            for item in scan_data
        ]
        print_rows(rows, args.json)
    finally:
        ib.disconnect()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ibkr-cli",
        description="Interactive Brokers TWS/Gateway CLI powered by ib_insync",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("account-summary", help="Fetch account summary tags")
    add_shared_connection_flags(p)
    p.set_defaults(func=cmd_account_summary)

    p = sub.add_parser("positions", help="Fetch current positions")
    add_shared_connection_flags(p)
    p.set_defaults(func=cmd_positions)

    p = sub.add_parser("portfolio", help="Fetch portfolio with PnL metrics")
    add_shared_connection_flags(p)
    p.set_defaults(func=cmd_portfolio)

    p = sub.add_parser("pnl", help="Fetch account-level PnL")
    add_shared_connection_flags(p)
    p.add_argument("--model-code", default="")
    p.add_argument("--wait", type=float, default=1.0, help="Seconds to wait for initial PnL update")
    p.set_defaults(func=cmd_pnl)

    p = sub.add_parser("quote", help="Fetch quote snapshot")
    add_shared_connection_flags(p)
    add_contract_flags(p)
    p.add_argument(
        "--market-data-type",
        type=int,
        default=1,
        choices=[1, 2, 3, 4],
        help="1=live 2=frozen 3=delayed 4=delayed-frozen",
    )
    p.set_defaults(func=cmd_quote)

    p = sub.add_parser("historical", help="Fetch historical bar data")
    add_shared_connection_flags(p)
    add_contract_flags(p)
    p.add_argument("--end", default="", help="IB endDateTime, e.g. 20260226-16:00:00")
    p.add_argument("--duration", default="30 D", help="e.g. '30 D', '2 W', '1 Y'")
    p.add_argument("--bar-size", default="1 day", help="e.g. '1 min', '1 hour', '1 day'")
    p.add_argument("--what-to-show", default="", help="TRADES, MIDPOINT, BID, ASK, ...")
    p.add_argument("--use-rth", type=bool_flag, default=True, help="Use regular trading hours")
    p.set_defaults(func=cmd_historical)

    p = sub.add_parser("place-order", help="Place an order and wait for status updates")
    add_shared_connection_flags(p)
    add_contract_flags(p)
    p.add_argument("--action", required=True, choices=["BUY", "SELL"])
    p.add_argument("--quantity", required=True, type=float)
    p.add_argument("--order-type", default="MKT", help="MKT, LMT, STP, STP LMT")
    p.add_argument("--limit-price", type=float)
    p.add_argument("--stop-price", type=float)
    p.add_argument("--tif", default="", help="DAY, GTC, IOC, FOK, OPG, etc")
    p.add_argument("--outside-rth", action="store_true")
    p.add_argument("--wait", type=float, default=8.0, help="Seconds to wait for terminal status")
    p.set_defaults(func=cmd_place_order)

    p = sub.add_parser("cancel-order", help="Cancel an open order by order id")
    add_shared_connection_flags(p)
    p.add_argument("--order-id", required=True, type=int)
    p.set_defaults(func=cmd_cancel_order)

    p = sub.add_parser("open-orders", help="List open orders")
    add_shared_connection_flags(p)
    p.set_defaults(func=cmd_open_orders)

    p = sub.add_parser("executions", help="List execution fills currently available in session")
    add_shared_connection_flags(p)
    p.set_defaults(func=cmd_executions)

    p = sub.add_parser("contract-details", help="Resolve contract details")
    add_shared_connection_flags(p)
    add_contract_flags(p)
    p.set_defaults(func=cmd_contract_details)

    p = sub.add_parser("scanner", help="Run market scanner query")
    add_shared_connection_flags(p)
    p.add_argument("--instrument", default="STK")
    p.add_argument("--location-code", default="STK.US.MAJOR")
    p.add_argument("--scan-code", default="TOP_PERC_GAIN")
    p.add_argument("--above-price", type=float, default=0)
    p.add_argument("--below-price", type=float, default=0)
    p.add_argument("--above-volume", type=int, default=0)
    p.add_argument("--rows", type=int, default=25)
    p.set_defaults(func=cmd_scanner)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    need_ib = require_ib()
    if need_ib is not None:
        return need_ib

    try:
        return args.func(args)
    except KeyboardInterrupt:
        return die("Interrupted", 130)
    except Exception as exc:
        return die(str(exc), 1)


if __name__ == "__main__":
    raise SystemExit(main())
