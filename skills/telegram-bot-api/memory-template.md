# Memory Template — Telegram Bot API

## Main Memory

Create `~/telegram-bot-api/memory.md`:

```markdown
# Telegram Bot API Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Preferences
parse_mode: HTML
example_style: curl
environment: local

## Notes
<!-- User preferences and patterns -->

---
*Updated: YYYY-MM-DD*
```

## Bot Configuration

Create `~/telegram-bot-api/bots/{botname}.md`:

```markdown
# Bot: {Bot Name}

## Config
username: @{username}
token: {BOT_TOKEN}
created: YYYY-MM-DD

## Webhook
url: https://example.com/webhook
max_connections: 40
allowed_updates: message,callback_query

## Defaults
parse_mode: HTML
disable_notification: false
protect_content: false

## Notes
<!-- Bot-specific notes -->
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Still learning preferences |
| `complete` | Ready to help |
| `paused` | User not active |

## Parse Mode Options

| Value | When to use |
|-------|-------------|
| `HTML` | Default — fewer escape issues |
| `MarkdownV2` | When user prefers Markdown |
| `Markdown` | Legacy — avoid for new bots |
| (none) | Plain text only |

## Example Style Options

| Value | When to use |
|-------|-------------|
| `curl` | Quick testing, no dependencies |
| `python` | Building with python-telegram-bot |
| `node` | Building with telegraf or node-telegram-bot-api |
| `raw` | Just show the JSON structure |
