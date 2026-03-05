"""Spot-Futures Arbitrage (Cash & Carry)"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from errors import ArbHedgeFailedError
from logger import get_logger
from okx_client import OKXClient

log = get_logger("okx.arb")


def basis(spot_id: str, swap_id: str) -> dict:
    """Calculate current basis between spot and perpetual swap."""
    client = OKXClient()

    spot_data = client.ticker(spot_id)
    swap_data = client.ticker(swap_id)
    funding_data = client.funding_rate(swap_id)

    if spot_data.get("code") != "0" or swap_data.get("code") != "0":
        return {"error": "Failed to fetch prices"}

    spot_px = float(spot_data["data"][0]["last"])
    swap_px = float(swap_data["data"][0]["last"])
    funding_rate = float(funding_data["data"][0].get("fundingRate", 0)) if funding_data.get("code") == "0" else 0

    basis_val = swap_px - spot_px
    basis_pct = basis_val / spot_px * 100
    annual_funding = funding_rate * 3 * 365 * 100  # 3x daily (8h intervals)

    return {
        "spot_id": spot_id,
        "swap_id": swap_id,
        "spot_price": spot_px,
        "swap_price": swap_px,
        "basis": round(basis_val, 4),
        "basis_pct": round(basis_pct, 4),
        "funding_rate": round(funding_rate * 100, 6),
        "annual_funding_pct": round(annual_funding, 2),
        "signal": "open" if basis_pct > 0.1 else "close" if basis_pct < 0.02 else "wait",
    }


def open_arb(spot_id: str, swap_id: str, usdt_sz: float,
             min_basis_pct: float = 0.1) -> None:
    """Open arbitrage: buy spot + short swap when basis > threshold."""
    client = OKXClient()
    info = basis(spot_id, swap_id)

    log.info(f"\nArbitrage Analysis:")
    log.info(f"  Spot:    {info['spot_price']:.4f}")
    log.info(f"  Swap:    {info['swap_price']:.4f}")
    log.info(f"  Basis:   {info['basis_pct']:.4f}% | Funding: {info['annual_funding_pct']:.2f}%/yr")

    if info["basis_pct"] < min_basis_pct:
        log.info(f"  ⚪ Basis {info['basis_pct']:.4f}% < threshold {min_basis_pct}% — no trade")
        return

    spot_sz = str(round(usdt_sz / info["spot_price"], 6))
    swap_sz = str(int(usdt_sz / info["swap_price"]))  # contracts

    log.info(f"\n  Opening arb: buy {spot_sz} {spot_id} + short {swap_sz} {swap_id}")
    confirm = input("  Confirm? [y/N]: ").strip().lower()
    if confirm != "y":
        log.info("  Cancelled.")
        return

    # Buy spot
    r1 = client.place_order(spot_id, "cash", "buy", "market", spot_sz)
    if r1.get("code") == "0":
        log.info(f"  ✅ Spot buy: {r1['data'][0]['ordId']}")
    else:
        log.error(f"Spot buy failed: {r1.get('msg')}")
        return

    # Short swap — if this fails, spot is already filled: critical hedge failure
    r2 = client.place_order(swap_id, "cross", "sell", "market", swap_sz, pos_side="short")
    if r2.get("code") == "0":
        log.info(f"  ✅ Swap short: {r2['data'][0]['ordId']}")
    else:
        raise ArbHedgeFailedError("swap-short", r2.get("msg", "unknown error"))


def close_arb(spot_id: str, swap_id: str, spot_sz: str, swap_sz: str,
              max_basis_pct: float = 0.02) -> None:
    """Close arbitrage: sell spot + close short when basis converges."""
    client = OKXClient()
    info = basis(spot_id, swap_id)

    log.info(f"\n  Current basis: {info['basis_pct']:.4f}%")
    if info["basis_pct"] > max_basis_pct:
        log.info(f"  ⚪ Basis {info['basis_pct']:.4f}% > close threshold {max_basis_pct}% — hold")
        return

    log.info(f"  Closing arb: sell {spot_sz} {spot_id} + close {swap_sz} {swap_id}")
    confirm = input("  Confirm? [y/N]: ").strip().lower()
    if confirm != "y":
        log.info("  Cancelled.")
        return

    r1 = client.place_order(spot_id, "cash", "sell", "market", spot_sz)
    if r1.get("code") == "0":
        log.info(f"  ✅ Spot sell: {r1['data'][0]['ordId']}")
    else:
        log.error(f"Spot sell failed: {r1.get('msg')}")

    r2 = client.place_order(swap_id, "cross", "buy", "market", swap_sz,
                             reduce_only=True, pos_side="short")
    if r2.get("code") == "0":
        log.info(f"  ✅ Swap close: {r2['data'][0]['ordId']}")
    else:
        log.error(f"Swap close failed: {r2.get('msg')}")


def scan(pairs: list = None) -> None:
    """Scan multiple pairs for arbitrage opportunities."""
    if not pairs:
        pairs = [
            ("BTC-USDT", "BTC-USDT-SWAP"),
            ("ETH-USDT", "ETH-USDT-SWAP"),
            ("SOL-USDT", "SOL-USDT-SWAP"),
        ]

    log.info(f"\n{'Pair':<20} {'Spot':>12} {'Swap':>12} {'Basis%':>8} {'Funding%/yr':>12} {'Signal':>8}")
    log.info("-" * 76)
    for spot_id, swap_id in pairs:
        info = basis(spot_id, swap_id)
        if "error" in info:
            log.warning(f"{spot_id}: {info['error']}")
            continue
        signal_icon = "🟢" if info["signal"] == "open" else "🔴" if info["signal"] == "close" else "⚪"
        log.info(f"{spot_id:<20} {info['spot_price']:>12.4f} {info['swap_price']:>12.4f} "
                 f"{info['basis_pct']:>8.4f} {info['annual_funding_pct']:>12.2f} "
                 f"{signal_icon} {info['signal']:>6}")


if __name__ == "__main__":
    """
    Usage:
      python arbitrage.py scan
      python arbitrage.py basis BTC-USDT BTC-USDT-SWAP
      python arbitrage.py open BTC-USDT BTC-USDT-SWAP 1000 --min-basis 0.1
      python arbitrage.py close BTC-USDT BTC-USDT-SWAP 0.01 1 --max-basis 0.02
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", choices=["scan", "basis", "open", "close"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--min-basis", type=float, default=0.1)
    parser.add_argument("--max-basis", type=float, default=0.02)
    a = parser.parse_args()

    if a.cmd == "scan":
        scan()
    elif a.cmd == "basis" and len(a.args) >= 2:
        log.info(json.dumps(basis(a.args[0], a.args[1]), indent=2))
    elif a.cmd == "open" and len(a.args) >= 3:
        try:
            open_arb(a.args[0], a.args[1], float(a.args[2]), a.min_basis)
        except ArbHedgeFailedError as e:
            log.error(f"HEDGE FAILURE — {e}. Spot is filled but swap is not. Close spot manually!")
            sys.exit(1)
    elif a.cmd == "close" and len(a.args) >= 4:
        close_arb(a.args[0], a.args[1], a.args[2], a.args[3], a.max_basis)
    else:
        parser.print_help()
