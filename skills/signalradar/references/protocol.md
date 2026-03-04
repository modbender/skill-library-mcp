# SignalRadar Protocol Reference

## Contract Versioning

- Add `schema_version` to all top-level objects.
- Do not break existing required fields without major version bump.

## EntrySpec

Required fields:

- `schema_version` (string)
- `entry_id` (string)
- `source` (string)
- `market_id` (string)
- `event_id` (string)
- `slug` (string)
- `status` (`active|inactive|archived`)
- `threshold_policy.abs_pp` (number)
- `created_at` (UTC ISO-8601 string)
- `updated_at` (UTC ISO-8601 string)
- `version` (integer)

Key rule:

- `entry_id = {source}:{market_id}:{slug}:{event_id}`

## SignalEvent

Required fields:

- `schema_version` (string)
- `request_id` (string, UUID recommended)
- `entry_id` (string)
- `source` (string)
- `current` (number)
- `baseline` (number)
- `abs_pp` (number)
- `confidence` (`high|medium|low`)
- `reason` (string)
- `ts` (UTC ISO-8601 string)
- `baseline_ts` (UTC ISO-8601 string)

Optional fields:

- `rel_pct` (number)
- `volume_24h` (number)
- `threshold_abs_pp` (number)
- `threshold_rel_pct` (number)

Default trigger:

- `HIT` when `abs_pp >= threshold.abs_pp`

## IntentSpec

Required fields:

- `schema_version` (string)
- `intent_id` (string)
- `action` (string)
- `entry_ids` (string array)
- `confirmed` (boolean)
- `requested_by` (string)

Required for state mutation:

- `confirmed = true`
- `confirmed_at` (UTC ISO-8601 string)

## DeliveryEnvelope

Required fields:

- `schema_version` (string)
- `delivery_id` (string)
- `request_id` (string)
- `idempotency_key` (string)
- `severity` (`P0|P1|P2`)
- `route.primary` (string)
- `human_text` (string)
- `machine_payload` (object)

Rules:

- Must be safe to retry with same `idempotency_key`.
- Must preserve full traceability via `request_id`.

## Standard Error Envelope

```json
{
  "error_code": "SR_TIMEOUT",
  "message": "Decide step timed out",
  "request_id": "9f98e47e-6e0e-4563-b7c8-87a3b19e97af",
  "retryable": true
}
```

Allowed `error_code` values:

- `SR_VALIDATION_ERROR`
- `SR_SOURCE_UNAVAILABLE`
- `SR_TIMEOUT`
- `SR_ROUTE_FAILURE`
- `SR_CONFIG_CONFLICT`
- `SR_PERMISSION_DENIED`

