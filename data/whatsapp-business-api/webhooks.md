# Webhooks — WhatsApp Business API

Webhooks notify your server of incoming messages, status updates, and other events.

## Setup Webhook

### 1. Configure in Meta App Dashboard

1. Go to your app in developers.facebook.com
2. WhatsApp → Configuration
3. Add webhook URL and verify token

### 2. Handle Verification

Meta sends GET request to verify your endpoint:

```
GET /webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=CHALLENGE_STRING
```

Your server must:
1. Verify `hub.verify_token` matches your token
2. Return `hub.challenge` as plain text

```javascript
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === process.env.VERIFY_TOKEN) {
    res.status(200).send(challenge);
  } else {
    res.sendStatus(403);
  }
});
```

### 3. Subscribe to Events

Select webhook fields in App Dashboard:
- `messages` — Incoming messages
- `message_template_status_update` — Template status changes
- `account_update` — Business account changes

---

## Verify Webhook Signature

**Always verify the signature to prevent fake events.**

Signature is in `X-Hub-Signature-256` header.

```javascript
const crypto = require('crypto');

function verifySignature(req) {
  const signature = req.headers['x-hub-signature-256'];
  const body = JSON.stringify(req.body);
  
  const expectedSignature = 'sha256=' + 
    crypto.createHmac('sha256', process.env.APP_SECRET)
      .update(body)
      .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}
```

```python
import hmac
import hashlib

def verify_signature(payload, signature, app_secret):
    expected = 'sha256=' + hmac.new(
        app_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

## Webhook Payload Structure

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "1234567890",
              "phone_number_id": "PHONE_NUMBER_ID"
            },
            "contacts": [...],
            "messages": [...],
            "statuses": [...]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

---

## Message Events

### Text Message

```json
{
  "messages": [
    {
      "from": "1234567890",
      "id": "wamid.xxxxx",
      "timestamp": "1234567890",
      "type": "text",
      "text": {
        "body": "Hello!"
      }
    }
  ],
  "contacts": [
    {
      "profile": {"name": "John Doe"},
      "wa_id": "1234567890"
    }
  ]
}
```

### Image Message

```json
{
  "messages": [
    {
      "from": "1234567890",
      "id": "wamid.xxxxx",
      "timestamp": "1234567890",
      "type": "image",
      "image": {
        "caption": "Check this out",
        "mime_type": "image/jpeg",
        "sha256": "abc123...",
        "id": "MEDIA_ID"
      }
    }
  ]
}
```

### Button Reply

```json
{
  "messages": [
    {
      "from": "1234567890",
      "id": "wamid.xxxxx",
      "timestamp": "1234567890",
      "type": "interactive",
      "interactive": {
        "type": "button_reply",
        "button_reply": {
          "id": "confirm",
          "title": "✅ Confirm"
        }
      }
    }
  ]
}
```

### List Reply

```json
{
  "messages": [
    {
      "from": "1234567890",
      "id": "wamid.xxxxx",
      "timestamp": "1234567890",
      "type": "interactive",
      "interactive": {
        "type": "list_reply",
        "list_reply": {
          "id": "pizza",
          "title": "🍕 Pizza",
          "description": "$12.99"
        }
      }
    }
  ]
}
```

### Location Shared

```json
{
  "messages": [
    {
      "from": "1234567890",
      "id": "wamid.xxxxx",
      "timestamp": "1234567890",
      "type": "location",
      "location": {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "name": "Home",
        "address": "123 Main St"
      }
    }
  ]
}
```

---

## Status Updates

Track message delivery:

```json
{
  "statuses": [
    {
      "id": "wamid.xxxxx",
      "status": "delivered",
      "timestamp": "1234567890",
      "recipient_id": "1234567890"
    }
  ]
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `sent` | Message sent to WhatsApp servers |
| `delivered` | Delivered to recipient's device |
| `read` | Recipient opened the message |
| `failed` | Delivery failed (see errors) |

### Failed Status

```json
{
  "statuses": [
    {
      "id": "wamid.xxxxx",
      "status": "failed",
      "timestamp": "1234567890",
      "recipient_id": "1234567890",
      "errors": [
        {
          "code": 131047,
          "title": "Re-engagement message",
          "message": "More than 24 hours have passed..."
        }
      ]
    }
  ]
}
```

---

## Best Practices

1. **Respond with 200 immediately** — Process asynchronously
2. **Deduplicate by message ID** — Webhooks may retry
3. **Store message IDs** — For reply threading
4. **Download media fast** — URLs expire
5. **Log failed deliveries** — Monitor error patterns
6. **Handle unknown types gracefully** — Meta adds new types

---

## Webhook Retry Behavior

If your server doesn't return 200:
- Retries for up to 24 hours
- Exponential backoff
- After 24h, message is dropped

**Always return 200 fast, then process.**
