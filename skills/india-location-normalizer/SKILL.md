---
name: india-location-normalizer
description: "Normalize Indian real-estate location text into canonical city and locality fields (Mumbai and Pune v1) with confidence and unresolved flags. Use when leads contain aliases like Goregaon, Andheri W, PCMC, Hinjewadi, Baner, or Wakad. Recommended chain position: lead-extractor then india-location-normalizer then sentiment-priority-scorer. Do not use for writes or outbound actions."
---

# India Location Normalizer

Resolve messy India locality aliases into canonical location fields without side effects.

## Quick Triggers

- Normalize Mumbai/Pune location aliases from extracted leads.
- Map PCMC and Hinjewadi variants to canonical localities.
- Resolve Mumbai shorthand like `Scruz`, `Khar`, `Andheri W`, `Turner Road`, `Carter Road`.
- Standardize locality names before scoring or storage.

## Recommended Chain

`message-parser -> lead-extractor -> india-location-normalizer -> sentiment-priority-scorer`

Target KPI for production tuning: improve canonical Mumbai/Pune locality resolution versus extractor-only baseline.

## Execute Workflow

1. Accept lead-location payload from Supervisor.
2. Validate input against `references/location-normalizer-input.schema.json`.
3. Use `references/india-location-aliases-v1.json` as the authoritative lookup map.
4. Match in this order:
   - exact alias match (case-insensitive)
   - token-normalized alias match (trim punctuation, collapse spaces)
   - conservative fuzzy match only when clearly unambiguous
5. Return one normalized location record per input lead with:
   - `city`
   - `locality_canonical`
   - `micro_market`
   - `matched_alias`
   - `confidence`
   - `unresolved_flag`
6. Validate output against `references/location-normalizer-output.schema.json`.

## Enforce Boundaries

- Never parse raw chat exports.
- Never extract non-location entities.
- Never write to Google Sheets, databases, or files.
- Never send messages or trigger external channels.
- Never auto-resolve low-confidence ambiguous aliases.

## Handle Ambiguity

1. If multiple localities match equally, set `unresolved_flag: true`.
2. If no confident match exists, preserve input in `matched_alias` and mark unresolved.
3. Prefer false-negative over false-positive for city/locality assignment.
