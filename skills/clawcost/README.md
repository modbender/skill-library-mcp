# ClawCost

Track your OpenClaw agent costs with budget alerts and balance tracking.

## Features

- **Daily/Weekly/Total Cost** - Track spending over time
- **Model Breakdown** - See costs per model (Opus, Sonnet, Haiku)
- **Budget Alerts** - Warnings when approaching limits
- **Balance Tracking** - Auto-calculate remaining balance
- **Daily History** - Last 7 days breakdown

## Installation

```bash
clawhub install clawcost
```

Or manually copy to your OpenClaw skills directory.

## Usage

The skill responds to natural language:
- "check cost"
- "how much spent today?"
- "cost breakdown"

### Set Balance

Set your initial balance (when you top up):
```bash
python3 scripts/clawcost.py --set-balance 50.00
```

Remaining auto-calculates: `initial - total_spent`

### Set Daily Budget

```bash
python3 scripts/clawcost.py --budget 10
```

## Output Example

```
💰 username
├ Balance $42.98 / $50 remaining
├ Today   $1.36 / $10 (14%) ✅
├ Week    $7.02
└ Total   $7.02 (15.5M tok)

📈 Sonnet $3.99 (57%) • Haiku $2.06 (29%) • Opus $0.97 (14%)
```

## Alerts

- ⚠️ Warning when >80% of daily budget used
- 🚨 Alert when over budget
- 💸 Low balance warning when <$5 remaining

## How It Works

ClawCost reads your OpenClaw session logs to calculate costs. It only accesses:
- `~/.openclaw/agents/main/sessions/*.jsonl` (read-only)
- `~/.clawcost/config.json` (read/write for settings)

No data is transmitted externally. All processing is local.

## Requirements

- Python 3.x
- OpenClaw installed with session logs at `~/.openclaw/agents/main/sessions/`

## Config

Config stored at `~/.clawcost/config.json`:
```json
{
  "initial_balance": 50.0,
  "budget_daily": 10.0
}
```

## Security

- Reads only current user's session logs (uses `$HOME`)
- No network calls or external data transmission
- Config is stored locally in user's home directory

## License

MIT
