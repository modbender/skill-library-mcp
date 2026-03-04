"""Account & portfolio management"""
import json
from datetime import datetime, timezone
from logger import get_logger
from okx_client import OKXClient

log = get_logger("okx.account")


def get_balance(ccy: str = "") -> None:
    client = OKXClient()
    data = client.balance(ccy)
    if data.get("code") != "0":
        log.error(f"Error: {data.get('msg')}")
        return

    details = data["data"][0]["details"] if data["data"] else []
    total_usd = float(data["data"][0].get("totalEq", 0)) if data["data"] else 0

    log.info(f"\n{'='*50}")
    log.info(f"Total Equity: ${total_usd:,.2f} USD")
    log.info(f"{'='*50}")
    log.info(f"{'Currency':<12} {'Available':>14} {'Frozen':>14} {'USD Value':>14}")
    log.info("-" * 56)
    for d in details:
        if float(d.get("cashBal", 0)) > 0:
            log.info(f"{d['ccy']:<12} {float(d['cashBal']):>14.6f} "
                     f"{float(d.get('frozenBal','0')):>14.6f} "
                     f"${float(d.get('eqUsd','0')):>13.2f}")
    log.info("")


def get_positions(inst_type: str = "", inst_id: str = "") -> None:
    client = OKXClient()
    data = client.positions(inst_type, inst_id)
    if data.get("code") != "0":
        log.error(f"Error: {data.get('msg')}")
        return

    positions = data.get("data", [])
    if not positions:
        log.info("No open positions.")
        return

    log.info(f"\n{'='*70}")
    log.info("Open Positions")
    log.info(f"{'='*70}")
    log.info(f"{'Instrument':<20} {'Side':<8} {'Size':>10} {'Entry':>12} "
             f"{'Mark':>12} {'Unr.PnL':>12} {'Lev':>6}")
    log.info("-" * 82)
    for p in positions:
        side = p.get("posSide", p.get("side", "-"))
        def _f(val: str) -> float:
            return float(val) if val else 0.0
        log.info(f"{p['instId']:<20} {side:<8} "
                 f"{_f(p.get('pos','0')):>10.4f} "
                 f"{_f(p.get('avgPx','0')):>12.4f} "
                 f"{_f(p.get('markPx','0')):>12.4f} "
                 f"{_f(p.get('upl','0')):>12.4f} "
                 f"{p.get('lever',''):>6}x")
    log.info("")


def get_pending_orders(inst_id: str = "") -> None:
    client = OKXClient()
    data = client.pending_orders(inst_id)
    if data.get("code") != "0":
        log.error(f"Error: {data.get('msg')}")
        return

    orders = data.get("data", [])
    if not orders:
        log.info("No pending orders.")
        return

    log.info(f"\nPending Orders ({len(orders)})")
    log.info(f"{'Instrument':<20} {'Side':<6} {'Type':<8} {'Size':>10} {'Price':>12} {'Filled':>10}")
    log.info("-" * 72)
    for o in orders:
        log.info(f"{o['instId']:<20} {o['side']:<6} {o['ordType']:<8} "
                 f"{float(o['sz']):>10.4f} {float(o.get('px','0')):>12.4f} "
                 f"{float(o.get('fillSz','0')):>10.4f}")
    log.info("")


def get_order_history(inst_type: str = "SPOT", inst_id: str = "", limit: int = 20) -> None:
    client = OKXClient()
    data = client.order_history(inst_type, inst_id, limit)
    if data.get("code") != "0":
        log.error(f"Error: {data.get('msg')}")
        return

    orders = data.get("data", [])
    if not orders:
        log.info("No order history.")
        return

    log.info(f"\nOrder History — {inst_type} (last {len(orders)})")
    log.info(f"{'Time (UTC)':<16} {'Instrument':<20} {'Side':<6} {'Type':<8} "
             f"{'Size':>10} {'Avg Price':>12} {'Status':<10}")
    log.info("-" * 86)
    for o in orders:
        ts = o.get("uTime") or o.get("cTime", "0")
        try:
            dt = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc).strftime("%m-%d %H:%M")
        except (ValueError, OSError):
            dt = "?"
        avg_px = float(o.get("avgPx") or 0)
        log.info(f"{dt:<16} {o['instId']:<20} {o['side']:<6} {o['ordType']:<8} "
                 f"{float(o.get('sz','0')):>10.4f} {avg_px:>12.4f} {o.get('state','?'):<10}")
    log.info("")


def portfolio_summary() -> None:
    log.info("\n=== Portfolio Summary ===")
    get_balance()
    get_positions()
    get_pending_orders()


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    arg = sys.argv[2] if len(sys.argv) > 2 else ""

    if cmd == "balance":
        get_balance(arg)
    elif cmd == "positions":
        get_positions(arg)
    elif cmd == "orders":
        get_pending_orders(arg)
    elif cmd == "history":
        inst_type = arg.upper() if arg else "SPOT"
        inst_id = sys.argv[3] if len(sys.argv) > 3 else ""
        limit = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        get_order_history(inst_type, inst_id, limit)
    else:
        portfolio_summary()
