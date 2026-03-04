---
name: feishu-reaction
description: Add or remove emoji reactions on Feishu (Lark) messages, and respond to user reactions. Use when the user asks to react to a message, add an emoji/expression to a message, when you want to acknowledge a message with a reaction instead of a text reply, or when the user reacts to your message with an emoji. Also enables proactive reactions to incoming messages based on sentiment. Requires Feishu channel configured in OpenClaw with im:message.reactions permission.
---

# Feishu Reaction

Add/remove emoji reactions on Feishu messages via API. Enables richer, more playful interactions beyond text.

## Usage

```bash
# Add reaction
bash scripts/feishu-reaction.sh <message_id> <emoji_type>

# Remove reaction
bash scripts/feishu-reaction.sh <message_id> <emoji_type> remove
```

Resolve `scripts/feishu-reaction.sh` relative to this skill's directory.

## Getting message_id

The `message_id` comes from inbound message metadata (e.g., `om_x100b554e82c620a4c...`). Use the current message's `message_id` from conversation context.

## Behavior Guide

### Proactive reactions to user messages

React to user messages naturally, like a human would:
- User says something nice → HEART, THUMBSUP, or YEAH
- User shares good news → PARTY, FIREWORKS, or CLAP
- User asks for help → OK (then reply with text)
- User sends something funny → SMILE or WITTY

Don't overdo it — not every message needs a reaction. Use when it adds warmth without cluttering.

### Responding to user reactions

When a user reacts to your message with an emoji, respond appropriately:

**Positive/neutral reactions** (HEART, THUMBSUP, YEAH, GoGoGo, FISTBUMP, PARTY, CLAP, SMILE, WOW, SaluteFace, WINK, GLANCE, etc.):
→ React back with a complementary emoji. No text reply needed.

**Negative/questioning reactions** (ANGRY, SPEECHLESS, FACEPALM, CRY, TERROR, SWEAT, WHAT, etc.):
→ React back with a caring emoji (HUG, HEART) AND follow up with a text message asking what's wrong.

### Choosing reaction emojis

Pick reactions that feel natural and varied — don't always use the same one. Match the energy:
- They send ❤️ → reply with 🤗 or ❤️
- They send 💪 → reply with 🔥 or 💪
- They send 👀 → reply with 😉

## Available Emoji Types

Common: `THUMBSUP`, `SMILE`, `OK`, `HEART`, `LOVE`, `THANKS`, `YEAH`, `AWESOME`, `PARTY`, `CLAP`, `APPLAUSE`

Emotions: `CRY`, `ANGRY`, `SHY`, `BLUSH`, `SPEECHLESS`, `TERROR`, `WOW`, `FACEPALM`, `SWEAT`, `PROUD`, `OBSESSED`

Actions: `WAVE`, `HUG`, `KISS`, `WINK`, `TONGUE`, `MUSCLE`, `SALUTE`

Objects: `FIRE`, `BEER`, `CAKE`, `GIFT`, `ROSE`, `FIREWORKS`

Other: `WITTY`, `JIAYI`

## Prerequisites

- Feishu channel configured in OpenClaw (`openclaw.json` has `channels.feishu.appId` and `appSecret`)
- App has `im:message:reaction` permission (飞书开放平台 → 应用权限 → 消息与群组 → 表情回复)

## Examples

React with thumbs up to acknowledge a message:
```bash
bash scripts/feishu-reaction.sh "om_xxx" "THUMBSUP"
```

React with heart to show appreciation:
```bash
bash scripts/feishu-reaction.sh "om_xxx" "HEART"
```

Remove a reaction:
```bash
bash scripts/feishu-reaction.sh "om_xxx" "THUMBSUP" remove
```
