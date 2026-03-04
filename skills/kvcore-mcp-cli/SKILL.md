---
name: kvcore-mcp-cli
description: Use this skill when users need KVcore CRM actions through MCP/CLI (contacts, tags, notes, calls, email, text, campaigns), including raw endpoint access and optional Twilio call fallback.
---

# KVcore MCP/CLI Skill

Use this skill for KVcore CRM operations from chat interfaces.

## Environment

Required:
- `KVCORE_API_TOKEN`

Optional:
- `KVCORE_BASE_URL` (default `https://api.kvcore.com`)
- `KVCORE_TIMEOUT_MS`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`

## MCP Server

Start with:

```bash
npm run dev:kvcore-mcp
```

Primary tools:
- `kvcore_contact_search`, `kvcore_contact_get`, `kvcore_contact_create`, `kvcore_contact_update`
- `kvcore_contact_tag_add`, `kvcore_contact_tag_remove`
- `kvcore_note_add`
- `kvcore_call_log`, `kvcore_call_schedule`
- `kvcore_email_send`, `kvcore_text_send`
- `kvcore_user_tasks`, `kvcore_user_calls`
- `kvcore_campaigns_refresh`
- `kvcore_request` (raw endpoint access)
- `twilio_call_create` (fallback outbound call)

## CLI

Build:

```bash
npm run build
```

Examples:

```bash
node packages/kvcore-cli/dist/index.js contact search --query "john smith" --pretty
node packages/kvcore-cli/dist/index.js email:send --contact-id 123 --subject "Quick update" --body "Following up" --pretty
node packages/kvcore-cli/dist/index.js text:send --contact-id 123 --body "Can we connect today?" --pretty
node packages/kvcore-cli/dist/index.js call:schedule --json '{"contact_id":123,"user_id":456,"scheduled_at":"2026-02-15 10:00:00"}' --pretty
node packages/kvcore-cli/dist/index.js call:twilio --to "+14165550001" --twiml "<Response><Say>Hello</Say></Response>" --pretty
```

## Scope Notes

KVcore Public API v2 supports contacts, notes, call logging, send email/text, schedule call, user task/call listing, and campaign refresh.

For endpoints not wrapped yet, use `kvcore_request` or CLI `raw`.
