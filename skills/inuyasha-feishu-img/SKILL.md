---
name: feishu-im
description: |
  Feishu IM messaging operations: send messages, images, files to users and groups via Bot API.
  Activate when user mentions: 飞书发图、发送图片、飞书消息、im:resource、image_key、飞书附件、飞书机器人发消息。
---

# Feishu IM Tool

Use the `message` tool with `channel=feishu` for all IM operations.

## Send Text Message

```
message(action=send, channel=feishu, target=<user_id or chat_id>, message="text")
```

## Send Image (CORRECT method)

**Always use `filePath` or `media`, never paste a raw path in message text.**

```
message(action=send, channel=feishu, target=<chat_id>, filePath="/absolute/path/to/image.jpg")
```

Or with caption:

```
message(action=send, channel=feishu, target=<chat_id>, media="/path/to/image.jpg", message="caption text")
```

The tool handles the two-step upload internally:
1. POST /im/v1/images → get image_key
2. POST /im/v1/messages with image_key

## Common Failure Modes — Images Show as Path/Link

See `references/image-sending-pitfalls.md` for full diagnosis.

**TL;DR root causes:**
- Assistant wrote raw file path in message text instead of calling `message` tool → plain text, no upload
- Used `MEDIA:/absolute/path` → security filter strips it
- `image_type` wrong during upload (must be `message`, not `avatar`)
- `tenant_access_token` expired (TTL ~2h) → upload silently fails, key is empty
- Webhook custom bot used instead of Bot App → no access_token, can't upload images

## Permissions Required

| Scope | Purpose |
|-------|---------|
| `im:resource` | Upload image/file to IM, get file_key / image_key |
| `im:message` | Send messages with media |
| `im:message:send_as_bot` | Send as bot identity |

All three are currently granted on this installation.

## Bot Type Comparison

| Feature | Webhook Custom Bot | Bot App (自建应用) |
|---------|-------------------|-------------------|
| Send text | ✅ | ✅ |
| Send image | ⚠️ base64 only (不推荐) | ✅ via image_key |
| access_token | ❌ 无 | ✅ tenant_access_token |
| Upload API | ❌ 不支持 | ✅ /im/v1/images |

**OpenClaw uses Bot App — always use the `message` tool, not raw Webhook POST.**

## Token Refresh

`tenant_access_token` expires in ~2 hours. If uploads silently fail:
- Error code `99991663` = image_key invalid
- Error code `99991400` = token expired

OpenClaw refreshes tokens automatically on each API call. If you see these errors, check Gateway logs.

## References

- `references/image-sending-pitfalls.md` — detailed failure mode diagnosis
- Feishu API docs: https://open.feishu.cn/document/server-docs/im-v1/image/create
