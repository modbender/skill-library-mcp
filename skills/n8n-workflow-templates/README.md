# n8n Workflow Templates

Production-ready n8n workflow templates for AI agents. Deploy automations in seconds.

## Quick Start

```bash
# Set credentials
export N8N_HOST="http://localhost:5678"
export N8N_API_KEY="n8n_api_xxxxx"

# List workflows
bash list-workflows.sh "$N8N_HOST" "$N8N_API_KEY"

# Deploy a template
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/webhook-to-telegram.json
```

## Available Templates

| Template | Purpose | Schedule |
|----------|---------|----------|
| `webhook-to-telegram.json` | Receive webhooks, send Telegram alerts | On webhook |
| `rss-monitor.json` | Monitor RSS feeds with filtering | Every 15 min |
| `health-check.json` | HTTP health checks with alerts | Every 5 min |
| `social-metrics.json` | Collect social media stats | Daily |
| `data-backup.json` | Automated backup with validation | Daily |

## Template Details

### Webhook to Telegram

Instant notifications from any service.

```bash
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/webhook-to-telegram.json "My Alerts"
```

**Usage:**
```bash
curl -X POST "$N8N_HOST/webhook/webhook-alert" \
  -H "Content-Type: application/json" \
  -d '{"message":"Server alert","level":"warning","source":"api"}'
```

**Configure:** Set Telegram bot token and chat ID in n8n UI.

### RSS Monitor

Track blogs, news, releases with keyword filtering.

```bash
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/rss-monitor.json
```

**Configure:** Edit the template to set RSS URL, keywords, and alert destination.

### Health Check

Monitor services, APIs, websites with response time tracking.

```bash
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/health-check.json
```

**Configure:** Set target URLs in the "Service List" node code.

### Social Metrics

Daily social media tracking.

```bash
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/social-metrics.json
```

**Configure:** Set accounts in "Account List" node, add API credentials.

### Data Backup

Automated backup with pre-checks and notifications.

```bash
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/data-backup.json
```

**Configure:** Set backup source, destination, and credentials in n8n UI.

## Scripts

### deploy.sh
Deploy a template to n8n.

```bash
bash deploy.sh <n8n-url> <api-key> <template-file> [workflow-name]
```

### list-workflows.sh
List all workflows.

```bash
bash list-workflows.sh <n8n-url> <api-key>
```

### activate-workflow.sh
Activate a workflow by ID.

```bash
bash activate-workflow.sh <n8n-url> <api-key> <workflow-id>
```

### delete-workflow.sh
Delete a workflow.

```bash
bash delete-workflow.sh <n8n-url> <api-key> <workflow-id>
```

## Customizing Templates

1. Copy template: `cp templates/health-check.json my-check.json`
2. Edit JSON or import to n8n UI and modify
3. Deploy: `bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" my-check.json`

## n8n API Reference

```
GET  /api/v1/workflows          # List
POST /api/v1/workflows          # Create
GET  /api/v1/workflows/:id      # Get
PUT  /api/v1/workflows/:id      # Update
POST /api/v1/workflows/:id/activate    # Activate
POST /api/v1/workflows/:id/deactivate  # Deactivate
```

Full docs: `$N8N_HOST/api/v1/docs`

## Requirements

- n8n v1.0+
- API access enabled in Settings → API
- curl, bash
- Network access to n8n instance

## License

MIT
