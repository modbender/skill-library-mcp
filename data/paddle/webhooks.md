# Webhooks — Paddle

## Webhook Setup

1. Go to Paddle Dashboard → Developer Tools → Notifications
2. Create a new destination with your endpoint URL
3. Select events to receive
4. Copy the webhook secret for verification

## Essential Events

### Subscription Lifecycle

| Event | When | Action |
|-------|------|--------|
| `subscription.created` | New subscription starts | Create subscription record, grant access |
| `subscription.updated` | Plan change, renewal | Update subscription details |
| `subscription.activated` | Trial converts or first payment succeeds | Confirm access granted |
| `subscription.paused` | User paused subscription | Restrict access, track pause date |
| `subscription.resumed` | User resumed subscription | Restore access |
| `subscription.canceled` | Subscription ended | Schedule access revocation |
| `subscription.past_due` | Payment failed, retry period | Warn user, show payment update UI |

### Transaction Events

| Event | When | Action |
|-------|------|--------|
| `transaction.completed` | Successful payment | Record payment, send receipt |
| `transaction.payment_failed` | Payment declined | Log failure, wait for retry |

## Signature Verification

**CRITICAL:** Always verify webhook signatures before processing.

### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhook(rawBody, signature, secret) {
  const ts = signature.split(';').find(p => p.startsWith('ts=')).split('=')[1];
  const h1 = signature.split(';').find(p => p.startsWith('h1=')).split('=')[1];
  
  const signedPayload = `${ts}:${rawBody}`;
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(h1),
    Buffer.from(expectedSig)
  );
}

// In your webhook handler
app.post('/webhooks/paddle', express.raw({ type: 'application/json' }), (req, res) => {
  const signature = req.headers['paddle-signature'];
  
  if (!verifyWebhook(req.body, signature, process.env.PADDLE_WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }
  
  const event = JSON.parse(req.body);
  // Process event...
  
  res.status(200).send('OK');
});
```

### Python Example

```python
import hmac
import hashlib

def verify_webhook(raw_body: bytes, signature: str, secret: str) -> bool:
    parts = dict(p.split('=') for p in signature.split(';'))
    ts = parts['ts']
    h1 = parts['h1']
    
    signed_payload = f"{ts}:{raw_body.decode()}"
    expected_sig = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(h1, expected_sig)

# In your webhook handler
@app.post("/webhooks/paddle")
async def paddle_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("paddle-signature")
    
    if not verify_webhook(raw_body, signature, os.environ["PADDLE_WEBHOOK_SECRET"]):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    event = json.loads(raw_body)
    # Process event...
    
    return {"status": "ok"}
```

## Event Payload Structure

```json
{
  "event_id": "evt_xxx",
  "event_type": "subscription.created",
  "occurred_at": "2024-01-15T10:30:00Z",
  "notification_id": "ntf_xxx",
  "data": {
    "id": "sub_xxx",
    "status": "active",
    "customer_id": "ctm_xxx",
    "items": [
      {
        "price": {
          "id": "pri_xxx",
          "product_id": "pro_xxx"
        },
        "quantity": 1
      }
    ],
    "billing_cycle": {
      "interval": "month",
      "frequency": 1
    },
    "current_billing_period": {
      "starts_at": "2024-01-15T00:00:00Z",
      "ends_at": "2024-02-15T00:00:00Z"
    },
    "custom_data": {
      "user_id": "your_internal_user_id"
    }
  }
}
```

## Idempotency

Webhooks may be delivered multiple times. Use `event_id` for idempotency:

```javascript
// Check if already processed
const existing = await db.processedEvents.findUnique({
  where: { eventId: event.event_id }
});

if (existing) {
  return res.status(200).send('Already processed');
}

// Process event...

// Mark as processed
await db.processedEvents.create({
  data: { eventId: event.event_id, processedAt: new Date() }
});
```

## Testing Webhooks

### Paddle CLI (Recommended)

```bash
# Install Paddle CLI
npm install -g @paddle/paddle-cli

# Forward webhooks to localhost
paddle webhooks listen --forward-to http://localhost:3000/webhooks/paddle
```

### Manual Testing

Use the "Resend" feature in Paddle Dashboard → Developer Tools → Notifications → Events tab.
