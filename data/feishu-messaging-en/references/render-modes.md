# Feishu Render Modes Deep Dive

## Overview

The `renderMode` setting controls how bot messages appear in Feishu chats. Understanding this setting is crucial for ensuring consistent, professional message formatting.

## Three Render Modes

### 1. `auto` (Default)

**Behavior:**
- Analyzes message content
- Uses card format if message contains:
  - Code blocks (```)
  - Tables
  - Complex markdown
- Uses raw text otherwise

**Pros:**
- Automatic adaptation
- Efficient for simple messages

**Cons:**
- ⚠️ **Unpredictable** - same type of content may render differently
- ⚠️ **Inconsistent** - users don't know what to expect
- ⚠️ **Debugging difficulty** - hard to troubleshoot formatting issues

**Example issues:**
```
Message 1: "Here's code: `print('hello')`" → Raw text
Message 2: "Here's code:
```python
print('hello')
```" → Card format

# Inconsistent appearance!
```

### 2. `raw`

**Behavior:**
- Always sends plain text
- Markdown tables converted to ASCII
- No syntax highlighting
- Links shown as URLs

**Pros:**
- ✅ **Predictable** - always same format
- ✅ **Fast** - minimal processing
- ✅ **Universal** - works in all clients

**Cons:**
- No syntax highlighting
- Tables are ASCII art
- Links not clickable in some clients

**Best for:**
- Simple text responses
- High-volume bots (performance)
- Legacy client compatibility

**Example output:**
```
Here's the data:

| Name  | Age |
|-------|-----|
| Alice | 30  |
| Bob   | 25  |

Link: https://example.com
```

### 3. `card` (Recommended)

**Behavior:**
- Always uses Feishu interactive card
- Full markdown rendering
- Syntax highlighting for code
- Clickable links
- Proper table formatting

**Pros:**
- ✅ **Consistent** - always professional appearance
- ✅ **Rich formatting** - syntax highlighting, tables, links
- ✅ **User-friendly** - best reading experience
- ✅ **Predictable** - no surprises

**Cons:**
- Slightly more processing overhead
- Requires Feishu card support

**Best for:**
- Production bots
- Technical content
- Professional appearance
- User-facing bots

**Example output:**
```
┌─────────────────────────────┐
│ Here's the data:            │
│                             │
│ ┌──────┬─────┐             │
│ │ Name │ Age │             │
│ ├──────┼─────┤             │
│ │Alice │ 30  │             │
│ │Bob   │ 25  │             │
│ └──────┴─────┘             │
│                             │
│ 🔗 Link (clickable)         │
└─────────────────────────────┘
```

## Auto-Reply vs Proactive Messages

### Auto-Replies

**What:** Bot responds to user messages

**Controlled by:** `renderMode` setting

**Examples:**
```
User: "@bot query data"
Bot: [Uses renderMode setting]
```

**Format flow:**
1. User sends message
2. Bot processes and generates response
3. Response formatted according to `renderMode`
4. Sent back to user

### Proactive Messages

**What:** Bot sends via `message` tool without user trigger

**Controlled by:** Always plain text (not affected by `renderMode`)

**Examples:**
```python
# Using message tool
message(
    action="send",
    channel="feishu",
    target="user:ou_xxx",
    message="Reminder: Meeting starting soon"
)
# → Always plain text
```

**Why plain text?**
- Uses `outbound.sendText` API
- Different code path from auto-replies
- Technical limitation of current implementation

**Workaround for card format:**
```
1. User sends message: "Set up reminder"
2. Bot auto-replies: "OK, reminder set" (card format if renderMode: "card")
```

## Decision Matrix

| Scenario | Recommended Mode | Reason |
|----------|------------------|--------|
| Production bot | `card` | Professional, consistent |
| Development/debugging | `raw` | See raw output |
| Simple notifications | `raw` | No formatting needed |
| Technical content | `card` | Syntax highlighting |
| Mixed content types | `card` | Handles all formats well |
| High-volume, simple text | `raw` | Performance |
| User-facing bot | `card` | Best UX |

## Implementation Details

### Auto Mode Logic

```python
def should_use_card(message: str) -> bool:
    """Auto mode decision logic"""
    if "```" in message:  # Code blocks
        return True
    if "|" in message and looks_like_table(message):
        return True
    if complex_markdown(message):
        return True
    return False
```

### Card Mode Rendering

```python
def render_as_card(message: str) -> Card:
    """Convert markdown to Feishu card"""
    return FeishuCard(
        elements=[
            MarkdownBlock(message)
        ],
        config={
            "enable_forwarding": True,
            "update_multi": False
        }
    )
```

### Raw Mode Rendering

```python
def render_as_raw(message: str) -> str:
    """Convert to plain text"""
    # Tables → ASCII
    message = convert_tables_to_ascii(message)
    # Links → URLs
    message = convert_links_to_urls(message)
    return message
```

## Troubleshooting

### Issue: Messages switching between formats

**Cause:** Using `renderMode: "auto"`

**Solution:**
```bash
openclaw config set channels.feishu.renderMode "card"
openclaw gateway restart
```

### Issue: Proactive messages not using card

**Expected behavior:** Proactive messages always plain text

**Workaround:** Have user send a message first, then reply

### Issue: Code blocks not highlighted

**Cause:** Using `renderMode: "raw"`

**Solution:**
```bash
openclaw config set channels.feishu.renderMode "card"
openclaw gateway restart
```

### Issue: Tables look broken

**Cause:** Using `renderMode: "raw"` - tables converted to ASCII

**Solution:** Use `renderMode: "card"` for proper table rendering

## Testing Render Modes

### Test Script

```bash
# Set to card mode
openclaw config set channels.feishu.renderMode "card"
openclaw gateway restart

# Test in Feishu:
# 1. Send: "@bot show me a table"
# 2. Verify: Table renders properly
# 3. Send: "@bot show me code"
# 4. Verify: Syntax highlighting works

# Set to raw mode
openclaw config set channels.feishu.renderMode "raw"
openclaw gateway restart

# Test again:
# 1. Send same messages
# 2. Verify: Plain text output
```

### Expected Results

| Mode | Code Block | Table | Link |
|------|-----------|-------|------|
| `auto` | Card if ``` present | Card if \| present | Card if formatted |
| `raw` | Plain text | ASCII art | URL text |
| `card` | Syntax highlighted | Proper table | Clickable |

## Migration Guide

### From `auto` to `card`

```bash
# 1. Update config
openclaw config set channels.feishu.renderMode "card"

# 2. Restart
openclaw gateway restart

# 3. Test
# Send test messages to verify formatting

# 4. Update documentation
# Add to USER.md:
# - **Feishu Message Format:** Configured with `renderMode: "card"`
```

### From `raw` to `card`

```bash
# Same process as above
# Note: Proactive messages still plain text
```

## Best Practices Summary

1. **Use `card` for production** - Consistent, professional appearance
2. **Avoid `auto` in production** - Unpredictable, inconsistent
3. **Document your choice** - Add to USER.md
4. **Test after changes** - Verify formatting works
5. **Understand limitations** - Proactive messages always plain text

## Related Topics

- [configuration.md](configuration.md): Complete config options
- Main plugin README: Feishu channel setup
- OpenClaw docs: General configuration
