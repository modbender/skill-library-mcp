# HITL Protocol — Service Integration Guide

This guide is for **service and website builders** who want to make their service accessible to autonomous agents via HITL Protocol.

## When to Return HTTP 202

Return HTTP 202 (not 200) when:
- The operation requires human judgment (approve a draft, select from options)
- Sensitive data needs human review before proceeding
- An irreversible action needs human confirmation
- The service needs structured input the agent cannot provide

Return HTTP 200 when the operation completes without human input.

## Enforcing HITL Choice

Agents default to the efficient path — skipping human review entirely. To prevent this, require agents to explicitly declare their intent via `prefer_hitl` or `skip_hitl` flags in every request.

### Decision Matrix

| `prefer_hitl` | `skip_hitl` | Result |
|:-:|:-:|--------|
| `true` | — | HTTP 202 + HITL object (human reviews) |
| — | `true` | HTTP 201 + `hitl_skipped: true` (direct execution) |
| — | — | HTTP 400 `HITL_CHOICE_REQUIRED` |
| `true` | `true` | HTTP 400 validation error (mutually exclusive) |

### Validation Gate (JavaScript)

```javascript
app.post('/api/action', async (req, res) => {
  const { prefer_hitl, skip_hitl, ...params } = req.body;

  // Reject ambiguous requests
  if (prefer_hitl && skip_hitl) {
    return res.status(400).json({
      error: 'VALIDATION_ERROR',
      message: 'prefer_hitl and skip_hitl are mutually exclusive.',
    });
  }
  if (!prefer_hitl && !skip_hitl) {
    return res.status(400).json({
      error: 'HITL_CHOICE_REQUIRED',
      message: 'You must send prefer_hitl: true or skip_hitl: true.',
    });
  }

  const result = await executeAction(params);

  if (skip_hitl) {
    // Direct execution — no human review
    return res.status(201).json({ ...result, hitl_skipped: true });
  }

  // HITL flow — create review case
  const hitl = await createReviewCase(result);
  return res.status(202).json({
    status: 'human_input_required',
    message: hitl.prompt,
    hitl,
  });
});
```

### Validation Gate (Python)

```python
@app.post("/api/action")
async def action(request: Request):
    body = await request.json()
    prefer_hitl = body.get("prefer_hitl", False)
    skip_hitl = body.get("skip_hitl", False)

    if prefer_hitl and skip_hitl:
        return JSONResponse(status_code=400, content={
            "error": "VALIDATION_ERROR",
            "message": "prefer_hitl and skip_hitl are mutually exclusive.",
        })
    if not prefer_hitl and not skip_hitl:
        return JSONResponse(status_code=400, content={
            "error": "HITL_CHOICE_REQUIRED",
            "message": "You must send prefer_hitl: true or skip_hitl: true.",
        })

    result = await execute_action(body)

    if skip_hitl:
        return JSONResponse(status_code=201, content={**result, "hitl_skipped": True})

    hitl = await create_review_case(result)
    return JSONResponse(status_code=202, content={
        "status": "human_input_required",
        "message": hitl["prompt"],
        "hitl": hitl,
    })
```

### HITL Continuation Chains

When a HITL flow triggers a follow-up request (e.g. `next_case_id`), the agent is already in a HITL context. In this case, neither flag is needed — derive `prefer_hitl` automatically:

```javascript
// If request contains a previous case_id, it's a HITL continuation
const isHitlContinuation = !!req.body.previous_case_id;
const effectivePreferHitl = prefer_hitl || isHitlContinuation;
```

### Documenting in Your SKILL.md

Add this to your service's SKILL.md so agents know the requirement upfront:

```yaml
metadata:
  hitl:
    supported: true
    hitl_required: true
    types: [selection, confirmation]
    info: "HITL is required. You MUST send prefer_hitl: true or skip_hitl: true."
```

## Implementation Checklist

- [ ] Return HTTP 202 with `hitl` object when human input is needed
- [ ] Generate opaque bearer token (43 chars, base64url, 256-bit entropy)
- [ ] Store only SHA-256 hash of token (never store raw token)
- [ ] Host a review page at `review_url`
- [ ] Implement poll endpoint at `poll_url` (GET, returns status + result)
- [ ] Implement response endpoint (POST, accepts human's decision)
- [ ] Enforce one-response per case (409 Conflict on duplicate)
- [ ] Implement state machine with valid transitions only
- [ ] Set appropriate timeout and default_action
- [ ] Return `Retry-After` header on rate limit (429)

## HITL Object — Complete Field Reference

### Required Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `spec_version` | string | Must be `"0.5"` | Protocol version |
| `case_id` | string | Pattern: `^[a-zA-Z0-9_-]+$` | Unique identifier. Recommended: `review_{random}` |
| `review_url` | URL | HTTPS only, includes opaque token | URL to the review page |
| `poll_url` | URL | HTTPS recommended | Status polling endpoint |
| `type` | enum | `approval` / `selection` / `input` / `confirmation` / `escalation` / `x-*` | Review type |
| `prompt` | string | Max 500 chars | What the human needs to decide |
| `created_at` | datetime | ISO 8601 | When the case was created |
| `expires_at` | datetime | ISO 8601 | When the case expires |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `timeout` | duration | How long review stays open. ISO 8601 (`PT24H`, `P7D`) or shorthand (`24h`, `7d`) |
| `default_action` | enum | `skip` / `approve` / `reject` / `abort` — action taken on expiry |
| `callback_url` | URL / null | Echo of agent's callback URL, or null |
| `events_url` | URL | SSE endpoint for real-time events |
| `context` | object | Arbitrary data for the review page. For `input` type, MAY include `form` |
| `reminder_at` | datetime / datetime[] | When to send reminder(s) |
| `previous_case_id` | string | Links to prior case in multi-round chain |
| `surface` | object | UI format declaration: `{format: "json-render", version: "1.0"}` |

## Security: Token Generation

```javascript
import crypto from 'crypto';

// Generate opaque bearer token (43 chars, 256-bit entropy)
const token = crypto.randomBytes(32).toString('base64url');

// Store ONLY the hash — never persist the raw token
const tokenHash = crypto.createHash('sha256').update(token).digest('hex');

// Build review URL
const reviewUrl = `https://yourservice.com/review/${caseId}?token=${token}`;

// Verify token on review page access
function verifyToken(incomingToken, storedHash) {
  const incomingHash = crypto.createHash('sha256').update(incomingToken).digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(incomingHash, 'hex'),
    Buffer.from(storedHash, 'hex')
  );
}
```

**Why opaque tokens instead of JWT?**
- 43 chars vs 241 chars — shorter URLs, no LLM tokenizer corruption
- Bearer model — URL sharing is delegation by design
- SHA-256 hash storage — compromised DB doesn't leak tokens

## State Machine

All valid transitions:

| From | To | Trigger |
|------|----|---------|
| *(created)* | `pending` | Service creates case |
| `pending` | `opened` | Human opens review URL |
| `pending` | `expired` | Timeout reached |
| `pending` | `cancelled` | Human clicks cancel |
| `opened` | `in_progress` | Human starts interacting with form |
| `opened` | `completed` | Human submits response |
| `opened` | `expired` | Timeout reached |
| `opened` | `cancelled` | Human clicks cancel |
| `in_progress` | `completed` | Human submits response |
| `in_progress` | `cancelled` | Human clicks cancel |

**Terminal states** (`completed`, `expired`, `cancelled`) are **immutable** — no transitions out.

**Optional intermediate states:** `opened` and `in_progress` are optional. Services that don't track page views may transition directly from `pending` to terminal states.

## Poll Endpoint Implementation

```
GET /v1/reviews/{caseId}/status
Authorization: Bearer <agent-token>  (or other auth)
```

Return the current status with appropriate fields per state:

```javascript
app.get('/v1/reviews/:caseId/status', (req, res) => {
  const rc = store.get(req.params.caseId);
  if (!rc) return res.status(404).json({ error: 'Case not found' });

  const response = { status: rc.status, case_id: rc.case_id };

  // Always include timestamps
  if (rc.created_at) response.created_at = rc.created_at;
  if (rc.expires_at) response.expires_at = rc.expires_at;
  if (rc.opened_at) response.opened_at = rc.opened_at;

  // Terminal state fields
  if (rc.status === 'completed') {
    response.completed_at = rc.completed_at;
    response.result = rc.result; // { action, data }
    if (rc.responded_by) response.responded_by = rc.responded_by;
    if (rc.next_case_id) response.next_case_id = rc.next_case_id;
  }
  if (rc.status === 'expired') {
    response.expired_at = rc.expired_at;
    response.default_action = rc.default_action;
  }
  if (rc.status === 'cancelled') {
    response.cancelled_at = rc.cancelled_at;
    if (rc.reason) response.reason = rc.reason;
  }

  // Progress tracking (optional, for multi-step Input forms)
  if (rc.status === 'in_progress' && rc.progress) {
    response.progress = rc.progress;
  }

  res.json(response);
});
```

### Rate Limiting

- Recommend 60 requests/min per case
- Return HTTP 429 with `Retry-After` header when exceeded
- Support `ETag` / `If-None-Match` for efficient polling (304 Not Modified)

## Review Page

The review page is hosted by your service. Use any web framework. Requirements:

1. **Verify token** — check opaque token against stored SHA-256 hash
2. **Display context** — render the review UI based on `type` and `context`
3. **Collect response** — submit human's decision to response endpoint
4. **One response only** — return 409 Conflict on duplicate submission

The agent never sees or renders this page. All sensitive data stays in the browser.

HTML templates for all 5 review types are available in [templates/](../../templates/).

## Response Endpoint

```
POST /v1/reviews/{caseId}/respond
Content-Type: application/json
```

```json
{
  "action": "select",
  "data": {
    "selected_jobs": ["job-123", "job-456"],
    "note": "Only remote positions"
  }
}
```

Valid `action` values per type:

| Type | Valid actions |
|------|-------------|
| Approval | `approve`, `edit`, `reject` |
| Selection | `select` |
| Input | `submit` |
| Confirmation | `confirm`, `cancel` |
| Escalation | `retry`, `skip`, `abort` |

## Form Field Definitions (Input Type)

For `input`-type reviews, include a `form` object in `context`:

### Single-Step Form

```json
{
  "context": {
    "form": {
      "fields": [
        {
          "key": "salary",
          "label": "Salary Expectation (EUR)",
          "type": "number",
          "required": true,
          "sensitive": true,
          "validation": { "min": 0, "max": 1000000 }
        },
        {
          "key": "start_date",
          "label": "Earliest Start Date",
          "type": "date",
          "required": true
        }
      ]
    }
  }
}
```

### Multi-Step Wizard

```json
{
  "context": {
    "form": {
      "session_id": "form_sess_x7k9m2",
      "steps": [
        {
          "title": "Personal Information",
          "description": "Basic contact details",
          "fields": [
            { "key": "full_name", "label": "Full Name", "type": "text", "required": true },
            { "key": "email", "label": "Email", "type": "email", "required": true }
          ]
        },
        {
          "title": "Preferences",
          "fields": [
            {
              "key": "employment_type",
              "label": "Employment Type",
              "type": "select",
              "required": true,
              "options": [
                { "value": "fulltime", "label": "Full-time" },
                { "value": "parttime", "label": "Part-time" }
              ]
            },
            {
              "key": "salary_range",
              "label": "Expected Salary (EUR)",
              "type": "range",
              "sensitive": true,
              "validation": { "min": 40000, "max": 200000 },
              "conditional": {
                "field": "employment_type",
                "operator": "eq",
                "value": "fulltime"
              }
            }
          ]
        }
      ]
    }
  }
}
```

Use `fields` (single-step) **or** `steps` (multi-step), never both.

### Field Types

| Type | HTML equiv | Value type | Notes |
|------|-----------|------------|-------|
| `text` | `<input type="text">` | string | Single-line |
| `textarea` | `<textarea>` | string | Multi-line |
| `number` | `<input type="number">` | number | Integer or decimal |
| `date` | `<input type="date">` | string (ISO 8601) | Date picker |
| `email` | `<input type="email">` | string | Email validation |
| `url` | `<input type="url">` | string | URL validation |
| `boolean` | `<input type="checkbox">` | boolean | Toggle |
| `select` | `<select>` | string | Single choice, requires `options` |
| `multiselect` | `<select multiple>` | string[] | Multiple choices, requires `options` |
| `range` | `<input type="range">` | number | Slider, requires `validation.min`/`max` |
| `x-*` | Custom | Any | Service-defined custom types |

### Field Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `key` | string | Yes | Unique field ID. Pattern: `^[a-zA-Z][a-zA-Z0-9_]*$` |
| `label` | string | Yes | Human-readable label (max 200 chars) |
| `type` | string | Yes | Field type from table above |
| `required` | boolean | No | Must be filled before submission (default: false) |
| `placeholder` | string | No | Placeholder text |
| `hint` | string | No | Help text displayed below field |
| `default` | any | No | Pre-filled value. MUST NOT contain sensitive data |
| `default_ref` | URL | No | URL to securely fetch pre-fill (requires token) |
| `sensitive` | boolean | No | Mask input, suppress logging (default: false) |
| `options` | array | For select/multiselect | `[{value, label}, ...]` |
| `validation` | object | No | `{minLength, maxLength, pattern, min, max}` |
| `conditional` | object | No | `{field, operator, value}`. Operators: `eq`, `neq`, `in`, `gt`, `lt` |

### Progress Tracking (Optional)

When a human is working on a multi-step form, include `progress` in `in_progress` poll responses:

```json
{
  "status": "in_progress",
  "progress": {
    "current_step": 2,
    "total_steps": 3,
    "completed_fields": 4,
    "total_fields": 8
  }
}
```

## SSE Event Stream (Optional)

If you implement real-time events, expose an `events_url`:

```
GET /v1/reviews/{caseId}/events
Accept: text/event-stream
```

Event types:

| Event | When | Data |
|-------|------|------|
| `review.opened` | Human opens URL | `{case_id, opened_at}` |
| `review.in_progress` | Human starts interacting | `{case_id, progress}` |
| `review.completed` | Human submits | `{case_id, completed_at, result}` |
| `review.expired` | Timeout reached | `{case_id, expired_at, default_action}` |
| `review.cancelled` | Human cancels | `{case_id, cancelled_at, reason}` |
| `review.reminder` | Reminder triggered | `{case_id, review_url}` |

Support `Last-Event-ID` for reconnection. Include `id` in each event.

## Callback/Webhook (Optional)

When the agent includes `hitl_callback_url` in the original request:

1. Echo it in `hitl.callback_url`
2. POST to the callback URL when the case reaches a terminal state
3. Sign with `X-HITL-Signature: sha256=<hmac>` (HMAC-SHA256 of request body)
4. Retry with exponential backoff (up to 3 attempts)

```json
POST {callback_url}
X-HITL-Signature: sha256=abc123...
Content-Type: application/json

{
  "event": "review.completed",
  "case_id": "review_abc123",
  "completed_at": "2026-02-22T10:15:00Z",
  "result": {
    "action": "select",
    "data": { "selected_jobs": ["job-123"] }
  }
}
```

## Service Discovery (Optional)

Expose a `.well-known/hitl.json` endpoint:

```json
{
  "hitl_protocol": "0.5",
  "service": {
    "name": "JobBoard Pro",
    "description": "Job search and application service"
  },
  "review_types": ["selection", "confirmation"],
  "review_base_url": "https://jobboard.example.com/review",
  "api_base_url": "https://api.jobboard.example.com/v1",
  "timeout_default": "24h",
  "features": {
    "callback": true,
    "signed_responses": false,
    "edit_grace_period": "5m"
  }
}
```

## Multi-Round Reviews (Approval Type)

For iterative edit cycles:

1. Service creates case with `type: "approval"`
2. Human responds with `action: "edit"` + feedback in `data`
3. Service creates new case with `previous_case_id` linking to the original
4. Poll response of original case includes `next_case_id`
5. Repeat until human responds with `action: "approve"` or `"reject"`

## SKILL.md Extension

Declare HITL support in your service's SKILL.md frontmatter (see [spec Section 12](../../spec/v0.5/hitl-protocol.md)):

```yaml
metadata:
  hitl:
    supported: true
    types: [selection, confirmation]
    review_base_url: "https://yourservice.com/review"
    timeout_default: "24h"
    info: "May ask user to select jobs or confirm applications."
```

| Field | Required | Description |
|-------|----------|-------------|
| `metadata.hitl.supported` | REQUIRED | `true` if service may return HITL responses |
| `metadata.hitl.types` | RECOMMENDED | Which review types the service may trigger |
| `metadata.hitl.review_base_url` | OPTIONAL | Base URL for review pages |
| `metadata.hitl.timeout_default` | OPTIONAL | Typical timeout duration |
| `metadata.hitl.info` | RECOMMENDED | When/why HITL is triggered (max 200 chars) |

## Reference Implementations

Working implementations in 4 frameworks:

| Framework | Path | Language |
|-----------|------|----------|
| Express 5 | [implementations/reference-service/express/](../../implementations/reference-service/express/) | Node.js |
| Hono | [implementations/reference-service/hono/](../../implementations/reference-service/hono/) | Edge/Deno/Bun |
| Next.js | [implementations/reference-service/nextjs/](../../implementations/reference-service/nextjs/) | TypeScript |
| FastAPI | [implementations/reference-service/python/](../../implementations/reference-service/python/) | Python |

## Common Implementation Mistakes

Real-world audits of services implementing HITL v0.7 have revealed recurring patterns. Avoid these:

### Mistake 1: Accepting Both Tokens Interchangeably (Security Critical)

**Wrong:**
```javascript
function verifyToken(token, hitlCase) {
  if (matchesHash(token, hitlCase.review_token_hash)) return true
  if (matchesHash(token, hitlCase.submit_token_hash)) return true  // ← WRONG
  return false
}
```

**Why it's dangerous:** If the `review_url` leaks (shared in chat, bookmarked, forwarded), an attacker can use the review token to make inline submissions — defeating the entire dual-token security model.

**Right:** Add a `purpose` parameter:
```javascript
function verifyToken(token, hitlCase, purpose) {
  if (purpose === 'review') return matchesHash(token, hitlCase.review_token_hash)
  if (purpose === 'submit') return matchesHash(token, hitlCase.submit_token_hash)
  return false
}
```

See [Spec Section 7.5](../../spec/v0.7/hitl-protocol.md) — `submit_token` MUST be different from the review URL token.

### Mistake 2: Wrong Body Format for Inline Submit

**Wrong:** Expecting `{ result: { action, data } }` for Bearer-authenticated inline submissions.

**Right:** Two distinct formats depending on the auth path:
- **Inline submit (Bearer header):** `{ action, data, submitted_via, submitted_by }` — flat
- **Review page (body/URL token):** `{ action, data }` or your existing format

See [Spec Section 7.5.1](../../spec/v0.7/hitl-protocol.md) for the inline submit request body.

### Mistake 3: HTTP 422 Instead of 403 for Invalid Inline Actions

**Wrong:** Returning `422 Unprocessable Entity` when an action is not in `inline_actions`.

**Right:** Return **403 Forbidden** with `review_url` in the error body:
```json
{
  "error": "action_not_inline",
  "message": "Action 'edit' requires the review page.",
  "review_url": "https://yourservice.com/review/abc123?token=..."
}
```

This lets the agent fall back to the browser flow gracefully. The human can complete the action on the full review page.

## JSON Schema Validation

Validate your HITL objects and poll responses:

- [hitl-object.schema.json](../../schemas/hitl-object.schema.json)
- [poll-response.schema.json](../../schemas/poll-response.schema.json)
- [form-field.schema.json](../../schemas/form-field.schema.json)
- [OpenAPI 3.1 spec](../../schemas/openapi.yaml)

## Compliance Tests

Run the test suites against your implementation:

- Node.js (Vitest): [tests/node/](../../tests/node/)
- Python (pytest): [tests/python/](../../tests/python/)
