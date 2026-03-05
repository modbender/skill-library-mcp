---
name: Telegram Bot API
slug: telegram-bot-api
version: 1.0.0
homepage: https://clawic.com/skills/telegram-bot-api
description: Build Telegram bots with correct API calls, message formatting, keyboards, and webhook setup.
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":["curl"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs to interact with the Telegram Bot API. Building bots, sending messages, handling updates, setting up webhooks, creating keyboards, or managing bot commands.

## Architecture

Memory lives in `~/telegram-bot-api/`. See `memory-template.md` for structure.

```
~/telegram-bot-api/
├── memory.md          # Bot tokens, preferences, defaults
├── bots/              # Per-bot configurations
│   └── {botname}.md   # Token, webhook URL, defaults
└── templates/         # Reusable message templates
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| All API methods | `methods.md` |
| Message formatting | `formatting.md` |
| Keyboards & buttons | `keyboards.md` |
| Webhooks & polling | `webhooks.md` |
| Media handling | `media.md` |
| Error codes | `errors.md` |

## Core Rules

### 1. API Base URL
All requests go to:
```
https://api.telegram.org/bot{TOKEN}/{METHOD}
```
Never expose the token in logs or user-visible output.

### 2. Required Parameters by Method

| Method | Required | Optional (common) |
|--------|----------|-------------------|
| sendMessage | chat_id, text | parse_mode, reply_markup, disable_notification |
| sendPhoto | chat_id, photo | caption, parse_mode |
| sendDocument | chat_id, document | caption, thumbnail |
| getUpdates | — | offset, limit, timeout |
| setWebhook | url | certificate, max_connections |
| deleteWebhook | — | drop_pending_updates |
| getMe | — | — |

### 3. Parse Mode Selection

| Format | Use when | Escape chars |
|--------|----------|--------------|
| `MarkdownV2` | Rich formatting needed | `_*[]()~\`>#+-=|{}.!` |
| `HTML` | Complex nesting, safer | `<>&` |
| None | Plain text only | None |

**Default to HTML** — fewer escape issues than MarkdownV2.

### 4. Chat ID Types

| Type | Format | Example |
|------|--------|---------|
| User | Positive integer | `123456789` |
| Group | Negative integer | `-123456789` |
| Supergroup/Channel | -100 prefix | `-1001234567890` |

### 5. Rate Limits

| Scope | Limit |
|-------|-------|
| Same chat | 1 msg/sec |
| Different chats | 30 msg/sec |
| Groups | 20 msg/min per group |
| Bulk notifications | Use sendMessage with different chat_ids |

When hitting 429 errors, use exponential backoff starting at `retry_after` seconds.

### 6. Message Length Limits

| Type | Limit |
|------|-------|
| Text message | 4096 chars |
| Caption | 1024 chars |
| Callback data | 64 bytes |
| Inline query | 256 chars |

Split long messages at sentence boundaries, not mid-word.

### 7. Keyboard Best Practices

**Inline keyboards** (in message):
- Max 8 buttons per row
- Max 100 buttons total
- Use `callback_data` for bot actions
- Use `url` for external links

**Reply keyboards** (below input):
- Use for frequent options
- `one_time_keyboard: true` to hide after use
- `resize_keyboard: true` for better mobile UX

## Common Traps

- **Forgetting to escape MarkdownV2** → Message fails silently or partially. Use HTML instead, or escape all special chars.
- **Using wrong chat_id format** → Groups need negative IDs. Supergroups/channels need -100 prefix.
- **Not handling 429 errors** → Bot gets temporarily blocked. Always implement retry logic.
- **Exposing bot token** → Anyone can control your bot. Never log or display tokens.
- **Sending too fast to groups** → 20 msg/min limit. Queue messages with delays.
- **Large file uploads** → 50MB limit for sendDocument. Use URL method for larger files.
- **Webhook not HTTPS** → Telegram requires valid SSL certificate.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://api.telegram.org/bot{TOKEN}/* | Messages, media, commands | All bot operations |

No other data is sent externally. Bot token is required for all requests.

## Security & Privacy

**Data that leaves your machine:**
- Messages and media sent via the Bot API
- Bot token in every request (required by Telegram)

**Data that stays local:**
- Bot configurations in `~/telegram-bot-api/`
- Message templates

**This skill does NOT:**
- Store message content long-term
- Access user data beyond what Telegram provides
- Make requests to endpoints other than api.telegram.org

## Trust

By using this skill, data is sent to Telegram's Bot API servers.
Only install if you trust Telegram with your bot's messages.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — REST API best practices
- `http` — HTTP protocol essentials
- `json` — JSON parsing and manipulation

## Feedback

- If useful: `clawhub star telegram-bot-api`
- Stay updated: `clawhub sync`
