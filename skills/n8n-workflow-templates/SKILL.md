---
name: n8n-workflow-templates
version: 1.0.0
description: "Production-ready n8n workflow templates for AI agents. Deploy pre-built automations for webhooks, RSS monitoring, health checks, social metrics, and data backup. Includes deployment scripts and workflow management utilities. Use when: (1) Setting up n8n automations from templates, (2) Deploying workflows to n8n instances, (3) Managing active workflows via API."
metadata:
  openclaw:
    requires:
      bins: ["curl", "bash"]
      env: ["N8N_HOST", "N8N_API_KEY"]
      config: []
    user-invocable: true
  homepage: https://github.com/yoder-bawt
  author: yoder-bawt
---

# n8n Workflow Templates

Deploy production-ready n8n workflows in seconds. Five battle-tested templates plus management scripts for the complete n8n workflow lifecycle.

## Quick Start

```bash
# Set your n8n credentials
export N8N_HOST="http://localhost:5678"
export N8N_API_KEY="n8n_api_xxxxx"

# List existing workflows
bash list-workflows.sh

# Deploy a template
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" templates/webhook-to-telegram.json
```

## Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `webhook-to-telegram.json` | Webhook receiver → Telegram alerts | Instant notifications from any service |
| `rss-monitor.json` | RSS feed monitoring with filtering | Track blogs, news, releases |
| `health-check.json` | HTTP health checks with alerts | Monitor services, APIs, websites |
| `social-metrics.json` | Scheduled social media collection | Track followers, engagement |
| `data-backup.json` | Automated backup with notifications | Database/file backups |

## Detailed Usage

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `N8N_HOST` | Yes | - | n8n instance URL |
| `N8N_API_KEY` | Yes | - | API key from n8n settings |

### Deployment

```bash
bash deploy.sh <n8n-url> <api-key> <template-file> [workflow-name]
```

**Arguments:**
- `n8n-url` - Full URL to n8n instance (e.g., `http://10.0.0.120:5678`)
- `api-key` - n8n API key
- `template-file` - Path to workflow JSON file
- `workflow-name` (optional) - Override the workflow name

**Example:**
```bash
bash deploy.sh "http://10.0.0.120:5678" "n8n_api_abc123" templates/health-check.json "My Health Monitor"
```

### Listing Workflows

```bash
bash list-workflows.sh <n8n-url> <api-key>
```

Lists all active workflows with their IDs, names, and activation status.

## Template Details

### webhook-to-telegram

Receives HTTP POST requests, processes JSON payload, sends formatted messages to Telegram.

**Webhook URL:** `${N8N_HOST}/webhook/workflow-id`

**Expected payload:**
```json
{
  "message": "Alert from my service",
  "level": "warning",
  "timestamp": "2026-02-10T22:00:00Z"
}
```

**Required setup:** Configure Telegram bot token and chat ID in the workflow.

### rss-monitor

Monitors RSS feeds on schedule, filters by keywords, alerts on new items.

**Features:**
- Runs every 15 minutes
- Keyword filtering (include/exclude)
- Duplicate detection
- Multi-channel alerts (Telegram, Discord, email)

**Required setup:** Set RSS feed URL and alert destination.

### health-check

Performs HTTP health checks, alerts on failure, tracks response times.

**Features:**
- Configurable check interval
- Response time thresholds
- Consecutive failure alerts
- Status history tracking

**Required setup:** Set target URLs and alert channels.

### social-metrics

Collects social media metrics on schedule, stores for trending.

**Features:**
- Daily metric collection
- Multi-platform support (X/Twitter, LinkedIn, etc.)
- Data storage in n8n or external DB
- Trend analysis ready

**Required setup:** Configure API credentials for each platform.

### data-backup

Automated backup workflow with pre/post checks and notifications.

**Features:**
- Schedule-based execution
- Pre-backup validation
- Backup verification
- Success/failure notifications
- Retention policy enforcement

**Required setup:** Configure backup source, destination, and credentials.

## API Reference

The scripts use n8n REST API v1:

```
GET  /api/v1/workflows          # List workflows
POST /api/v1/workflows          # Create workflow
GET  /api/v1/workflows/:id      # Get workflow
PUT  /api/v1/workflows/:id      # Update workflow
POST /api/v1/workflows/:id/activate    # Activate
POST /api/v1/workflows/:id/deactivate  # Deactivate
```

Full API docs: `${N8N_HOST}/api/v1/docs`

## Customizing Templates

Templates are standard n8n workflow JSON. Edit in n8n UI or modify the JSON directly:

```bash
# Copy and customize
cp templates/health-check.json my-custom-check.json
# Edit my-custom-check.json with your favorite editor
bash deploy.sh "$N8N_HOST" "$N8N_API_KEY" my-custom-check.json
```

## Troubleshooting

### "Unauthorized" error
- Verify API key is correct
- Check API key hasn't expired in n8n settings

### "Connection refused"
- Verify n8n is running
- Check N8N_HOST includes correct port
- Ensure firewall allows connection

### Workflow won't activate
- Check all credentials are configured in the workflow
- Verify webhook nodes don't conflict with existing webhooks
- Check n8n execution logs for errors

### Template deployment fails
- Validate JSON: `python3 -c "import json; json.load(open('template.json'))"`
- Check n8n version compatibility (templates tested on v1.0+)

## Requirements

- n8n instance v1.0 or later
- API access enabled in n8n settings
- curl and bash
- Network access to n8n instance

## See Also

- n8n Documentation: https://docs.n8n.io/
- n8n API Reference: https://docs.n8n.io/api/
- Workflow examples: https://n8n.io/workflows/
