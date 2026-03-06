---
name: airtable-participants
description: >
  Read and query retreat participant data from the Ceremonia Airtable base.
  Use this skill when asked about participants, subscriber counts, retreat
  attendance, contact segments, phone numbers, emails, or donation status.
  Also used by other skills (email-newsletter, sms-outreach) to retrieve
  recipient lists. Read-only by default.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - AIRTABLE_API_KEY
      bins:
        - curl
        - jq
    primaryEnv: AIRTABLE_API_KEY
    emoji: "contacts"
    homepage: https://airtable.com/developers/web/api/introduction
---

# Airtable Participants Skill

## Purpose

Query retreat participant data from the Ceremonia Airtable base. This is the
authoritative source of truth for who receives emails and SMS messages.
Access is read-only by default — record modifications require Austin's
explicit instruction per change.

## Required Setup

Ensure AIRTABLE_API_KEY is set in .env.

You will also need:
- **Base ID:** [VERIFY — find in Airtable API docs at airtable.com/developers or ask Austin]
- **Table name:** [VERIFY — confirm the participant table name with Austin]

Store confirmed values in TOOLS.md and MEMORY.md once verified.

## Expected Data Structure

Participant records are expected to have at minimum these fields:

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Full name |
| email | Email | Primary email address |
| phone | Phone | E.164 format preferred (+1XXXXXXXXXX) |
| retreat_status | Select | e.g., active, alumni, prospective, unsubscribed |
| tags | Multi-select | e.g., february-2026, guide-circle, donor |
| last_contact | Date | Most recent outreach date |
| donation_status | Select | e.g., donor, non-donor |

[VERIFY actual field names with Austin on first use — update this section when confirmed]

## Common Query Patterns

### Get all active participants (for newsletter sends)
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?filterByFormula={retreat_status}='active'&fields[]=name&fields[]=email" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq '.records[].fields'
```

### Get participants with phone numbers (for SMS campaigns)
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?filterByFormula=AND({retreat_status}='active',{phone}!='')&fields[]=name&fields[]=phone" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq '.records[].fields'
```

### Get participant count by status
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?fields[]=retreat_status" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq '[.records[].fields.retreat_status] | group_by(.) | map({status: .[0], count: length})'
```

### Get participants by tag
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?filterByFormula=FIND('february-2026',ARRAYJOIN({tags}))" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq '.records[].fields'
```

Note: Airtable paginates at 100 records. Use the offset parameter from the response to fetch subsequent pages:
```bash
curl -s "https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}?offset={OFFSET_TOKEN}" \
  -H "Authorization: Bearer $AIRTABLE_API_KEY" | jq .
```
Always paginate fully before reporting totals or building recipient lists.

## Behavior Rules

- Read-only by default — never PATCH, POST, or DELETE Airtable records without Austin's explicit instruction per operation
- When building a recipient list for email or SMS: always filter out records where retreat_status is 'unsubscribed'
- Never include email addresses or phone numbers in Slack messages — summarize counts and segments only
- If a query returns 0 results unexpectedly: report the issue to Austin rather than sending to an empty list
- Paginate all list queries fully — do not report partial counts or build partial recipient lists
- If Airtable API returns an error: surface it to Austin immediately with the error code and message

## Record Modification (Requires Austin Approval)

When Austin instructs a record change (e.g., marking someone unsubscribed, updating last_contact):
1. Confirm the specific change with Austin before executing
2. Execute the PATCH request
3. Log the change in memory/logs/crm-writes/YYYY-MM-DD.md with: record name/email, field changed, old value, new value, Austin's instruction timestamp

## Example Invocations

- "How many active participants do we have?"
- "Get the email list for the February retreat attendees"
- "Who attended the last three retreats?"
- "How many people have phone numbers in the system?"
- "Mark [name] as unsubscribed" (requires Austin approval)
- "Pull the full active participant list for the newsletter"
- "How many people joined since January?"
