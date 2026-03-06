---
name: newsletter-automation
description: Complete newsletter management system with subscriber signup (double opt-in), automated welcome drip sequence, broadcast sender, and subscriber analytics. 4 production-ready n8n workflows with Google Sheets backend.
tags: [newsletter, email, subscribers, drip, automation, marketing, n8n, google-sheets]
author: mhmalvi
version: 1.2.0
license: CC BY-NC-SA 4.0
metadata:
  clawdbot:
    emoji: "\U0001F4EC"
    requires:
      n8nCredentials: [google-sheets-oauth2, smtp]
      env: [NEWSLETTER_ADMIN_EMAIL, NEWSLETTER_BASE_URL, NEWSLETTER_SECRET]
    os: [linux, darwin, win32]
---

# Newsletter Automation

A complete newsletter management system built on n8n and Google Sheets. Handles subscriber signups with double opt-in, automated welcome drip emails, broadcast sending, and daily analytics reports.

## Problem

Running a newsletter manually means juggling signup forms, confirmation emails, welcome sequences, and broadcast sends across multiple tools. Most newsletter platforms charge per subscriber, and you lose control of your data.

This system gives you a free, self-hosted newsletter pipeline using n8n and Google Sheets.

## What It Does

1. **Double Opt-In Signup** — Webhook receives signups, validates email, sends confirmation link, stores in Sheets
2. **Welcome Drip Sequence** — Automatically sends Day 0 (welcome), Day 3 (tips), Day 7 (resources) emails
3. **Broadcast Sender** — API-triggered broadcast to all confirmed subscribers with unsubscribe links
4. **Daily Analytics** — Subscriber counts, growth metrics, confirmation rates, top sources

## Included Workflows

| # | File | Purpose |
|---|------|---------|
| 01 | `01-subscriber-signup.json` | Webhook signup with validation, double opt-in, and Sheets storage |
| 02 | `02-welcome-sequence.json` | Scheduled drip emails at Day 0, 3, and 7 |
| 03 | `03-broadcast-sender.json` | Webhook-triggered broadcast to all confirmed subscribers |
| 04 | `04-subscriber-analytics.json` | Daily metrics report email |

## Architecture

```
Signup Form (website)
    |
    v
Workflow 01: Subscriber Signup
    |
    +-> Validate email
    +-> Save to Google Sheets (status: pending)
    +-> Send confirmation email (double opt-in)
    +-> Return success response

User clicks confirmation link
    |
    v
Update Sheets (status: confirmed)

Scheduled (every 6 hours):
    |
    v
Workflow 02: Welcome Drip Sequence
    +-> Read confirmed subscribers
    +-> Check drip schedule (Day 0/3/7)
    +-> Send appropriate email
    +-> Update last_drip_day in Sheets

API Trigger:
    |
    v
Workflow 03: Broadcast Sender
    +-> Validate request + auth
    +-> Fetch confirmed subscribers
    +-> Send broadcast email to each
    +-> Include unsubscribe link

Daily Schedule:
    |
    v
Workflow 04: Subscriber Analytics
    +-> Read all subscribers
    +-> Calculate metrics (total, growth, rates)
    +-> Email report to admin
```

## Required n8n Credentials

| Credential Type | Used For | Placeholder in JSON |
|----------------|----------|---------------------|
| Google Sheets OAuth2 | Subscriber storage | `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` |
| SMTP (Gmail or custom) | All emails (confirmation, drip, broadcast, reports) | `YOUR_SMTP_CREDENTIAL_ID` |

## Environment Variables

```bash
# Required
NEWSLETTER_ADMIN_EMAIL=admin@yourbusiness.com
NEWSLETTER_BASE_URL=https://yourdomain.com
NEWSLETTER_SECRET=your-broadcast-api-secret
```

## Configuration Placeholders

| Placeholder | Description |
|-------------|-------------|
| `YOUR_SUBSCRIBERS_SHEET_ID` | Google Sheet ID for subscriber data |
| `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` | n8n Google Sheets credential ID |
| `YOUR_SMTP_CREDENTIAL_ID` | n8n SMTP credential ID |
| `YOUR_NOTIFICATION_EMAIL` | Fallback admin email (also set via `NEWSLETTER_ADMIN_EMAIL` env) |
| `YOUR_DOMAIN` | Fallback domain (also set via `NEWSLETTER_BASE_URL` env) |

## Google Sheets Schema (Subscribers)

| Column | Type | Description |
|--------|------|-------------|
| email | text | Primary key, subscriber email |
| name | text | Subscriber name |
| status | text | pending / confirmed / unsubscribed |
| source | text | Where they signed up (website, landing-page, etc.) |
| subscribed_at | datetime | Signup timestamp |
| confirmed | boolean | Whether email is confirmed |
| token | text | Confirmation token |
| last_drip_day | number | Last drip sent (0, 3, or 7) |
| last_drip_at | datetime | When last drip was sent |

## Quick Start

### 1. Prerequisites
- n8n v2.4+ (self-hosted)
- Google Sheets OAuth2 credentials
- SMTP email credentials

### 2. Create Subscriber Sheet
Create a Google Sheet with the columns above. Name the sheet tab "Subscribers".

### 3. Import Workflows
Import all 4 JSON files into n8n. Replace all `YOUR_*` placeholders.

### 4. Test Signup
```bash
curl -X POST https://your-n8n.com/webhook/newsletter/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User", "source": "api-test"}'
```

### 5. Test Broadcast
```bash
curl -X POST https://your-n8n.com/webhook/newsletter/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "_secret": "your-newsletter-secret",
    "subject": "Test Broadcast",
    "content": "<p>This is a test broadcast.</p>"
  }'
```

## Use Cases

1. **Personal newsletters** — Self-hosted alternative to Substack or ConvertKit
2. **Business newsletters** — Weekly updates to customers with zero per-subscriber cost
3. **Product updates** — Notify users about new features and releases
4. **Community newsletters** — Manage subscriber lists for communities or organizations
5. **Content creators** — Build an audience with automated drip sequences

## Requirements

- n8n v2.4+ (self-hosted recommended)
- Google Sheets OAuth2 credentials
- SMTP email credentials (Gmail, SES, or custom)
