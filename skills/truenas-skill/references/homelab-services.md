# Homelab Services

Automation, monitoring, and utility services commonly run alongside TrueNAS.
Each service is independent — users pick what applies to their setup.

## Environment Variables

```
NTFY_URL                             — Push notifications (no auth)
SYNCTHING_URL, SYNCTHING_API_KEY     — File sync
N8N_URL, N8N_API_KEY                 — Workflow automation
NOCODB_URL, NOCODB_API_KEY           — Spreadsheet database
CHANGEDETECTION_URL, CHANGEDETECTION_API_KEY — Website monitoring
CRAFTY_URL, CRAFTY_API_KEY           — Minecraft server management
```

## ntfy (Push Notifications)

```bash
# Send notification
curl -X POST "$NTFY_URL/TOPIC" -d "Message body"

# Send with title and priority
curl -X POST "$NTFY_URL/TOPIC" \
  -H "Title: Alert!" -H "Priority: high" -H "Tags: warning" \
  -d "Message body"

# Health check
curl -s "$NTFY_URL/v1/health"
```

## Syncthing (File Sync)

```bash
# Status
curl -s "$SYNCTHING_URL/rest/system/status" -H "X-API-Key: $SYNCTHING_API_KEY"

# Connections
curl -s "$SYNCTHING_URL/rest/system/connections" -H "X-API-Key: $SYNCTHING_API_KEY"

# Folder status
curl -s "$SYNCTHING_URL/rest/db/status?folder=FOLDER_ID" -H "X-API-Key: $SYNCTHING_API_KEY"
```

## n8n (Workflow Automation)

```bash
# List workflows
curl -s "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY"

# Execute workflow
curl -X POST "$N8N_URL/api/v1/workflows/WORKFLOW_ID/execute" -H "X-N8N-API-KEY: $N8N_API_KEY"

# Get executions
curl -s "$N8N_URL/api/v1/executions" -H "X-N8N-API-KEY: $N8N_API_KEY"
```

## NocoDB (Database)

```bash
# List bases
curl -s "$NOCODB_URL/api/v2/meta/bases" -H "xc-token: $NOCODB_API_KEY"

# List tables in base
curl -s "$NOCODB_URL/api/v2/meta/bases/BASE_ID/tables" -H "xc-token: $NOCODB_API_KEY"

# Read records
curl -s "$NOCODB_URL/api/v2/tables/TABLE_ID/records" -H "xc-token: $NOCODB_API_KEY"

# Create record
curl -X POST "$NOCODB_URL/api/v2/tables/TABLE_ID/records" \
  -H "xc-token: $NOCODB_API_KEY" \
  -H "Content-Type: application/json" -d '{...}'
```

## ChangeDetection.io (Website Monitoring)

```bash
# List watches
curl -s "$CHANGEDETECTION_URL/api/v1/watch" -H "x-api-key: $CHANGEDETECTION_API_KEY"

# Get specific watch
curl -s "$CHANGEDETECTION_URL/api/v1/watch/UUID" -H "x-api-key: $CHANGEDETECTION_API_KEY"

# Trigger recheck
curl -X POST "$CHANGEDETECTION_URL/api/v1/watch/UUID/recheck" \
  -H "x-api-key: $CHANGEDETECTION_API_KEY"

# Add watch
curl -X POST "$CHANGEDETECTION_URL/api/v1/watch" \
  -H "x-api-key: $CHANGEDETECTION_API_KEY" \
  -H "Content-Type: application/json" -d '{"url": "https://example.com"}'
```

## Crafty (Minecraft Server Management)

```bash
# List servers
curl -sk "$CRAFTY_URL/api/v2/servers" -H "Authorization: Bearer $CRAFTY_API_KEY"

# Start server
curl -sk -X POST "$CRAFTY_URL/api/v2/servers/SERVER_ID/action/start_server" \
  -H "Authorization: Bearer $CRAFTY_API_KEY"

# Stop server
curl -sk -X POST "$CRAFTY_URL/api/v2/servers/SERVER_ID/action/stop_server" \
  -H "Authorization: Bearer $CRAFTY_API_KEY"

# Send command
curl -sk -X POST "$CRAFTY_URL/api/v2/servers/SERVER_ID/stdin" \
  -H "Authorization: Bearer $CRAFTY_API_KEY" -d '{"command": "say Hello!"}'
```

## Common Agent Tasks

### "Send a notification"

Use ntfy to push a message to a topic. Subscribers on that topic get the notification
on their phone/desktop.

### "Check sync status"

Use Syncthing's folder status endpoint to see if folders are in sync.

### "Run a workflow"

Use n8n's execute endpoint with the workflow ID.

### "Monitor a website"

Add a URL to ChangeDetection and it will track changes automatically.
