---
name: ghl-crm-for-realtors
description: "Use this skill for GoHighLevel CRM work for realtors: contact
  lookup and updates, opportunity/pipeline actions, conversation messaging,
  calendar slots, and workflow enrollment using GoHighLevel API v2."
---


# GHL CRM for Realtors

Use this skill when a user wants realtor CRM actions in GoHighLevel (GHL), including lead follow-up, pipeline movement, appointment booking context, and messaging workflows.

## Required Environment

Set these variables before running the scripts:

- `HIGHLEVEL_TOKEN` (Private Integration token)
- `HIGHLEVEL_LOCATION_ID` (sub-account location ID)

Optional runtime variables:

- `PYTHONUNBUFFERED=1`

## Setup

If the user asks to connect or set up GHL, run:

```bash
python3 scripts/setup-wizard.py
```

The wizard validates credentials and tests API connectivity.

## Primary Script

Use the helper script for direct actions:

```bash
python3 scripts/ghl-api.py <command> [args...]
```

Common commands for realtor workflows:

- `test_connection`
- `search_contacts [query]`
- `get_contact [contact_id]`
- `create_contact [json]`
- `update_contact [contact_id] [json]`
- `list_opportunities`
- `list_pipelines`
- `list_conversations`
- `send_message [contact_id] [message]`
- `list_calendars`
- `get_free_slots [calendar_id] [start_date] [end_date]`
- `list_workflows`
- `add_to_workflow [contact_id] [workflow_id]`

## Realtor-Focused Playbooks

### New Lead Intake

1. `search_contacts` to prevent duplicates.
2. If not found, `create_contact` with source tags (for example: `buyer`, `zillow`, `open-house`).
3. Add next-step task/note using supported contact endpoints.

### Pipeline Progress

1. `list_opportunities` to inspect active deals.
2. Move stage using the opportunity update command path in `ghl-api.py`.
3. Confirm stage and status in response payload.

### Follow-Up Messaging

1. Resolve contact first (`search_contacts` or `get_contact`).
2. Send message with `send_message`.
3. Re-check conversation history with `list_conversations`.

### Appointment Assist

1. `list_calendars`
2. `get_free_slots` for date range.
3. Use the calendar endpoints in script for appointment creation if requested.

## Safety Rules

- Never print or echo raw tokens in chat output.
- Prefer dry informational reads before write actions when intent is ambiguous.
- Validate contact/opportunity IDs from GHL responses instead of guessing.
- If an API error returns 401/403, stop and ask for corrected scopes or token.

## References

Load these only as needed:

- `references/contacts.md`
- `references/opportunities.md`
- `references/conversations.md`
- `references/calendars.md`
- `references/troubleshooting.md`
