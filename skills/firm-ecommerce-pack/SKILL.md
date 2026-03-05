---
name: firm-ecommerce-pack
version: 1.0.0
description: >
  Curated skill bundle for e-commerce platforms, D2C brands and marketplace operators.
  Activates the firm pyramid with Marketing, Commercial, Operations and Engineering agents
  pre-configured for catalog management, campaign orchestration, customer support and
  revenue operations workflows.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    requires:
      env: []
      bins: []
    tools:
      - sessions_send
      - sessions_spawn
      - sessions_history
    primaryEnv: ""
tags:
  - ecommerce
  - d2c
  - marketplace
  - retail
  - shopify
  - firm-pack
  - sector
---

# firm-ecommerce-pack

Sector bundle for **e-commerce & retail** environments.

## Activated departments

| Department | Services activated | Focus |
|---|---|---|
| Marketing | Product Marketing · Growth Marketing · Content & Brand | Campaigns, SEO, UGC |
| Commercial | Sales Engineering · Revenue Operations · Partnerships | GMV, conversion, B2B |
| Engineering | Frontend · Backend · Data Engineering · Integration | Platform, APIs, feeds |
| Support Clients | Client Support Operations · Client Incident Response | CX, returns, escalations |
| Finance | FP&A · Pricing Strategy · Billing & Collections | Margin, pricing, cashflow |
| Operations | DevOps · Release · Documentation | Deployments, catalog ops |

## Recommended ClawHub skills to install alongside

```bash
npx clawhub@latest install activecampaign           # Email/CRM automation
npx clawhub@latest install airtable-automation      # Product catalog management
npx clawhub@latest install biz-reporter             # GA4 + Stripe analytics
npx clawhub@latest install ai-hunter-pro            # Social media trend automation
npx clawhub@latest install shopping-ecommerce       # Product data extraction
npx clawhub@latest install firm-orchestration       # A2A orchestration backbone
npx clawhub@latest install firm-delivery-export     # Output → PR / ticket / doc
```

## Firm configuration overlay

```json
{
  "agent": {
    "model": "anthropic/claude-opus-4-6",
    "workspace": "~/.openclaw/workspace/ecommerce-firm"
  },
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace/ecommerce-firm"
    }
  }
}
```

## Prompt: product launch orchestration

```
Use firm-orchestration with:
  objective: "Launch Summer 2026 collection across all channels by March 15"
  departments: ["marketing", "engineering", "operations"]
  constraints: ["budget €15k", "no discount > 20%", "mobile-first"]
  definition_of_done: "Launch checklist: landing page live, campaigns scheduled, inventory synced"
  delivery_format: "project_brief"
```

## Prompt: CX incident response

```
Use firm-orchestration with:
  objective: "Triage 47 open complaints from payment gateway outage on Feb 27"
  departments: ["support_clients", "engineering", "finance"]
  constraints: ["SLA: 24h response", "auto-refund for orders < €50"]
  definition_of_done: "Resolution report: refunds processed, root cause, prevention plan"
  delivery_format: "markdown_report"
```

## Routing profiles

| Task | Profile | Model hint |
|---|---|---|
| Campaign copy | `marketing` → `creative-premium` | Claude Opus |
| Code review | `engineering` → `reasoning-technical` | Claude Sonnet |
| Data analysis | `finance` → `analysis-deep` | Claude Opus |
| Product description | `marketing` → `translation-precision` | Claude Haiku |

---

## 💎 Support

Si ce skill vous est utile, vous pouvez soutenir le développement :

**Dogecoin** : `DQBggqFNWsRNTPb6kkiwppnMo1Hm8edfWq`
