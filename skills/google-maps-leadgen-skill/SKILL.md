---
name: google-maps-leadgen
description: Generate B2B leads from Google Maps using a self-hosted MCP server (`google-maps`) and export to CSV or XLSX. Use when the user asks for lead generation by country/city/industry, wants phone/website/email enrichment, wants deduped lead lists, or asks to send lead files back in chat (especially Telegram file delivery).
---

# Google Maps Lead Generation (MCP)

Use this skill to run repeatable lead-gen batches from Google Maps via MCP.

## Preconditions

- `mcporter` configured with server `google-maps`.
- Server key in env (`GOOGLE_MAPS_API_KEY`) must be server-compatible (no browser referrer restriction).
- For XLSX output, `openpyxl` available in venv.

## Fast workflow

1. Build query set from geography + target verticals.
2. Run `maps_search_places` for each query.
3. Keep only in-target geography, dedupe by `place_id`.
4. Enrich each place with `maps_place_details`.
5. Export CSV or XLSX.
6. If user asks for file in Telegram, send with `message` tool `action=send` + `media` path.

## Query strategy

Use focused terms instead of broad generic terms.

- Good: `"odoo partner <city> <country>"`, `"erp integrator <city> <country>"`, `"logistics company <city> <country>"`
- Avoid huge overlapping lists in one run; do batches.

## Required output columns (V2)

- `name`
- `address`
- `phone`
- `website`
- `email` (empty if not discoverable)
- `rating`
- `place_id`
- `google_maps_url` (mobile-safe):
  - `https://www.google.com/maps/search/?api=1&query=<NAME>&query_place_id=<PLACE_ID>`

## Cost notes

- Search calls are usually main paid SKU driver.
- Place details add enrichment cost.
- Report rough run cost estimate and mention free-tier caveat.

## Reliability guardrails

- Batch enrich in small chunks (10–50) to avoid long-running timeouts.
- Add retries for transient failures.
- Never commit API keys or sensitive exports.

## Delivery rules

- If user asks for CSV/XLSX file in chat: send via `message` tool (`media` path).
- If user asks specifically for XLSX formatting/edits, use xlsx workflow standards.
- Keep summary concise: count, coverage (`with_phone`, `with_website`, `with_email`), file path/name.
