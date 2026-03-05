---
name: feishu-chat
description: Feishu (Lark) group chat messaging guide for OpenClaw. Includes Raw/Card message modes, @ mention formatting, and group member management. Use when sending messages in Feishu groups, mentioning users/bots, or formatting messages with Markdown. Trigger words: feishu, lark, chat, mention, at, markdown, group.
---

# Feishu Group Chat Guide

## Prerequisites

1. **In a Feishu group** - OpenClaw connected to Feishu
2. **Know member IDs**:
   - Human: `open_id` (ou_xxx format)
   - Bot: `App ID` (cli_xxx format)

---

## 1. Message Sending

### ⚠️ CRITICAL: Only Use ONE Method

**DO NOT use both direct reply and message tool for the same content!** This will send two messages.

Choose ONE:
- Plain text → message tool only
- Markdown → direct reply only

---

### Two Methods

| Method | Tool | Render Mode | Use Case |
|--------|------|-------------|----------|
| **message tool** | `message` | Raw (plain text) | Plain text, @ mentions |
| **Direct reply** | Session reply | Card (with Markdown) | Markdown formatted messages |

### Raw Mode (Plain Text)

**When to use**: Plain text messages, @ mentions

**How to send**:
```javascript
message({
  action: "send",
  channel: "feishu",
  target: "oc_xxx",
  message: "Plain text content"
})
```

**@ Mention format**:
```javascript
message({
  action: "send",
  channel: "feishu",
  target: "oc_xxx",
  message: "<at user_id=\"ou_xxx\">nickname</at> Hello!"
})
```

**Raw Mode Limitations**:
- ❌ No Markdown rendering (bold, italic, code blocks won't render)
- ❌ Tables won't render
- ❌ Links won't render
- ✅ @ mentions work correctly

### Card Mode (Markdown)

**When to use**: Formatted messages with code blocks, tables, bold/italic text

**How to send**: Direct reply in session with Markdown elements.

**Card Mode Triggers** (any of these):
- Code blocks ``` ```
- Tables `| table |`
- Bold `**bold**`
- Italic `*italic*`
- Strikethrough `~~text~~`
- Links `[link](url)`
- Headings `# heading`
- Lists `- item` or `1. item`

**@ Mention format**:
```
<at id=ou_xxx></at> This is Card mode @ mention

**Markdown content** renders correctly
```

**Supported in Card Mode**:

| Style | Syntax | Status |
|-------|--------|--------|
| Bold | `**bold**` | ✅ Supported |
| Italic | `*italic*` | ✅ Supported |
| Strikethrough | `~~text~~` | ✅ Supported |
| Color | `<font color='red'>text</font>` | ✅ Supported |
| Links | `[link](https://xxx)` | ✅ Supported |
| Headings | `# heading` | ✅ Supported |
| Lists | `- item` or `1. item` | ✅ Supported |
| Code blocks | ``` code ``` | ✅ Supported |
| Tables | `| table |` | ✅ Supported |

**Not Supported in Card Mode**:

| Style | Syntax | Status |
|-------|--------|--------|
| Blockquote | `> quote` | ❌ Not supported |
| Inline code | `` `code` `` | ❌ Unstable |
| Horizontal rule | `---` | ❌ Not supported |
| Complex nesting | Multiple levels | ❌ Unstable |

**Best Practice for Card Mode**:
- Use `**bold**` for emphasis
- Use `*italic*` for light emphasis
- Use numbered lists `1.` or bullet lists `-`
- Avoid `---`, `>`, and inline code
- Keep formatting simple

### Avoid Auto Mode

**Problem**: Auto mode can incorrectly choose between Raw and Card.

**Best Practice**:
- **Plain text** → Use message tool (Raw mode)
- **Markdown content** → Direct reply (Card mode)

**Don't**:
- Use message tool for Markdown (won't render)
- Use complex structures in Card mode (may trigger Raw incorrectly)

---

## 2. Group Member Management

### ⚠️ Important: Bots Only See @ Mentioned Messages

**Bots can only see messages that @ mention them!** If a group member sends a message without @ mentioning the bot, the bot won't receive it.

This means:
- To identify a human member's open_id, they must **@ mention the bot and send a message**
- The bot cannot see past messages where it wasn't mentioned

### How to Get Member IDs

**Human open_id** (must @ mention bot):

1. Ask the human to @ mention the bot and send any message
2. When the message arrives, the system shows:
   `[Feishu oc_xxx:ou_xxx timestamp] nickname: message content`
3. The `ou_xxx` is the sender's open_id

**Bot App ID** (requires user to provide):
1. Go to Feishu Developer Console: https://open.feishu.cn/app
2. Click on the bot you want to view
3. In "Application Credentials" (应用凭证), copy the App ID (cli_xxx format)
4. @ mention the bot and send the App ID

### Maintain Member List

Store member info in memory file:

```markdown
## Group Members (oc_xxx)
### Humans
- nickname1: `ou_xxx`
- nickname2: `ou_xxx`

### AI Bots
- bot1: `cli_xxx` (must @ to receive messages)
```

---

## 3. @ Mention Tips

### @ Format Difference (Critical!)

| Mode | @ Format | Example |
|------|----------|---------|
| Raw (message tool) | `<at user_id="ID">nickname</at>` | `<at user_id="ou_xxx">kk</at>` |
| Card (direct reply) | `<at id=ID></at>` | `<at id=ou_xxx></at>` |

### @ Different Target Types

| @ Target | ID Type | Raw Format | Card Format |
|----------|---------|------------|-------------|
| Human | open_id (ou_xxx) | `<at user_id="ou_xxx">nickname</at>` | `<at id=ou_xxx></at>` |
| Bot | App ID (cli_xxx) | `<at user_id="cli_xxx">botname</at>` | `<at id=cli_xxx></at>` |
| Everyone | "all" | `<at user_id="all">everyone</at>` | `<at id=all></at>` |

### @ Bot vs @ Human

**Important difference**:
- **Bots**: **MUST be @ mentioned to receive messages!** Without @, bots won't get notified
- **Humans**: Can see all group messages, @ not required

**⚠️ Feishu Limitation: Bot-to-Bot Messages**
- A bot CAN send messages and @ mention another bot
- But **bots can only receive messages from human accounts**
- Bots **cannot receive messages from other bots**
- Therefore, **@ mentioning another bot will NOT notify that bot**

**Practical implication**: 
- If you need to communicate with another bot, ask a human to send the message instead
- Bot-to-bot communication is not possible in Feishu groups

**Example - @ Bot**:
```javascript
// Raw mode
message({
  action: "send",
  channel: "feishu",
  target: "oc_xxx",
  message: "<at user_id=\"cli_xxx\">botname</at> Please reply!"
})
```

```
// Card mode
<at id=cli_xxx></at> Please reply!

**Markdown content**
```

### @ Everyone

**Note**: Requires group permission (Group Settings > Group Management > Who can @everyone)

```javascript
// Raw mode
message({
  action: "send",
  channel: "feishu",
  target: "oc_xxx",
  message: "<at user_id=\"all\">everyone</at> Important announcement!"
})
```

```
// Card mode
<at id=all></at> Important announcement!
```

### Common @ Mistakes

**Raw mode errors**:
- `@nickname` - Plain text, no notification
- `@{nickname}` - Plain text
- `<at id="ou_xxx"></at>` - id attribute doesn't work in Raw mode

**Card mode errors**:
- `<at user_id="ou_xxx">nickname</at>` - user_id attribute doesn't work in Card mode

---

## 4. Quick Reference

### Message Decision Tree

```
Need to send message
    │
    ├─ Plain text only?
    │   └─ YES → message tool (Raw mode)
    │
    └─ Need Markdown?
        └─ YES → Direct reply (Card mode)
```

### @ Mention Decision Tree

```
Need to @ mention
    │
    ├─ Using message tool?
    │   └─ YES → <at user_id="ID">nickname</at>
    │
    └─ Direct reply (Card mode)?
        └─ YES → <at id=ID></at>
```

### ID Format Reference

| Type | Format | Example |
|------|--------|---------|
| Human open_id | ou_xxx | ou_example123abc |
| Bot App ID | cli_xxx | cli_example456def |
| Group chat_id | oc_xxx | oc_example789ghi |

---

## 5. Important Notes

1. **Card and Raw mode use different @ formats** - Wrong format = @ fails
2. **Bots MUST be @ mentioned to receive messages** - Humans don't need @
3. **Bot-to-bot communication is NOT possible** - Bots can only receive messages from humans, not other bots
4. **message tool only sends Raw mode** - No Markdown rendering
5. **@everyone requires group permission**
6. **Avoid unsupported styles in Card mode** (blockquote, inline code, horizontal rule)

---

## Source

- Tested on: OpenClaw Feishu integration
- Test date: 2026-02-27 ~ 2026-02-28
- Source files:
  - `/home/admin/.openclaw/extensions/feishu/src/bot.ts`
  - `/home/admin/.openclaw/extensions/feishu/src/reply-dispatcher.ts`
  - `/home/admin/.openclaw/extensions/feishu/src/mention.ts`
  - `/home/admin/.openclaw/extensions/feishu/src/send.ts`
