---
name: skill-amazon-review-request
description: Sends Amazon review requests for eligible Shipped orders via SP-API
  Messaging API. Hardened with retry logic, deduplication, eligibility window
  enforcement, and dry-run mode.
---

# skill-amazon-review-request

Sends Amazon review requests for eligible Shipped orders via SP-API Messaging API.
Hardened with retry logic, deduplication, eligibility window enforcement, and dry-run mode.

## Prerequisites

- SP-API credentials in `~/amazon-sp-api.json`:
  ```json
  {
    "refreshToken": "...",
    "clientId": "...",
    "clientSecret": "...",
    "marketplaceId": "A2VIGQ35RCS4UG"
  }
  ```
- Or set env vars: `SP_API_REFRESH_TOKEN`, `SP_API_CLIENT_ID`, `SP_API_CLIENT_SECRET`, `SP_API_MARKETPLACE_ID`
- SP-API app must have **Messaging** permission granted

## Usage

```bash
# Dry run — see what would be sent (no requests made)
node scripts/request-reviews.js --dry-run

# Live run
node scripts/request-reviews.js
```

## Behavior

| Feature | Detail |
|---|---|
| **Eligibility window** | Orders 5–30 days old only (Amazon's allowed window) |
| **Deduplication** | Skips orders already logged as `sent` in the tracking log |
| **Retry logic** | Up to 3 attempts with 5s delay on 5xx / 429 responses |
| **Rate limiting** | 1.1s pause between requests |
| **Dry-run** | `--dry-run` flag — logs what would be sent, no API calls |
| **Tracking log** | `data/review-requests-log.json` — per-order status, sentAt, attempts |
| **Text log** | `data/review-requests.log` — timestamped human-readable run log |

## Tracking Log Schema

`data/review-requests-log.json`:
```json
[
  {
    "orderId": "123-4567890-1234567",
    "sentAt": "2026-03-01T10:00:00.000Z",
    "status": "sent",       // "sent" | "failed" | "skipped"
    "attempts": 1,
    "reason": "optional error string for failed/skipped"
  }
]
```

## Summary Output

```
=== DONE | Sent: 12 | Skipped: 4 | Failed: 1 ===
```

Dry-run:
```
=== DONE [DRY RUN] | Would send: 15 | Skipped: 4 ===
```

## Scheduling (Recommended)

Run daily via cron:
```bash
# 9am UAE time (UTC+4) = 5am UTC
0 5 * * * cd $HOME/.openclaw/workspace && node skills/skill-amazon-review-request/scripts/request-reviews.js >> data/review-requests-cron.log 2>&1
```

## Region Note

Script targets `sellingpartnerapi-eu.amazon.com` (EU endpoint, covers UAE marketplace).
Change to `sellingpartnerapi-na.amazon.com` or `sellingpartnerapi-fe.amazon.com` for other regions.
