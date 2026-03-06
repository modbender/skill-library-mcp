---
name: universal-notify
description: Send notifications through multiple channels with a single script. Supports ntfy.sh (free, no signup), Gotify (self-hosted), generic webhooks, email (SMTP/curl), Telegram Bot API, and Pushover. Use when sending alerts, monitoring notifications, deployment notices, or any event that needs to reach a human through their preferred channel. Unified interface with priority levels (low/normal/high/urgent).
---

# Universal Notify

Send notifications via `scripts/notify.sh`:

```bash
# ntfy.sh (free, no auth needed)
scripts/notify.sh --channel ntfy --topic myalerts --message "Disk 90%!" --priority urgent

# Gotify (self-hosted)
scripts/notify.sh --channel gotify --url https://gotify.local --token TOKEN --message "Deploy done"

# Webhook (generic JSON POST)
scripts/notify.sh --channel webhook --url https://hooks.example.com/abc --message "Event fired"

# Email
scripts/notify.sh --channel email --smtp smtp://mail:587 --from a@x.com --to b@y.com --subject "Alert" --message "Check server"

# Telegram
scripts/notify.sh --channel telegram --bot-token BOT:TOK --chat-id 12345 --message "Hello"

# Pushover
scripts/notify.sh --channel pushover --app-token X --user-key Y --message "Alert" --priority high
```

## Common Options

All channels support `--message` (required), `--title` (optional), and `--priority low|normal|high|urgent` (default: normal).

## Requirements

- `curl` (standard on most systems)
- No API keys needed for ntfy.sh — other channels require their respective credentials
