---
name: pamela-call
description: Make AI phone calls instantly. No lag, no setup, unlimited scale.
homepage: https://docs.thisispamela.com
metadata:
  {"openclaw":{"requires":{"env":["PAMELA_API_KEY"]},"primaryEnv":"PAMELA_API_KEY","homepage":"https://docs.thisispamela.com"}}
---

# Pamela Calls

Make AI phone calls instantly. No lag, no setup, unlimited scale. **[ThisIsPamela](https://thisispamela.com)** is a voice AI platform for outbound calls, phone tree navigation, and integration via SDKs, webhooks, and MCP.

**Jump to:** [Installation](#installation) · [Quick Start](#quick-start) · [Examples](#examples) · [SDK Reference](#sdk-reference)

**ClawHub skill release:** `v1.1.12`

## Prerequisites

- API subscription (required for API access)
- API key from your API account
- Node.js 18+, Bun, or Python 3.8+ (for Python)

## Installation

**JavaScript/TypeScript:** (npm, yarn, or bun)
```bash
npm install @thisispamela/sdk
# or: yarn add @thisispamela/sdk
# or: bun add @thisispamela/sdk
```

**Python:**
```bash
pip install thisispamela
```

**React:** (npm, yarn, or bun)
```bash
npm install @thisispamela/react @thisispamela/sdk
# or: bun add @thisispamela/react @thisispamela/sdk
```

**CLI:**
```bash
npm install -g @thisispamela/cli
```

**MCP (for MCP-based agents):**
```bash
npm install @thisispamela/mcp
```

**Widget (embeddable, no framework):**
```bash
npm install @thisispamela/widget
```

Latest versions: SDK / CLI / Widget / MCP / Python / React `1.2.0`.

## Getting Your API Key

1. Sign up for an API subscription at [developer.thisispamela.com](https://developer.thisispamela.com)
2. Navigate to Settings → API Access
3. Set up billing through Stripe
4. Click "Create API Key"
5. Save immediately - the full key (starts with `pk_live_`) is only shown once

## Trust & security

- **Official packages:** npm [@thisispamela](https://www.npmjs.com/org/thisispamela), PyPI [thisispamela](https://pypi.org/project/thisispamela/) — verify these exact names to avoid typosquatting.
- **Before going live:** Use a restricted or test API key when trying the skill; enable billing alerts in your account; do not put production keys (`pk_live_...`) in public configs or logs.
- **Webhooks:** Always validate the `X-Pamela-Signature` header and secure your endpoint; see [SDK docs](https://docs.thisispamela.com/sdk/javascript#verifywebhooksignature) for verification.
- **Data:** Call audio and transcripts are sent to Pamela and may be stored or forwarded to your webhooks; review [privacy and data practices](https://thisispamela.com) (or contact support@thisispamela.com).
- **Costs:** Monitor usage and billing after enabling; only connected minutes are charged at $0.10/min.

## Quick Start

**Note:** Phone numbers must be in E.164 format (e.g., `+1234567890`).

### JavaScript

```typescript
import { PamelaClient } from '@thisispamela/sdk';

const client = new PamelaClient({ apiKey: 'pk_live_...' });

const call = await client.createCall({
  to: '+1234567890',
  task: 'Call the pharmacy and check if my prescription is ready',
  voice: 'female',
  agent_name: 'Pamela',
});

const status = await client.getCall(call.id);
console.log(status.transcript);
```

### Python

```python
from pamela import PamelaClient

client = PamelaClient(api_key="pk_live_...")

call = client.create_call(
    to="+1234567890",
    task="Call the pharmacy and check if my prescription is ready",
    voice="female",
    agent_name="Pamela",
)

status = client.get_call(call["id"])
print(status["transcript"])
```

### CLI

```bash
export PAMELA_API_KEY="pk_live_..."

thisispamela create-call \
  --to "+1234567890" \
  --task "Call the pharmacy and check if my prescription is ready"
```

## Examples

| Scenario | Example Task |
|----------|--------------|
| Appointment Scheduling | "Call the dentist and schedule a cleaning for next week" |
| Order Status | "Call the pharmacy and check if my prescription is ready" |
| Customer Support | "Navigate the IVR menu to reach billing department" |
| Information Gathering | "Call the restaurant and ask about vegetarian options" |
| Follow-ups | "Call to confirm the appointment for tomorrow at 2pm" |
| IVR Navigation | "Navigate the phone menu to reach a human representative" |

## Key Features

- **Phone tree navigation** - Automatically navigates IVR menus, handles holds and transfers
- **Custom tools** - Register tools the AI can call mid-conversation
- **Real-time transcripts** - Webhook updates as the call progresses
- **React components** - Pre-built UI for call status and transcripts

## SDK Reference

For detailed SDK documentation:

- **[JavaScript SDK](https://docs.thisispamela.com/sdk/javascript)** - Full JS/TS reference
- **[Python SDK](https://docs.thisispamela.com/sdk/python)** - Full Python reference
- **[React Components](https://docs.thisispamela.com/sdk/react)** - Component library (v1.1.5)
- **[Widget](https://docs.thisispamela.com/sdk/widget)** - Embeddable widget for any website
- **[MCP Server](https://docs.thisispamela.com/sdk/mcp)** - MCP tools for AI assistants
- **[CLI](https://docs.thisispamela.com/sdk/cli)** - Command-line reference

## Webhooks

Pamela sends webhooks for call lifecycle events:

- `call.queued` - Call created and queued
- `call.started` - Call connected
- `call.completed` - Call finished successfully
- `call.failed` - Call failed
- `call.transcript_update` - New transcript entries

Only credential required is your API key. For webhooks, always verify the `X-Pamela-Signature` header; see SDK docs for verification.

## Billing

- **$0.10/minute** for API usage
- **Minimum 1 minute** per call
- **Only connected calls** are billed
- API subscription required

## Troubleshooting

**"Invalid API key"**
- Verify key starts with `pk_live_`
- Check key is active in the API settings panel

**"403 Forbidden"**
- API subscription required
- Check subscription status at developer.thisispamela.com

**"Invalid phone number"**
- Use E.164 format with country code: `+1234567890`

## Resources

- **Website:** https://thisispamela.com
- **Docs:** https://docs.thisispamela.com
- **Demo:** https://demo.thisispamela.com
- **API:** https://api.thisispamela.com
- **Discord (live support):** https://discord.gg/cJj5CK8V
- **Email:** support@thisispamela.com
