---
name: sophiie
description: Manage your Sophiie sales pipeline — leads, inquiries, appointments, FAQs, policies, SMS, and calls via the Sophiie REST API.
metadata:
  openclaw:
    requires:
      env:
        - SOPHIIE_API_KEY
      bins:
        - curl
        - jq
    primaryEnv: SOPHIIE_API_KEY
    emoji: "📞"
    homepage: https://docs.sophiie.ai
    files:
      - SKILL.md
      - README.md
      - scripts/sophiie.sh
---

# Sophiie — Sales Pipeline Management

Sophiie is a B2B SaaS platform for sales pipeline management. Organizations get AI-powered virtual assistant agents that handle calls, SMS, and lead management. This skill lets you manage your Sophiie pipeline via natural language.

## Authentication

All requests use `Authorization: Bearer <key>` where the key is `SOPHIIE_API_KEY`. Keys are prefixed `sk_live_*` (production) or `sk_test_*` (sandbox).

- **Base URL**: `https://api.sophiie.ai`
- **Rate limit**: 60 requests/minute
- **All responses**: JSON

## External Endpoints

| Method | URL | Data Sent |
|--------|-----|-----------|
| GET | `https://api.sophiie.ai/v1/leads` | Query: page, limit |
| GET | `https://api.sophiie.ai/v1/leads/{id}` | None |
| POST | `https://api.sophiie.ai/v1/leads` | Body: firstName, lastName, email, phone, suburb, businessName, socials |
| PUT | `https://api.sophiie.ai/v1/leads/{id}` | Body: firstName, lastName, email, phone, suburb, businessName, socials |
| DELETE | `https://api.sophiie.ai/v1/leads/{id}` | None |
| GET | `https://api.sophiie.ai/v1/leads/{id}/notes` | Query: page, limit |
| GET | `https://api.sophiie.ai/v1/leads/{id}/activities` | Query: page, limit |
| GET | `https://api.sophiie.ai/v1/inquiries` | Query: page, limit, leadId, expand |
| GET | `https://api.sophiie.ai/v1/inquiries/{id}` | None |
| GET | `https://api.sophiie.ai/v1/appointments` | Query: page, limit, leadId |
| POST | `https://api.sophiie.ai/v1/calls` | Body: name, phoneNumber, mode, custom_instructions |
| POST | `https://api.sophiie.ai/v1/sms` | Body: userId, leadId, message, messageThreadId |
| GET | `https://api.sophiie.ai/v1/faqs` | Query: page, limit |
| POST | `https://api.sophiie.ai/v1/faqs` | Body: question, answer, isActive |
| PUT | `https://api.sophiie.ai/v1/faqs/{id}` | Body: question, answer, isActive |
| DELETE | `https://api.sophiie.ai/v1/faqs/{id}` | None |
| GET | `https://api.sophiie.ai/v1/policies` | Query: page, limit |
| POST | `https://api.sophiie.ai/v1/policies` | Body: title, content, isActive |
| PUT | `https://api.sophiie.ai/v1/policies/{id}` | Body: title, content, isActive |
| DELETE | `https://api.sophiie.ai/v1/policies/{id}` | None |
| GET | `https://api.sophiie.ai/v1/members` | Query: page, limit |
| GET | `https://api.sophiie.ai/v1/organization` | None |
| GET | `https://api.sophiie.ai/v1/organization/availability` | None |
| GET | `https://api.sophiie.ai/v1/organization/members` | Query: page, limit |
| GET | `https://api.sophiie.ai/v1/organization/services` | None |
| GET | `https://api.sophiie.ai/v1/organization/products` | None |

## Security & Privacy

- The `SOPHIIE_API_KEY` is **never** logged, printed, or echoed in output
- All requests use **HTTPS only**
- No data is cached locally — every command fetches live from the API
- All user input is sanitized via `jq -n` (never string-interpolated into JSON bodies)
- The skill has **read-only access** to `SOPHIIE_API_KEY` — it cannot modify or delete the environment variable

## Command Reference

All commands are run via `scripts/sophiie.sh <domain> <action> [options]`.

### Leads

**`leads list`** — List all leads in the pipeline
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when the user wants to see their pipeline, check leads, or browse contacts.

**`leads get <id>`** — Get full details for a specific lead
Use when the user asks about a specific lead by name or ID. Lead IDs start with `ld_`.

**`leads create`** — Create a new lead
```
--firstName <name>      Required (min 2 chars)
--suburb <suburb>       Required
--lastName <name>       Optional
--email <email>         Optional (valid email)
--phone <number>        Optional (E.164 format, e.g. +61412345678)
--businessName <name>   Optional
--instagram <handle>    Optional
--facebook <handle>     Optional
```
Use when the user wants to add a new contact or lead to their pipeline.

**`leads update <id>`** — Update an existing lead
Same options as create, but all are optional. At least one field must be provided.
Use when the user wants to change lead details.

**`leads delete <id>`** — Delete a lead (soft delete)
Use when the user explicitly asks to remove a lead. **Always confirm before deleting.**

**`leads notes <id>`** — List notes for a lead
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when the user asks about notes or history on a specific lead.

**`leads activities <id>`** — List activity log for a lead
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when the user wants to see what happened with a lead (timeline, events).

### Inquiries

**`inquiries list`** — List all inquiries
```
--page <n>       Page number (default: 1)
--limit <n>      Items per page (default: 50, max: 100)
--leadId <id>    Filter by lead ID (ld_...)
--expand <type>  Expand related data: "external", "lead", or "both"
```
Use when the user asks about incoming inquiries, messages, or calls received.

**`inquiries get <id>`** — Get full inquiry details with source data
Returns the inquiry with expanded source data (call transcripts, SMS messages, webform submissions, etc.) depending on the inquiry source type (CALL, SMS, EMAIL, CHATBOT, WEBFORM).
Use when the user wants details on a specific inquiry.

### FAQs

**`faqs list`** — List all FAQs
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when the user wants to see their knowledge base or FAQ entries.

**`faqs create`** — Create a new FAQ
```
--question <text>    Required (max 255 chars)
--answer <text>      Required
--isActive <bool>    Optional (true/false)
```
Use when the user wants to add to their AI agent's knowledge base.

**`faqs update <id>`** — Update an FAQ (ID is a number)
Same options as create, all optional.
Use when the user wants to change an existing FAQ entry.

**`faqs delete <id>`** — Delete an FAQ (soft delete)
**Always confirm before deleting.**

### Policies

**`policies list`** — List all policies
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when the user asks about their business policies.

**`policies create`** — Create a new policy
```
--title <text>      Required (min 2, max 255 chars)
--content <text>    Required (min 2 chars)
--isActive <bool>   Optional (true/false)
```
Use when the user wants to add a business policy for their AI agent.

**`policies update <id>`** — Update a policy (ID is a number)
Same options as create, all optional.

**`policies delete <id>`** — Delete a policy (soft delete)
**Always confirm before deleting.**

### Communication

**`calls send`** — Initiate an outbound AI call
```
--name <name>                 Required — name of person being called
--phoneNumber <number>        Required — E.164 format (e.g. +61412345678)
--mode <mode>                 Optional — "normal" (default) or "transfer_only"
--custom_instructions <text>  Optional — required when mode is "transfer_only"
```
Use when the user wants to call someone. **Always confirm the phone number before calling.**

**`sms send`** — Send an SMS message
```
--userId <id>             Required — sender user ID (usr_...)
--leadId <id>             Required — recipient lead ID (ld_...)
--message <text>          Required — message text (min 2 chars)
--messageThreadId <n>     Optional — existing thread ID (number); omit to start new thread
```
Use when the user wants to text a lead. You need to know the userId — use `members list` first if needed.

### Appointments

**`appointments list`** — List all appointments
```
--page <n>       Page number (default: 1)
--limit <n>      Items per page (default: 50, max: 100)
--leadId <id>    Filter by lead ID (ld_...)
```
Use when the user asks about upcoming appointments or scheduled meetings.

### Organization

**`org get`** — Get organization details (name, timezone, currency, etc.)
Use when the user asks about their org settings or business info.

**`org availability`** — Get business hours / availability schedules
Use when the user asks about working hours or availability.

**`org members`** — List organization members with roles
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when the user asks about team members (returns membership-level data with positions/avatars).

**`org services`** — List services offered (grouped by category)
Use when the user asks about their service offerings.

**`org products`** — List products offered (grouped by category)
Use when the user asks about their product catalog.

### Members

**`members list`** — List all organization members
```
--page <n>    Page number (default: 1)
--limit <n>   Items per page (default: 50, max: 100)
```
Use when you need user IDs (usr_...) for operations like sending SMS. Returns user-level data with roles.

## Decision Guide

| User intent | Command(s) |
|-------------|-----------|
| "Check my pipeline" / "Show leads" | `leads list` |
| "Tell me about [lead name]" | `leads list` → find by name → `leads get <id>` |
| "Add a new lead" / "New contact" | `leads create` |
| "Update [lead]'s phone number" | `leads update <id> --phone <number>` |
| "Remove this lead" | `leads delete <id>` (confirm first) |
| "What inquiries came in?" | `inquiries list` |
| "Show me that call transcript" | `inquiries get <id>` |
| "Any appointments today?" | `appointments list` |
| "Call [person]" / "Ring [number]" | `calls send` (confirm number first) |
| "Text [lead] about [topic]" | `members list` → get userId → `sms send` |
| "Update the knowledge base" | `faqs list` → then `faqs create` or `faqs update` |
| "Add a refund policy" | `policies create` |
| "What are our business hours?" | `org availability` |
| "Who's on the team?" | `members list` or `org members` |
| "What services do we offer?" | `org services` |

## Pagination

All list endpoints return paginated responses:
```json
{
  "items": [...],
  "totalPages": 5,
  "currentPage": 1,
  "totalCount": 237
}
```

- Default: page 1, 50 items per page
- Maximum: 100 items per page
- **Always check `totalPages`** — if there are more pages, tell the user and offer to fetch the next page

## Error Reference

| Code | Meaning | What to tell the user |
|------|---------|----------------------|
| 401 | Invalid or missing API key | "Your API key appears to be invalid. Check SOPHIIE_API_KEY." |
| 404 | Resource not found | "That [lead/inquiry/etc.] wasn't found. Double-check the ID." |
| 409 | Conflict (duplicate lead) | "A lead with that info already exists." |
| 429 | Rate limited | "Too many requests. Wait a moment and try again." |
| 500 | Server error | "Something went wrong on Sophiie's end. Try again shortly." |

Error responses have this shape:
```json
{
  "success": false,
  "message": "...",
  "error": { "status": 401, "message": "..." }
}
```
