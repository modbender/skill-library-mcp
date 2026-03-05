# Call Control and Anti-Abuse

Use a local gate in front of Brek API. Do not rely only on upstream limits.

## Recommended default limits

Apply all limits together:
- Per `actorId`: max 12 `/events` calls per minute.
- Per `actorId`: max 200 `/events` calls per day.
- Per partner key: max 3000 total calls per day.
- Concurrent in-flight calls per `actorId`: max 2.
- Maximum active sessions per `actorId` per 24h: 3.

Tune these numbers by real traffic and budget.

## Retry policy

- On `429`: respect `retry-after`; then retry with exponential backoff and jitter.
- On timeouts/`5xx`: retry at most 2 times.
- On `400/401/403/404/409`: no blind retry.

## Circuit breaker

Open breaker when either condition is met:
- 5 failures in 60 seconds for same partner key.
- 50%+ failure ratio over last 20 requests.

During open breaker:
- Reject new writes for 60 seconds.
- Allow only a small probe flow (for example, 1 request every 10 seconds).

## Idempotency policy

For write-like kinds, persist a dedupe record:
- Key: `partnerId + sessionId + kind + clientActionId`
- TTL: 24 hours
- If duplicate key appears, return cached outcome or block duplicate call.

## Budget kill switch

Track estimated spend and enforce hard stop:
- Daily budget per partner key (USD).
- Monthly budget per partner key (USD).
- Trigger alert at 70%, 85%, 100%.
- At 100%, deny write-like events and require operator override.
