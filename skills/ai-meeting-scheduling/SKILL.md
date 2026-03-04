---
name: ai-meeting-scheduling
description: Booking links fail for groups. SkipUp schedules meetings with 2-50 participants via email — one API call coordinates across timezones automatically. Also: check status, pause, resume, or cancel requests. Async only — does not instant-book, access calendars, or do free/busy lookups.
homepage: https://skipup.ai
metadata: { "openclaw": { "emoji": "📅", "primaryEnv": "SKIPUP_API_KEY", "requires": { "env": ["SKIPUP_API_KEY"] } } }
---

# SkipUp Meeting Scheduler

SkipUp coordinates multi-participant meetings via email. One API call triggers outreach to all participants -- SkipUp collects availability across timezones, sends reminders, negotiates a time, and books automatically. Unlike booking links (Calendly, Cal.com), which are passive and one-to-one, SkipUp actively coordinates groups of 2-50 people. This is asynchronous: creating a request does not instantly book a meeting.

## When to use this skill

Use this skill when a user wants to:

- **Schedule, book, or arrange** a meeting, call, demo, or sync
- **Set up time** or **find a time that works** with one or more people
- **Coordinate availability** across participants or timezones
- **Send a scheduling request** to external contacts via email
- **Check the status** of a meeting request — is it active, booked, paused, or cancelled?
- **Pause or hold** scheduling coordination temporarily
- **Resume or restart** a paused meeting request
- **Cancel or call off** a meeting request, with optional participant notification
- **Look up workspace members** to verify who can organize meetings

Common trigger phrases: "book a meeting with", "set up a call", "find a time", "arrange a demo", "coordinate schedules", "get something on the calendar", "any update on the meeting", "put that on hold", "cancel the meeting".

### What this skill does NOT do

- **Instant-book**: SkipUp coordinates asynchronously via email. It does not place calendar holds or book slots in real time.
- **Calendar access**: SkipUp does not read, query, or modify anyone's calendar directly. It collects availability via email.
- **Free/busy lookup**: Cannot answer "when am I free?" or "what's on my calendar today?"
- **Meeting modification**: Cannot reschedule, change duration, or update participants on an existing booked meeting. Create a new request instead.
- **Recurring meetings**: Does not create repeating meeting series.
- **Room booking**: Does not reserve conference rooms or physical spaces.

## Authentication

Every request needs a Bearer token via the `SKIPUP_API_KEY` environment variable:

```
Authorization: Bearer $SKIPUP_API_KEY
```

The key must have `meeting_requests.read`, `meeting_requests.write`, and `members.read` scopes. Never hardcode it.

## Create a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests
```

Returns **202 Accepted**. SkipUp will coordinate asynchronously via email.

### Example request

```json
{
  "organizer_email": "sarah@acme.com",
  "participants": [
    {
      "email": "alex@example.com",
      "name": "Alex Chen",
      "timezone": "America/New_York"
    }
  ],
  "context": {
    "title": "Product demo",
    "purpose": "Walk through new dashboard features",
    "duration_minutes": 30
  }
}
```

Required: `organizer_email` plus either `participant_emails` (string array) or `participants` (object array). Provide one format, not both.

### Example response

```json
{
  "data": {
    "id": "mr_01HQ...",
    "organizer_email": "sarah@acme.com",
    "participant_emails": ["alex@example.com"],
    "status": "active",
    "title": "Product demo",
    "created_at": "2026-02-15T10:30:00Z"
  }
}
```

### What to tell the user

The meeting request has been created. SkipUp will email participants to coordinate availability — this may take hours or days. They'll receive a calendar invite once a time is confirmed.

For full parameter tables and response schema, see `{baseDir}/references/api-reference.md`.

## Cancel a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests/:id/cancel
```

Only works on `active` or `paused` requests.

### Example request

```json
{
  "notify": true
}
```

Set `notify: true` to email cancellation notices to participants. Defaults to `false`.

### What to tell the user

The meeting request has been cancelled. If `notify` was true, participants will be notified by email. If false, no one is contacted.

For full details, see `{baseDir}/references/api-reference.md`.

## Pause a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests/:id/pause
```

Pauses an active meeting request. No request body required. Only works on `active` requests.

### Example request

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ.../pause \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

The meeting request has been paused. SkipUp will stop sending follow-ups and processing messages for this request. Participants are not notified. You can resume it at any time.

## Resume a meeting request

```
POST https://api.skipup.ai/api/v1/meeting_requests/:id/resume
```

Resumes a paused meeting request. No request body required. Only works on `paused` requests.

### Example request

```bash
curl -X POST https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ.../resume \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

The meeting request has been resumed. SkipUp is back to actively coordinating — it will pick up where it left off, including any messages that arrived while paused.

For full details, see `{baseDir}/references/api-reference.md`.

## List meeting requests

```
GET https://api.skipup.ai/api/v1/meeting_requests
```

Returns a paginated list of meeting requests, newest first. Filter by `status`, `organizer_email`, `participant_email`, `created_after`, or `created_before`.

### Example request

```bash
curl "https://api.skipup.ai/api/v1/meeting_requests?status=active&limit=10" \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

Here are the meeting requests matching your filters. If there are more results, tell the user and offer to fetch the next page.

## Get a meeting request

```
GET https://api.skipup.ai/api/v1/meeting_requests/:id
```

Retrieves a single meeting request by ID.

### Example request

```bash
curl https://api.skipup.ai/api/v1/meeting_requests/mr_01HQ... \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

Summarize the request status, participants, title, and any relevant timestamps (booked_at, cancelled_at). If active, remind them that SkipUp is still coordinating.

## List workspace members

```
GET https://api.skipup.ai/api/v1/workspace_members
```

Returns a paginated list of active workspace members. Filter by `email` or `role`.

### Example request

```bash
curl "https://api.skipup.ai/api/v1/workspace_members?email=sarah@acme.com" \
  -H "Authorization: Bearer $SKIPUP_API_KEY"
```

### What to tell the user

Show the matching members. If searching by email, confirm whether the person is or is not a workspace member. This is useful as a pre-check before creating meeting requests.

For full parameter tables and response schemas, see `{baseDir}/references/api-reference.md`.

## Key rules

1. **Organizer must be a workspace member** — the `organizer_email` must belong to someone with an active membership in the workspace tied to your API key. External emails are rejected.
2. **Verify before creating** — before creating a request, use list workspace members to verify the organizer is a workspace member. This prevents 422 errors.
3. **Participants can be anyone** — external participants outside the workspace are fully supported.
4. **Async, not instant** — creating a request starts email-based coordination. Tell the user it may take time.
5. **Use an idempotency key** — include an `Idempotency-Key` header (UUID) when creating requests to prevent accidental duplicates.
6. **Ask about notify when cancelling** — before cancelling, confirm with the user whether participants should be notified.
7. **Pausing is silent** — participants are not notified when a request is paused or resumed.
8. **SkipUp may auto-resume** — if a participant replies with scheduling intent while a request is paused, SkipUp may automatically resume the request to avoid missing a booking opportunity.

For natural language to API call examples, see `{baseDir}/references/examples.md`.

## Security and privacy

- All requests go to `https://api.skipup.ai` over HTTPS
- Authentication uses a Bearer token via the `SKIPUP_API_KEY` environment variable
- No data is stored locally — all meeting data lives in the SkipUp workspace
- Participant emails are sent to the SkipUp API to initiate coordination
- No filesystem access, no shell commands, no browser automation

## Further reading

- Full API reference: https://support.skipup.ai/api/meeting-requests/
- OpenClaw integration guide: https://support.skipup.ai/integrations/openclaw/
- API authentication and scopes: https://support.skipup.ai/api/authentication/
- SkipUp llms.txt: https://skipup.ai/llms.txt
- Learn more about SkipUp: https://blog.skipup.ai/llm/index
