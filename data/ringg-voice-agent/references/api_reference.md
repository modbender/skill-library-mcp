# Ringg AI API Reference

Base URL: `https://api.ringg.ai/v1`

Authentication: Bearer token via `Authorization: Bearer <RINGG_API_KEY>` header.

---

## Workspace

### Get Workspace Info
```
GET /workspace
```
Returns workspace details including ID, name, plan, and usage.

---

## Assistants

### List Assistants
```
GET /assistants
```
Returns all voice assistants in the workspace.

**Response:**
```json
{
  "assistants": [
    {
      "id": "asst_abc123",
      "name": "PolicyBazaar Health",
      "language": "en-hi",
      "status": "active",
      "created_at": "2026-01-15T10:00:00Z"
    }
  ]
}
```

### Get Assistant Details
```
GET /assistants/{assistant_id}
```

### Create Assistant
```
POST /assistants
```
**Body:**
```json
{
  "name": "My Voice Agent",
  "language": "en",
  "prompt": "You are a helpful customer service agent for...",
  "voice": "female-1",
  "first_message": "Hello! Thank you for your time today."
}
```

### Update Assistant
```
PATCH /assistants/{assistant_id}
```
Same body fields as create; only include fields to update.

---

## Numbers

### List Numbers
```
GET /numbers
```
Returns phone numbers associated with the workspace.

### Assign Number to Assistant
```
POST /numbers/{number_id}/assign
```
**Body:**
```json
{
  "assistant_id": "asst_abc123"
}
```

---

## Calling

### Initiate Outbound Call
```
POST /calls/outbound
```
**Body:**
```json
{
  "assistant_id": "asst_abc123",
  "to_number": "+919876543210",
  "from_number": "+918001234567",
  "dynamic_variables": {
    "customer_name": "Rahul",
    "order_id": "ORD-12345",
    "product": "Health Insurance Premium"
  },
  "webhook_url": "https://optional-per-call-webhook.example.com/callback"
}
```

**Response:**
```json
{
  "call_id": "call_xyz789",
  "status": "initiated",
  "to_number": "+919876543210",
  "from_number": "+918001234567",
  "assistant_id": "asst_abc123",
  "created_at": "2026-02-06T14:30:00Z"
}
```

### Get Call Status
```
GET /calls/{call_id}/status
```
**Response:**
```json
{
  "call_id": "call_xyz789",
  "status": "completed",
  "duration_seconds": 145,
  "disposition": "interested",
  "summary": "Customer expressed interest in health insurance renewal.",
  "ended_at": "2026-02-06T14:32:25Z"
}
```

Possible `status` values: `initiated`, `ringing`, `in-progress`, `completed`, `failed`, `no-answer`, `busy`.

### Get Call Transcript
```
GET /calls/{call_id}/transcript
```
**Response:**
```json
{
  "call_id": "call_xyz789",
  "transcript": [
    {"role": "agent", "text": "Hello Rahul, I'm calling from..."},
    {"role": "customer", "text": "Yes, tell me more..."}
  ],
  "language": "en-hi"
}
```

### End Call
```
POST /calls/{call_id}/end
```

---

## Campaigns

### List Campaigns
```
GET /campaigns
```

### Launch Campaign
```
POST /campaigns/launch
```
**Body:**
```json
{
  "campaign_id": "camp_abc123",
  "contacts": [
    {
      "phone": "+919876543210",
      "name": "Rahul",
      "email": "rahul@example.com",
      "custom_fields": {"policy_number": "POL-456"}
    }
  ],
  "schedule": {
    "start_time": "2026-02-07T09:00:00+05:30",
    "end_time": "2026-02-07T18:00:00+05:30",
    "timezone": "Asia/Kolkata"
  }
}
```

### Get Campaign Status
```
GET /campaigns/{campaign_id}/status
```

---

## History

### Get Call History
```
GET /calls/history?limit=20&offset=0&from=2026-02-01&to=2026-02-06
```

Query parameters:
- `limit` — Max results (default 20, max 100)
- `offset` — Pagination offset
- `from` / `to` — Date range (ISO 8601)
- `assistant_id` — Filter by assistant
- `status` — Filter by status (completed, failed, etc.)
- `disposition` — Filter by disposition

---

## Analytics

### Get Analytics
```
GET /analytics?from=2026-02-01&to=2026-02-06
```

**Response:**
```json
{
  "total_calls": 1250,
  "completed": 980,
  "failed": 45,
  "no_answer": 225,
  "avg_duration_seconds": 132,
  "dispositions": {
    "interested": 420,
    "not_interested": 310,
    "callback_requested": 150,
    "other": 100
  }
}
```

---

## Webhooks

### Register Webhook
```
POST /webhooks
```
**Body:**
```json
{
  "url": "https://your-endpoint.example.com/webhook/ringg",
  "events": ["call.completed", "call.failed", "call.transcript_ready", "campaign.completed"],
  "secret": "optional-signing-secret"
}
```

### Webhook Event Payload (call.completed)
```json
{
  "event": "call.completed",
  "call_id": "call_xyz789",
  "assistant_id": "asst_abc123",
  "to_number": "+919876543210",
  "status": "completed",
  "duration_seconds": 145,
  "disposition": "interested",
  "summary": "Customer expressed interest.",
  "transcript_available": true,
  "timestamp": "2026-02-06T14:32:25Z"
}
```

Available webhook events:
- `call.initiated`
- `call.ringing`
- `call.answered`
- `call.completed`
- `call.failed`
- `call.transcript_ready`
- `campaign.started`
- `campaign.completed`

### List Webhooks
```
GET /webhooks
```

### Delete Webhook
```
DELETE /webhooks/{webhook_id}
```

---

## Web Call (Embeddable)

### Get Web Call Embed Token
```
POST /webcall/token
```
**Body:**
```json
{
  "assistant_id": "asst_abc123",
  "visitor_info": {
    "name": "Website Visitor",
    "page_url": "https://example.com/pricing"
  }
}
```

Returns a short-lived token for the JavaScript embed widget.

---

## Rate Limits

- Standard: 60 requests/minute per API key
- Outbound calls: Subject to workspace plan limits
- Campaign launches: 1 concurrent campaign per assistant (configurable)

## Error Codes

| Code | Meaning |
|------|---------|
| 400  | Bad request — check body format and required fields |
| 401  | Invalid or expired API key |
| 403  | Insufficient permissions for this workspace |
| 404  | Resource not found (assistant, call, campaign) |
| 429  | Rate limited — retry after `Retry-After` header value |
| 500  | Internal server error — retry with backoff |
