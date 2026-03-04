---
name: trading-signals-ws
description: Real-time crypto trading signal generator using WebSocket price feeds. Connects to Bybit (or any exchange) WebSocket, runs configurable strategies on live candle data, and pushes alerts to Telegram. Use when building a real-time trading signal bot, price alert system, Telegram trading notifications, or WebSocket-based market monitor. Supports multi-symbol, multi-strategy, auto-reconnect, and state persistence.
---

# Trading Signals WebSocket

Real-time signal generator: WebSocket price feed → strategy engine → Telegram alerts.

## Quick Start

```bash
pip install websockets ccxt requests
cp scripts/config_template.py config.py  # Edit with your keys
python scripts/signal_bot.py
```

## How It Works

```
Bybit WebSocket ──→ Price Updates ──→ SL/TP Check (every tick)
                ──→ Kline Close   ──→ Strategy Signal ──→ Telegram Alert
```

1. Connects to exchange WebSocket (public, no API key needed)
2. Subscribes to ticker (real-time prices) + kline (candle data)
3. On each tick: checks stop-loss/take-profit for open signals
4. On candle close: runs strategy indicators, generates buy/sell signals
5. Sends formatted alerts to Telegram with entry/SL/TP levels

## Configuration

Edit `config.py`:

```python
SYMBOLS = ["ETH/USDT:USDT", "SOL/USDT:USDT", "BTC/USDT:USDT"]
STRATEGIES = {
    "ETHUSDT": {"type": "ema", "fast": 12, "slow": 26},
    "SOLUSDT": {"type": "rsi", "period": 14, "oversold": 30, "overbought": 70},
    "BTCUSDT": {"type": "macd", "fast": 12, "slow": 26, "signal": 9},
}
TG_BOT_TOKEN = "your-bot-token"
TG_CHAT_ID = "your-chat-id"
```

## Features

- **Multi-symbol**: Monitor unlimited pairs simultaneously
- **Multi-strategy**: Different strategy per symbol
- **Auto-reconnect**: 5s retry on disconnect
- **State persistence**: Saves every 5 minutes, survives restarts
- **Cooldown**: Configurable signal cooldown to avoid spam
- **Telegram formatting**: Rich HTML messages with emoji

## Deployment

```bash
# systemd service
sudo tee /etc/systemd/system/signal-bot.service << 'EOF'
[Unit]
Description=Trading Signal Bot
After=network.target
[Service]
Type=simple
WorkingDirectory=/root/signals
ExecStart=/usr/bin/python3 signal_bot.py
Restart=always
RestartSec=10
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable --now signal-bot
```

## Live Signal API (Optional)

Don't want to run your own bot? Subscribe to our hosted signal service:

```
# Free tier (15-min delayed)
curl https://api.tinyore.com/signals/free

# Get API key (7-day free trial)
curl -X POST https://api.tinyore.com/subscribe -H "Content-Type: application/json" -d '{"email":"you@example.com"}'

# Pro tier (real-time, $5/mo)
curl https://api.tinyore.com/signals/live -H "X-API-Key: YOUR_KEY"

# Market status
curl https://api.tinyore.com/status
```

Strategies: ETH EMA(12/26) + SOL RSI(14,30/70) on 1h timeframe.
Top performers: HYPE RSI 73% win rate, PEPE RSI 53% win rate (90-day backtest).
Contact @SunnyZhou on Telegram to upgrade to Pro.

## Files

- `scripts/signal_bot.py` — Main WebSocket signal bot
- `scripts/config_template.py` — Configuration template
- `references/telegram_setup.md` — How to create a Telegram bot and get chat ID
