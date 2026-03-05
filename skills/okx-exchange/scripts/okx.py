#!/usr/bin/env python3
"""OKX Exchange Skill — Unified CLI dispatcher

Usage:
  python okx.py account [balance|positions|orders] [CCY]
  python okx.py buy|sell <inst_id> <type> <sz> [options]
  python okx.py cancel <inst_id> <ord_id>
  python okx.py cancel-all <inst_id>
  python okx.py leverage <inst_id> <lever> [--td cross]
  python okx.py trend analyze|run <inst_id> [options]
  python okx.py grid setup|check|stop <inst_id> [options]
  python okx.py arb scan|basis|open|close [options]
  python okx.py monitor [sl-tp|scan]
  python okx.py prefs [show|set <key> <value>]
  python okx.py setup
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategies"))

from logger import get_logger

log = get_logger("okx")


def resolve_inst_id(name: str) -> str:
    """Resolve a short coin name (e.g. 'BTC') to a full instrument ID.

    If the input already contains '-', it is returned as-is (backward compatible).
    Otherwise the watchlist is searched first; on multiple matches a SWAP contract
    is preferred.  Falls back to '<COIN>-USDT-SWAP' when nothing is found.
    """
    if not name or "-" in name:
        return name  # already a full ID or empty (means "all")

    coin = name.upper()
    from config import load_prefs
    watchlist = load_prefs().get("watchlist", [])

    matches = [w for w in watchlist if w.upper().startswith(coin + "-")]
    if len(matches) == 1:
        resolved = matches[0]
    elif len(matches) > 1:
        swaps = [m for m in matches if "SWAP" in m.upper()]
        resolved = swaps[0] if swaps else matches[0]
    else:
        resolved = f"{coin}-USDT-SWAP"

    if resolved != name:
        log.info(f"  ↳ '{name}' resolved to '{resolved}'")
    return resolved

HELP = """
OKX Exchange Skill — Unified CLI

Account:
  python okx.py account                             Portfolio overview
  python okx.py account balance [CCY]               Balance by currency
  python okx.py account positions [INST_ID]         Open positions
  python okx.py account orders [INST_ID]            Pending orders
  python okx.py account history [SPOT|SWAP] [INST]  Filled order history

Market Data:
  python okx.py instruments [SPOT|SWAP|FUTURES] [COIN]  List instruments (filterable)
  python okx.py ticker <inst_id|COIN>                   Single ticker
  python okx.py ticker [SPOT|SWAP|FUTURES] [COIN]       Batch tickers by type
  python okx.py ticker watchlist                         Tickers for all watchlist coins
  python okx.py candles [INST_ID|COIN] [--bar 1H] [--limit 5]  Single K-line
  python okx.py candles --all [--bar 1H] [--limit 5]    K-lines for all watchlist coins

Trading:
  python okx.py buy  <inst_id> <type> <sz> [--td cash] [--pos long] [--px P] [--tp P] [--sl P] [--no-confirm]
  python okx.py sell <inst_id> <type> <sz> [--td cash] [--pos short] [--reduce]
  python okx.py cancel <inst_id> <ord_id>
  python okx.py cancel-all <inst_id>
  python okx.py leverage <inst_id> <lever> [--td cross]
  python okx.py transfer <ccy> <amount> <from> <to>  (from/to: funding or trading)

Strategies:
  python okx.py trend analyze <inst_id> [--bar 1H]
  python okx.py trend run <inst_id> <sz> [--bar 4H --tp 0.05 --sl 0.03 --td cross --pos long --dry]
  python okx.py grid setup <inst_id> <lower> <upper> <grids> <usdt> [--td cash]
  python okx.py grid check|stop <inst_id>
  python okx.py arb scan
  python okx.py arb basis <spot_id> <swap_id>
  python okx.py arb open <spot_id> <swap_id> <usdt_sz> [--min-basis 0.1]
  python okx.py arb close <spot_id> <swap_id> <spot_sz> <swap_sz> [--max-basis 0.02]

Algo Orders (standalone TP/SL — works on existing positions):
  python okx.py algo list [INST_ID]                    Pending algo orders
  python okx.py algo oco  <inst_id> <sz> --tp P --sl P [--td cross --pos long --reduce]
  python okx.py algo stop <inst_id> <sz> --sl P        Single stop-loss trigger
  python okx.py algo cancel <inst_id> <algo_id>        Cancel one algo order

Monitor:
  python okx.py monitor              SL/TP check, strategy scan, and liquidation risk
  python okx.py monitor sl-tp        Stop-loss / take-profit check only
  python okx.py monitor scan         Strategy scan — full watchlist
  python okx.py monitor scan <COIN>  Strategy scan — single coin only
  python okx.py monitor liq-risk [%] Liquidation price warning (default threshold: 10%)

Preferences:
  python okx.py prefs show           Show all preferences
  python okx.py prefs set <key> <v>  Update a preference value

Environment:
  OKX_SIMULATED=1     Paper trading mode (safe for testing)
  OKX_LOG_LEVEL       DEBUG | INFO | WARNING | ERROR  (default: INFO)
  OKX_LOG_FORMAT      text | json                     (default: text)
  OKX_CRON_MODE=1     Suppress INFO output (for cron)
""".strip()


# ── Account ───────────────────────────────────────────────────────────────────

def cmd_account(args: list) -> None:
    import account
    sub = args[0] if args else "summary"
    arg = args[1] if len(args) > 1 else ""
    if sub == "balance":
        account.get_balance(arg)
    elif sub == "positions":
        account.get_positions(inst_id=resolve_inst_id(arg))
    elif sub == "orders":
        account.get_pending_orders(resolve_inst_id(arg))
    elif sub == "history":
        inst_type = arg.upper() if arg else "SPOT"
        inst_id = resolve_inst_id(args[2]) if len(args) > 2 else ""
        limit = int(args[3]) if len(args) > 3 else 20
        account.get_order_history(inst_type, inst_id, limit)
    else:
        account.portfolio_summary()


# ── Trading ───────────────────────────────────────────────────────────────────

def cmd_trade(side: str, args: list) -> None:
    import argparse
    import execute
    p = argparse.ArgumentParser(prog=f"okx.py {side}")
    p.add_argument("inst_id")
    p.add_argument("ord_type")
    p.add_argument("sz")
    p.add_argument("--td", default="cash")
    p.add_argument("--pos", default="")
    p.add_argument("--px", default="")
    p.add_argument("--tp", default="")
    p.add_argument("--sl", default="")
    p.add_argument("--reduce", action="store_true")
    p.add_argument("--no-confirm", action="store_true")
    a = p.parse_args(args)
    execute.place_order(
        inst_id=resolve_inst_id(a.inst_id), side=side, ord_type=a.ord_type, sz=a.sz,
        td_mode=a.td, px=a.px, pos_side=a.pos, reduce_only=a.reduce,
        tp=a.tp, sl=a.sl, no_confirm=a.no_confirm,
    )


def cmd_cancel(args: list) -> None:
    import execute
    if len(args) < 2:
        log.error("Usage: okx.py cancel <inst_id> <ord_id>")
        sys.exit(1)
    execute.cancel_order(resolve_inst_id(args[0]), args[1])


def cmd_cancel_all(args: list) -> None:
    import execute
    if not args:
        log.error("Usage: okx.py cancel-all <inst_id>")
        sys.exit(1)
    execute.cancel_all(resolve_inst_id(args[0]))


def cmd_leverage(args: list) -> None:
    import argparse
    import execute
    p = argparse.ArgumentParser(prog="okx.py leverage")
    p.add_argument("inst_id")
    p.add_argument("lever", type=int)
    p.add_argument("--td", default="cross")
    a = p.parse_args(args)
    execute.set_leverage(resolve_inst_id(a.inst_id), a.lever, a.td)


def cmd_transfer(args: list) -> None:
    import execute
    # Aliases: funding/fund/6 → "6",  trading/trade/18 → "18"
    _code = {"funding": "6", "fund": "6", "6": "6", "trading": "18", "trade": "18", "18": "18"}
    if len(args) < 4:
        log.error("Usage: okx.py transfer <ccy> <amount> <from> <to>")
        log.info("  from/to: funding (6) or trading (18)")
        log.info("  Example: okx.py transfer USDT 100 funding trading")
        sys.exit(1)
    ccy, amt = args[0], args[1]
    from_acct = _code.get(args[2].lower(), args[2])
    to_acct = _code.get(args[3].lower(), args[3])
    execute.transfer_funds(ccy, amt, from_acct, to_acct)


# ── Strategies ────────────────────────────────────────────────────────────────

def cmd_trend(args: list) -> None:
    import argparse
    import trend
    p = argparse.ArgumentParser(prog="okx.py trend")
    p.add_argument("sub", choices=["analyze", "run"])
    p.add_argument("inst_id")
    p.add_argument("sz", nargs="?", default="0.01")
    p.add_argument("--bar", default="1H")
    p.add_argument("--td", default="cash")
    p.add_argument("--pos", default="")
    p.add_argument("--tp", type=float, default=0.05)
    p.add_argument("--sl", type=float, default=0.03)
    p.add_argument("--dry", action="store_true")
    a = p.parse_args(args)
    inst_id = resolve_inst_id(a.inst_id)
    if a.sub == "analyze":
        result = trend.analyze(inst_id, a.bar)
        print(json.dumps(result, indent=2))
    else:
        trend.run(inst_id, a.sz, a.td, a.pos, a.bar, a.tp, a.sl, a.dry)


def cmd_grid(args: list) -> None:
    import argparse
    import grid
    p = argparse.ArgumentParser(prog="okx.py grid")
    p.add_argument("sub", choices=["setup", "check", "stop"])
    p.add_argument("inst_id")
    p.add_argument("lower", nargs="?", type=float)
    p.add_argument("upper", nargs="?", type=float)
    p.add_argument("grids", nargs="?", type=int)
    p.add_argument("usdt", nargs="?", type=float)
    p.add_argument("--td", default="cash")
    a = p.parse_args(args)
    inst_id = resolve_inst_id(a.inst_id)
    if a.sub == "setup":
        if None in (a.lower, a.upper, a.grids, a.usdt):
            log.error("Usage: okx.py grid setup <inst_id> <lower> <upper> <grids> <usdt>")
            sys.exit(1)
        grid.setup_grid(inst_id, a.lower, a.upper, a.grids, a.usdt, a.td)
    elif a.sub == "check":
        grid.check_grid(inst_id)
    else:
        grid.stop_grid(inst_id)


def cmd_arb(args: list) -> None:
    import argparse
    import arbitrage
    from errors import ArbHedgeFailedError
    p = argparse.ArgumentParser(prog="okx.py arb")
    p.add_argument("sub", choices=["scan", "basis", "open", "close"])
    p.add_argument("rest", nargs="*")
    p.add_argument("--min-basis", type=float, default=0.1)
    p.add_argument("--max-basis", type=float, default=0.02)
    a = p.parse_args(args)
    if a.sub == "scan":
        arbitrage.scan()
    elif a.sub == "basis":
        if len(a.rest) < 2:
            log.error("Usage: okx.py arb basis <spot_id> <swap_id>")
            sys.exit(1)
        print(json.dumps(arbitrage.basis(resolve_inst_id(a.rest[0]), resolve_inst_id(a.rest[1])), indent=2))
    elif a.sub == "open":
        if len(a.rest) < 3:
            log.error("Usage: okx.py arb open <spot_id> <swap_id> <usdt_sz>")
            sys.exit(1)
        try:
            arbitrage.open_arb(resolve_inst_id(a.rest[0]), resolve_inst_id(a.rest[1]), float(a.rest[2]), a.min_basis)
        except ArbHedgeFailedError as e:
            log.error(f"HEDGE FAILURE — {e}. Spot is filled but swap is not. Close spot manually!")
            sys.exit(1)
    elif a.sub == "close":
        if len(a.rest) < 4:
            log.error("Usage: okx.py arb close <spot_id> <swap_id> <spot_sz> <swap_sz>")
            sys.exit(1)
        arbitrage.close_arb(resolve_inst_id(a.rest[0]), resolve_inst_id(a.rest[1]), a.rest[2], a.rest[3], a.max_basis)


# ── Algo Orders ───────────────────────────────────────────────────────────────

def cmd_algo(args: list) -> None:
    import argparse
    from okx_client import OKXClient
    client = OKXClient()
    sub = args[0] if args else "list"

    if sub == "list":
        inst_id = resolve_inst_id(args[1]) if len(args) > 1 else ""
        data = client.pending_algo_orders(inst_id)
        if data.get("code") != "0":
            log.error(f"Error: {data.get('msg')}")
            return
        orders = data.get("data", [])
        if not orders:
            log.info("No pending algo orders.")
            return
        log.info(f"\n{'Algo ID':<20} {'Instrument':<25} {'Type':<12} {'Side':<6} "
                 f"{'Size':>8} {'TP Trigger':>12} {'SL Trigger':>12}")
        log.info("-" * 100)
        for o in orders:
            log.info(f"  {o.get('algoId',''):<18} {o.get('instId',''):<23} "
                     f"{o.get('ordType',''):<12} {o.get('side',''):<6} "
                     f"{float(o.get('sz','0')):>8.4f} "
                     f"{o.get('tpTriggerPx','-'):>12} "
                     f"{o.get('slTriggerPx','-'):>12}")
        return

    if sub in ("oco", "stop"):
        p = argparse.ArgumentParser(prog=f"okx.py algo {sub}")
        p.add_argument("inst_id")
        p.add_argument("sz")
        p.add_argument("--side", default="sell")
        p.add_argument("--td", default="cross")
        p.add_argument("--pos", default="")
        p.add_argument("--tp", default="")
        p.add_argument("--sl", default="")
        p.add_argument("--reduce", action="store_true")
        p.add_argument("--no-confirm", action="store_true")
        a = p.parse_args(args[1:])
        inst_id = resolve_inst_id(a.inst_id)

        if sub == "oco" and (not a.tp or not a.sl):
            log.error("oco requires both --tp and --sl")
            sys.exit(1)
        if sub == "stop" and not a.sl:
            log.error("stop requires --sl")
            sys.exit(1)

        ord_type = "oco" if sub == "oco" else "conditional"
        log.info(f"\nAlgo Order Preview:")
        log.info(f"  Instrument : {inst_id}")
        log.info(f"  Type       : {ord_type.upper()}")
        log.info(f"  Side       : {a.side.upper()}")
        log.info(f"  Size       : {a.sz}")
        if a.tp:
            log.info(f"  TP Trigger : {a.tp}")
        if a.sl:
            log.info(f"  SL Trigger : {a.sl}")

        if not a.no_confirm:
            confirm = input("Confirm? [y/N] ").strip().lower()
            if confirm != "y":
                log.info("Cancelled.")
                return

        result = client.place_algo_order(
            inst_id=inst_id, td_mode=a.td, side=a.side,
            ord_type=ord_type, sz=a.sz,
            tp_trigger_px=a.tp, sl_trigger_px=a.sl,
            pos_side=a.pos, reduce_only=a.reduce,
        )
        if result.get("code") == "0":
            algo_id = result["data"][0].get("algoId", "")
            log.info(f"✅ Algo order placed: {algo_id}")
        else:
            log.error(f"❌ Error: {result.get('msg')} (code={result.get('code')})")
        return

    if sub == "cancel":
        if len(args) < 3:
            log.error("Usage: okx.py algo cancel <inst_id> <algo_id>")
            sys.exit(1)
        inst_id = resolve_inst_id(args[1])
        algo_id = args[2]
        result = client.cancel_algo_order(inst_id, algo_id)
        if result.get("code") == "0":
            log.info(f"✅ Algo order {algo_id} cancelled")
        else:
            log.error(f"❌ Error: {result.get('msg')}")
        return

    log.error(f"Unknown algo sub-command: {sub}")
    log.info("Usage: okx.py algo [list|oco|stop|cancel]")
    sys.exit(1)


# ── Monitor ───────────────────────────────────────────────────────────────────

def cmd_instruments(args: list) -> None:
    """List instruments by type, with optional coin filter."""
    from okx_client import OKXClient
    inst_type = args[0].upper() if args else "SWAP"
    coin_filter = args[1].upper() if len(args) > 1 else ""
    data = OKXClient().instruments(inst_type)
    if data.get("code") != "0":
        log.error(f"Error: {data.get('msg')}")
        return
    items = data.get("data", [])
    if coin_filter:
        items = [i for i in items if coin_filter in i["instId"].upper()]
    log.info(f"\n{inst_type} Instruments ({len(items)} matched):")
    for i in items:
        log.info(f"  {i['instId']:<25} ctVal={i.get('ctVal','-')} minSz={i.get('minSz','-')}")


def cmd_ticker(args: list) -> None:
    """Fetch ticker(s): single inst_id or all by inst_type or watchlist."""
    import json
    from okx_client import OKXClient
    from config import load_prefs
    client = OKXClient()

    if not args or args[0].lower() == "watchlist":
        # All tickers for watchlist coins
        watchlist = load_prefs().get("watchlist", [])
        log.info(f"\n{'Instrument':<25} {'Last':>12} {'24h%':>8} {'Vol(USDT)':>16}")
        log.info("-" * 65)
        for inst_id in watchlist:
            d = client.ticker(inst_id)
            if d.get("code") == "0" and d["data"]:
                t = d["data"][0]
                chg = float(t.get("sodUtc8", t.get("last", 0)) or 0)
                last = float(t.get("last", 0))
                pct = ((last - chg) / chg * 100) if chg else 0.0
                vol = float(t.get("volCcy24h", 0))
                log.info(f"  {inst_id:<23} {last:>12.4f} {pct:>+7.2f}% {vol:>16,.0f}")
    elif args[0].upper() in ("SPOT", "SWAP", "FUTURES", "OPTION"):
        # Batch fetch all by inst_type
        inst_type = args[0].upper()
        coin_filter = args[1].upper() if len(args) > 1 else ""
        d = client.tickers(inst_type)
        if d.get("code") != "0":
            log.error(f"Error: {d.get('msg')}")
            return
        items = d.get("data", [])
        if coin_filter:
            items = [t for t in items if coin_filter in t["instId"].upper()]
        items.sort(key=lambda t: float(t.get("volCcy24h", 0)), reverse=True)
        log.info(f"\n{inst_type} Tickers ({len(items)} shown):")
        log.info(f"  {'Instrument':<25} {'Last':>12} {'Vol(USDT)':>16}")
        log.info("  " + "-" * 57)
        for t in items[:50]:  # cap at 50 rows
            log.info(f"  {t['instId']:<25} {float(t.get('last',0)):>12.4f} "
                     f"{float(t.get('volCcy24h',0)):>16,.0f}")
    else:
        # Single inst_id
        inst_id = resolve_inst_id(args[0])
        d = client.ticker(inst_id)
        if d.get("code") != "0":
            log.error(f"Error: {d.get('msg')}")
            return
        print(json.dumps(d["data"][0], indent=2))


def cmd_candles(args: list) -> None:
    """Fetch K-line data: single coin or all watchlist coins."""
    import argparse
    from okx_client import OKXClient
    from config import load_prefs
    p = argparse.ArgumentParser(prog="okx.py candles")
    p.add_argument("inst_id", nargs="?", default="")
    p.add_argument("--bar", default="1H")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--all", dest="all_watchlist", action="store_true")
    a = p.parse_args(args)

    client = OKXClient()
    targets = load_prefs().get("watchlist", []) if a.all_watchlist else [resolve_inst_id(a.inst_id)]

    for inst_id in targets:
        d = client.candles(inst_id, a.bar, a.limit)
        if d.get("code") != "0":
            log.error(f"{inst_id}: {d.get('msg')}")
            continue
        rows = d.get("data", [])
        log.info(f"\n{inst_id} [{a.bar}] — last {len(rows)} candles:")
        log.info(f"  {'Time':<22} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Vol':>14}")
        log.info("  " + "-" * 80)
        for r in reversed(rows):  # OKX returns newest first
            from datetime import datetime, timezone
            ts = datetime.fromtimestamp(int(r[0]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")
            log.info(f"  {ts:<22} {float(r[1]):>10.4f} {float(r[2]):>10.4f} "
                     f"{float(r[3]):>10.4f} {float(r[4]):>10.4f} {float(r[5]):>14,.2f}")


def cmd_monitor(args: list) -> None:
    import monitor
    sub = args[0] if args else "all"
    inst_id = resolve_inst_id(args[1]) if len(args) > 1 else ""
    if sub == "sl-tp":
        monitor.check_stop_loss_take_profit()
    elif sub == "scan":
        monitor.scan_opportunities(inst_id)
    elif sub == "liq-risk":
        threshold = float(args[1]) if len(args) > 1 else 10.0
        monitor.check_liquidation_risk(threshold)
    else:
        monitor.check_stop_loss_take_profit()
        monitor.scan_opportunities()
        monitor.check_liquidation_risk()


# ── Preferences ───────────────────────────────────────────────────────────────

def cmd_prefs(args: list) -> None:
    from config import load_prefs, save_prefs
    sub = args[0] if args else "show"

    if sub == "show":
        log.info(json.dumps(load_prefs(), indent=2))
        return

    if sub == "set":
        if len(args) < 3:
            log.error("Usage: okx.py prefs set <key> <value>")
            sys.exit(1)
        key, raw = args[1], args[2]
        prefs = load_prefs()
        if key not in prefs:
            log.error(f"Unknown key: {key}. Valid keys: {', '.join(prefs.keys())}")
            sys.exit(1)
        # Coerce to current value's type
        current = prefs[key]
        if isinstance(current, bool):
            prefs[key] = raw.lower() in ("true", "1", "yes")
        elif isinstance(current, int):
            prefs[key] = int(raw)
        elif isinstance(current, float):
            prefs[key] = float(raw)
        elif isinstance(current, list):
            prefs[key] = [v.strip() for v in raw.split(",")]
        else:
            prefs[key] = raw
        save_prefs(prefs)
        log.info(f"✅ {key} = {prefs[key]}")
        return

    log.error(f"Unknown prefs sub-command: {sub}")
    log.info("Usage: okx.py prefs [show|set <key> <value>]")
    sys.exit(1)


def cmd_mode(args: list) -> None:
    """Switch between live and demo (simulated) trading."""
    from config import load_prefs, save_prefs
    prefs = load_prefs()
    current = prefs.get("mode", "demo")

    if not args:
        mode_label = f"{'🔴 LIVE' if current == 'live' else '🟢 DEMO'} ({current.upper()})"
        log.info(f"Current trading mode: {mode_label}")
        return

    new_mode = args[0].lower()
    if new_mode not in ("live", "demo"):
        log.error("Usage: okx.py mode [live|demo]")
        sys.exit(1)

    if new_mode == current:
        log.info(f"Already in {new_mode.upper()} mode.")
        return

    if new_mode == "live":
        log.info("⚠️  WARNING: Switching to LIVE trading mode — real money at risk!")
        log.info("   Live credentials: OKX_API_KEY_LIVE / OKX_SECRET_KEY_LIVE")
        confirm = input("   Type 'yes' to confirm: ").strip().lower()
        if confirm != "yes":
            log.info("Cancelled.")
            return

    prefs["mode"] = new_mode
    save_prefs(prefs)
    icon = "🔴" if new_mode == "live" else "🟢"
    log.info(f"✅ Mode switched to {icon} {new_mode.upper()}")


def cmd_snapshot(args: list) -> None:
    """Fetch live data, persist snapshot, print formatted cron report with real history."""
    from okx_client import OKXClient
    from config import load_snapshots, save_snapshot
    from datetime import datetime, timezone
    import zoneinfo

    client = OKXClient()
    tz = zoneinfo.ZoneInfo("Asia/Shanghai")
    now = datetime.now(tz)
    ts_label = now.strftime("%m-%d %H:%M")

    # ── 1. Fetch balance ──────────────────────────────────────────────────────
    bal_data = client.balance()
    equity_usd = 0.0
    avail_usdt = 0.0
    top_holdings = []
    if bal_data.get("code") == "0":
        for detail in bal_data["data"][0].get("details", []):
            eq = float(detail.get("eqUsd", 0) or 0)
            if eq < 0.01:
                continue
            equity_usd += eq
            top_holdings.append((detail.get("ccy", ""), eq,
                                  float(detail.get("availBal", 0) or 0)))
            if detail.get("ccy") == "USDT":
                avail_usdt = float(detail.get("availBal", 0) or 0)
    else:
        log.error(f"Balance fetch error: {bal_data.get('msg')}")
        sys.exit(1)

    top_holdings.sort(key=lambda x: x[1], reverse=True)

    # ── 2. Fetch positions ────────────────────────────────────────────────────
    pos_data = client.positions()
    positions = []
    total_upl = 0.0
    total_realized = 0.0
    if pos_data.get("code") == "0":
        for p in pos_data["data"]:
            if not p.get("instId") or float(p.get("pos", 0) or 0) == 0:
                continue
            upl = float(p.get("upl", 0) or 0)
            realized = float(p.get("realizedPnl", 0) or 0)
            mark_px = float(p.get("markPx", 0) or 0)
            positions.append({
                "inst_id": p["instId"],
                "pos_side": p.get("posSide", "net"),
                "sz": p.get("pos", "0"),
                "entry_px": float(p.get("avgPx", 0) or 0),
                "mark_px": mark_px,
                "upl": upl,
                "realized": realized,
                "liq_px": float(p.get("liqPx", 0) or 0),
                "lever": p.get("lever", ""),
            })
            total_upl += upl
            total_realized += realized
    else:
        log.error(f"Positions fetch error: {pos_data.get('msg')}")
        sys.exit(1)

    # ── 3. Persist snapshot ───────────────────────────────────────────────────
    snapshot = {
        "ts": now.isoformat(),
        "ts_label": ts_label,
        "equity_usd": round(equity_usd, 2),
        "avail_usdt": round(avail_usdt, 2),
        "total_upl": round(total_upl, 2),
        "total_realized": round(total_realized, 2),
        "positions": positions,
    }
    save_snapshot(snapshot)

    # ── 4. Load history ───────────────────────────────────────────────────────
    history = load_snapshots()
    initial_equity = history["initial_equity"] or equity_usd
    equity_change = equity_usd - initial_equity
    equity_change_pct = equity_change / initial_equity * 100 if initial_equity else 0.0
    snapshots = history["snapshots"]

    # ── 5. Build report ───────────────────────────────────────────────────────
    lines = []
    sep = "─" * 38

    lines.append(f"📊 OKX 交易监控报告 ({ts_label})")
    lines.append(sep)

    # Account overview
    lines.append("💰 账户总览")
    lines.append(f"  总权益   : ${equity_usd:>12,.2f}")
    lines.append(f"  初始资金 : ${initial_equity:>12,.2f}")
    change_icon = "📈" if equity_change >= 0 else "📉"
    lines.append(f"  资金变化 : {change_icon} {equity_change:+.2f} ({equity_change_pct:+.2f}%)")
    lines.append(f"  可用USDT : ${avail_usdt:>12,.2f}")

    # Top holdings (up to 5, skip USDT if avail is the same)
    if top_holdings:
        lines.append(sep)
        lines.append("🏦 主要持仓")
        for ccy, eq, avail in top_holdings[:5]:
            lines.append(f"  {ccy:<8} ${eq:>12,.2f}")

    # Open positions
    if positions:
        lines.append(sep)
        lines.append("📈 合约持仓")
        for p in positions:
            direction = "📉 空" if p["pos_side"] == "short" else "📈 多"
            upl_icon = "✅" if p["upl"] >= 0 else "❌"
            lines.append(
                f"  {p['inst_id']} {direction} x{p['lever']}"
            )
            lines.append(
                f"    入场 {p['entry_px']:,.1f} → 标记 {p['mark_px']:,.1f}"
            )
            lines.append(
                f"    未实现盈亏 {p['upl']:+.4f} USDT {upl_icon}"
                + (f"  | 已实现 {p['realized']:+.4f}" if abs(p["realized"]) > 0.001 else "")
            )
            if p["liq_px"] and 0 < p["liq_px"] < p["mark_px"] * 50:
                dist = abs(p["mark_px"] - p["liq_px"]) / p["mark_px"] * 100
                lines.append(f"    强平价 {p['liq_px']:,.1f}  距离 {dist:.1f}%")
        lines.append(f"  净未实现盈亏: {total_upl:+.4f} USDT")
    else:
        lines.append(sep)
        lines.append("📈 合约持仓: 无")

    # Historical tracking (last 5 real snapshots)
    if len(snapshots) >= 2:
        lines.append(sep)
        lines.append("📉 历史追踪（真实数据）")
        lines.append(f"  {'时间':<8} {'总权益':>14} {'未实现盈亏':>12} {'资金变化':>12}")
        for s in snapshots[-5:]:
            eq = s.get("equity_usd", 0)
            upl = s.get("total_upl", 0)
            chg = eq - initial_equity
            upl_icon = "✅" if upl >= 0 else "❌"
            chg_icon = "📈" if chg >= 0 else "📉"
            lines.append(
                f"  {s['ts_label']:<8} ${eq:>12,.2f}  {upl:>+10.4f}{upl_icon}"
                f"  {chg:>+10.2f}{chg_icon}"
            )

    lines.append(sep)
    print("\n".join(lines))


# ── Dispatch ──────────────────────────────────────────────────────────────────

_COMMANDS = {
    "account": cmd_account,
    "instruments": cmd_instruments,
    "ticker": cmd_ticker,
    "candles": cmd_candles,
    "trend": cmd_trend,
    "grid": cmd_grid,
    "arb": cmd_arb,
    "algo": cmd_algo,
    "monitor": cmd_monitor,
    "prefs": cmd_prefs,
    "mode": cmd_mode,
    "snapshot": cmd_snapshot,
    "report": lambda args: __import__("report").main(args),
    "transfer": cmd_transfer,
}

if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(HELP)
        sys.exit(0)

    cmd = argv[0]
    rest = argv[1:]

    if cmd in ("buy", "sell"):
        cmd_trade(cmd, rest)
    elif cmd == "cancel":
        cmd_cancel(rest)
    elif cmd == "cancel-all":
        cmd_cancel_all(rest)
    elif cmd == "leverage":
        cmd_leverage(rest)
    elif cmd == "setup":
        import setup as s
        s.check_deps()
        if s.check_env() and s.validate_api():
            s.create_default_prefs()
            log.info("\n✅ Setup complete. Run `python okx.py help` to see all commands.")
    elif cmd in _COMMANDS:
        _COMMANDS[cmd](rest)
    else:
        log.error(f"Unknown command: {cmd}")
        print(HELP)
        sys.exit(1)
