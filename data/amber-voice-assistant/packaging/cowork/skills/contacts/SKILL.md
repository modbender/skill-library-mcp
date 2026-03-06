---
name: contacts
description: >
  Look up contacts by name to resolve phone numbers before making calls.
  Use when the user says "call John" instead of providing a phone number.
---

# Contacts

Resolve contact names to phone numbers for outbound calls.

## Flow

1. User says "call [name]" or "/amber:call [name] [objective]"
2. Look up the name in the CRM via `crm(action: "lookup", identifier: "name")`
3. If found, use the stored phone number
4. If multiple matches, present options and let the user choose
5. If not found, ask the user for the phone number

## Guidelines

- Be fuzzy with name matching — "John" should match "John Smith"
- If ambiguous, always confirm before dialing ("I found John Smith at +1-416-555-1234 — is that right?")
