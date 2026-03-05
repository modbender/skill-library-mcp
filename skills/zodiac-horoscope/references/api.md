# Zodiac Today API Reference

Base URL: `https://zodiac-today.com`

## Authentication

All endpoints require API key in header:
```
Authorization: Bearer hsk_your_api_key
```
Get your key from https://zodiac-today.com/en/dashboard after login.

## Endpoints

### POST /api/auth/send-code
Send a 6-digit verification code to an email. Creates a new user if not registered.
```json
{"email": "user@example.com"}
```
Response: `{"success": true}`

### POST /api/auth/verify
Verify the code. Returns user info. Auto-generates API key on first login.
```json
{"email": "user@example.com", "code": "123456"}
```
Response: `{"success": true, "user": {"id": "...", "email": "...", "tier": "free"}}`

### GET /api/auth/me
Get current user info (requires API key).

### GET /api/keys
List API keys (requires session cookie).

### POST /api/keys
Create a new API key (requires session cookie).
```json
{"name": "My Key"}
```
Response: `{"id": "...", "key": "hsk_...", "name": "My Key"}`

### POST /api/profiles
Create a birth profile.
```json
{"name": "John", "birthDate": "1990-05-15", "birthCity": "London, UK"}
```

### GET /api/profiles
List all profiles.

### GET /api/horoscope/daily
Get personalized daily horoscope.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| profileId | string | Required. Profile ID |
| startDate | YYYY-MM-DD | Required. Start date |
| endDate | YYYY-MM-DD | Required. End date |

**Tier Limits:**
| Tier | Max Profiles | Max Days from Today |
|------|-------------|-------------------|
| Free | 1 | 1 (today + tomorrow) |
| Starter ($4.99/mo) | 3 | 30 |
| Pro ($9.99/mo) | 5 | 90 |
| Premium ($19.99/mo) | 10 | 365 |

**Response:**
```json
{
  "profileId": "clxyz...",
  "profileName": "John",
  "sunSign": "Taurus",
  "horoscopes": [
    {
      "date": "2026-02-09",
      "overallRating": 7.8,
      "metrics": {
        "energy": "High",
        "focus": "Moderate",
        "romance": "Good",
        "luck": "High"
      },
      "favorable": ["Job interviews", "Starting a fitness routine"],
      "unfavorable": ["Major purchases", "Confrontations"],
      "luckyColors": [{"name": "Rose Pink", "hex": "#FF007F"}],
      "luckyNumbers": [7, 23, 42, 68],
      "summary": "With transit Venus forming a trine to your natal Sun..."
    }
  ]
}
```
