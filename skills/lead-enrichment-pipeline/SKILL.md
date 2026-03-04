---
name: lead-enrichment-pipeline
description: Automated lead capture, deduplication, tracking, and notification pipeline. Captures leads from web forms via webhooks, deduplicates by email in Google Sheets, scores by source and engagement, sends team notifications. 3 production-ready n8n workflows included.
tags: [leads, crm, google-sheets, sales, pipeline, automation, b2b, prospecting, webhooks, n8n]
author: mhmalvi
version: 1.2.0
license: CC BY-NC-SA 4.0
metadata:
  clawdbot:
    emoji: "🎯"
    requires:
      n8nCredentials: [google-sheets-oauth2, smtp]
    os: [linux, darwin, win32]
---

# Lead Capture & Tracking Pipeline 🎯

Capture leads from any source, deduplicate by email, score by intent, track in Google Sheets, and notify your team — all automatically via n8n workflows.

## Problem

Leads come from multiple sources (website forms, newsletters, strategy calls, product waitlists). Manually entering them into a CRM and following up is error-prone and slow. Hot leads go cold.

This pipeline captures, deduplicates, scores, and routes leads in real-time.

## What It Does

1. **Capture** — Receives leads from webhooks (website forms, landing pages, chatbots)
2. **Deduplicate** — Checks Google Sheets for existing leads (email match via `appendOrUpdate`)
3. **Score** — Basic lead scoring based on source type and engagement signals
4. **Store** — Appends to Google Sheets with scoring data
5. **Notify** — Emails team with lead details and suggested next action

> **Note:** This pipeline does not include third-party enrichment integrations (e.g., Clearbit, FullContact). To add enrichment, insert an HTTP Request node between the webhook and the Sheets node in the workflow, calling your preferred enrichment API.

## Included Workflows

| # | File | Purpose |
|---|------|---------|
| 1 | `lead-tracker.json` | Webhook → deduplicate → store in Sheets → notify owner |
| 2 | `lead-magnet.json` | Lead magnet download → store lead → send PDF attachment email |
| 3 | `newsletter.json` | Newsletter signup → store subscriber → send welcome email |

## Architecture

```
Lead Source (form, chatbot, API)
    │
    ▼
Webhook Endpoint (n8n)
    │
    ├── Validate required fields (name, email)
    ├── Check for duplicates (email match in Sheets)
    │
    ├── IF new lead:
    │   ├── Score lead (source type + available fields)
    │   ├── Append to Google Sheets
    │   └── Send notification email to team
    │
    └── IF existing lead:
        ├── Update engagement count
        └── Log new touchpoint
```

## Required n8n Credentials

You must create these credentials in your n8n instance before importing:

| Credential Type | Used For | Placeholder in JSON |
|----------------|----------|---------------------|
| Google Sheets OAuth2 | Reading/writing lead data | `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` |
| SMTP (Gmail or custom) | Sending notification and welcome emails | `YOUR_SMTP_CREDENTIAL_ID` |

After importing, open each workflow and reconnect the credential nodes to your own credentials.

## Configuration Placeholders

Replace these placeholders in the workflow JSON before deploying:

| Placeholder | Description |
|-------------|-------------|
| `YOUR_LEADS_SHEET_ID` | Your Google Sheet ID for lead tracking |
| `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` | Your n8n Google Sheets credential ID |
| `YOUR_SMTP_CREDENTIAL_ID` | Your n8n SMTP credential ID |
| `YOUR_FROM_EMAIL` | Sender email address |
| `YOUR_NOTIFICATION_EMAIL` | Where to send lead notifications |
| `YOUR_NAME` | Your name for email templates |
| `YOUR_DOMAIN` | Your website domain for email links |

## Supported Lead Sources

| Source | Webhook Path | Fields |
|--------|-------------|--------|
| Newsletter signup | `/webhook/newsletter` | email |
| Lead magnet download | `/webhook/lead-magnet` | name, email, company |
| Strategy call booking | `/webhook/strategy-call` | name, email, phone, company, message |
| Product waitlist | `/webhook/product-waitlist` | name, email |
| Contact form | `/webhook/contact` | name, email, subject, message |
| Custom | `/webhook/add-lead-enriched` | Any JSON payload |

## Google Sheets Schema

| Column | Type | Description |
|--------|------|-------------|
| name | text | Full name |
| email | text | Email address (primary key for dedup) |
| company | text | Company name |
| phone | text | Phone number |
| source | text | Where they came from |
| score | number | Lead score (0-100) |
| status | text | new / contacted / qualified / converted |
| created_at | date | First captured |
| updated_at | date | Last activity |
| touchpoints | number | Total interactions |
| notes | text | Additional notes |

## Quick Start

### 1. Prerequisites
- n8n v2.4+ (self-hosted or cloud)
- Google Sheets API credentials (OAuth2)
- SMTP email credentials (Gmail or custom)

### 2. Create Tracking Sheet
Set up a Google Sheet with the columns above. Enable `appendOrUpdate` matching on `email` column to prevent duplicates.

### 3. Import Workflows
Import the 3 JSON files from the `workflows/` directory into n8n. Replace all `YOUR_*` placeholders with your actual values.

### 4. Test
```bash
curl -X POST https://your-n8n.com/webhook/add-lead-enriched \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@company.com",
    "company": "Acme Inc",
    "source": "website-contact"
  }'
```

## Lead Scoring

| Factor | Points | Example |
|--------|--------|---------|
| Source: Strategy call | +40 | High intent |
| Source: Lead magnet | +25 | Medium intent |
| Source: Newsletter | +10 | Low intent |
| Has company name | +10 | B2B signal |
| Has phone number | +15 | Ready to talk |
| Repeat visitor | +10 per touchpoint | Engaged |

## Use Cases

1. **Freelancers** — Track inbound leads from website contact forms
2. **Agencies** — Multi-source lead capture with team notifications
3. **SaaS** — Waitlist management with scoring
4. **Content creators** — Newsletter subscriber tracking with engagement scoring
5. **eCommerce** — Customer inquiry pipeline

## Requirements

- n8n v2.4+ (self-hosted or cloud)
- Google Sheets OAuth2 credentials
- SMTP email credentials
