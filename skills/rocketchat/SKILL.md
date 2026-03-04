---
name: rocketchat
description: Rocket.Chat team messaging - channels, messages, users, integrations via REST API
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - RC_URL
        - RC_TOKEN
        - RC_USER_ID
      bins:
        - curl
      anyBins:
        - jq
    primaryEnv: RC_TOKEN
    homepage: https://developer.rocket.chat/reference/api/rest-api
---

# Rocket.Chat Skill

Open-source team chat platform for communication and collaboration.

## Overview

Rocket.Chat supports:
- Channels (public/private), DMs, threads
- User and role management
- Integrations (webhooks, bots)
- Federation and omnichannel

Three room types: channels (`channels.*`), groups/private (`groups.*`), DMs (`im.*`). Generic `chat.*` endpoints work across all types via `roomId`.

## API Authentication

```bash
# Header-based auth
curl -s \
  -H "X-Auth-Token: $RC_TOKEN" \
  -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/me"

# Get tokens from login
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"user":"username","password":"password"}' \
  "$RC_URL/api/v1/login" | jq '{userId: .data.userId, authToken: .data.authToken}'
```

## Key Identifiers

- **roomId** — room identifier (e.g. `GENERAL`, `ByehQjC44FwMeiLbX`)
- **msgId** — alphanumeric message ID (not a timestamp like Slack)
- **emoji** — name without colons (e.g. `thumbsup`, `white_check_mark`)

Message context lines include `rocketchat message id` and `room` fields — reuse them directly.

## Channels

```bash
# List channels
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/channels.list?count=50"

# Channel info
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/channels.info?roomId=ROOM_ID"

# Get channel history
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/channels.history?roomId=ROOM_ID&count=50"

# Create channel
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"name":"new-channel","members":["user1"]}' \
  "$RC_URL/api/v1/channels.create"

# Archive channel
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"roomId":"ROOM_ID"}' \
  "$RC_URL/api/v1/channels.archive"

# Set channel topic
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"roomId":"ROOM_ID","topic":"Weekly standup notes"}' \
  "$RC_URL/api/v1/channels.setTopic"

# List channel members
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/channels.members?roomId=ROOM_ID&count=50"
```

For private groups use `groups.*`, for DMs use `im.*`. Same query params.

## Messages

```bash
# Send message (simple)
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"channel":"#general","text":"Hello!"}' \
  "$RC_URL/api/v1/chat.postMessage"
```

`channel` accepts: `#channel-name`, `@username` (DM), or a roomId.

```bash
# Send message (advanced — custom _id, alias, avatar)
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"message":{"rid":"ROOM_ID","msg":"Hello from Clawdbot"}}' \
  "$RC_URL/api/v1/chat.sendMessage"

# Read recent messages
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/channels.messages?roomId=ROOM_ID&count=20"

# Edit message
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"roomId":"ROOM_ID","msgId":"MSG_ID","text":"Updated text"}' \
  "$RC_URL/api/v1/chat.update"

# Delete message
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"roomId":"ROOM_ID","msgId":"MSG_ID"}' \
  "$RC_URL/api/v1/chat.delete"

# Search messages
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/chat.search?roomId=ROOM_ID&searchText=keyword"

# React to message (toggle — calling again removes it)
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"messageId":"MSG_ID","emoji":"thumbsup"}' \
  "$RC_URL/api/v1/chat.react"

# Get message (includes reactions in message.reactions field)
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/chat.getMessage?msgId=MSG_ID"
```

## Pins

```bash
# Pin a message
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"messageId":"MSG_ID"}' \
  "$RC_URL/api/v1/chat.pinMessage"

# Unpin a message
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"messageId":"MSG_ID"}' \
  "$RC_URL/api/v1/chat.unPinMessage"

# List pinned messages (query is URL-encoded {"pinned":true})
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/channels.messages?roomId=ROOM_ID&query=%7B%22pinned%22%3Atrue%7D"
```

## Users

```bash
# List users
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/users.list"

# Get user info (by username or userId)
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/users.info?username=john"

curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/users.info?userId=USER_ID"

# Create user (admin)
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John","username":"john","password":"pass123"}' \
  "$RC_URL/api/v1/users.create"

# Set user status
curl -s -X POST -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  -H "Content-Type: application/json" \
  -d '{"message":"In a meeting","status":"busy"}' \
  "$RC_URL/api/v1/users.setStatus"
```

## Emoji

```bash
# List custom emoji
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/emoji-custom.list"
```

## Integrations

```bash
# List webhooks
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/integrations.list?type=webhook-incoming"

# Use incoming webhook (no auth needed)
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"text":"Alert from external system!"}' \
  "$RC_URL/hooks/WEBHOOK_ID/WEBHOOK_TOKEN"
```

## Statistics

```bash
# Server statistics
curl -s -H "X-Auth-Token: $RC_TOKEN" -H "X-User-Id: $RC_USER_ID" \
  "$RC_URL/api/v1/statistics"
```

## Rate Limits

Default: 20 requests/second per user. Check headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`.

## Ideas to try

- React with `white_check_mark` to mark completed tasks
- Pin key decisions or weekly status updates
- Search messages for past discussions before asking a question
- Create project-specific channels and set descriptive topics
- DM users via `chat.postMessage` with `"channel": "@username"`
- Use incoming webhooks for external system alerts without auth

For full documentation, see [Rocket.Chat API Docs](https://developer.rocket.chat/reference/api).
