"""Grid Trading Strategy"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MEMORY_DIR, grid_state_path
from logger import get_logger
from okx_client import OKXClient

log = get_logger("okx.grid")


def load_state(inst_id: str) -> dict:
    path = grid_state_path(inst_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def save_state(inst_id: str, state: dict) -> None:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    with open(grid_state_path(inst_id), "w") as f:
        json.dump(state, f, indent=2)


def setup_grid(inst_id: str, lower: float, upper: float, grids: int,
               total_usdt: float, td_mode: str = "cash") -> None:
    """Initialize grid: place buy orders at each grid level below current price."""
    client = OKXClient()
    ticker = client.ticker(inst_id)
    if ticker.get("code") != "0":
        log.error(f"Error fetching price: {ticker.get('msg')}")
        return

    current = float(ticker["data"][0]["last"])
    step = (upper - lower) / grids
    levels = [lower + i * step for i in range(grids + 1)]
    order_usdt = total_usdt / grids

    log.info(f"\nGrid Setup: {inst_id}")
    log.info(f"Range: {lower} — {upper} | Grids: {grids} | Step: {step:.4f}")
    log.info(f"Current Price: {current:.4f}")
    log.info(f"USDT per grid: {order_usdt:.2f}\n")

    state = {
        "inst_id": inst_id,
        "lower": lower,
        "upper": upper,
        "grids": grids,
        "step": step,
        "total_usdt": total_usdt,
        "td_mode": td_mode,
        "levels": levels,
        "orders": {},
        "pnl": 0.0,
    }

    placed = 0
    for level in levels:
        if level >= current:
            continue  # Will place sell orders when price rises
        sz = str(round(order_usdt / level, 6))
        result = client.place_order(
            inst_id=inst_id,
            td_mode=td_mode,
            side="buy",
            ord_type="limit",
            sz=sz,
            px=str(round(level, 4)),
        )
        if result.get("code") == "0":
            ord_id = result["data"][0]["ordId"]
            state["orders"][str(round(level, 4))] = {"ordId": ord_id, "side": "buy", "sz": sz}
            placed += 1
            log.info(f"  ✅ Buy @ {level:.4f} | sz={sz}")
        else:
            log.error(f"Failed @ {level:.4f}: {result.get('msg')}")

    save_state(inst_id, state)
    log.info(f"\nGrid active: {placed} buy orders placed.")


def check_grid(inst_id: str) -> None:
    """Check filled orders and place opposite side orders."""
    client = OKXClient()
    state = load_state(inst_id)
    if not state:
        log.warning(f"No active grid for {inst_id}")
        return

    ticker = client.ticker(inst_id)
    current = float(ticker["data"][0]["last"])
    step = state["step"]
    td_mode = state["td_mode"]
    order_usdt = state["total_usdt"] / state["grids"]

    history = client.order_history("SPOT" if "SWAP" not in inst_id else "SWAP", inst_id, limit=50)
    filled_ids = {o["ordId"]: o for o in history.get("data", []) if o["state"] == "filled"}

    for px_str, order in list(state["orders"].items()):
        if order["ordId"] not in filled_ids:
            continue

        filled = filled_ids[order["ordId"]]
        fill_px = float(filled["avgPx"])
        sz = filled["accFillSz"]

        # Place opposite order
        if order["side"] == "buy":
            sell_px = round(fill_px + step, 4)
            result = client.place_order(
                inst_id=inst_id,
                td_mode=td_mode,
                side="sell",
                ord_type="limit",
                sz=sz,
                px=str(sell_px),
            )
            if result.get("code") == "0":
                ord_id = result["data"][0]["ordId"]
                state["orders"][str(sell_px)] = {"ordId": ord_id, "side": "sell", "sz": sz}
                del state["orders"][px_str]
                log.info(f"  🔄 Filled buy @ {fill_px:.4f} → placed sell @ {sell_px:.4f}")
        else:
            trade_profit = float(sz) * step  # profit = size × grid step
            state["pnl"] += trade_profit
            buy_px = round(fill_px - step, 4)
            new_sz = str(round(order_usdt / buy_px, 6))
            result = client.place_order(
                inst_id=inst_id,
                td_mode=td_mode,
                side="buy",
                ord_type="limit",
                sz=new_sz,
                px=str(buy_px),
            )
            if result.get("code") == "0":
                ord_id = result["data"][0]["ordId"]
                state["orders"][str(buy_px)] = {"ordId": ord_id, "side": "buy", "sz": new_sz}
                del state["orders"][px_str]
                log.info(f"  🔄 Filled sell @ {fill_px:.4f} → placed buy @ {buy_px:.4f} | trade profit: {trade_profit:.4f}")

    save_state(inst_id, state)
    log.info(f"\nCurrent: {current:.4f} | Total PnL: {state['pnl']:.4f} USDT")


def stop_grid(inst_id: str) -> None:
    """Cancel all grid orders."""
    client = OKXClient()
    state = load_state(inst_id)
    if not state:
        log.warning(f"No active grid for {inst_id}")
        return

    cancelled = 0
    for px_str, order in state["orders"].items():
        result = client.cancel_order(inst_id, order["ordId"])
        if result.get("code") == "0":
            cancelled += 1

    state["orders"] = {}
    save_state(inst_id, state)
    log.info(f"✅ Grid stopped. Cancelled {cancelled} orders. Total PnL: {state['pnl']:.4f} USDT")


if __name__ == "__main__":
    """
    Usage:
      python grid.py setup BTC-USDT 40000 50000 10 1000
      python grid.py check BTC-USDT
      python grid.py stop BTC-USDT
    """
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    inst = sys.argv[2] if len(sys.argv) > 2 else ""

    if cmd == "setup" and len(sys.argv) >= 7:
        setup_grid(inst, float(sys.argv[3]), float(sys.argv[4]),
                   int(sys.argv[5]), float(sys.argv[6]),
                   sys.argv[7] if len(sys.argv) > 7 else "cash")
    elif cmd == "check":
        check_grid(inst)
    elif cmd == "stop":
        stop_grid(inst)
    else:
        log.info("Usage: grid.py setup <inst_id> <lower> <upper> <grids> <usdt> [td_mode]")
        log.info("       grid.py check <inst_id>")
        log.info("       grid.py stop <inst_id>")
