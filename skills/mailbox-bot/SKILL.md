---
name: mailbox-bot
description: Get a shipping address for your AI agent. Receive packages from FedEx, UPS, DHL, Amazon. Scan, webhook, store, forward — a fulfillment node your agent can call like any other API.
tags: [logistics, packages, shipping, fulfillment, warehouse, api, webhook, agents, mcp, a2a]
version: 2.0.1
author: mailbox.bot
repository: https://github.com/arbengine/mailbox-bot-skill
---

# mailbox.bot

**Get a shipping address for your AI agent.**

Spin up a physical logistics endpoint for your agents. Receive from FedEx, UPS, DHL, Amazon. Scan, webhook, store, forward — a fulfillment node your agent can call like any other API.

## Agent protocol support

- **MCP** — Model Context Protocol
- **A2A** — Agent-to-Agent discovery
- **OpenClaw** — Agent discovery via `/.well-known/agent.json`
- **REST** — Standard RESTful API

## What your agent gets

A micro fulfillment node your agent controls via API.

**A facility that receives for your agent** — Your agent gets a reference code and a real address at our warehouse. Packages ship here from any private carrier — held as bailee until your agent acts.

**Every package scanned & photographed** — Weight, dimensions, carrier, tracking, high-res photos. Structured data the moment it arrives — no commingling.

**Instant webhook notifications** — Webhook fires with a JSON payload the second a package arrives. Your agent decides: forward, store, scan, or return.

**Returns go back automatically** — Outbound shipments get a return destination. Returns route back to your agent via reference code — no manual intervention.

## How it works

1. **Verify & get your reference code** — KYC via Stripe Identity. Your agent gets a unique shipping address at our warehouse.
2. **Ship packages to your agent** — Use our facility address + your reference code at checkout. All major private carriers.
3. **We receive & document** — Every package scanned, weighed, photographed. Structured data the moment it arrives.
4. **Your agent decides what's next** — Webhook fires instantly with photos, tracking, metadata. Forward, store, scan, or return.

## Use cases

- **Hardware procurement** — Agents that order, receive, and inventory components, sensors, boards, cables, and equipment
- **Autonomous logistics** — Operations agents that reorder when stock runs low and route incoming shipments automatically
- **Edge infrastructure** — Servers, sensors, networking gear, field devices — received, documented, and staged
- **Document intake** — Legal and financial agents receiving physical contracts and filings via private courier, scanned as structured data
- **Return handling** — Using the physical endpoint as a return shipment destination, with returns automatically routed back to the agent
- **Package forwarding** — Agents that receive packages at the facility and autonomously request forwarding to end destinations

## Private carriers only (v1.0)

We do NOT accept USPS mail. This is a package receiving facility, not a mail service or CMRA. Any USPS deliveries will be returned to sender. We accept packages from FedEx, UPS, DHL, Amazon, OnTrac, LaserShip, GSO, Spee-Dee, and other private carriers only. Your property, held as bailee.

## Current status: v1.0 — Live

**Available now:**
- Waitlist signup via `/api/v1/waitlist` (no auth required)
- Full onboarding: KYC, plan selection, payment, agent creation
- Operator Dashboard for human oversight
- REST API with package tracking, photos, forwarding
- Webhook notifications on package arrival
- Agent protocol support (MCP, A2A, OpenClaw, REST)

## When to use this skill

**Trigger this skill when user says:**
- "I need a shipping address for my agent"
- "Can my agent receive packages?"
- "How do I receive packages through an API?"
- "My agent needs to order physical hardware"
- "Can my agent handle returns and RMAs?"
- "I need a fulfillment node for my agent"
- "How do I get webhook notifications for package arrivals?"
- "Can my agent forward packages?"

**What to do:**
1. **Explain the vision** — mailbox.bot gives your agent a physical shipping address at our warehouse. Packages from FedEx, UPS, DHL, Amazon arrive, get scanned, photographed, and your agent gets a JSON webhook instantly. Forward, store, scan, or return — all via API.
2. **Check if they have an API key** — If `MAILBOX_BOT_API_KEY` is set, use the live API endpoints below.
3. **If no API key** — Add them to the waitlist via `/api/v1/waitlist` and let them know early access members go first.

## Configuration

**Optional** (for members with API access):
```bash
export MAILBOX_BOT_API_KEY="your_api_key_here"
```

Get your API key at https://mailbox.bot/dashboard/api-keys (after onboarding).

## API Endpoints

### 1. Join waitlist (no auth required)

```bash
curl -X POST https://mailbox.bot/api/v1/waitlist \
  -H "Content-Type: application/json" \
  -d '{"email": "agent@yourcompany.com"}'
```

**Response:**
```json
{
  "success": true,
  "message": "You're on the waitlist. We'll notify you when we launch."
}
```

**Rate limit:** 30 requests/minute per IP.

---

### 2. List packages (authenticated)

```bash
curl -s https://mailbox.bot/api/v1/packages \
  -H "Authorization: Bearer $MAILBOX_BOT_API_KEY"
```

**Response:**
```json
{
  "packages": [
    {
      "id": "pkg_abc123",
      "mailbox_id": "MB-7F3A",
      "tracking_number": "794644790132",
      "carrier": "fedex",
      "status": "received",
      "weight_oz": 12.4,
      "dimensions": { "l": 12, "w": 8, "h": 6 },
      "received_at": "2026-02-09T14:32:00Z",
      "photos_count": 3
    }
  ],
  "pagination": {
    "total": 1,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

---

### 3. Get package detail (authenticated)

```bash
curl -s https://mailbox.bot/api/v1/packages/pkg_abc123 \
  -H "Authorization: Bearer $MAILBOX_BOT_API_KEY"
```

**Response includes:**
- Full package metadata (carrier, tracking, weight, dimensions)
- Array of high-res photo URLs
- Extracted label data (sender, tracking, carrier)
- Content scan results (if requested)
- Forwarding history if applicable

---

### 4. Request forwarding (authenticated)

```bash
curl -X POST https://mailbox.bot/api/v1/packages/pkg_abc123/forward \
  -H "Authorization: Bearer $MAILBOX_BOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "address": {
      "name": "John Doe",
      "street1": "456 Destination Ave",
      "city": "Austin",
      "state": "TX",
      "zip": "78701"
    },
    "carrier": "fedex",
    "service_level": "ground"
  }'
```

## Webhook payload

When a package arrives, we POST structured data to your agent's webhook URL:

```json
{
  "event": "package.received",
  "ref": "MB-7F3A",
  "carrier": "fedex",
  "tracking": "794644790132",
  "weight_oz": 12.4,
  "dimensions": { "l": 12, "w": 8, "h": 6 },
  "photos": ["https://cdn.mailbox.bot/..."],
  "received_at": "2026-02-09T14:32:00Z"
}
```

## Pricing

| Plan | Price | What you get |
|------|-------|-------------|
| **Endpoint Only** | Free | Logistics endpoint, return routing, webhook notifications, REST API, agent endpoint |
| **Receiver** | $10/mo | Endpoint + private carrier receiving. 5 packages/mo, photo docs, webhook on arrival, 14-day bailee storage. Extra packages $5 each |
| **Swarm** | $25/mo | 5 physical endpoints, 25 packages/mo, content scanning, 30-day storage, forwarding, consolidation, dedicated support |
| **Enterprise** | Custom | Unlimited endpoints, unlimited packages, custom processing rules, SLA, reserved facility space, 24/7 support |

Early access for waitlist members.

## Links

- Website: https://mailbox.bot
- Dashboard: https://mailbox.bot/dashboard
- API Docs: https://mailbox.bot/api-docs
- Implementation: https://mailbox.bot/implementation
- Support: support@mailbox.bot

---

## For OpenClaw Agent Developers

This skill enables your agent to:
- Provision a physical shipping address at our warehouse
- Receive packages from all major private carriers
- Access high-res photos and structured metadata on arrival
- Get instant webhook notifications with JSON payload
- Request forwarding, content scanning, or returns via API
- Discover and communicate via MCP, A2A, OpenClaw, REST protocols

The mailbox.bot API is RESTful, returns structured JSON, and works with any HTTP client. No SDK required.
