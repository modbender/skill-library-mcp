---
name: quotly-style-sticker
description: Generate QuotLy-style stickers from forwarded messages and return one MEDIA path for auto-send. Use when users ask to create quote stickers from selected forwarded messages or quoted messages in groups.
---

# QuotLy Style Sticker

## How To Call (Agent)

1. Build payload with required `selected_messages`.
2. When available, include event metadata for dedupe:
   - `context.event.channel` (example: `telegram`)
   - `context.event.update_id` (preferred)
   - fallback keys: `event_id`, `delivery_id`, `id`
3. Run:
   - `python3 scripts/openclaw_quote_autoreply.py --input <json-file-or->`
4. Use tool-emitted `MEDIA:` for delivery.
5. Final assistant text must be empty.

## Input

- Required: `selected_messages` (array, must not be empty)
- Optional: `context.event` for dedupe accuracy
  - `channel` (string)
  - `update_id` (string or number, preferred)
  - `event_id` / `delivery_id` / `id` (fallback keys)
- Each item structure:
  ```json5
  {
    "message": {
      "message_id": 2002,
      "text": "Forwarded message content",
      "forward_from": {
        "type": "hidden_user",  // optional, indicates hidden user
        "id": 123456789,        // optional, user id
        "first_name": "张",     // required, first name or nickname
        "last_name": "三",      // optional, last name
        "avatar_url": "",       // optional, avatar url or base64 data (from user profile or platform API)
        "status_url": ""        // optional, status url or base64 data (from user profile or platform API)
      }
    },
    // Optional: override message fields
    "overwrite_message": {
      "text": "哈哈哈哈哈",
      "forward_from": {
        "avatar_url": "",       // from user profile or platform API
        "status_url": ""        // from user profile or platform API
      },
      "entities": [  // optional, text formatting entities
        {"type": "bold", "offset": 0, "length": 4},
        {"type": "italic", "offset": 5, "length": 4}
      ]
    }
  }
  ```
- Optional canvas: `width`, `height`, `scale`, `max_width`, `border_radius`, `picture_radius`, `background_color`

## Entities (Text Formatting)

The skill supports Telegram-style message entities for text formatting:

```json5
[
  {"type": "bold", "offset": 0, "length": 5},
  {"type": "italic", "offset": 6, "length": 6},
  {"type": "url", "offset": 13, "length": 15, "url": "https://example.com"}
]
```

**Supported types:** `mention`, `hashtag`, `cashtag`, `bot_command`, `url`, `email`, `phone_number`, `bold`, `italic`, `underline`, `strikethrough`, `spoiler`, `code`, `pre`, `text_link`, `text_mention`, `custom_emoji`

**Entity fields:**
- `type` (required) - entity type
- `offset` (required) - UTF-8 offset in text
- `length` (required) - UTF-8 length
- `url` (optional) - for `text_link` type
- `user` (optional) - for `text_mention` type
- `language` (optional) - for `pre` type
- `custom_emoji_id` (optional) - for `custom_emoji` type

## Field Mapping

- Quote text:
  - `overwrite_message.text` > `message.text`
- Name/avatar:
  - `overwrite_message.forward_from` > `message.forward_from`
- Text formatting (entities):
  - `overwrite_message.entities` > `message.entities` > `message.caption_entities`

## Output

- stdout includes:
  - `Quote sticker generated.`
  - `MEDIA:<absolute-path-to-webp>`
- For duplicate retries detected within dedupe window, generation is skipped and no `MEDIA:` line is emitted.

## Environment Variables

- `QUOTLY_API_URL` - QuotLy API endpoint (default: `https://bot.lyo.su/quote/generate`).
- `QUOTLY_API_ALLOW_HOSTS` - Comma-separated list of allowed API hosts (e.g., `bot.lyo.su`). When set, the skill will only contact hosts in this list.
- `QUOTLY_AUDIT_LOG` - Set to `1`, `true`, or `yes` to enable audit logging to stderr.
- `QUOTLY_DEDUP_WINDOW_SECONDS` - Suppress duplicate requests for the same event/payload within this window (default: `180`). Set to `0` to disable.

## Dedupe Key (How `_build_dedupe_key` reads input)

`_build_dedupe_key(input_payload)` resolves keys in this order:

1. `context.event.update_id` (or `event_id` / `delivery_id` / `id`)
2. `event.update_id` (or `event_id` / `delivery_id` / `id`) when `context.event` is missing
3. `context.event.update.update_id` (nested update object)
4. Fallback: stable hash of `selected_messages`

Recommended wrapper payload:

```json
{
  "context": {
    "event": {
      "channel": "telegram",
      "update_id": 123456789
    }
  },
  "selected_messages": [
    {
      "message": {
        "message_id": 2002,
        "text": "Forwarded message content"
      }
    }
  ]
}
```

## Security Notes

- This skill sends message content to an external API to generate stickers.
- **SSRF Protection**: Multiple layers of protection are implemented:
  - Hostname validation blocks internal/private IPs, localhost, and metadata endpoints
  - DNS rebinding protection: resolves hostnames and validates resolved IPs
  - Path traversal prevention: blocks `..` and suspicious path patterns
  - URL credentials stripping: removes username/password from URLs
- **Request Limits**: Maximum payload size 1MB, maximum response size 10MB
- **Audit Logging**: Enable with `QUOTLY_AUDIT_LOG=1` to log API requests and responses for security monitoring
- In sensitive environments, always set `QUOTLY_API_ALLOW_HOSTS` to restrict which hosts the skill can contact.
- Avatar and status URLs from user input are passed to the rendering service; ensure input comes from trusted sources.

## Reply Rule

- Do not output any final text.
