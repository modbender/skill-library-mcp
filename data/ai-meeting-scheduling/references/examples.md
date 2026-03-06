# Examples: natural language to API calls

These examples show how to translate user requests into SkipUp API calls.

---

## 1. Simple 1:1 meeting

**User says:** "Schedule a 30-minute meeting with bob@example.com to discuss the proposal"

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests \
  -H "Authorization: Bearer $SKIPUP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "organizer_email": "user@workspace.com",
    "participant_emails": ["bob@example.com"],
    "context": {
      "title": "Proposal discussion",
      "purpose": "Discuss the proposal",
      "duration_minutes": 30
    }
  }'
```

**Response (202 Accepted):**

```json
{
  "data": {
    "id": "mr_01HA...",
    "organizer_email": "user@workspace.com",
    "participant_emails": ["bob@example.com"],
    "status": "active",
    "title": "Proposal discussion",
    "created_at": "2026-02-15T09:00:00Z",
    "updated_at": "2026-02-15T09:00:00Z"
  }
}
```

**What to tell the user:** "I've created a meeting request with bob@example.com to discuss the proposal. SkipUp will email Bob to find a 30-minute slot that works for both of you. You'll get a calendar invite once a time is confirmed."

---

## 2. Multi-participant with rich context

**User says:** "Set up a product demo with the Acme team next week — invite alex@acme.com and priya@acme.com"

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests \
  -H "Authorization: Bearer $SKIPUP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "organizer_email": "user@workspace.com",
    "participants": [
      { "email": "alex@acme.com", "name": "Alex" },
      { "email": "priya@acme.com", "name": "Priya" }
    ],
    "include_introduction": true,
    "context": {
      "title": "Product demo for Acme",
      "purpose": "Walk through product features with the Acme team",
      "duration_minutes": 45,
      "timeframe": {
        "start": "2026-02-16T00:00:00Z",
        "end": "2026-02-20T23:59:59Z"
      }
    }
  }'
```

**Response (202 Accepted):**

```json
{
  "data": {
    "id": "mr_01HB...",
    "organizer_email": "user@workspace.com",
    "participant_emails": ["alex@acme.com", "priya@acme.com"],
    "status": "active",
    "title": "Product demo for Acme",
    "created_at": "2026-02-15T11:00:00Z",
    "updated_at": "2026-02-15T11:00:00Z"
  }
}
```

**What to tell the user:** "I've set up a product demo with Alex and Priya from Acme for next week. SkipUp will email both of them to coordinate availability and book a 45-minute slot. I've included introductions so SkipUp will introduce everyone in the initial email."

---

## 3. Cross-timezone with timeframe

**User says:** "Book a meeting between our Tokyo and NYC offices for Q2 planning — invite kenji@workspace.com and maria@workspace.com"

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests \
  -H "Authorization: Bearer $SKIPUP_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: $(uuidgen)" \
  -d '{
    "organizer_email": "user@workspace.com",
    "participants": [
      { "email": "kenji@workspace.com", "name": "Kenji", "timezone": "Asia/Tokyo" },
      { "email": "maria@workspace.com", "name": "Maria", "timezone": "America/New_York" }
    ],
    "context": {
      "title": "Q2 planning — Tokyo + NYC",
      "purpose": "Cross-office Q2 planning session",
      "duration_minutes": 60,
      "timeframe": {
        "start": "2026-04-01T00:00:00Z",
        "end": "2026-04-15T23:59:59Z"
      }
    }
  }'
```

**Response (202 Accepted):**

```json
{
  "data": {
    "id": "mr_01HC...",
    "organizer_email": "user@workspace.com",
    "participant_emails": ["kenji@workspace.com", "maria@workspace.com"],
    "status": "active",
    "title": "Q2 planning — Tokyo + NYC",
    "created_at": "2026-02-15T14:00:00Z",
    "updated_at": "2026-02-15T14:00:00Z"
  }
}
```

**What to tell the user:** "I've created a meeting request for Q2 planning with Kenji (Tokyo) and Maria (NYC). SkipUp will factor in both timezones when finding a 60-minute slot in the first two weeks of April. You'll get a calendar invite once everyone's availability is collected."

---

## 4. Cancel with notification

**User says:** "Cancel meeting mr_01HQ... and let everyone know"

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ.../cancel \
  -H "Authorization: Bearer $SKIPUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "notify": true
  }'
```

**Response:**

```json
{
  "data": {
    "id": "mr_01HQ...",
    "status": "cancelled",
    "cancelled_at": "2026-02-15T16:00:00Z"
  }
}
```

**What to tell the user:** "Done — I've cancelled the meeting request and all participants will be notified by email."

---

## 5. Cancel without notification

**User says:** "Cancel the pending meeting with the design team, no need to notify anyone"

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HD.../cancel \
  -H "Authorization: Bearer $SKIPUP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "notify": false
  }'
```

**Response:**

```json
{
  "data": {
    "id": "mr_01HD...",
    "status": "cancelled",
    "cancelled_at": "2026-02-15T17:30:00Z"
  }
}
```

**What to tell the user:** "The meeting request has been cancelled. Participants won't receive a notification email."

---

## 6. Check the status of a meeting

**User says:** "Check the status of my meeting with Bob — the ID is mr_01HQ..."

**Request:**

```bash
curl https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ... \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

**Response (200 OK):**

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "user@workspace.com",
    "participant_emails": ["bob@example.com"],
    "status": "active",
    "title": "Proposal discussion",
    "duration_minutes": 30,
    "created_at": "2026-02-15T09:00:00Z",
    "updated_at": "2026-02-15T09:00:00Z"
  }
}
```

**What to tell the user:** "Your meeting request with Bob is still active — SkipUp is coordinating availability. The request is for a 30-minute 'Proposal discussion'. You'll get a calendar invite once a time is confirmed."

---

## 7. Show all active meeting requests

**User says:** "Show me all active meeting requests"

**Request:**

```bash
curl "https://api.skipup.ai/api/v1/meeting_requests?status=active" \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

**Response (200 OK):**

```json
{
  "data": [
    {
      "id": "mr_01HA...",
      "organizer_email": "user@workspace.com",
      "participant_emails": ["bob@example.com"],
      "status": "active",
      "title": "Proposal discussion",
      "created_at": "2026-02-15T09:00:00Z",
      "updated_at": "2026-02-15T09:00:00Z"
    },
    {
      "id": "mr_01HB...",
      "organizer_email": "user@workspace.com",
      "participant_emails": ["alex@acme.com", "priya@acme.com"],
      "status": "active",
      "title": "Product demo for Acme",
      "created_at": "2026-02-15T11:00:00Z",
      "updated_at": "2026-02-15T11:00:00Z"
    }
  ],
  "meta": {
    "limit": 25,
    "has_more": false
  }
}
```

**What to tell the user:** "You have 2 active meeting requests: (1) 'Proposal discussion' with bob@example.com, and (2) 'Product demo for Acme' with alex@acme.com and priya@acme.com. SkipUp is still coordinating both."

---

## 8. Verify someone is a workspace member

**User says:** "Is sarah@acme.com a workspace member?"

**Request:**

```bash
curl "https://api.skipup.ai/api/v1/workspace_members?email=sarah@acme.com" \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

**Response (200 OK) — member found:**

```json
{
  "data": [
    {
      "id": "mem_01H...",
      "email": "sarah@acme.com",
      "name": "Sarah Chen",
      "role": "member",
      "deactivated_at": null,
      "created_at": "2025-06-01T10:00:00Z"
    }
  ],
  "meta": {
    "limit": 25,
    "has_more": false
  }
}
```

**What to tell the user:** "Yes, sarah@acme.com is a workspace member (role: member). She can be used as an organizer for meeting requests."

**Response (200 OK) — member not found:**

```json
{
  "data": [],
  "meta": {
    "limit": 25,
    "has_more": false
  }
}
```

**What to tell the user:** "sarah@acme.com is not a workspace member. She can be added as a participant to meeting requests, but cannot be the organizer."

---

## 9. Pause a meeting request

**User says:** "Pause the meeting request with the design team — the ID is mr_01HE..."

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HE.../pause \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

**Response (200 OK):**

```json
{
  "data": {
    "id": "mr_01HE...",
    "organizer_email": "user@workspace.com",
    "participant_emails": ["designer@example.com"],
    "status": "paused",
    "title": "Design review",
    "paused_at": "2026-02-15T15:00:00Z",
    "created_at": "2026-02-14T10:00:00Z",
    "updated_at": "2026-02-15T15:00:00Z"
  }
}
```

**What to tell the user:** "The meeting request with the design team has been paused. SkipUp will stop coordinating until you resume it. Participants are not notified about the pause."

---

## 10. Resume a paused meeting request

**User says:** "Resume the paused meeting with Bob — the ID is mr_01HQ..."

**Request:**

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ.../resume \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

**Response (200 OK):**

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "user@workspace.com",
    "participant_emails": ["bob@example.com"],
    "status": "active",
    "title": "Proposal discussion",
    "paused_at": null,
    "created_at": "2026-02-15T09:00:00Z",
    "updated_at": "2026-02-15T16:00:00Z"
  }
}
```

**What to tell the user:** "The meeting request with Bob has been resumed. SkipUp is back to coordinating — it will review any messages that arrived while the request was paused and continue finding a time."
