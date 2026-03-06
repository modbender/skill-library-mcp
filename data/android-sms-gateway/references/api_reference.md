# SMS Gateway API Reference

Detailed API documentation for supported Android SMS Gateway apps.

---

## SMS Gateway API (itsmeichigo/SMSGateway) ⭐ Recommended

**GitHub:** https://github.com/itsmeichigo/SMSGateway

**Download:** https://github.com/itsmeichigo/SMSGateway/releases

### Base URL

```
http://<PHONE_IP>:8080/api/v1
```

### Authentication

```http
Authorization: Bearer <YOUR_API_TOKEN>
```

Set API token in app settings → Security → API Token

---

### Endpoints

#### GET /status

Check gateway health and status.

**Request:**
```bash
curl http://PHONE_IP:8080/api/v1/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "status": "online",
  "phone_number": "+1234567890",
  "signal_strength": 4,
  "battery_level": 85,
  "pending_messages": 0,
  "app_version": "2.1.0"
}
```

---

#### POST /send

Send an SMS message.

**Request:**
```bash
curl -X POST http://PHONE_IP:8080/api/v1/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "message": "Hello from OpenClaw",
    "sim": 1
  }'
```

**Body Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone | string | Yes | Recipient number (with country code) |
| message | string | Yes | Message content |
| sim | integer | No | SIM slot (1 or 2, for dual SIM) |

**Response:**
```json
{
  "success": true,
  "message_id": "msg_abc123",
  "status": "queued",
  "timestamp": "2026-02-22T09:00:00Z"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Invalid phone number format",
  "code": "INVALID_PHONE"
}
```

---

#### GET /messages/received

Fetch received SMS messages.

**Request:**
```bash
curl -X GET "http://PHONE_IP:8080/api/v1/messages/received?limit=10&since=2026-02-22T00:00:00Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | integer | 10 | Max messages to return |
| since | string | - | ISO 8601 timestamp |
| offset | integer | 0 | Pagination offset |

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_xyz789",
      "from": "+0987654321",
      "message": "Reply message",
      "received_at": "2026-02-22T08:30:00Z",
      "sim": 1,
      "read": false
    }
  ],
  "total": 1,
  "has_more": false
}
```

---

#### GET /messages/sent

Fetch sent SMS history.

**Request:**
```bash
curl -X GET "http://PHONE_IP:8080/api/v1/messages/sent?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_abc123",
      "to": "+1234567890",
      "message": "Hello",
      "sent_at": "2026-02-22T09:00:00Z",
      "status": "delivered",
      "delivered_at": "2026-02-22T09:00:05Z"
    }
  ]
}
```

---

#### DELETE /messages/:id

Delete a message from history.

**Request:**
```bash
curl -X DELETE http://PHONE_IP:8080/api/v1/messages/msg_abc123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Webhooks (Delivery Reports)

Configure webhook URL in app settings for delivery callbacks.

**Webhook Payload:**
```json
{
  "event": "message.delivered",
  "message_id": "msg_abc123",
  "phone": "+1234567890",
  "status": "delivered",
  "timestamp": "2026-02-22T09:00:05Z"
}
```

**Event Types:**
- `message.queued` - Message queued for sending
- `message.sent` - Message sent from phone
- `message.delivered` - Message delivered to recipient
- `message.failed` - Message failed to send

---

## SMSGate

**GitHub:** https://github.com/iamsmgate/smsgate

### Base URL

```
http://<PHONE_IP>:8080
```

### Authentication

```http
X-API-Key: <YOUR_API_KEY>
```

### Endpoints

#### POST /sms/send

```bash
curl -X POST http://PHONE_IP:8080/sms/send \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890",
    "body": "Message text"
  }'
```

**Response:**
```json
{
  "success": true,
  "messageId": "12345"
}
```

#### GET /sms/inbox

```bash
curl -X GET "http://PHONE_IP:8080/sms/inbox?limit=10" \
  -H "X-API-Key: YOUR_KEY"
```

---

## SMS Forwarder

**GitHub:** https://github.com/pppscn/SmsForwarder

### Base URL

```
http://<PHONE_IP>:<PORT>
```

### Authentication

```http
Authorization: Basic <base64(user:pass)>
```

### Endpoints

#### POST /api/v1/send

```bash
curl -X POST http://PHONE_IP:PORT/api/v1/send \
  -H "Authorization: Basic BASE64_CREDENTIALS" \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+1234567890",
    "content": "Message text"
  }'
```

---

## Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| 401 | Unauthorized | Check API token/key |
| 400 | Invalid phone format | Use international format (+CountryCode) |
| 403 | Permission denied | Enable SMS permissions in app |
| 408 | Request timeout | Check network connectivity |
| 500 | Internal error | Restart gateway app |
| 503 | Service unavailable | Phone may be offline |

---

## Best Practices

### Phone Number Format

Always use international E.164 format:
- ✅ `+1234567890`
- ✅ `+447911123456`
- ❌ `07911123456`
- ❌ `(123) 456-7890`

### Rate Limiting

- Max ~1 SMS/second to avoid carrier flags
- Implement exponential backoff on failures
- Batch sends with 1-2 second delays

### Message Length

- GSM 7-bit: 160 chars per SMS
- Unicode (emoji, special chars): 70 chars per SMS
- Longer messages auto-split (concatenated SMS)

### Security

1. **Network isolation:** Keep gateway on LAN
2. **Strong tokens:** 32+ character random strings
3. **HTTPS:** Use reverse proxy if exposing externally
4. **Firewall:** Restrict access to gateway port
5. **Monitoring:** Log all API requests

---

## Troubleshooting

### Connection Refused

```bash
# Check phone is reachable
ping PHONE_IP

# Check app is running
# On phone: Open SMS Gateway app, verify server started

# Check port
nmap -p 8080 PHONE_IP
```

### Authentication Failed

```bash
# Verify token matches app settings
curl -v http://PHONE_IP:8080/api/v1/status \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check for typos, trailing spaces
```

### Message Not Delivered

1. Check phone has signal
2. Verify SMS plan/credit
3. Check app logs for errors
4. Verify recipient number format
5. Check carrier spam filters

---

## Alternative Apps

If the recommended app doesn't work for your device, try:

| App | GitHub | Notes |
|-----|--------|-------|
| SMS Gateway API | itsmeichigo/SMSGateway | ⭐ Recommended, active |
| SMSGate | iamsmgate/smsgate | Good alternative |
| SMS Forwarder | pppscn/SmsForwarder | Focus on forwarding |
| KDE Connect | KDE/kdeconnect-android | Limited SMS support |
