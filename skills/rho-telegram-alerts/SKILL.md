---
name: telegram-alerts
version: 1.0.0
description: Send formatted trading alerts, portfolio updates, and market signals via Telegram. Supports price alerts, stop-loss notifications, win/loss reporting, and scheduled summaries. Use when you need Telegram notifications for trades, price alerts, portfolio updates, or automated trading reports.
author: JamieRossouw
tags: [telegram, alerts, trading, notifications, crypto, automation, bots]
---
# Telegram Alerts — Trading Notification System

Send rich trading alerts to Telegram for any crypto event or portfolio update.

## Alert Types
- **Trade alerts**: entry/exit with P&L, entry price, stop, target
- **Price alerts**: trigger when asset crosses threshold
- **Portfolio summaries**: NAV, daily P&L, positions
- **Stop-loss warnings**: drawdown approaching limit
- **Win/loss streaks**: celebration + tilt prevention
- **Scheduled reports**: daily 18:00, weekly Monday

## Usage
```
Use telegram-alerts to send a trade entry notification for BTC LONG at $68,000

Use telegram-alerts to send my daily portfolio summary

Use telegram-alerts to alert me when SOL breaks $90
```

## Format Example
```
🟢 TRADE OPENED
Asset: BTC/USDT | LONG
Entry: $68,247 | Stop: $67,200 | Target: $70,000
Risk: $0.38 (0.05% NAV) | R:R = 1:2.6
```

## Setup
Requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file.
