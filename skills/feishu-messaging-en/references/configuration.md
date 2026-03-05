# Feishu Channel Configuration Reference

## Complete Configuration Schema

```yaml
channels:
  feishu:
    # Required
    enabled: true
    appId: "cli_xxxxx"
    appSecret: "your_app_secret"

    # Connection Settings
    domain: "feishu"  # "feishu" (China) or "lark" (International)
    connectionMode: "websocket"  # "websocket" (recommended) or "webhook"

    # Message Formatting
    renderMode: "card"  # "auto" | "raw" | "card"
    mediaMaxMb: 30  # Max media file size in MB

    # Access Control
    dmPolicy: "pairing"  # "pairing" | "open" | "allowlist"
    groupPolicy: "allowlist"  # "open" | "allowlist" | "disabled"
    requireMention: true  # In groups, bot only responds when @mentioned

    # Tools (optional)
    tools:
      doc: true  # Enable feishu_doc tool
      drive: true  # Enable feishu_drive tool
      wiki: true  # Enable feishu_wiki tool
```

## Configuration Options Explained

### Connection Settings

#### `domain`

- **Type:** string
- **Values:** `"feishu"` | `"lark"`
- **Default:** `"feishu"`
- **Description:**
  - `"feishu"`: For China (feishu.cn)
  - `"lark"`: For international (larksuite.com)

#### `connectionMode`

- **Type:** string
- **Values:** `"websocket"` | `"webhook"`
- **Default:** `"websocket"`
- **Description:**
  - `"websocket"`: Long connection, recommended for stability
  - `"webhook"`: Requires public URL, for specific deployment scenarios

**Recommendation:** Use `"websocket"` for most cases.

### Message Formatting

#### `renderMode` ⚠️ Important

- **Type:** string
- **Values:** `"auto"` | `"raw"` | `"card"`
- **Default:** `"auto"`
- **Description:**
  - `"auto"`: Automatically detect content type
  - `"raw"`: Always plain text
  - `"card"`: Always interactive card with full markdown

**Impact:** Only affects auto-replies, NOT proactive messages via `message` tool.

**Recommendation:** Use `"card"` for consistent formatting.

#### `mediaMaxMb`

- **Type:** number
- **Default:** `30`
- **Description:** Maximum media file size in megabytes for uploads.

### Access Control

#### `dmPolicy` (Direct Messages)

- **Type:** string
- **Values:** `"pairing"` | `"open"` | `"allowlist"`
- **Default:** `"pairing"`
- **Description:**
  - `"pairing"`: Users must approve bot before chatting (recommended)
  - `"open"`: Anyone can DM the bot
  - `"allowlist"`: Only allowlisted users can DM

#### `groupPolicy` (Group Chats)

- **Type:** string
- **Values:** `"open"` | `"allowlist"` | `"disabled"`
- **Default:** `"allowlist"`
- **Description:**
  - `"open"`: Bot joins any group
  - `"allowlist"`: Only allowed groups
  - `"disabled"`: No group support

#### `requireMention`

- **Type:** boolean
- **Default:** `true`
- **Description:** In groups, bot only responds when @mentioned.

**Recommendation:** Keep `true` to avoid spamming groups.

## Quick Configuration Commands

### Set renderMode to card

```bash
openclaw config set channels.feishu.renderMode "card"
openclaw gateway restart
```

### Enable all tools

```bash
openclaw config set channels.feishu.tools.doc true
openclaw config set channels.feishu.tools.drive true
openclaw config set channels.feishu.tools.wiki true
openclaw gateway restart
```

### Change group policy

```bash
openclaw config set channels.feishu.groupPolicy "open"
openclaw gateway restart
```

### View current configuration

```bash
openclaw config get channels.feishu
```

## Environment-Specific Configurations

### Development

```yaml
channels:
  feishu:
    renderMode: "raw"  # Simpler for debugging
    dmPolicy: "open"  # Easier testing
    groupPolicy: "open"
```

### Production

```yaml
channels:
  feishu:
    renderMode: "card"  # Professional appearance
    dmPolicy: "pairing"  # Security
    groupPolicy: "allowlist"  # Access control
    requireMention: true
```

### High-Volume

```yaml
channels:
  feishu:
    renderMode: "raw"  # Faster processing
    mediaMaxMb: 10  # Smaller files
```

## Validation Checklist

After configuration changes:

- [ ] Restart gateway: `openclaw gateway restart`
- [ ] Test DM: Send message to bot
- [ ] Test group: @mention bot in allowed group
- [ ] Verify formatting: Check message appearance
- [ ] Check logs: `openclaw logs` for errors

## Common Configuration Mistakes

### 1. Forgetting to restart

**Problem:** Changes don't take effect

**Solution:** Always run `openclaw gateway restart` after config changes

### 2. Using "auto" renderMode in production

**Problem:** Inconsistent message formatting

**Solution:** Use `"card"` or `"raw"` explicitly

### 3. Setting requireMention to false

**Problem:** Bot responds to every group message, annoying users

**Solution:** Keep `requireMention: true`

### 4. Not configuring event subscriptions

**Problem:** Bot can send but cannot receive messages

**Solution:** Configure events in Feishu Open Platform console (see main README)

## Related Documentation

- Main plugin README: `/home/admin/.openclaw/extensions/feishu/README.md`
- Render modes detail: [render-modes.md](render-modes.md)
- OpenClaw docs: https://docs.openclaw.ai
