# Sentinel Shield — Installation

## Quick Install (OpenClaw Skill)

Already installed if you're reading this. The skill auto-registers via `SKILL.md`.

## Initialize Baselines

```bash
node scripts/sentinel.js init
```

This creates SHA-256 hashes of monitored files. Run once after install, and again after any legitimate config changes.

## Configure Telegram Alerts (Optional)

Edit `config/shield.json`:

```json
{
  "telegram": {
    "enabled": true,
    "botToken": "YOUR_BOT_TOKEN",
    "chatId": "YOUR_CHAT_ID"
  }
}
```

### Get Your Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. `/newbot` → follow prompts → copy token

### Get Your Chat ID
1. Message your new bot
2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `"chat":{"id":XXXXXXXX}` in response

## Customize Monitored Files

Add paths to `config/shield.json` → `monitoredFiles` array. Supports `~/` expansion.

## Commands

| Command | Description |
|---------|-------------|
| `sentinel.js status` | Quick health check |
| `sentinel.js audit` | Full security audit |
| `sentinel.js alerts` | Recent alerts (--hours N) |
| `sentinel.js ratelimit` | Rate limit status |
| `sentinel.js scan --text "..."` | Scan text for injection |
| `sentinel.js kill` | Emergency stop |
| `sentinel.js init` | Initialize/reset baselines |

## Requirements

- Node.js >= 18
- No external dependencies
