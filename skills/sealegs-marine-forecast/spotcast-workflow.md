# SpotCast Workflow Example

Complete end-to-end example of getting a marine forecast.

## Scenario

User asks: "Is it safe to take my 30ft sailboat out from Miami Marina this Saturday?"

## Step 1: Create the SpotCast

```bash
curl -X POST https://api.sealegs.ai/v3/spotcast \
  -H "Authorization: Bearer $SEALEGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 25.7617,
    "longitude": -80.1918,
    "start_date": "2025-12-07T00:00:00Z",
    "num_days": 1,
    "vessel_info": {
      "type": "sailboat",
      "length_ft": 30
    },
    "metadata": {
      "location_name": "Miami Marina"
    }
  }'
```

Response:
```json
{
  "id": "spc_abc123xyz",
  "status": "processing",
  "forecast_id": "fcst_xyz789",
  "estimated_completion_seconds": 45,
  "created_at": "2025-12-06T14:30:00Z",
  "credits_charged": 1,
  "credits_remaining": 199,
  "links": {
    "self": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz",
    "status": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/status",
    "forecast": "https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/forecast/fcst_xyz789"
  }
}
```

## Step 2: Poll for Completion

```bash
curl https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/status \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

Response (still processing):
```json
{
  "id": "spc_abc123xyz",
  "status": "processing",
  "progress": {
    "stage": "ai_analysis",
    "percentage": 75
  }
}
```

Wait 10-15 seconds and poll again until status is "completed".

## Step 3: Get the Forecast

```bash
curl https://api.sealegs.ai/v3/spotcast/spc_abc123xyz \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

Response:
```json
{
  "id": "spc_abc123xyz",
  "status": "completed",
  "created_at": "2025-12-06T14:30:00Z",
  "coordinates": {
    "latitude": 25.7617,
    "longitude": -80.1918
  },
  "forecast_period": {
    "start_date": "2025-12-07T00:00:00Z",
    "end_date": "2025-12-07T23:59:59Z",
    "num_days": 1
  },
  "trip_duration_hours": 12,
  "forecast_count": 1,
  "metadata": {
    "location_name": "Miami Marina"
  },
  "latest_forecast": {
    "forecast_id": "fcst_xyz789",
    "status": "completed",
    "ai_analysis": {
      "summary": "Good conditions for sailing. Light to moderate winds from the northeast will provide comfortable sailing conditions. Seas are calm with occasional 2ft swells.",
      "daily_classifications": [
        {
          "date": "2025-12-07",
          "classification": "GO",
          "summary": "Winds 10-15kt from NE, ideal for sailing. Waves 1-2ft. Visibility excellent at 10+ nm. Clear skies, no precipitation expected. Best sailing: morning through early afternoon before sea breeze builds."
        }
      ]
    }
  }
}
```

## Step 4: Present to User

Based on the forecast:

**Classification: GO**

Saturday looks great for your 30ft sailboat at Miami Marina:

- **Wind**: 10-15 kts from NE (ideal sailing conditions)
- **Waves**: 1-2 ft (calm)
- **Visibility**: Excellent (10+ nm)
- **Precipitation**: None expected

**Recommendation**: Best sailing window is morning through early afternoon before the sea breeze builds.

## Refreshing Later

If the trip is a few days away and you want updated data closer to the date:

```bash
curl -X POST https://api.sealegs.ai/v3/spotcast/spc_abc123xyz/refresh \
  -H "Authorization: Bearer $SEALEGS_API_KEY"
```

Then poll status and retrieve the updated forecast.
