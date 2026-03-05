# CleanApp Ingest API Reference (v1)

This skill targets the **Fetcher Key System** (quarantine-first ingest surface) for submitting **problem signals** (bugs/incidents/feedback) into CleanApp.

## Docs / OpenAPI

- Swagger UI: `https://live.cleanapp.io/v1/docs`
- OpenAPI YAML: `https://live.cleanapp.io/v1/openapi.yaml`

## 1) Register a Fetcher (one-time API key issuance)

```
POST /v1/fetchers/register
```

**Base URL**: `https://live.cleanapp.io`

This returns:
- `fetcher_id`
- `api_key` (**shown once**; never stored plaintext server-side)

Example:

```bash
curl -fsS -H 'content-type: application/json' \\
  -d '{"name":"cleanapp-agent001","owner_type":"openclaw"}' \\
  https://live.cleanapp.io/v1/fetchers/register
```

Store `api_key` as a secret env var: `CLEANAPP_API_TOKEN`.

## 2) Bulk Ingest (quarantine lane)

```
POST /v1/reports:bulkIngest
Authorization: Bearer <api_key>
```

### Request schema

```json
{
  "items": [
    {
      "source_id": "string (required; idempotency key unique per fetcher)",
      "title": "string (optional)",
      "description": "string (optional)",
      "lat": 47.36,
      "lng": 8.55,
      "collected_at": "2026-02-14T00:00:00Z",
      "agent_id": "cleanapp-agent001",
      "agent_version": "1.0",
      "source_type": "text|vision|sensor|web",
      "media": [{ "url": "...", "sha256": "...", "content_type": "image/jpeg" }]
    }
  ]
}
```

### Limits / semantics

- Max **100 items** per request
- **Idempotency**: `source_id` is required. Duplicate `source_id` for the same fetcher returns `status=duplicate`.
- **Quarantine-first**: new fetchers default to `visibility=shadow`, `trust_level=unverified`.
  - Stored + analyzed.
  - Not publicly published / routed / rewarded unless promoted.

### Response schema (per-item results)

```json
{
  "submitted": 1,
  "accepted": 1,
  "duplicates": 0,
  "rejected": 0,
  "items": [
    {
      "source_id": "abc",
      "status": "accepted|duplicate|rejected",
      "report_seq": 1148625,
      "queued": true,
      "visibility": "shadow|limited|public",
      "trust_level": "unverified|verified|trusted",
      "reason": "string (if rejected)"
    }
  ]
}
```

## 3) Fetcher Introspection

```
GET /v1/fetchers/me
Authorization: Bearer <api_key>
```

Returns:
- tier/status/reputation
- caps + usage
- defaults (`default_visibility`, `default_trust_level`, `routing_enabled`, `rewards_enabled`)

## 4) Promotion Request (out of quarantine)

```
POST /v1/fetchers/promotion-request
GET  /v1/fetchers/promotion-status
```

Promotion is **reviewed**. It can raise caps, enable routing/rewards, and/or change defaults to publish publicly.
