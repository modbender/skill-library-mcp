---
name: feishu-messaging
description: |
  Best practices for Feishu (Lark) message configuration and formatting. Use when: (1) Configuring Feishu channel settings, (2) Experiencing message formatting issues (raw vs card), (3) Setting up renderMode for stable message display, (4) Understanding differences between auto-replies and proactive messages. Essential for ensuring consistent message formatting in Feishu chats.
---

# Feishu Messaging Configuration

## Quick Start

For stable, consistent message formatting in Feishu, configure:

```yaml
channels:
  feishu:
    renderMode: "card"  # Recommended for most use cases
```

This ensures all auto-replies use interactive cards with proper markdown rendering.

## Message Format Stability

### The Problem: Raw vs Card Mixing

Without proper configuration, Feishu messages can inconsistently appear as:
- **Raw text**: Plain markdown source, no formatting
- **Card format**: Rendered markdown with syntax highlighting, tables, links

This creates a poor user experience with unpredictable message appearance.

### The Solution: Explicit renderMode

Set `renderMode` explicitly instead of relying on "auto":

| Mode | Behavior | Use Case |
|------|----------|----------|
| `auto` | Detects content, uses card for code/tables | Default, but can be inconsistent |
| `raw` | Always plain text | Simple text-only responses |
| `card` | Always interactive card | **Recommended** - consistent formatting |

**Recommended configuration:**

```yaml
channels:
  feishu:
    renderMode: "card"
```

This guarantees:
- ✅ Consistent message appearance
- ✅ Proper markdown rendering (syntax highlighting, tables, links)
- ✅ No unexpected format switching
- ✅ Professional, polished look

## Auto-Reply vs Proactive Messages

### Auto-Replies (Bot responds to user messages)

Controlled by `renderMode`:
- `renderMode: "card"` → All auto-replies use card format
- `renderMode: "raw"` → All auto-replies use plain text

**Example flow:**
1. User: "Show me the code"
2. Bot auto-reply uses card format (if `renderMode: "card"`)

### Proactive Messages (Bot sends via `message` tool)

Always use plain text format via `outbound.sendText`.

**To send card format proactively:**
1. Ask user to send a message first
2. Bot replies to that message (uses `renderMode`)

**Example:**
```
User: "Remind me about the meeting"
Bot (proactive): "OK, reminder set"  # Plain text via message tool

vs

User: "Set up a reminder"
Bot (auto-reply): "OK, reminder set"  # Card format if renderMode: "card"
```

## Configuration Checklist

### Basic Setup

```yaml
channels:
  feishu:
    enabled: true
    appId: "cli_xxxxx"
    appSecret: "secret"
    renderMode: "card"  # 🔑 Key setting for stable formatting
```

### Advanced Options

```yaml
channels:
  feishu:
    # Connection
    connectionMode: "websocket"  # Recommended
    domain: "feishu"  # or "lark" for international

    # Message behavior
    requireMention: true  # Groups: bot only responds when @mentioned
    mediaMaxMb: 30

    # Access control
    dmPolicy: "pairing"  # DM requires approval
    groupPolicy: "allowlist"  # Only allowed groups
```

## Troubleshooting

### Messages appear as raw markdown

**Problem:** Users see unformatted markdown source

**Solution:**
1. Check `renderMode` setting: `openclaw config get channels.feishu.renderMode`
2. Set to "card": `openclaw config set channels.feishu.renderMode "card"`
3. Restart OpenClaw: `openclaw gateway restart`

### Format switches between raw and card

**Problem:** Some messages are formatted, others are raw

**Solution:**
- Change from `renderMode: "auto"` to `renderMode: "card"`
- "auto" mode switches based on content detection, causing inconsistency

### Proactive messages not using card format

**Expected behavior:** Proactive messages (via `message` tool) always use plain text

**Workaround:**
1. User sends a message first
2. Bot's auto-reply will use card format

## Best Practices

### 1. Use Explicit renderMode

Avoid "auto" mode for production. Choose "card" or "raw" explicitly.

```yaml
# ✅ Good - explicit, predictable
renderMode: "card"

# ⚠️ Risky - can be inconsistent
renderMode: "auto"
```

### 2. Document Configuration in USER.md

Add user preferences to workspace USER.md:

```markdown
## Preferences

- **Feishu Message Format:** Configured with `renderMode: "card"`, auto-replies use card format
- **Note:** Proactive messages via `message` tool are still plain text
```

### 3. Test Configuration

After changing settings:

1. Restart: `openclaw gateway restart`
2. Send test message to bot
3. Verify formatting is consistent

### 4. Group Chat Considerations

In groups, bot only responds when mentioned (if `requireMention: true`):

```
User: @bot help me check the data
Bot: [Card format reply with data]

User: Nice weather today
Bot: [No response - not mentioned]
```

## Related Skills

- **feishu-doc**: Document read/write operations
- **feishu-drive**: Cloud storage file management
- **feishu-wiki**: Knowledge base navigation
- **feishu-perm**: Permission management

## References

For detailed configuration and API documentation, see:
- [configuration.md](references/configuration.md): Complete configuration options
- [render-modes.md](references/render-modes.md): Deep dive into render modes
