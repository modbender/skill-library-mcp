#!/usr/bin/env python3
"""
Alpaca Trading CLI - Trade stocks and crypto via Alpaca API.
Supports paper and live trading, market data, and portfolio management.
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timedelta, time
from pathlib import Path
from zoneinfo import ZoneInfo

# Alerts storage
ALERTS_FILE = Path.home() / ".openclaw" / "data" / "alpaca-alerts.json"

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import (
        MarketOrderRequest, LimitOrderRequest, StopOrderRequest, StopLimitOrderRequest,
        GetOrdersRequest
    )
    from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus, QueryOrderStatus
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestQuoteRequest, StockBarsRequest
    from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
    from alpaca.data.live import StockDataStream
    HAS_STREAM = True
    try:
        from alpaca.data.requests import StockNewsRequest
        HAS_NEWS = True
    except ImportError:
        HAS_NEWS = False
except ImportError as e:
    print(f"Error: alpaca-py not installed or import error: {e}")
    print("Run: pip install alpaca-py")
    sys.exit(1)


def get_market_session():
    """
    Determine current market session based on Eastern Time.
    Returns: (session_type, is_open, message)
    session_type: 'pre-market', 'regular', 'after-hours', 'closed'
    """
    et = ZoneInfo("America/New_York")
    now = datetime.now(et)
    current_time = now.time()
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    # Weekend check
    if weekday >= 5:  # Saturday or Sunday
        return ('closed', False, 'Markets are closed (weekend)')
    
    # Define market hours (Eastern Time)
    pre_market_start = time(4, 0)    # 4:00 AM ET
    regular_open = time(9, 30)        # 9:30 AM ET
    regular_close = time(16, 0)       # 4:00 PM ET
    after_hours_end = time(20, 0)     # 8:00 PM ET
    
    if current_time < pre_market_start:
        return ('closed', False, 'Markets are closed (before pre-market)')
    elif current_time < regular_open:
        return ('pre-market', False, f'Pre-market session (4:00 AM - 9:30 AM ET)')
    elif current_time < regular_close:
        return ('regular', True, 'Regular market hours')
    elif current_time < after_hours_end:
        return ('after-hours', False, f'After-hours session (4:00 PM - 8:00 PM ET)')
    else:
        return ('closed', False, 'Markets are closed (after extended hours)')


def load_credentials():
    """Load Alpaca credentials from environment or config file."""
    api_key = os.environ.get("ALPACA_API_KEY")
    secret_key = os.environ.get("ALPACA_SECRET_KEY")
    paper = os.environ.get("ALPACA_PAPER", "true").lower() == "true"
    
    if not api_key or not secret_key:
        config_path = Path.home() / ".openclaw" / "credentials" / "alpaca.json"
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                api_key = config.get("apiKey")
                secret_key = config.get("secretKey")
                paper = config.get("paper", True)
    
    if not api_key or not secret_key:
        print("Error: Alpaca credentials not found.")
        print("Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables,")
        print("or create ~/.openclaw/credentials/alpaca.json")
        sys.exit(1)
    
    return api_key, secret_key, paper


def get_trading_client():
    """Get authenticated trading client."""
    api_key, secret_key, paper = load_credentials()
    return TradingClient(api_key, secret_key, paper=paper)


def get_data_client():
    """Get authenticated data client."""
    api_key, secret_key, _ = load_credentials()
    return StockHistoricalDataClient(api_key, secret_key)


def parse_timeframe(tf_str):
    """Parse timeframe string to TimeFrame object."""
    tf_map = {
        "1min": TimeFrame(1, TimeFrameUnit.Minute),
        "5min": TimeFrame(5, TimeFrameUnit.Minute),
        "15min": TimeFrame(15, TimeFrameUnit.Minute),
        "30min": TimeFrame(30, TimeFrameUnit.Minute),
        "1hour": TimeFrame(1, TimeFrameUnit.Hour),
        "4hour": TimeFrame(4, TimeFrameUnit.Hour),
        "1day": TimeFrame(1, TimeFrameUnit.Day),
        "1week": TimeFrame(1, TimeFrameUnit.Week),
        "1month": TimeFrame(1, TimeFrameUnit.Month),
    }
    return tf_map.get(tf_str.lower(), TimeFrame(1, TimeFrameUnit.Day))


def cmd_account(args):
    """Show account information."""
    client = get_trading_client()
    account = client.get_account()
    
    print(f"Account Status: {account.status}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Equity: ${float(account.equity):,.2f}")
    print(f"Long Market Value: ${float(account.long_market_value):,.2f}")
    print(f"Short Market Value: ${float(account.short_market_value):,.2f}")
    print(f"Day Trade Count: {account.daytrade_count}")
    print(f"Pattern Day Trader: {account.pattern_day_trader}")


def cmd_positions(args):
    """List all positions."""
    client = get_trading_client()
    positions = client.get_all_positions()
    
    if not positions:
        print("No open positions.")
        return
    
    print(f"{'Symbol':<8} {'Qty':>10} {'Avg Cost':>12} {'Current':>12} {'P/L':>12} {'P/L %':>8}")
    print("-" * 64)
    
    for pos in positions:
        symbol = pos.symbol
        qty = float(pos.qty)
        avg_cost = float(pos.avg_entry_price)
        current = float(pos.current_price)
        pl = float(pos.unrealized_pl)
        pl_pct = float(pos.unrealized_plpc) * 100
        
        pl_str = f"${pl:,.2f}" if pl >= 0 else f"-${abs(pl):,.2f}"
        print(f"{symbol:<8} {qty:>10.2f} ${avg_cost:>10.2f} ${current:>10.2f} {pl_str:>12} {pl_pct:>7.2f}%")


def cmd_quote(args):
    """Get latest quote for symbols."""
    client = get_data_client()
    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    
    request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
    quotes = client.get_stock_latest_quote(request)
    
    print(f"{'Symbol':<8} {'Bid':>12} {'Ask':>12} {'Spread':>10}")
    print("-" * 44)
    
    for symbol, quote in quotes.items():
        bid = float(quote.bid_price)
        ask = float(quote.ask_price)
        spread = ask - bid
        print(f"{symbol:<8} ${bid:>10.2f} ${ask:>10.2f} ${spread:>8.4f}")


def cmd_bars(args):
    """Get historical bars for a symbol."""
    client = get_data_client()
    symbol = args.symbol.upper()
    timeframe = parse_timeframe(args.timeframe)
    
    end = datetime.now()
    if args.start:
        start = datetime.fromisoformat(args.start)
    else:
        start = end - timedelta(days=30)
    
    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start=start,
        end=end,
        limit=args.limit
    )
    bars = client.get_stock_bars(request)
    
    if symbol not in bars or not bars[symbol]:
        print(f"No data for {symbol}")
        return
    
    print(f"{'Timestamp':<20} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12}")
    print("-" * 76)
    
    for bar in bars[symbol]:
        ts = bar.timestamp.strftime("%Y-%m-%d %H:%M")
        print(f"{ts:<20} ${bar.open:>8.2f} ${bar.high:>8.2f} ${bar.low:>8.2f} ${bar.close:>8.2f} {bar.volume:>12,}")


def cmd_order(args):
    """Place an order."""
    client = get_trading_client()
    data_client = get_data_client()
    
    side = OrderSide.BUY if args.side.lower() == "buy" else OrderSide.SELL
    symbol = args.symbol.upper()
    qty = float(args.qty)
    force = getattr(args, 'force', False)
    
    # === GUARDRAIL 1: Symbol validation ===
    try:
        quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quotes = data_client.get_stock_latest_quote(quote_request)
        if symbol not in quotes:
            print(f"❌ Error: Symbol '{symbol}' not found or no market data available.")
            return
        quote = quotes[symbol]
        bid = float(quote.bid_price) if quote.bid_price else 0
        ask = float(quote.ask_price) if quote.ask_price else 0
        current_price = ask if side == OrderSide.BUY else bid
    except Exception as e:
        print(f"❌ Error: Could not validate symbol '{symbol}': {e}")
        return
    
    # === GUARDRAIL 2: Buying power check (for buys) ===
    if side == OrderSide.BUY:
        account = client.get_account()
        buying_power = float(account.buying_power)
        
        # Estimate cost
        estimated_price = args.limit if args.limit else ask
        estimated_cost = qty * estimated_price if estimated_price > 0 else 0
        
        if estimated_cost > buying_power:
            print(f"❌ Error: Insufficient buying power.")
            print(f"   Order cost: ${estimated_cost:,.2f}")
            print(f"   Buying power: ${buying_power:,.2f}")
            max_shares = int(buying_power / estimated_price) if estimated_price > 0 else 0
            print(f"   Max shares you can buy: {max_shares}")
            return
    
    # === GUARDRAIL 3: Duplicate order detection ===
    open_orders_request = GetOrdersRequest(status=QueryOrderStatus.OPEN)
    open_orders = client.get_orders(open_orders_request)
    duplicate_orders = [o for o in open_orders if o.symbol == symbol and o.side == side]
    
    if duplicate_orders and not force:
        print(f"⚠️  Warning: You already have {len(duplicate_orders)} open {side.name} order(s) for {symbol}:")
        for o in duplicate_orders:
            o_qty = float(o.qty) if o.qty else 0
            o_price = f"@ ${float(o.limit_price):.2f}" if o.limit_price else "(market)"
            print(f"   - {o_qty:.0f} shares {o_price}")
        confirm = input("   Place another order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
    
    # === GUARDRAIL 4: Limit price validation ===
    if args.limit:
        if side == OrderSide.BUY and args.limit > ask and ask > 0:
            print(f"⚠️  Warning: Buy limit ${args.limit:.2f} is ABOVE current ask ${ask:.2f}")
            print(f"   This will likely fill immediately at ~${ask:.2f}")
            print(f"   Suggested: Set limit at or below ${ask:.2f}")
            if not force:
                confirm = input("   Proceed anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Order cancelled.")
                    return
                    
        elif side == OrderSide.SELL and args.limit < bid and bid > 0:
            print(f"⚠️  Warning: Sell limit ${args.limit:.2f} is BELOW current bid ${bid:.2f}")
            print(f"   This will likely fill immediately at ~${bid:.2f}")
            print(f"   Suggested: Set limit at or above ${bid:.2f}")
            if not force:
                confirm = input("   Proceed anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Order cancelled.")
                    return
    
    # === GUARDRAIL 5: Market hours check ===
    session_type, is_regular_hours, session_msg = get_market_session()
    extended_hours = False
    
    if not is_regular_hours and not force:
        print(f"\n⏰ Market Status: {session_msg}")
        
        if session_type == 'pre-market':
            print("   Regular market opens at 9:30 AM ET.")
            print("   Options:")
            print("   [1] Place pre-market order (executes now if filled)")
            print("   [2] Place regular hours order (queues until 9:30 AM)")
            print("   [3] Cancel")
            choice = input("   Choice (1/2/3): ").strip()
            if choice == '1':
                extended_hours = True
                print("   → Pre-market order selected")
            elif choice == '2':
                extended_hours = False
                print("   → Regular hours order selected (will queue)")
            else:
                print("Order cancelled.")
                return
                
        elif session_type == 'after-hours':
            print("   Regular market closed at 4:00 PM ET.")
            print("   Options:")
            print("   [1] Place after-hours order (executes now if filled)")
            print("   [2] Place regular hours order (queues until tomorrow 9:30 AM)")
            print("   [3] Cancel")
            choice = input("   Choice (1/2/3): ").strip()
            if choice == '1':
                extended_hours = True
                print("   → After-hours order selected")
            elif choice == '2':
                extended_hours = False
                print("   → Regular hours order selected (will queue)")
            else:
                print("Order cancelled.")
                return
                
        elif session_type == 'closed':
            print("   Your order will queue until next market open (9:30 AM ET).")
            if not force:
                confirm = input("   Continue? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("Order cancelled.")
                    return
    
    # === GUARDRAIL 6: Cost basis display & confirmation ===
    if args.limit:
        order_price = args.limit
        total_cost = qty * order_price
        print(f"\n📋 Order Summary:")
        print(f"   {side.name} {int(qty)} {symbol} @ ${order_price:.2f} limit")
        print(f"   Total: ${total_cost:,.2f}")
    elif args.stop:
        print(f"\n📋 Order Summary:")
        print(f"   {side.name} {int(qty)} {symbol} @ ${args.stop:.2f} stop")
    else:
        estimated_total = qty * current_price if current_price > 0 else 0
        print(f"\n📋 Order Summary:")
        print(f"   {side.name} {int(qty)} {symbol} @ MARKET (~${current_price:.2f})")
        print(f"   Estimated total: ${estimated_total:,.2f}")
    
    if not force:
        confirm = input("   Confirm order? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Order cancelled.")
            return
    
    # === Build and submit order ===
    if args.limit and args.stop:
        # Stop-limit order
        request = StopLimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
            limit_price=args.limit,
            stop_price=args.stop,
            extended_hours=extended_hours
        )
        order_type = "stop-limit"
    elif args.limit:
        # Limit order
        request = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
            limit_price=args.limit,
            extended_hours=extended_hours
        )
        order_type = "limit"
    elif args.stop:
        # Stop order
        request = StopOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
            stop_price=args.stop,
            extended_hours=extended_hours
        )
        order_type = "stop"
    else:
        # Market order (note: market orders don't support extended hours)
        if extended_hours:
            print("⚠️  Note: Market orders don't support extended hours. Converting to limit order at current price.")
            request = LimitOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=current_price,
                extended_hours=True
            )
            order_type = "limit (converted from market)"
        else:
            request = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            order_type = "market"
    
    order = client.submit_order(request)
    
    print(f"Order Submitted!")
    print(f"  ID: {order.id}")
    print(f"  Symbol: {order.symbol}")
    print(f"  Side: {order.side}")
    print(f"  Qty: {order.qty}")
    print(f"  Type: {order_type}")
    print(f"  Status: {order.status}")
    if args.limit:
        print(f"  Limit Price: ${args.limit:.2f}")
    if args.stop:
        print(f"  Stop Price: ${args.stop:.2f}")
    if extended_hours:
        print(f"  Extended Hours: Yes")


def cmd_orders(args):
    """List orders."""
    client = get_trading_client()
    
    status_map = {
        "open": QueryOrderStatus.OPEN,
        "closed": QueryOrderStatus.CLOSED,
        "all": QueryOrderStatus.ALL
    }
    
    request = GetOrdersRequest(
        status=status_map.get(args.status, QueryOrderStatus.OPEN),
        limit=args.limit
    )
    orders = client.get_orders(request)
    
    if not orders:
        print("No orders found.")
        return
    
    print(f"{'ID':<36} {'Symbol':<8} {'Side':<6} {'Qty':>8} {'Type':<10} {'Status':<12}")
    print("-" * 84)
    
    for order in orders:
        symbol = order.symbol or "N/A"
        qty = float(order.qty) if order.qty else 0
        order_type = order.order_type.name if order.order_type else "N/A"
        print(f"{order.id} {symbol:<8} {order.side.name:<6} {qty:>8.2f} {order_type:<10} {order.status.name:<12}")


def cmd_cancel(args):
    """Cancel an order or all orders."""
    client = get_trading_client()
    
    if args.order_id.lower() == "all":
        client.cancel_orders()
        print("All open orders cancelled.")
    else:
        client.cancel_order_by_id(args.order_id)
        print(f"Order {args.order_id} cancelled.")


def cmd_news(args):
    """Get news for symbols."""
    if not HAS_NEWS:
        print("News feature not available in this alpaca-py version.")
        print("Try: pip install alpaca-py --upgrade")
        return
    
    client = get_data_client()
    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    
    request = StockNewsRequest(
        symbols=symbols,
        limit=args.limit
    )
    news = client.get_stock_news(request)
    
    if not news.news:
        print("No news found.")
        return
    
    for article in news.news:
        print(f"\n[{article.created_at.strftime('%Y-%m-%d %H:%M')}] {article.headline}")
        print(f"  Source: {article.source}")
        print(f"  Symbols: {', '.join(article.symbols)}")
        print(f"  URL: {article.url}")


def cmd_stream(args):
    """Stream live market data via websocket."""
    api_key, secret_key, _ = load_credentials()
    symbols = [s.strip().upper() for s in args.symbols.split(",")]
    
    # Create stream client
    stream = StockDataStream(api_key, secret_key)
    
    # Handler for quotes
    async def quote_handler(data):
        ts = data.timestamp.strftime("%H:%M:%S")
        print(f"[{ts}] {data.symbol} QUOTE: bid=${data.bid_price:.2f} x {data.bid_size} | ask=${data.ask_price:.2f} x {data.ask_size}")
    
    # Handler for trades
    async def trade_handler(data):
        ts = data.timestamp.strftime("%H:%M:%S")
        print(f"[{ts}] {data.symbol} TRADE: ${data.price:.2f} x {data.size} ({data.exchange})")
    
    # Handler for bars
    async def bar_handler(data):
        ts = data.timestamp.strftime("%H:%M:%S")
        print(f"[{ts}] {data.symbol} BAR: O=${data.open:.2f} H=${data.high:.2f} L=${data.low:.2f} C=${data.close:.2f} V={data.volume}")
    
    # Subscribe based on data type
    data_type = args.type.lower()
    
    print(f"Streaming {data_type} data for: {', '.join(symbols)}")
    print("Press Ctrl+C to stop\n")
    
    if data_type == "quotes":
        stream.subscribe_quotes(quote_handler, *symbols)
    elif data_type == "trades":
        stream.subscribe_trades(trade_handler, *symbols)
    elif data_type == "bars":
        stream.subscribe_bars(bar_handler, *symbols)
    elif data_type == "all":
        stream.subscribe_quotes(quote_handler, *symbols)
        stream.subscribe_trades(trade_handler, *symbols)
        stream.subscribe_bars(bar_handler, *symbols)
    
    try:
        stream.run()
    except KeyboardInterrupt:
        print("\nStopping stream...")


def cmd_watchlist(args):
    """Manage watchlists."""
    client = get_trading_client()
    
    if args.watchlist_action == "list":
        watchlists = client.get_watchlists()
        if not watchlists:
            print("No watchlists.")
            return
        for wl in watchlists:
            symbols = ", ".join([a.symbol for a in wl.assets]) if wl.assets else "empty"
            print(f"{wl.id}: {wl.name} [{symbols}]")
    
    elif args.watchlist_action == "create":
        if not args.name or not args.symbols:
            print("Error: --name and symbols required for create")
            return
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
        wl = client.create_watchlist(args.name, symbols)
        print(f"Created watchlist: {wl.id} - {wl.name}")
    
    elif args.watchlist_action == "add":
        if not args.watchlist_id or not args.symbol:
            print("Error: watchlist_id and symbol required")
            return
        client.add_asset_to_watchlist_by_id(args.watchlist_id, args.symbol.upper())
        print(f"Added {args.symbol.upper()} to watchlist")
    
    elif args.watchlist_action == "delete":
        if not args.watchlist_id:
            print("Error: watchlist_id required")
            return
        client.delete_watchlist_by_id(args.watchlist_id)
        print(f"Deleted watchlist {args.watchlist_id}")


def load_alerts():
    """Load alerts from file."""
    if ALERTS_FILE.exists():
        with open(ALERTS_FILE) as f:
            return json.load(f)
    return {"alerts": []}


def save_alerts(data):
    """Save alerts to file."""
    ALERTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERTS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def cmd_alert(args):
    """Manage price alerts."""
    
    if args.alert_action == "add":
        symbol = args.symbol.upper()
        target_price = args.price
        condition = args.condition  # 'above' or 'below'
        
        # Validate symbol and get current price
        try:
            data_client = get_data_client()
            quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            quotes = data_client.get_stock_latest_quote(quote_request)
            if symbol not in quotes:
                print(f"❌ Error: Symbol '{symbol}' not found.")
                return
            quote = quotes[symbol]
            current_price = float(quote.ask_price) if quote.ask_price else float(quote.bid_price)
        except Exception as e:
            print(f"❌ Error validating symbol: {e}")
            return
        
        # Validate condition makes sense
        if condition == 'above' and target_price <= current_price:
            print(f"⚠️  Warning: {symbol} is already at ${current_price:.2f}, above your target ${target_price:.2f}")
            confirm = input("   Create alert anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Alert cancelled.")
                return
        elif condition == 'below' and target_price >= current_price:
            print(f"⚠️  Warning: {symbol} is already at ${current_price:.2f}, below your target ${target_price:.2f}")
            confirm = input("   Create alert anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Alert cancelled.")
                return
        
        # Create alert
        alert = {
            "id": str(uuid.uuid4())[:8],
            "symbol": symbol,
            "condition": condition,
            "target_price": target_price,
            "created_at": datetime.now().isoformat(),
            "current_price_at_creation": current_price,
            "triggered": False
        }
        
        data = load_alerts()
        data["alerts"].append(alert)
        save_alerts(data)
        
        print(f"✅ Alert created!")
        print(f"   ID: {alert['id']}")
        print(f"   {symbol} {condition} ${target_price:.2f}")
        print(f"   Current price: ${current_price:.2f}")
        
    elif args.alert_action == "list":
        data = load_alerts()
        alerts = [a for a in data["alerts"] if not a.get("triggered", False)]
        
        if not alerts:
            print("No active alerts.")
            return
        
        print(f"{'ID':<10} {'Symbol':<8} {'Condition':<8} {'Target':>12} {'Created':<20}")
        print("-" * 62)
        for a in alerts:
            created = a.get("created_at", "")[:16].replace("T", " ")
            print(f"{a['id']:<10} {a['symbol']:<8} {a['condition']:<8} ${a['target_price']:>10.2f} {created:<20}")
    
    elif args.alert_action == "remove":
        alert_id = args.alert_id
        data = load_alerts()
        
        original_count = len(data["alerts"])
        data["alerts"] = [a for a in data["alerts"] if a["id"] != alert_id]
        
        if len(data["alerts"]) == original_count:
            print(f"❌ Alert '{alert_id}' not found.")
            return
        
        save_alerts(data)
        print(f"✅ Alert '{alert_id}' removed.")
    
    elif args.alert_action == "clear":
        data = {"alerts": []}
        save_alerts(data)
        print("✅ All alerts cleared.")
    
    elif args.alert_action == "check":
        # Check all alerts against current prices (called by cron)
        data = load_alerts()
        alerts = [a for a in data["alerts"] if not a.get("triggered", False)]
        
        if not alerts:
            print("No active alerts to check.")
            return
        
        # Get unique symbols
        symbols = list(set(a["symbol"] for a in alerts))
        
        try:
            data_client = get_data_client()
            quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
            quotes = data_client.get_stock_latest_quote(quote_request)
        except Exception as e:
            print(f"❌ Error fetching quotes: {e}")
            return
        
        triggered = []
        for alert in alerts:
            symbol = alert["symbol"]
            if symbol not in quotes:
                continue
            
            quote = quotes[symbol]
            current_price = float(quote.ask_price) if quote.ask_price else float(quote.bid_price)
            
            condition_met = False
            if alert["condition"] == "above" and current_price >= alert["target_price"]:
                condition_met = True
            elif alert["condition"] == "below" and current_price <= alert["target_price"]:
                condition_met = True
            
            if condition_met:
                alert["triggered"] = True
                alert["triggered_at"] = datetime.now().isoformat()
                alert["triggered_price"] = current_price
                triggered.append(alert)
        
        save_alerts(data)
        
        if triggered:
            print("🚨 ALERTS TRIGGERED:")
            for a in triggered:
                print(f"   {a['symbol']} hit ${a['triggered_price']:.2f} ({a['condition']} ${a['target_price']:.2f})")
            # Output in a format that can be parsed for notifications
            print("\n---TRIGGERED_ALERTS_JSON---")
            print(json.dumps(triggered))
        else:
            print(f"Checked {len(alerts)} alerts. None triggered.")


def main():
    parser = argparse.ArgumentParser(description="Alpaca Trading CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Account
    subparsers.add_parser("account", help="Show account info")
    
    # Positions
    subparsers.add_parser("positions", help="List positions")
    
    # Quote
    quote_parser = subparsers.add_parser("quote", help="Get quote")
    quote_parser.add_argument("symbols", help="Comma-separated symbols")
    
    # Bars
    bars_parser = subparsers.add_parser("bars", help="Get historical bars")
    bars_parser.add_argument("symbol", help="Symbol")
    bars_parser.add_argument("--timeframe", default="1Day", help="Timeframe (1Min, 5Min, 1Hour, 1Day, etc.)")
    bars_parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    bars_parser.add_argument("--limit", type=int, default=20, help="Max bars")
    
    # Order
    order_parser = subparsers.add_parser("order", help="Place order")
    order_parser.add_argument("side", choices=["buy", "sell"], help="Buy or sell")
    order_parser.add_argument("symbol", help="Symbol")
    order_parser.add_argument("qty", type=float, help="Quantity")
    order_parser.add_argument("--limit", type=float, help="Limit price")
    order_parser.add_argument("--stop", type=float, help="Stop price")
    order_parser.add_argument("--force", action="store_true", help="Skip price validation warnings")
    
    # Orders
    orders_parser = subparsers.add_parser("orders", help="List orders")
    orders_parser.add_argument("--status", default="open", choices=["open", "closed", "all"])
    orders_parser.add_argument("--limit", type=int, default=50)
    
    # Cancel
    cancel_parser = subparsers.add_parser("cancel", help="Cancel order")
    cancel_parser.add_argument("order_id", help="Order ID or 'all'")
    
    # News
    news_parser = subparsers.add_parser("news", help="Get news")
    news_parser.add_argument("symbols", help="Comma-separated symbols")
    news_parser.add_argument("--limit", type=int, default=10)
    
    # Watchlist
    wl_parser = subparsers.add_parser("watchlist", help="Manage watchlists")
    wl_parser.add_argument("watchlist_action", choices=["list", "create", "add", "delete"])
    wl_parser.add_argument("--name", help="Watchlist name (for create)")
    wl_parser.add_argument("--symbols", help="Comma-separated symbols (for create)")
    wl_parser.add_argument("--watchlist_id", help="Watchlist ID")
    wl_parser.add_argument("--symbol", help="Single symbol (for add)")
    
    # Stream (live data)
    stream_parser = subparsers.add_parser("stream", help="Stream live market data")
    stream_parser.add_argument("symbols", help="Comma-separated symbols")
    stream_parser.add_argument("--type", default="trades", choices=["quotes", "trades", "bars", "all"],
                               help="Data type to stream")
    
    # Alerts
    alert_parser = subparsers.add_parser("alert", help="Manage price alerts")
    alert_parser.add_argument("alert_action", choices=["add", "list", "remove", "clear", "check"],
                              help="Alert action")
    alert_parser.add_argument("--symbol", help="Stock symbol (for add)")
    alert_parser.add_argument("--price", type=float, help="Target price (for add)")
    alert_parser.add_argument("--condition", choices=["above", "below"], default="above",
                              help="Trigger when price goes above or below target")
    alert_parser.add_argument("--alert_id", help="Alert ID (for remove)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "account": cmd_account,
        "positions": cmd_positions,
        "quote": cmd_quote,
        "bars": cmd_bars,
        "order": cmd_order,
        "orders": cmd_orders,
        "cancel": cmd_cancel,
        "news": cmd_news,
        "watchlist": cmd_watchlist,
        "stream": cmd_stream,
        "alert": cmd_alert,
    }
    
    commands[args.command](args)


if __name__ == "__main__":
    main()
