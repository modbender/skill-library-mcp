# CRM Skill — Design Document

**Author:** Jarvis (design review)
**Date:** 2026-02-27
**Status:** Draft — awaiting Abe's review before implementation

---

## 1. Core Philosophy

A voice-agent CRM is not Salesforce. It's a **memory system for phone calls.**

The fundamental difference: in a web CRM, a human types structured data into forms. In a voice CRM, an AI extracts structured data from messy, real-time conversation. This means:

- **Capture must be invisible.** Amber should never say "Can I get your email for our records?" like a call center drone. She captures what people naturally share ("My name's Sarah, you can reach me at sarah@...") and fills in the rest from caller ID.
- **Phone number is the primary key.** Every call arrives with a caller ID. That's your anchor. Names, emails, and context accrue over repeated calls.
- **The CRM is append-heavy, query-light.** Amber will write on every call but only read when she needs context ("Have I spoken to this person before?"). Optimize for writes.
- **Contacts are living records.** A contact isn't a one-time capture — it's a profile that gets richer with each call. First call: just a phone number. Second call: now we have a name. Third call: they mentioned they're from Acme Corp.
- **Less is more.** Don't try to model pipelines, deals, stages, or sales funnels. That's web CRM territory. This is a **contact memory + interaction log.**

---

## 2. Data Model

### contacts table

| Field | Type | Notes |
|-------|------|-------|
| `id` | TEXT (ULID) | Primary key. ULIDs sort chronologically. |
| `phone` | TEXT | E.164 format. **Unique index.** The natural key. |
| `email` | TEXT | Nullable. Captured when volunteered. |
| `name` | TEXT | Nullable. May be partial ("Sarah") initially. |
| `company` | TEXT | Nullable. Captured when mentioned. |
| `notes` | TEXT | Freeform operator notes. Not call-derived. |
| `tags` | TEXT | JSON array string, e.g. `["vip","vendor"]`. Operator-managed. |
| `source` | TEXT | How first seen: `inbound_call`, `outbound_call`, `manual`. |
| `external_id` | TEXT | ID in external CRM (HubSpot, etc.). Nullable. |
| `created_at` | TEXT | ISO 8601 timestamp. |
| `updated_at` | TEXT | ISO 8601 timestamp. Auto-set on upsert. |

**Why not separate first/last name?** Because voice capture is messy. Someone says "It's Mike" — that's one token. Forcing first/last creates bad data. Store the full name string; let external CRM adapters split it if they need to.

### interactions table

| Field | Type | Notes |
|-------|------|-------|
| `id` | TEXT (ULID) | Primary key. |
| `contact_id` | TEXT | FK → contacts.id. Indexed. |
| `call_sid` | TEXT | Twilio/Telnyx call SID. Links to call log. |
| `direction` | TEXT | `inbound` or `outbound`. |
| `summary` | TEXT | One-liner: what the call was about. |
| `outcome` | TEXT | Enum-ish: `message_left`, `appointment_booked`, `info_provided`, `callback_requested`, `other`. |
| `details` | TEXT | JSON blob for structured extras (e.g. `{"appointment_date":"2026-03-01T14:00"}`). |
| `duration_sec` | INTEGER | Call duration if available. |
| `created_at` | TEXT | ISO 8601. When the interaction was logged. |

**What we DON'T store here:** Full transcripts. Those live in the call log JSONL (already captured by the Amber runtime). The CRM stores the *distilled* information — the summary, the outcome, the contact details. This keeps the DB lean and avoids duplicating the transcript store.

---

## 3. Built-in Database Design

### Recommendation: **SQLite**

Why SQLite over JSON/JSONL:
- **Indexing.** Looking up a contact by phone number on every inbound call must be fast. SQLite's B-tree index on `phone` is O(log n). JSONL grep is O(n).
- **Upserts.** `INSERT ... ON CONFLICT(phone) DO UPDATE` is atomic and clean. With JSONL you'd need read-parse-modify-rewrite.
- **Queries.** "Show me all interactions for this contact" is a trivial indexed query. With JSONL you'd scan the whole file.
- **Concurrency.** SQLite handles concurrent reads + serialized writes out of the box with WAL mode. Multiple calls hitting the CRM simultaneously won't corrupt data.
- **Size.** A CRM with 10K contacts and 50K interactions is ~5MB in SQLite. Trivially small.

### File Location

```
~/.config/amber/crm.sqlite
```

Not inside the skill directory (which is code, potentially git-tracked). User data goes in a config/data directory. The path should be configurable via env var `AMBER_CRM_DB_PATH` with the above as default.

### Schema DDL

```sql
CREATE TABLE IF NOT EXISTS contacts (
  id          TEXT PRIMARY KEY,
  phone       TEXT UNIQUE,
  email       TEXT,
  name        TEXT,
  company     TEXT,
  notes       TEXT,
  tags        TEXT DEFAULT '[]',
  source      TEXT DEFAULT 'inbound_call',
  external_id TEXT,
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name) WHERE name IS NOT NULL;

CREATE TABLE IF NOT EXISTS interactions (
  id           TEXT PRIMARY KEY,
  contact_id   TEXT NOT NULL REFERENCES contacts(id),
  call_sid     TEXT,
  direction    TEXT NOT NULL DEFAULT 'inbound',
  summary      TEXT,
  outcome      TEXT,
  details      TEXT DEFAULT '{}',
  duration_sec INTEGER,
  created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_interactions_call_sid ON interactions(call_sid) WHERE call_sid IS NOT NULL;
```

### Initialization

The handler auto-creates the DB file and runs migrations on first call. Use a simple `user_version` pragma for schema versioning:

```sql
PRAGMA user_version;  -- 0 = fresh, run full DDL
                      -- 1 = v1 schema, etc.
```

---

## 4. Skill Actions (API Surface)

The CRM skill exposes **one function** to Amber with an `action` discriminator (same pattern as calendar). This keeps the function_schema count low — Amber has one tool, not four.

### Function: `crm`

#### Action: `lookup_contact`

Look up a contact by phone number (primary) or name (fuzzy fallback).

```json
{
  "action": "lookup_contact",
  "phone": "+14165551234",
  "name": "Sarah"
}
```

Returns: contact record + last 5 interactions, or `null` if not found.

**When Amber uses this:** Start of every inbound call (automatic, using `context.callerId`). Also when a caller mentions someone by name ("I spoke to you last week about...").

#### Action: `upsert_contact`

Create or update a contact. Phone is the merge key.

```json
{
  "action": "upsert_contact",
  "phone": "+14165551234",
  "name": "Sarah Chen",
  "email": "sarah@acme.com",
  "company": "Acme Corp"
}
```

Only provided fields are updated; nulls/missing fields are left unchanged. Returns the full updated contact.

**When Amber uses this:** During or after a call when new info is captured ("My name is Sarah Chen, I'm with Acme").

#### Action: `log_interaction`

Log a call interaction against a contact.

```json
{
  "action": "log_interaction",
  "phone": "+14165551234",
  "summary": "Called to reschedule appointment from March 1 to March 5",
  "outcome": "appointment_booked",
  "details": {"new_date": "2026-03-05T14:00"}
}
```

If the phone number doesn't match an existing contact, one is auto-created (source: `inbound_call`). The `call_sid` is injected automatically from `context.callSid`.

**When Amber uses this:** End of every call. This is the bread and butter.

#### Action: `get_history`

Get interaction history for a contact.

```json
{
  "action": "get_history",
  "phone": "+14165551234",
  "limit": 10
}
```

Returns interactions sorted newest-first. Default limit: 10.

#### Action: `search_contacts`

Full-text search across name, email, company, notes.

```json
{
  "action": "search_contacts",
  "query": "Acme",
  "limit": 10
}
```

Uses `LIKE '%query%'` for MVP. FTS5 in v2 if needed.

#### Action: `tag_contact`

Add or remove tags.

```json
{
  "action": "tag_contact",
  "phone": "+14165551234",
  "add": ["vip"],
  "remove": ["prospect"]
}
```

### Full function_schema

```json
{
  "name": "crm",
  "description": "Manage contacts and interaction history. Use lookup_contact at the start of calls to check if the caller is known. Use upsert_contact to save new information learned during calls. Use log_interaction at the end of every call to record what happened. NEVER ask the caller robotic CRM questions — capture information naturally from conversation.",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["lookup_contact", "upsert_contact", "log_interaction", "get_history", "search_contacts", "tag_contact"],
        "description": "The CRM action to perform"
      },
      "phone": {
        "type": "string",
        "description": "Contact phone number in E.164 format (e.g. +14165551234)",
        "pattern": "^\\+[1-9]\\d{6,14}$"
      },
      "name": { "type": "string", "maxLength": 200 },
      "email": { "type": "string", "maxLength": 200 },
      "company": { "type": "string", "maxLength": 200 },
      "summary": { "type": "string", "maxLength": 500 },
      "outcome": {
        "type": "string",
        "enum": ["message_left", "appointment_booked", "info_provided", "callback_requested", "transferred", "other"]
      },
      "details": { "type": "object", "description": "Structured extras as key-value pairs" },
      "query": { "type": "string", "maxLength": 200 },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
      "add": { "type": "array", "items": { "type": "string", "maxLength": 50 }, "maxItems": 10 },
      "remove": { "type": "array", "items": { "type": "string", "maxLength": 50 }, "maxItems": 10 }
    },
    "required": ["action"]
  }
}
```

---

## 5. Handler.js Design

```
handler(params, context) {
  1. Validate action
  2. Route to action handler
  3. Each action handler:
     a. Validate inputs (same three-layer pattern as calendar)
     b. Open/init DB (lazy singleton — one connection per process lifetime)
     c. Execute query
     d. If external adapter configured, sync (fire-and-forget, don't block call)
     e. Return structured response
  4. On error: log to callLog, return graceful error message
}
```

### DB Connection Pattern

```javascript
const Database = require('better-sqlite3');
let _db = null;

function getDb() {
  if (!_db) {
    const dbPath = process.env.AMBER_CRM_DB_PATH || 
      require('path').join(require('os').homedir(), '.config/amber/crm.sqlite');
    require('fs').mkdirSync(require('path').dirname(dbPath), { recursive: true });
    _db = new Database(dbPath, { journal_mode: 'WAL' });
    migrate(_db);
  }
  return _db;
}
```

**Dependency:** `better-sqlite3` — synchronous SQLite bindings for Node.js. Fast, no async overhead for simple queries. Added to the Amber runtime's `package.json`.

### Response Shape

Every action returns:

```json
{
  "success": true|false,
  "message": "Human-readable summary for Amber to speak",
  "result": { ... }  // Structured data
}
```

This matches the calendar skill's pattern exactly.

### Auto-lookup on Call Start

The handler should support being called with just a phone number for `lookup_contact`. If no contact exists, it returns a `null` result with a message like "This is a new caller." This lets Amber naturally adapt: "Welcome back, Sarah!" vs generic greeting.

---

## 6. AGENT.md Instructions (Amber System Prompt Additions)

Add to Amber's system prompt / AGENT.md:

```markdown
## CRM — Contact Memory

You have a CRM that remembers callers across calls. Use it naturally:

### On every inbound call:
1. **Immediately** call `crm` with `lookup_contact` using the caller's phone number
2. If the caller is known: greet them by name, reference past context if relevant
3. If the caller is new: proceed normally, listen for their name

### During the call:
- When someone shares their name, email, company, or any identifying info,
  call `crm` with `upsert_contact` to save it. Do this silently — don't announce
  "I'm saving your information" or ask permission to "add them to the system."
- This should feel like a human assistant who simply *remembers* people.

### At the end of every call:
- Call `crm` with `log_interaction` — summarize what the call was about and the outcome.
- This happens silently after the call ends or as part of your wrap-up.

### What NOT to do:
- ❌ Don't ask "Can I get your name and email for our records?"
- ❌ Don't say "I'm updating your contact information"
- ❌ Don't ask for information just to fill CRM fields
- ✅ DO capture info that's naturally volunteered
- ✅ DO use CRM context to make conversations feel personal
- ✅ DO log every call's outcome, even if brief

### Greeting examples:
- Known caller: "Hi Sarah, good to hear from you again. How can I help?"
- Known caller + context: "Hi Sarah — last time we spoke you were asking about the March schedule. What can I do for you today?"
- Unknown caller: "Hello, thanks for calling. How can I help you?"
```

---

## 7. External CRM Adapter Pattern

### Adapter Interface

An adapter is a JS module that exports a standard contract:

```javascript
// adapters/hubspot.js
module.exports = {
  name: 'hubspot',
  
  // Push a contact to the external CRM. Called after upsert_contact.
  async pushContact(contact) → { externalId: string }
  
  // Pull a contact from the external CRM by phone/email.
  async pullContact(query: { phone?, email? }) → Contact | null
  
  // Push an interaction/note to the external CRM.
  async pushInteraction(contact, interaction) → { externalId: string }
  
  // Test connectivity. Called on startup.
  async healthCheck() → { ok: boolean, error?: string }
}
```

### Configuration

```env
AMBER_CRM_ADAPTER=hubspot
AMBER_CRM_HUBSPOT_API_KEY=pat-xxx
```

The handler loads the adapter dynamically:

```javascript
let adapter = null;
const adapterName = process.env.AMBER_CRM_ADAPTER;
if (adapterName) {
  adapter = require(`./adapters/${adapterName}`);
}
```

### Sync Strategy

- **Write-through, async.** On every `upsert_contact` or `log_interaction`, the handler writes to local SQLite first (synchronous, fast), then fires off the adapter push in the background. The call is never blocked by external CRM latency.
- **Pull on lookup miss.** If `lookup_contact` finds nothing locally, and an adapter is configured, try pulling from the external CRM. Cache the result locally.
- **external_id mapping.** Once a contact is pushed/pulled, store the `external_id` in the local record for future correlation.
- **Failure tolerance.** Adapter failures are logged but never surface to callers. The local DB is always the source of truth.

### MVP Adapters

Don't build any adapters for MVP. Ship the interface, document it, build adapters when Abe actually connects an external CRM. The adapter pattern exists so the handler code doesn't need to change.

---

## 8. Privacy & Security

### PII Handling

| Data | Stored? | Notes |
|------|---------|-------|
| Phone number | ✅ Yes | Core identifier. Arrives via Twilio anyway. |
| Name | ✅ Yes | Only what's volunteered by caller. |
| Email | ✅ Yes | Only what's volunteered by caller. |
| Company | ✅ Yes | Only what's volunteered by caller. |
| Call transcript | ❌ No | Lives in call log JSONL, not CRM DB. |
| Voicemail audio | ❌ No | Not CRM's concern. |
| Interaction summary | ✅ Yes | AI-generated one-liner, not raw transcript. |

### Access Controls

- **DB file permissions:** Created with mode `0600` (owner read/write only).
- **No network exposure.** The CRM DB is local. No API server, no web endpoints. Access is only through the skill handler.
- **Dashboard (if built)** runs on localhost only, behind the existing OpenClaw gateway auth.

### Data Retention

- No automatic deletion in MVP. Contacts persist indefinitely.
- v2: Add `AMBER_CRM_RETENTION_DAYS` for auto-archiving interactions older than N days.
- Operator can always manually delete via a `delete_contact` action (v2).

### Input Sanitization

Same three-layer security as calendar:
1. **Schema level** — patterns on phone, maxLength on strings, enums on action/outcome
2. **Handler level** — explicit validation, control character stripping
3. **Exec level** — N/A (no CLI calls; pure SQLite via `better-sqlite3` with parameterized queries — no SQL injection surface)

The SQLite parameterized query approach is actually *more* secure than the calendar's exec pattern since there's no subprocess at all.

---

## 9. Dashboard / Reporting

### Recommendation: Yes, build a simple HTML dashboard.

The call log dashboard already exists (`dashboard/`). The CRM dashboard should follow the same pattern: a static HTML + JS page served by the Amber runtime, reading from the SQLite DB via a small API endpoint.

### What it shows:

1. **Contact list** — searchable table: name, phone, email, company, # of interactions, last contact date, tags
2. **Contact detail** — click into a contact to see full interaction history, timeline view
3. **Recent activity** — last 20 interactions across all contacts, chronological
4. **Stats** — total contacts, calls this week/month, top callers, new vs returning ratio

### Implementation approach:

- Add 3-4 read-only API routes to the Amber runtime's Express server:
  - `GET /crm/contacts?q=&limit=&offset=`
  - `GET /crm/contacts/:id`
  - `GET /crm/contacts/:id/interactions`
  - `GET /crm/stats`
- Static HTML page with vanilla JS (no framework — matches existing dashboard pattern)
- Localhost only, same auth as existing dashboard

### Scope:

- **MVP:** Skip the dashboard entirely. The DB is inspectable via `sqlite3` CLI. Ship the skill first.
- **v1.5:** Basic contact list + interaction history page.
- **v2:** Stats, search, tag management, export.

---

## 10. Rollout Plan

### MVP (v1.0) — Ship This Week

**Goal:** Amber remembers callers and logs interactions. Zero visible change to caller experience except personalized greetings for return callers.

Scope:
- [x] SQLite database with contacts + interactions tables
- [x] `lookup_contact` — auto-called on every inbound call
- [x] `upsert_contact` — saves name/email/company from conversation
- [x] `log_interaction` — logs every call summary + outcome
- [x] `get_history` — retrieves past interactions
- [x] SKILL.md with function_schema
- [x] handler.js with full input validation
- [x] System prompt additions for natural CRM capture
- [x] Add to SKILL_MANIFEST.json

**Not in MVP:**
- No dashboard
- No external CRM adapters
- No `search_contacts` or `tag_contact`
- No data export
- No retention policies

### v1.1 — Quick Follows

- `search_contacts` action (LIKE-based search)
- `tag_contact` action
- Automatic greeting personalization (Amber references last interaction context)

### v1.5 — Dashboard

- Basic web dashboard (contact list, interaction history)
- Read-only API endpoints on Amber runtime

### v2.0 — External + Advanced

- External CRM adapter interface + first adapter (HubSpot or Airtable)
- `delete_contact` action
- Data retention / auto-archive
- FTS5 full-text search
- Contact merge (dedup by phone + email)
- Export to CSV
- Interaction sentiment field (derived from call tone)

---

## Appendix: SKILL.md Frontmatter (Ready to Use)

```yaml
---
name: crm
version: 1.0.0
description: "Contact memory and interaction log — remembers callers across calls"
metadata: {"amber": {"capabilities": ["read", "act"], "confirmation_required": false, "timeout_ms": 3000, "permissions": {"local_binaries": [], "telegram": false, "openclaw_action": false, "network": false}, "function_schema": { ... see section 4 above ... }}}
---
```

Key decisions in the frontmatter:
- **`confirmation_required: false`** — CRM writes happen silently. Unlike send-message, there's no caller-facing action to confirm.
- **`timeout_ms: 3000`** — SQLite queries are sub-millisecond. 3s is generous.
- **`permissions.network: false`** — Local DB only. External adapter sync would need this flipped to `true` in v2.
- **Capabilities: `["read", "act"]`** — Lookups are reads, upserts/logs are acts.

---

## Appendix: Dependencies

| Package | Why | Size |
|---------|-----|------|
| `better-sqlite3` | Synchronous SQLite bindings | ~2MB native |
| `ulid` | Sortable unique IDs | 3KB |

Both are well-maintained, zero-transitive-dependency packages. `better-sqlite3` requires a native build step (node-gyp) but this is standard for Node.js SQLite.

---

*End of design document. Ready for Abe's review.*
