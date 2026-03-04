# Zulip API Quick Reference

## Core Concepts

- **Streams** - Public or private channels (like Discord channels or Slack channels)
- **Topics** - Conversation threads within streams
- **Messages** - Individual messages within topics
- **Direct Messages (DM)** - Private 1-on-1 or group conversations

## Authentication

HTTP Basic Auth: `bot-email:api-key`

```bash
curl -u "bot@example.zulipchat.com:API_KEY" https://example.zulipchat.com/api/v1/...
```

## Common Endpoints

### List Streams

```bash
GET /api/v1/streams
```

Response: Array of streams with metadata (name, ID, description, subscriber count)

### Get Messages

```bash
GET /api/v1/messages?anchor=newest&num_before=20&num_after=0&narrow=[...]
```

**Narrow filters (JSON array):**
- Stream: `[{"operator":"stream","operand":"General"}]`
- Topic: `[{"operator":"topic","operand":"Bug fixes"}]`
- Private: `[{"operator":"is","operand":"private"}]`
- Mentioned: `[{"operator":"is","operand":"mentioned"}]`
- Search: `[{"operator":"search","operand":"keyword"}]`

### Send Message

```bash
POST /api/v1/messages
```

**Stream message:**
```json
{
  "type": "stream",
  "to": "General",
  "topic": "Updates",
  "content": "Message text"
}
```

**Private message:**
```json
{
  "type": "private",
  "to": [user_id1, user_id2],
  "content": "Private message"
}
```

### List Users

```bash
GET /api/v1/users
```

Response: Array of users with user_id, full_name, email

### Upload File

```bash
POST /api/v1/user_uploads
```

Returns file URL that can be embedded in messages:
```markdown
[filename](uploaded_file_url)
```

## Message Formatting

Zulip uses Markdown:

```markdown
**bold** *italic* ~~strikethrough~~
[link](url)
`code` ```code block```
> quote
- list
1. numbered list
@**username** - mention user
#**stream-name** - link to stream
```

## Rate Limits

- Standard: 200 requests/minute
- Messages: ~20-30/minute
- Respect `Retry-After` header on 429 responses

## Python Client Example

```python
import zulip

client = zulip.Client(config_file="~/.config/zulip/zuliprc")

# Get messages
result = client.get_messages({
    "anchor": "newest",
    "num_before": 10,
    "num_after": 0,
    "narrow": [{"operator": "stream", "operand": "General"}]
})

# Send message
result = client.send_message({
    "type": "stream",
    "to": "General",
    "topic": "Updates",
    "content": "Hello!"
})

# List users
result = client.get_members()
```

## Common Workflows

### Read latest messages from stream
```bash
curl -u "bot@example.com:KEY" -G \
  "https://example.zulipchat.com/api/v1/messages" \
  --data-urlencode 'anchor=newest' \
  --data-urlencode 'num_before=20' \
  --data-urlencode 'num_after=0' \
  --data-urlencode 'narrow=[{"operator":"stream","operand":"General"}]'
```

### Send DM to user
```bash
curl -X POST "https://example.zulipchat.com/api/v1/messages" \
  -u "bot@example.com:KEY" \
  --data-urlencode 'type=private' \
  --data-urlencode 'to=[123]' \
  --data-urlencode 'content=Hello!'
```

### Reply in topic
```bash
curl -X POST "https://example.zulipchat.com/api/v1/messages" \
  -u "bot@example.com:KEY" \
  --data-urlencode 'type=stream' \
  --data-urlencode 'to=General' \
  --data-urlencode 'topic=Discussion' \
  --data-urlencode 'content=My reply'
```
