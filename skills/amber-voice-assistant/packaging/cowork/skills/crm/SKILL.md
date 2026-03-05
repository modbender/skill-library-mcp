---
name: crm
description: >
  Contact memory and interaction log. Remembers callers across calls,
  stores personal context, and logs every conversation. Use when looking
  up a contact, adding notes about someone, or reviewing interaction history.
---

# CRM — Contact Memory

Amber remembers everyone she talks to. The CRM stores contact details,
personal context, and a log of every interaction.

## MCP Tools

### crm
Manage contacts and interaction history.
- `action` (string, required): "lookup", "create", "update", "log", "history"
- `identifier` (string): Phone number or name to look up
- `name` (string): Contact name
- `phone` (string): Phone number
- `email` (string): Email address
- `notes` (string): Personal context or notes about the contact
- `tags` (array): Tags for categorization (e.g., ["client", "vendor", "friend"])

## Automatic Behavior

- On inbound calls, Amber automatically looks up the caller by phone number
- If the caller is known, their context and history are loaded into the conversation
- After every call, an interaction log entry is created with: date, summary, sentiment, outcome
- New callers are automatically added to the CRM after their first call

## Guidelines

- Use the CRM to personalize interactions ("Welcome back, Sarah! Last time we spoke about...")
- Keep notes professional but useful — preferences, important dates, relationship context
- Never expose CRM data to callers beyond what's socially appropriate
