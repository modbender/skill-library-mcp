---
name: lead-storage
description: "Persist validated lead objects through write-only storage operations after Supervisor provides explicit confirmation. Use when users ask to save approved leads to Google Sheets or DB, including normalized location and priority fields. Recommended chain end: supervisor confirmation then lead-storage. Do not use for parsing, extraction, analytics, or action recommendation."
---

# Lead Storage

Store validated leads with strict confirmation gating.

## Quick Triggers

- Save approved leads to Google Sheets.
- Persist these normalized records after confirmation.
- Commit validated leads with confirmation token.

## Recommended Chain

`... -> supervisor confirmation -> lead-storage`

## Execute Workflow

1. Accept payload from Supervisor.
2. Validate payload with `references/storage-input.schema.json`.
3. Verify `confirmation_token` is present and non-empty.
4. Write leads to storage through write-only interfaces.
5. Preserve optional extraction/normalization/scoring metadata when present:
   - extraction: `deal_type`, `asset_class`, `price_basis`, `area_sqft`, `area_basis`
   - record typing: `dataset_mode`, `record_type`
   - location: `city`, `city_canonical`, `locality_canonical`, `micro_market`, `location_hint`
   - prioritization: `urgency`, `priority_bucket`
6. Enforce idempotency by `lead_id` and avoid duplicate inserts for repeated broker forwards.
7. Return result using `references/storage-output.schema.json`.
8. On partial failures, return `status: "failure"` and a populated `error_message`.

## Enforce Boundaries

- Never parse raw messages.
- Never extract new lead entities.
- Never perform read queries for analytics or summaries.
- Never generate suggested actions.
- Never write anything when confirmation token is missing or invalid.
- Never self-approve writes.

## Reliability Rules

1. Prefer idempotent writes keyed by `lead_id`.
2. Log rejected writes with validation reason.
3. Fail closed on any permission ambiguity.
