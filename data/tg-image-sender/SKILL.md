---
name: tg-image-sender
description: Send test or generated images directly to Telegram chats using the message tool with Picsum.photos URLs or custom media. Use when the user requests to 'send photo', 'generate image here in TG', or show/test images in Telegram (e.g., 'пришли фото', 'покажи картинку').
---

# TG Image Sender

## Quick Usage

Call the `message` tool directly:

```
message action=send channel=telegram media="https://picsum.photos/800/600?random=1" caption="Test image 🦞"
```

- **Size**: Adjust width/height, e.g., `https://picsum.photos/400/300`
- **Seed**: `https://picsum.photos/800/600?random=1234` for reproducible.
- **Real image**: Replace with actual URL/media path.
- **Caption**: Optional description.

## Examples

- Random photo: `media="https://picsum.photos/800/600?random=1"`
- Specific: `media="https://picsum.photos/seed/cat/800/600"`

After sending, use `NO_REPLY` to avoid duplicate text.

## Workflow

1. Match user request for TG image.
2. Generate Picsum URL or use provided.
3. Send via `message` tool.
4. NO_REPLY.

No scripts needed—pure tool call.