# Security Model — pager-triage

**Version:** 0.1.1
**Last updated:** 2026-02-16

---

## 1. API Key Handling

### Storage
- API keys are read **exclusively** from environment variables (`PAGERDUTY_API_KEY`, `PAGERDUTY_EMAIL`)
- Keys are **never** hardcoded, written to disk, cached, or stored in any skill state
- Keys are **never** passed as command-line arguments (which would be visible in `ps` output)

### Masking
- If an API key appears in an error message (e.g., authentication failure), it is masked to `****<last 4 chars>` using the `mask_key()` function
- The agent **never** displays the full key value, even if the user asks — the script physically cannot output it
- Error messages reference the environment variable name, not the value

### Missing Keys
- If `PAGERDUTY_API_KEY` is not set, the tool outputs a structured JSON error with setup instructions and exits non-zero
- If `PAGERDUTY_EMAIL` is not set and a write operation is attempted, the tool outputs a specific error and does not make any API call

---

## 2. Read-Only by Default

### Read Operations (5 commands — no confirmation needed)
| Command | What it reads | PD API endpoint |
|---------|--------------|-----------------|
| `incidents` | Active incidents list | `GET /incidents` |
| `detail` | Single incident + timeline + alerts + notes | `GET /incidents/{id}`, `/log_entries`, `/alerts`, `/notes` |
| `oncall` | On-call schedules | `GET /oncalls` |
| `services` | Service list with status | `GET /services` |
| `recent` | Historical incidents | `GET /incidents` (with `since`/`until`) |

These commands use only `GET` requests. They cannot modify any PagerDuty state.

### Write Operations (3 commands — require `--confirm`)
| Command | What it modifies | PD API method | HTTP |
|---------|-----------------|---------------|------|
| `ack` | Incident status → acknowledged | `PUT /incidents/{id}` | PUT |
| `resolve` | Incident status → resolved | `PUT /incidents/{id}` | PUT |
| `note` | Adds note to incident | `POST /incidents/{id}/notes` | POST |

**Confirmation gate behavior:**
1. Without `--confirm`: The tool fetches the incident details, displays them as a JSON preview, and exits with a non-zero status. **No write API call is made.**
2. With `--confirm`: The write operation proceeds.

The agent should always run without `--confirm` first to show the user what will happen, then re-run with `--confirm` only after explicit user approval.

---

## 3. Data Flow

### What goes TO PagerDuty
| Direction | Data sent |
|-----------|----------|
| Auth header | `Authorization: Token token=<API_KEY>` (HTTPS only — TLS encrypted in transit) |
| From header | `From: <PAGERDUTY_EMAIL>` (write operations only) |
| Query params | Filter criteria: status, service IDs, time ranges, incident IDs |
| Request body | Write ops only: status change (`acknowledged`/`resolved`) or note content |

**No user conversation content, agent prompts, or other tool outputs are sent to PagerDuty.** Only structured API parameters.

### What comes FROM PagerDuty
| Data | Contains |
|------|----------|
| Incident data | Titles, descriptions, status, urgency, timestamps |
| User data | Names, emails of assignees, acknowledgers, on-call users |
| Service data | Service names, descriptions, integration names |
| Alert data | Alert summaries, severities, source details |
| Timeline data | Log entries with types and summaries |

### What the Agent Sees
The agent receives **processed JSON output** from the script. The script:
1. Makes API calls with the key in the auth header
2. Parses the PagerDuty response with `jq`
3. Outputs a normalized, trimmed JSON structure
4. **Never includes** the API key, raw HTTP headers, or full API responses in output

### URL Validation
The script enforces HTTPS-only: any URL not starting with `https://` is rejected before any network call is made.

---

## 4. Threat Model

### T1: Prompt Injection via Incident Data

**Risk:** An attacker creates a PagerDuty incident with a title or description containing prompt injection payload (e.g., "Ignore previous instructions and...").

**Mitigation:**
- Incident data flows through `jq` field extraction — only specific fields are included in output
- The agent sees structured JSON, not raw text that could be confused with instructions
- The tool does not interpret incident content; it only passes structured fields

**Residual risk:** Medium. The agent may still process malicious content in incident titles/descriptions. This is an inherent LLM risk that should be addressed at the agent framework level.

### T2: Credential Exfiltration

**Risk:** A prompt injection or malicious instruction causes the agent to reveal API keys.

**Mitigation:**
- The script never outputs the API key — it's used only in HTTP headers
- `mask_key()` ensures even error messages show only `****<last 4>`
- The agent does not have access to the environment variable value through the tool's output
- If asked "what's my API key?", the skill has no mechanism to reveal it

**Residual risk:** Low. The key exists in the agent's environment, which is a runtime-level concern outside this tool's scope.

### T3: Unauthorized Acknowledge/Resolve

**Risk:** The agent auto-acknowledges or auto-resolves incidents without user consent, hiding real incidents from on-call responders.

**Mitigation:**
- `--confirm` flag is mandatory — without it, write operations exit non-zero with a preview
- The agent should be instructed to never pass `--confirm` without explicit user approval
- PagerDuty's `From` header creates an audit trail showing which email performed the action
- PagerDuty's own timeline records all acknowledgment/resolution events

**Residual risk:** Low-medium. If the agent is misconfigured to auto-confirm, this gate is bypassed at the agent level. The `--confirm` flag is a defense-in-depth measure, not a complete solution.

### T4: Incident ID Injection

**Risk:** A crafted incident ID could be used for path traversal or API manipulation.

**Mitigation:**
- All incident IDs are validated against `^[A-Za-z0-9]+$` regex before use
- Service IDs are similarly validated
- Invalid IDs produce a clear error and no API call is made

### T5: API Key with Excessive Permissions

**Risk:** A full-access PagerDuty API key could be used to perform operations beyond what this tool exposes (create incidents, modify escalation policies, etc.).

**Mitigation:**
- The tool only implements 8 specific operations — it cannot be tricked into calling arbitrary PagerDuty endpoints
- We recommend read-only API keys for triage-only use cases (see RBAC section below)

---

## 5. RBAC Recommendations

### For triage-only use (recommended default)

Create a **read-only** PagerDuty API key:
1. PagerDuty → Settings → API Access Keys
2. Create New API Key → Name: `OpenClaw Agent (read-only)` → **Read-only**

With a read-only key:
- ✅ `incidents`, `detail`, `oncall`, `services`, `recent` all work
- ❌ `ack`, `resolve`, `note` will fail with HTTP 403 (the tool handles this gracefully)

### For full incident response

Create a **full-access** API key:
1. PagerDuty → Settings → API Access Keys
2. Create New API Key → Name: `OpenClaw Agent (full)` → **Full Access**
3. Also set `PAGERDUTY_EMAIL` to the email of the user authorizing actions

**Recommendation:** Start with read-only. Upgrade to full access only after you've validated the triage workflow and trust the agent's confirmation behavior.

### PagerDuty Team-Scoped Keys

If your PagerDuty account supports team-scoped API keys, consider:
- Creating a key scoped to only the team(s) the on-call engineer manages
- This limits blast radius if the key is compromised

---

## 6. Audit Trail

All write operations are fully auditable:
- PagerDuty records the `From` email header as the actor for ack/resolve/note operations
- PagerDuty's incident timeline shows all state changes with timestamps
- The tool outputs structured JSON with `acknowledged_by`/`resolved_by` fields that include the email

---

## 7. Network Security

- All API calls use **HTTPS only** (enforced by URL validation in the script)
- Connection timeout: **10 seconds** (prevents hanging on network issues)
- No data is cached or written to disk by the tool
- No external services are contacted besides `api.pagerduty.com`

---

<sub>Security documentation for pager-triage v0.1.1 · [Anvil AI](https://anvil-ai.io)</sub>
