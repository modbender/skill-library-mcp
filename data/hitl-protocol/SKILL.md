---
name: hitl-protocol
description: "HITL Protocol — the open standard for human decisions in autonomous agent workflows. When a website or API needs human input, it returns HTTP 202 with a review URL. Autonomous agents like OpenClaw, Claude, Codex, or Goose forward the URL, poll for the structured result, and continue. Use this skill to make any website agent-ready, or to handle human-in-the-loop responses in your agent. Covers approval, selection, input forms, confirmation, and escalation review types. Supports polling, SSE, webhook transports, channel-native inline buttons (Telegram, Slack, Discord, WhatsApp, Teams), opaque token security, multi-step form wizards, and multi-round edit cycles."
license: Apache-2.0
compatibility:
  - claude
  - codex
  - gemini
  - openclaw
  - goose
  - copilot
metadata:
  version: "0.7"
  spec_url: "https://github.com/rotorstar/hitl-protocol/blob/main/spec/v0.7/hitl-protocol.md"
  hitl:
    supported: true
    types: [approval, selection, input, confirmation, escalation]
    info: "Teaches the HITL Protocol itself — for building HITL services and HITL-aware agents."
---

# HITL Protocol

AI agents increasingly visit websites and services on behalf of their users: searching, booking, applying, purchasing. But some decisions are too important to leave to an agent alone — an agent can hallucinate, misinterpret, or make the wrong call at a critical moment — cancel the wrong insurance policy, book a non-refundable trip to the wrong city, wire money to the wrong account. HITL Protocol ("Human in the Loop") is an open standard that ensures humans stay in control of these moments. The user stays in their favorite messenger — Telegram, WhatsApp, Slack — and either taps a decision button right there or follows a link to a web page with a comfortable UI: cards, forms, buttons. No wall of text. No blind agent decisions. When you encounter a HITL response, tell your user that a decision is needed that should not be made by an agent alone — forward the prompt and make it easy to act: show the review link or render action buttons.

HITL Protocol is to human decisions what OAuth is to authentication — an open standard connecting **Services**, **Agents**, and **Humans**. When a service needs human input, it returns HTTP 202 with a review URL. The agent forwards the URL to the human. The human opens it in a browser, gets a rich UI, and makes an informed decision. The agent polls for the structured result and continues.

For simple decisions (confirm/cancel, approve/reject), agents can render **native messaging buttons** directly in Telegram, Slack, Discord, WhatsApp, or Teams — no browser needed. The service opts in via `submit_url`.

**No SDK required. No UI framework mandated. Just HTTP + URL + polling.**

**[Interactive Playground](https://rotorstar.github.io/hitl-protocol/playground/index.html)** — try all review types, transports, and inline actions live in your browser.

## Who Are You?

| Your role | You want to... | Read |
|-----------|----------------|------|
| Service/website builder | Add HITL endpoints to your API so agents can request human input | [Service Integration Guide](skills/references/service-integration.md) |
| Agent developer | Handle HTTP 202 + HITL responses from services | [Agent Integration Guide](skills/references/agent-integration.md) |
| Both / Learning | Understand the full protocol | Continue reading below |

## The Flow

```
Standard flow (all review types):
1. Human → Agent:    "Find me jobs in Berlin"
2. Agent → Service:  POST /api/search {query: "Senior Dev Berlin"}
3. Service → Agent:  HTTP 202 + hitl object (review_url, poll_url, type, prompt)
4. Agent → Human:    "Found 5 jobs. Review here: {review_url}"
5. Human → Browser:  Opens review_url → rich UI (cards, forms, buttons)
6. Human → Service:  Makes selection, clicks Submit
7. Agent → Service:  GET {poll_url} → {status: "completed", result: {action, data}}
8. Agent → Human:    "Applied to 2 selected jobs."

Inline flow (v0.7 — simple decisions only, when submit_url present):
1. Human → Agent:    "Send my application emails"
2. Agent → Service:  POST /api/send {emails: [...]}
3. Service → Agent:  HTTP 202 + hitl object (incl. submit_url, submit_token, inline_actions)
4. Agent → Human:    Native buttons in chat: [Confirm] [Cancel] [Details →]
5. Human → Agent:    Taps [Confirm] in chat
6. Agent → Service:  POST {submit_url} {action: "confirm", submitted_via: "telegram"}
7. Service → Agent:  200 OK {status: "completed"}
8. Agent → Human:    Updates message: "Confirmed — 3 emails sent."
```

The agent never renders UI. The service hosts the review page. Sensitive data stays in the browser — never passes through the agent. The inline flow is an optional shortcut for simple decisions.

## Feature Matrix

| Feature | Details |
|---------|---------|
| **Review types** | `approval`, `selection`, `input`, `confirmation`, `escalation` |
| **Form field types** | `text`, `textarea`, `number`, `date`, `email`, `url`, `boolean`, `select`, `multiselect`, `range`, custom `x-*` |
| **Transport** | Polling (required), SSE (optional), Callback/Webhook (optional) |
| **Inline submit** | `submit_url` + native messaging buttons (Telegram, Slack, Discord, WhatsApp, Teams) — service opt-in |
| **States** | `pending` → `opened` → `in_progress` → `completed` / `expired` / `cancelled` |
| **Security** | Opaque tokens (43 chars, base64url, 256-bit entropy), SHA-256 hash storage, timing-safe comparison, HTTPS only |
| **Multi-round** | `previous_case_id` / `next_case_id` for iterative edit cycles (Approval type) |
| **Forms** | Single-step fields, multi-step wizard, conditional visibility, validation rules, progress tracking |
| **Timeouts** | ISO 8601 duration, `default_action`: `skip` / `approve` / `reject` / `abort` |
| **Discovery** | `.well-known/hitl.json`, SKILL.md `metadata.hitl` extension |
| **Reminders** | `reminder_at` timestamps, `review.reminder` SSE event |
| **Rate limiting** | 60 requests/min per case on poll endpoint, `Retry-After` header |

## Five Review Types

| Type | Actions | Multi-round | Form fields | Use case |
|------|---------|:-----------:|:-----------:|----------|
| **Approval** | `approve`, `edit`, `reject` | Yes | No | Artifact review (CV, email, deployment plan) |
| **Selection** | `select` | No | No | Choose from options (job listings, targets) |
| **Input** | `submit` | No | Yes | Structured data entry (salary, dates, preferences) |
| **Confirmation** | `confirm`, `cancel` | No | No | Irreversible action gate (send emails, deploy) |
| **Escalation** | `retry`, `skip`, `abort` | No | No | Error recovery (deployment failed, API error) |

## HITL Object (HTTP 202 Response Body)

When a service needs human input, it returns HTTP 202 with this structure:

```json
{
  "status": "human_input_required",
  "message": "5 matching jobs found. Please select which ones to apply for.",
  "hitl": {
    "spec_version": "0.7",
    "case_id": "review_abc123",
    "review_url": "https://service.example.com/review/abc123?token=K7xR2mN4pQ...",
    "poll_url": "https://api.service.example.com/v1/reviews/abc123/status",
    "type": "selection",
    "prompt": "Select which jobs to apply for",
    "timeout": "24h",
    "default_action": "skip",
    "created_at": "2026-02-22T10:00:00Z",
    "expires_at": "2026-02-23T10:00:00Z",
    "context": {
      "total_options": 5,
      "query": "Senior Dev Berlin"
    }
  }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `spec_version` | `"0.7"` | Protocol version |
| `case_id` | string | Unique, URL-safe identifier (pattern: `review_{random}`) |
| `review_url` | URL | HTTPS URL to review page with opaque bearer token |
| `poll_url` | URL | Status polling endpoint |
| `type` | enum | `approval` / `selection` / `input` / `confirmation` / `escalation` / `x-*` |
| `prompt` | string | What the human needs to decide (max 500 chars) |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `expires_at` | datetime | ISO 8601 expiration timestamp |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `timeout` | duration | How long the review stays open (`24h`, `PT24H`, `P7D`) |
| `default_action` | enum | `skip` / `approve` / `reject` / `abort` — action on expiry |
| `callback_url` | URL / null | Echoed callback URL if agent provided one |
| `events_url` | URL | SSE endpoint for real-time status events |
| `context` | object | Arbitrary data for the review page (not processed by agent) |
| `reminder_at` | datetime / datetime[] | When to re-send the review URL |
| `previous_case_id` | string | Links to prior case in multi-round chain |
| `surface` | object | UI format declaration (`format`, `version`) |
| `submit_url` | URL | Agent-submit endpoint for channel-native inline buttons (v0.7) |
| `submit_token` | string | Bearer token for `submit_url` authentication (required if `submit_url` set) |
| `inline_actions` | string[] | Actions permitted via `submit_url` (e.g. `["confirm", "cancel"]`). If absent, all actions for the type are allowed. |

## Poll Response (Completed)

```json
{
  "status": "completed",
  "case_id": "review_abc123",
  "completed_at": "2026-02-22T10:15:00Z",
  "result": {
    "action": "select",
    "data": {
      "selected_jobs": ["job-123", "job-456"],
      "note": "Only remote positions"
    }
  }
}
```

The `result` object is present only when `status` is `"completed"`. It always contains `action` (string) and `data` (object with type-dependent content).

### Poll Response Statuses

| Status | Terminal | Description | Key fields |
|--------|:--------:|-------------|------------|
| `pending` | No | Case created, human hasn't opened URL | `expires_at` |
| `opened` | No | Human opened the review URL | `opened_at` |
| `in_progress` | No | Human is interacting with the form | `progress` (optional) |
| `completed` | Yes | Human submitted response | `result`, `completed_at`, `responded_by` |
| `expired` | Yes | Timeout reached | `expired_at`, `default_action` |
| `cancelled` | Yes | Human clicked cancel | `cancelled_at`, `reason` |

## State Machine

```
            +---------------------------------------------+
            |                                             v
[created] -> pending -> opened -> in_progress -> completed [terminal]
               |         |          |
               |         |          +---------> cancelled  [terminal]
               |         |
               |         +--> completed     [terminal]
               |         +--> expired       [terminal]
               |         +--> cancelled     [terminal]
               |
               +----------> expired          [terminal]
               +----------> cancelled        [terminal]
```

Terminal states (`completed`, `expired`, `cancelled`) are immutable — no further transitions.

## For Services: Quick Start

Return HTTP 202 when human input is needed:

```javascript
// Express / Hono / any HTTP framework
app.post('/api/search', async (req, res) => {
  const results = await searchJobs(req.body.query);

  // Create review case with opaque token
  const caseId = `review_${crypto.randomBytes(16).toString('hex')}`;
  const token = crypto.randomBytes(32).toString('base64url'); // 43 chars
  const tokenHash = crypto.createHash('sha256').update(token).digest('hex');

  store.set(caseId, {
    status: 'pending',
    tokenHash,
    results,
    created_at: new Date().toISOString(),
    expires_at: new Date(Date.now() + 86400000).toISOString(),
  });

  res.status(202).json({
    status: 'human_input_required',
    message: `${results.length} jobs found. Please select which ones to apply for.`,
    hitl: {
      spec_version: '0.6',
      case_id: caseId,
      review_url: `https://yourservice.com/review/${caseId}?token=${token}`,
      poll_url: `https://api.yourservice.com/v1/reviews/${caseId}/status`,
      type: 'selection',
      prompt: 'Select which jobs to apply for',
      timeout: '24h',
      default_action: 'skip',
      created_at: store.get(caseId).created_at,
      expires_at: store.get(caseId).expires_at,
    },
  });
});
```

You also need: a review page (any web framework), a poll endpoint (`GET /reviews/:caseId/status`), and a response endpoint (`POST /reviews/:caseId/respond`). See [Service Integration Guide](skills/references/service-integration.md) for full details.

## For Agents: Quick Start

Handle HTTP 202 responses — ~15 lines:

```python
import time, httpx

response = httpx.post("https://api.jobboard.com/search", json=query)

if response.status_code == 202:
    hitl = response.json()["hitl"]

    # v0.7: Check for inline submit support
    if "submit_url" in hitl and "submit_token" in hitl:
        # Render native buttons in messaging platform (e.g. Telegram, Slack)
        send_inline_buttons(hitl["prompt"], hitl["inline_actions"], hitl["review_url"])
        # When human taps button → POST to submit_url (see Agent Integration Guide)
    else:
        # Standard flow: forward URL to human
        send_to_user(f"{hitl['prompt']}\n{hitl['review_url']}")

    # Poll for result (standard flow or fallback)
    while True:
        time.sleep(30)
        poll = httpx.get(hitl["poll_url"], headers=auth).json()

        if poll["status"] == "completed":
            result = poll["result"]  # {action: "select", data: {...}}
            break
        if poll["status"] in ("expired", "cancelled"):
            break
```

No SDK. No UI rendering. Just HTTP + URL forwarding + polling. See [Agent Integration Guide](skills/references/agent-integration.md) for inline submit, SSE, callbacks, multi-round, and edge cases.

## Three Transport Modes

| Transport | Agent needs public endpoint? | Real-time? | Complexity |
|-----------|:---------------------------:|:----------:|:----------:|
| **Polling** (default) | No | No | Minimal |
| **SSE** (optional) | No | Yes | Low |
| **Callback** (optional) | Yes | Yes | Medium |

Polling is the baseline — every HITL-compliant service MUST support it. SSE and callbacks are optional enhancements.

## Channel-Native Inline Actions (v0.7)

For simple decisions, agents can render **native messaging buttons** instead of sending a URL. The human taps a button directly in the chat — no browser switch needed.

**How it works:** The service includes `submit_url` + `submit_token` in the HITL object. The agent detects these fields and renders platform-native buttons. When the human taps a button, the agent POSTs the action to `submit_url`. The messaging platform is passive — it renders whatever the agent sends. No messenger auto-detects HITL support.

**When to use inline buttons:**

| Review type | Inline possible? | Reason |
|-------------|:----------------:|--------|
| **Confirmation** | Yes | 2 buttons: Confirm / Cancel |
| **Escalation** | Yes | 3 buttons: Retry / Skip / Abort |
| **Approval** (simple) | Yes | 2 buttons: Approve / Reject (without edit) |
| **Approval** (with edit) | URL only | Edit requires rich UI |
| **Selection** | URL only | Needs list/cards UI |
| **Input** | URL only | Needs form fields |

**Always include a URL fallback button** (e.g. "Details &#8594;") linking to `review_url` — the human can always switch to the full review page.

**Platform requirements:** The agent must be a platform bot (Telegram Bot via BotFather, Slack App, Discord Bot, WhatsApp Business API, Teams Bot) to send native buttons. See [Agent Integration Guide](skills/references/agent-integration.md) for platform-specific rendering patterns.

## Non-Goals

- **Does NOT render review UI** — the service hosts and renders the review page. The agent is a messenger.
- **Does NOT define the review page framework** — any web technology works (React, plain HTML, etc.).
- **Does NOT replace OAuth** — HITL is for decisions, not authentication.
- **Does NOT submit on behalf of the human** — unless the human explicitly triggers an inline action button in a messaging platform (v0.7 `submit_url`).

## SKILL.md Extension for Services

Services that use HITL can declare support in their own SKILL.md frontmatter:

```yaml
metadata:
  hitl:
    supported: true
    types: [selection, confirmation]
    supports_inline_submit: true
    review_base_url: "https://yourservice.com/review"
    timeout_default: "24h"
    info: "May ask user to select preferred jobs or confirm applications."
```

See [spec Section 12](spec/v0.7/hitl-protocol.md) for the full field reference.

### Best Practice: Enforce HITL Choice

**Problem:** Agents tend to take the efficient path and silently skip HITL — defaulting to no human review. Even though the protocol says agents MUST NOT ignore HTTP 202, nothing prevents an agent from never sending requests that trigger HITL in the first place.

**Solution:** Force agents to make an **explicit choice** per request. Add `prefer_hitl` and `skip_hitl` flags to your API and reject requests that provide neither.

Declare this in your SKILL.md:

```yaml
metadata:
  hitl:
    supported: true
    hitl_required: true
    types: [selection, confirmation]
    info: "HITL is required. You MUST send prefer_hitl: true or skip_hitl: true."
```

Add an **Agent Guidelines** section to your SKILL.md body:

```markdown
## Agent Guidelines

HITL is required for this service. Every request MUST include exactly one of:

| Parameter | Type | Effect |
|-----------|------|--------|
| `prefer_hitl` | boolean | `true` → human reviews via HITL (HTTP 202) |
| `skip_hitl` | boolean | `true` → direct execution, no human review (HTTP 201) |

You MUST choose one. Omitting both returns 400 `HITL_CHOICE_REQUIRED`.
Sending both returns 400 validation error.

### Example: With HITL

POST /api/search
{"query": "Senior Dev Berlin", "prefer_hitl": true}

→ 202 + hitl object (human reviews results)

### Example: Without HITL

POST /api/search
{"query": "Senior Dev Berlin", "skip_hitl": true}

→ 201 {"results": [...], "hitl_skipped": true}

### Example: Missing choice

POST /api/search
{"query": "Senior Dev Berlin"}

→ 400 {"error": "HITL_CHOICE_REQUIRED", "message": "You must send prefer_hitl or skip_hitl."}
```

See [Service Integration Guide — Enforcing HITL Choice](skills/references/service-integration.md#enforcing-hitl-choice) for validation gate implementation.

### Optional: Quality Improvement Signal

Services can include `improvement_suggestions` in successful (non-202) responses to give agents structured feedback they can act on — without requiring a new HITL flow.

Declare support in your SKILL.md:

```yaml
metadata:
  hitl:
    supported: true
    supports_improvement_suggestions: true
    info: "Returns improvement_suggestions in 201 responses. Agents may offer up to 2 improvement cycles."
```

**Suggestion object schema:**

| Field | Type | Description |
|-------|------|-------------|
| `field` | string | Which data field can be improved |
| `issue` | string | What is missing or suboptimal |
| `agent_action` | string | Exact question/action for the agent to take |
| `impact` | string | Human-readable benefit (e.g. `"+25 quality points"`) |
| `priority` | `"high"` / `"medium"` / `"low"` | Order of importance |

**Agent behavior:**
- Always share the primary result first
- Offer up to **2 improvement cycles** — one question per suggestion, re-submit with enriched data
- Stop when `improvement_suggestions` is empty or `maxAttempts` reached
- Never loop indefinitely

See [Agent Checklist — Quality Improvement Loop](agents/checklist.md#enhanced-quality-improvement-loop) and [Example 13](examples/13-quality-improvement-loop.json).

## RFC Alignment

This protocol and skill documentation are aligned with these core RFCs:

- [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110) — HTTP semantics (`202 Accepted`, conditional requests, retry behavior)
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) + [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — normative terms (`MUST`, `SHOULD`, `MAY`)
- [RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) — timestamp formats used by HITL case lifecycle fields
- [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750) — bearer token usage for review and inline submit authorization

For the complete implementation matrix, see [README RFC Alignment](README.md#rfc-alignment).

## Resources

- [Full Specification (v0.7)](spec/v0.7/hitl-protocol.md)
- [OpenAPI 3.1 Spec](schemas/openapi.yaml) — all endpoints documented
- [JSON Schemas](schemas/) — HITL object, poll response, form field, submit request definitions
- [Reference Implementations](implementations/reference-service/) — Express 5, Hono, Next.js, FastAPI
- [Review Page Templates](templates/) — HTML templates for all 5 review types
- [Examples](examples/) — 12 end-to-end flows (incl. inline confirmation, escalation, hybrid approval)
- [Agent Implementation Checklist](agents/checklist.md) — detailed agent guide with pseudocode
- [Interactive Playground](playground/)
- [SDK Design Guide](docs/sdk-guide.md) — build a community SDK
