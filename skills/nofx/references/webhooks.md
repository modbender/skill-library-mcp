# NOFX Webhook Notification Integration

## Supported Notification Channels

| Channel | Purpose | Configuration |
|---------|---------|---------------|
| Telegram | Instant messaging | Bot Token + Chat ID |
| Discord | Team collaboration | Webhook URL |
| Slack | Work notifications | Webhook URL |
| Custom | Third-party systems | HTTP POST |

## Telegram Notifications

### Via Clawdbot

Clawdbot is integrated, use cron job to send directly:

```json
{
  "payload": {
    "deliver": true,
    "channel": "telegram",
    "to": "YOUR_CHAT_ID"
  }
}
```

### Direct Telegram API Call

```bash
TELEGRAM_BOT_TOKEN="your_bot_token"
CHAT_ID="your_chat_id"
MESSAGE="🚀 NOFX Alert: ETH breaks $2000"

curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -d "chat_id=$CHAT_ID" \
  -d "text=$MESSAGE" \
  -d "parse_mode=Markdown"
```

## Discord Webhook

### Create Webhook

1. Server Settings → Integrations → Webhooks
2. Create Webhook, copy URL

### Send Notification

```bash
DISCORD_WEBHOOK="https://discord.com/api/webhooks/xxx/yyy"

curl -H "Content-Type: application/json" \
  -X POST "$DISCORD_WEBHOOK" \
  -d '{
    "content": "🚀 NOFX Alert",
    "embeds": [{
      "title": "AI500 New Signal",
      "description": "POWER enters ranking, score 88.5",
      "color": 5763719
    }]
  }'
```

## Slack Webhook

### Create Webhook

1. Slack App → Incoming Webhooks
2. Add to channel, copy URL

### Send Notification

```bash
SLACK_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"

curl -X POST "$SLACK_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🚀 NOFX Alert: ETH institutional inflow $10M"
  }'
```

## Custom Webhook

### Generic HTTP POST

```bash
WEBHOOK_URL="https://your-server.com/webhook"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "ai500_signal",
    "symbol": "POWER",
    "score": 88.5,
    "timestamp": "2026-02-12T12:00:00Z"
  }'
```

## Clawdbot Integration Examples

### Price Alert

```bash
# Monitor BTC price, notify when breaks 70000
if [ $(curl -s "https://nofxos.ai/api/coin/BTC?auth=$KEY" | jq '.data.price') -gt 70000 ]; then
  # Send Telegram notification
  curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID" \
    -d "text=🚀 BTC breaks $70,000!"
fi
```

### AI500 New Coin Alert

```bash
# Check AI500 new coins
NEW_COINS=$(curl -s "https://nofxos.ai/api/ai500/list?auth=$KEY" | \
  jq -r '.data.coins[] | select(.start_time > (now - 3600)) | .pair')

if [ -n "$NEW_COINS" ]; then
  # Send notification
  MESSAGE="🆕 AI500 new entry: $NEW_COINS"
  # ... send to Telegram/Discord/Slack
fi
```

### Large Fund Flow Alert

```bash
# Check institutional inflow > $10M
BIG_FLOWS=$(curl -s "https://nofxos.ai/api/netflow/top-ranking?auth=$KEY&limit=5&duration=1h&type=institution" | \
  jq -r '.data.netflows[] | select(.amount > 10000000) | "\(.symbol): $\(.amount/1000000)M"')

if [ -n "$BIG_FLOWS" ]; then
  MESSAGE="💰 Large institutional inflow:\n$BIG_FLOWS"
  # ... send notification
fi
```

## Notification Templates

### Market Report Template

```
📊 NOFX Market Report | {time}

🤖 AI500 Signals
{ai500_list}

💰 Institutional Inflow TOP5
{flow_list}

🚀 1h Gainers TOP5
{gainers_list}

⚠️ Risk Alert
{alerts}
```

### Trading Signal Template

```
🎯 Trading Signal | {symbol}

Direction: {direction}
Entry: ${entry_price}
Stop Loss: ${stop_loss}
Take Profit: ${take_profit}
Position: {position_size}%

AI Score: {ai_score}
Fund Flow: {fund_flow}
```

### P&L Report Template

```
💰 {trader_name} Daily Report

Equity: ${equity}
P&L: ${pnl} ({pnl_pct}%)
Positions: {positions_count}

Today's Trades: {trades_count}
Win Rate: {win_rate}%
```