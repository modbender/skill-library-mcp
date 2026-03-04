# Z.AI Usage Monitor

Monitor your Z.AI GLM Coding Plan usage and quota limits directly from OpenClaw.

## Features

- ✅ **Real-time quota tracking** - 5-hour and monthly token quotas
- ✅ **Web tool monitoring** - Track search/reader/zread usage
- ✅ **Visual progress bars** - Easy-to-read usage indicators
- ✅ **Reset countdown** - Know when quotas refresh
- ✅ **Quick status** - One-line summary for fast checks

## Screenshot

```
╔════════════════════════════════════════════════════════════╗
║           Z.AI GLM Coding Plan Usage                       ║
╚════════════════════════════════════════════════════════════╝

Subscription: GLM Coding Pro

5-Hour Token Quota:
   8M / 200M tokens (4%)
   [█░░░░░░░░░░░░░░░░░░░░]
   192M remaining
   Resets in: 4h 47m

Monthly Quota:
   19% used
   Resets: 2026-03-04

Web Tools (Monthly):
   1000 / 2000 calls (0%)
   1000 remaining

Status: ✅ Good
```

## Installation

### Option 1: ClawHub (Recommended)

```bash
cd ~/.openclaw
clawhub install zai-usage
```

### Option 2: Manual

```bash
cd ~/.openclaw/skills
git clone https://github.com/openclaw/skills.git temp
mv temp/zai-usage .
rm -rf temp
```

## Setup

### Step 1: Get Your Token

You need a JWT token from your Z.AI browser session (not an API key).

1. Go to: https://z.ai/manage-apikey/subscription
2. Open DevTools (`F12` or `Cmd+Option+I`)
3. Navigate to: **Application** → **Local Storage** → `https://z.ai`
4. Find: `z-ai-open-platform-token-production`
5. Copy the value (starts with `eyJhbGci...`)

**Reference:** https://github.com/zereraz/tokensight

### Step 2: Store Your Token

Add your token to OpenClaw secrets:

```bash
mkdir -p ~/.openclaw/secrets
echo "ZAI_JWT_TOKEN=eyJhbGci..." > ~/.openclaw/secrets/zai.env
```

Or add to your shell environment:

```bash
export ZAI_JWT_TOKEN="eyJhbGci..."
```

## Usage

### Command Line

```bash
# Full usage report
~/.openclaw/skills/zai-usage/scripts/usage-summary.sh

# Quick one-line status
~/.openclaw/skills/zai-usage/scripts/quick-check.sh
```

### Ask OpenClaw

Just ask naturally:

- "How's our Z.AI usage?"
- "Check credit usage"
- "Are we running low on credits?"
- "Do we need to upgrade?"
- "What's my token quota?"

### Output Formats

**Full Report:**
```
Subscription: GLM Coding Pro
5-Hour Token Quota: 4% used (192M remaining)
Monthly Quota: 19% used
Resets: 2026-03-04
```

**Quick Check:**
```
ZAI: ✅ 5% 5h | 20% monthly
```

## API Details

### Endpoint

```
GET https://api.z.ai/api/monitor/usage/quota/limit
Authorization: Bearer {JWT_TOKEN}
```

### Response Format

```json
{
  "success": true,
  "data": {
    "level": "pro",
    "limits": [
      {
        "type": "TOKENS_LIMIT",
        "unit": 3,
        "number": 5,
        "percentage": 2,
        "nextResetTime": 1772142380917
      }
    ]
  }
}
```

## Quota Types

| Type | Unit | Description | Reset Period |
|------|------|-------------|--------------|
| `TOKENS_LIMIT` | 3 | 5-hour rolling token quota | Every 5 hours |
| `TOKENS_LIMIT` | 6 | Monthly token quota | Monthly |
| `TIME_LIMIT` | 5 | Web tool calls (search/reader/zread) | Monthly |

## Plan Levels

| Level | 5-Hour Quota | Monthly Quota | Web Tools |
|-------|--------------|---------------|-----------|
| Lite | 50M tokens | Limited | Limited |
| Pro | 200M tokens | 1000 calls | 1000 calls |

## Status Indicators

| Icon | Status | Usage |
|------|--------|-------|
| ✅ | Good | < 50% |
| ⚠️ | Moderate | 50-80% |
| 🔴 | High | > 80% |

## When to Upgrade

Consider upgrading your plan if:

- 5-hour quota frequently exceeds 80%
- Monthly quota runs out before reset
- Getting rate limited often
- Need more web tool calls for research

## Security

- Tokens are stored in `~/.openclaw/secrets/zai.env`
- Never displayed in logs or responses
- File permissions: `600` (owner read/write only)

## Troubleshooting

### "ZAI_JWT_TOKEN not configured"

**Solution:** Add your token to `~/.openclaw/secrets/zai.env`

### "token expired or incorrect"

**Solutions:**
1. Token may have expired - get a fresh one from browser
2. Make sure you copied the full JWT (starts with `eyJhbGci`)
3. Check for extra whitespace in the token

### "Auth error"

**Solution:** Your token may have been revoked. Log back into https://z.ai and get a new token.

## Requirements

- `curl` - HTTP requests
- `jq` - JSON parsing
- `bc` - Number formatting (optional)

## Credits

- Inspired by [tokensight](https://github.com/zereraz/tokensight) by zereraz
- Built for [OpenClaw](https://openclaw.ai)

## Sources

- https://github.com/zereraz/tokensight
- https://www.reddit.com/r/ZaiGLM/comments/1pmb7fj/how_to_check_zai_coding_usage/
- https://z.ai/manage-apikey/subscription

## License

MIT

---

Made with 🐱 by OpenClaw
