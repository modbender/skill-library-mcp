---
name: telegram-context
description: Toggle-enabled skill that fetches Telegram message history at session start for conversational continuity. Maintains context across sessions without relying solely on memory files.
homepage: https://github.com/openclaw/skills
metadata:
  openclaw:
    emoji: "💬"
    requires:
      bins: []
      env: []
    permissions:
      - message:read
---

# Telegram Context

Provides conversational continuity by fetching recent Telegram messages at session start. When enabled, the agent automatically retrieves message history to maintain context across disconnected sessions.

## Credits

Created by @fourthdensity

## Commands

- `/telegram-context on` — Enable automatic history fetching
- `/telegram-context off` — Disable automatic fetching
- `/telegram-context status` — Show current settings
- `/telegram-context fetch [n]` — Manually fetch last n messages (default: 20)

## Setup

1. The skill auto-detects Telegram channels — no configuration needed
2. State is stored in `memory/telegram-context.json`
3. Only activates when the current channel is Telegram

## How It Works

When a session starts in Telegram:

1. Check `memory/telegram-context.json` for enabled state
2. If enabled, fetch recent messages via `message` tool
3. Provide history as context for the conversation
4. Update `lastFetch` timestamp

## State File

`memory/telegram-context.json`:
```json
{
  "enabled": true,
  "fetchCount": 20,
  "lastFetch": "2025-01-15T10:30:00Z"
}
```

## Implementation Notes

### Command Handlers

**Enable/disable:**
```javascript
// Read current state
read: memory/telegram-context.json

// Update state
write: memory/telegram-context.json
{
  "enabled": true/false,
  "fetchCount": 20,
  "lastFetch": "2025-01-15T10:30:00Z"
}
```

**Manual fetch:**
```javascript
message: {
  action: "list",
  limit: 20  // or user-specified count
}
// Provide results as context summary
```

### Session Start Behavior

At the start of each Telegram session:

1. Check if `memory/telegram-context.json` exists
2. If enabled, call `message` tool with `action: "list"`
3. Summarize recent messages for context window
4. Acknowledge continuity to user (optional)

### Implementation Scope

The skill uses OpenClaw's built-in `message` tool with:
- `action: "list"` — limited to the **current Telegram chat only**
- No access to other chats, channels, or external Telegram accounts
- Requires the OpenClaw gateway to have Telegram channel permissions already configured

### Privacy & Security

**Data Handling:**
- Only fetches from the **current chat** (never cross-chats or other Telegram conversations)
- Message content is **included in the agent's context window** and sent to the configured LLM provider
- No message content is stored in `telegram-context.json` — only settings and timestamps
- Message content may appear in OpenClaw session logs (depends on your logging configuration)

**Recommendations for Sensitive Conversations:**
- Use **manual fetch** (`/telegram-context fetch`) instead of auto-fetch
- Set **low fetchCount** (5-10) to minimize context exposure
- **Disable** the skill entirely when discussing sensitive topics: `/telegram-context off`
- Be aware that fetched messages become part of the conversation history sent to AI models

**User Control:**
- Full toggle on/off anytime — no persistence beyond your control
- No external credentials or API keys required
- No binaries installed — pure instruction-based skill

## Limitations

- Telegram-only (other channels not supported)
- Requires appropriate message permissions via OpenClaw gateway
- Large history may need summarization to fit context window
- **Fetched messages are sent to your configured LLM provider** — review your threat model for sensitive conversations

## Tips

- Set `fetchCount` to 10-30 for most use cases (balance context vs. tokens)
- Use `/telegram-context fetch 50` when you need deep context for a specific task
- Works best alongside `MEMORY.md` for long-term persistence
