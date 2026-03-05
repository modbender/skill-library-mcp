# Signal Generator Skill

Generate automated trading signals and send alerts to Discord/Telegram.

## 📋 Overview

This skill generates trading signals based on technical indicators and automatically sends alerts to your configured channels (Discord, Telegram, etc.).

## 🚀 Features

- **Multiple Strategies:**
  - **BB Breakout** - Bollinger Bands squeeze + breakout with volume spike
  - **RSI Reversal** - Overbought/Oversold reversal signals

- **Multi-Timeframe Support** - Run on 15m, 1h, 4h, etc.

- **Flexible Targets** - Send alerts to Discord, Telegram, or any OpenClaw channel

- **Easy Configuration** - Simple JSON config, no coding required

## 📦 Installation

1. Copy the skill directory to your OpenClaw workspace:
```bash
cp -r signal-generator ~/.openclaw/workspace/skills/
```

2. Configure your settings (see Configuration below)

3. Run the skill:
```bash
cd ~/.openclaw/workspace/skills/signal-generator
python3 signal_generator.py
```

## ⚙️ Configuration

Copy `config.json.example` to `config.json` and edit:

```json
{
  "symbol": "BTC/USDT",
  "strategy": "bb_breakout",
  "intervals": ["15m", "1h"],
  "targets": [
    "discord:your_channel_id",
    "telegram:your_chat_id"
  ],
  "filters": {
    "volume_spike": true,
    "trend_filter": false
  }
}
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `symbol` | Trading pair (e.g., BTC/USDT) | BTC/USDT |
| `strategy` | Strategy: `bb_breakout` or `rsi_reversal` | bb_breakout |
| `intervals` | Timeframes to check (e.g., `["15m", "1h"]`) | ["15m", "1h"] |
| `targets` | Where to send alerts (channel IDs) | [] |
| `filters.volume_spike` | Require volume spike for signals | true |
| `filters.trend_filter` | Apply trend filter (coming soon) | false |

## 🎯 Strategies

### BB Breakout (Default)

- **Logic:**
  1. BB Squeeze detected (BB inside Keltner Channels)
  2. Price closes outside Bollinger Bands
  3. Volume > 20-period average

- **Long Signal:** Close > BB Upper + Volume Spike
- **Short Signal:** Close < BB Lower + Volume Spike

### RSI Reversal

- **Logic:**
  1. RSI < 30 (Oversold) → Long
  2. RSI > 70 (Overbought) → Short

- **Long Signal:** RSI crosses below 30 then rises
- **Short Signal:** RSI crosses above 70 then falls

## 📊 Example Usage

### Manual Run

```bash
cd ~/.openclaw/workspace/skills/signal-generator
python3 signal_generator.py
```

Output:
```
📊 **BB Breakout** - BTC/USDT
⏱️ Interval: 15m
💰 Price: $77,564.10

🟢 LONG: False
🔴 SHORT: False

📈 BB Upper: $78,234.50
📉 BB Lower: $76,890.20
🔢 RSI: 52.34

🕐 2026-02-02T11:00:00
```

### Cron/Schedule

Run every 5 minutes:
```bash
*/5 * * * * cd ~/.openclaw/workspace/skills/signal-generator && python3 signal_generator.py
```

## 🔧 Troubleshooting

**No signals generated?**
- Check if `config.json` exists and is valid JSON
- Verify symbol is correct (e.g., BTC/USDT, not BTCUSDT)
- Check exchange connection (Binance API)

**Import errors?**
- Ensure `quant-trading-bot` is accessible:
```bash
ls /root/quant-trading-bot/src/exchange_api.py
```

## 📝 License

This skill is provided as-is. Use at your own risk. Trading signals are not financial advice.

## 🤝 Contributing

Have ideas for new strategies? Contributions welcome!

---

**Version:** 1.0.0
**Last Updated:** 2026-02-02
