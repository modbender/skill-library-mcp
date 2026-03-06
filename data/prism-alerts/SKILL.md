---
name: prism-alerts
description: Real-time Pump.fun token alerts for Solana traders. New launches, graduations, volume spikes. For trading bots, Discord, Telegram, AI agents.
version: 1.1.1
keywords: pumpfun, solana, memecoin, token-alerts, trading-bot, crypto-alerts, degen, solana-trading, real-time-alerts, ai, ai-agent, ai-coding, llm, cursor, claude, automation, defi, web3, openclaw, moltbot, vibe-coding, agentic
---

# Pump.fun Alert Bot

**Never miss a launch.** Real-time alerts for Pump.fun token launches, graduations, and volume spikes on Solana.

Built for trading bots, Discord alerts, and Telegram notifications. Powered by Strykr PRISM.

## Quick Usage

```bash
# Get current bonding tokens
./alerts.sh bonding

# Get recently graduated tokens
./alerts.sh graduated

# Watch for new tokens (poll every 30s)
./alerts.sh watch
```

## Unique Data Source

PRISM is one of the **only APIs** with real-time Pump.fun bonding curve data:

| Endpoint | Description | Speed |
|----------|-------------|-------|
| `/crypto/trending/solana/bonding` | Tokens on bonding curve | 648ms |
| `/crypto/trending/solana/graduated` | Graduated to DEX | 307ms |

## Alert Types

### 1. New Launch Alert
```
🚀 NEW PUMP.FUN TOKEN

$DOGWIFCAT
CA: 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

📊 Stats:
• Bonding Progress: 12%
• Market Cap: $8,450
• Holders: 23
• Created: 2 min ago

[🔍 Scan] [📈 Chart] [💰 Buy]
```

### 2. Graduation Alert
```
🎓 TOKEN GRADUATED!

$MEMECOIN just graduated to Raydium!

📊 Final Stats:
• Market Cap: $69,000
• Total Holders: 1,247
• Bonding Time: 4h 23m

Trading now live on Raydium DEX
[📈 Trade on Raydium]
```

### 3. Volume Spike Alert
```
📈 VOLUME SPIKE DETECTED

$CATDOG seeing unusual activity

• Volume (5m): $45,230 (+340%)
• Price: +28% in 10 minutes
• New holders: +89

⚠️ Could be coordinated buy - DYOR
[🔍 Scan] [📈 Chart]
```

## Bot Commands

```
/start           - Subscribe to alerts
/stop            - Unsubscribe
/bonding         - Current bonding tokens
/graduated       - Recent graduations
/scan <token>    - Scan specific token
/settings        - Configure alert filters
```

## Alert Filters

Configure which alerts you receive:

```javascript
{
  "minMarketCap": 5000,      // Minimum MC to alert
  "maxMarketCap": 100000,    // Maximum MC to alert
  "minHolders": 10,          // Minimum holder count
  "bondingProgress": 20,     // Alert when > 20% bonded
  "volumeSpike": 200,        // Alert on 200%+ volume increase
  "enableGraduations": true, // Alert on graduations
  "enableNewLaunches": true  // Alert on new tokens
}
```

## Integration

### Telegram Bot
```javascript
import { Telegraf } from 'telegraf';
import { PrismClient } from './prism';

const bot = new Telegraf(process.env.BOT_TOKEN);
const prism = new PrismClient();

// Poll every 30 seconds
setInterval(async () => {
  const bonding = await prism.pumpfunBonding();
  const newTokens = filterNewTokens(bonding);
  
  for (const token of newTokens) {
    await bot.telegram.sendMessage(CHANNEL_ID, formatAlert(token));
  }
}, 30000);
```

### Discord Bot
```javascript
import { Client } from 'discord.js';

client.on('ready', () => {
  pollPumpfun(client);
});
```

## Environment Variables

```bash
PRISM_URL=https://strykr-prism.up.railway.app
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHANNEL_ID=xxx
DISCORD_BOT_TOKEN=xxx
DISCORD_CHANNEL_ID=xxx
```

## Polling Best Practices

1. **Rate Limiting**: Poll max once per 30 seconds
2. **Deduplication**: Track sent alerts in SQLite/Redis
3. **Batching**: Group multiple alerts into one message
4. **Cooldowns**: Don't spam same token within 5 minutes

---

Built by [@NextXFrontier](https://x.com/NextXFrontier)
