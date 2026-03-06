# Dooray Incoming Webhook API Reference

## Overview

Dooray provides incoming webhooks for sending messages to chat rooms programmatically. Each webhook is unique to a specific chat room.

## Getting a Webhook URL

1. Open the target Dooray chat room
2. Go to **Settings** → **Integrations** → **Incoming Webhook**
3. Enable incoming webhook
4. Copy the generated webhook URL

The URL format is:
```
https://hook.dooray.com/services/{TOKEN}
```

## HTTP Request

**Method:** POST  
**URL:** `https://hook.dooray.com/services/{TOKEN}`  
**Content-Type:** `application/json`

## Request Body

### Required Fields

```json
{
  "text": "Your message here"
}
```

### Optional Fields

```json
{
  "botName": "MyBot",
  "botIconImage": "https://static.dooray.com/static_images/dooray-bot.png",
  "text": "Dooray!"
}
```

#### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | Yes | Message content (plain text only) |
| `botName` | string | No | Display name for the bot sender |
| `botIconImage` | string | No | Avatar image URL for the bot |

## Response

### Success Response

**HTTP Status:** 200 OK

```json
{
  "success": true
}
```

### Error Responses

**HTTP Status:** 400 Bad Request
- Invalid JSON payload
- Missing required fields

**HTTP Status:** 404 Not Found
- Invalid webhook token
- Webhook has been deleted

**HTTP Status:** 429 Too Many Requests
- Rate limit exceeded

## Limitations

### Content Limitations

- **Markdown:** Not supported
- **Text Length:** Maximum 4000 characters (recommended)
- **Formatting:** Plain text only
- **Mentions:** Not supported via webhook

### Rate Limits

- Recommended: Max 10 messages per minute per webhook
- Excessive requests may be throttled or blocked

### Security

- Webhook URLs should be treated as secrets
- Anyone with the URL can post to the room
- No authentication required (URL itself is the credential)
- Regenerate webhook if URL is compromised

## Example Requests

### cURL Example

```bash
curl -X POST https://hook.dooray.com/services/YOUR_TOKEN \
  -H "Content-Type: application/json" \
  -d '{
    "botName": "DeployBot",
    "botIconImage": "https://example.com/bot-icon.png",
    "text": "Deployment to production completed successfully ✅"
  }'
```

### Python (urllib) Example

```python
import urllib.request
import json

webhook_url = "https://hook.dooray.com/services/YOUR_TOKEN"
payload = {
    "botName": "AlertBot",
    "text": "Server CPU usage is high!"
}

req = urllib.request.Request(
    webhook_url,
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as response:
    print(response.read().decode('utf-8'))
```

### JavaScript (fetch) Example

```javascript
const webhookUrl = 'https://hook.dooray.com/services/YOUR_TOKEN';
const payload = {
  botName: 'StatusBot',
  text: 'All systems operational 🟢'
};

fetch(webhookUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Best Practices

### Message Design

1. **Keep messages concise** - Aim for clarity over verbosity
2. **Use emoji sparingly** - ✅ ❌ 🟢 for status indicators
3. **Include context** - Avoid ambiguous messages
4. **Structure information** - Use line breaks for readability

### Error Handling

1. **Retry on failure** - Implement exponential backoff
2. **Log failures** - Track webhook delivery issues
3. **Validate URLs** - Check webhook format before sending
4. **Handle rate limits** - Queue messages if needed

### Security

1. **Store URLs securely** - Never commit webhooks to version control
2. **Use environment variables** - Keep tokens out of code
3. **Rotate webhooks** - Regenerate if exposed or periodically
4. **Limit access** - Only share webhooks with authorized systems

## Troubleshooting

### Message Not Appearing

- Verify webhook URL is correct
- Check that webhook is still enabled in Dooray
- Ensure JSON payload is valid
- Confirm room still exists

### 404 Error

- Webhook may have been deleted/regenerated
- Token in URL is invalid
- Room was archived or deleted

### Rate Limiting

- Reduce message frequency
- Implement message batching
- Add delays between requests

## Official Documentation

For the latest official Dooray webhook documentation (Korean):
https://helpdesk.dooray.com/

## Change Log

- **2024-02-10**: Initial API reference for OpenClaw skill
