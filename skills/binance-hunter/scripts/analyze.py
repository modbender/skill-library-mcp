import ccxt
import pandas as pd
import ta
import sys
import json

# === Configuration ===
EXCHANGE = ccxt.binance()
TIMEFRAME_HIGH = '1d'
TIMEFRAME_MID = '4h'
TIMEFRAME_LOW = '15m'

def analyze(symbol):
    try:
        # Load Data
        df_high = fetch_data(symbol, TIMEFRAME_HIGH, 50)
        df_mid = fetch_data(symbol, TIMEFRAME_MID, 50)
        df_low = fetch_data(symbol, TIMEFRAME_LOW, 50)

        # 1. Trend (Daily)
        ema_daily = ta.trend.EMAIndicator(close=df_high['close'], window=20).ema_indicator().iloc[-1]
        daily_bullish = df_high['close'].iloc[-1] > ema_daily

        # 2. Momentum (4H)
        macd = ta.trend.MACD(close=df_mid['close'])
        macd_bullish = macd.macd().iloc[-1] > macd.macd_signal().iloc[-1]

        # 3. Trigger (15m)
        rsi = ta.momentum.RSIIndicator(close=df_low['close'], window=14).rsi().iloc[-1]
        bb = ta.volatility.BollingerBands(close=df_low['close'], window=20, window_dev=2)
        price = df_low['close'].iloc[-1]
        
        # Result
        status = "NEUTRAL"
        action = "WAIT"
        
        if daily_bullish and macd_bullish:
            status = "BULLISH 🟢"
            if rsi < 45 or price <= bb.bollinger_lband().iloc[-1]:
                action = "BUY (LONG) 🚀"
        elif not daily_bullish and not macd_bullish:
            status = "BEARISH 🔴"
            if rsi > 55 or price >= bb.bollinger_hband().iloc[-1]:
                action = "SELL (SHORT) 📉"

        return {
            "symbol": symbol,
            "price": price,
            "trend": status,
            "action": action,
            "rsi": round(rsi, 1)
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_data(symbol, timeframe, limit):
    ohlcv = EXCHANGE.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTC/USDT"
    print(json.dumps(analyze(symbol), indent=2))
