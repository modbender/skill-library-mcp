# Loopuman API Reference

Base URL: `https://api.loopuman.com`

All requests require the `x-api-key` header.

## Authentication

```
x-api-key: YOUR_API_KEY
```

Get your key (no auth needed):
```bash
curl -X POST https://api.loopuman.com/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "company_name": "Your Name"}'
```
Save the returned `api_key` (starts with `lpm_`) — it cannot be retrieved later.

## Endpoints

### POST /api/v1/register

Get an API key. No authentication required.

**Request:**
```json
{
  "email": "you@example.com",
  "company_name": "Your Name or Company"
}
```

**Response (201):**
```json
{
  "message": "Welcome to Loopuman — The Human Layer for AI",
  "api_key": "lpm_abc123...",
  "user_id": "uuid",
  "important": "⚠️ Save this API key now — it cannot be retrieved later."
}
```

### POST /api/v1/tasks

Create a new human task.

**Request:**
```json
{
  "title": "Verify business address",
  "description": "Check if 123 Main St, Nairobi exists on Google Maps. Reply YES/NO with screenshot.",
  "category": "other",
  "budget_vae": 30,
  "estimated_seconds": 120,
  "max_workers": 1,
  "priority": "normal",
  "webhook_url": "https://your-server.com/webhook"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | yes | Short task title |
| `description` | string | yes | Detailed worker instructions |
| `category` | string | no | `survey`, `labeling`, `translation`, `writing`, `research`, `content_creation`, `ai_training`, `micro`, `other` (default: `other`) |
| `budget_vae` | integer | no | Payment per worker in VAE (default: 100). 100 VAE = $1 USD |
| `budget_usd` | number | no | Alternative: specify budget in USD |
| `estimated_seconds` | integer | yes | Expected completion time. Used for $6/hr minimum rate enforcement |
| `max_workers` | integer | no | Number of workers (default: 1, max: 100) |
| `priority` | string | no | `normal` or `high` (high notifies workers) |
| `webhook_url` | string | no | URL for push notification on completion |
| `auto_approve` | boolean | no | Auto-approve submissions (default: false) |
| `reference_media` | array | no | Array of image/doc URLs for worker reference |

**Response (201):**
```json
{
  "task_id": "uuid-here",
  "status": "active",
  "budget_vae": 30,
  "budget_usd": "0.30",
  "workers_needed": 1,
  "expires_at": "2026-02-14T19:00:00Z"
}
```

### GET /api/v1/tasks/:id

Get task status, progress, and submissions.

**Response:**
```json
{
  "task_id": "uuid-here",
  "title": "Verify business address",
  "description": "...",
  "category": "other",
  "status": "active",
  "budget_vae": 30,
  "budget_usd": "0.30",
  "max_workers": 1,
  "created_at": "2026-02-13T19:00:00Z",
  "expires_at": "2026-02-14T19:00:00Z",
  "progress": {
    "approved": 1,
    "pending_review": 0,
    "in_progress": 0,
    "total_slots": 1
  },
  "submissions": [
    {
      "submission_id": "sub-uuid",
      "content": "YES — the address exists. Commercial building on Kenyatta Ave.",
      "submitted_at": "2026-02-13T19:08:42Z",
      "approved_at": "2026-02-13T19:08:45Z",
      "rating": 5
    }
  ],
  "pending_submissions": []
}
```

**Statuses:** `active` → `completed` | `expired` | `cancelled`

### GET /api/v1/tasks

List all tasks for your API key.

### DELETE /api/v1/tasks/:id

Cancel a task. Refunds your balance if no workers have started.

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid or missing `x-api-key` |
| 400 | Missing required fields, invalid category, or budget too low |
| 402 | Insufficient VAE balance |
| 404 | Task not found |
| 429 | Rate limit exceeded |
| 500 | Server error |

## Fair Pay

Loopuman enforces a **$6/hr minimum effective rate**. The API calculates: `(budget_vae / 100) / (estimated_seconds / 3600)`. If below $6/hr, it returns an error with a suggested budget.

## Currency

- 100 VAE = $1.00 USD
- New accounts: 100 VAE free
- 20% commission charged on top of budget (requester pays budget × 1.2)
- Workers receive 80% of budget (worker gets budget × 0.8)
- Workers paid in 8 seconds via cUSD on Celo blockchain
