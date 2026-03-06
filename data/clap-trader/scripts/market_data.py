import ccxt
import pandas as pd
import pandas_ta as ta
import argparse
import json
import sys

def fetch_market_data(symbol='ETH/USDT', timeframe='1h', limit=100):
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

def calculate_indicators(df):
    # RSI
    df['RSI'] = df.ta.rsi(length=14)
    
    # MACD
    macd = df.ta.macd(fast=12, slow=26, signal=9)
    df = pd.concat([df, macd], axis=1)
    
    # EMA
    df['EMA_50'] = df.ta.ema(length=50)
    df['EMA_200'] = df.ta.ema(length=200)

    # Bollinger Bands
    bbands = df.ta.bbands(length=20)
    df = pd.concat([df, bbands], axis=1)

    return df

def main():
    parser = argparse.ArgumentParser(description='Fetch crypto market data and indicators.')
    parser.add_argument('--symbol', type=str, default='ETH/USDT', help='Trading pair symbol')
    parser.add_argument('--timeframe', type=str, default='1h', help='Timeframe for candles')
    args = parser.parse_args()

    df = fetch_market_data(args.symbol, args.timeframe)
    df = calculate_indicators(df)

    # Get the latest row
    latest = df.iloc[-1].to_dict()
    
    # Clean up timestamp for JSON serialization
    latest['timestamp'] = str(latest['timestamp'])
    
    # Output JSON
    print(json.dumps(latest, indent=2))

if __name__ == "__main__":
    main()
