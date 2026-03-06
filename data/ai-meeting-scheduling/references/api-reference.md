# API reference

Base URL: `https://api.skipup.ai/api/v1`

All requests require a Bearer token:

```
Authorization: Bearer $SKIPUP_API_KEY
```

The key must have `meeting_requests.read`, `meeting_requests.write`, and `members.read` scopes.

For the complete API reference including webhooks, workspace member management, and advanced workflows, see https://support.skipup.ai/api/meeting-requests/

---

## Create a meeting request

```
POST /meeting_requests
```

Returns **202 Accepted**. The meeting is not booked yet — SkipUp coordinates asynchronously via email.

### Required parameters

| Field | Type | Description |
|---|---|---|
| `organizer_email` | string | Email of the organizer. Must be an active workspace member. |
| `participant_emails` **or** `participants` | string[] or object[] | Who to invite. Provide one format, not both. |

The `participants` array accepts richer objects:

```json
{ "email": "alex@example.com", "name": "Alex Chen", "timezone": "America/New_York" }
```

- `email` (string, required) — participant's email address
- `name` (string, optional) — display name
- `timezone` (string, optional) — IANA timezone identifier

### Optional parameters

| Field | Type | Constraints | Description |
|---|---|---|---|
| `organizer_name` | string | | Display name for the organizer |
| `organizer_timezone` | string | IANA timezone | Organizer's timezone (e.g. `America/Los_Angeles`) |
| `include_introduction` | boolean | | When true, the AI composes a warm introduction in the outreach. Defaults to false |
| `context.title` | string | | Meeting title |
| `context.purpose` | string | | Why the meeting is happening |
| `context.description` | string | | Free-text instructions for the AI (e.g. CRM notes, tone guidance) |
| `context.duration_minutes` | number | | Desired meeting length in minutes |
| `context.timeframe.start` | string | ISO 8601 datetime | Earliest acceptable meeting time |
| `context.timeframe.end` | string | ISO 8601 datetime | Latest acceptable meeting time |

### Response schema (202 Accepted)

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "sarah@acme.com",
    "participant_emails": ["alex@example.com", "priya@example.com"],
    "status": "active",
    "title": "Product demo walkthrough",
    "purpose": "Show the new dashboard features",
    "description": null,
    "include_introduction": true,
    "duration_minutes": 30,
    "timeframe": {
      "start": "2026-02-16T00:00:00Z",
      "end": "2026-02-20T23:59:59Z"
    },
    "created_at": "2026-02-15T10:30:00Z",
    "updated_at": "2026-02-15T10:30:00Z",
    "booked_at": null,
    "cancelled_at": null,
    "paused_at": null
  }
}
```

All response fields:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique request identifier (prefixed `mr_`) |
| `organizer_email` | string | Organizer's email |
| `participant_emails` | string[] | Normalized list of participant emails |
| `status` | string | Current status (see Status lifecycle below) |
| `title` | string \| null | Meeting title |
| `purpose` | string \| null | Meeting purpose |
| `description` | string \| null | Additional details |
| `include_introduction` | boolean | Whether introductions are enabled |
| `duration_minutes` | number \| null | Requested duration |
| `timeframe` | object \| null | `{ start, end }` ISO 8601 datetimes |
| `created_at` | string | ISO 8601 creation timestamp |
| `updated_at` | string | ISO 8601 last-updated timestamp |
| `booked_at` | string \| null | When the meeting was booked |
| `cancelled_at` | string \| null | When the request was cancelled |
| `paused_at` | string \| null | When the request was paused |

### Idempotency

Include an `Idempotency-Key` header with a unique string (e.g. a UUID) to safely retry requests without creating duplicates. Cached responses are stored for 24 hours. If you retry a request with the same key within that window, the API returns the original response without creating a new meeting request.

```
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

---

## Cancel a meeting request

```
POST /meeting_requests/:id/cancel
```

Cancels an active or paused meeting request. Requests that are already `booked` or `cancelled` cannot be cancelled (returns 422).

### Parameters

| Field | Type | Default | Description |
|---|---|---|---|
| `notify` | boolean | `false` | Send cancellation emails to all participants |

### Response schema

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "sarah@acme.com",
    "participant_emails": ["alex@example.com", "priya@example.com"],
    "status": "cancelled",
    "cancelled_at": "2026-02-15T14:00:00Z",
    "created_at": "2026-02-15T10:30:00Z",
    "updated_at": "2026-02-15T14:00:00Z"
  }
}
```

---

## Pause a meeting request

```
POST /meeting_requests/:id/pause
```

Pauses an active meeting request. While paused, SkipUp stops processing messages and sending follow-ups on this conversation. Incoming messages are still recorded but not acted on. Only requests with status `active` can be paused.

**Scope required:** `meeting_requests.write`

### Parameters

No request body required.

### Response schema

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "alice@example.com",
    "participant_emails": ["bob@example.com"],
    "status": "paused",
    "title": "Project kickoff",
    "purpose": "Discuss Q2 roadmap",
    "duration_minutes": 30,
    "timeframe": {
      "start": "2025-02-01T00:00:00Z",
      "end": "2025-02-14T23:59:59Z"
    },
    "created_at": "2025-01-20T14:30:00Z",
    "updated_at": "2025-01-22T09:00:00Z",
    "paused_at": "2025-01-22T09:00:00Z",
    "booked_at": null,
    "cancelled_at": null
  }
}
```

### Errors

| HTTP Status | Error Type | Cause |
|---|---|---|
| 422 | `invalid_request` | The request is not in `active` status (e.g. "Cannot pause a request that is already paused") |

Pausing is a silent operation — participants are not notified.

---

## Resume a meeting request

```
POST /meeting_requests/:id/resume
```

Resumes a paused meeting request. SkipUp returns the request to `active` status and picks up scheduling where it left off, including reviewing any messages that arrived while the request was paused. Only requests with status `paused` can be resumed.

**Scope required:** `meeting_requests.write`

### Parameters

No request body required.

### Response schema

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "alice@example.com",
    "participant_emails": ["bob@example.com"],
    "status": "active",
    "title": "Project kickoff",
    "paused_at": null,
    "created_at": "2025-01-20T14:30:00Z",
    "updated_at": "2025-01-23T11:00:00Z"
  }
}
```

### Errors

| HTTP Status | Error Type | Cause |
|---|---|---|
| 422 | `invalid_request` | The request is not in `paused` status (e.g. "Cannot resume a request that is not paused") |

If a participant sends a message with scheduling intent while the request is paused, SkipUp may automatically resume the request to avoid missing a booking opportunity.

---

## List meeting requests

```
GET /meeting_requests
```

Returns a paginated list of meeting requests in your workspace, sorted by creation date (newest first).

**Scope required:** `meeting_requests.read`

### Query parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `participant_email` | string | — | Filter by participant email address |
| `organizer_email` | string | — | Filter by organizer email address |
| `status` | string | — | Filter by status: `active`, `paused`, `booked`, or `cancelled` |
| `created_after` | string | — | ISO 8601 timestamp. Only return requests created on or after this time |
| `created_before` | string | — | ISO 8601 timestamp. Only return requests created on or before this time |
| `limit` | integer | `25` | Results per page (1–100) |
| `cursor` | string | — | Cursor for the next page of results |

### Response schema (200 OK)

```json
{
  "data": [
    {
      "id": "mr_01HQ...",
      "organizer_email": "alice@example.com",
      "participant_emails": ["bob@example.com", "carol@example.com"],
      "status": "active",
      "title": "Project kickoff",
      "purpose": "Discuss Q2 roadmap",
      "duration_minutes": 30,
      "timeframe": {
        "start": "2025-02-01T00:00:00Z",
        "end": "2025-02-14T23:59:59Z"
      },
      "created_at": "2025-01-20T14:30:00Z",
      "updated_at": "2025-01-20T14:30:00Z"
    }
  ],
  "meta": {
    "limit": 10,
    "has_more": true,
    "next_cursor": "mr_01HP..."
  }
}
```

### Pagination

To paginate through all results, pass the `next_cursor` value from each response as the `cursor` parameter until `has_more` is `false`.

---

## Get a meeting request

```
GET /meeting_requests/:id
```

Retrieves a single meeting request by ID.

**Scope required:** `meeting_requests.read`

### Response schema (200 OK)

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "alice@example.com",
    "participant_emails": ["bob@example.com"],
    "status": "booked",
    "title": "1:1 sync",
    "duration_minutes": 30,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-16T09:00:00Z",
    "booked_at": "2025-01-16T09:00:00Z"
  }
}
```

The response uses the same meeting request object schema as the create endpoint. See the response fields table above for all fields.

---

## List workspace members

```
GET /workspace_members
```

Returns a paginated list of active workspace members, ordered by most recently added.

**Scope required:** `members.read`

### Member object

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique member ID |
| `email` | string | Member's email address |
| `name` | string | Member's display name |
| `role` | string | Role in the workspace (e.g. `"member"`, `"admin"`) |
| `deactivated_at` | string \| null | ISO 8601 timestamp if deactivated, otherwise `null` |
| `created_at` | string | ISO 8601 timestamp when the member was added |

### Query parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `email` | string | — | Filter by exact email address |
| `role` | string | — | Filter by role |
| `limit` | integer | `25` | Results per page (1–100) |
| `cursor` | string | — | Cursor for the next page of results |

### Response schema (200 OK)

```json
{
  "data": [
    {
      "id": "mem_01H...",
      "email": "alice@example.com",
      "name": "Alice Johnson",
      "role": "admin",
      "deactivated_at": null,
      "created_at": "2025-01-10T09:00:00Z"
    },
    {
      "id": "mem_02H...",
      "email": "bob@example.com",
      "name": "Bob Smith",
      "role": "member",
      "deactivated_at": null,
      "created_at": "2025-01-08T14:30:00Z"
    }
  ],
  "meta": {
    "limit": 25,
    "has_more": false
  }
}
```

### Pagination

To paginate through all results, pass the `next_cursor` value from each response as the `cursor` parameter until `has_more` is `false`.

---

## Status lifecycle

| Status | Meaning | Transitions to |
|---|---|---|
| `active` | SkipUp is coordinating availability with participants | `booked`, `cancelled`, `paused` |
| `booked` | Meeting time found, calendar invites sent | (terminal) |
| `paused` | Coordination temporarily paused | `active`, `cancelled` |
| `cancelled` | Request was cancelled before booking | (terminal) |

Only `active` and `paused` requests can be cancelled via the API.

---

## Error codes

All errors return:

```json
{
  "error": {
    "type": "error_type",
    "message": "Human-readable description"
  }
}
```

| HTTP Status | Error Type | Cause | What to do |
|---|---|---|---|
| 401 | `unauthorized` | Missing or invalid API key | Check `SKIPUP_API_KEY` is set and valid |
| 403 | `forbidden` | API key lacks required scope | Ensure key has the required scope (`meeting_requests.read`, `meeting_requests.write`, or `members.read`) |
| 404 | `not_found` | Meeting request ID does not exist | Verify the request ID |
| 422 | `invalid_request` | Invalid parameters or cannot perform action in current state | Check request body and meeting request status |
| 422 | `validation_error` | Field validation failed (e.g. organizer not a workspace member) | Verify organizer is a workspace member |
| 429 | `rate_limited` | Exceeded rate limit | Wait and retry. Limit: 120 requests per minute |

---

## Rate limits

The API allows **120 requests per minute** per API key. Exceeding this returns a 429 status code. Use exponential backoff when retrying.
