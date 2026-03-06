---
name: email-webhook
description: Receive incoming emails via JSON webhooks and wake the agent. Built for AI Commander.
metadata: {"openclaw": {"requires": {"bins": ["node", "openclaw"], "env": ["WEBHOOK_SECRET"]}, "primaryEnv": "WEBHOOK_SECRET", "install": [{"id": "npm-deps", "kind": "node", "package": "express@4.21.2", "label": "Install Webhook dependencies"}]}}
---

# Email Webhook Receiver

This skill provides a secure endpoint to receive emails as standardized JSON webhooks and automatically wakes the agent.

## 🤖 Agent Setup (Post-Install)

After installing and starting this skill, add the following logic to your `HEARTBEAT.md`:

```markdown
### 📧 Inbound Email Check
- Read `<path-to-inbox.jsonl>` (configured via INBOX_FILE or default: inbox.jsonl in cwd)
- Compare the latest `receivedAt` timestamp with your last-checked timestamp
- If there are NEW emails since last check:
  - Notify the user via their last active communication channel (Discord, WhatsApp, etc.)
  - Format: "📧 New email from [from]: [subject] — [text preview]"
  - Update your last-checked timestamp
- If no new emails: continue silently
```

> 💡 You don't need to know the user's channel in advance — use the most recently active channel from your session history. If you're unsure how to reach the user, ask them directly.

The skill fires `openclaw system event` on each incoming email to wake you immediately. Your HEARTBEAT.md logic will then run and handle the notification.

## ⚡️ Wake Mechanism

When an email is received, the server invokes `openclaw system event --mode now`. This ensures the agent is notified immediately and can process the incoming communication without waiting for the next heartbeat cycle.

## 🚨 Security & Privacy

### Command Injection Protection
The server uses secure process spawning (`child_process.spawn`) with argument arrays instead of shell execution. User-controlled input (email headers) cannot be used to execute arbitrary system commands.

### Path Traversal Protection
The `INBOX_FILE` parameter is sanitized using `path.basename()`, ensuring that files are only written within the server's working directory.

### Authentication
A strong `WEBHOOK_SECRET` environment variable is **REQUIRED** for the server to start. All incoming requests must provide this secret in the `Authorization: Bearer <secret>` header.

### Data Storage
- **Local Inbox**: Incoming emails (raw body and metadata) are appended to a local `inbox.jsonl` file.
- **Cleanup**: Users should periodically rotate or delete the inbox file to save disk space and protect privacy.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `WEBHOOK_SECRET` | **Yes** | — | Secret token for webhook authentication. |
| `OPENCLAW_AGENT_ID` | **Yes** | — | Your agent ID (e.g. `skippy`). Without this, incoming emails wake **ALL** agents on the server. |
| `PORT` | No | `2083` | Port to listen on. Configurable — set to match your `OPENCLAW_WEBHOOK_URL`. |
| `INBOX_FILE` | No | `inbox.jsonl` | Filename for the activity feed. |

## Setup

1. **Install dependencies**:
   ```bash
   npm install express@4.21.2
   ```
2. **Start Server**:
   ```bash
   WEBHOOK_SECRET=your-strong-token node scripts/webhook_server.js
   ```

## Cloudflare Setup

This server listens on port **2082**. Cloudflare natively supports port 2082 as an HTTP origin port with Flexible SSL.

When configuring your Cloudflare Email Worker, set `OPENCLAW_WEBHOOK_URL` using **`http://`** with the port explicitly:

```
https://webhook.yourdomain.com:2083/api/email
```

Port **2083** is a Cloudflare-supported port. Works with **Flexible SSL** — the server uses a self-signed certificate (auto-generated on first run) which Cloudflare accepts on this port.

> ⚠️ If you use a different port, set the `PORT` env var when starting the server.
> ⚠️ If you omit the port in the Worker URL, Cloudflare defaults to port 80 → 404.

DNS setup: create an A record for `webhook.yourdomain.com` pointing to your server IP with the orange cloud (proxy) enabled.

## Runtime Requirements
Requires: `express`, `node`, `openclaw` CLI.
