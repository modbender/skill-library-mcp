---
name: minimax-usage
description: Check MiniMax coding plan usage/credits remaining. Requires MINIMAX_API_KEY environment variable.
metadata: {"openclaw":{"emoji":"💳","requires":{"bins":["curl","jq"],"env":["MINIMAX_API_KEY"]}}}
---

# MiniMax Usage

Check your MiniMax coding plan credits remaining.

## Usage

```bash
# Check remaining credits
minimax-usage.sh

# Only alert when remaining drops below 20%
minimax-usage.sh --threshold 20
```

## Options

| Flag | Description |
|------|-------------|
| `--threshold <percent>` | Only output when remaining % is below this value. If omitted, always outputs. |

## Output

Returns a Discord-formatted message:
- **Title** with model name (warning icon when below threshold)
- **Remaining** requests out of total with percentage
- **Reset time** in Eastern Time
- **Time left** in H:MM:SS

### Example: Below threshold alert

When remaining usage falls below the configured threshold:

```
⚠️ MiniMax Usage Alert — MiniMax-M1
Remaining: 42 of 500 requests (8.4%)
Resets: Feb 17, 2026 12:00 AM ET
Time left: 7:23:15
```

When above the threshold, the command produces no output and exits with code 0.

## Cron Job

The `--threshold` flag makes this ideal for a cron job that runs periodically and only sends an alert when available credits drop below a percentage:

```bash
# Check every 30 minutes, alert if below 20%
# Requires MINIMAX_API_KEY to be set in the cron environment
*/30 * * * * minimax-usage.sh --threshold 20 | discord-webhook
```

No output is produced when usage is above the threshold, so downstream commands (e.g. a webhook) are only triggered when credits are running low.
