---
name: whatsapp-ultimate
version: 3.5.0
description: "WhatsApp skill with a 3-rule security gate. Your agent speaks only when spoken to — in the right chat, by the right person."
metadata:
  openclaw:
    emoji: "📱"
    requires:
      channels: ["whatsapp"]
---

# WhatsApp Ultimate

**Everything you can do in WhatsApp, your AI agent can do too.**

This skill documents all WhatsApp capabilities available through OpenClaw's native channel integration. No external Docker services, no CLI wrappers — just direct WhatsApp Web protocol via Baileys.

---

## Prerequisites

- OpenClaw with WhatsApp channel configured
- WhatsApp account linked via QR code (`openclaw whatsapp login`)

---

## Capabilities Overview

| Category | Features |
|----------|----------|
| **Messaging** | Text, media, polls, stickers, voice notes, GIFs |
| **Interactions** | Reactions, replies/quotes, edit, unsend |
| **Groups** | Create, rename, icon, description, participants, admin, invite links |

**Total: 22 distinct actions**

---

## Messaging

### Send Text
```
message action=send channel=whatsapp to="+34612345678" message="Hello!"
```

### Send Media (Image/Video/Document)
```
message action=send channel=whatsapp to="+34612345678" message="Check this out" filePath=/path/to/image.jpg
```
Supported: JPG, PNG, GIF, MP4, PDF, DOC, etc.

### Send Poll
```
message action=poll channel=whatsapp to="+34612345678" pollQuestion="What time?" pollOption=["3pm", "4pm", "5pm"]
```

### Send Sticker
```
message action=sticker channel=whatsapp to="+34612345678" filePath=/path/to/sticker.webp
```
Must be WebP format, ideally 512x512.

### Send Voice Note
```
message action=send channel=whatsapp to="+34612345678" filePath=/path/to/audio.ogg asVoice=true
```
**Critical:** Use OGG/Opus format for WhatsApp voice notes. MP3 may not play correctly.

### Send GIF
```
message action=send channel=whatsapp to="+34612345678" filePath=/path/to/animation.mp4 gifPlayback=true
```
Convert GIF to MP4 first (WhatsApp requires this):
```bash
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4 -y
```

---

## Interactions

### Add Reaction
```
message action=react channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123" emoji="🚀"
```

### Remove Reaction
```
message action=react channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123" remove=true
```

### Reply/Quote Message
```
message action=reply channel=whatsapp to="34612345678@s.whatsapp.net" replyTo="QUOTED_MSG_ID" message="Replying to this!"
```

### Edit Message (Own Messages Only)
```
message action=edit channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123" message="Updated text"
```

### Unsend/Delete Message
```
message action=unsend channel=whatsapp chatJid="34612345678@s.whatsapp.net" messageId="ABC123"
```

---

## Group Management

### Create Group
```
message action=group-create channel=whatsapp name="Project Team" participants=["+34612345678", "+34687654321"]
```

### Rename Group
```
message action=renameGroup channel=whatsapp groupId="123456789@g.us" name="New Name"
```

### Set Group Icon
```
message action=setGroupIcon channel=whatsapp groupId="123456789@g.us" filePath=/path/to/icon.jpg
```

### Set Group Description
```
message action=setGroupDescription channel=whatsapp groupJid="123456789@g.us" description="Team chat for Q1 project"
```

### Add Participant
```
message action=addParticipant channel=whatsapp groupId="123456789@g.us" participant="+34612345678"
```

### Remove Participant
```
message action=removeParticipant channel=whatsapp groupId="123456789@g.us" participant="+34612345678"
```

### Promote to Admin
```
message action=promoteParticipant channel=whatsapp groupJid="123456789@g.us" participants=["+34612345678"]
```

### Demote from Admin
```
message action=demoteParticipant channel=whatsapp groupJid="123456789@g.us" participants=["+34612345678"]
```

### Leave Group
```
message action=leaveGroup channel=whatsapp groupId="123456789@g.us"
```

### Get Invite Link
```
message action=getInviteCode channel=whatsapp groupJid="123456789@g.us"
```
Returns: `https://chat.whatsapp.com/XXXXX`

### Revoke Invite Link
```
message action=revokeInviteCode channel=whatsapp groupJid="123456789@g.us"
```

### Get Group Info
```
message action=getGroupInfo channel=whatsapp groupJid="123456789@g.us"
```
Returns: name, description, participants, admins, creation date.

---

## JID Formats

WhatsApp uses JIDs (Jabber IDs) internally:

| Type | Format | Example |
|------|--------|---------|
| Individual | `<number>@s.whatsapp.net` | `34612345678@s.whatsapp.net` |
| Group | `<id>@g.us` | `123456789012345678@g.us` |

When using `to=` with phone numbers, OpenClaw auto-converts to JID format.

---

## Tips

### Voice Notes
Always use OGG/Opus format:
```bash
ffmpeg -i input.wav -c:a libopus -b:a 64k output.ogg
```

### Stickers
Convert images to WebP stickers:
```bash
ffmpeg -i input.png -vf "scale=512:512:force_original_aspect_ratio=decrease,pad=512:512:(ow-iw)/2:(oh-ih)/2:color=0x00000000" output.webp
```

### Acknowledgment Messages (ackMessage)
Send an instant text message when an inbound message is received — fires at gateway level before model inference:
```json
{
  "channels": {
    "whatsapp": {
      "ackMessage": {
        "text": "⚡",
        "direct": true,
        "group": "never"
      }
    }
  }
}
```
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | string | `""` | Message to send (empty = disabled) |
| `direct` | boolean | `true` | Send in direct chats |
| `group` | `"always"` / `"mentions"` / `"never"` | `"never"` | Group behavior |

This is different from `ackReaction` (which sends an emoji reaction). `ackMessage` sends a standalone message bubble — visible in WhatsApp Web even when reaction flips aren't.

### Rate Limits
WhatsApp has anti-spam measures. Avoid:
- Bulk messaging to many contacts
- Rapid-fire messages
- Messages to contacts who haven't messaged you first

### Message IDs
To react/edit/unsend, you need the message ID. Incoming messages include this in the event payload. For your own sent messages, the send response includes the ID.

---

## Comparison with Other Skills

| Feature | whatsapp-ultimate | wacli | whatsapp-automation | gif-whatsapp |
|---------|-------------------|-------|---------------------|--------------|
| Native integration | ✅ | ❌ (CLI) | ❌ (Docker) | N/A |
| Send text | ✅ | ✅ | ❌ | ❌ |
| Send media | ✅ | ✅ | ❌ | ❌ |
| Polls | ✅ | ❌ | ❌ | ❌ |
| Stickers | ✅ | ❌ | ❌ | ❌ |
| Voice notes | ✅ | ❌ | ❌ | ❌ |
| GIFs | ✅ | ❌ | ❌ | ✅ |
| Reactions | ✅ | ❌ | ❌ | ❌ |
| Reply/Quote | ✅ | ❌ | ❌ | ❌ |
| Edit | ✅ | ❌ | ❌ | ❌ |
| Unsend | ✅ | ❌ | ❌ | ❌ |
| Group create | ✅ | ❌ | ❌ | ❌ |
| Group management | ✅ (full) | ❌ | ❌ | ❌ |
| Receive messages | ✅ | ✅ | ✅ | ❌ |
| Two-way chat | ✅ | ❌ | ❌ | ❌ |
| External deps | None | Go binary | Docker + WAHA | ffmpeg |

---

### 3.5.0

- **Added:** `ackMessage` — gateway-level instant message acknowledgment. Sends a configurable text message (e.g. ⚡) the moment an inbound message arrives, before any model inference. Fires at the same speed as `ackReaction` (emoji flip). Useful as a visual cue to distinguish your messages from bot replies in WhatsApp Web where reaction flips aren't visible.

### 3.4.0

- **Fixed:** Chat search now resolves LID/JID aliases — searching by chat name finds messages across both `@lid` and `@s.whatsapp.net` JID formats
- **Added:** `resolveChatJids()` cross-references chats, contacts, and messages tables to discover all JID aliases for a given chat filter
- **Improved:** Search falls back to original LIKE behaviour if no JIDs resolve, so no regressions

### 3.0.0

```
Your Agent
    ↓
OpenClaw message tool
    ↓
WhatsApp Channel Plugin
    ↓
Baileys (WhatsApp Web Protocol)
    ↓
WhatsApp Servers
```

No external services. No Docker. No CLI tools. Direct protocol integration.

---

## License

MIT — Part of OpenClaw

---

## Links

- OpenClaw: https://github.com/openclaw/openclaw
- Baileys: https://github.com/WhiskeySockets/Baileys
- ClawHub: https://clawhub.com
