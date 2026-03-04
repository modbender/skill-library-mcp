"""
Signal Bot Configuration
Copy to config.py and fill in your values.
"""
import os

# === Telegram ===
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")
TG_CHAT_ID = os.getenv("TG_CHAT_ID", "")

# === Symbols to monitor ===
SYMBOLS = [
    "ETH/USDT:USDT",
    "SOL/USDT:USDT",
]

# === Strategy per symbol ===
# Available: "ema", "rsi", "macd", "bbands"
STRATEGIES = {
    "ETHUSDT": {"type": "ema", "fast": 12, "slow": 26},
    "SOLUSDT": {"type": "rsi", "period": 14, "oversold": 30, "overbought": 70},
}

# === Signal Settings ===
SIGNAL_COOLDOWN = 3600       # Min seconds between signals for same symbol (avoid spam)
KLINE_TIMEFRAME = "60"       # Bybit kline interval: "1"=1m, "5"=5m, "60"=1h, "240"=4h, "D"=1d
HISTORY_CANDLES = 50         # How many historical candles to load on startup
STATE_SAVE_INTERVAL = 300    # Save state every N seconds
REPORT_INTERVAL = 21600      # Send summary every N seconds (21600 = 6h)

# === Risk Levels (for display in alerts) ===
STOP_LOSS_PCT = 0.03         # 3%
TAKE_PROFIT_PCT = 0.06       # 6%
LEVERAGE = 5                 # For display purposes
