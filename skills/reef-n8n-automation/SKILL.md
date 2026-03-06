---
name: n8n Automation — Build & Deliver Workflows Fast
description: "Build, customize, and deliver n8n workflows using our
  2,061-template library. Reference: /projects/n8n-workflows/ — browse by
  integration folder. Our n8n instance: localhost:5678 (requires fnm use ..."
---

# n8n Automation — Build & Deliver Workflows Fast

Build, customize, and deliver n8n workflows using our 2,061-template library.
Reference: `~/projects/n8n-workflows/` — browse by integration folder.
Our n8n instance: `localhost:5678` (requires `fnm use 22` before starting).
All outputs go to `workspace/artifacts/`.

## Use when
- Building an n8n workflow for a client (Upwork, Alfred, direct)
- Customizing a template from our library for a specific use case
- Debugging or optimizing an existing n8n workflow
- Designing a workflow architecture before building
- Estimating delivery time for a workflow project
- Importing/exporting workflow JSON

## Don't use when
- Finding Upwork jobs (use upwork-hunting skill)
- Writing the client proposal (use proposal-writing skill)
- General coding tasks not involving n8n
- Zapier/Make.com builds (different platforms, different nodes)

## Negative examples
- "Find me automation jobs on Upwork" → No. Use upwork-hunting.
- "Build me a Python script" → No. This is n8n-specific.
- "Set up my n8n server" → Borderline. Infrastructure setup is ops, not workflow building. But credential configuration fits here.

## Edge cases
- Workflow uses custom JavaScript (Code node) → YES. n8n supports inline JS.
- Client wants Zapier→n8n migration → YES. Map Zapier triggers/actions to n8n equivalents.
- Workflow needs external API with no n8n node → YES. Use HTTP Request node.
- Multi-workflow orchestration → YES. Use Execute Workflow node.

---

## Template Library Quick Reference

**Location:** `~/projects/n8n-workflows/workflows/`
**Structure:** `workflows/[IntegrationName]/[id]_[integration]_[action]_[trigger].json`

### Finding the Right Template
```bash
# List all templates for an integration
ls ~/projects/n8n-workflows/workflows/Twilio/

# Search across all workflows
find ~/projects/n8n-workflows/workflows/ -name "*.json" | grep -i "shopify"

# Count templates per integration
ls ~/projects/n8n-workflows/workflows/ | while read d; do echo "$(ls ~/projects/n8n-workflows/workflows/$d/ | wc -l) $d"; done | sort -rn | head -20
```

### Top Integration Folders (by Upwork demand)
| Integration | Path | Common Jobs |
|-------------|------|-------------|
| Gmail | workflows/Gmail/ | Auto-responders, lead capture, notifications |
| Google Sheets | workflows/Googlesheets/ | Data logging, reporting, sync |
| Slack | workflows/Slack/ | Notifications, bots, CRM sync |
| Twilio | workflows/Twilio/ | SMS automation, call routing, alerts |
| Telegram | workflows/Telegram/ | Chatbots, notifications, AI assistants |
| WhatsApp | workflows/Whatsapp/ | Business messaging, chatbots |
| Shopify | workflows/Shopify/ | Order notifications, inventory sync |
| HubSpot | workflows/Hubspot/ | CRM automation, lead routing |
| Calendly | workflows/Calendly/ | Booking confirmations, follow-ups |
| OpenAI | workflows/Openai/ | AI chatbots, content generation |
| Webhook | workflows/Webhook/ | Custom triggers, API integrations |
| Airtable | workflows/Airtable/ | Database sync, form processing |

---

## Workflow Building Process

### Step 1: Assess Requirements
From client discovery, answer:
- What **triggers** the workflow? (webhook, schedule, form, app event)
- What **actions** need to happen? (send email, update CRM, create record)
- What **data** needs to flow? (fields, formats, transformations)
- What **error handling** is needed? (retries, fallback, alerts)
- What **credentials** are required? (API keys, OAuth, etc.)

### Step 2: Find Matching Templates
```bash
# Search for relevant templates
find ~/projects/n8n-workflows/workflows/ -name "*.json" | xargs grep -l "keyword" 2>/dev/null
```

Or browse by integration folder. Most jobs need 2-3 templates stitched together.

### Step 3: Import & Customize
1. Copy template JSON
2. In n8n: Menu → Import from File (or paste JSON)
3. Update credentials (Client's API keys)
4. Update field mappings (their data structure)
5. Adjust trigger settings (their webhook URL, schedule, etc.)
6. Add error handling nodes (Error Trigger → notification)

### Step 4: Test
- Use n8n's **Manual Execution** to test each node step-by-step
- Verify data flows correctly between nodes
- Test error paths (what happens when an API is down?)
- Check rate limits (especially for bulk operations)

### Step 5: Document & Deliver
Every delivered workflow includes:
```
## Workflow: [Name]
**Trigger:** [What starts it]
**Steps:** [1. → 2. → 3.]
**Credentials needed:** [List]
**Testing:** [How to verify it works]
**Maintenance:** [What might break and how to fix it]
```

---

## Common Workflow Patterns

### Pattern 1: Trigger → Transform → Action
The simplest and most common. Event happens → process data → do something.
```
[Webhook/Form/Schedule] → [Set/Code node: transform data] → [Send Email/Update CRM/Create Record]
```

### Pattern 2: Trigger → Branch → Multiple Actions
Different outcomes based on conditions.
```
[Trigger] → [IF node: check condition] → True: [Action A] / False: [Action B]
```

### Pattern 3: Scheduled Batch Processing
Periodic bulk operations.
```
[Cron/Schedule] → [Get data from Sheet/DB] → [Loop: process each item] → [Action per item]
```

### Pattern 4: Webhook API Endpoint
n8n acts as an API that other services call.
```
[Webhook: receive request] → [Process] → [Respond to Webhook: return data]
```

### Pattern 5: Multi-Step Pipeline
Complex workflows with multiple stages.
```
[Trigger] → [Enrich data] → [Route/Split] → [Multiple actions] → [Aggregate] → [Final action]
```

### Pattern 6: Error-Resilient Workflow
Production-grade with error handling.
```
[Trigger] → [Try: main flow] → [Catch: Error Trigger] → [Alert via Slack/Email]
```

---

## Node Cheat Sheet

| Need | Node | Notes |
|------|------|-------|
| Custom logic | Code | JavaScript, access to all data |
| API call (no native node) | HTTP Request | Works with any REST API |
| Conditional routing | IF / Switch | Branch based on data |
| Loop over items | Split In Batches | Process items one at a time |
| Wait/delay | Wait | Pause between steps |
| Merge data | Merge | Combine data from branches |
| Transform data | Set | Rename/restructure fields |
| Schedule | Schedule Trigger | Cron expressions |
| Webhook | Webhook | Receive external HTTP calls |
| Respond | Respond to Webhook | Return data to caller |
| Error handling | Error Trigger | Catch workflow errors |
| Sub-workflow | Execute Workflow | Call another workflow |

---

## Credential Setup Checklist

Before delivering to a client, ensure:
- [ ] All credentials use THEIR API keys (never ours)
- [ ] OAuth tokens are connected to THEIR accounts
- [ ] Webhook URLs point to THEIR n8n instance (or ours if managed)
- [ ] Sensitive data isn't hardcoded in nodes (use credentials store)
- [ ] Test credentials work in production (not just sandbox)

---

## Delivery Checklist

- [ ] Workflow tested end-to-end with real data
- [ ] Error handling nodes in place
- [ ] Documentation written (trigger, steps, credentials, maintenance)
- [ ] Workflow JSON exported as backup
- [ ] Client can import and run independently
- [ ] Edge cases tested (empty data, API errors, rate limits)
- [ ] Screenshot of working workflow included in delivery

---

## Estimation Guide

| Complexity | Description | Time | Price Range |
|------------|-------------|------|-------------|
| Simple | 2-3 nodes, single trigger→action | 1-2 hrs | $100-300 |
| Standard | 4-8 nodes, branching, transforms | 2-4 hrs | $300-600 |
| Complex | 10+ nodes, multiple APIs, error handling | 4-8 hrs | $600-1,200 |
| Enterprise | Multi-workflow, database, custom code | 8-20 hrs | $1,200-3,000 |

**Our speed advantage:** Templates cut these times by 40-60%.

---

## n8n Instance Management

**Start n8n:**
```bash
eval "$(fnm env)" && fnm use 22 && nohup n8n start > /tmp/n8n.log 2>&1 &
```

**Access:** http://localhost:5678

**Import workflow via API:**
```bash
curl -X POST http://localhost:5678/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -d @workflow.json
```

**Our credentials configured:**
- Twilio API Auth (ID: 2hP5kiyhResadXrF)
- More to be added per client
