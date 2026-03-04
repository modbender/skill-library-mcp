---
name: sealegs-marine-forecast
description: Get AI-powered marine weather forecasts for any location worldwide
homepage: https://developer.sealegs.ai
metadata: {"openclaw": {"requires": {"env": ["SEALEGS_API_KEY"], "bins": ["curl"]}, "primaryEnv": "SEALEGS_API_KEY"}, "emoji": "⛵", "tags": ["weather", "marine", "forecast", "boating", "sailing", "ocean", "waves", "wind"]}
---

# SeaLegs AI Marine Forecast API

Get AI-powered marine weather forecasts for any location worldwide. Includes wind, waves, visibility, precipitation analysis with GO/CAUTION/NO-GO safety classifications.

## Features

- **SpotCast Forecasts**: Get marine weather forecasts for any coordinates worldwide
- **AI Safety Analysis**: GO / CAUTION / NO-GO classifications for each day
- **Vessel-Specific**: Tailored recommendations based on boat type and size
- **Multi-Language**: Supports English, Spanish, French, Portuguese, Italian, Japanese

## Setup

### 1. Get an API Key

1. Sign up at https://developer.sealegs.ai — you'll get **10 free credits** to get started
2. Generate an API key from your dashboard
3. Need more? Add credits anytime ($10 = 200 forecast-days)

### 2. Configure OpenClaw

Add to your OpenClaw configuration:

```json5
{
  skills: {
    entries: {
      "sealegs-marine-forecast": {
        enabled: true,
        apiKey: "sk_live_your_key_here"
      }
    }
  }
}
```

Or set the environment variable:

```bash
export SEALEGS_API_KEY=sk_live_your_key_here
```

### 3. Install the Skill

```bash
clawhub install sealegs-marine-forecast
```

## Usage Example

```jsonc
// Miami, FL
POST /v3/spotcast
{
  "latitude": 25.7617,
  "longitude": -80.1918,
  "start_date": "2026-02-10T00:00:00Z",
  "num_days": 2,
  "vessel_info": {"type": "sailboat", "length_ft": 35}  // optional
}
```

**Sample response:**
```json
{
  "id": "spc_FrZdSAs6T3cxbXiPtNZvxu",
  "coordinates": {
    "latitude": 25.7617,
    "longitude": -80.1918
  },
  "forecast_period": {
    "start_date": "2026-02-10T00:00:00-05:00",
    "end_date": "2026-02-11T23:59:59-05:00",
    "num_days": "2"
  },
  "trip_duration_hours": "12",
  "metadata": {
    "location_name": "Miami Marina"
  },
  "latest_forecast": {
    "status": "completed",
    "ai_analysis": {
      "summary": "Ideal conditions both days with light winds",
      "daily_classifications": [
        {
          "date": "2026-02-10",
          "classification": "GO",
          "short_summary": "Outstanding conditions all day with light winds under 7kt and calm 1.1-1.6ft seas. Best window is morning 5:00 AM-12:00 PM with nearly calm 1-4kt northwest winds and comfortable 1.4ft seas at 11-second periods.",
          "summary": "Outstanding sailing conditions throughout Monday with exceptionally light winds and calm seas. Morning hours offer the best window with nearly calm 1-4kt northwest winds and comfortable 1.4ft seas at 11-second periods from the northeast."
        },
        {
          "date": "2026-02-11",
          "classification": "GO",
          "short_summary": "Exceptional conditions with very light winds 1-6kt and minimal 1.2-1.3ft seas all day. Best window 9:00 AM-1:00 PM offers glassy conditions with 1-3kt winds and 1.2ft seas at 11-second periods.",
          "summary": "Exceptional boating conditions on Tuesday with very light winds and minimal seas throughout the day. Morning through midday provides ideal glassy conditions with 1-3kt east-southeast winds and 1.2ft seas at 10-11 second periods from the northeast."
        }
      ]
    }
  }
}
```

## API Endpoints

| Operation | Endpoint | Cost |
|-----------|----------|------|
| Create forecast | POST /v3/spotcast | 1 credit/day |
| Get forecast | GET /v3/spotcast/{id} | Free |
| Check status | GET /v3/spotcast/{id}/status | Free |
| Refresh forecast | POST /v3/spotcast/{id}/refresh | 1 credit/day |
| List forecasts for SpotCast | GET /v3/spotcast/{id}/forecasts | Free |
| Get specific forecast | GET /v3/spotcast/{id}/forecast/{forecast_id} | Free |
| List SpotCasts | GET /v3/spotcasts | Free |
| Get balance | GET /v3/account/balance | Free |

## Weather Factors Used

- Wind speed, gusts, and direction
- Wave height, period, and direction
- Visibility and fog probability
- Precipitation probability and intensity
- Air and water temperature

## Authentication

All requests require:
```
Authorization: Bearer $SEALEGS_API_KEY
Content-Type: application/json
```

## Rate Limits

- Standard tier: 60 requests per minute
- Rate limit headers included in all responses: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Billing

- 1 credit per forecast-day (3-day forecast = 3 credits)
- GET operations are free
- Refreshes cost 1 credit per forecast-day

---

# SpotCast Forecasts

SpotCast generates AI-powered marine weather forecasts for specific coordinates.

## Create SpotCast

**POST** `https://api.sealegs.ai/v3/spotcast`

Creates a new forecast request. Processing is asynchronous (typically 30-60 seconds).

**Required parameters:**
- `latitude` (number): -90 to 90
- `longitude` (number): -180 to 180
- `start_date` (string): ISO 8601 format (e.g., "2025-12-05T00:00:00Z")
- `num_days` (integer): 1-5

**Optional parameters:**
- `webhook_url` (string): HTTPS endpoint for completion notification
- `metadata` (object): Custom key-value pairs for your reference
- `trip_duration_hours` (integer): Trip duration in hours
- `preferences.language`: en, es, fr, pt, it, ja (default: en)
- `preferences.distance_units`: nm, mi, km (default: nm)
- `preferences.speed_units`: kts, mph, ms (default: kts)
- `vessel_info.type`: powerBoat, sailboat, pwc, yacht, catamaran
- `vessel_info.length_ft`: 1-500

**Example request:**
```bash
curl -X POST https://api.sealegs.ai/v3/spotcast \
  -H "Authorization: Bearer $SEALEGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 25.7617,
    "longitude": -80.1918,
    "start_date": "2025-12-05T00:00:00Z",
    "num_days": 2,
    "vessel_info": {"type": "sailboat", "length_ft": 35}
  }'
```

**Response (202 Accepted):**
```json
{
  "id": "spc_abc123xyz",
  "forecast_id": "fcst_xyz789",
  "status": "processing",
  "created_at": "2025-12-01T10:30:00Z",
  "estimated_completion_seconds": 45,
  "credits_charged": 2,
  "credits_remaining": 98,
  "links": {
    "self": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz",
    "forecast": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/forecast/fcst_xyz789",
    "status": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/status"
  }
}
```

## Check SpotCast Status

**GET** `https://api.sealegs.ai/v3/spotcast/{id}/status`

Poll this endpoint until status is "completed" or "failed". Recommended poll interval: 10-15 seconds.

**Status values:**
- `pending`: Queued for processing (no `progress` field)
- `processing`: Currently generating forecast (includes `progress`)
- `completed`: Ready to retrieve (includes `progress` at 100%)
- `failed`: Error occurred

**Progress stages** (only present when status is `processing` or `completed`):
- fetching_weather
- processing_data
- ai_analysis
- completing
- completed (100%)

**Example request:**
```bash
curl https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/status \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (pending):**
```json
{
  "id": "spc_abc123xyz",
  "forecast_id": "fcst_xyz789",
  "status": "pending",
  "created_at": "2025-12-01T10:30:00Z"
}
```

**Response (processing):**
```json
{
  "id": "spc_abc123xyz",
  "forecast_id": "fcst_xyz789",
  "status": "processing",
  "created_at": "2025-12-01T10:30:00Z",
  "progress": {
    "stage": "ai_analysis",
    "percentage": 75
  }
}
```

**Response (completed):**
```json
{
  "id": "spc_abc123xyz",
  "forecast_id": "fcst_xyz789",
  "status": "completed",
  "created_at": "2025-12-01T10:30:00Z",
  "completed_at": "2025-12-01T10:30:45Z",
  "progress": {
    "stage": "completed",
    "percentage": 100
  }
}
```

## Get SpotCast

**GET** `https://api.sealegs.ai/v3/spotcast/{id}`

Retrieves the completed forecast with AI analysis.

**Example request:**
```bash
curl https://api.sealegs.ai/v3/spotcast/spc_abc123xyz \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (200 OK):**
```json
{
  "id": "spc_abc123xyz",
  "created_at": "2025-12-01T10:30:00Z",
  "coordinates": {
    "latitude": 25.7617,
    "longitude": -80.1918
  },
  "forecast_period": {
    "start_date": "2025-12-05T00:00:00Z",
    "end_date": "2025-12-06T00:00:00Z",
    "num_days": 2
  },
  "trip_duration_hours": 12,
  "forecast_count": 1,
  "metadata": {
    "location_name": "Miami Marina"
  },
  "latest_forecast": {
    "forecast_id": "fcst_xyz789",
    "status": "completed",
    "created_at": "2025-12-01T10:30:00Z",
    "completed_at": "2025-12-01T10:30:45Z",
    "ai_analysis": {
      "summary": "Excellent conditions expected. Light winds 8-12kt from the NE with calm 1-2ft seas.",
      "daily_classifications": [
        {
          "date": "2025-12-05",
          "classification": "GO",
          "summary": "Light winds 8-12kt from NE. Seas 1-2ft. Visibility excellent at 10+ nm. No precipitation expected."
        },
        {
          "date": "2025-12-06",
          "classification": "CAUTION",
          "summary": "Winds increasing to 15-20kt. Seas building to 3-4ft by afternoon. Morning departure recommended."
        }
      ]
    }
  }
}
```

## Refresh SpotCast

**POST** `https://api.sealegs.ai/v3/spotcast/{id}/refresh`

Updates an existing forecast with the latest weather data. Costs 1 credit per forecast-day.

**Optional body:**
- `webhook_url` (string): Override webhook for this refresh

**Example request:**
```bash
curl -X POST https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/refresh \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (202 Accepted):**
```json
{
  "id": "spc_abc123xyz",
  "forecast_id": "fcst_newxyz789",
  "status": "processing",
  "created_at": "2025-12-02T08:00:00Z",
  "links": {
    "self": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz",
    "status": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/status"
  }
}
```

## List Forecasts

**GET** `https://api.sealegs.ai/v3/spotcast/{id}/forecasts`

Lists all forecasts for a SpotCast, sorted by creation date (newest first). Each time you create or refresh a SpotCast, a new forecast is generated.

**Query parameters:**
- `limit` (integer): Number of results to return (default: 10)

**Example request:**
```bash
curl "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/forecasts?limit=5" \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (200 OK):**
```json
{
  "spotcast_id": "spc_abc123xyz",
  "data": [
    {
      "forecast_id": "fcst_newxyz789",
      "status": "completed",
      "created_at": "2025-12-02T08:00:00Z",
      "completed_at": "2025-12-02T08:00:42Z"
    },
    {
      "forecast_id": "fcst_xyz789",
      "status": "completed",
      "created_at": "2025-12-01T10:30:00Z",
      "completed_at": "2025-12-01T10:30:45Z"
    }
  ],
  "has_more": false
}
```

## Get Forecast

**GET** `https://api.sealegs.ai/v3/spotcast/{id}/forecast/{forecast_id}`

Retrieves a specific forecast with full details including AI analysis. Use this to access any forecast in a SpotCast's history, not just the latest one.

**Example request:**
```bash
curl "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/forecast/fcst_xyz789" \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (200 OK - Completed):**
```json
{
  "forecast_id": "fcst_xyz789",
  "spotcast_id": "spc_abc123xyz",
  "status": "completed",
  "created_at": "2025-12-01T10:30:00Z",
  "completed_at": "2025-12-01T10:30:45Z",
  "forecast_period": {
    "start_date": "2025-12-05T00:00:00Z",
    "num_days": 2
  },
  "ai_analysis": {
    "summary": "Excellent conditions expected. Light winds 8-12kt from the NE with calm 1-2ft seas.",
    "daily_classifications": [
      {
        "date": "2025-12-05",
        "classification": "GO",
        "summary": "Light winds and calm seas throughout the day."
      },
      {
        "date": "2025-12-06",
        "classification": "CAUTION",
        "summary": "Improving conditions with best windows in the afternoon."
      }
    ]
  }
}
```

**Response (200 OK - Processing):**
```json
{
  "forecast_id": "fcst_xyz789",
  "spotcast_id": "spc_abc123xyz",
  "status": "processing",
  "created_at": "2025-12-01T10:30:00Z",
  "forecast_period": {
    "start_date": "2025-12-05T00:00:00Z",
    "num_days": 2
  },
  "progress": {
    "stage": "analyzing",
    "percentage": 65
  }
}
```

**Response (200 OK - Failed):**
```json
{
  "forecast_id": "fcst_xyz789",
  "spotcast_id": "spc_abc123xyz",
  "status": "failed",
  "created_at": "2025-12-01T10:30:00Z",
  "forecast_period": {
    "start_date": "2025-12-05T00:00:00Z",
    "num_days": 2
  },
  "error": "Processing failed"
}
```

## List SpotCasts

**GET** `https://api.sealegs.ai/v3/spotcasts`

Retrieves all SpotCasts for your account.

**Query parameters:**
- `limit` (integer): 1-100 results (default: 20)
- `after` (string): Cursor for pagination

**Example request:**
```bash
curl "https://api.sealegs.ai/v3/spotcasts?limit=10" \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "spc_abc123xyz",
      "created_at": "2025-12-01T10:30:00Z",
      "coordinates": {
        "latitude": 25.7617,
        "longitude": -80.1918
      },
      "start_date": "2025-12-05T00:00:00-05:00",
      "end_date": "2025-12-06T23:59:59-05:00",
      "num_days": 2,
      "latest_forecast": {
        "forecast_id": "fcst_xyz789",
        "status": "completed"
      }
    }
  ],
  "has_more": true,
  "next_cursor": "spc_def456"
}
```

---

# Account

## Get Balance

**GET** `https://api.sealegs.ai/v3/account/balance`

Returns your current credit balance and usage.

**Example request:**
```bash
curl https://api.sealegs.ai/v3/account/balance \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

**Response (200 OK):**
```json
{
  "credit_balance": 100,
  "total_credits_purchased": 200,
  "total_credits_used": 100,
  "purchase_url": "https://developers.sealegs.ai/dashboard/billing"
}
```

---

# Webhooks

When you provide a `webhook_url` during SpotCast creation or refresh, SeaLegs sends a POST request to that URL when processing completes or fails.

## Webhook Headers

```
Content-Type: application/json
X-SeaLegs-Event: spotcast.forecast.completed
X-SeaLegs-Signature: sha256=abc123...
X-SeaLegs-Delivery-ID: whk_abc123xyz
X-SeaLegs-Timestamp: 1733045400
User-Agent: SeaLegs-Webhooks/1.0
```

## Verifying Signatures

Every webhook includes an HMAC-SHA256 signature in the `X-SeaLegs-Signature` header. Your webhook secret is available in the Developer Dashboard. Always verify the signature before processing the payload.

**Python:**
```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

**JavaScript:**
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expected = crypto.createHmac('sha256', secret).update(payload).digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expected}`),
    Buffer.from(signature)
  );
}
```

## Completed Event

```json
{
  "event": "spotcast.forecast.completed",
  "created_at": "2025-12-01T10:30:45Z",
  "data": {
    "spotcast_id": "spc_abc123xyz",
    "forecast_id": "fcst_xyz789",
    "status": "completed",
    "summary": "Excellent conditions expected. Light winds 8-12kt from the NE with calm 1-2ft seas.",
    "metadata": {
      "trip_name": "Weekend Fishing Trip"
    }
  }
}
```

The `summary` field is included when AI analysis completes successfully. The `metadata` object is included when you provided metadata in the original `POST /v3/spotcast` request, echoed back exactly as sent.

## Failed Event

```json
{
  "event": "spotcast.forecast.failed",
  "created_at": "2025-12-01T10:31:00Z",
  "data": {
    "spotcast_id": "spc_abc123xyz",
    "forecast_id": "fcst_xyz789",
    "status": "failed",
    "error": {
      "code": "processing_failed",
      "message": "Unable to fetch weather data for the specified location"
    },
    "metadata": {
      "trip_name": "Weekend Fishing Trip"
    }
  }
}
```

## Retry Policy

Failed deliveries are retried up to 4 times: after 5 minutes, 30 minutes, 2 hours, and 24 hours.

---

# Understanding Results

## Daily Classifications

Each forecast day receives a safety classification:

| Classification | Meaning |
|----------------|---------|
| **GO** | Safe conditions for the vessel type |
| **CAUTION** | Proceed with awareness; conditions may be challenging |
| **NO-GO** | Conditions not recommended for the vessel type |

Classifications are adjusted based on vessel type and size when `vessel_info` is provided.

## Weather Variables Analyzed

- **Wind**: Speed (kts), gusts, direction (degrees)
- **Waves**: Height (ft), period (seconds), direction, swell
- **Visibility**: Distance (nm), fog probability
- **Precipitation**: Probability (%), intensity
- **Temperature**: Air and water (F/C)

## Vessel-Specific Adjustments

When `vessel_info` is provided:
- **PWC/Jet Ski**: Stricter wave height limits
- **Sailboats**: Wind optimization recommendations
- **Large Yachts**: Higher tolerance for wave conditions
- **Small Powerboats**: Balanced wind/wave thresholds

---

# Error Handling

## Error Response Format

```json
{
  "error": {
    "code": "invalid_coordinates",
    "message": "Latitude must be between -90 and 90",
    "param": "latitude"
  }
}
```

## HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Request completed |
| 201 | Created | Resource created |
| 202 | Accepted | Async processing started |
| 400 | Bad Request | Check parameter values |
| 401 | Unauthorized | Verify API key is correct |
| 402 | Payment Required | Add credits at developer.sealegs.ai |
| 403 | Forbidden | Account not verified or suspended |
| 404 | Not Found | Check resource ID |
| 429 | Rate Limited | Wait and retry (60 req/min limit) |
| 500 | Server Error | Retry after brief delay |

## Error Codes

### Authentication (401)

| Code | Description |
|------|-------------|
| `missing_api_key` | No API key provided in request |
| `invalid_api_key` | API key is not recognized |
| `key_revoked` | API key has been revoked |

### Authorization (403)

| Code | Description |
|------|-------------|
| `account_not_verified` | Developer account has not been verified |
| `account_suspended` | Developer account has been suspended |

### Payment (402)

| Code | Description |
|------|-------------|
| `insufficient_balance` | Not enough credits (response includes `current_balance`, `required_credits`, `purchase_url`) |

### Validation (400)

| Code | Description |
|------|-------------|
| `invalid_coordinates` | Coordinates out of valid range |
| `invalid_date_format` | Not ISO 8601 format |
| `invalid_webhook_url` | Not a valid HTTPS URL |
| `invalid_preferences` | Preferences format is invalid |
| `invalid_language` | Language not supported (use: en, es, fr, pt, it, ja) |
| `invalid_distance_units` | Distance units not supported (use: nm, mi, km) |
| `invalid_speed_units` | Speed units not supported (use: kts, mph, ms) |
| `invalid_json` | Request body is not valid JSON |

### Not Found (404)

| Code | Description |
|------|-------------|
| `spotcast_not_found` | The specified SpotCast does not exist |
| `forecast_not_found` | The specified forecast does not exist |

### Rate Limit (429)

| Code | Description |
|------|-------------|
| `rate_limit_exceeded` | Too many requests (response includes `retry_after` seconds) |

### Server (500)

| Code | Description |
|------|-------------|
| `internal_error` | An unexpected error occurred |
| `creation_failed` | Failed to create SpotCast |
| `retrieval_failed` | Failed to retrieve resource |

---

# Common Workflows

## Get a Marine Forecast

1. Create a SpotCast with coordinates and dates
2. Poll the status endpoint until "completed"
3. Retrieve the full forecast with AI analysis
4. Present GO/CAUTION/NO-GO classification to user

## Check Conditions Before a Trip

1. Create SpotCast with trip coordinates and date
2. Include vessel_info for tailored recommendations
3. Check daily_classifications for each day
4. Review AI summary for specific concerns

---

## Links

- [Developer Portal](https://developer.sealegs.ai)
- [API Documentation](https://developer.sealegs.ai/docs/)
- [SeaLegs App](https://sealegs.ai)

## License

MIT
