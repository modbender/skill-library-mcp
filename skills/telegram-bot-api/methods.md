# API Methods — Telegram Bot API

## Getting Updates

### getUpdates
Long polling to receive updates.

```bash
curl "https://api.telegram.org/bot${TOKEN}/getUpdates?offset=${OFFSET}&timeout=30"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| offset | No | ID of first update to return |
| limit | No | Max updates (1-100, default 100) |
| timeout | No | Long polling timeout in seconds |
| allowed_updates | No | Array of update types |

**Tip:** Set `offset` to `last_update_id + 1` to mark updates as processed.

### setWebhook
Set webhook URL for receiving updates.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/setWebhook" \
  -d "url=https://example.com/webhook" \
  -d "max_connections=40"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| url | Yes | HTTPS URL for webhook |
| certificate | No | Self-signed cert (PEM format) |
| ip_address | No | Fixed IP for webhook |
| max_connections | No | Max simultaneous connections (1-100) |
| allowed_updates | No | Array of update types |
| drop_pending_updates | No | Drop pending updates |
| secret_token | No | Secret token for verification |

### deleteWebhook
Remove webhook.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/deleteWebhook?drop_pending_updates=true"
```

### getWebhookInfo
Get current webhook status.

```bash
curl "https://api.telegram.org/bot${TOKEN}/getWebhookInfo"
```

---

## Sending Messages

### sendMessage
Send text message.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "text": "Hello!",
    "parse_mode": "HTML"
  }'
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| chat_id | Yes | Target chat ID |
| text | Yes | Message text (1-4096 chars) |
| parse_mode | No | HTML, MarkdownV2, or Markdown |
| entities | No | Special entities (bold, links, etc.) |
| link_preview_options | No | Link preview settings |
| disable_notification | No | Send silently |
| protect_content | No | Prevent forwarding/saving |
| reply_parameters | No | Reply to message |
| reply_markup | No | Keyboard markup |

### forwardMessage
Forward existing message.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/forwardMessage" \
  -d "chat_id=TARGET_CHAT_ID" \
  -d "from_chat_id=SOURCE_CHAT_ID" \
  -d "message_id=MESSAGE_ID"
```

### copyMessage
Copy message without "Forwarded from" header.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/copyMessage" \
  -d "chat_id=TARGET_CHAT_ID" \
  -d "from_chat_id=SOURCE_CHAT_ID" \
  -d "message_id=MESSAGE_ID"
```

### editMessageText
Edit sent message text.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/editMessageText" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "message_id": 100,
    "text": "Updated text",
    "parse_mode": "HTML"
  }'
```

### deleteMessage
Delete a message.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/deleteMessage" \
  -d "chat_id=123456789" \
  -d "message_id=100"
```

**Note:** Bots can only delete messages less than 48 hours old. Can delete own messages anytime.

---

## Sending Media

### sendPhoto
Send photo by file_id, URL, or upload.

```bash
# By URL
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendPhoto" \
  -d "chat_id=123456789" \
  -d "photo=https://example.com/photo.jpg" \
  -d "caption=Photo caption"

# Upload file
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendPhoto" \
  -F "chat_id=123456789" \
  -F "photo=@/path/to/photo.jpg" \
  -F "caption=Photo caption"
```

### sendDocument
Send file (any type).

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendDocument" \
  -F "chat_id=123456789" \
  -F "document=@/path/to/file.pdf" \
  -F "caption=Document caption"
```

**File size limits:**
- Photos: 10 MB
- Other files: 50 MB
- Use URL for files up to 20 MB download

### sendVideo
Send video file.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendVideo" \
  -F "chat_id=123456789" \
  -F "video=@/path/to/video.mp4" \
  -F "caption=Video caption" \
  -F "supports_streaming=true"
```

### sendAudio
Send audio file (music, displayed with cover and title).

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendAudio" \
  -F "chat_id=123456789" \
  -F "audio=@/path/to/audio.mp3" \
  -F "title=Song Title" \
  -F "performer=Artist"
```

### sendVoice
Send voice message (.ogg with OPUS).

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendVoice" \
  -F "chat_id=123456789" \
  -F "voice=@/path/to/voice.ogg"
```

### sendMediaGroup
Send album of photos/videos (2-10 items).

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/sendMediaGroup" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 123456789,
    "media": [
      {"type": "photo", "media": "https://example.com/1.jpg"},
      {"type": "photo", "media": "https://example.com/2.jpg"}
    ]
  }'
```

---

## Bot Management

### getMe
Get bot info.

```bash
curl "https://api.telegram.org/bot${TOKEN}/getMe"
```

### setMyCommands
Set bot command menu.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command": "start", "description": "Start the bot"},
      {"command": "help", "description": "Show help"},
      {"command": "settings", "description": "Bot settings"}
    ]
  }'
```

### setMyDescription
Set bot description (shown when user opens bot for first time).

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/setMyDescription" \
  -d "description=Your bot description here"
```

### setMyShortDescription
Set short description (shown in profile and forwarded messages).

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/setMyShortDescription" \
  -d "short_description=Short description"
```

---

## Chat Management

### getChat
Get chat info.

```bash
curl "https://api.telegram.org/bot${TOKEN}/getChat?chat_id=-1001234567890"
```

### getChatMember
Get info about a chat member.

```bash
curl "https://api.telegram.org/bot${TOKEN}/getChatMember?chat_id=-1001234567890&user_id=123456789"
```

### getChatMemberCount
Get member count.

```bash
curl "https://api.telegram.org/bot${TOKEN}/getChatMemberCount?chat_id=-1001234567890"
```

### banChatMember
Ban user from chat.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/banChatMember" \
  -d "chat_id=-1001234567890" \
  -d "user_id=123456789" \
  -d "revoke_messages=true"
```

### unbanChatMember
Unban user.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/unbanChatMember" \
  -d "chat_id=-1001234567890" \
  -d "user_id=123456789" \
  -d "only_if_banned=true"
```

---

## Callback Queries

### answerCallbackQuery
Respond to button press.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/answerCallbackQuery" \
  -d "callback_query_id=QUERY_ID" \
  -d "text=Action completed"
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| callback_query_id | Yes | From the update |
| text | No | Toast notification (200 chars) |
| show_alert | No | Show alert instead of toast |
| url | No | URL to open |
| cache_time | No | Cache time in seconds |

**Always answer callback queries** — even with empty response. User sees loading indicator until you answer.

---

## Inline Mode

### answerInlineQuery
Answer inline query.

```bash
curl -X POST "https://api.telegram.org/bot${TOKEN}/answerInlineQuery" \
  -H "Content-Type: application/json" \
  -d '{
    "inline_query_id": "QUERY_ID",
    "results": [
      {
        "type": "article",
        "id": "1",
        "title": "Result Title",
        "input_message_content": {
          "message_text": "Result message"
        }
      }
    ]
  }'
```

**Must enable inline mode** with @BotFather first: /setinline
