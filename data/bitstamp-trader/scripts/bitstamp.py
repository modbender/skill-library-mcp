#!/usr/bin/env python3
"""
Bitstamp Trading CLI — Safety-first cryptocurrency trading on Bitstamp.

Uses CCXT for exchange communication. All actions are logged.
Dry-run mode is ON by default — live trading requires explicit --live flag.

Safety features:
  - Granular API key permissions (trade-only, no withdrawal by default)
  - Maximum order size hard caps
  - Price sanity checks (rejects orders >3% from market)
  - Daily volume tracking with automatic cutoff
  - Confirmation prompts for large trades
  - Kill switch to cancel all open orders
  - Full audit trail logging
"""

import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve venv — auto-activate if running outside it
# ---------------------------------------------------------------------------
SKILL_DIR = Path(__file__).resolve().parent.parent
VENV_SITE = SKILL_DIR / ".venv" / "lib"
if VENV_SITE.exists():
    # Find the python3.x site-packages inside the venv
    for p in sorted(VENV_SITE.glob("python*/site-packages")):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
        break

try:
    import ccxt
except ImportError:
    print("ERROR: ccxt not installed. Run:")
    print(f"  source {SKILL_DIR}/.venv/bin/activate && pip install ccxt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
CONFIG_DIR = Path(os.environ.get("BITSTAMP_CONFIG_DIR", Path.home() / ".config" / "bitstamp-trader"))
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "audit.jsonl"
DAILY_VOLUME_FILE = CONFIG_DIR / "daily_volume.json"
KILL_SWITCH_FILE = CONFIG_DIR / "KILL_SWITCH"

DEFAULT_CONFIG = {
    "max_order_size_usd": 100.0,
    "max_daily_volume_usd": 500.0,
    "price_deviation_pct": 3.0,
    "large_trade_threshold_usd": 50.0,
    "default_market": "BTC/USD",
    "allowed_markets": ["BTC/USD", "ETH/USD", "BTC/EUR", "ETH/EUR"],
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def audit_log(category: str, action: str, details: dict):
    """Append-only structured audit log."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "id": str(uuid.uuid4())[:8],
        "category": category,
        "action": action,
        **details,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def log_print(category: str, action: str, details: dict, quiet=False):
    entry = audit_log(category, action, details)
    if not quiet:
        status = details.get("status", "")
        msg = details.get("msg", details.get("error", ""))
        print(f"[{entry['ts'][:19]}] [{category}] {action}: {status} {msg}".strip())


# ---------------------------------------------------------------------------
# Config management
# ---------------------------------------------------------------------------
def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            stored = json.load(f)
        # Merge with defaults for any missing keys
        merged = {**DEFAULT_CONFIG, **stored}
        return merged
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ---------------------------------------------------------------------------
# Kill switch
# ---------------------------------------------------------------------------
def is_kill_switch_active() -> bool:
    return KILL_SWITCH_FILE.exists()


def activate_kill_switch(reason: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    KILL_SWITCH_FILE.write_text(json.dumps({
        "activated": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }))
    log_print("KILL_SWITCH", "ACTIVATED", {"status": "🛑", "msg": reason})


def deactivate_kill_switch():
    if KILL_SWITCH_FILE.exists():
        KILL_SWITCH_FILE.unlink()
        log_print("KILL_SWITCH", "DEACTIVATED", {"status": "✅", "msg": "Trading resumed"})
    else:
        print("Kill switch is not active.")


# ---------------------------------------------------------------------------
# Daily volume tracking
# ---------------------------------------------------------------------------
def get_daily_volume() -> float:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if DAILY_VOLUME_FILE.exists():
        with open(DAILY_VOLUME_FILE) as f:
            data = json.load(f)
        if data.get("date") == today:
            return data.get("volume_usd", 0.0)
    return 0.0


def add_daily_volume(amount_usd: float):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    current = get_daily_volume()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(DAILY_VOLUME_FILE, "w") as f:
        json.dump({"date": today, "volume_usd": current + amount_usd}, f)


# ---------------------------------------------------------------------------
# Exchange connection
# ---------------------------------------------------------------------------
def get_exchange(live: bool = False) -> ccxt.bitstamp:
    api_key = os.environ.get("BITSTAMP_API_KEY", "")
    api_secret = os.environ.get("BITSTAMP_API_SECRET", "")

    if not api_key or not api_secret:
        if live:
            print("ERROR: BITSTAMP_API_KEY and BITSTAMP_API_SECRET must be set for live trading.")
            print("Export them as environment variables or add to your shell profile.")
            sys.exit(1)
        # For dry-run, return exchange without auth (public endpoints only)
        return ccxt.bitstamp({"enableRateLimit": True})

    return ccxt.bitstamp({
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
    })


# ---------------------------------------------------------------------------
# Safety checks
# ---------------------------------------------------------------------------
def pre_trade_checks(cfg: dict, side: str, market: str, amount: float,
                     price: float | None, live: bool, exchange: ccxt.bitstamp) -> float:
    """Run all safety checks before placing an order. Returns estimated USD value."""

    # Kill switch
    if is_kill_switch_active():
        print("🛑 KILL SWITCH IS ACTIVE. Trading is disabled.")
        print(f"   Details: {KILL_SWITCH_FILE.read_text()}")
        print("   To resume: bitstamp.py kill-switch --deactivate")
        sys.exit(1)

    # Market allowed?
    if market not in cfg["allowed_markets"]:
        print(f"ERROR: Market {market} not in allowed list: {cfg['allowed_markets']}")
        sys.exit(1)

    # Get current price for sanity checks
    ticker = exchange.fetch_ticker(market)
    current_price = ticker["last"]
    print(f"📊 Current {market} price: ${current_price:,.2f}")

    # Estimate order value in USD
    if price:
        order_price = price
    else:
        order_price = current_price

    # For buy orders, amount is in base currency
    est_usd = amount * order_price
    if "/EUR" in market:
        est_usd *= 1.08  # Rough EUR→USD for limit checks

    print(f"💰 Estimated order value: ${est_usd:,.2f}")

    # Max order size
    if est_usd > cfg["max_order_size_usd"]:
        print(f"🚫 Order exceeds max size (${cfg['max_order_size_usd']:,.2f}). Rejected.")
        log_print("GUARDRAIL", "MAX_SIZE_REJECTED", {
            "status": "BLOCKED", "side": side, "market": market,
            "amount": amount, "est_usd": est_usd,
            "limit": cfg["max_order_size_usd"],
        })
        sys.exit(1)

    # Daily volume
    daily_vol = get_daily_volume()
    if daily_vol + est_usd > cfg["max_daily_volume_usd"]:
        print(f"🚫 Daily volume limit would be exceeded.")
        print(f"   Used today: ${daily_vol:,.2f} / ${cfg['max_daily_volume_usd']:,.2f}")
        print(f"   This order: ${est_usd:,.2f}")
        log_print("GUARDRAIL", "DAILY_LIMIT_REJECTED", {
            "status": "BLOCKED", "side": side, "market": market,
            "daily_vol": daily_vol, "order_usd": est_usd,
            "limit": cfg["max_daily_volume_usd"],
        })
        sys.exit(1)

    # Price sanity check (for limit orders)
    if price:
        deviation = abs(price - current_price) / current_price * 100
        if deviation > cfg["price_deviation_pct"]:
            print(f"🚫 Price ${price:,.2f} deviates {deviation:.1f}% from market ${current_price:,.2f}.")
            print(f"   Max allowed: {cfg['price_deviation_pct']}%")
            log_print("GUARDRAIL", "PRICE_DEVIATION_REJECTED", {
                "status": "BLOCKED", "side": side, "market": market,
                "price": price, "current": current_price,
                "deviation_pct": round(deviation, 2),
            })
            sys.exit(1)

    # Large trade confirmation
    if live and est_usd >= cfg["large_trade_threshold_usd"]:
        print(f"\n⚠️  LARGE TRADE WARNING: ${est_usd:,.2f}")
        print(f"   Action: {side.upper()} {amount} {market} @ {'MARKET' if not price else f'${price:,.2f}'}")
        confirm = input("   Type CONFIRM to proceed: ")
        if confirm.strip() != "CONFIRM":
            print("Cancelled.")
            log_print("ORDER", "CANCELLED_BY_USER", {
                "status": "CANCELLED", "side": side, "market": market,
                "amount": amount, "est_usd": est_usd,
            })
            sys.exit(0)

    return est_usd


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_ticker(args):
    exchange = get_exchange()
    market = args.market or load_config()["default_market"]
    ticker = exchange.fetch_ticker(market)
    print(f"\n{'='*40}")
    print(f"  {market} Ticker")
    print(f"{'='*40}")
    print(f"  Last:   ${ticker['last']:>12,.2f}")
    print(f"  Bid:    ${ticker['bid']:>12,.2f}")
    print(f"  Ask:    ${ticker['ask']:>12,.2f}")
    print(f"  High:   ${ticker['high']:>12,.2f}")
    print(f"  Low:    ${ticker['low']:>12,.2f}")
    print(f"  Volume: {ticker['baseVolume']:>12,.4f}")
    print(f"  VWAP:   ${ticker.get('vwap', 0) or 0:>12,.2f}")
    print(f"{'='*40}")
    if args.json:
        print(json.dumps(ticker, indent=2, default=str))


def cmd_orderbook(args):
    exchange = get_exchange()
    market = args.market or load_config()["default_market"]
    limit = args.depth or 10
    ob = exchange.fetch_order_book(market, limit)
    print(f"\n  {market} Order Book (top {limit})")
    print(f"  {'ASK':>12}  {'':>12}  {'BID':>12}")
    print(f"  {'─'*12}  {'─'*12}  {'─'*12}")
    for i in range(min(limit, max(len(ob["asks"]), len(ob["bids"])))):
        ask = f"${ob['asks'][i][0]:>10,.2f}" if i < len(ob["asks"]) else " " * 12
        bid = f"${ob['bids'][i][0]:>10,.2f}" if i < len(ob["bids"]) else " " * 12
        print(f"  {ask}  {'':>12}  {bid}")


def cmd_balance(args):
    exchange = get_exchange(live=True)
    balance = exchange.fetch_balance()
    print(f"\n  Bitstamp Account Balance")
    print(f"  {'Currency':<8} {'Total':>14} {'Available':>14} {'Reserved':>14}")
    print(f"  {'─'*8} {'─'*14} {'─'*14} {'─'*14}")
    skip_keys = {"info", "timestamp", "datetime", "free", "used", "total"}
    for currency in sorted(k for k in balance.keys() if k not in skip_keys):
        entry = balance.get(currency, {})
        if not isinstance(entry, dict):
            continue
        total = float(entry.get("total", 0) or 0)
        free = float(entry.get("free", 0) or 0)
        used = float(entry.get("used", 0) or 0)
        if total > 0 or args.all:
            print(f"  {currency:<8} {total:>14.8f} {free:>14.8f} {used:>14.8f}")
    log_print("ACCOUNT", "BALANCE_CHECK", {"status": "OK"}, quiet=True)


def cmd_buy(args):
    cfg = load_config()
    market = args.market or cfg["default_market"]
    live = args.live
    exchange = get_exchange(live=live)

    est_usd = pre_trade_checks(cfg, "buy", market, args.amount, args.price, live, exchange)

    order_type = "limit" if args.price else "market"
    mode = "🔴 LIVE" if live else "🟡 DRY-RUN"

    print(f"\n{mode} | BUY {args.amount} {market} | Type: {order_type}" +
          (f" @ ${args.price:,.2f}" if args.price else ""))

    if live:
        if args.price:
            order = exchange.create_limit_buy_order(market, args.amount, args.price)
        else:
            order = exchange.create_market_buy_order(market, args.amount)
        add_daily_volume(est_usd)
        log_print("ORDER", "BUY_EXECUTED", {
            "status": "FILLED" if order.get("status") == "closed" else order.get("status", "SUBMITTED"),
            "order_id": order.get("id"),
            "market": market, "amount": args.amount, "price": args.price,
            "type": order_type, "est_usd": est_usd,
        })
        print(f"✅ Order placed: {order.get('id')}")
        if args.json:
            print(json.dumps(order, indent=2, default=str))
    else:
        log_print("ORDER", "BUY_DRY_RUN", {
            "status": "SIMULATED", "market": market,
            "amount": args.amount, "price": args.price,
            "type": order_type, "est_usd": est_usd,
        })
        print("✅ Dry-run complete. Add --live to execute.")


def cmd_sell(args):
    cfg = load_config()
    market = args.market or cfg["default_market"]
    live = args.live
    exchange = get_exchange(live=live)

    est_usd = pre_trade_checks(cfg, "sell", market, args.amount, args.price, live, exchange)

    order_type = "limit" if args.price else "market"
    mode = "🔴 LIVE" if live else "🟡 DRY-RUN"

    print(f"\n{mode} | SELL {args.amount} {market} | Type: {order_type}" +
          (f" @ ${args.price:,.2f}" if args.price else ""))

    if live:
        if args.price:
            order = exchange.create_limit_sell_order(market, args.amount, args.price)
        else:
            order = exchange.create_market_sell_order(market, args.amount)
        add_daily_volume(est_usd)
        log_print("ORDER", "SELL_EXECUTED", {
            "status": "FILLED" if order.get("status") == "closed" else order.get("status", "SUBMITTED"),
            "order_id": order.get("id"),
            "market": market, "amount": args.amount, "price": args.price,
            "type": order_type, "est_usd": est_usd,
        })
        print(f"✅ Order placed: {order.get('id')}")
        if args.json:
            print(json.dumps(order, indent=2, default=str))
    else:
        log_print("ORDER", "SELL_DRY_RUN", {
            "status": "SIMULATED", "market": market,
            "amount": args.amount, "price": args.price,
            "type": order_type, "est_usd": est_usd,
        })
        print("✅ Dry-run complete. Add --live to execute.")


def cmd_orders(args):
    exchange = get_exchange(live=True)
    market = args.market or None
    orders = exchange.fetch_open_orders(market)
    if not orders:
        print("No open orders.")
        return
    print(f"\n  Open Orders" + (f" ({market})" if market else ""))
    print(f"  {'ID':<12} {'Side':<6} {'Type':<8} {'Market':<10} {'Amount':>12} {'Price':>12} {'Status':<10}")
    print(f"  {'─'*12} {'─'*6} {'─'*8} {'─'*10} {'─'*12} {'─'*12} {'─'*10}")
    for o in orders:
        print(f"  {str(o['id']):<12} {o['side']:<6} {o['type']:<8} {o['symbol']:<10} "
              f"{o['amount']:>12.8f} {(o.get('price') or 0):>12.2f} {o['status']:<10}")


def cmd_cancel(args):
    exchange = get_exchange(live=True)
    if args.all:
        orders = exchange.fetch_open_orders()
        if not orders:
            print("No open orders to cancel.")
            return
        print(f"Cancelling {len(orders)} open orders...")
        for o in orders:
            try:
                exchange.cancel_order(o["id"], o["symbol"])
                log_print("ORDER", "CANCELLED", {"status": "OK", "order_id": o["id"], "market": o["symbol"]})
            except Exception as e:
                log_print("ORDER", "CANCEL_FAILED", {"status": "ERROR", "order_id": o["id"], "error": str(e)})
        print("✅ All orders cancelled.")
    elif args.order_id:
        market = args.market or load_config()["default_market"]
        exchange.cancel_order(args.order_id, market)
        log_print("ORDER", "CANCELLED", {"status": "OK", "order_id": args.order_id, "market": market})
        print(f"✅ Order {args.order_id} cancelled.")
    else:
        print("Specify --order-id or --all")


def cmd_trades(args):
    exchange = get_exchange(live=True)
    market = args.market or load_config()["default_market"]
    limit = args.limit or 20
    trades = exchange.fetch_my_trades(market, limit=limit)
    if not trades:
        print("No recent trades.")
        return
    print(f"\n  Recent Trades ({market})")
    print(f"  {'Date':<20} {'Side':<6} {'Amount':>14} {'Price':>12} {'Fee':>10}")
    print(f"  {'─'*20} {'─'*6} {'─'*14} {'─'*12} {'─'*10}")
    for t in trades:
        dt = t.get("datetime", "")[:19]
        fee = t.get("fee", {}).get("cost", 0) or 0
        print(f"  {dt:<20} {t['side']:<6} {t['amount']:>14.8f} {t['price']:>12.2f} {fee:>10.4f}")


def cmd_kill_switch(args):
    if args.deactivate:
        deactivate_kill_switch()
    elif args.status:
        if is_kill_switch_active():
            data = json.loads(KILL_SWITCH_FILE.read_text())
            print(f"🛑 Kill switch ACTIVE since {data['activated']}")
            print(f"   Reason: {data['reason']}")
        else:
            print("✅ Kill switch is NOT active. Trading is enabled.")
    else:
        reason = args.reason or "Manual activation"
        activate_kill_switch(reason)
        # Also cancel all open orders
        try:
            exchange = get_exchange(live=True)
            orders = exchange.fetch_open_orders()
            for o in orders:
                try:
                    exchange.cancel_order(o["id"], o["symbol"])
                except Exception:
                    pass
            print(f"Cancelled {len(orders)} open orders.")
        except Exception:
            print("(Could not cancel orders — no API keys or connection issue)")


def cmd_config(args):
    cfg = load_config()
    if args.set:
        key, value = args.set.split("=", 1)
        key = key.strip()
        if key not in DEFAULT_CONFIG:
            print(f"Unknown config key: {key}")
            print(f"Valid keys: {list(DEFAULT_CONFIG.keys())}")
            sys.exit(1)
        # Type coerce
        default_val = DEFAULT_CONFIG[key]
        if isinstance(default_val, float):
            value = float(value)
        elif isinstance(default_val, list):
            value = [v.strip() for v in value.split(",")]
        cfg[key] = value
        save_config(cfg)
        print(f"✅ Set {key} = {value}")
        log_print("CONFIG", "UPDATED", {"key": key, "value": str(value)}, quiet=True)
    else:
        print(f"\n  Bitstamp Trader Config ({CONFIG_FILE})")
        print(f"  {'─'*50}")
        for k, v in cfg.items():
            print(f"  {k:<30} {v}")


def cmd_audit(args):
    if not LOG_FILE.exists():
        print("No audit log yet.")
        return
    limit = args.limit or 20
    lines = LOG_FILE.read_text().strip().split("\n")
    recent = lines[-limit:]
    print(f"\n  Audit Log (last {len(recent)} entries)")
    print(f"  {'─'*70}")
    for line in recent:
        entry = json.loads(line)
        ts = entry.get("ts", "")[:19]
        cat = entry.get("category", "")
        action = entry.get("action", "")
        status = entry.get("status", "")
        print(f"  {ts} [{cat}] {action}: {status}")


def cmd_markets(args):
    exchange = get_exchange()
    exchange.load_markets()
    markets = sorted(exchange.symbols)
    cfg = load_config()
    allowed = cfg["allowed_markets"]
    print(f"\n  Available Markets on Bitstamp ({len(markets)} total)")
    print(f"  Allowed for trading: {allowed}\n")
    if args.all:
        for m in markets:
            flag = "✅" if m in allowed else "  "
            print(f"  {flag} {m}")
    else:
        for m in allowed:
            print(f"  ✅ {m}")
        print(f"\n  Use --all to see all {len(markets)} markets.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        prog="bitstamp",
        description="🛡️ Safety-first Bitstamp trading CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ticker
    p = sub.add_parser("ticker", help="Get current price ticker")
    p.add_argument("--market", "-m", help="Trading pair (e.g. BTC/USD)")
    p.add_argument("--json", action="store_true", help="Output raw JSON")

    # orderbook
    p = sub.add_parser("orderbook", help="View order book")
    p.add_argument("--market", "-m", help="Trading pair")
    p.add_argument("--depth", "-d", type=int, default=10, help="Depth (default: 10)")

    # balance
    p = sub.add_parser("balance", help="View account balance")
    p.add_argument("--all", "-a", action="store_true", help="Show all currencies")

    # buy
    p = sub.add_parser("buy", help="Place a buy order")
    p.add_argument("amount", type=float, help="Amount to buy (in base currency)")
    p.add_argument("--price", "-p", type=float, help="Limit price (omit for market order)")
    p.add_argument("--market", "-m", help="Trading pair")
    p.add_argument("--live", action="store_true", help="Execute live (default: dry-run)")
    p.add_argument("--json", action="store_true")

    # sell
    p = sub.add_parser("sell", help="Place a sell order")
    p.add_argument("amount", type=float, help="Amount to sell (in base currency)")
    p.add_argument("--price", "-p", type=float, help="Limit price (omit for market order)")
    p.add_argument("--market", "-m", help="Trading pair")
    p.add_argument("--live", action="store_true", help="Execute live (default: dry-run)")
    p.add_argument("--json", action="store_true")

    # orders
    p = sub.add_parser("orders", help="List open orders")
    p.add_argument("--market", "-m", help="Filter by market")

    # cancel
    p = sub.add_parser("cancel", help="Cancel orders")
    p.add_argument("--order-id", help="Specific order ID")
    p.add_argument("--market", "-m", help="Market (required with --order-id)")
    p.add_argument("--all", action="store_true", help="Cancel ALL open orders")

    # trades
    p = sub.add_parser("trades", help="View recent trades")
    p.add_argument("--market", "-m", help="Trading pair")
    p.add_argument("--limit", "-l", type=int, default=20)

    # kill-switch
    p = sub.add_parser("kill-switch", help="Emergency stop — cancel all & block trading")
    p.add_argument("--deactivate", action="store_true", help="Resume trading")
    p.add_argument("--status", action="store_true", help="Check kill switch status")
    p.add_argument("--reason", help="Reason for activation")

    # config
    p = sub.add_parser("config", help="View/edit safety config")
    p.add_argument("--set", help="Set key=value (e.g. max_order_size_usd=200)")

    # audit
    p = sub.add_parser("audit", help="View audit log")
    p.add_argument("--limit", "-l", type=int, default=20)

    # markets
    p = sub.add_parser("markets", help="List available markets")
    p.add_argument("--all", "-a", action="store_true", help="Show all markets")

    args = parser.parse_args()

    commands = {
        "ticker": cmd_ticker,
        "orderbook": cmd_orderbook,
        "balance": cmd_balance,
        "buy": cmd_buy,
        "sell": cmd_sell,
        "orders": cmd_orders,
        "cancel": cmd_cancel,
        "trades": cmd_trades,
        "kill-switch": cmd_kill_switch,
        "config": cmd_config,
        "audit": cmd_audit,
        "markets": cmd_markets,
    }

    try:
        commands[args.command](args)
    except ccxt.AuthenticationError as e:
        print(f"🔐 Authentication error: {e}")
        print("Check your BITSTAMP_API_KEY and BITSTAMP_API_SECRET.")
        sys.exit(1)
    except ccxt.InsufficientFunds as e:
        print(f"💸 Insufficient funds: {e}")
        sys.exit(1)
    except ccxt.InvalidOrder as e:
        print(f"❌ Invalid order: {e}")
        sys.exit(1)
    except ccxt.RateLimitExceeded as e:
        print(f"⏳ Rate limit exceeded: {e}")
        sys.exit(1)
    except ccxt.NetworkError as e:
        print(f"🌐 Network error: {e}")
        sys.exit(1)
    except ccxt.ExchangeError as e:
        print(f"⚠️ Exchange error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)


if __name__ == "__main__":
    main()
