---
name: aerobase-flights
description: Search, score, and compare flights with jetlag impact analysis.
homepage: https://aerobase.app
metadata:
  openclaw:
    requires:
      env:
        - AEROBASE_API_KEY
    primaryEnv: AEROBASE_API_KEY
---

# Aerobase Flights Skill

Search and analyze flights with jetlag scoring for healthier travel.

## Authentication

Set `AEROBASE_API_KEY` as an environment variable:

```bash
export AEROBASE_API_KEY="ak_xxxxxxxx"
```

Get your API key from https://aerobase.app/connect

## API Base URL

```
https://aerobase.app/api
```

## Tools

---

### 1. Search Flights

Find flights between destinations with jetlag scoring.

**Command:**
```bash
curl -X POST https://aerobase.app/api/v1/flights/search \
  -H "Authorization: Bearer $AEROBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "LAX",
    "to": "NRT",
    "date": "2026-04-15",
    "cabin": "economy",
    "sort": "jetlag",
    "limit": 10
  }'
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| from | string | Origin IATA code (e.g., LAX) |
| to | string | Destination IATA code (e.g., NRT) |
| date | string | Departure date (YYYY-MM-DD) |
| returnDate | string | Optional return date |
| cabin | string | economy, premium_economy, business, first |
| sort | string | jetlag, price, duration |
| limit | number | Results to return (free=5, pro=50) |

**Response includes:** flight details + jetlag_score, recovery_days, direction

---

### 2. Score a Flight

Get detailed jetlag analysis for a specific flight.

**Command:**
```bash
curl -X POST https://aerobase.app/api/v1/flights/score \
  -H "Authorization: Bearer $AEROBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "LAX",
    "to": "NRT",
    "departure": "2026-04-15T08:00:00-07:00",
    "arrival": "2026-04-16T14:30:00+09:00",
    "cabin": "business"
  }'
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| from | string | Origin IATA code |
| to | string | Destination IATA code |
| departure | string | ISO 8601 with offset |
| arrival | string | ISO 8601 with offset |
| cabin | string | economy, premium_economy, business, first |
| chronotype | string | early_bird, night_owl, normal |

**Response includes:**
- score (0-100, higher is better)
- tier: excellent|good|moderate|poor|severe
- recovery_days
- direction: east|west
- timezone_shift_hours
- breakdown (timezoneShift, departureTime, arrivalTime, duration, cabinComfort)
- strategies (departure, arrival, shift, recovery)
- tips

---

### 3. Compare Flights

Compare 2-10 flights side by side.

**Command:**
```bash
curl -X POST https://aerobase.app/api/v1/flights/compare \
  -H "Authorization: Bearer $AEROBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "flights": [
      {"from": "JFK", "to": "LHR", "departure": "2026-04-15T18:00:00-04:00", "arrival": "2026-04-16T07:00:00+01:00", "label": "Evening departure"},
      {"from": "JFK", "to": "LHR", "departure": "2026-04-15T22:00:00-04:00", "arrival": "2026-04-16T11:00:00+01:00", "label": "Red-eye"}
    ]
  }'
```

---

### 4. Recovery Plan

Generate personalized jetlag recovery plan.

**Command:**
```bash
curl -X POST https://aerobase.app/api/v1/recovery/plan \
  -H "Authorization: Bearer $AEROBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "LAX",
    "to": "NRT",
    "departure": "2026-04-15T08:00:00-07:00",
    "arrival": "2026-04-16T14:30:00+09:00",
    "arrival_commitments": [
      {"event": "Board Meeting", "time": "2026-04-17T09:00:00+09:00"}
    ]
  }'
```

**Response includes:**
- pre_flight_schedule (days before departure)
- during_flight recommendations
- post_arrival_schedule
- commitment_risks (if meetings provided)

---

### 5. Get Travel Deals

Find jetlag-scored travel deals.

**Command:**
```bash
curl "https://aerobase.app/api/v1/deals?departure=LAX&max_price=600&sort=jetlag_score&limit=10" \
  -H "Authorization: Bearer $AEROBASE_API_KEY"
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| departure | string | Origin IATA code |
| destination | string | Destination IATA code |
| max_price | number | Maximum price in USD |
| sort | string | value_score, price, jetlag_score, newest |
| limit | number | Results (free=3, pro=50) |

---

### 6. Airport Info

Get airport details with facilities.

**Command:**
```bash
curl "https://aerobase.app/api/v1/airports/JFK" \
  -H "Authorization: Bearer $AEROBASE_API_KEY"
```

---

### 7. Hotel Search

Find jetlag-friendly hotels near airport.

**Command:**
```bash
curl "https://aerobase.app/api/v1/hotels?airport=NRT&jetlagFriendly=true" \
  -H "Authorization: Bearer $AEROBASE_API_KEY"
```

---

### 8. Lounge Search

Find airport lounges.

**Command:**
```bash
curl "https://aerobase.app/api/v1/lounges?airport=LHR" \
  -H "Authorization: Bearer $AEROBASE_API_KEY"
```

---

### 9. Itinerary Analysis

Analyze multi-leg trips for cumulative jetlag.

**Command:**
```bash
curl -X POST https://aerobase.app/api/v1/itinerary/analyze \
  -H "Authorization: Bearer $AEROBASE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "legs": [
      {"from": "LAX", "to": "NRT", "departure": "...", "arrival": "..."},
      {"from": "NRT", "to": "SIN", "departure": "...", "arrival": "..."}
    ]
  }'
```

---

## Jetlag Score Guide

| Score | Tier | Recovery |
|-------|------|----------|
| 80-100 | Excellent | 0-2 days |
| 60-79 | Good | 2-3 days |
| 40-59 | Moderate | 3-5 days |
| 20-39 | Poor | 5-7 days |
| 0-19 | Severe | 7+ days |

## Response Format

All responses:

```json
{
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "tier": "free|pro|concierge|api",
    "calls_remaining": 95,
    "latency_ms": 234
  }
}
```

## Error Handling

Common error codes:
- INVALID_API_KEY - Check your API key
- VALIDATION_ERROR - Invalid parameters
- RATE_LIMIT_EXCEEDED - Upgrade tier
- TIER_REQUIRED - Endpoint needs higher tier

## Rate Limits

| Tier | Daily Calls |
|------|-------------|
| Free | 100 |
| Pro | 1,000 |
| Concierge | 10,000 |
| API | Unlimited |

## Presenting Results

Show the jetlag score prominently:

```
✈️ UA870 LAX → NRT
   Score: 72/100 (Good) | Recovery: 3 days
   Dep: 11:00 AM | Arr: 2:30 PM (+1 day)
   💡 Red-eye aligns with natural sleep
```

## Tips

- Always lead with the jetlag score
- Recommend flights with scores 60+ for business travel
- For important meetings, flag if score < 50
- Sort searches by "jetlag" for healthiest options
