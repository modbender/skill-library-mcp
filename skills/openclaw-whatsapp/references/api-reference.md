# openclaw-whatsapp API Reference

Base URL: `http://localhost:8555`

## Status & Auth

### GET /status
Connection status, uptime, and version.

### GET /qr
QR code web page for WhatsApp device linking. Auto-refreshes every 3s.

### GET /qr/data
QR code as base64 PNG in JSON: `{"qr": "data:image/png;base64,..."}`

### POST /logout
Unlink the WhatsApp device.

## Messaging

### POST /send/text
Send a text message.
```json
{"to": "+971558762351", "message": "Hello!"}
```

### POST /send/file
Send a file (multipart form data).
- `file` — the file
- `to` — recipient phone number
- `caption` — optional caption

### POST /reply
Agent reply endpoint. Used by agents to send replies back through WhatsApp.
```json
{
  "to": "971558762351@s.whatsapp.net",
  "message": "Hello!",
  "quote_message_id": "ABC123"
}
```
- `to` (required) — recipient JID
- `message` (required) — reply text
- `quote_message_id` (optional) — message ID to quote-reply

## Messages

### GET /messages?chat=JID&limit=50
Get messages for a chat. Parameters:
- `chat` — JID of the chat
- `limit` — max messages to return (default 50)

### GET /messages/search?q=keyword
Full-text search across all messages using SQLite FTS5.

### GET /chats
List all chats with their last message.

### GET /chats/{jid}/messages
Get messages for a specific chat by JID. Supports `?limit=N`.

## Contacts

### GET /contacts
List all synced contacts with names and phone numbers.

## Webhook Payload

When `webhook_url` is configured, incoming messages are POSTed as:

```json
{
  "from": "971558762351@s.whatsapp.net",
  "name": "Sam",
  "message": "Hey!",
  "timestamp": 1708387200,
  "type": "text",
  "media_url": "",
  "chat_type": "dm",
  "group_name": "",
  "message_id": "ABC123"
}
```
