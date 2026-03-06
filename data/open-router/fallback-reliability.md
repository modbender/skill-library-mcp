# Fallback Reliability — Open Router

## Failure Modes to Plan For

- Rate limit responses during traffic spikes.
- Provider-side outages or degraded regions.
- Latency spikes that breach user expectations.
- Quality regressions after model updates.

## Fallback Policy Design

| Trigger | Immediate Action | Follow-up |
|---------|------------------|-----------|
| Rate limit | Retry once with jitter, then fallback | Log event and adjust burst policy |
| Timeout | Fallback to lower-latency model | Record latency threshold breach |
| Repeated format failure | Switch to more deterministic model | Tighten prompt constraints |
| Provider outage | Route to different provider family | Mark incident and recovery time |

## Reliability Rules

1. Avoid infinite retries; cap attempts and fail forward.
2. Keep at least two independent routing paths for critical workloads.
3. Separate reliability fallback from cost optimization fallback.
4. Record incident fingerprints so repeated outages are recognized quickly.

## Quick Health Check

```bash
curl -sS https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer ${OPENROUTER_API_KEY}" \
  -H "Content-Type: application/json" | jq '.data[0].id'
```

If this fails consistently, avoid changing routing policy until connectivity and auth are confirmed.
