#!/usr/bin/env python3
"""
Yahoo Finance Stock Price Fetcher
Fetches real-time and historical stock prices from Yahoo Finance
"""

import sys
import json
from datetime import datetime
import yfinance as yf

def fetch_stock_price(symbol, market='us'):
    """Fetch current stock price"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period='1d')

        current_price = hist['Close'].iloc[-1] if not hist.empty else None
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else None
        change = current_price - prev_close if prev_close else 0
        change_pct = (change / prev_close * 100) if prev_close else 0

        result = {
            'symbol': symbol,
            'name': info.get('longName', 'N/A'),
            'currency': info.get('currency', 'USD'),
            'current_price': round(float(current_price), 2) if current_price is not None else None,
            'previous_close': round(float(prev_close), 2) if prev_close is not None else None,
            'change': round(float(change), 2),
            'change_percent': round(float(change_pct), 2),
            'market_cap': int(info.get('marketCap')) if info.get('marketCap') is not None else None,
            'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else None,
            'high_52w': float(info.get('fiftyTwoWeekHigh')) if info.get('fiftyTwoWeekHigh') is not None else None,
            'low_52w': float(info.get('fiftyTwoWeekLow')) if info.get('fiftyTwoWeekLow') is not None else None,
            'fetched_at': datetime.now().isoformat()
        }

        return result

    except Exception as e:
        print(f"Error fetching {symbol}: {e}", file=sys.stderr)
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_yahoo.py <symbol> [--market japan|us]")
        sys.exit(1)

    symbol = sys.argv[1]
    market = 'japan' if '--market japan' in sys.argv else 'us'

    # Adjust symbol for Japan market
    if market == 'japan' and not symbol.endswith('.T'):
        symbol = f"{symbol}.T"

    print(f"Fetching stock price for {symbol} ({market} market)...")

    result = fetch_stock_price(symbol, market)

    if result:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Failed to fetch data for {symbol}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
