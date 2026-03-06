---
name: crm
version: 1.0.0
description: "Contact memory and interaction log — remembers callers across calls, logs every conversation with outcome and personal context"
metadata: {"amber": {"capabilities": ["read", "act"], "confirmation_required": false, "timeout_ms": 3000, "permissions": {"local_binaries": [], "telegram": false, "openclaw_action": false, "network": false}, "function_schema": {"name": "crm", "description": "Manage contacts and interaction history. Use lookup_contact at the start of inbound calls (automatic, using caller ID) to check if the caller is known and retrieve their history and personal context. Use upsert_contact to save new information learned during calls (name, email, company) — do this silently, never announce it. Use log_interaction at the end of every call to record what happened (summary, outcome). Use context_notes to store and update personal details about the caller (pet names, preferences, mentioned life details, etc.) — update context_notes at the end of calls to synthesize new information with what was known before. NEVER ask robotic CRM questions. NEVER announce you are saving information. Capture what people naturally volunteer and remember it for next time.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["lookup_contact", "upsert_contact", "log_interaction", "get_history", "search_contacts", "tag_contact"], "description": "The CRM action to perform"}, "phone": {"type": "string", "description": "Contact phone number in E.164 format (e.g. +14165551234)", "pattern": "^\\+[1-9]\\d{6,14}$|^$"}, "name": {"type": "string", "maxLength": 200}, "email": {"type": "string", "maxLength": 200}, "company": {"type": "string", "maxLength": 200}, "context_notes": {"type": "string", "maxLength": 1000, "description": "Free-form personal context: pet names, preferences, life details, callback patterns. AI-maintained, rewritten after each call."}, "summary": {"type": "string", "maxLength": 500, "description": "One-liner: what the call was about"}, "outcome": {"type": "string", "enum": ["message_left", "appointment_booked", "info_provided", "callback_requested", "transferred", "other"], "description": "Call outcome"}, "details": {"type": "object", "description": "Structured extras as key-value pairs (e.g. appointment_date, purpose)"}, "query": {"type": "string", "maxLength": 200}, "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10}, "add": {"type": "array", "items": {"type": "string", "maxLength": 50}, "maxItems": 10}, "remove": {"type": "array", "items": {"type": "string", "maxLength": 50}, "maxItems": 10}}, "required": ["action"]}}}}
---

# CRM Skill — Contact Memory for Voice Calls

Remembers callers across calls and logs every conversation.

## How It Works

### On Every Inbound Call

1. **Lookup** — Call `crm` with `lookup_contact` using the caller's phone number (from Twilio caller ID).
2. **If known** — Greet by name and use `context_notes` to personalize (ask about their dog, remember their preference, etc.)
3. **If unknown** — Proceed normally, listen for their name.

### During the Call

When someone shares their name, email, company, or any personal detail, silently upsert it via `crm.upsert_contact`. Don't announce this.

### At End of Call

1. Log the interaction: `log_interaction` with summary + outcome
2. Update context_notes with any new personal details learned, synthesizing with what was known before

### On Outbound Calls

Same exact flow: lookup at start, upsert + log_interaction at end.

## API Reference

| Action | Purpose |
|--------|---------|
| `lookup_contact` | Fetch contact + last 5 interactions + context_notes. Returns null if not found. |
| `upsert_contact` | Create or update a contact by phone. Only provided fields are updated. |
| `log_interaction` | Log a call: summary, outcome, details. Auto-creates contact if needed. |
| `get_history` | Get past interactions for a contact (sorted newest-first). |
| `search_contacts` | Search by name, email, company, notes. |
| `tag_contact` | Add/remove tags (e.g. "vip", "callback_later"). |

## Privacy

- **Event details stay private.** Like the calendar skill, never disclose event details to callers.
- **CRM context is personal.** The `context_notes` field is for Amber's internal memory, not for sharing call transcripts. Use it to inform conversation, not to recite it.
- **PII storage.** Phone, name, email, company, context_notes are stored locally in SQLite. No network transmission, no external CRM by default.

## Security

- Synchronous SQLite (better-sqlite3) with parameterized queries — no SQL injection surface
- Private number detection — calls from anonymous/blocked numbers are skipped entirely
- Input validation at three levels: schema patterns, handler validation, database constraints
- Database file created with mode 0600 (owner read/write only)

## Examples

**Greeting a known caller:**
```
Amber: "Hi Sarah, good to hear from you again. How's Max doing?" 
[context_notes remembered: "Has a Golden Retriever named Max. Prefers afternoon calls."]
```

**Capturing new info silently:**
```
Caller: "By the way, I got married last month!"
Amber: [silently calls upsert_contact + updates context_notes with "Recently married"]
Amber (aloud): "That's wonderful! Congrats!"
```

**End-of-call log:**
```
Amber: [calls log_interaction: summary="Called to reschedule Friday appointment", outcome="appointment_booked"]
Amber: [calls upsert_contact with context_notes: "Prefers afternoon calls. Recently married. Reschedules frequently but always shows up."]
```
