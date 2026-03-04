# GOWA API Endpoints Reference

Base URL: `http://localhost:3000` (default)

## Authentication
- No authentication required by default
- Optional Basic Auth (if GOWA started with `--basic-auth=user:password`)
  - Header: `Authorization: Basic <base64(user:password)>`

## Multi-Device Support
All device-scoped API calls require either:
- `X-Device-Id` header, or
- `device_id` query parameter

If only one device is registered, it will be used as default.

## Core Endpoints

### Device Management
- `GET /devices` - List all registered devices
- `POST /devices` - Add new device
- `GET /devices/:device_id` - Get device info
- `DELETE /devices/:device_id` - Remove device
- `GET /devices/:device_id/login` - Login with QR code
- `POST /devices/:device_id/login/code` - Login with pairing code
- `POST /devices/:device_id/logout` - Logout device
- `POST /devices/:device_id/reconnect` - Reconnect device
- `GET /devices/:device_id/status` - Get device connection status

### Legacy App Endpoints (backward compatibility)
- `GET /app/login` - Login with QR (scan)
- `GET /app/login-with-code` - Login with pairing code
- `GET /app/logout` - Logout
- `GET /app/reconnect` - Reconnect
- `GET /app/devices` - List devices
- `GET /app/status` - Connection status

### Send Messages
- `POST /send/message` - Send text message
  - Supports mentions: `@628xxx` in text
  - Ghost mentions: pass phone numbers in `mentions` field
  - Mention all: use `@everyone` keyword
- `POST /send/image` - Send image (auto-compress)
- `POST /send/file` - Send document
- `POST /send/video` - Send video (auto-compress)
- `POST /send/sticker` - Send sticker (auto-convert to WebP)
- `POST /send/contact` - Send contact card
- `POST /send/link` - Send link with preview
- `POST /send/location` - Send location
- `POST /send/poll` - Send poll/vote
- `POST /send/audio` - Send audio
- `POST /send/presence` - Send presence (available/unavailable)
- `POST /send/chat-presence` - Send typing indicator

### Message Operations
- `POST /message/:message_id/revoke` - Delete for everyone
- `POST /message/:message_id/reaction` - React to message
- `POST /message/:message_id/delete` - Delete for me
- `POST /message/:message_id/update` - Edit message
- `POST /message/:message_id/read` - Mark as read
- `POST /message/:message_id/star` - Star message
- `POST /message/:message_id/unstar` - Unstar message
- `GET /message/:message_id/download` - Download media

### User Info
- `GET /user/info` - Get user info
- `GET /user/avatar` - Get user avatar
- `POST /user/avatar` - Change avatar
- `POST /user/pushname` - Change display name
- `GET /user/my/groups` - List my groups (max 500)
- `GET /user/my/newsletters` - List my newsletters
- `GET /user/my/privacy` - Get privacy settings
- `GET /user/my/contacts` - List contacts
- `GET /user/check` - Check if user exists
- `GET /user/business-profile` - Get business profile

### Groups
- `POST /group` - Create group
- `POST /group/join-with-link` - Join via invite link
- `GET /group/info-from-link` - Get group info from link
- `GET /group/info` - Get group info
- `POST /group/leave` - Leave group
- `GET /group/participants` - List participants
- `POST /group/participants` - Add participants
- `POST /group/participants/remove` - Remove participant
- `POST /group/participants/promote` - Promote to admin
- `POST /group/participants/demote` - Demote from admin
- `GET /group/participants/export` - Export participants (CSV)
- `GET /group/participant-requests` - List join requests
- `POST /group/participant-requests/approve` - Approve join request
- `POST /group/participant-requests/reject` - Reject join request
- `POST /group/photo` - Set group photo
- `POST /group/name` - Set group name
- `POST /group/locked` - Lock group info (admin only edit)
- `POST /group/announce` - Set announcement mode
- `POST /group/topic` - Set group description
- `GET /group/invite-link` - Get invite link

### Chats
- `GET /chats` - Get chat list
- `GET /chat/:chat_jid/messages` - Get chat messages
- `POST /chat/:chat_jid/label` - Label chat
- `POST /chat/:chat_jid/pin` - Pin chat
- `POST /chat/:chat_jid/archive` - Archive chat
- `POST /chat/:chat_jid/disappearing` - Set disappearing messages

### Newsletter
- `POST /newsletter/unfollow` - Unfollow newsletter

## Common Request Formats

### Send Text Message
```json
{
  "phone": "628xxx",
  "message": "Hello everyone!",
  "mentions": ["@everyone"]
}
```

**Ghost Mention (mention all without showing @ in text):**
```json
{
  "phone": "628xxx@g.us",
  "message": "Important announcement",
  "mentions": ["@everyone"]
}
```
- Use `"@everyone"` to mention all group members
- Members get notification but no @ shown in message text
- Tested and working in both REST and MCP modes

**Regular Mentions (shows @phone in text):**
```json
{
  "phone": "628xxx",
  "message": "Hello @628xxx",
  "mentions": ["628xxx@s.whatsapp.net"]
}
```

### Send Document
```json
{
  "phone": "628xxx",
  "caption": "Document caption",
  "file": "base64_encoded_file_or_url"
}
```

### Get QR Code
```
GET /app/login
Returns: PNG image (QR code)
```

### List Groups
```
GET /user/my/groups
Returns: JSON array of group objects
```

## Response Format
Success:
```json
{
  "code": 200,
  "message": "Success",
  "data": {...}
}
```

Error:
```json
{
  "code": 400,
  "message": "Error description"
}
```

## Notes
- Phone numbers format: international without `+` (e.g., `628123456789`)
- JID format: `phone@s.whatsapp.net` for users, `phone@g.us` for groups
- Media files: can be base64 encoded or URL
- Auto-compression enabled for images and videos
- Stickers auto-converted to WebP format
