# Traffic & Abuse Control Plan — Swaps Intel Public Beta

## Objectives
- Measure source-to-query conversion per channel
- Detect abuse early
- Keep infra cost predictable
- Preserve investigation quality signals

## Tracking Model
### Channel tags (required)
- ClawHub skill: `src=clawhub`
- ChatGPT mini app: `src=chatgpt-miniapp`
- Telegram bot: `src=telegram-bot`
- Telegram mini app: `src=telegram-miniapp`
- iOS app: `src=ios-app`

### Event schema (minimum)
- `event_name`: request_received | request_blocked | request_scored | report_opened | rate_limited
- `source`: one of tags above
- `api_key_id` (nullable)
- `anon_fingerprint` (hashed)
- `address_hash` (hashed)
- `risk_bucket` (low/medium/high/critical)
- `latency_ms`
- `status_code`
- `timestamp`

## Quotas & Limits (beta defaults)
- Anonymous app/web: 3 checks/day per user/device fingerprint
- Free API key: 50 checks/month
- Burst control: 5 req/min/key, 2 req/min/fingerprint
- Hard cutoff: 429 with clear retry window

## Abuse Heuristics
Flag if any:
- High-frequency probing across many random addresses
- Repeated sanctioned-entity scans from same fingerprint/key
- Distinct addresses > threshold in short window
- Invalid-auth storm / key enumeration patterns

## Enforcement Actions
1. Soft throttle + warning banner
2. Temporary block (15m / 1h)
3. Key revoke + manual review queue

## Dashboards (daily)
- Requests by source
- Unique users/keys by source
- 429 rate by source
- High-risk hit rate by source
- Top abuse fingerprints/keys

## Alerts
- 429 spike > 3x baseline in 15m
- Error rate > 2%
- One key consuming > 20% daily volume
- Suspicious pattern spike from single source

## Public Beta Banner Copy
"Public beta: community-built analytics tool. Signals may be incomplete. Use with independent verification."
