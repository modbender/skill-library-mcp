# 17track API Reference

## Overview

17track provides a universal package tracking API supporting 2000+ carriers worldwide.

- **API Version:** v2.2
- **Base URL:** `https://api.17track.net/track/v2.2`
- **Auth:** Header `17token: YOUR_API_KEY`
- **Free Tier:** 100 tracking registrations/month, unlimited gettrackinfo calls

## Getting an API Key

1. Go to https://admin.17track.net
2. Create an account
3. Navigate to API settings
4. Copy your API key

## Endpoints

### POST /register

Register tracking numbers for monitoring. **Costs 1 registration per number.**

```json
// Request body
[{"number": "1Z999AA10123456784", "carrier": 100002}]

// Response
{
  "code": 0,
  "data": {
    "accepted": [{"number": "1Z999AA10123456784", "carrier": 100002}],
    "rejected": []
  }
}
```

**Important:** Each registration counts against your monthly quota (100/month free).

**Error codes:**
- `-18010012` — Already registered (safe to ignore)
- `-18010001` — Invalid tracking number
- `-18010014` — Quota exceeded

### POST /gettrackinfo

Get tracking status for registered numbers. **Free and unlimited.**

```json
// Request body
[{"number": "1Z999AA10123456784"}]

// Response
{
  "code": 0,
  "data": {
    "accepted": [{
      "number": "1Z999AA10123456784",
      "track": {
        "e": 10,          // status code (see below)
        "z0": {           // tracking events from primary provider
          "z": [           // event list (newest first)
            {
              "a": "2024-01-15 14:30:00",  // date
              "z": "New York, NY",          // location
              "c": "Package departed facility" // description
            }
          ]
        }
      }
    }]
  }
}
```

### GET /getquota

Check remaining API quota.

```json
// Response
{
  "code": 0,
  "data": {
    "quota_total": 100,
    "quota_used": 42
  }
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 0 | Not Found |
| 10 | In Transit |
| 20 | Expired |
| 30 | Pick Up |
| 35 | Undelivered |
| 40 | Delivered |
| 50 | Alert |

## Rate Limits

- **Free tier:** 100 registrations/month
- **gettrackinfo:** No limit on calls (only registered numbers work)
- **Batch size:** Up to 40 numbers per gettrackinfo call
- **Recommended polling interval:** Every 2-4 hours for active packages

## Carrier Codes

Pass `carrier: 0` for auto-detection, or specify a code:
- `100001` — DHL
- `100002` — UPS
- `100003` — FedEx
- `2151` — CTT Portugal
- `3011` — China Post
- `1051` — Royal Mail
- `1031` — La Poste
- `1011` — Deutsche Post
- `1071` — PostNL

Full list: https://api.17track.net/track/v2.2/getcarrier
