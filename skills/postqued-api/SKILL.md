---
name: postqued-api
description: PostQued social media scheduling API integration. Use when performing API calls to PostQued for content upload, publishing to TikTok (and other platforms), managing platform accounts, or querying publish status. Triggers on tasks involving social media posting, content scheduling, TikTok draft posting, or any PostQued API operations.
---

# PostQued API Skill

## Setup

Add your PostQued API key to your workspace `.env` file:

```
POSTQUED_API_KEY=pq_your_api_key_here
```

API keys are created in the PostQued dashboard at https://postqued.com/console. Keys start with `pq_` prefix.

## Authentication

All API requests require authentication via Bearer token:

```
Authorization: Bearer $POSTQUED_API_KEY
```

## Base URL

```
https://api.postqued.com
```

## API Documentation

OpenAPI spec: https://api.postqued.com/v1/docs/openapi.json

## Core Workflow: Upload and Publish Content

### Step 1: Upload Content

**For videos** (presigned URL upload):

```bash
# Start upload session
curl -X POST https://api.postqued.com/v1/content/upload \
  -H "Authorization: Bearer $POSTQUED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "video.mp4",
    "contentType": "video/mp4",
    "fileSize": 52428800
  }'
# Response: { "contentId": "uuid", "upload": { "url": "presigned-url", "method": "PUT", "headers": {...} } }

# Upload file to presigned URL
curl -X PUT "PRESIGNED_URL" \
  -H "Content-Type: video/mp4" \
  --data-binary @video.mp4

# Confirm upload
curl -X POST https://api.postqued.com/v1/content/upload/complete \
  -H "Authorization: Bearer $POSTQUED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contentId": "uuid-from-step-1",
    "key": "content/user-id/content-id.mp4",
    "filename": "video.mp4",
    "contentType": "video/mp4",
    "size": 52428800,
    "width": 1920,
    "height": 1080,
    "durationMs": 30000
  }'
```

**For images** (direct upload):

```bash
curl -X POST https://api.postqued.com/v1/content/upload-image \
  -H "Authorization: Bearer $POSTQUED_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

### Step 2: Get Platform Account ID

```bash
curl https://api.postqued.com/v1/platform-accounts?platform=tiktok \
  -H "Authorization: Bearer $POSTQUED_API_KEY"
# Response: { "accounts": [{ "id": "account-uuid", "username": "@user", ... }] }
```

### Step 3: Publish Content

**Important:** Always include a unique `Idempotency-Key` header (valid 24h).

```bash
curl -X POST https://api.postqued.com/v1/content/publish \
  -H "Authorization: Bearer $POSTQUED_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: unique-uuid-per-request" \
  -d '{
    "contentIds": ["content-uuid"],
    "targets": [{
      "platform": "tiktok",
      "accountId": "account-uuid",
      "intent": "draft",
      "caption": "Check this out! #fyp",
      "dispatchAt": null,
      "options": {
        "privacyLevel": "SELF_ONLY",
        "disableDuet": false,
        "disableStitch": false,
        "disableComment": false
      }
    }]
  }'
# Response: { "publishId": "uuid", "status": "pending", "targets": [...] }
```

### Step 4: Check Publish Status

```bash
curl https://api.postqued.com/v1/content/publish/PUBLISH_ID \
  -H "Authorization: Bearer $POSTQUED_API_KEY"
```

## API Reference

See [references/api.md](references/api.md) for complete endpoint documentation.

## TikTok-Specific Options

| Option                | Type    | Description                                                                       |
| --------------------- | ------- | --------------------------------------------------------------------------------- |
| privacyLevel          | string  | `PUBLIC_TO_EVERYONE`, `MUTUAL_FOLLOW_FRIENDS`, `FOLLOWER_OF_CREATOR`, `SELF_ONLY` |
| disableDuet           | boolean | Disable duet                                                                      |
| disableStitch         | boolean | Disable stitch                                                                    |
| disableComment        | boolean | Disable comments                                                                  |
| videoCoverTimestampMs | integer | Cover frame timestamp (videos)                                                    |
| autoAddMusic          | boolean | Auto-add music (photos)                                                           |
| brandContentToggle    | boolean | Paid partnership disclosure                                                       |
| brandOrganicToggle    | boolean | Promotional content disclosure                                                    |

## Intent Values

- `draft` - Send to TikTok inbox as draft (user publishes manually)
- `publish` - Direct publish to user's TikTok profile

## Status Values

**Publish Request:** `pending` | `processing` | `completed` | `partial_failed` | `failed` | `canceled`

**Target:** `queued` | `scheduled` | `processing` | `sent` | `published` | `failed` | `canceled`

## Scheduling

Set `dispatchAt` to a future UTC ISO timestamp:

```json
{
  "dispatchAt": "2026-02-20T15:00:00Z"
}
```

Set to `null` for immediate dispatch.

## Rate Limits

| Operation | Limit  |
| --------- | ------ |
| Upload    | 20/min |
| Read      | 30/min |
| Publish   | 10/min |
| Delete    | 20/min |

## Error Handling

Errors return:

```json
{
  "error": "Message",
  "code": "ERROR_CODE"
}
```

Common codes: `MISSING_IDEMPOTENCY_KEY`, `IDEMPOTENCY_CONFLICT`, `SUBSCRIPTION_REQUIRED`
