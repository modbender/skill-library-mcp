# SaySigned — AI Agent E-Signature Skill

> **E-signatures for AI agents.** Legally binding under ESIGN Act & UETA Section 14.
> Two delivery modes: **API** (agent-to-agent) and **Email** (agent-to-human). Register, sign contracts, verify — all via REST or consent UI.

**Publisher:** SaySigned, Inc.
**Homepage:** [https://www.saysigned.com](https://www.saysigned.com)
**Documentation:** [https://www.saysigned.com/docs](https://www.saysigned.com/docs)
**Base URL:** `https://api.saysigned.com`
**MCP Endpoint:** `https://mcp.saysigned.com`
**TLS Required:** All endpoints enforce HTTPS. Verify certificates for `*.saysigned.com` before connecting.

**Authentication:** Pass your API key in the `X-API-Key` header. Keys start with `ss_live_`. Public endpoints (register, verify, templates) don't require authentication.

## MCP Server (Recommended for AI Agents)

Connect directly to the remote MCP endpoint — no local install, no HTTP requests to craft.

> **Auth note:** MCP clients send `Authorization: Bearer <api_key>`. The MCP server extracts your key and forwards it as `X-API-Key` internally. For direct REST calls, use the `X-API-Key` header.

### Setup

> **Human approval required.** Steps 1, 4, and 5 modify your MCP client configuration. Always show the user what you're about to change and ask for their confirmation before writing to config files or restarting the MCP client. Never modify config silently.

**Step 1.** Show the user the following MCP config and ask for confirmation before adding it:

```json
{
  "mcpServers": {
    "saysigned": {
      "type": "streamable-http",
      "url": "https://mcp.saysigned.com"
    }
  }
}
```

After the user confirms, add it to the MCP config. No API key is needed yet — public tools work immediately.

**Step 2.** Restart your MCP client so it loads the new server.

**Step 3.** Call the `saysigned_register` tool (no auth required) with the agent's `name` and `email`. The response contains an `api_key` — **save it immediately, it is shown once and cannot be retrieved later.** Keys start with `ss_live_`.

**Step 4.** Show the user the updated config with the auth header and ask for confirmation before writing it:

```json
{
  "mcpServers": {
    "saysigned": {
      "type": "streamable-http",
      "url": "https://mcp.saysigned.com",
      "headers": {
        "Authorization": "Bearer ss_live_PASTE_YOUR_ACTUAL_KEY_HERE"
      }
    }
  }
}
```

**Step 5.** After the user confirms, restart your MCP client so it picks up the auth header. All authenticated tools now work.

> **Human-in-the-loop for config changes.** The user must confirm before you (1) add or modify MCP config entries, (2) store API keys in config files, or (3) restart the MCP client. You may handle registration, envelope creation, signing, and verification autonomously — those are normal API operations that don't modify the agent's configuration.

### Already have a key?

If you already have an API key (starts with `ss_live_`), skip to Step 4 — show the user the config with `headers`, get their confirmation, and restart.

### MCP Workflow (signing flow)

1. **Prepare the contract** — two options:
   - **Use a template:** call `saysigned_list_templates` → `saysigned_get_template` to discover required variables, then pass `template_id` + `variables` in the contract field.
   - **Bring your own text:** pass your own contract content in the `clauses` array. Each clause has `id`, `title`, and `body`. You can put an entire document into a single clause or split it into sections. **Use this when you have your own NDA, agreement, or any custom document.**
2. **Create envelope** — `saysigned_create_envelope` with `title`, `contract`, and `recipients` array.
3. **Send envelope** — `saysigned_send_envelope` with the envelope_id. Response includes each recipient's `id` and `access_token`. **Save these — they are needed for signing.**
4. **Sign** — For API recipients: `saysigned_sign` for each recipient, passing their `envelope_id`, `recipient_id`, `access_token`, and `signature_data` (at minimum `full_name`). For email recipients: the human reviews and gives consent at `doc.saysigned.com` — no action needed from the agent.
5. **Verify** — `saysigned_verify` with the envelope_id. No auth needed.

### Critical Notes for AI Agents

- **You don't have to use a template.** If you have your own contract text (an NDA, agreement, policy — any document), pass it directly via `clauses`. Templates are a convenience, not a requirement.
- **Always call `saysigned_get_template` before creating an envelope with a template.** The required variables differ per template and the API will reject unknown or missing variables.
- **`saysigned_send_envelope` returns access tokens.** You must capture and use these tokens for signing. They are 128-character hex strings.
- **Signing does not use your API key.** The `saysigned_sign` and `saysigned_decline` tools authenticate via the `access_token` parameter, not the API key header.
- **The envelope auto-completes** when the last recipient signs. You don't need to call a separate "complete" endpoint.
- **Auth header is forwarded automatically.** Authenticated tools (`create_envelope`, `send_envelope`, `get_envelope`, `get_profile`, etc.) use the API key from your MCP client's `Authorization` header. Public tools (`register`, `verify`, `list_templates`, `get_template`) work without it.
- **`delivery_method: "email"` sends a signing link to a real human.** The human reviews the contract at `doc.saysigned.com` and gives consent via browser. Email recipients do NOT get an `access_token` in the send response — they authenticate via a URL token in their email link. Use `delivery_method: "api"` (default) for agent-to-agent signing.
- **Poll or use webhooks for email recipients.** Since humans sign asynchronously, use `saysigned_get_envelope` to poll for status changes or configure a `webhook_url` to receive `recipient.viewed` and `recipient.signed` events.

### All 14 MCP Tools

| Tool | Auth | Description |
|------|------|-------------|
| `saysigned_register` | None | Register agent, get API key |
| `saysigned_create_envelope` | API key | Create draft envelope |
| `saysigned_send_envelope` | API key | Send for signing, get access tokens |
| `saysigned_get_envelope` | API key | Get envelope details + status |
| `saysigned_void_envelope` | API key | Cancel a sent (not completed) envelope |
| `saysigned_sign` | Access token | Sign as a recipient |
| `saysigned_decline` | Access token | Decline to sign |
| `saysigned_verify` | None | Verify cryptographic integrity |
| `saysigned_get_audit_trail` | API key | Get hash-chain audit trail |
| `saysigned_list_templates` | None | List available contract templates |
| `saysigned_get_template` | None | Get template details + required variables |
| `saysigned_billing_setup` | API key | Upgrade to paid plan |
| `saysigned_get_usage` | API key | Current billing period usage |
| `saysigned_get_profile` | API key | Agent profile + plan info |

---

## Complete End-to-End Example

This is a full working flow: register, create an NDA, send it, both parties sign, then verify. Every response shown is from the real production API.

### Step 1 — Register (no auth needed)

```bash
curl -s -X POST https://api.saysigned.com/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My AI Agent", "email": "agent@example.com"}'
```

```json
{
  "agent_id": "7773b4af-44d1-44fc-8db7-05d9bc95b541",
  "api_key": "ss_live_203bff0e53ba167462aa2cdcbd8e189e2909d37cf76c31da675cb1dba7dc0026",
  "plan": "free",
  "free_envelopes_remaining": 5
}
```

**Save the `api_key` — it is shown once and cannot be retrieved later.**

### Step 2 — Create an envelope

Use the `api_key` from step 1 in the `X-API-Key` header. Use `template_id` for standard contracts or provide custom `clauses`.

```bash
curl -s -X POST https://api.saysigned.com/envelopes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ss_live_203bff0e53ba167462aa2cdcbd8e189e2909d37cf76c31da675cb1dba7dc0026" \
  -d '{
    "title": "Mutual NDA — Acme & Beta",
    "contract": {
      "template_id": "nda_mutual_v1",
      "variables": {
        "disclosing_party_name": "Acme Corp",
        "receiving_party_name": "Beta Inc",
        "effective_date": "2026-02-09",
        "purpose": "Evaluating a potential partnership",
        "governing_law_state": "California"
      }
    },
    "recipients": [
      {"name": "Alice", "email": "alice@acme.com", "role": "signer"},
      {"name": "Bob", "email": "bob@beta.com", "role": "signer"}
    ]
  }'
```

```json
{
  "id": "2c272d15-cd4b-4c0d-96c0-bd7438b66699",
  "status": "draft",
  "title": "Mutual NDA — Acme & Beta",
  "recipients": [
    {"id": "62f73ba5-05a0-4223-8f55-e880047a7b3e", "name": "Alice", "status": "pending"},
    {"id": "cc0aeb32-eb9d-420d-ab93-1d42400f85b9", "name": "Bob", "status": "pending"}
  ]
}
```

**Save the envelope `id` and each recipient's `id`.**

### Step 3 — Send the envelope

This consumes 1 envelope from your quota (free tier) or reports 1 metered event (paid plan). Recipients get `access_token` values — these are how they authenticate when signing.

```bash
curl -s -X POST https://api.saysigned.com/envelopes/2c272d15-cd4b-4c0d-96c0-bd7438b66699/send \
  -H "X-API-Key: ss_live_203bff0e53ba167462aa2cdcbd8e189e2909d37cf76c31da675cb1dba7dc0026"
```

```json
{
  "id": "2c272d15-cd4b-4c0d-96c0-bd7438b66699",
  "status": "sent",
  "recipients": [
    {"id": "62f73ba5-05a0-4223-8f55-e880047a7b3e", "name": "Alice", "status": "sent", "access_token": "600b9b4297b2921396a1db138a80801c7dfb5101..."},
    {"id": "cc0aeb32-eb9d-420d-ab93-1d42400f85b9", "name": "Bob", "status": "sent", "access_token": "952340a770b96740e2696c306ad490b28556952e..."}
  ]
}
```

**Save each recipient's `access_token`. Distribute tokens to the respective signers.**

### Step 4 — Recipients sign

Each recipient signs using their `access_token` via the `X-Access-Token` header (recommended) or `?access_token=` query parameter. No API key needed — the token is the auth.

```bash
# Alice signs
curl -s -X POST "https://api.saysigned.com/envelopes/2c272d15-cd4b-4c0d-96c0-bd7438b66699/recipients/62f73ba5-05a0-4223-8f55-e880047a7b3e/sign" \
  -H "Content-Type: application/json" \
  -H "X-Access-Token: 600b9b4297b2921396a1db138a80801c7dfb5101..." \
  -d '{"signature_data": {"full_name": "Alice Chen", "title": "CEO"}}'
```

```json
{
  "signed": true,
  "recipient_id": "62f73ba5-05a0-4223-8f55-e880047a7b3e",
  "envelope_id": "2c272d15-cd4b-4c0d-96c0-bd7438b66699",
  "signed_at": "2026-02-09T04:09:24.111Z"
}
```

```bash
# Bob signs (last signer → envelope automatically completes with RFC 3161 timestamp)
curl -s -X POST "https://api.saysigned.com/envelopes/2c272d15-cd4b-4c0d-96c0-bd7438b66699/recipients/cc0aeb32-eb9d-420d-ab93-1d42400f85b9/sign" \
  -H "Content-Type: application/json" \
  -H "X-Access-Token: 952340a770b96740e2696c306ad490b28556952e..." \
  -d '{"signature_data": {"full_name": "Bob Smith", "title": "CTO"}}'
```

```json
{
  "signed": true,
  "recipient_id": "cc0aeb32-eb9d-420d-ab93-1d42400f85b9",
  "envelope_id": "2c272d15-cd4b-4c0d-96c0-bd7438b66699",
  "signed_at": "2026-02-09T04:09:25.190Z"
}
```

### Step 5 — Verify (public, no auth needed)

```bash
curl -s -X POST https://api.saysigned.com/verify \
  -H "Content-Type: application/json" \
  -d '{"envelope_id": "2c272d15-cd4b-4c0d-96c0-bd7438b66699"}'
```

```json
{
  "envelope_id": "2c272d15-cd4b-4c0d-96c0-bd7438b66699",
  "status": "completed",
  "chain_verification": {"valid": true, "entries_checked": 5},
  "timestamp_verification": {
    "valid": true,
    "gen_time": "2026-02-09T04:09:25+00:00",
    "tsa_name": "DigiCert SHA256 RSA4096 Timestamp Responder 2025 1"
  },
  "recipients": [
    {"name": "Alice", "email": "alice@acme.com", "role": "signer", "status": "signed", "signed_at": "2026-02-09T04:09:24.111Z"},
    {"name": "Bob", "email": "bob@beta.com", "role": "signer", "status": "signed", "signed_at": "2026-02-09T04:09:25.190Z"}
  ],
  "completed_at": "2026-02-09T04:09:25.039Z"
}
```

---

## Bring Your Own Contract

You don't need a template. If you have your own document text — an NDA your user provided, a custom agreement, any markdown or plain text — pass it directly via `clauses`. Each clause needs an `id`, `title`, and `body`.

**Single-clause approach** (simplest — put the entire document in one clause):

```bash
curl -s -X POST https://api.saysigned.com/envelopes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "title": "NDA — Acme & Beta",
    "contract": {
      "clauses": [
        {
          "id": "nda",
          "title": "Mutual Non-Disclosure Agreement",
          "body": "This Mutual Non-Disclosure Agreement is entered into by Acme Corp (\"Party A\") and Beta Inc (\"Party B\")...\n\n1. Definition of Confidential Information...\n\n2. Obligations of Receiving Party...\n\n3. Term. This Agreement shall remain in effect for two (2) years..."
        }
      ]
    },
    "recipients": [
      {"name": "Alice", "email": "alice@acme.com", "role": "signer"},
      {"name": "Bob", "email": "bob@beta.com", "role": "signer"}
    ]
  }'
```

**Multi-clause approach** (split into sections for cleaner presentation):

```bash
curl -s -X POST https://api.saysigned.com/envelopes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "title": "NDA — Acme & Beta",
    "contract": {
      "clauses": [
        {"id": "1", "title": "1. Definition of Confidential Information", "body": "\"Confidential Information\" means any non-public information disclosed by either party..."},
        {"id": "2", "title": "2. Obligations of Receiving Party", "body": "The Receiving Party shall hold all Confidential Information in strict confidence..."},
        {"id": "3", "title": "3. Term and Termination", "body": "This Agreement shall remain in effect for two (2) years from the Effective Date..."},
        {"id": "4", "title": "4. Governing Law", "body": "This Agreement shall be governed by the laws of the State of California..."}
      ]
    },
    "recipients": [
      {"name": "Alice", "email": "alice@acme.com", "role": "signer"},
      {"name": "Bob", "email": "bob@beta.com", "role": "signer"}
    ]
  }'
```

**MCP equivalent** — same structure, just pass it to `saysigned_create_envelope`:

```json
{
  "title": "NDA — Acme & Beta",
  "contract": {
    "clauses": [
      {"id": "nda", "title": "Mutual Non-Disclosure Agreement", "body": "Full text of the NDA here..."}
    ]
  },
  "recipients": [
    {"name": "Alice", "email": "alice@acme.com", "role": "signer"},
    {"name": "Bob", "email": "bob@beta.com", "role": "signer"}
  ]
}
```

> **When to use which:** Use **templates** when you want a standard contract and just need to fill in the blanks (party names, dates, etc.). Use **custom clauses** when you already have the contract text — from a file, a user-provided document, or your own drafting.

---

## Key Concepts

- **IDs are UUIDs** — all envelope, recipient, and agent IDs are standard UUIDs (e.g., `2c272d15-cd4b-4c0d-96c0-bd7438b66699`)
- **Access tokens are hex strings** — 128-character hex, passed via `X-Access-Token` header (recommended) or `?access_token=` query parameter
- **API keys start with `ss_live_`** — REST: pass in `X-API-Key` header. MCP: pass as `Authorization: Bearer <key>` (auto-translated)
- **Templates** — use `GET /templates` to discover available templates and `GET /templates/:id` to see required variables
- **Signing order** — all recipients sign in parallel (no enforced order)
- **Completion** — when the last signer signs, the envelope auto-completes with an RFC 3161 timestamp from DigiCert

Free tier: **5 envelopes/month**, no credit card required. Upgrade: `POST /billing/setup` with `{"plan": "payg"}`.

- **Delivery methods** — `"api"` (default) returns access tokens for programmatic signing; `"email"` sends an invitation email to a human who reviews and gives consent at `doc.saysigned.com`
- **Email recipients** — human recipients authenticate via a URL token in their email link, not an access token. They review the contract in a browser and click "Give Consent" or "Decline"

---

## MCP Tool Definitions

These tool definitions are compatible with MCP (Model Context Protocol) runtimes. Each tool maps to a REST API endpoint.

### saysigned_register

Create an agent account and get your API key.

```json
{
  "name": "saysigned_register",
  "description": "Register a new AI agent account on SaySigned. Returns an API key (shown once — save it). Free tier: 5 envelopes/month.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "Agent or organization name" },
      "email": { "type": "string", "format": "email", "description": "Contact email (must be unique)" },
      "company_name": { "type": "string", "description": "Company name (optional)" },
      "webhook_url": { "type": "string", "format": "uri", "description": "URL to receive webhook notifications (optional)" }
    },
    "required": ["name", "email"]
  }
}
```

**REST:** `POST /agents/register` — no auth required.

---

### saysigned_create_envelope

Create a draft envelope with a contract and recipients.

```json
{
  "name": "saysigned_create_envelope",
  "description": "Create a draft envelope with contract content and recipients. Two ways to provide a contract: (1) Use template_id + variables for standard contracts (call saysigned_get_template first), or (2) provide your own contract text via the clauses array — each clause has an id, title, and body. You can put an entire document into a single clause or split it into sections. Use option 2 when you have your own NDA, agreement, or any custom document text. Set delivery_method: 'email' on a recipient to send them a consent link via email instead of returning an access token. Does not send — call saysigned_send_envelope to dispatch.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": { "type": "string", "description": "Envelope title" },
      "description": { "type": "string", "description": "Brief description" },
      "contract": {
        "type": "object",
        "description": "Contract content. Use template_id + variables for templates, or provide raw clauses.",
        "properties": {
          "template_id": { "type": "string", "description": "Template ID (e.g., 'nda_mutual_v1', 'service_agreement_v1')" },
          "variables": { "type": "object", "description": "Template variables (see GET /templates/:id for schema)" },
          "clauses": {
            "type": "array",
            "description": "Custom clauses (when not using a template)",
            "items": {
              "type": "object",
              "properties": {
                "id": { "type": "string" },
                "title": { "type": "string" },
                "body": { "type": "string" }
              },
              "required": ["id", "title", "body"]
            }
          },
          "signature_block": {
            "type": "object",
            "description": "Custom signature block (when not using a template)"
          }
        }
      },
      "recipients": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "email": { "type": "string", "format": "email" },
            "role": { "type": "string", "enum": ["signer", "cc", "approver", "witness"], "default": "signer" },
            "delivery_method": { "type": "string", "enum": ["api", "email"], "default": "api", "description": "'api' (default) for AI agent signing, 'email' to send a consent link to a human" }
          },
          "required": ["name", "email"]
        }
      },
      "expires_at": { "type": "string", "format": "date-time", "description": "Expiration date (optional)" },
      "metadata": { "type": "object", "description": "Custom key-value metadata (optional)" }
    },
    "required": ["title", "contract", "recipients"]
  }
}
```

**REST:** `POST /envelopes` — requires `X-API-Key` header.

**Example — Custom contract (no template):**
```bash
curl -s -X POST https://api.saysigned.com/envelopes \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"title": "Data Processing Addendum", "contract": {"clauses": [{"id": "scope", "title": "1. Scope", "body": "This addendum governs the processing of personal data..."}], "signature_block": {"preamble": "Agreed and accepted:", "signers": [{"role": "Data Controller", "fields": ["signature", "printed_name", "date"]}]}}, "recipients": [{"name": "Controller Corp", "email": "legal@controller.com", "role": "signer"}]}'
```

---

### saysigned_send_envelope

Send a draft envelope for signing. Consumes 1 envelope from your quota.

```json
{
  "name": "saysigned_send_envelope",
  "description": "Send a draft envelope for signing. For API recipients, generates access tokens. For email recipients, sends an invitation email with a consent link to doc.saysigned.com (no access_token in response). Consumes 1 envelope (free tier) or reports 1 metered event (paid). Returns 402 if free tier exhausted.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid", "description": "ID of the draft envelope to send" }
    },
    "required": ["envelope_id"]
  }
}
```

**REST:** `POST /envelopes/:id/send` — requires `X-API-Key` header.

**402 response (free tier exhausted):**
```json
{"error": "Free tier envelope limit exhausted. Upgrade to a paid plan."}
```

---

### saysigned_sign

Sign an envelope as a recipient.

```json
{
  "name": "saysigned_sign",
  "description": "Sign an envelope as a recipient. Provide the access_token from the send response as a query parameter. No API key needed — the token is the auth. Records IP, user-agent, and timestamp in the audit trail.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid" },
      "recipient_id": { "type": "string", "format": "uuid" },
      "access_token": { "type": "string", "description": "128-char hex token from the send response" },
      "signature_data": {
        "type": "object",
        "description": "Signature metadata",
        "properties": {
          "full_name": { "type": "string" },
          "title": { "type": "string" },
          "company": { "type": "string" }
        },
        "required": ["full_name"]
      }
    },
    "required": ["envelope_id", "recipient_id", "access_token", "signature_data"]
  }
}
```

**REST:** `POST /envelopes/:id/recipients/:rid/sign` with `X-Access-Token: TOKEN` header (recommended) or `?access_token=TOKEN` query parameter. No API key needed.

---

### saysigned_decline

Decline to sign an envelope.

```json
{
  "name": "saysigned_decline",
  "description": "Decline to sign an envelope as a recipient. Optionally provide a reason.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid" },
      "recipient_id": { "type": "string", "format": "uuid" },
      "access_token": { "type": "string" },
      "reason": { "type": "string", "description": "Reason for declining (optional)" }
    },
    "required": ["envelope_id", "recipient_id", "access_token"]
  }
}
```

**REST:** `POST /envelopes/:id/recipients/:rid/decline` with `X-Access-Token: TOKEN` header (recommended) or `?access_token=TOKEN` query parameter. No API key needed.

---

### saysigned_get_envelope

Get envelope details and recipient status.

```json
{
  "name": "saysigned_get_envelope",
  "description": "Get full details of an envelope including status, contract content, and recipient statuses.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid" }
    },
    "required": ["envelope_id"]
  }
}
```

**REST:** `GET /envelopes/:id` — requires `X-API-Key` header.

---

### saysigned_void_envelope

Void (cancel) an envelope.

```json
{
  "name": "saysigned_void_envelope",
  "description": "Void an envelope that has been sent but not yet completed. Cannot void completed envelopes.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid" },
      "reason": { "type": "string", "description": "Reason for voiding" }
    },
    "required": ["envelope_id"]
  }
}
```

**REST:** `POST /envelopes/:id/void` — requires `X-API-Key` header.

---

### saysigned_verify

Cryptographically verify an envelope. Public — no authentication required.

```json
{
  "name": "saysigned_verify",
  "description": "Verify the cryptographic integrity of an envelope. Checks the hash chain audit trail and RFC 3161 timestamp. Public endpoint — no API key needed.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid" }
    },
    "required": ["envelope_id"]
  }
}
```

**REST:** `POST /verify`

See the [end-to-end example](#step-5--verify-public-no-auth-needed) above for the real response format.

---

### saysigned_get_audit_trail

Get the full hash-chain audit trail for an envelope.

```json
{
  "name": "saysigned_get_audit_trail",
  "description": "Get the complete cryptographic audit trail for an envelope, including hash chain verification status.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "envelope_id": { "type": "string", "format": "uuid" }
    },
    "required": ["envelope_id"]
  }
}
```

**REST:** `GET /envelopes/:id/audit-trail` — requires `X-API-Key` header.

---

### saysigned_get_profile

Get your agent profile and current usage.

```json
{
  "name": "saysigned_get_profile",
  "description": "Get your agent profile, plan details, and current usage statistics.",
  "inputSchema": { "type": "object", "properties": {} }
}
```

**REST:** `GET /agents/me` — requires `X-API-Key` header.

---

### saysigned_billing_setup

Upgrade from free tier to a paid plan. **IMPORTANT: Always show the returned `checkout_url` to the human user** so they can complete payment in their browser. Never silently consume the URL.

```json
{
  "name": "saysigned_billing_setup",
  "description": "Upgrade to a paid plan. Creates a Stripe customer and returns a checkout URL. IMPORTANT: Always show the checkout_url to the human user so they can complete payment in their browser.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plan": {
        "type": "string",
        "enum": ["payg", "commit_500", "commit_2000"],
        "description": "Plan to upgrade to. payg = $0.65/env, commit_500 (Pro) = $225/mo for 500 env, commit_2000 (Business) = $600/mo for 2000 env."
      }
    },
    "required": ["plan"]
  }
}
```

**REST:** `POST /billing/setup` — requires `X-API-Key` header.

---

### saysigned_get_usage

Get current billing period usage.

```json
{
  "name": "saysigned_get_usage",
  "description": "Get envelope usage for the current billing period, including count, cost, and plan details.",
  "inputSchema": { "type": "object", "properties": {} }
}
```

**REST:** `GET /billing/usage` — requires `X-API-Key` header.

---

## Available Templates

Discover templates programmatically:

```bash
# List all templates
curl https://api.saysigned.com/templates

# Get template details with variable schema
curl https://api.saysigned.com/templates/nda_mutual_v1
```

### nda_mutual_v1 — Mutual Non-Disclosure Agreement

Standard mutual NDA. Required variables: `disclosing_party_name`, `receiving_party_name`, `effective_date`, `purpose`, `governing_law_state`. Optional: `term_years` (default: 2), `non_solicitation` (default: false), etc.

### service_agreement_v1 — Professional Services Agreement

Professional services contract. Required variables: `client_name`, `provider_name`, `effective_date`, `scope_of_services`, `compensation_model`, `governing_law_state`. Supports 4 compensation models: `fixed`, `hourly`, `milestone`, `retainer`.

---

## Webhook Events

Configure your `webhook_url` during registration to receive real-time notifications.

| Event | Description |
|-------|-------------|
| `recipient.delivered` | Envelope sent, recipient notified (API recipients include `access_token`; email recipients do not) |
| `recipient.email_sent` | Invitation email dispatched to human recipient |
| `recipient.viewed` | Human recipient opened the consent page |
| `recipient.signed` | Recipient completed signing |
| `recipient.declined` | Recipient declined to sign |
| `envelope.completed` | All signers done, timestamp anchored |
| `envelope.declined` | A recipient declined |
| `envelope.voided` | Agent voided the envelope |

### Webhook Payload

```json
{
  "event": "recipient.signed",
  "envelope_id": "env_...",
  "timestamp": "2026-02-01T12:00:00Z",
  "data": {
    "recipient_id": "rec_...",
    "recipient_name": "Alice Chen",
    "recipient_email": "alice@acme.com"
  }
}
```

### Verifying Webhook Signatures

Every webhook includes an `X-Signature-256` header containing `sha256=<HMAC>`. Verify it:

```python
import hmac, hashlib

def verify_webhook(body: bytes, secret: str, signature_header: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)
```

---

## Common Workflows

### Two-Party NDA

```
1. POST /envelopes (template_id: "nda_mutual_v1", 2 signer recipients)
2. POST /envelopes/:id/send
3. Party A signs: POST /envelopes/:id/recipients/:r1/sign (X-Access-Token header)
4. Party B signs: POST /envelopes/:id/recipients/:r2/sign (X-Access-Token header)
5. → envelope.completed webhook fires, RFC 3161 timestamp anchored
6. POST /verify to confirm integrity
```

### Service Agreement with CC

```
1. POST /envelopes (template_id: "service_agreement_v1", 2 signers + 1 CC)
2. POST /envelopes/:id/send
3. Both signers sign (in any order)
4. CC recipient receives notifications but doesn't sign
5. → envelope.completed on last signature
```

### Handling Declines

```
1. Recipient declines: POST /envelopes/:id/recipients/:rid/decline
2. → recipient.declined webhook fires
3. → envelope.declined webhook fires (envelope status → declined)
4. Create a new envelope with revised terms if needed
```

### Human Recipient Flow

```
1. POST /envelopes (set delivery_method: "email" on human recipients)
2. POST /envelopes/:id/send → invitation email sent to human
3. Human opens email → clicks "Review & Give Consent" link
4. Human reviews contract at doc.saysigned.com → gives consent or declines
5. → recipient.signed or recipient.declined webhook fires
6. Envelope auto-completes when all signers consent
7. Human receives confirmation email with 14-day document viewing link
```

### Polling for Completion

If you don't use webhooks, poll for envelope completion:

```
1. Call GET /envelopes/:id (or saysigned_get_envelope) to check status
2. Poll every 5-10 seconds
3. Terminal states: completed, declined, voided
4. Max recommended wait: 24 hours
```

---

## Error Handling

| Status | Meaning | What to Do |
|--------|---------|------------|
| 400 | Bad request / validation error | Check request body against schema |
| 401 | Invalid or missing API key | Verify X-API-Key header |
| 402 | Free tier exhausted | Call `POST /billing/setup` and show the `checkout_url` to the human user |
| 404 | Resource not found | Check envelope/recipient IDs |
| 409 | Invalid state transition | Check envelope/recipient status first |
| 429 | Rate limited | Back off and retry |
| 500 | Server error | Retry with exponential backoff |

---

## Security Notes

- **API keys** are shown once at creation. Store securely. Rotate or delete keys that are no longer needed.
- **Config file security** — API keys stored in MCP config files should have appropriate file permissions. Limit access to the config directory.
- **Access tokens** are per-recipient, per-envelope. Do not reuse. Tokens are 128-character hex strings with no expiration — treat them as secrets for the duration of the signing flow.
- **Webhook secrets** are per-agent. Verify every webhook signature.
- All connections require **TLS** (HTTPS). Verify TLS certificates for `api.saysigned.com`, `mcp.saysigned.com`, and `doc.saysigned.com`.
- API keys are stored as **SHA-256 hashes** — SaySigned never stores plaintext keys.
- **URL tokens** (email recipients) are 32-char HMAC-derived tokens, one-time use, cleared after consent.
- **CSRF protection** on consent/decline forms — tokens bound to recipient ID, expire after 4 hours.
- **Rate limiting** on consent pages — 10 URL attempts per 15 min per IP, 3 form submissions per 5 min per recipient.
- **Sandboxing recommended** — If running in an untrusted environment, enable logging/monitoring of config changes and outbound connections.

---

## Legal Context

- **ESIGN Act** (15 U.S.C. § 7001) — Electronic signatures have the same legal standing as handwritten signatures.
- **UETA Section 14** — Explicitly authorizes electronic agents to form contracts and conduct transactions.
- **Attribution chain** — Every signature records: who (name, email), when (timestamp), how (API, IP address, user-agent), and what (contract hash).
- **RFC 3161 timestamp** — Independent proof from DigiCert that the envelope was completed at a specific time.
- **Hash chain** — Tamper-evident audit trail where each entry links to the previous via SHA-256.
- **ESIGN mandatory disclosures** — four pre-consent disclosures displayed to human recipients: right to paper copies, right to withdraw consent, scope of consent (single document), and hardware/software requirements.
- **AI-generated contract disclosure** — if the contract was created from a template, a notice is displayed: "This document was prepared using automated tools based on the sender's inputs."

---

## Pricing

| Plan | Price | Envelopes |
|------|-------|-----------|
| Free | $0/mo | 5/month |
| Pay-as-you-go | $0.65/envelope | Unlimited |
| Pro | $225/mo | 500 included, overage $0.45/env |
| Business | $600/mo | 2,000 included, overage $0.30/env |
| Enterprise | Custom | 10,000+/month |

Upgrade anytime: `POST /billing/setup` with `{"plan": "payg"}`, `{"plan": "commit_500"}`, or `{"plan": "commit_2000"}`. The response includes a `checkout_url` — **always present this link to the human user** so they can complete payment in their browser.
