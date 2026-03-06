---
name: approval-queue
description: Manage pending actions (posts, deploys) with approve/reject
  workflow via REST API and CLI.
---


# Approval Queue

Lightweight approval queue for managing pending actions — SNS posts, deployments, content publishing. Approve or reject with a single tap.

## Quick Start

```bash
cd {skill_dir}
npm install && npm run build

# Start API server
node dist/server.js --port 3010

# CLI usage
node dist/cli.js add --type sns_post --payload '{"text":"Hello world","platform":"twitter"}'
node dist/cli.js list --status pending
node dist/cli.js approve <item-id>
node dist/cli.js reject <item-id> --reason "Not appropriate"
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/queue` | List items (filter: `?status=pending&type=sns_post`) |
| `POST` | `/api/queue` | Add item |
| `POST` | `/api/queue/:id/approve` | Approve |
| `POST` | `/api/queue/:id/reject` | Reject (body: `{"reason": "..."}`) |
| `GET` | `/api/queue/:id` | Get item details |
| `DELETE` | `/api/queue/:id` | Delete item |

## Queue Item Structure

```json
{
  "id": "uuid",
  "type": "sns_post",
  "status": "pending",
  "payload": { "text": "Post content", "platform": "twitter" },
  "created_at": "2025-01-01T00:00:00Z",
  "reviewed_at": null,
  "reviewer_note": null
}
```

## Integration with OpenClaw

```
Agent creates content → Adds to queue → Sends inline approval button → User taps → Action executes
```

## Security

- Validate all input payloads before queuing — reject malformed JSON
- Sanitize `reviewer_note` to prevent injection if displayed in UI
- Use authentication middleware in production (API key or JWT)
- SQLite DB file should be `chmod 600`

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3010 | Server port |
| `DB_PATH` | `./data/queue.db` | SQLite path |
| `WEBHOOK_URL` | — | Callback on approve/reject |

## Troubleshooting

- **Port in use**: `lsof -i :3010` to find conflicts
- **DB locked**: Only one server process should access the SQLite file
- **Webhook failures**: Check URL reachability; add retry logic for production

## Requirements

- Node.js 18+
- No external API keys needed
