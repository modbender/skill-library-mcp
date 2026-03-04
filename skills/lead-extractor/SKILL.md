---
name: lead-extractor
description: "Extract structured real-estate lead records from parsed message objects. Use when users ask to find leads in WhatsApp exports, extract name-phone-budget, or classify listing vs requirement posts. Recommended chain: run after message-parser and before india-location-normalizer. Do not use for storage, summaries, outbound messaging, or action execution."
---

# Lead Extractor

Identify lead signals in parsed messages and emit strict lead objects.

## Quick Triggers

- Find all buyer leads from this WhatsApp chat.
- Extract contact details and budget from these messages.
- Identify serious property inquiries from parsed messages.

## Recommended Chain

`message-parser -> lead-extractor -> india-location-normalizer`

## Execute Workflow

1. Accept parsed messages from Supervisor.
2. Validate input with `references/parsed-message-input.schema.json`.
3. Apply chat-specific extraction rules from `references/extraction-rules-re-india-v1.md`.
4. Determine `dataset_mode` from Supervisor context:
   - default: `broker_group`
   - allowed: `broker_group`, `buyer_inquiry`, `mixed`
5. Detect lead-candidate messages using inquiry intent, contact details, and property-related preferences.
6. Classify `record_type`:
   - `inventory_listing` for broker inventory/availability posts (default in broker groups)
   - `buyer_requirement` for explicit "required/chahiye looking for" demand posts
   - drop non-lead/system noise instead of emitting `noise_or_system`
7. Handle multiline listings as one candidate record when body lines contain price, area, or location details.
8. Build lead records with:
   - required: `lead_id`, `name`, `phone`, `record_type`
   - optional: `dataset_mode`, `property_type`, `budget`, `deal_type`, `asset_class`, `price_basis`, `area_sqft`, `area_basis`, `location_hint`, `raw_text`, `source`, `created_at`
9. Normalize phone extraction from spaced variants such as `+91 98205 82462` and `98200 78845`.
10. Distinguish price intent from rate intent:
   - examples: `3.5 Lakh rent` (monthly), `60K psf` (per-sqft), `4.25 Cr` (total)
11. Deduplicate leads by stable keys when records clearly refer to the same person.
12. Validate output with `references/output-leads.schema.json`.
13. Return only validated lead objects.

## Enforce Boundaries

- Never write or update persistent storage.
- Never modify source messages.
- Never generate summaries.
- Never suggest or execute follow-up actions.
- Never send communication or invoke external side effects.

## Handle Errors

1. Reject invalid parsed-message input.
2. Emit an empty array when no lead evidence exists.
3. Return field-level validation errors when extracted records violate schema.
