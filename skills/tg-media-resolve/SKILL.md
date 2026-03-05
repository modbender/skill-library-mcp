---
name: tg-media-resolve
description: Resolve Telegram <media:image>, <media:document>, <media:video> and other media placeholders into actual files for vision/analysis. Use when a Telegram message contains a media placeholder (e.g. <media:image>) that you cannot see — typically in quoted/replied-to messages or group chat history. Downloads the media via Telegram Bot API and returns a local file path for the image tool or further processing.
---

# Telegram Media Resolver

Resolves `<media:*>` placeholders from Telegram messages into downloadable files.

## When to use

When you see `<media:image>`, `<media:document>`, `<media:video>`, `<media:sticker>`, `<media:voice>`, or `<media:animation>` in a Telegram message (especially in reply-quoted context or group history) and need to actually see/analyze the content.

## How it works

1. Temporarily forwards the target message via Bot API to get file metadata
2. Downloads the file from Telegram servers
3. Deletes the forwarded copy (cleanup)
4. Returns local file path for use with `image` tool or `exec`

## Usage

```bash
python3 scripts/fetch_media.py \
  --bot-token "$BOT_TOKEN" \
  --chat-id CHAT_ID \
  --message-id MESSAGE_ID \
  [--out /tmp] \
  [--forward-to SELF_CHAT_ID]
```

### Parameters

- `--bot-token` — Telegram Bot API token (read from OpenClaw config: `channels.telegram.botToken`)
- `--chat-id` — Chat where the message lives (from message context, e.g. `-1001234567890`)
- `--message-id` — ID of the message containing media (from `[id:XXXXX]` in message context)
- `--out` — Output directory (default: `/tmp`)
- `--forward-to` — Chat ID for temporary forward (default: same as `--chat-id`). Use bot owner's DM chat ID to avoid visible forwards in groups.

### Extracting parameters from message context

OpenClaw formats Telegram messages like:
```
[Telegram GroupName id:CHAT_ID topic:N ...] User (USER_ID): <media:image> [id:MSG_ID chat:CHAT_ID]
```

Extract `CHAT_ID` and `MSG_ID` from this format.

## Workflow

1. Extract `chat_id` and `message_id` from the message context
2. Read bot token: `cat ~/.openclaw/openclaw.json | python3 -c "import sys,json; print(json.load(sys.stdin)['channels']['telegram']['botToken'])"`
3. Run fetch script
4. Use returned file path with `image` tool for vision analysis

## Supported media types

Photos, documents, videos, animations (GIFs), stickers, voice messages, video notes, audio files.

## Limitations

- Bot must be a member of the chat containing the target message
- Files over 20MB cannot be downloaded via Bot API
- The temporary forward may briefly appear in the forward-to chat before deletion
- Use `--forward-to` with a private chat (e.g. bot owner's DM) to avoid visible forwards in group chats
