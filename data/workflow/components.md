# Components

Reusable pieces shared across workflows.

## Connections

Account configurations for external services.

### Format: `components/connections/{service}.md`

```markdown
# {Service Name}

## Auth
- **Method:** api_key | oauth | basic | bearer
- **Secret:** `{workflow}_{service}_api_key` (keychain name)
- **Scope:** {permissions granted}
- **Expires:** {if oauth, when tokens expire}

## Access
- **Base URL:** https://api.example.com/v1
- **Rate limits:** 100 req/min
- **Timeout:** 30s recommended

## Setup
1. Go to {service} developer console
2. Create API key / OAuth app
3. Store in keychain: `security add-generic-password -a clawdbot -s {secret_name} -w "TOKEN"`

## Refresh (OAuth only)
```bash
# Refresh token stored as: {service}_refresh_token
ACCESS=$(curl -X POST "https://api.example.com/oauth/token" \
  -d "refresh_token=$(security find-generic-password -a clawdbot -s {service}_refresh_token -w)" \
  -d "grant_type=refresh_token" | jq -r '.access_token')
```

## Workflows Using This
<!-- Keep updated when adding/removing workflows -->
- daily-email-digest
- weekly-report

## Configured
- **Date:** 2024-01-15
- **By:** agent:main
```

### Database Connections

Different format for databases:

```markdown
# PostgreSQL - {name}

## Connection
- **Secret:** `{workflow}_pg_connection` (full connection string)
- **Format:** `postgresql://user:pass@host:port/database`

## Access
- **Host:** db.example.com
- **Port:** 5432
- **SSL:** required

## Schema Dependencies
This connection assumes these tables exist:
- `orders` (id, customer_id, total, created_at)
- `customers` (id, email, name)

See `schemas/{name}.sql` for DDL.
```

### Secret Naming Convention

```
{workflow}_{service}_{purpose}

Examples:
- daily-digest_gmail_oauth_refresh
- price-monitor_slack_webhook_url
- data-sync_postgres_connection
```

Access in scripts:
```bash
TOKEN=$(security find-generic-password -a clawdbot -s "daily-digest_gmail_oauth_refresh" -w)
```

## Nodes

Reusable operations shared across workflows.

### Format: `components/nodes/{operation}.md`

```markdown
# {Operation Name}

## Purpose
{One-line description}

## Input
- **Schema:** `{ items: array, config: object }`
- **Required fields:** items
- **Optional fields:** config.limit (default: 100)

## Output
- **Schema:** `{ processed: array, count: number }`

## Implementation
```bash
# Path: components/nodes/{operation}.sh
# Called with: ./{operation}.sh input.json output.json

INPUT=$1
OUTPUT=$2

jq '[.items[] | {id, processed: true}]' "$INPUT" > "$OUTPUT"
```

## Configuration
Accepts via environment or config.yaml:
- `MAX_ITEMS`: Maximum items to process (default: 100)
- `TIMEOUT_SEC`: Per-item timeout (default: 30)

## Error Behavior
- Empty input: Returns empty array
- Invalid JSON: Exits 1
- Timeout: Logs warning, skips item

## Workflows Using This
- daily-email-digest (filter step)
- weekly-report (transform step)
```

### Common Nodes

| Node | Purpose | Input → Output |
|------|---------|----------------|
| fetch-url | HTTP GET with retry | url → response JSON |
| filter | Apply jq filter | array + filter → array |
| transform | Map items | array + mapping → array |
| notify | Send notification | message → confirmation |
| diff | Compare datasets | old + new → changes |
| dedupe | Remove duplicates | array + key → array |

## Triggers

Event sources that start workflows.

### Format: `components/triggers/{source}.md`

```markdown
# {Trigger Source}

## Type
webhook | file-watcher | queue | schedule

## Setup

### Webhook
1. Configure in external service to POST to: `https://your-server/webhooks/{workflow}`
2. Set secret for validation: `{workflow}_webhook_secret`
3. Add to webhook router (see below)

### Webhook Router (webhook-server.sh)
```bash
# Simple webhook receiver
while read -r request; do
  PATH=$(echo "$request" | jq -r '.path')
  WORKFLOW=${PATH#/webhooks/}
  PAYLOAD=$(echo "$request" | jq '.body')
  
  # Validate signature
  # ...
  
  # Trigger workflow
  echo "$PAYLOAD" > "workflows/flows/$WORKFLOW/data/00-trigger.json"
  (cd "workflows/flows/$WORKFLOW" && ./run.sh) &
done
```

## Payload Format
```json
{
  "event": "item.created",
  "timestamp": "2024-01-15T08:00:00Z",
  "data": {
    "id": "123",
    "type": "order"
  }
}
```

## Validation
- Check signature header: `X-Webhook-Signature`
- Verify timestamp within 5 minutes
- Check event type matches expected
```

### File Watcher Trigger

```markdown
# File Watcher

## Setup
```bash
# Using fswatch (macOS) or inotifywait (Linux)
fswatch -o /path/to/watch | while read; do
  ./run.sh
done
```

## Configuration
- **Watch path:** /path/to/directory
- **Events:** create | modify | delete
- **Debounce:** 5s (avoid rapid re-triggers)
```

## Discovery

Before creating new components:

```bash
# Search connections
ls workflows/components/connections/

# Search nodes
ls workflows/components/nodes/

# Search by keyword in all components
grep -r "email" workflows/components/

# Find workflows using a component
grep -l "gmail" workflows/flows/*/flow.md
```

## Maintenance

### When Updating a Component

1. Find all workflows using it:
   ```bash
   grep -l "{component}" workflows/flows/*/flow.md
   ```

2. Test with dry-run:
   ```bash
   for flow in $(grep -l ...); do
     (cd "$(dirname $flow)" && ./run.sh --dry-run)
   done
   ```

3. Update "Workflows Using This" in component file

### When Deprecating a Component

1. Mark in component file: `## Status: DEPRECATED - use {alternative}`
2. Notify in all using workflows' CHANGELOG
3. After migration: delete component file
