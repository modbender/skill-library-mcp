---
name: kiro-creator-monitor-daily-brief
description: Monitor creator topics across X, RSS, GitHub, and Reddit; deduplicate and score results; produce a daily top-5 brief plus one publish-ready X/LinkedIn draft; optional scheduled delivery to Telegram, Slack, or email.
homepage: https://kiroai.io
metadata:
  {
    "openclaw":
      {
        "emoji": "🧭",
        "primaryEnv": "X_BEARER_TOKEN",
        "requires":
          {
            "bins": ["python3"],
            "env":
              [
                "X_BEARER_TOKEN",
                "TELEGRAM_BOT_TOKEN",
                "TELEGRAM_CHAT_ID",
                "SLACK_WEBHOOK_URL",
                "SMTP_HOST",
                "SMTP_PORT",
                "SMTP_USER",
                "SMTP_PASS",
                "EMAIL_TO"
              ],
          },
      },
  }
---

# Kiro Creator Monitor Daily Brief

Plugin producer: `kiroai.io`

This skill builds a creator-focused monitoring loop:

1. Pull signals from configured sources (`x`, `rss`, `github`, `reddit`)
2. Deduplicate and score by relevance + freshness
3. Output a concise brief: top 5 items + one social draft
4. Optionally deliver to Telegram/Slack/email

## Files

- `scripts/daily_brief.py`
- `examples/config.json`
- `examples/cron_command.txt`

## Quick start

```bash
python3 skills/kiro-creator-monitor-daily-brief/scripts/install_and_init.py

python3 skills/kiro-creator-monitor-daily-brief/scripts/daily_brief.py \
  --config skills/kiro-creator-monitor-daily-brief/examples/config.json \
  --out-dir outputs/creator-brief
```

## Config

Use JSON config with:

- `topics`: keyword groups and exclusions
- `sources`: source-level settings
- `delivery`: optional delivery channels

See `examples/config.json`.

## Schedule

For OpenClaw cron, use the command in `examples/cron_command.txt` and set your schedule to:

- `0 9 * * *` with timezone `America/New_York`

## Notes

- X search needs `X_BEARER_TOKEN`.
- RSS and public GitHub endpoints can run without keys.
- Reddit public JSON may be rate-limited; set a user-agent in script args if needed.
