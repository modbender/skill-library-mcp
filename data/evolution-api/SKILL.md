---
name: evolution-api-v2
description: Complete WhatsApp automation via Evolution API v2.3 - instances, messages (text/media/polls/lists/buttons/status), groups, labels, chatbots (Typebot/OpenAI/Dify/Flowise/N8N/EvoAI), webhooks, proxy, S3 storage, and Chatwoot integration
metadata:
  openclaw:
    requires:
      bins: []
    env:
      EVO_API_URL: "Evolution API base URL (e.g., http://localhost:8080 or https://api.yourdomain.com)"
      EVO_GLOBAL_KEY: "Global API key for admin operations (instance management)"
      EVO_INSTANCE: "Default instance name"
      EVO_API_KEY: "Instance-specific API key for messaging operations"
---

# Evolution API v2.3

Complete WhatsApp automation via Evolution API v2.3. Send messages, manage groups, integrate chatbots (Typebot, OpenAI, Dify, Flowise, N8N, Evo AI), configure webhooks, and connect with Chatwoot.

---

## Quick Start

### 1. Set Environment Variables

```json5
{
  env: {
    EVO_API_URL: "http://localhost:8080",       // Your API URL
    EVO_GLOBAL_KEY: "your-global-admin-key",    // Admin key (instance mgmt)
    EVO_INSTANCE: "my-bot",                     // Instance name
    EVO_API_KEY: "your-instance-token"          // Instance token (messaging)
  }
}
```

### 2. Create Instance & Connect

```bash
# Create instance (supports Baileys, Business, or Evolution integration)
curl -X POST "$EVO_API_URL/instance/create" \
  -H "apikey: $EVO_GLOBAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "my-bot",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'

# Connect & get QR code
curl -X GET "$EVO_API_URL/instance/connect/$EVO_INSTANCE" \
  -H "apikey: $EVO_API_KEY"
```

Scan the QR code returned in `base64` field. Alternately pass `?number=5511999999999` for pairing code.

### 3. Send First Message

```bash
curl -X POST "$EVO_API_URL/message/sendText/$EVO_INSTANCE" \
  -H "apikey: $EVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "number": "5511999999999",
    "text": "Hello from Evolution API v2! 🚀"
  }'
```

---

## Authentication

Two authentication levels:

| Type | Header | Usage |
|------|--------|-------|
| **Global API Key** | `apikey: $EVO_GLOBAL_KEY` | Admin: create/delete instances, fetch all |
| **Instance API Key** | `apikey: $EVO_API_KEY` | Messaging, groups, chat, profile, labels |

All instance endpoints use the path pattern: `/{resource}/{action}/{instanceName}`

---

## Core Concepts

### Phone Number Formats

| Context | Format | Example |
|---------|--------|---------|
| **Sending messages** | Country code + number | `5511999999999` |
| **Group JID** | Group ID | `999999999999999999@g.us` |
| **User JID** | Number + suffix | `5511999999999@s.whatsapp.net` |

### Integration Types

| Value | Description |
|-------|-------------|
| `WHATSAPP-BAILEYS` | Unofficial (default, full features) |
| `WHATSAPP-BUSINESS` | Official Cloud API |
| `EVOLUTION` | Evolution channel |

### Message Delay

Add `delay` (milliseconds) to avoid rate limits:
```json
{ "delay": 1200 }
```

---

## Feature Reference

### Instance Management

#### Create Instance
```bash
POST /instance/create
Header: apikey: $EVO_GLOBAL_KEY

{
  "instanceName": "my-bot",
  "qrcode": true,
  "integration": "WHATSAPP-BAILEYS",
  // Optional
  "token": "custom-api-key",
  "number": "5511999999999",
  // Settings (optional)
  "rejectCall": false,
  "msgCall": "",
  "groupsIgnore": false,
  "alwaysOnline": false,
  "readMessages": false,
  "readStatus": false,
  "syncFullHistory": false,
  // Proxy (optional)
  "proxyHost": "",
  "proxyPort": "",
  "proxyProtocol": "",
  "proxyUsername": "",
  "proxyPassword": ""
}
```

**Inline webhook** (optional during creation):
```json
{
  "webhook": {
    "url": "https://webhook.site/your-id",
    "byEvents": false,
    "base64": true,
    "headers": {
      "autorization": "Bearer TOKEN"
    },
    "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
  }
}
```

**Inline RabbitMQ / SQS** (optional during creation):
```json
{
  "rabbitmq": { "enabled": true, "events": ["MESSAGES_UPSERT"] },
  "sqs": { "enabled": true, "events": ["MESSAGES_UPSERT"] }
}
```

**Inline Chatwoot** (optional during creation):
```json
{
  "chatwootAccountId": "1",
  "chatwootToken": "TOKEN",
  "chatwootUrl": "https://chatwoot.com",
  "chatwootSignMsg": true,
  "chatwootReopenConversation": true,
  "chatwootConversationPending": false,
  "chatwootImportContacts": true,
  "chatwootNameInbox": "evolution",
  "chatwootMergeBrazilContacts": true,
  "chatwootImportMessages": true,
  "chatwootDaysLimitImportMessages": 3
}
```

#### Fetch Instances
```bash
GET /instance/fetchInstances
Header: apikey: $EVO_GLOBAL_KEY

# Optional query params:
# ?instanceName=my-bot
# ?instanceId=INSTANCE_ID
```

#### Connect Instance (QR Code)
```bash
GET /instance/connect/{instance}
Header: apikey: $EVO_API_KEY

# Optional: ?number=5511999999999 (for pairing code)
```

#### Connection Status
```bash
GET /instance/connectionState/{instance}
Header: apikey: $EVO_API_KEY
```

#### Restart Instance
```bash
POST /instance/restart/{instance}
Header: apikey: $EVO_API_KEY
```

#### Set Presence
```bash
POST /instance/setPresence/{instance}
Header: apikey: $EVO_API_KEY

{ "presence": "available" }
```
**Options:** `available`, `unavailable`

#### Logout Instance
```bash
DELETE /instance/logout/{instance}
Header: apikey: $EVO_API_KEY
```

#### Delete Instance
```bash
DELETE /instance/delete/{instance}
Header: apikey: $EVO_GLOBAL_KEY
```

---

### Settings

#### Set Settings
```bash
POST /settings/set/{instance}
Header: apikey: $EVO_API_KEY

{
  "rejectCall": true,
  "msgCall": "I do not accept calls",
  "groupsIgnore": false,
  "alwaysOnline": true,
  "readMessages": false,
  "syncFullHistory": false,
  "readStatus": false
}
```

#### Find Settings
```bash
GET /settings/find/{instance}
Header: apikey: $EVO_API_KEY
```

---

### Proxy

#### Set Proxy
```bash
POST /proxy/set/{instance}
Header: apikey: $EVO_API_KEY

{
  "enabled": true,
  "host": "0.0.0.0",
  "port": "8000",
  "protocol": "http",
  "username": "user",
  "password": "pass"
}
```

#### Find Proxy
```bash
GET /proxy/find/{instance}
Header: apikey: $EVO_API_KEY
```

---

### Send Messages

#### Send Text
```bash
POST /message/sendText/{instance}

{
  "number": "5511999999999",
  "text": "Hello World!"
  // Options:
  // "delay": 1200,
  // "linkPreview": false,
  // "mentionsEveryOne": false,
  // "mentioned": ["5511888888888"],
  // "quoted": { "key": { "id": "MESSAGE_ID" }, "message": { "conversation": "quoted text" } }
}
```

#### Send Media (URL)
```bash
POST /message/sendMedia/{instance}

{
  "number": "5511999999999",
  "mediatype": "image",
  "mimetype": "image/png",
  "caption": "Caption text",
  "media": "https://example.com/photo.jpg",
  "fileName": "photo.png"
  // Options: delay, quoted, mentionsEveryOne, mentioned
}
```

**Media types:** `image`, `video`, `document`

#### Send Media (File Upload)
```bash
POST /message/sendMedia/{instance}
Content-Type: multipart/form-data

# Use form-data with file field
```

#### Send PTV (Round Video)
```bash
POST /message/sendPtv/{instance}

{
  "number": "5511999999999",
  "video": "https://example.com/video.mp4"
  // Options: delay, quoted, mentionsEveryOne, mentioned
}
```

Also supports file upload via form-data.

#### Send Narrated Audio (Voice Note)
```bash
POST /message/sendWhatsAppAudio/{instance}

{
  "number": "5511999999999",
  "audio": "https://example.com/audio.mp3"
  // Options: delay, quoted, encoding (true/false)
}
```

#### Send Status/Stories
```bash
POST /message/sendStatus/{instance}

{
  "type": "text",
  "content": "My status update!",
  "backgroundColor": "#008000",
  "font": 1,
  "allContacts": false,
  "statusJidList": ["5511999999999@s.whatsapp.net"]
}
```

**Types:** `text`, `image`, `video`, `audio`  
**Fonts (text only):** `1` SERIF, `2` NORICAN_REGULAR, `3` BRYNDAN_WRITE, `4` BEBASNEUE_REGULAR, `5` OSWALD_HEAVY  
For image/video: use `content` as URL and `caption` for text.

#### Send Sticker
```bash
POST /message/sendSticker/{instance}

{
  "number": "5511999999999",
  "sticker": "https://example.com/sticker.webp"
  // Options: delay, quoted
}
```

#### Send Location
```bash
POST /message/sendLocation/{instance}

{
  "number": "5511999999999",
  "name": "Bora Bora",
  "address": "French Polynesia",
  "latitude": -16.505538,
  "longitude": -151.742277
  // Options: delay, quoted
}
```

#### Send Contact (vCard)
```bash
POST /message/sendContact/{instance}

{
  "number": "5511999999999",
  "contact": [
    {
      "fullName": "Contact Name",
      "wuid": "559999999999",
      "phoneNumber": "+55 99 9 9999-9999",
      "organization": "Company",
      "email": "email@example.com",
      "url": "https://example.com"
    }
  ]
}
```

Multiple contacts can be sent in the array.

#### Send Reaction
```bash
POST /message/sendReaction/{instance}

{
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "BAE5A75CB0F39712"
  },
  "reaction": "🚀"
}
```

Set `reaction: ""` to remove.

#### Send Poll
```bash
POST /message/sendPoll/{instance}

{
  "number": "5511999999999",
  "name": "What is your favorite color?",
  "selectableCount": 1,
  "values": ["Red", "Blue", "Green"]
  // Options: delay, quoted
}
```

#### Send List
```bash
POST /message/sendList/{instance}

{
  "number": "5511999999999",
  "title": "List Title",
  "description": "Choose an option",
  "buttonText": "Click Here",
  "footerText": "Footer text",
  "sections": [
    {
      "title": "Section 1",
      "rows": [
        {
          "title": "Option A",
          "description": "Description of option A",
          "rowId": "opt_a"
        },
        {
          "title": "Option B",
          "description": "Description of option B",
          "rowId": "opt_b"
        }
      ]
    }
  ]
  // Options: delay, quoted
}
```

#### Send Buttons
```bash
POST /message/sendButtons/{instance}

{
  "number": "5511999999999",
  "title": "Button Title",
  "description": "Button Description",
  "footer": "Footer Text",
  "buttons": [
    { "type": "reply", "displayText": "Reply", "id": "btn_1" },
    { "type": "copy", "displayText": "Copy Code", "copyCode": "ABC123" },
    { "type": "url", "displayText": "Open Link", "url": "https://example.com" },
    { "type": "call", "displayText": "Call Us", "phoneNumber": "5511999999999" },
    { "type": "pix", "currency": "BRL", "name": "John Doe", "keyType": "random", "key": "uuid-key" }
  ]
  // Options: delay, quoted
}
```

**Button types:** `reply`, `copy`, `url`, `call`, `pix`  
**Pix keyType:** `phone`, `email`, `cpf`, `cnpj`, `random`

---

### Chat Operations

#### Check WhatsApp Numbers
```bash
POST /chat/whatsappNumbers/{instance}

{
  "numbers": [
    "55911111111",
    "55922222222",
    "55933333333"
  ]
}
```

#### Read Messages (Mark as Read)
```bash
POST /chat/markMessageAsRead/{instance}

{
  "readMessages": [
    {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "MESSAGE_ID"
    }
  ]
}
```

#### Archive Chat
```bash
POST /chat/archiveChat/{instance}

{
  "lastMessage": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "MESSAGE_ID"
    }
  },
  "chat": "5511999999999@s.whatsapp.net",
  "archive": true
}
```

Set `archive: false` to unarchive.

#### Mark Chat Unread
```bash
POST /chat/markChatUnread/{instance}

{
  "lastMessage": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "MESSAGE_ID"
    }
  },
  "chat": "5511999999999@s.whatsapp.net"
}
```

#### Delete Message
```bash
DELETE /chat/deleteMessageForEveryone/{instance}

{
  "id": "MESSAGE_ID",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "fromMe": true,
  "participant": "participant_jid"
}
```

#### Update Message (Edit)
```bash
POST /chat/updateMessage/{instance}

{
  "number": "5511999999999",
  "key": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "fromMe": true,
    "id": "MESSAGE_ID"
  },
  "text": "new edited message"
}
```

#### Send Presence (Typing Indicator)
```bash
POST /chat/sendPresence/{instance}

{
  "number": "5511999999999",
  "delay": 1200,
  "presence": "composing"
}
```

**Options:** `composing`, `recording`, `paused`

#### Update Block Status
```bash
POST /message/updateBlockStatus/{instance}

{
  "number": "5511999999999",
  "status": "block"
}
```

**Options:** `block`, `unblock`

#### Fetch Profile Picture
```bash
POST /chat/fetchProfilePictureUrl/{instance}

{ "number": "5511999999999" }
```

#### Get Base64 From Media Message
```bash
POST /chat/getBase64FromMediaMessage/{instance}

{
  "message": {
    "key": { "id": "MESSAGE_ID" }
  },
  "convertToMp4": false
}
```

Extracts base64 from received media. Set `convertToMp4: true` for audio files to get MP4 instead of OGG.

#### Find Contacts
```bash
POST /chat/findContacts/{instance}

{
  "where": {
    "id": "5511999999999"
  }
}
```

Omit `id` to list all contacts.

#### Find Messages
```bash
POST /chat/findMessages/{instance}

{
  "where": {
    "key": {
      "remoteJid": "5511999999999"
    }
  },
  "page": 1,
  "offset": 10
}
```

#### Find Status Message
```bash
POST /chat/findStatusMessage/{instance}

{
  "where": {
    "remoteJid": "5511999999999@s.whatsapp.net",
    "id": "MESSAGE_ID"
  },
  "page": 1,
  "offset": 10
}
```

#### Find Chats
```bash
POST /chat/findChats/{instance}
```

---

### Calls

#### Fake Call (Offer)
```bash
POST /call/offer/{instance}

{
  "number": "5511999999999",
  "isVideo": false,
  "callDuration": 3
}
```

Simulates a call offer to the number. `callDuration` is in seconds.

---

### Labels

#### Find Labels
```bash
GET /label/findLabels/{instance}
```

#### Handle Labels (Add/Remove)
```bash
POST /label/handleLabel/{instance}

{
  "number": "5511999999999",
  "labelId": "label_id_here",
  "action": "add"
}
```

**Actions:** `add`, `remove`

---

### Profile Settings

#### Fetch Business Profile
```bash
POST /chat/fetchBusinessProfile/{instance}

{ "number": "5511999999999" }
```

#### Fetch Profile
```bash
POST /chat/fetchProfile/{instance}

{ "number": "5511999999999" }
```

#### Update Profile Name
```bash
POST /chat/updateProfileName/{instance}

{ "name": "My Bot Name" }
```

#### Update Profile Status
```bash
POST /chat/updateProfileStatus/{instance}

{ "status": "Available 24/7" }
```

#### Update Profile Picture
```bash
POST /chat/updateProfilePicture/{instance}

{ "picture": "https://example.com/avatar.jpg" }
```

#### Remove Profile Picture
```bash
DELETE /chat/removeProfilePicture/{instance}
```

#### Fetch Privacy Settings
```bash
GET /chat/fetchPrivacySettings/{instance}
```

#### Update Privacy Settings
```bash
POST /chat/updatePrivacySettings/{instance}

{
  "readreceipts": "all",
  "profile": "all",
  "status": "contacts",
  "online": "all",
  "last": "contacts",
  "groupadd": "none"
}
```

**Privacy values:**
- `readreceipts`: `all`, `none`
- `profile`: `all`, `contacts`, `contact_blacklist`, `none`
- `status`: `all`, `contacts`, `contact_blacklist`, `none`
- `online`: `all`, `match_last_seen`
- `last`: `all`, `contacts`, `contact_blacklist`, `none`
- `groupadd`: `all`, `contacts`, `contact_blacklist`

---

### Group Management

#### Create Group
```bash
POST /group/create/{instance}

{
  "subject": "Group Name",
  "description": "Group description (optional)",
  "participants": [
    "5531900000000",
    "5531900000000"
  ]
}
```

#### Update Group Picture
```bash
POST /group/updateGroupPicture/{instance}?groupJid={groupJid}

{ "image": "https://example.com/group-photo.png" }
```

#### Update Group Subject (Name)
```bash
POST /group/updateGroupSubject/{instance}?groupJid={groupJid}

{ "subject": "New Group Name" }
```

#### Update Group Description
```bash
POST /group/updateGroupDescription/{instance}?groupJid={groupJid}

{ "description": "New group description" }
```

#### Fetch Invite Code
```bash
GET /group/inviteCode/{instance}?groupJid={groupJid}
```

#### Revoke Invite Code
```bash
POST /group/revokeInviteCode/{instance}?groupJid={groupJid}
```

#### Send Invite URL
```bash
POST /group/sendInvite/{instance}

{
  "groupJid": "999999999@g.us",
  "description": "Join my WhatsApp group:",
  "numbers": ["5511999999999"]
}
```

#### Find Group by Invite Code
```bash
GET /group/inviteInfo/{instance}?inviteCode={inviteCode}
```

#### Find Group by JID
```bash
GET /group/findGroupInfos/{instance}?groupJid={groupJid}
```

#### Fetch All Groups
```bash
GET /group/fetchAllGroups/{instance}
# Optional: ?getParticipants=true
```

#### Find Participants
```bash
GET /group/participants/{instance}?groupJid={groupJid}
```

#### Update Participants
```bash
POST /group/updateParticipant/{instance}?groupJid={groupJid}

{
  "action": "add",
  "participants": ["5511999999999"]
}
```

**Actions:** `add`, `remove`, `promote`, `demote`

#### Update Group Settings
```bash
POST /group/updateSetting/{instance}?groupJid={groupJid}

{ "action": "announcement" }
```

**Actions:**  
- `announcement` - Only admins send messages  
- `not_announcement` - Everyone can send  
- `locked` - Only admins edit group info  
- `unlocked` - Everyone can edit group info

#### Toggle Ephemeral (Disappearing Messages)
```bash
POST /group/toggleEphemeral/{instance}?groupJid={groupJid}

{ "expiration": 86400 }
```

**Expiration values (seconds):**  
- `0` - Off  
- `86400` - 24 hours  
- `604800` - 7 days  
- `7776000` - 90 days

#### Leave Group
```bash
DELETE /group/leaveGroup/{instance}?groupJid={groupJid}
```

---

### Integrations - Events

#### Webhook
```bash
# Set Webhook
POST /webhook/set/{instance}

{
  "webhook": {
    "enabled": true,
    "url": "https://webhook.site/your-id",
    "headers": {
      "autorization": "Bearer TOKEN",
      "Content-Type": "application/json"
    },
    "byEvents": false,
    "base64": false,
    "events": [
      "APPLICATION_STARTUP",
      "QRCODE_UPDATED",
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "MESSAGES_DELETE",
      "SEND_MESSAGE",
      "CONTACTS_UPDATE",
      "PRESENCE_UPDATE",
      "CHATS_UPDATE",
      "CHATS_DELETE",
      "GROUPS_UPSERT",
      "GROUP_UPDATE",
      "GROUP_PARTICIPANTS_UPDATE",
      "CONNECTION_UPDATE",
      "LABELS_EDIT",
      "LABELS_ASSOCIATION",
      "CALL",
      "TYPEBOT_START",
      "TYPEBOT_CHANGE_STATUS"
    ]
  }
}

# Find Webhook
GET /webhook/find/{instance}
```

**Key options:**
- `byEvents` - If `true`, sends to separate URLs per event type
- `base64` - If `true`, media comes as base64 in payload

#### WebSocket
```bash
POST /websocket/set/{instance}

{
  "websocket": {
    "enabled": true,
    "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
  }
}

GET /websocket/find/{instance}
```

#### RabbitMQ
```bash
POST /rabbitmq/set/{instance}

{
  "rabbitmq": {
    "enabled": true,
    "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
  }
}

GET /rabbitmq/find/{instance}
```

#### SQS (Amazon)
```bash
POST /sqs/set/{instance}

{
  "sqs": {
    "enabled": true,
    "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
  }
}

GET /sqs/find/{instance}
```

#### NATS
```bash
POST /nats/set/{instance}
GET /nats/find/{instance}
```
Same payload structure as SQS/RabbitMQ.

#### Pusher
```bash
POST /pusher/set/{instance}
GET /pusher/find/{instance}
```
Same payload structure as SQS/RabbitMQ.

**Available Events (all transports):**
`APPLICATION_STARTUP`, `QRCODE_UPDATED`, `MESSAGES_SET`, `MESSAGES_UPSERT`, `MESSAGES_UPDATE`, `MESSAGES_DELETE`, `SEND_MESSAGE`, `CONTACTS_SET`, `CONTACTS_UPSERT`, `CONTACTS_UPDATE`, `PRESENCE_UPDATE`, `CHATS_SET`, `CHATS_UPSERT`, `CHATS_UPDATE`, `CHATS_DELETE`, `GROUPS_UPSERT`, `GROUP_UPDATE`, `GROUP_PARTICIPANTS_UPDATE`, `CONNECTION_UPDATE`, `LABELS_EDIT`, `LABELS_ASSOCIATION`, `CALL`, `TYPEBOT_START`, `TYPEBOT_CHANGE_STATUS`

---

### Integrations - Chatbots

All chatbot integrations share a common pattern with settings, session management, CRUD, and trigger configuration.

**Common trigger options (all chatbots):**
```json
{
  "triggerType": "keyword",
  "triggerOperator": "equals",
  "triggerValue": "hello",
  "expire": 20,
  "keywordFinish": "#SAIR",
  "delayMessage": 1000,
  "unknownMessage": "Message not recognized",
  "listeningFromMe": false,
  "stopBotFromMe": false,
  "keepOpen": false,
  "debounceTime": 10,
  "ignoreJids": []
}
```

| Field | Description |
|-------|-------------|
| `triggerType` | `all` (every message) or `keyword` (matched) |
| `triggerOperator` | `contains`, `equals`, `startsWith`, `endsWith`, `regex`, `none` |
| `triggerValue` | The keyword/pattern to match |
| `expire` | Session timeout (minutes) |
| `keywordFinish` | Keyword to end bot session |
| `delayMessage` | Delay between messages (ms) |
| `unknownMessage` | Response for unrecognized input |
| `listeningFromMe` | Process messages sent by you |
| `stopBotFromMe` | Pause bot when you send a message |
| `keepOpen` | Keep session alive after flow ends |
| `debounceTime` | Debounce interval (seconds) |
| `ignoreJids` | JIDs to ignore (e.g., `["@g.us"]` to ignore groups) |

#### Chatwoot
```bash
# Set Chatwoot
POST /chatwoot/set/{instance}

{
  "enabled": true,
  "accountId": "1",
  "token": "CHATWOOT_TOKEN",
  "url": "https://chatwoot.yourdomain.com",
  "signMsg": true,
  "reopenConversation": true,
  "conversationPending": false,
  "nameInbox": "evolution",
  "mergeBrazilContacts": true,
  "importContacts": true,
  "importMessages": true,
  "daysLimitImportMessages": 2,
  "signDelimiter": "\n",
  "autoCreate": true,
  "organization": "BOT",
  "logo": "https://example.com/logo.png",
  "ignoreJids": ["@g.us"]
}

# Find Chatwoot
GET /chatwoot/find/{instance}
```

#### Typebot
```bash
# Create Typebot
POST /typebot/create/{instance}

{
  "enabled": true,
  "url": "https://typebot.yourdomain.com",
  "typebot": "my-typebot-flow-id",
  "triggerType": "keyword",
  "triggerOperator": "regex",
  "triggerValue": "^atend.*",
  "expire": 20,
  "keywordFinish": "#SAIR",
  "delayMessage": 1000,
  "unknownMessage": "Message not recognized",
  "listeningFromMe": false,
  "stopBotFromMe": false,
  "keepOpen": false,
  "debounceTime": 10
}

# Find/Fetch/Update/Delete
GET  /typebot/find/{instance}
GET  /typebot/fetch/{typebotId}/{instance}
PUT  /typebot/update/{typebotId}/{instance}
DELETE /typebot/delete/{typebotId}/{instance}

# Start Typebot manually
POST /typebot/start/{instance}

{
  "url": "https://typebot.yourdomain.com",
  "typebot": "flow-id",
  "remoteJid": "5511999999999@s.whatsapp.net",
  "startSession": false,
  "variables": [
    { "name": "pushName", "value": "User Name" }
  ]
}

# Change session status
POST /typebot/changeStatus/{instance}
{ "remoteJid": "5511999999999@s.whatsapp.net", "status": "closed" }

# Fetch sessions
GET /typebot/fetchSessions/{typebotId}/{instance}

# Default settings
POST /typebot/settings/{instance}
GET  /typebot/fetchSettings/{instance}

{
  "expire": 20,
  "keywordFinish": "#SAIR",
  "delayMessage": 1000,
  "unknownMessage": "Not recognized",
  "listeningFromMe": false,
  "stopBotFromMe": false,
  "keepOpen": false,
  "debounceTime": 10,
  "ignoreJids": [],
  "typebotIdFallback": "fallback-typebot-id"
}
```

**Session statuses:** `opened`, `paused`, `closed`

#### OpenAI
```bash
# Set Credentials
POST /openai/creds/{instance}
{ "name": "apikey", "apiKey": "sk-proj-..." }

GET /openai/creds/{instance}
DELETE /openai/creds/{openaiCredsId}/{instance}

# Create Bot (Assistant or Chat Completion)
POST /openai/create/{instance}

{
  "enabled": true,
  "openaiCredsId": "creds-id",
  "botType": "assistant",
  // For assistants:
  "assistantId": "asst_XXXXX",
  "functionUrl": "https://n8n.site.com",
  // For chatCompletion:
  "model": "gpt-4o",
  "systemMessages": ["You are a helpful assistant."],
  "assistantMessages": ["Hello, how can I help?"],
  "userMessages": ["Hello!"],
  "maxTokens": 300,
  // Trigger options...
  "triggerType": "keyword",
  "triggerOperator": "equals",
  "triggerValue": "ai"
}

# Find/Fetch/Update/Delete
GET  /openai/find/{instance}
GET  /openai/fetch/{openaiBotId}/{instance}
PUT  /openai/update/{openaiBotId}/{instance}
DELETE /openai/delete/{openaiBotId}/{instance}

# Session management
POST /openai/changeStatus/{instance}
GET  /openai/fetchSessions/{openaiBotId}/{instance}

# Default settings
POST /openai/settings/{instance}
GET  /openai/fetchSettings/{instance}
```

**Bot types:** `assistant`, `chatCompletion`

#### Dify
```bash
POST /dify/create/{instance}

{
  "enabled": true,
  "botType": "chatBot",
  "apiUrl": "http://dify.site.com/v1",
  "apiKey": "app-123456",
  // Trigger options...
}

GET  /dify/find/{instance}
GET  /dify/fetch/{difyId}/{instance}
PUT  /dify/update/{difyId}/{instance}
DELETE /dify/delete/{difyId}/{instance}

POST /dify/changeStatus/{instance}
GET  /dify/fetchSessions/{difyId}/{instance}

POST /dify/settings/{instance}
GET  /dify/fetchSettings/{instance}
```

**Dify bot types:** `chatBot`, `textGenerator`, `agent`, `workflow`

#### Flowise
```bash
POST /flowise/create/{instance}

{
  "enabled": true,
  "apiUrl": "http://flowise.site.com/v1",
  "apiKey": "app-123456",
  // Trigger options...
}

GET  /flowise/find/{instance}
GET  /flowise/fetch/{flowiseId}/{instance}
PUT  /flowise/update/{flowiseId}/{instance}
DELETE /flowise/delete/{flowiseId}/{instance}

POST /flowise/changeStatus/{instance}
GET  /flowise/fetchSessions/{flowiseId}/{instance}

POST /flowise/settings/{instance}
GET  /flowise/fetchSettings/{instance}
```

#### N8N
```bash
POST /n8n/create/{instance}

{
  "enabled": true,
  "apiUrl": "http://n8n.site.com/v1",
  "apiKey": "app-123456",
  // Trigger options...
}

GET  /n8n/find/{instance}
GET  /n8n/fetch/{n8nId}/{instance}
PUT  /n8n/update/{n8nId}/{instance}
DELETE /n8n/delete/{n8nId}/{instance}

POST /n8n/changeStatus/{instance}
GET  /n8n/fetchSessions/{n8nId}/{instance}

POST /n8n/settings/{instance}
GET  /n8n/fetchSettings/{instance}
```

#### Evolution Bot
```bash
POST /evolutionBot/create/{instance}

{
  "enabled": true,
  "apiUrl": "http://api.site.com/v1",
  "apiKey": "app-123456",
  // Trigger options...
}

GET  /evolutionBot/find/{instance}
GET  /evolutionBot/fetch/{evolutionBotId}/{instance}
PUT  /evolutionBot/update/{evolutionBotId}/{instance}
DELETE /evolutionBot/delete/{evolutionBotId}/{instance}

POST /evolutionBot/changeStatus/{instance}
GET  /evolutionBot/fetchSessions/{evolutionBotId}/{instance}

POST /evolutionBot/settings/{instance}
GET  /evolutionBot/fetchSettings/{instance}
```

#### Evo AI
```bash
POST /evoai/create/{instance}

{
  "enabled": true,
  "apiUrl": "http://evoai.site.com/v1",
  "apiKey": "app-123456",
  // Trigger options...
}

GET  /evoai/find/{instance}
GET  /evoai/fetch/{evoaiId}/{instance}
PUT  /evoai/update/{evoaiId}/{instance}
DELETE /evoai/delete/{evoaiId}/{instance}

POST /evoai/changeStatus/{instance}
GET  /evoai/fetchSessions/{evoaiId}/{instance}

POST /evoai/settings/{instance}
GET  /evoai/fetchSettings/{instance}
```

---

### Integrations - Channel (WhatsApp Business Cloud API)

#### Send Template
```bash
POST /message/sendTemplate/{instance}

{
  "number": "5511999999999",
  "name": "hello_world",
  "language": "en_US",
  "components": [
    {
      "type": "body",
      "parameters": [
        { "type": "text", "text": "John" },
        { "type": "text", "text": "email@email.com" }
      ]
    },
    {
      "type": "button",
      "sub_type": "URL",
      "index": "1",
      "parameters": [
        { "type": "text", "text": "/reset-password/1234" }
      ]
    }
  ]
}
```

#### Create Template
```bash
POST /template/create/{instance}

{
  "name": "my_template",
  "category": "MARKETING",
  "allowCategoryChange": false,
  "language": "en_US",
  "components": [
    {
      "type": "BODY",
      "text": "Thank you {{1}}! Confirmation: {{2}}",
      "example": {
        "body_text": [["John", "860198-230332"]]
      }
    },
    {
      "type": "BUTTONS",
      "buttons": [
        { "type": "QUICK_REPLY", "text": "Unsubscribe" },
        { "type": "URL", "text": "Support", "url": "https://example.com" }
      ]
    }
  ]
}
```

**Categories:** `AUTHENTICATION`, `MARKETING`, `UTILITY`

#### Find Templates
```bash
GET /template/find/{instance}
```

#### Evolution Channel Webhook
```bash
POST /webhook/evolution

{
  "numberId": "5511999999999",
  "key": {
    "remoteJid": "5511888888888",
    "fromMe": false,
    "id": "ABC1234"
  },
  "pushName": "Contact Name",
  "message": {
    "conversation": "Hello"
  },
  "messageType": "conversation"
}
```

**Message types:** `conversation`, `imageMessage`, `videoMessage`, `documentMessage`, `audioMessage`

---

### Storage (S3/MinIO)

#### Get Media
```bash
POST /s3/getMedia/{instance}

{
  "id": "media-id",
  "type": "image",
  "messageId": "MESSAGE_ID"
}
```

#### Get Media URL
```bash
POST /s3/getMediaUrl/{instance}

{
  "id": "media-id"
}
```

---

### System

#### Get API Information
```bash
GET /
```

Returns API version and system info.

#### Metrics
```bash
GET /metrics
Authorization: Basic (METRICS_USER:password)
```

---

## Common Workflows

### Broadcast Message
```bash
for number in 5511999999999 5511888888888 5511777777777; do
  curl -X POST "$EVO_API_URL/message/sendText/$EVO_INSTANCE" \
    -H "apikey: $EVO_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"number\": \"$number\",
      \"text\": \"Broadcast message!\",
      \"delay\": 2000
    }"
done
```

### Auto-Create Group + Configure Bot
```bash
# 1. Create group
curl -X POST "$EVO_API_URL/group/create/$EVO_INSTANCE" \
  -H "apikey: $EVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Support Group",
    "participants": ["5511999999999"]
  }'

# 2. Attach Typebot for auto-response
curl -X POST "$EVO_API_URL/typebot/create/$EVO_INSTANCE" \
  -H "apikey: $EVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "url": "https://typebot.yourdomain.com",
    "typebot": "support-flow-id",
    "triggerType": "all"
  }'
```

### Full Instance Setup (Instance + Webhook + Chatwoot)
```bash
# 1. Create instance with webhook inline
curl -X POST "$EVO_API_URL/instance/create" \
  -H "apikey: $EVO_GLOBAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "support-bot",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS",
    "webhook": {
      "url": "https://n8n.yourdomain.com/webhook/evo",
      "byEvents": false,
      "base64": false,
      "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]
    }
  }'

# 2. Connect
curl -X GET "$EVO_API_URL/instance/connect/support-bot" \
  -H "apikey: $EVO_API_KEY"

# 3. Configure Chatwoot
curl -X POST "$EVO_API_URL/chatwoot/set/support-bot" \
  -H "apikey: $EVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "accountId": "1",
    "token": "CHATWOOT_TOKEN",
    "url": "https://chatwoot.yourdomain.com",
    "signMsg": true,
    "importContacts": true,
    "importMessages": true,
    "autoCreate": true,
    "nameInbox": "support-bot"
  }'
```

### Check Numbers Before Sending
```bash
# 1. Validate numbers
curl -X POST "$EVO_API_URL/chat/whatsappNumbers/$EVO_INSTANCE" \
  -H "apikey: $EVO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "numbers": ["5511999999999", "5511888888888"] }'

# 2. Send only to valid numbers
```

---

## Rate Limits & Best Practices

### Delays
Always add delays between messages:
```json
{ "delay": 1200 }
```

**Recommended:**
- 1-2 seconds between individual messages
- 3-5 seconds between mass sends
- Exponential backoff on errors

### Error Handling

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad request (check body/params) |
| `401` | Unauthorized (check API key) |
| `404` | Not found (instance/resource) |
| `500` | Server error |

### Common Issues

| Error | Solution |
|-------|----------|
| Instance not connected | Run `GET /instance/connect/{instance}` |
| Invalid phone format | Use country code without `+`: `5511999999999` |
| Message not sent | Check `GET /instance/connectionState/{instance}` |
| Group operation failed | Verify you're admin |
| Media extraction fails | Ensure MongoDB/file storage is enabled |
| Chatwoot not syncing | Check token and URL, verify `importMessages` is true |

---

## Troubleshooting

### Instance Won't Connect
```bash
# 1. Check instances
GET /instance/fetchInstances

# 2. Restart instance
POST /instance/restart/{instance}

# 3. Reconnect
GET /instance/connect/{instance}
```

### Chatbot Not Responding
1. Check bot is enabled: `GET /{botType}/find/{instance}`
2. Check trigger matches incoming message
3. Check session status: `GET /{botType}/fetchSessions/{botId}/{instance}`
4. Reset session: `POST /{botType}/changeStatus/{instance}` with `status: "closed"`

### Messages Not Being Delivered
1. Verify connection: `GET /instance/connectionState/{instance}`
2. Check phone format (no `+`, no spaces)
3. Verify recipient has WhatsApp: `POST /chat/whatsappNumbers/{instance}`
4. Check webhook for delivery status events

---

## v2 vs v3 (Evolution Go) Differences

| Feature | v2.3 | v3 (Go) |
|---------|------|---------|
| **Language** | Node.js/TypeScript | Go |
| **Endpoints** | `/message/sendText/{instance}` | `/send/text` |
| **Chatbot integrations** | 7 (Typebot, OpenAI, Dify, Flowise, N8N, EvolutionBot, EvoAI) | Fewer built-in |
| **Chatwoot** | Native integration | Separate |
| **Event transports** | 6 (Webhook, WS, RabbitMQ, SQS, NATS, Pusher) | Fewer |
| **Lists/Buttons** | Supported | Deprecated |
| **PTV (Round Video)** | Supported | Supported |
| **Status/Stories** | Supported | Supported |
| **Templates** | Business Cloud API | Business Cloud API |
| **S3 Storage** | Built-in | Separate |

---

## Resources

- **Evolution API:** https://github.com/EvolutionAPI/evolution-api
- **Documentation:** https://doc.evolution-api.com
- **Chatwoot:** https://www.chatwoot.com
- **Typebot:** https://typebot.io
- **WhatsApp Business API:** https://developers.facebook.com/docs/whatsapp

---

## Tips

1. **Always check connection** before operations
2. **Use delays** to avoid rate limits (1.2s+ between messages)
3. **Store keys** in environment variables, never hardcode
4. **Handle disconnects** with webhook `CONNECTION_UPDATE` event
5. **Validate numbers** with `whatsappNumbers` before bulk sends
6. **Use `debounceTime`** in chatbots to group fast messages
7. **Set `ignoreJids: ["@g.us"]`** in chatbots to ignore group messages
8. **Test triggers** with `triggerType: "keyword"` before switching to `"all"`
9. **Monitor sessions** - expired sessions stop chatbot responses
10. **Use Chatwoot** for human handoff from chatbot flows
