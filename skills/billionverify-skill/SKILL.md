---
name: billionverify
description: Verify email addresses using the BillionVerify API. Use when user wants to verify single emails, batch verify email lists, upload files for bulk verification, check credit balance, or manage webhooks.
version: 1.0.0
allowed-tools: Bash
---

# BillionVerify API Skill

Call the [BillionVerify](https://billionverify.com/) API to verify email addresses — single, batch, or bulk file processing.

## Setup

API key must be set in environment variable `BILLIONVERIFY_API_KEY`.
Get your API key at: https://billionverify.com/auth/sign-in?next=/home/api-keys

## Base URL

```
https://api.billionverify.com
```

## Authentication

All requests require an API key header:
```bash
-H "BV-API-KEY: $BILLIONVERIFY_API_KEY"
```

## Endpoints

### Verify Single Email
```bash
curl -X POST "https://api.billionverify.com/v1/verify/single" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "check_smtp": true
  }'
```

Response includes: `status` (valid/invalid/unknown/risky/disposable/catchall/role), `score` (0-1), `is_deliverable`, `is_disposable`, `is_catchall`, `is_role`, `is_free`, `domain`, `domain_age`, `mx_records`, `domain_reputation`, `smtp_check`, `reason`, `suggestion`, `response_time`, `credits_used`.

### Verify Batch Emails (max 50)
```bash
curl -X POST "https://api.billionverify.com/v1/verify/bulk" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["user1@example.com", "user2@example.com"],
    "check_smtp": true
  }'
```

### Upload File for Bulk Verification
Upload CSV, Excel (.xlsx/.xls), or TXT files (max 20MB, 100,000 emails):
```bash
curl -X POST "https://api.billionverify.com/v1/verify/file" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY" \
  -F "file=@/path/to/emails.csv" \
  -F "check_smtp=true" \
  -F "email_column=email" \
  -F "preserve_original=true"
```

Returns `task_id` for tracking the async job.

### Get File Job Status
Supports long-polling with `timeout` parameter (0-300 seconds):
```bash
curl -X GET "https://api.billionverify.com/v1/verify/file/{task_id}?timeout=30" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY"
```

Status values: `pending`, `processing`, `completed`, `failed`.

### Download Verification Results
Without filters returns redirect to full result file. With filters returns CSV of matching emails (filters combined with OR logic):
```bash
curl -X GET "https://api.billionverify.com/v1/verify/file/{task_id}/results?valid=true&invalid=true" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY" \
  -L -o results.csv
```

Filter parameters: `valid`, `invalid`, `catchall`, `role`, `unknown`, `disposable`, `risky`.

### Get Credit Balance
```bash
curl -X GET "https://api.billionverify.com/v1/credits" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY"
```

### Create Webhook
```bash
curl -X POST "https://api.billionverify.com/v1/webhooks" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/billionverify",
    "events": ["file.completed", "file.failed"]
  }'
```

The `secret` is only returned on creation — store it securely.

### List Webhooks
```bash
curl -X GET "https://api.billionverify.com/v1/webhooks" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY"
```

### Delete Webhook
```bash
curl -X DELETE "https://api.billionverify.com/v1/webhooks/{webhook_id}" \
  -H "BV-API-KEY: $BILLIONVERIFY_API_KEY"
```

### Health Check (no auth required)
```bash
curl -X GET "https://api.billionverify.com/health"
```

## Credits & Billing

- **Invalid** / **Unknown**: 0 credits (free)
- All other statuses (valid, risky, disposable, catchall, role): 1 credit each

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Single Verification | 6,000/min |
| Batch Verification | 1,500/min |
| File Upload | 300/min |
| Other endpoints | 200/min |

## User Request

$ARGUMENTS
