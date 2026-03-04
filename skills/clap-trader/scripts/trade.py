import ccxt
import os
import argparse
import sys
import datetime
import csv

LOG_FILE = 'skills/crypto_trader/logs/trade_history.csv'

def get_exchange():
    api_key = os.environ.get('BINANCE_API_KEY')
    api_secret = os.environ.get('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set.", file=sys.stderr)
        return None
        
    return ccxt.binance({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True,
    })

def log_trade(timestamp, symbol, side, amount, price, cost, type, status, is_dry_run):
    file_exists = os.path.isfile(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Symbol', 'Side', 'Amount', 'Price', 'Cost', 'Type', 'Status', 'DryRun'])
        
        writer.writerow([timestamp, symbol, side, amount, price, cost, type, status, is_dry_run])

def main():
    parser = argparse.ArgumentParser(description='Execute crypto trades on Binance.')
    parser.add_argument('--symbol', type=str, required=True, help='Trading pair symbol (e.g. ETH/USDT)')
    parser.add_argument('--side', type=str, required=True, choices=['buy', 'sell'], help='Order side')
    parser.add_argument('--amount', type=float, required=True, help='Amount to trade')
    parser.add_argument('--type', type=str, default='market', choices=['market', 'limit'], help='Order type')
    parser.add_argument('--price', type=float, help='Limit price (required for limit orders)')
    parser.add_argument('--dry-run', action='store_true', help='Simulate trade without executing')
    
    args = parser.parse_args()

    # Dry Run Logic
    if args.dry_run:
        print(f"DRY RUN: Would place {args.side} order for {args.amount} {args.symbol} at {args.type} price.")
        # Simulate a price for logging
        simulated_price = 0.0
        try:
            # Try to get current price for better simulation if keys exist, else 0
            exchange = get_exchange()
            if exchange:
                ticker = exchange.fetch_ticker(args.symbol)
                simulated_price = ticker['last']
        except:
            pass
            
        log_trade(datetime.datetime.now().isoformat(), args.symbol, args.side, args.amount, simulated_price, args.amount * simulated_price, args.type, 'simulated', True)
        return

    # Real Trade Logic
    exchange = get_exchange()
    if not exchange:
        sys.exit(1)

    try:
        # Check balance (optional but good practice)
        # balance = exchange.fetch_balance()
        # print(balance)

        order = None
        if args.type == 'market':
            order = exchange.create_market_order(args.symbol, args.side, args.amount)
        elif args.type == 'limit':
            if not args.price:
                print("Error: --price is required for limit orders.")
                sys.exit(1)
            order = exchange.create_limit_order(args.symbol, args.side, args.amount, args.price)

        print(f"Order placed successfully: {order['id']}")
        
        # Log successful trade
        log_trade(datetime.datetime.now().isoformat(), args.symbol, args.side, args.amount, order.get('price', 0), order.get('cost', 0), args.type, 'filled', False)

    except Exception as e:
        print(f"Trade failed: {e}", file=sys.stderr)
        log_trade(datetime.datetime.now().isoformat(), args.symbol, args.side, args.amount, 0, 0, args.type, f"failed: {str(e)}", False)
        sys.exit(1)

if __name__ == "__main__":
    main()
