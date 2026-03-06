---
name: ghl-crm
description: GoHighLevel CRM integration — manage contacts, pipelines, conversations (SMS/email/WhatsApp), calendars, appointments, and workflows through the GHL API v2. The definitive GHL skill for OpenClaw. Use when managing leads, booking appointments, sending follow-ups, or automating your CRM.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, GoHighLevel account with API v2 access
metadata: {"openclaw": {"emoji": "\ud83d\udcde", "requires": {"env": ["GHL_API_KEY"]}, "primaryEnv": "GHL_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# GHL CRM — GoHighLevel Integration for OpenClaw

Complete GoHighLevel CRM integration. Manage contacts, pipelines, conversations, appointments, and workflows through the GHL API v2.

## Quick Start

```bash
export GHL_API_KEY="your-private-integration-token"
export GHL_LOCATION_ID="your-location-id"
python3 {baseDir}/scripts/ghl_api.py contacts search "john@example.com"
```

## Authentication

GHL uses **Private Integration Tokens** (API v2). Get yours from:
1. Go to **Settings → Integrations → Private Integrations** in your GHL sub-account
2. Create a new integration, enable the scopes you need
3. Copy the API key — this is your `GHL_API_KEY`

The `GHL_LOCATION_ID` is your sub-account/location ID (found in Settings → Business Info or the URL).

**Base URL:** `https://services.leadconnectorhq.com`

**Auth header:** `Authorization: Bearer <GHL_API_KEY>` + `Version: 2021-07-28`

## Available Commands

### Contact Management
```bash
# Search contacts by email, phone, or name
python3 {baseDir}/scripts/ghl_api.py contacts search "query"

# Get contact by ID
python3 {baseDir}/scripts/ghl_api.py contacts get <contactId>

# Create a new contact
python3 {baseDir}/scripts/ghl_api.py contacts create '{"firstName":"John","lastName":"Doe","email":"john@example.com","phone":"+15551234567"}'

# Update contact
python3 {baseDir}/scripts/ghl_api.py contacts update <contactId> '{"tags":["vip","hot-lead"]}'

# Delete contact
python3 {baseDir}/scripts/ghl_api.py contacts delete <contactId>

# List contacts (with optional limit)
python3 {baseDir}/scripts/ghl_api.py contacts list --limit 20
```

### Pipeline & Opportunity Management
```bash
# List all pipelines
python3 {baseDir}/scripts/ghl_api.py pipelines list

# List opportunities in a pipeline
python3 {baseDir}/scripts/ghl_api.py opportunities list <pipelineId>

# Get opportunity details
python3 {baseDir}/scripts/ghl_api.py opportunities get <opportunityId>

# Create opportunity
python3 {baseDir}/scripts/ghl_api.py opportunities create '{"pipelineId":"...","stageId":"...","contactId":"...","name":"Deal Name","monetaryValue":5000}'

# Update opportunity (move stage, update value)
python3 {baseDir}/scripts/ghl_api.py opportunities update <opportunityId> '{"stageId":"new-stage-id","status":"won"}'

# Delete opportunity
python3 {baseDir}/scripts/ghl_api.py opportunities delete <opportunityId>
```

### Conversations (SMS, Email, WhatsApp)
```bash
# List recent conversations
python3 {baseDir}/scripts/ghl_api.py conversations list

# Get conversation messages
python3 {baseDir}/scripts/ghl_api.py conversations get <conversationId>

# Send SMS
python3 {baseDir}/scripts/ghl_api.py conversations send-sms <contactId> "Hello! Following up on our call."

# Send email
python3 {baseDir}/scripts/ghl_api.py conversations send-email <contactId> '{"subject":"Follow Up","body":"<p>Hi there!</p>","emailFrom":"you@domain.com"}'
```

### Calendar & Appointments
```bash
# List calendars
python3 {baseDir}/scripts/ghl_api.py calendars list

# Get free slots
python3 {baseDir}/scripts/ghl_api.py calendars slots <calendarId> --start 2026-02-16 --end 2026-02-17

# Create appointment
python3 {baseDir}/scripts/ghl_api.py appointments create '{"calendarId":"...","contactId":"...","startTime":"2026-02-16T10:00:00Z","endTime":"2026-02-16T10:30:00Z","title":"Discovery Call"}'

# List appointments
python3 {baseDir}/scripts/ghl_api.py appointments list <calendarId>

# Update appointment
python3 {baseDir}/scripts/ghl_api.py appointments update <appointmentId> '{"status":"confirmed"}'

# Delete appointment
python3 {baseDir}/scripts/ghl_api.py appointments delete <appointmentId>
```

### Workflows
```bash
# Add contact to workflow
python3 {baseDir}/scripts/ghl_api.py workflows add-contact <workflowId> <contactId>

# Remove contact from workflow  
python3 {baseDir}/scripts/ghl_api.py workflows remove-contact <workflowId> <contactId>
```

## Key API Endpoints Reference

| Resource | Method | Endpoint |
|----------|--------|----------|
| Search contacts | GET | `/contacts/search?query=...&locationId=...` |
| Get contact | GET | `/contacts/{id}` |
| Create contact | POST | `/contacts/` |
| Update contact | PUT | `/contacts/{id}` |
| List pipelines | GET | `/opportunities/pipelines?locationId=...` |
| List opportunities | GET | `/opportunities/search?location_id=...&pipeline_id=...` |
| Create opportunity | POST | `/opportunities/` |
| List conversations | GET | `/conversations/search?locationId=...` |
| Send message | POST | `/conversations/messages` |
| List calendars | GET | `/calendars/?locationId=...` |
| Get free slots | GET | `/calendars/{id}/free-slots?startDate=...&endDate=...` |
| Create appointment | POST | `/calendars/events/appointments` |

## Rate Limits

GHL API v2 enforces rate limits:
- **General:** 100 requests/10 seconds per location
- **Bulk operations:** 10 requests/10 seconds
- The script auto-retries on 429 with exponential backoff (up to 3 retries)

## Integration Patterns

### Lead Capture → CRM Pipeline
1. Capture lead via form/chatbot
2. `contacts create` with lead data
3. `opportunities create` to add to pipeline
4. `workflows add-contact` to trigger nurture sequence

### Appointment Booking Flow
1. `calendars list` to find the right calendar
2. `calendars slots` to get availability
3. `appointments create` to book the slot
4. GHL auto-sends confirmation via configured workflow

### Follow-Up Automation
1. `conversations list` to find unresponded conversations
2. `contacts get` for context
3. Generate follow-up with AI
4. `conversations send-sms` or `send-email`

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
