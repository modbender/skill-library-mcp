---
name: clawcrm
description: Agent-native CRM built for AI agents to manage sales pipelines autonomously
repository: https://github.com/Protosome-Inc/ReadyCRM
homepage: https://clawcrm.ai
metadata:
  openclaw:
    requires:
      env:
        - CLAWCRM_API_KEY
      external:
        - service: ClawCRM
          url: https://readycrm.netlify.app
          pricing: "$9/mo BYOA, $999 managed setup"
          required: true
    primaryEnv: CLAWCRM_API_KEY
    repository: https://github.com/Protosome-Inc/ReadyCRM
    homepage: https://clawcrm.ai
tags:
  - crm
  - sales
  - automation
  - enrichment
  - pipeline
  - email
---

# ClawCRM Skill

**Agent-native CRM built for AI agents to manage sales pipelines autonomously.**

## What This Skill Does

ClawCRM lets you:
- Create and manage leads programmatically
- Auto-enrich leads with professional data (Apollo.io + Google Deep Search)
- Generate personalized proposal pages
- Track engagement (views, video plays, CTA clicks)
- Send email sequences with proper delays
- Analyze pipeline health and conversion metrics

**Zero human clicks required.** You handle the entire sales workflow.

## Installation

### 1. Sign Up Your Human

```bash
curl -X POST https://readycrm.netlify.app/api/openclaw/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "human@company.com",
    "firstName": "Jane",
    "lastName": "Smith",
    "organizationName": "Acme Corp"
  }'
```

Response:
```json
{
  "success": true,
  "orgId": "org_abc123",
  "apiKey": "rcm_live_xyz789",
  "dashboardUrl": "https://readycrm.netlify.app/dashboard"
}
```

**Save the API key** - you'll need it for all subsequent calls.

### 2. Bootstrap Workspace (One-Shot Setup)

```bash
curl -X POST https://readycrm.netlify.app/api/openclaw/setup \
  -H "Content-Type: application/json" \
  -H "x-admin-token: rcm_live_xyz789" \
  -d '{
    "projectSlug": "acme-corp",
    "org": {
      "name": "Acme Corp",
      "website": "https://acme.com",
      "industry": "SaaS",
      "bookingLink": "https://calendly.com/acme/demo",
      "primaryColor": "#3B82F6"
    },
    "stages": [
      { "name": "New Lead", "order": 0, "color": "#6B7280", "isDefault": true },
      { "name": "Contacted", "order": 1, "color": "#3B82F6" },
      { "name": "Demo Booked", "order": 2, "color": "#8B5CF6" },
      { "name": "Won", "order": 3, "color": "#10B981" }
    ]
  }'
```

**Done!** Your human's CRM is fully configured. They never touched the dashboard.

## Usage Examples

### Create a Lead (Auto-Enrichment Enabled)

```bash
curl -X POST https://readycrm.netlify.app/api/openclaw/leads \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_TOKEN" \
  -d '{
    "email": "founder@startup.com",
    "firstName": "John",
    "lastName": "Doe",
    "organizationName": "Cool Startup Inc",
    "businessType": "SaaS"
  }'
```

Response:
```json
{
  "success": true,
  "lead": {
    "id": "rp_abc123",
    "email": "founder@startup.com",
    "firstName": "John",
    "proposalId": "cool-startup-inc-abc123",
    "proposalUrl": "https://readycrm.netlify.app/proposal/cool-startup-inc-abc123"
  }
}
```

**Auto-enrichment happens in background (30-60 seconds):**
- Apollo.io → professional email, phone, LinkedIn, company data
- Google Deep Search → website research, tech stack, discussion points
- Spider Web → connections to other leads in your CRM

### Check Enrichment Status

```bash
curl "https://readycrm.netlify.app/api/openclaw/enrich?leadId=rp_abc123" \
  -H "x-admin-token: YOUR_TOKEN"
```

Response:
```json
{
  "leadId": "rp_abc123",
  "status": "complete",
  "enrichment": {
    "tier": 1,
    "sources": ["apollo", "google_deep"],
    "discussionPoints": [
      {
        "topic": "Current Tech Stack",
        "detail": "Using Stripe, Intercom, Google Analytics",
        "source": "website"
      }
    ],
    "practiceModel": "subscription",
    "techStack": ["Stripe", "Intercom", "Google Analytics"],
    "confidence": { "overall": "high" }
  }
}
```

### Send Email Sequence

```bash
curl -X POST https://readycrm.netlify.app/api/openclaw/email/send-sequence \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_TOKEN" \
  -d '{
    "leadId": "rp_abc123",
    "sequence": [
      {
        "delayMinutes": 0,
        "subject": "Your Custom Demo - {{organizationName}}",
        "body": "Hi {{firstName}},\n\nI put together a custom demo for {{organizationName}}:\n{{proposalUrl}}\n\nBest,\nTeam"
      },
      {
        "delayMinutes": 5760,
        "subject": "Following up",
        "body": "Hi {{firstName}},\n\nDid you get a chance to check out the demo?\n\nBest,\nTeam"
      }
    ]
  }'
```

**Template Variables:**
- `{{firstName}}`, `{{lastName}}`
- `{{organizationName}}`, `{{businessType}}`
- `{{proposalUrl}}` - auto-generated proposal page
- `{{email}}`, `{{phone}}`

**Delays:**
- 0 = immediate
- 1440 = 1 day (24 hours)
- 5760 = 4 days
- 10080 = 1 week

### Track Proposal Engagement

```bash
curl "https://readycrm.netlify.app/api/tracking/proposal?leadId=rp_abc123" \
  -H "x-admin-token: YOUR_TOKEN"
```

Response:
```json
{
  "totalViews": 3,
  "timeOnPage": 420,
  "sectionsViewed": ["hero", "features", "pricing"],
  "videoCompletion": 75,
  "ctaClicks": 2
}
```

### List Leads (Filter & Sort)

```bash
curl "https://readycrm.netlify.app/api/openclaw/leads?status=new&tier=high&limit=50" \
  -H "x-admin-token: YOUR_TOKEN"
```

### Update Lead Status

```bash
curl -X PATCH https://readycrm.netlify.app/api/openclaw/leads \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_TOKEN" \
  -d '{
    "id": "rp_abc123",
    "status": "qualified"
  }'
```

## Advanced Features

### Bulk Enrichment

```bash
curl -X POST https://readycrm.netlify.app/api/openclaw/enrich/bulk \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_TOKEN" \
  -d '{
    "leadIds": ["rp_123", "rp_456", "rp_789"]
  }'
```

### Spider Web Analysis (Find Connections)

```bash
curl -X POST https://readycrm.netlify.app/api/openclaw/enrich/spider-web \
  -H "Content-Type: application/json" \
  -H "x-admin-token: YOUR_TOKEN" \
  -d '{
    "leadId": "rp_abc123"
  }'
```

Returns:
```json
{
  "connections": [
    {
      "leadId": "rp_456",
      "name": "Jane Smith",
      "connectionType": "same_university",
      "detail": "Both attended Stanford",
      "strength": "high"
    }
  ],
  "totalConnections": 5
}
```

### Pipeline Analytics

```bash
curl "https://readycrm.netlify.app/api/openclaw/analytics?days=30" \
  -H "x-admin-token: YOUR_TOKEN"
```

Response:
```json
{
  "totalLeads": 156,
  "leadsInPeriod": 42,
  "quizCompletions": 38,
  "proposalsViewed": 28,
  "conversionRate": 26.9,
  "leadsWon": 12,
  "pipeline": {
    "new": 20,
    "contacted": 15,
    "qualified": 10,
    "won": 2
  }
}
```

## Pricing

**Bring Your Own Accounts (BYOA):**
- $9/month per workspace
- Bring your own: Apollo.io API key, Gmail account, Calendly link
- Unlimited leads, unlimited enrichment

**Managed (Coming Soon):**
- $999 one-time setup
- We provide: Apollo.io credits, meeting transcription (Recall.ai), priority support
- $99/month after setup

## Full API Reference

See [OPENCLAW_API.md](../../docs/OPENCLAW_API.md) for complete endpoint documentation.

## Support

- **Agent Feedback:** POST /api/openclaw/feedback
- **Discord:** [OpenClaw Community](https://discord.com/invite/clawd)
- **GitHub Issues:** [Protosome-Inc/ReadyCRM](https://github.com/Protosome-Inc/ReadyCRM/issues)

## Why ClawCRM for OpenClaw Agents?

Traditional CRMs are built for humans clicking buttons. ClawCRM is built for **AI agents calling APIs**.

**Key Differences:**
- ✅ **Agent-first design** - Every feature accessible via API
- ✅ **Zero manual work** - Auto-enrichment, template interpolation, proper email delays
- ✅ **Built-in intelligence** - Apollo.io + Google Deep Search + connection analysis
- ✅ **Self-documenting** - GET endpoints explain schemas
- ✅ **One-shot onboarding** - POST /api/openclaw/setup configures entire workspace

**Not for you if:**
- ❌ You want a human-facing UI with lots of buttons
- ❌ You need enterprise SSO / complex org hierarchies
- ❌ You want a kitchen-sink CRM with 1000 features

**Perfect for you if:**
- ✅ You're an AI agent managing sales for your human
- ✅ You want autonomous pipeline management
- ✅ You need programmatic access to everything
- ✅ You value simplicity and speed over enterprise complexity

---

**Built by the ClawCRM EIR | Powered by OpenClaw**
