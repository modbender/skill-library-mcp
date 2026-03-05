# mailbox.bot OpenClaw Skill

Get a shipping address for your AI agent. Physical logistics infrastructure — receive packages, scan, webhook, store, forward.

## Quick Start: Publishing to ClawHub

### 1. Install ClawHub CLI

```bash
npm install -g clawhub
```

### 2. Authenticate

```bash
clawhub login
```

This opens GitHub OAuth. Your account must be **at least 1 week old** to publish.

### 3. Publish

```bash
clawhub publish . \
  --slug mailbox-bot \
  --name "mailbox.bot" \
  --version 2.0.0 \
  --changelog "v2.0 — Updated to reflect live v1.0 platform. Physical logistics endpoint for AI agents. Private carrier receiving (FedEx, UPS, DHL, Amazon). Webhook notifications, content scanning, package forwarding. Agent protocol support: MCP, A2A, OpenClaw, REST."
```

### 4. Verify

```bash
clawhub info mailbox-bot
```

## Installation (for OpenClaw users)

```bash
clawhub install mailbox-bot
```

Or paste the skill GitHub URL directly into your OpenClaw chat.

## What This Skill Does

Your agent gets a physical shipping address at our warehouse with a unique reference code (e.g., `Ref: MB-7F3A`). Packages from FedEx, UPS, DHL, Amazon, and other private carriers arrive, get scanned, weighed, and photographed. Your agent receives a JSON webhook instantly and decides what to do — forward, store, scan contents, or return.

**Key capabilities:**
- Receive packages from all major private carriers
- Instant webhook notifications with structured JSON
- High-res photos, weight, dimensions, carrier info
- Package forwarding and consolidation
- Content scanning (open + photograph contents)
- Return routing via reference code
- Agent protocol support: MCP, A2A, OpenClaw, REST

**Private carriers only (v1.0)** — No USPS mail. This is a package receiving facility, not a mail service.

## Pricing

| Plan | Price | Includes |
|------|-------|---------|
| Endpoint Only | Free | Logistics endpoint, webhooks, API access |
| Receiver | $10/mo | 5 packages/mo, photos, 14-day storage |
| Swarm | $25/mo | 5 endpoints, 25 packages/mo, scanning, forwarding |
| Enterprise | Custom | Unlimited everything, SLA, reserved space |

## Links

- Website: https://mailbox.bot
- Dashboard: https://mailbox.bot/dashboard
- API Docs: https://mailbox.bot/api-docs
- Implementation: https://mailbox.bot/implementation

---

Questions? support@mailbox.bot
