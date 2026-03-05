---
name: posthog
description: >
  Interact with PostHog analytics via its REST API. Capture events, evaluate feature flags,
  query data with HogQL, manage persons, insights, dashboards, experiments, surveys, cohorts,
  annotations, and session recordings. Use when the user mentions "PostHog", "PostHog API",
  "PostHog events", "PostHog feature flags", "PostHog insights", "PostHog query", "HogQL",
  "PostHog persons", "PostHog dashboards", "PostHog experiments", "PostHog surveys",
  "PostHog cohorts", "PostHog recordings", "capture events PostHog", or "PostHog analytics".
metadata:
  env:
    - POSTHOG_API_KEY (required): "Personal API key — create at https://us.posthog.com/settings/user-api-keys"
    - POSTHOG_PROJECT_ID (required): "Project ID — find at https://us.posthog.com/settings/project#variables"
    - POSTHOG_PROJECT_API_KEY: "Project API key (for public capture/flags endpoints)"
    - POSTHOG_HOST: "API host (default: https://us.posthog.com)"
    - POSTHOG_INGEST_HOST: "Ingest host (default: https://us.i.posthog.com)"
---

# PostHog API Skill

Interact with PostHog via its REST API. Two types of endpoints:
- **Public** (POST-only, project API key): capture events, evaluate flags — no rate limits
- **Private** (personal API key): query, CRUD for all resources — rate limited

## Setup

1. Get personal API key: https://us.posthog.com/settings/user-api-keys
2. Get project ID: https://us.posthog.com/settings/project#variables
3. Set env vars:
   ```bash
   export POSTHOG_API_KEY="phx_..."
   export POSTHOG_PROJECT_ID="12345"
   export POSTHOG_PROJECT_API_KEY="phc_..."  # optional, for capture/flags
   # For EU Cloud:
   # export POSTHOG_HOST="https://eu.posthog.com"
   # export POSTHOG_INGEST_HOST="https://eu.i.posthog.com"
   ```
4. Verify: `bash scripts/posthog.sh whoami`

## Helper Script

`scripts/posthog.sh` wraps common operations. Run `bash scripts/posthog.sh help` for full usage.

### Examples

```bash
# Capture an event
bash scripts/posthog.sh capture "signup" "user_123" '{"plan":"pro"}'

# Evaluate feature flags
bash scripts/posthog.sh evaluate-flags "user_123"

# HogQL query — top events last 7 days
bash scripts/posthog.sh query "SELECT event, count() FROM events WHERE timestamp >= now() - INTERVAL 7 DAY GROUP BY event ORDER BY count() DESC LIMIT 20"

# List persons
bash scripts/posthog.sh list-persons 10 | jq '.results[] | {name, distinct_ids}'

# List feature flags
bash scripts/posthog.sh list-flags | jq '.results[] | {id, key, active}'

# Create a feature flag
echo '{"key":"new-dashboard","name":"New Dashboard","active":true,"filters":{"groups":[{"rollout_percentage":50}]}}' | \
  bash scripts/posthog.sh create-flag

# List dashboards
bash scripts/posthog.sh list-dashboards | jq '.results[] | {id, name}'
```

## Key Concepts

### Two API types
- **Public endpoints** (`/i/v0/e/`, `/batch/`, `/flags`): Use project API key in body. No auth header. No rate limits.
- **Private endpoints** (`/api/projects/:project_id/...`): Use personal API key via `Authorization: Bearer`. Rate limited.

### HogQL Queries
The query endpoint (`POST /api/projects/:project_id/query/`) is the most powerful way to extract data. Uses SQL-like HogQL syntax against tables: `events`, `persons`, `sessions`, `groups`, plus data warehouse tables.

Always include time ranges and LIMIT. Use timestamp-based pagination for large exports.

### Rate Limits (private endpoints)
| Type | Limit |
|------|-------|
| Analytics (insights, persons, recordings) | 240/min, 1200/hr |
| Query endpoint | 2400/hr |
| Feature flag local evaluation | 600/min |
| Other CRUD | 480/min, 4800/hr |

Limits apply per organization. On 429: back off and retry.

### Domains
| Cloud | Public | Private |
|-------|--------|---------|
| US | `us.i.posthog.com` | `us.posthog.com` |
| EU | `eu.i.posthog.com` | `eu.posthog.com` |

### Events API (deprecated)
The `/api/projects/:project_id/events/` endpoint is deprecated. Use HogQL queries or batch exports instead.

## Direct curl

```bash
# Private endpoint
curl -H "Authorization: Bearer $POSTHOG_API_KEY" \
  "$POSTHOG_HOST/api/projects/$POSTHOG_PROJECT_ID/feature_flags/"

# HogQL query
curl -H "Authorization: Bearer $POSTHOG_API_KEY" \
  -H "Content-Type: application/json" \
  -X POST -d '{"query":{"kind":"HogQLQuery","query":"SELECT count() FROM events WHERE timestamp >= now() - INTERVAL 1 DAY"}}' \
  "$POSTHOG_HOST/api/projects/$POSTHOG_PROJECT_ID/query/"

# Capture event (public)
curl -H "Content-Type: application/json" \
  -X POST -d '{"api_key":"'$POSTHOG_PROJECT_API_KEY'","event":"test","distinct_id":"u1"}' \
  "$POSTHOG_INGEST_HOST/i/v0/e/"
```

## Full API Reference

See [references/api-endpoints.md](references/api-endpoints.md) for complete endpoint listing with parameters, body schemas, scopes, and response formats.

Sections: Public Endpoints (Capture, Batch, Flags), Private Endpoints (Persons, Feature Flags, Insights, Dashboards, Annotations, Cohorts, Experiments, Surveys, Actions, Session Recordings, Users, Definitions), Query API (HogQL).
