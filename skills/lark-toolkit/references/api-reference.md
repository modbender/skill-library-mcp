# Lark API Reference

API base: `https://open.larksuite.com/open-apis/` (international) or `https://open.feishu.cn/open-apis/` (China)

## Authentication

```bash
# tenant_access_token (app-level, ~2h validity)
POST /auth/v3/tenant_access_token/internal
{"app_id":"cli_xxx","app_secret":"xxx"}
# Response: {"tenant_access_token":"t-xxx","expire":7200}

# All subsequent requests:
-H "Authorization: Bearer $TOKEN"
```

## Messages (IM)

### Send Message
```
POST /im/v1/messages?receive_id_type={chat_id|open_id|user_id|union_id|email}
{
  "receive_id": "TARGET_ID",
  "msg_type": "text|post|image|interactive|file|audio|media|sticker",
  "content": "<JSON string>"
}
```

**Content formats by msg_type:**

| Type | Content JSON |
|------|-------------|
| `text` | `{"text":"hello @user"}` |
| `post` | `{"title":"Title","content":[[{"tag":"text","text":"body"}]]}` |
| `image` | `{"image_key":"img_xxx"}` |
| `file` | `{"file_key":"file_xxx","file_name":"doc.pdf"}` |
| `interactive` | Card JSON (see below) |

### Reply in Thread
```
POST /im/v1/messages/{message_id}/reply
{
  "msg_type": "text",
  "content": "{\"text\":\"reply\"}",
  "reply_in_thread": true
}
```

### Get History
```
GET /im/v1/messages?container_id_type=chat&container_id=CHAT_ID&page_size=20&sort_type=ByCreateTimeDesc
```

### Get Message Resource (image/file download)
```
GET /im/v1/messages/{message_id}/resources/{file_key}?type={image|file}
```

### Forward Message
```
POST /im/v1/messages/{message_id}/forward?receive_id_type=chat_id
{"receive_id":"TARGET_CHAT_ID"}
```

## Reactions

```
# Add
POST /im/v1/messages/{message_id}/reactions
{"reaction_type":{"emoji_type":"THUMBSUP"}}

# List
GET /im/v1/messages/{message_id}/reactions

# Delete
DELETE /im/v1/messages/{message_id}/reactions/{reaction_id}
```

Valid emoji types: `THUMBSUP` `HEART` `LAUGH` `OK` `COOL` `FINGERHEART` `SMILE` `JIAYOU` `Get` `Salute` `Fireworks`

## Groups (Chat)

```
# List bot's groups
GET /im/v1/chats?page_size=100

# Get group info
GET /im/v1/chats/{chat_id}

# List members
GET /im/v1/chats/{chat_id}/members

# Add members
POST /im/v1/chats/{chat_id}/members?member_id_type=open_id
{"id_list":["ou_xxx"]}

# Create group
POST /im/v1/chats
{"name":"Group Name","chat_mode":"group"}
```

## Calendar

```
# Get primary calendar
GET /calendar/v4/calendars/primary

# Create event
POST /calendar/v4/calendars/{calendar_id}/events
{
  "summary": "Meeting",
  "start_time": {"timestamp": "1640000000"},
  "end_time": {"timestamp": "1640003600"}
}

# Free/busy query
POST /calendar/v4/freebusy/list
{"time_min":"2024-01-01T00:00:00+08:00","time_max":"2024-01-02T00:00:00+08:00","user_id":"ou_xxx"}
```

## Docs

```
# Get document content (raw)
GET /docx/v1/documents/{document_id}/raw_content

# Search documents
POST /suite/docs-api/search/object
{"search_key":"keyword","count":20,"docs_types":[2,7,8,12,15,16]}
```

## Contacts

```
# Batch get user ID by email/phone
POST /contact/v3/users/batch_get_id
{"emails":["user@example.com"],"mobiles":["+1234567890"]}
```

## Bot Info

```
GET /bot/v3/info
# Returns: bot open_id, app_name, avatar_url
```

## Interactive Cards

Minimal card template:
```json
{
  "header": {
    "title": {"tag": "plain_text", "content": "Card Title"},
    "template": "blue"
  },
  "elements": [
    {"tag": "div", "text": {"tag": "lark_md", "content": "**Markdown** content here"}}
  ]
}
```

Templates: `blue` `wathet` `turquoise` `green` `yellow` `orange` `red` `carmine` `violet` `purple` `indigo` `grey`

## Response Format

All API responses:
```json
{"code": 0, "msg": "success", "data": {...}}
```

`code: 0` = success. Non-zero = error. Always check `code`.

## Upload Media

```bash
# Upload image
POST /im/v1/images
Content-Type: multipart/form-data
image_type=message_type, image=@file.png
# Returns: {"image_key":"img_xxx"}

# Upload file
POST /im/v1/files
Content-Type: multipart/form-data
file_type=opus|mp4|pdf|doc|xls|ppt|stream, file=@file.pdf, file_name=doc.pdf
# Returns: {"file_key":"file_xxx"}
```

## Rate Limits

- Most APIs: 100 req/s per app
- Message send: 5 msg/s per chat for bots
- Token refresh: cache it, don't fetch every request
