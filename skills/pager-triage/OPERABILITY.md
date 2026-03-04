# Operability Guide — pager-triage

**Version:** 0.1.1
**Last updated:** 2026-02-16

---

## 1. Failure Modes

| Failure | Detection | Behavior | User-Visible Output |
|---------|-----------|----------|---------------------|
| **PagerDuty API unreachable** | `curl` timeout (10s) or connection refused | Retry once after 2s backoff. If still failing, exit with error. | `{"error": "PagerDuty API is unreachable. Check https://status.pagerduty.com/"}` |
| **Invalid API key** | HTTP 401 response | Immediate failure, no retry | `{"error": "Invalid PAGERDUTY_API_KEY (****xxxx). Create a read-only API key at PagerDuty → Settings → API Access Keys."}` |
| **Insufficient permissions** | HTTP 403 response | Immediate failure, no retry | `{"error": "Access denied (HTTP 403). Your API key (****xxxx) lacks permission for this operation."}` |
| **Rate limited** | HTTP 429 response | Immediate failure, no retry (429 is unlikely with 960 req/min limit) | `{"error": "PagerDuty rate limit hit (HTTP 429). Wait 30 seconds and retry."}` |
| **Server error** | HTTP 5xx response | Retry once after 2s backoff | After 2 attempts: `{"error": "PagerDuty API error (HTTP 5xx). Check https://status.pagerduty.com/"}` |
| **Missing API key** | `PAGERDUTY_API_KEY` env var empty/unset | Immediate failure, no API call | `{"error": "PAGERDUTY_API_KEY is not set. Create a REST API v2 key at PagerDuty → Settings → API Access Keys..."}` |
| **Missing email (write ops)** | `PAGERDUTY_EMAIL` env var empty/unset | Immediate failure, no API call | `{"error": "PAGERDUTY_EMAIL is not set. Required for write operations..."}` |
| **Missing dependencies** | `curl` or `jq` not found via `command -v` | Immediate failure | `{"error": "Required dependency 'curl' is not installed."}` |
| **Invalid incident ID** | Regex validation `^[A-Za-z0-9]+$` fails | Immediate failure, no API call | `{"error": "Invalid incident ID format. Expected alphanumeric, got: ..."}` |
| **Non-HTTPS URL** | URL scheme check | Immediate failure, no network call | `{"error": "Refusing non-HTTPS URL: ..."}` |

---

## 2. Retry Behavior

### What gets retried
- **5xx errors** (server errors): 1 retry after 2-second sleep
- **Network failures** (connection refused, timeout): 1 retry after 2-second sleep

### What does NOT get retried
- **4xx errors** (client errors: 401, 403, 429, 404, etc.): Immediate failure. These are deterministic — retrying won't help.
- **Input validation failures**: No network call is made, so nothing to retry.

### Retry timing
```
Attempt 1: immediate
  ↓ (fail with 5xx or network error)
  sleep 2s
Attempt 2: retry
  ↓ (fail again)
  exit with error
```

**Maximum total wait for a single API call:** ~24 seconds (10s timeout × 2 attempts + 2s backoff + 2s buffer).

### Why only 1 retry
- PagerDuty API is highly available (99.99% SLA on most plans)
- 5xx errors are almost always transient and resolve within seconds
- Aggressive retries risk hitting the rate limit
- The user is waiting at 3am — faster failure is better than slow failure

---

## 3. Timeout Handling

| Component | Timeout | Configured Via |
|-----------|---------|----------------|
| **curl connection + transfer** | 10 seconds | `--max-time 10` in `curl` args |
| **Total per-subcommand (worst case)** | ~24 seconds | 2 attempts × 10s timeout + 2s backoff + jq processing |
| **jq processing** | Unbounded (but fast) | Not explicitly bounded; PagerDuty response sizes are small |

### Timeout scenarios
- **Normal case:** API responds in 200–500ms. Total subcommand time: < 1 second.
- **Slow API:** API responds in 5 seconds. Total: ~5 seconds.
- **API down:** First timeout at 10s, retry at 12s, second timeout at 22s, error at ~24s.

### Detail subcommand (4 sequential API calls)
The `detail` subcommand makes 4 API calls sequentially (incident, log_entries, alerts, notes). In the worst case:
- **Normal:** 4 × 500ms = ~2 seconds
- **Worst case:** 4 × 10s timeout × 2 attempts = ~96 seconds (extremely unlikely)

If this becomes an issue in practice, the calls could be parallelized in a future version.

---

## 4. Deterministic Parsing Contracts

The tool transforms PagerDuty API responses into normalized JSON using `jq`. These are the contracts the agent and downstream consumers can rely on:

### All subcommands
- Output is **always valid JSON** (or a JSON error on stderr)
- The `tool` field identifies which subcommand produced the output
- All timestamps are **ISO 8601** format (`YYYY-MM-DDTHH:MM:SSZ`)
- Array fields are **always arrays** (never `null`) — empty state is `[]`
- Integer fields are **always integers** — `total_incidents`, `alert_count`, `escalation_level`, etc.

### pd_incidents
```
.tool              = "pd_incidents"           (string, constant)
.provider          = "pagerduty"              (string)
.timestamp         = ISO 8601                 (string)
.total_incidents   = integer ≥ 0
.incidents         = array of incident objects
.incidents[].id    = string (alphanumeric PD ID)
.incidents[].status ∈ {"triggered", "acknowledged"}
.incidents[].urgency ∈ {"high", "low"}
.summary           = human-readable string
```

### pd_incident_detail
```
.tool              = "pd_incident_detail"     (string, constant)
.incident.id       = string
.incident.status   ∈ {"triggered", "acknowledged", "resolved"}
.timeline          = array, sorted by .created_at ascending
.alerts            = array (may be empty)
.notes             = array (may be empty)
.analysis.alert_count     = integer ≥ 0
.analysis.acknowledged    = boolean
.analysis.trigger_source  = string
```

### pd_oncall
```
.tool              = "pd_oncall"              (string, constant)
.oncalls           = array of on-call assignment objects
.oncalls[].user.name     = string
.oncalls[].escalation_level = integer ≥ 1
.summary           = human-readable string
```

### pd_services
```
.tool              = "pd_services"            (string, constant)
.services          = array of service objects
.services[].status ∈ {"active", "warning", "critical", "disabled"}
.summary           = human-readable string
```

### pd_recent
```
.tool              = "pd_recent"              (string, constant)
.period            = human-readable string
.incidents         = array
.stats.total       = integer ≥ 0
.stats.by_urgency  = object (keys are urgency values, values are counts)
.stats.by_status   = object (keys are status values, values are counts)
.stats.mean_time_to_resolve_minutes = integer or null
```

### Write operations (ack, resolve, note)
```
.tool              = "pd_incident_ack" | "pd_incident_resolve" | "pd_incident_note"
.incident_id       = string
.status            = new status (for ack/resolve)
```

### Error output
```
stderr: {"error": "human-readable error message"}
exit code: 1
stdout: (empty)
```

---

## 5. PagerDuty API Assumptions

The tool depends on these PagerDuty REST API v2 behaviors:

| Assumption | Risk if violated |
|-----------|-----------------|
| `GET /incidents` returns `{"incidents": [...]}` | `jq` parsing fails; output is empty or malformed |
| `GET /incidents/{id}` returns `{"incident": {...}}` | Detail command fails |
| `GET /oncalls` returns `{"oncalls": [...]}` | Oncall command fails |
| `GET /services` returns `{"services": [...]}` | Services command fails |
| Pagination uses `offset`/`limit`; `more: true` indicates more pages | Tool returns at most 25/100 items (by design) |
| Auth via `Authorization: Token token=...` header | All requests fail with 401 |
| Write ops require `From:` header with valid email | Ack/resolve/note fail with 400 |
| Status values are `triggered`, `acknowledged`, `resolved` | Agent may see unexpected values |
| Urgency values are `high`, `low` | Agent may see unexpected values |

### API version pinning
The tool targets PagerDuty REST API **v2** (the current stable version as of 2026). PagerDuty has not announced deprecation plans. The base URL `https://api.pagerduty.com` routes to v2 by default.

---

## 6. Observability Checklist

| What to monitor | How |
|----------------|-----|
| API key validity | Watch for 401 errors in tool output |
| Rate limit proximity | Watch for 429 errors (rare with 960/min limit) |
| API latency | Time the subcommand execution; > 5s suggests PD issues |
| PagerDuty status | https://status.pagerduty.com/ |
| Tool availability | Run `smoke.sh` periodically |

---

<sub>Operability documentation for pager-triage v0.1.1 · [Anvil AI](https://anvil-ai.io)</sub>
