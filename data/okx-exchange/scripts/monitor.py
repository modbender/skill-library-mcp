"""Automated monitor: stop-loss/take-profit + strategy scan (for cron)"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import load_prefs, load_state, save_state, log_trade
from logger import get_logger
from okx_client import OKXClient
from okx_learning import record_trade, should_avoid_trade
from okx_ws_client import get_feed

log = get_logger("okx.monitor")


def _ws_warmup(watchlist: list, bar: str = "1H") -> None:
    """Subscribe WS feed to watchlist and wait briefly for connection."""
    feed = get_feed()
    if not feed:
        return
    feed.subscribe_tickers(watchlist)
    feed.subscribe_candles(watchlist, bar)
    if not feed._connected.is_set():
        feed.wait_ready(timeout=3)
    log.info(f"WS feed active — subscribed {len(watchlist)} instruments")


def check_stop_loss_take_profit() -> None:
    """Check all positions against SL/TP thresholds."""
    prefs = load_prefs()
    state = load_state()
    _ws_warmup(prefs.get("watchlist", []))
    client = OKXClient()

    positions_data = client.positions()
    if positions_data.get("code") != "0":
        log.error(f"Error fetching positions: {positions_data.get('msg')}")
        return

    positions = positions_data.get("data", [])
    if not positions:
        return

    today = datetime.utcnow().strftime("%Y-%m-%d")
    if state.get("last_reset") != today:
        state["daily_trades"] = 0
        state["last_reset"] = today

    actions_taken = []

    for pos in positions:
        inst_id = pos["instId"]
        upl_ratio = float(pos.get("uplRatio", 0)) * 100  # %
        side = pos.get("posSide", "net")
        sz = pos.get("pos", "0")

        if upl_ratio <= -prefs["stop_loss_pct"]:
            action = "stop_loss"
            close_side = "sell" if side in ("long", "net") else "buy"
        elif upl_ratio >= prefs["take_profit_pct"]:
            action = "take_profit"
            close_side = "sell" if side in ("long", "net") else "buy"
        else:
            continue

        msg = f"{'🛑 Stop-loss' if action == 'stop_loss' else '🎯 Take-profit'}: {inst_id} | PnL: {upl_ratio:.2f}%"
        log.info(msg)

        if prefs.get("auto_trade") and state["daily_trades"] < prefs["max_daily_trades"]:
            result = client.place_order(
                inst_id=inst_id,
                td_mode="cross",
                side=close_side,
                ord_type="market",
                sz=sz,
                reduce_only=True,
                pos_side=side if side not in ("net",) else "",
            )
            if result.get("code") == "0":
                state["daily_trades"] += 1
                actions_taken.append({"inst_id": inst_id, "action": action, "upl_pct": upl_ratio})
                log_trade({
                    "ts": datetime.utcnow().isoformat(),
                    "inst_id": inst_id,
                    "action": action,
                    "upl_pct": upl_ratio,
                    "ord_id": result["data"][0]["ordId"],
                })
                record_trade({
                    "coin": inst_id,
                    "direction": "long" if side in ("long", "net") else "short",
                    "signal_type": action,
                    "market_regime": "unknown",
                    "pnl_pct": upl_ratio,
                    "pnl_usdt": 0,
                    "hold_time_hours": 0,
                })
        else:
            log.warning(f"auto_trade=false or daily limit reached — manual action needed")

    save_state(state)
    if actions_taken:
        log.info(f"\nActions taken: {len(actions_taken)}")
    else:
        log.info("No SL/TP triggered.")


def scan_opportunities(inst_id: str = "") -> None:
    """Run strategy analysis on watchlist (or a single inst_id) and optionally execute."""
    prefs = load_prefs()
    state = load_state()
    watchlist = [inst_id] if inst_id else prefs.get("watchlist", [])
    strategies = prefs.get("strategies", ["trend"])

    _ws_warmup(watchlist)
    log.info(f"\n=== Opportunity Scan [{datetime.utcnow().strftime('%H:%M UTC')}] ===")

    for inst_id in watchlist:
        log.info(f"\n{inst_id}:")

        if "trend" in strategies:
            from strategies.trend import analyze
            result = analyze(inst_id)
            signal = result.get("signal", "hold")
            log.info(f"  Trend: {signal.upper()} | RSI:{result.get('rsi','?')} | "
                     f"MACD:{result.get('macd_histogram','?')}")

            if signal != "hold" and prefs.get("auto_trade"):
                today = datetime.utcnow().strftime("%Y-%m-%d")
                if state.get("last_reset") != today:
                    state["daily_trades"] = 0
                    state["last_reset"] = today
                if state["daily_trades"] >= prefs["max_daily_trades"]:
                    log.warning(f"Daily trade limit reached ({prefs['max_daily_trades']})")
                    continue

                market_regime = result.get("market_regime", "unknown")
                should_avoid, avoid_reason = should_avoid_trade(inst_id, signal.upper(), market_regime)
                if should_avoid:
                    log.warning(f"  ⚠️ Learning system skip: {avoid_reason}")
                    continue

                from execute import place_order
                sz = str(prefs.get("default_sz", "0.01"))
                td_mode = "cross" if "SWAP" in inst_id else "cash"
                current = result["current_price"]
                tp_pct = prefs.get("take_profit_pct", 5) / 100
                sl_pct = prefs.get("stop_loss_pct", 3) / 100

                tp = str(round(current * (1 + tp_pct if signal == "buy" else 1 - tp_pct), 4))
                sl = str(round(current * (1 - sl_pct if signal == "buy" else 1 + sl_pct), 4))

                pos_side = "long" if signal == "buy" else "short"
                log.info(f"  → Auto-{signal.upper()} sz={sz} pos={pos_side} TP={tp} SL={sl} [{market_regime}]")
                place_order(inst_id, signal, "market", sz, td_mode,
                            pos_side=pos_side, tp=tp, sl=sl, no_confirm=True)
                state["daily_trades"] += 1
                log_trade({
                    "ts": datetime.utcnow().isoformat(),
                    "inst_id": inst_id,
                    "action": f"auto_{signal}",
                    "signal_source": "trend",
                    "price": current,
                })
                record_trade({
                    "coin": inst_id,
                    "direction": "long" if signal == "buy" else "short",
                    "signal_type": f"trend_{signal}",
                    "market_regime": market_regime,
                    "pnl_pct": 0,
                    "pnl_usdt": 0,
                    "hold_time_hours": 0,
                })

        if "arbitrage" in strategies:
            if "SWAP" not in inst_id:
                continue
            from strategies.arbitrage import basis
            spot_id = inst_id.replace("-SWAP", "")
            info = basis(spot_id, inst_id)
            log.info(f"  Arb basis: {info.get('basis_pct','?')}% | Signal: {info.get('signal','?')}")

    state["last_scan"] = datetime.utcnow().isoformat()
    save_state(state)


def check_liquidation_risk(threshold_pct: float = 10.0) -> None:
    """Alert when mark price is within threshold_pct% of the liquidation price."""
    client = OKXClient()
    risk_data = client.position_risk()
    if risk_data.get("code") != "0":
        log.error(f"Error fetching position risk: {risk_data.get('msg')}")
        return

    alerts = []
    for item in risk_data.get("data", []):
        for pos in item.get("posData", []):
            inst_id = pos.get("instId", "")
            liq_px = pos.get("liqPx", "")
            mark_px = pos.get("markPx", "")
            pos_side = pos.get("posSide", "net")
            if not liq_px or not mark_px or liq_px == "0" or mark_px == "0":
                continue
            try:
                liq = float(liq_px)
                mark = float(mark_px)
            except ValueError:
                continue

            distance_pct = abs(mark - liq) / mark * 100
            if distance_pct <= threshold_pct:
                alerts.append({
                    "inst_id": inst_id,
                    "pos_side": pos_side,
                    "mark_px": mark,
                    "liq_px": liq,
                    "distance_pct": distance_pct,
                })
                log.warning(
                    f"⚠️ Liquidation risk: {inst_id} [{pos_side}] "
                    f"mark={mark} liq={liq} distance={distance_pct:.1f}%"
                )

    if not alerts:
        log.info(f"No liquidation risk (threshold={threshold_pct}%).")
    return alerts


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    inst_id = sys.argv[2] if len(sys.argv) > 2 else ""
    if cmd == "sl-tp":
        check_stop_loss_take_profit()
    elif cmd == "scan":
        scan_opportunities(inst_id)
    elif cmd == "liq-risk":
        threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
        check_liquidation_risk(threshold)
    else:
        check_stop_loss_take_profit()
        scan_opportunities()
        check_liquidation_risk()
