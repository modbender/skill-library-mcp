# Build Spec: pager-triage

**RUN_ID:** cf_rd_20260215_2021
**Date:** 2026-02-15
**Status:** APPROVED — Build from this spec alone.
**Estimated build time:** 2 days
**Builder notes:** This is decision-complete. Do not deviate from this spec without judge approval.

---

## 1. SKILL.md Frontmatter

```yaml
---
name: pager-triage
version: 1.0.0
displayName: PagerDuty Incident Triage
description: >
  AI-powered incident triage for PagerDuty and OpsGenie. List active incidents,
  get incident details with timeline analysis, check on-call schedules, correlate
  alerts, and acknowledge/resolve with confirmation gates. Read-only by default.
author: Anvil AI
tags:
  - pagerduty
  - opsgenie
  - incident-response
  - sre
  - on-call
  - devops
  - enterprise
  - monitoring
tools:
  - name: pd_incidents
    description: List active PagerDuty incidents (triggered + acknowledged)
  - name: pd_incident_detail
    description: Get detailed incident info including timeline, alerts, and notes
  - name: pd_oncall
    description: Show current on-call schedules and escalation policies
  - name: pd_incident_ack
    description: Acknowledge an incident (requires confirmation)
  - name: pd_incident_resolve
    description: Resolve an incident (requires confirmation)
  - name: pd_incident_note
    description: Add a note to an incident (requires confirmation)
  - name: pd_services
    description: List PagerDuty services and their current status
  - name: pd_recent
    description: Show recent incidents for a service (last 24h/7d)
---
```

## 2. Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PAGERDUTY_API_KEY` | Yes (for PD) | — | PagerDuty REST API v2 token. Recommend read-only key. |
| `PAGERDUTY_EMAIL` | No | — | User email for write operations (ack/resolve). PD API requires `From` header. |
| `OPSGENIE_API_KEY` | No | — | OpsGenie API key. Alternative to PagerDuty. |
| `PAGER_TRIAGE_PROVIDER` | No | `auto` | Force provider: `pagerduty`, `opsgenie`, or `auto` (detect from available keys). |

**Auto-detection logic:** If `PAGERDUTY_API_KEY` is set → use PagerDuty. If `OPSGENIE_API_KEY` is set → use OpsGenie. If both → prefer PagerDuty (more common). If neither → error with setup instructions.

## 3. Subcommands & Behavior

### 3.1 `pd_incidents` — List Active Incidents

**Purpose:** Show all triggered and acknowledged incidents, sorted by urgency then creation time.

**API Call:**
```bash
curl -s \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  -H "Content-Type: application/json" \
  "https://api.pagerduty.com/incidents?statuses[]=triggered&statuses[]=acknowledged&sort_by=urgency&limit=25&include[]=assignees&include[]=services"
```

**Output Schema:**
```json
{
  "tool": "pd_incidents",
  "provider": "pagerduty",
  "timestamp": "2026-02-16T03:45:00Z",
  "total_incidents": 3,
  "incidents": [
    {
      "id": "P123ABC",
      "incident_number": 4521,
      "title": "High CPU on prod-web-03",
      "status": "triggered",
      "urgency": "high",
      "service": {
        "id": "PSVC123",
        "name": "Production Web"
      },
      "created_at": "2026-02-16T03:00:00Z",
      "duration_minutes": 45,
      "assignments": [
        {"name": "Jane Doe", "email": "jane@company.com"}
      ],
      "alert_count": 3,
      "escalation_level": 1,
      "last_status_change": "2026-02-16T03:05:00Z"
    }
  ],
  "summary": "3 active incidents: 1 critical (triggered), 1 high (acknowledged), 1 low (triggered)"
}
```

**Determinism:** Output is machine-parseable JSON. `total_incidents` is an integer. `incidents` is always an array (empty if none). `status` is always one of: `triggered`, `acknowledged`. `urgency` is always one of: `high`, `low`.

### 3.2 `pd_incident_detail` — Incident Deep Dive

**Purpose:** Get full incident details including timeline (log entries), related alerts, and notes.

**Parameters:**
- `incident_id` (required): PagerDuty incident ID (e.g., `P123ABC`)

**API Calls (sequential):**
```bash
# 1. Incident details
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID?include[]=assignees&include[]=acknowledgers&include[]=conference_bridge"

# 2. Log entries (timeline)
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID/log_entries?limit=25&include[]=channels"

# 3. Alerts
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID/alerts?limit=25"

# 4. Notes
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID/notes"
```

**Output Schema:**
```json
{
  "tool": "pd_incident_detail",
  "incident": {
    "id": "P123ABC",
    "incident_number": 4521,
    "title": "High CPU on prod-web-03",
    "status": "triggered",
    "urgency": "high",
    "service": {"id": "PSVC123", "name": "Production Web"},
    "created_at": "2026-02-16T03:00:00Z",
    "duration_minutes": 45,
    "escalation_policy": {"id": "PESC123", "name": "Production Escalation"},
    "assignments": [
      {"name": "Jane Doe", "email": "jane@company.com", "escalation_level": 1}
    ],
    "acknowledgers": [],
    "description": "CPU usage exceeded 95% threshold for 5 minutes",
    "conference_bridge": null
  },
  "timeline": [
    {
      "type": "trigger_log_entry",
      "created_at": "2026-02-16T03:00:00Z",
      "summary": "Incident triggered via Prometheus Alertmanager",
      "channel_type": "api"
    },
    {
      "type": "escalate_log_entry",
      "created_at": "2026-02-16T03:05:00Z",
      "summary": "Escalated to Jane Doe (Level 1)"
    },
    {
      "type": "notify_log_entry",
      "created_at": "2026-02-16T03:05:30Z",
      "summary": "Notified Jane Doe via push, SMS"
    }
  ],
  "alerts": [
    {
      "id": "A456DEF",
      "status": "triggered",
      "summary": "CPU > 95% on prod-web-03",
      "severity": "critical",
      "created_at": "2026-02-16T03:00:00Z",
      "source": "Prometheus Alertmanager",
      "details": {"metric": "node_cpu_seconds_total", "value": "97.3%", "threshold": "95%"}
    }
  ],
  "notes": [],
  "analysis": {
    "duration": "45 minutes",
    "alert_count": 3,
    "escalation_count": 1,
    "acknowledged": false,
    "trigger_source": "Prometheus Alertmanager"
  }
}
```

**Determinism:** All fields are typed and deterministic. `timeline` is chronologically ordered. `alerts` array may be empty. `notes` array may be empty.

### 3.3 `pd_oncall` — On-Call Schedules

**Purpose:** Show who's on call now, upcoming rotations, and escalation paths.

**API Call:**
```bash
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/oncalls?earliest=true&include[]=users&include[]=schedules&include[]=escalation_policies"
```

**Output Schema:**
```json
{
  "tool": "pd_oncall",
  "oncalls": [
    {
      "user": {"name": "Jane Doe", "email": "jane@company.com"},
      "schedule": {"name": "Primary SRE", "id": "PSCHED1"},
      "escalation_policy": {"name": "Production Escalation", "id": "PESC123"},
      "escalation_level": 1,
      "start": "2026-02-15T17:00:00Z",
      "end": "2026-02-16T17:00:00Z"
    }
  ],
  "summary": "2 on-call schedules active. Primary SRE: Jane Doe. Secondary SRE: Bob Smith."
}
```

### 3.4 `pd_incident_ack` — Acknowledge Incident ⚠️ WRITE OPERATION

**Purpose:** Acknowledge a triggered incident. **Requires confirmation.**

**Parameters:**
- `incident_id` (required): PagerDuty incident ID

**Confirmation Gate (MANDATORY):**
Before executing, the skill MUST display:
```
⚠️ ACKNOWLEDGE INCIDENT
  ID: P123ABC (#4521)
  Title: High CPU on prod-web-03
  Service: Production Web
  Urgency: HIGH
  Duration: 45 minutes
  Alerts: 3

Acknowledge this incident? This will stop escalation. [y/N]
```

The agent MUST NOT proceed without explicit user confirmation.

**API Call (after confirmation):**
```bash
curl -s -X PUT \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  -H "From: $PAGERDUTY_EMAIL" \
  -H "Content-Type: application/json" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID" \
  -d '{"incident": {"type": "incident_reference", "status": "acknowledged"}}'
```

**Output Schema:**
```json
{
  "tool": "pd_incident_ack",
  "incident_id": "P123ABC",
  "status": "acknowledged",
  "acknowledged_at": "2026-02-16T03:46:00Z",
  "acknowledged_by": "jane@company.com"
}
```

### 3.5 `pd_incident_resolve` — Resolve Incident ⚠️ WRITE OPERATION

**Purpose:** Resolve an incident. **Requires confirmation.**

**Parameters:**
- `incident_id` (required): PagerDuty incident ID

**Confirmation Gate (MANDATORY):**
```
⚠️ RESOLVE INCIDENT
  ID: P123ABC (#4521)
  Title: High CPU on prod-web-03
  Service: Production Web
  Duration: 45 minutes
  Alerts: 3

Resolve this incident? This marks it as fixed. [y/N]
```

**API Call (after confirmation):**
```bash
curl -s -X PUT \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  -H "From: $PAGERDUTY_EMAIL" \
  -H "Content-Type: application/json" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID" \
  -d '{"incident": {"type": "incident_reference", "status": "resolved"}}'
```

### 3.6 `pd_incident_note` — Add Incident Note ⚠️ WRITE OPERATION

**Purpose:** Add a note/update to an incident. **Requires confirmation.**

**Parameters:**
- `incident_id` (required): PagerDuty incident ID
- `content` (required): Note text

**Confirmation Gate:**
```
⚠️ ADD NOTE TO INCIDENT P123ABC
  Note: "Identified root cause as memory leak in auth-service v2.14.3. Rolling back."

Add this note? [y/N]
```

**API Call:**
```bash
curl -s -X POST \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  -H "From: $PAGERDUTY_EMAIL" \
  -H "Content-Type: application/json" \
  "https://api.pagerduty.com/incidents/$INCIDENT_ID/notes" \
  -d '{"note": {"content": "..."}}'
```

### 3.7 `pd_services` — List Services

**Purpose:** List all PagerDuty services with their current status (active, warning, critical, disabled).

**API Call:**
```bash
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/services?include[]=integrations&limit=100"
```

**Output Schema:**
```json
{
  "tool": "pd_services",
  "services": [
    {
      "id": "PSVC123",
      "name": "Production Web",
      "status": "critical",
      "description": "Production web application servers",
      "created_at": "2024-01-15T00:00:00Z",
      "escalation_policy": "Production Escalation",
      "active_incidents": 2,
      "integrations": ["Prometheus Alertmanager", "CloudWatch"]
    }
  ],
  "summary": "12 services: 1 critical, 1 warning, 10 active, 0 disabled"
}
```

### 3.8 `pd_recent` — Recent Incident History

**Purpose:** Show recent incidents for a service or across all services.

**Parameters:**
- `service_id` (optional): Filter to specific service
- `since` (optional, default: `24h`): Time window — `24h`, `7d`, `30d`

**API Call:**
```bash
curl -s -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  "https://api.pagerduty.com/incidents?since=$SINCE&until=now&service_ids[]=$SERVICE_ID&limit=25&sort_by=created_at:desc"
```

**Output Schema:**
```json
{
  "tool": "pd_recent",
  "period": "last 24 hours",
  "service": "Production Web",
  "incidents": [
    {
      "id": "P123ABC",
      "title": "High CPU on prod-web-03",
      "status": "resolved",
      "urgency": "high",
      "created_at": "2026-02-16T03:00:00Z",
      "resolved_at": "2026-02-16T04:15:00Z",
      "duration_minutes": 75,
      "alert_count": 3
    }
  ],
  "stats": {
    "total": 5,
    "by_urgency": {"high": 2, "low": 3},
    "by_status": {"resolved": 4, "triggered": 1},
    "mean_time_to_resolve_minutes": 42
  }
}
```

---

## 4. OpsGenie Fallback

If `OPSGENIE_API_KEY` is set instead of `PAGERDUTY_API_KEY`, map the same subcommands to OpsGenie's API:

| Subcommand | OpsGenie Endpoint |
|------------|-------------------|
| `pd_incidents` | `GET https://api.opsgenie.com/v2/alerts?status=open` |
| `pd_incident_detail` | `GET https://api.opsgenie.com/v2/alerts/{id}` |
| `pd_oncall` | `GET https://api.opsgenie.com/v2/schedules/{id}/on-calls` |
| `pd_incident_ack` | `POST https://api.opsgenie.com/v2/alerts/{id}/acknowledge` |
| `pd_incident_resolve` | `POST https://api.opsgenie.com/v2/alerts/{id}/close` |
| `pd_incident_note` | `POST https://api.opsgenie.com/v2/alerts/{id}/notes` |
| `pd_services` | `GET https://api.opsgenie.com/v1/services` |

**OpsGenie Auth Header:** `Authorization: GenieKey $OPSGENIE_API_KEY`

**Note:** OpsGenie support is a Day 2 stretch goal. Day 1 focuses entirely on PagerDuty. The output schemas should be normalized so the agent sees the same structure regardless of provider.

---

## 5. Failover Plan

| Failure | Detection | Fallback |
|---------|-----------|----------|
| PagerDuty API unreachable | HTTP timeout (10s) or 5xx response | Retry once after 2s. If still failing, report "PagerDuty API is unreachable. Check https://status.pagerduty.com/" |
| Invalid API key | HTTP 401 response | Report "Invalid PAGERDUTY_API_KEY. Create a read-only API key at Settings → API Access Keys." |
| Rate limited | HTTP 429 response | Report "PagerDuty rate limit hit. Wait 30 seconds and retry." (960 req/min limit is very generous — this should be rare.) |
| `pd` CLI installed locally | Check `which pd` | If PagerDuty API fails AND `pd` CLI is found, fall back to `pd incident:list --json`, `pd incident:open --json`, etc. |
| No env vars set | Neither `PAGERDUTY_API_KEY` nor `OPSGENIE_API_KEY` present | Error with setup guide: "Set PAGERDUTY_API_KEY or OPSGENIE_API_KEY. See setup guide below." |
| PAGERDUTY_EMAIL not set for write ops | Missing `From` header | Error: "Set PAGERDUTY_EMAIL to your PagerDuty login email. Required for acknowledge/resolve operations." |

---

## 6. Security Constraints

### Read-Only by Default
The following operations are **always allowed** without confirmation:
- `pd_incidents` (list)
- `pd_incident_detail` (read)
- `pd_oncall` (read)
- `pd_services` (list)
- `pd_recent` (read)

### Confirmation-Gated (Write Operations)
The following operations **MUST** display a confirmation prompt and wait for explicit user approval:
- `pd_incident_ack` — acknowledging stops escalation
- `pd_incident_resolve` — resolving marks the incident as fixed
- `pd_incident_note` — adds permanent record to incident

### Credential Handling
- API keys read from environment variables ONLY
- NEVER log, display, or include API keys in output
- NEVER include API keys in error messages
- If the user asks "what's my API key?" respond with "I don't display credentials for security. Check your PAGERDUTY_API_KEY environment variable."

### API Key Permissions
The SKILL.md setup guide MUST recommend creating a **read-only** API key for initial setup, with write permissions added only if the user wants ack/resolve capability. Document how to create both:
1. Read-only key: Settings → API Access Keys → Create → Read-only
2. Full key: Settings → API Access Keys → Create → Full Access

---

## 7. Quality Gate Checklist

The following MUST pass before reviewer sign-off:

### Functionality Gates
- [ ] `pd_incidents` returns valid JSON with correct schema when incidents exist
- [ ] `pd_incidents` returns empty `incidents` array (not error) when no active incidents
- [ ] `pd_incident_detail` returns full incident with timeline, alerts, and notes
- [ ] `pd_incident_detail` returns clear error for invalid incident ID
- [ ] `pd_oncall` returns current on-call schedules
- [ ] `pd_services` lists services with correct status indicators
- [ ] `pd_recent` returns incident history with accurate stats
- [ ] All write operations show confirmation prompt before executing
- [ ] Write operations fail gracefully when `PAGERDUTY_EMAIL` is not set

### Safety Gates
- [ ] No API key appears in any output or error message
- [ ] `pd_incident_ack` cannot execute without explicit user confirmation
- [ ] `pd_incident_resolve` cannot execute without explicit user confirmation
- [ ] `pd_incident_note` cannot execute without explicit user confirmation
- [ ] Invalid API key produces helpful error (not stack trace)
- [ ] Missing env vars produce setup guide (not crash)

### Schema Gates
- [ ] All tool outputs are valid JSON
- [ ] All timestamps are ISO 8601
- [ ] `total_incidents` is always an integer
- [ ] `incidents` is always an array
- [ ] `status` values are from documented enum set
- [ ] Empty states return empty arrays, not null

### Documentation Gates
- [ ] SKILL.md includes step-by-step PagerDuty API key creation guide
- [ ] SKILL.md includes example interactions for each subcommand
- [ ] SKILL.md explains read-only vs full-access key differences
- [ ] SKILL.md includes OpsGenie setup instructions (even if Day 2)
- [ ] README includes "What's firing?" quickstart example

---

## 8. Test Plan

### Smoke Tests (Run Before Every Publish)

```bash
# Test 1: List incidents (read-only)
# Expected: JSON with incidents array, summary string
# Pass if: valid JSON, no error, incidents is array

# Test 2: Get incident detail for known incident
# Expected: JSON with incident object, timeline array, alerts array
# Pass if: valid JSON, timeline is chronologically ordered

# Test 3: Show on-call schedules
# Expected: JSON with oncalls array
# Pass if: valid JSON, each oncall has user.name and schedule.name

# Test 4: List services
# Expected: JSON with services array, summary string
# Pass if: valid JSON, each service has status field

# Test 5: Recent incidents (last 24h)
# Expected: JSON with incidents array and stats object
# Pass if: valid JSON, stats.total matches incidents array length

# Test 6: Missing API key
# Expected: Helpful error message with setup instructions
# Pass if: error message includes "PAGERDUTY_API_KEY" and setup URL

# Test 7: Invalid API key
# Expected: "Invalid PAGERDUTY_API_KEY" error
# Pass if: no stack trace, clear error message

# Test 8: Write operation without PAGERDUTY_EMAIL
# Expected: Error requesting PAGERDUTY_EMAIL
# Pass if: clear error, no API call attempted

# Test 9: Confirmation gate (ack)
# Expected: Confirmation prompt displayed with incident details
# Pass if: incident title, service name, and urgency shown in prompt

# Test 10: Empty state (no active incidents)
# Expected: JSON with empty incidents array and "No active incidents" summary
# Pass if: valid JSON, incidents is empty array, no error
```

### Integration Test (Manual, with real PD account)

1. Create a test incident via PagerDuty API
2. Run `pd_incidents` → verify it appears
3. Run `pd_incident_detail` → verify timeline shows trigger
4. Run `pd_incident_ack` → confirm → verify status changes
5. Run `pd_incident_note` → add note → verify note appears
6. Run `pd_incident_resolve` → confirm → verify resolution
7. Run `pd_recent` → verify resolved incident in history

---

## 9. SKILL.md Content Structure

The SKILL.md should be structured as follows:

```markdown
# PagerDuty Incident Triage

AI-powered incident triage for PagerDuty. Read-only by default. Write operations require confirmation.

## Quick Setup

1. Go to PagerDuty → Settings → API Access Keys
2. Click "Create New API Key"
3. Name it "OpenClaw Agent" and select "Read-only" (or "Full Access" for ack/resolve)
4. Copy the key
5. Set environment variable: `export PAGERDUTY_API_KEY=your_key_here`
6. (Optional for write ops) Set: `export PAGERDUTY_EMAIL=your@email.com`

## What You Can Do

### Read Operations (always safe)
- "What's firing on PagerDuty?" → Lists all active incidents
- "Tell me about incident P123ABC" → Full details with timeline
- "Who's on call?" → Current on-call schedules
- "Show me all services" → Service health overview
- "What happened in the last 24 hours?" → Recent incident history

### Write Operations (confirmation required)
- "Acknowledge incident P123ABC" → ⚠️ Requires confirmation
- "Resolve incident P123ABC" → ⚠️ Requires confirmation
- "Add a note to incident P123ABC" → ⚠️ Requires confirmation

## Tools Reference

[... tool definitions as specified in frontmatter ...]

## OpsGenie Support

[... OpsGenie setup instructions ...]

## Security

- API keys are read from environment variables only
- Read-only mode by default
- All write operations require explicit user confirmation
- We recommend starting with a read-only API key
```

---

## 10. Implementation Notes for Builder

### Priority Order
1. **pd_incidents** — the "hello world" of this skill. Ship this first, test it immediately.
2. **pd_incident_detail** — the money feature. Timeline + alert correlation is the "holy shit" moment.
3. **pd_oncall** — simple and useful.
4. **pd_services** — context for incidents.
5. **pd_recent** — historical context.
6. **pd_incident_ack** — first write operation. Get the confirmation gate pattern right here.
7. **pd_incident_resolve** — same pattern as ack.
8. **pd_incident_note** — same pattern, different API call.

### Key Implementation Details
- PagerDuty API v2 base URL: `https://api.pagerduty.com`
- Auth header: `Authorization: Token token=$PAGERDUTY_API_KEY`
- Write ops require `From: $PAGERDUTY_EMAIL` header
- All responses are JSON
- Pagination: PagerDuty uses `offset`/`limit` pagination. Default `limit=25` is fine for most ops. If `more: true` in response, there are additional pages.
- Time format: ISO 8601 throughout. Use `since`/`until` query params for time-ranged queries.
- Include params: Use `include[]=` query params to embed related objects (avoids extra API calls).

### What NOT to Build (MVP exclusions)
- ❌ No incident creation (too dangerous for v1)
- ❌ No escalation policy modification
- ❌ No schedule management
- ❌ No maintenance window creation
- ❌ No webhook setup
- ❌ No real-time streaming/polling (just point-in-time queries)
- ❌ No multi-account support in v1

### Agent Guidance in SKILL.md
Include guidance for the LLM agent on HOW to use these tools effectively:
- When user says "what's wrong?" or "what's firing?" → start with `pd_incidents`
- When user mentions a specific incident → use `pd_incident_detail`
- When triaging → show incidents first, then detail on the most urgent one
- When user wants to act → ALWAYS show confirmation with full context
- When correlating → look for incidents on the same service, similar timeframes
- Suggest checking prom-query or kube-medic for deeper investigation if those skills are installed
