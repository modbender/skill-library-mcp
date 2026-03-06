# Failure Taxonomy

Every non-2xx response uses the error envelope: `{ "error": { "code": "STRING_CODE", "message": "...", "details": {} } }`. Always parse `code`, never `message`.

## Error classification: retry vs fix vs stop

### Retryable (same idempotency key, same payload)

| Status | Code | What happened | Action |
|---|---|---|---|
| 5xx | (any) | Server error | Retry with same key, exponential backoff (2s, 4s, 8s), max 3 attempts |
| timeout | — | Request didn't complete | Retry with same key immediately |

### Fixable (new idempotency key, adjusted payload)

| Status | Code | What happened | Action |
|---|---|---|---|
| 402 | `credits_exhausted` | Not enough credits | Purchase credits using `credit_pack_options` from the error response, then retry with new key |
| 402 | `budget_cap_exceeded` | Search budget too low for results | Increase `budget.credits_requested`, retry with new key. `credit_pack_options` included if balance is also low |
| 409 | `stale_write_conflict` | Someone else modified the resource | Re-read resource, get new `version`, retry PATCH with new key |
| 409 | `idempotency_key_reuse_conflict` | Same key used with different payload | Generate a new key, retry |
| 422 | `validation_error` | Payload doesn't match schema | Fix per `details` field, retry with new key |
| 422 | `legal_required` | Legal assent missing or outdated | Read `required_legal_version` from `/v1/meta`, assent, retry |
| 422 | `content_contact_info_disallowed` | Contact info detected in text fields | Remove emails, phones, handles from text, retry with new key |
| 429 | `rate_limit_exceeded` | Too many requests | Wait for `Retry-After` seconds, then retry with same key |

### Non-retryable (stop and re-evaluate)

| Status | Code | What happened | Action |
|---|---|---|---|
| 401 | `unauthorized` | Bad or revoked API key | Re-check key; if lost, use recovery flow |
| 403 | `forbidden` | Node suspended or key revoked | Check node status via recovery; contact support |
| 404 | `not_found` | Resource doesn't exist | Verify the ID; the resource may have been deleted |
| 409 | `invalid_state_transition` | Offer is in a terminal state | Re-read the offer to see current status; likely already accepted/rejected/expired |
| 429 | `prepurchase_daily_limit_exceeded` | Pre-purchase limits active | Make any purchase (subscription or credit pack) to permanently remove these limits. `purchase_options` is included in the response. |

## Decision tree for errors

```
Got an error?
├─ Is it 5xx or timeout?
│  └─ YES → Retry with SAME idempotency key, exponential backoff, max 3x
├─ Is it 401?
│  └─ YES → STOP. Your key is invalid. Re-bootstrap or recover.
├─ Is it 402?
│  └─ YES → Read credit_pack_options from error. Purchase credits. Retry.
├─ Is it 409?
│  ├─ idempotency_key_reuse_conflict → New key + retry
│  ├─ stale_write_conflict → Re-read, new key + new If-Match, retry
│  └─ invalid_state_transition → Re-read offer, adapt strategy
├─ Is it 422?
│  ├─ validation_error → Fix payload per details, new key + retry
│  ├─ legal_required → Assent to current legal version, retry
│  └─ content_contact_info_disallowed → Remove contact info, retry
└─ Is it 429?
   ├─ rate_limit_exceeded → Wait Retry-After seconds, retry
   └─ prepurchase_daily_limit_exceeded → Purchase something, retry
```

## Credit management

### When you're running low

The 402 error response includes ready-to-use `credit_pack_options`:

```json
{
  "error": {
    "code": "credits_exhausted",
    "details": {
      "credits_required": 5,
      "credits_balance": 2,
      "credit_pack_options": {
        "stripe": [ { "pack_code": "500", "credits": 500, "price": "$9.99", ... } ],
        "crypto": [ { "pack_code": "500", "credits": 500, ... } ]
      }
    }
  }
}
```

Use the `stripe` or `crypto` options directly — they include pre-filled request bodies.

### Proactive credit monitoring

Check your balance before expensive operations:
```
GET /v1/credits/balance
```

If balance < 50 credits and you have more work to do, purchase proactively rather than hitting 402 mid-workflow.

## Bounded retry policy

For any operation:

```
max_retries = 3
backoff = [2000ms, 4000ms, 8000ms]

for attempt in 1..max_retries:
  response = make_request(...)
  if response.ok: return response
  if not retryable(response.status): return error(response)
  sleep(backoff[attempt - 1])
return give_up(last_response)
```

After 3 retries: log the failure, surface it to your operator, and move on. Don't loop forever.
