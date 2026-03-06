# Hybrid Training Plan API Reference

Base URL: `https://api.hybridtrainingplan.app`

All endpoints require `Authorization: Bearer <token>` where the token is either:
- A JWT from the web app session, or
- An API key with prefix `htp_` generated from the Account page

---

## Authentication

### API key format
`htp_` + 64 hex characters (68 chars total)

Example: `htp_a1b2c3d4e5f6...`

---

## Users

### GET /api/users/me
Returns the authenticated user's profile.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Jane Smith",
  "distanceUnit": "km",
  "timezone": "Europe/London"
}
```

### GET /api/users/me/dashboard
Returns a summary of the user's current training plan and today's workout.

**Response:**
```json
{
  "currentPlanId": "uuid | null",
  "today": "2026-02-27",
  "currentWeek": { "weekNumber": 3, "theme": "Volume build" },
  "todayDay": {
    "date": "2026-02-27",
    "dayOfWeek": "friday",
    "isRestDay": false,
    "status": "pending",
    "sessions": [{ "id": "uuid", "title": "Lower Strength", "sessionType": "strength" }]
  }
}
```

---

## Plans

### GET /api/plans/:planId
Returns a plan with its full content.

**Response:**
```json
{
  "id": "uuid",
  "title": "12-Week Hybrid Plan",
  "status": "active",
  "content": {
    "weeks": [
      {
        "weekNumber": 1,
        "theme": "Foundation",
        "days": [
          {
            "date": "2026-02-27",
            "dayOfWeek": "friday",
            "isRestDay": false,
            "status": "pending",
            "sessions": [
              {
                "id": "uuid",
                "title": "Lower Strength",
                "sessionType": "strength",
                "strength": {
                  "exercises": [
                    {
                      "name": "Squat",
                      "sets": 3,
                      "reps": "5",
                      "loadGuidance": "@RPE8"
                    }
                  ]
                }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### PATCH /api/plans/:planId/days/:date
Update the status of a day.

**Request body:**
```json
{ "status": "completed" | "skipped" | "pending" }
```

**Response:** `{ "success": true }`

---

## Session Logs

### GET /api/session-logs?planId=&sessionId=
Fetch a single session log + prefill suggestions.

**Response:**
```json
{
  "log": {
    "id": "uuid",
    "planId": "uuid",
    "sessionId": "uuid",
    "dayDate": "2026-02-27",
    "sessionType": "strength",
    "strengthSets": [
      {
        "exerciseName": "Squat",
        "exerciseKey": "squat",
        "setIndex": 0,
        "reps": 5,
        "weightKg": 100
      }
    ],
    "runDistanceKm": null,
    "runDurationSeconds": null,
    "notes": null,
    "updatedAt": "2026-02-27T10:00:00.000Z"
  },
  "prefill": {
    "strengthSets": [
      {
        "exerciseName": "Squat",
        "exerciseKey": "squat",
        "suggestedWeightKg": 95.0,
        "source": "calculated_1rm" | "previous_log" | "none"
      }
    ],
    "runDistanceKm": null
  }
}
```

`log` is `null` if no log exists yet.

### GET /api/session-logs?planId=&dayDate=
Fetch all session logs for a day.

**Response:**
```json
{
  "logs": [ /* array of log objects (same shape as above, no prefill) */ ]
}
```

### PUT /api/session-logs
Upsert a session log (create or update). Also auto-updates exercise 1RMs if Epley-implied max exceeds current stored value.

**Request body:**
```json
{
  "planId": "uuid",
  "sessionId": "uuid",
  "dayDate": "2026-02-27",
  "sessionType": "strength",
  "strengthSets": [
    {
      "exerciseName": "Squat",
      "exerciseKey": "squat",
      "setIndex": 0,
      "reps": 5,
      "weightKg": 100
    }
  ],
  "runDistanceKm": null,
  "runDurationSeconds": null,
  "notes": "Felt strong"
}
```

All fields except `planId`, `sessionId`, `dayDate`, `sessionType` are optional/nullable.

**StrengthSetLog shape:**
```typescript
{
  exerciseName: string    // display name from plan
  exerciseKey: string     // normalised (lowercase, trimmed, spaces→underscores)
  setIndex: number        // 0-based
  reps: number | null
  weightKg: number | null
}
```

**Response:** `{ "log": { ...logObject } }`

---

## Exercise Maxes (1RMs)

### GET /api/exercise-maxes
Returns all stored 1RMs for the user.

**Response:**
```json
{
  "maxes": [
    {
      "exerciseKey": "squat",
      "displayName": "Squat",
      "oneRepMaxKg": 120.0,
      "updatedAt": "2026-02-20T09:00:00.000Z"
    }
  ]
}
```

### POST /api/exercise-maxes
Create or update a 1RM.

**Request body:**
```json
{
  "displayName": "Squat",
  "oneRepMaxKg": 120.0
}
```

**Response:** `{ "max": { ...maxObject } }`

---

## API Keys

### GET /api/api-keys
List active (non-revoked) API keys for the user.

**Response:**
```json
{
  "keys": [
    {
      "id": "uuid",
      "name": "My Claude Code",
      "createdAt": "2026-02-01T12:00:00.000Z",
      "lastUsedAt": "2026-02-27T08:30:00.000Z"
    }
  ]
}
```

### POST /api/api-keys
Create a new API key. The raw key is returned **once** — store it immediately.

**Request body:** `{ "name": "My Claude Code" }`

**Response:**
```json
{
  "key": "htp_a1b2c3d4...",
  "id": "uuid",
  "name": "My Claude Code",
  "createdAt": "2026-02-27T12:00:00.000Z"
}
```

### DELETE /api/api-keys/:id
Revoke a key. Immediate effect — any subsequent request with this key returns 401.

**Response:** `{ "success": true }`
