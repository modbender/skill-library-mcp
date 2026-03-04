"""Order execution with safety checks"""
import sys
from config import load_prefs
from logger import get_logger
from okx_client import OKXClient

log = get_logger("okx.execute")


def check_price_impact(client: OKXClient, inst_id: str, side: str, sz: float) -> tuple[float, bool]:
    book = client.orderbook(inst_id, sz=20)
    if book.get("code") != "0":
        return 0.0, False

    asks = book["data"][0]["asks"]  # [[price, qty, ...], ...]
    bids = book["data"][0]["bids"]

    orders = asks if side == "buy" else bids
    mid = (float(asks[0][0]) + float(bids[0][0])) / 2

    filled = 0.0
    cost = 0.0
    for price, qty, *_ in orders:
        take = min(float(qty), sz - filled)
        cost += take * float(price)
        filled += take
        if filled >= sz:
            break

    avg = cost / filled if filled > 0 else float(orders[0][0])
    impact = abs(avg - mid) / mid
    return impact, filled >= sz


def place_order(inst_id: str, side: str, ord_type: str, sz: str,
                td_mode: str = "cash", px: str = "",
                pos_side: str = "", reduce_only: bool = False,
                tp: str = "", sl: str = "", no_confirm: bool = False) -> None:
    prefs = load_prefs()
    client = OKXClient()

    # Max order USD check (spot only; derivatives rely on leverage limit)
    if td_mode == "cash":
        ticker = client.ticker(inst_id)
        if ticker.get("code") == "0":
            price = float(ticker["data"][0].get("last", 0))
            order_usd = float(sz) * price
            max_usd = prefs.get("max_order_usd", 100)
            if order_usd > max_usd:
                log.error(f"Aborted: order value ${order_usd:.2f} exceeds max_order_usd=${max_usd}")
                return

    # Price impact check for market orders
    if ord_type == "market":
        impact, fillable = check_price_impact(client, inst_id, side, float(sz))
        warn = prefs["price_impact_warn"]
        abort = prefs["price_impact_abort"]

        if impact > abort:
            log.error(f"Aborted: price impact {impact*100:.2f}% > {abort*100:.1f}% limit")
            return
        if impact > warn:
            log.warning(f"High price impact: {impact*100:.2f}%")

    # Confirmation (if required)
    if prefs.get("require_confirm") and not no_confirm:
        log.info(f"\nOrder Preview:")
        log.info(f"  Instrument : {inst_id}")
        log.info(f"  Side       : {side.upper()}")
        log.info(f"  Type       : {ord_type}")
        log.info(f"  Size       : {sz}")
        if px:
            log.info(f"  Price      : {px}")
        if tp:
            log.info(f"  Take Profit: {tp}")
        if sl:
            log.info(f"  Stop Loss  : {sl}")
        confirm = input("\nConfirm? [y/N]: ").strip().lower()
        if confirm != "y":
            log.info("Cancelled.")
            return

    result = client.place_order(
        inst_id=inst_id,
        td_mode=td_mode,
        side=side,
        ord_type=ord_type,
        sz=sz,
        px=px,
        reduce_only=reduce_only,
        pos_side=pos_side,
        tp_trigger_px=tp,
        sl_trigger_px=sl,
    )

    if result.get("code") == "0":
        ord_id = result["data"][0]["ordId"]
        log.info(f"✅ Order placed: {ord_id}")
    else:
        log.error(f"Error: {result.get('msg')} — {result.get('data', [{}])[0].get('sMsg', '')}")


def cancel_order(inst_id: str, ord_id: str) -> None:
    client = OKXClient()
    result = client.cancel_order(inst_id, ord_id)
    if result.get("code") == "0":
        log.info(f"✅ Cancelled: {ord_id}")
    else:
        log.error(f"Error: {result.get('msg')}")


def cancel_all(inst_id: str) -> None:
    client = OKXClient()
    result = client.cancel_all_orders(inst_id)
    failed = result.get("failed", 0)
    log.info(f"✅ Cancelled {result['cancelled']} orders for {inst_id}" +
             (f" ({failed} failed)" if failed else ""))


def set_leverage(inst_id: str, lever: int, mg_mode: str = "cross") -> None:
    prefs = load_prefs()
    max_lev = prefs.get("max_leverage", 10)
    if lever > max_lev:
        log.error(f"Aborted: leverage {lever}x exceeds max_leverage={max_lev}x")
        return
    client = OKXClient()
    result = client.set_leverage(inst_id, lever, mg_mode)
    if result.get("code") == "0":
        log.info(f"✅ Leverage set to {lever}x for {inst_id}")
    else:
        log.error(f"Error: {result.get('msg')}")


_ACCT_NAMES = {"6": "Funding", "18": "Trading"}


def transfer_funds(ccy: str, amt: str, from_acct: str, to_acct: str) -> None:
    """Transfer funds between OKX sub-accounts. from/to: 6=Funding, 18=Trading."""
    client = OKXClient()
    result = client.transfer(ccy, amt, from_acct, to_acct)
    if result.get("code") == "0":
        trans_id = result["data"][0].get("transId", "?")
        from_name = _ACCT_NAMES.get(from_acct, f"Acct {from_acct}")
        to_name = _ACCT_NAMES.get(to_acct, f"Acct {to_acct}")
        log.info(f"✅ Transfer submitted: {amt} {ccy} | {from_name} → {to_name} | ID: {trans_id}")
    else:
        log.error(f"Transfer failed: {result.get('msg')}")


if __name__ == "__main__":
    """
    Usage:
      python execute.py buy BTC-USDT market 0.01
      python execute.py buy BTC-USDT-SWAP market 1 --td isolated --pos long --sl 40000 --tp 50000
      python execute.py sell BTC-USDT limit 0.01 --px 45000
      python execute.py cancel BTC-USDT <ord_id>
      python execute.py cancel-all BTC-USDT
      python execute.py leverage BTC-USDT-SWAP 10
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["buy", "sell", "cancel", "cancel-all", "leverage"])
    parser.add_argument("inst_id")
    parser.add_argument("extra", nargs="*")
    parser.add_argument("--td", default="cash", help="tdMode: cash/cross/isolated")
    parser.add_argument("--pos", default="", help="posSide: long/short/net")
    parser.add_argument("--px", default="", help="Limit price")
    parser.add_argument("--tp", default="", help="Take profit trigger price")
    parser.add_argument("--sl", default="", help="Stop loss trigger price")
    parser.add_argument("--reduce", action="store_true")
    parser.add_argument("--no-confirm", action="store_true")
    args = parser.parse_args()

    if args.action in ("buy", "sell"):
        if len(args.extra) < 2:
            log.error("Usage: execute.py buy/sell <inst_id> <ord_type> <sz> [options]")
            sys.exit(1)
        place_order(
            inst_id=args.inst_id,
            side=args.action,
            ord_type=args.extra[0],
            sz=args.extra[1],
            td_mode=args.td,
            px=args.px,
            pos_side=args.pos,
            reduce_only=args.reduce,
            tp=args.tp,
            sl=args.sl,
            no_confirm=args.no_confirm,
        )
    elif args.action == "cancel":
        cancel_order(args.inst_id, args.extra[0])
    elif args.action == "cancel-all":
        cancel_all(args.inst_id)
    elif args.action == "leverage":
        set_leverage(args.inst_id, int(args.extra[0]), args.td)
