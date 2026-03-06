# Event Updates for Pull-Based CallMyCall

CallMyCall usage in this skill is currently pull-based. To support event-like updates in OpenClaw (for example, "call completed"), use one of the following patterns.

## Option 1: In-session polling loop

How it works:
- After `start-call`, poll `GET /v1/calls/:callId` every N seconds while session is active.
- Emit updates when status changes (`queued` -> `ringing` -> `in-progress` -> `completed|failed|canceled`).

Pros:
- No external infrastructure.
- Fast to implement.

Cons:
- Only works while the chat/session is active.
- Adds API traffic and local timers.

Best for:
- MVP and interactive operator workflows.

## Option 2: Scheduled background poller (cron/job)

How it works:
- Persist active call IDs in a durable store.
- Run a cron job (for example every 15-60 seconds) that polls status and writes events to an OpenClaw-visible event table/queue.

Pros:
- Works even when user is offline.
- Operationally simple compared to realtime infra.

Cons:
- Not truly realtime.
- Requires scheduler + durable storage.

Best for:
- Production deployments that need reliability without websocket complexity.

## Option 3: Websocket bridge service

How it works:
- Bridge polls CallMyCall or consumes upstream events.
- Pushes normalized call events over websocket/SSE to OpenClaw clients.

Pros:
- Near-realtime UX.
- Good fit for live dashboards.

Cons:
- Stateful service complexity.
- Connection lifecycle and auth management required.

Best for:
- Multi-user live operations consoles.

## Option 4: Webhook relay service (if/when webhooks enabled)

How it works:
- Configure CallMyCall webhook/webhook_events (if available in account setup).
- Receive callbacks in a relay service, validate signatures, transform payloads, and forward internal events to OpenClaw.

Pros:
- Event-driven and efficient.
- Lowest polling overhead.

Cons:
- Public endpoint and secure webhook handling required.
- Depends on webhook availability and reliability.

Best for:
- Mature production event pipelines.

## Recommended rollout

1. Start with Option 1 for immediate UX improvements.
2. Move to Option 2 for durable production behavior.
3. Add Option 4 when webhook support is confirmed and operational controls are ready.
4. Use Option 3 only if realtime push UX is a hard requirement.

## Event model (common across options)

Normalize emitted events to a stable schema:

```json
{
  "eventType": "call.status.changed",
  "callSid": "CA...",
  "previousStatus": "in-progress",
  "currentStatus": "completed",
  "timestamp": "2026-02-18T12:00:00Z",
  "source": "poller|webhook|bridge",
  "metadata": {}
}
```

This lets OpenClaw consume a single event contract regardless of transport.
