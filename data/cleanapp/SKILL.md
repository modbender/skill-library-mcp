---
name: "SKILL: CleanApp Ingest v1 (OpenClaw/ClawHub)"
description: This is a skill package that lets an agent submit any problem
  signal into CleanApp (bugs, incidents, scams, UX friction, policy violations,
  safety hazards, improvement proposals) using the Fetcher ...
---

# SKILL: CleanApp Ingest v1 (OpenClaw/ClawHub)

This is a **skill package** that lets an agent submit **any problem signal** into CleanApp (bugs, incidents, scams, UX friction, policy violations, safety hazards, improvement proposals) using the **Fetcher Key System**:

- `POST /v1/fetchers/register` (one-time key issuance)
- `POST /v1/reports:bulkIngest` (bulk ingest, quarantine-first)
- `GET  /v1/fetchers/me` (introspection)

This is **not** a long-lived agent running inside the CleanApp backend. It’s a client-side integration that talks to CleanApp over HTTPS.

## Why This Is Safe (Compartmentalized)

1. The only secret in the agent is a **revocable CleanApp API key** (`CLEANAPP_API_TOKEN`).
2. New keys default to a **quarantine lane** on the backend:
   - Stored + analyzed
   - Not publicly published
   - Not automatically routed to third parties
   - Not rewarded
3. The backend enforces:
   - rate limits / quotas
   - idempotency (`source_id`)
   - kill switches (revoke/suspend)

So even if an agent is prompt-injected, the blast radius is limited to “submitting more quarantined reports” until the key is revoked.

## Required Secret

- `CLEANAPP_API_TOKEN` (Bearer token). Get it once via:
  - `POST /v1/fetchers/register` (see `references/API_REFERENCE.md`)
  - Store it as a ClawHub/OpenClaw secret; never paste into chat logs.

Optional env:
- `CLEANAPP_BASE_URL` (default `https://live.cleanapp.io`)

## Data Handling (Minimal by Default)

This skill submits:
- `title`, `description` (text)
- optional `lat`/`lng` (location)
- optional `media[]` metadata (URL/SHA/content-type)

Recommended low-risk defaults:
- `--approx-location` (round coordinates to reduce precision)
- `--no-media` (drop media metadata unless needed)

## Idempotency (Important)

Every item must include a stable `source_id`. The backend enforces:
- `UNIQUE(fetcher_id, source_id)`
- retries won’t duplicate rows if you reuse the same `source_id`

## Usage

### Bulk ingest from JSON (recommended)

```bash
export CLEANAPP_API_TOKEN="cleanapp_fk_live_..."
python3 ingest.py \\
  --base-url https://live.cleanapp.io \\
  --input examples/sample_items.json \\
  --approx-location \\
  --no-media
```

### Dry run (no network)

```bash
python3 ingest.py --input examples/sample_items.json --dry-run
```

### Single-item helper (shell)

This is useful for quick manual submissions while debugging.

```bash
export CLEANAPP_API_TOKEN="cleanapp_fk_live_..."
./scripts/submit_report.sh --title "Broken elevator" --description "Stuck on floor 3" --lat 34.0702 --lng -118.4441 --approx-location
```

## Promotion (Out of Quarantine)

Promotion is a **reviewed** process. As you build reputation, CleanApp can:
- raise caps
- allow public publishing/routing/rewards

See:
- `POST /v1/fetchers/promotion-request`
- `GET  /v1/fetchers/promotion-status`

## References

- Swagger UI: `https://live.cleanapp.io/v1/docs`
- OpenAPI YAML: `https://live.cleanapp.io/v1/openapi.yaml`
- `references/API_REFERENCE.md` in this package
