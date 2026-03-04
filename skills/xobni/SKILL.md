---
name: xobni
description: Email infrastructure for AI agents via Xobni.ai. Provides real email addresses (@xobni.ai) with REST API and MCP server access. Use when an AI agent needs to send/receive email, search inbox, manage attachments, or set up webhooks for email notifications.
---

# Xobni.ai Email Skill

Give AI agents real email addresses with full inbox functionality.

## Quick Start

1. Create agent at [xobni.ai/agents/new](https://xobni.ai/agents/new) → gets email like `your-agent@xobni.ai`
2. Create API key at [xobni.ai/settings/api-keys](https://xobni.ai/settings/api-keys) scoped to your agent
3. Connect via REST API or MCP

## API Key Scoping

Each API key is scoped to a **single agent**. The key can only access that agent's emails, threads, attachments, and webhooks. No need to pass `account_id` or `agent_id` — they're auto-resolved from your key.

**What scoped keys can do:**
- Read, send, search, and manage emails
- Create and manage webhooks
- View agent info and storage usage

**What scoped keys cannot do:**
- Access other agents' data (returns 403)
- Create or delete agents
- Manage API keys or billing

## MCP Connection

**URL**: `https://api.xobni.ai/mcp/`  
**Transport**: Streamable HTTP  
**Auth**: `Authorization: Bearer YOUR_API_KEY`

### Claude Desktop Config
```json
{
  "mcpServers": {
    "xobni": {
      "url": "https://api.xobni.ai/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY"
      }
    }
  }
}
```

## Core Operations

### Read Inbox
```bash
curl -H "Authorization: Bearer $XOBNI_KEY" \
  "https://api.xobni.ai/api/v1/emails?status=received&limit=20"
```

### Send Email
```bash
curl -X POST -H "Authorization: Bearer $XOBNI_KEY" \
  -H "Content-Type: application/json" \
  "https://api.xobni.ai/api/v1/emails/send" \
  -d '{"to":["recipient@example.com"],"subject":"Hello","body_text":"Message here"}'
```

### Send with Attachments
```bash
curl -X POST -H "Authorization: Bearer $XOBNI_KEY" \
  -H "Content-Type: application/json" \
  "https://api.xobni.ai/api/v1/emails/send" \
  -d '{
    "to":["recipient@example.com"],
    "subject":"Report",
    "body_text":"See attached.",
    "attachments":[{"filename":"report.pdf","data":"<base64>","content_type":"application/pdf"}]
  }'
```

### Search (Semantic)
```bash
curl -X POST -H "Authorization: Bearer $XOBNI_KEY" \
  -H "Content-Type: application/json" \
  "https://api.xobni.ai/api/v1/search" \
  -d '{"query":"invoices from last month","limit":10}'
```

### Get Agent Info
```bash
curl -H "Authorization: Bearer $XOBNI_KEY" \
  "https://api.xobni.ai/api/v1/agents"
```

### Check Storage Usage
```bash
curl -H "Authorization: Bearer $XOBNI_KEY" \
  "https://api.xobni.ai/api/v1/emails/storage-usage"
```

## MCP Tools (14 total)

| Tool | Purpose |
|------|---------|
| `get_agent_info` | Get agent's name, email, slug, status |
| `read_inbox` | List emails with filters (status, limit, offset) |
| `read_email` | Get full email content by ID |
| `send_email` | Send with optional attachments and reply threading |
| `get_thread` | Get all emails in a conversation |
| `list_attachments` | List attachments for an email |
| `download_attachment` | Get pre-signed download URL (15 min) |
| `get_attachment_text` | Extract text from PDF/DOCX/XLSX/PPTX |
| `mark_email` | Update status: read/unread/starred/unstarred/archived |
| `search_emails` | Semantic search across emails + attachments |
| `list_webhooks` | List configured webhooks |
| `create_webhook` | Create webhook for email.received/email.sent |
| `delete_webhook` | Remove a webhook |
| `list_webhook_deliveries` | View webhook delivery history |

## Webhooks

Set up real-time notifications when emails arrive or are sent:

```bash
curl -X POST -H "Authorization: Bearer $XOBNI_KEY" \
  -H "Content-Type: application/json" \
  "https://api.xobni.ai/api/v1/event-hooks" \
  -d '{
    "url": "https://your-endpoint.com/webhook",
    "events": ["email.received"],
    "description": "Email notifications"
  }'
```

Supported events: `email.received`, `email.sent`. Payloads include email metadata and a 200-character snippet. Use `read_email` to fetch full content.

## API Reference

See [references/api.md](references/api.md) for full endpoint documentation.

## Key Concepts

- **Agent-scoped keys**: Each key works with one agent only. Auto-resolves IDs.
- **Semantic search**: Natural language queries across email bodies AND attachments (PDF, DOCX, etc.)
- **Attachments**: Send files via base64 (max 10 files, 10MB total)
- **Webhooks**: Real-time notifications for email events via n8n, Zapier, Make, or any HTTP endpoint.
