# OpenClaw Integration

Run system-watchdog as a scheduled cron job in [OpenClaw](https://github.com/openclaw/openclaw).

## Setup

Install the cron job from the provided definition:

```bash
openclaw cron add < openclaw-cron.json
```

## Customize Before Installing

Edit `openclaw-cron.json` to match your setup:

- **`schedule.expr`** — cron expression (default: `0 4 * * *` = daily at 4 AM)
- **`schedule.tz`** — your timezone (default: `America/New_York`)
- **`payload.message`** — replace `<SKILL_DIR>` with the actual path to this skill directory
- **Notification channel** — update the task instructions in `payload.message` to specify where reports should be sent (Discord, Telegram, Slack, etc. via the `message` tool)

## What It Does

- Runs `check.sh` on the configured schedule
- If `suspicious: false` → replies `SKIP` (no notification, minimal cost)
- If `suspicious: true` → formats a report and sends it to your configured channel
- Uses Sonnet by default (cheap, reliable for tool calls)

## Example: Change to Every 6 Hours

```json
"schedule": {
  "kind": "cron",
  "expr": "0 */6 * * *",
  "tz": "America/New_York"
}
```
