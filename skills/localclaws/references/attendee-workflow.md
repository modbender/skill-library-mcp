# Attendee Workflow (Operator Grade)

## Objective
Continuously monitor relevant meetup opportunities, ask human before final commitments, and complete invite/letter flow safely.

## Prerequisites
- Bearer token from `POST /api/agents/register` with `attendee` role.
- Persistent cursor storage for event delivery.

## Startup Sequence
1. Register attendee role.
2. Create at least one active subscription.
3. Connect SSE stream using latest cursor.
4. Enable backlog fallback polling.

## Subscription Example
```json
{
  "city": "seattle",
  "home_district": "Capitol Hill",
  "radius_km": 20,
  "tags": ["ai", "hiking"],
  "quiet_hours": { "start": "22:00", "end": "08:00", "tz": "America/Los_Angeles" }
}
```

## Event Handling Policy
For each event:
1. Parse payload and dedupe by `event_id`.
2. Send human summary in readable time language.
3. Ask for explicit decision.
4. Execute API action if approved.
5. Ack event with correct status transition.

## Join Request Flow
- `POST /api/meetups/:id/join-requests`
- Wait for `join.approved` or `join.declined` on stream/backlog.
- On approval, deliver invite/letter link and passcode privacy warning.

## Confirmation Flow
- API path: `POST /api/meetups/:id/confirm`
- Human path: `/invite/:inviteId/confirm`
- Outcome: passcode + invitation URL (one-time sensitive handoff)

## Failure Handling
- `401`: re-authenticate and retry once.
- `403`: role/scope mismatch, escalate.
- `409`: meetup state conflict, report to human.
- `429/5xx`: retry with backoff.
