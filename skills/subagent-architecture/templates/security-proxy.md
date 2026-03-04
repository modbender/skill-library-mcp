# Security Proxy Pattern

**Use case:** Isolate high-risk operations from main agent context (API calls to untrusted services, experimental features, sandbox testing)

## Core Philosophy

**Blast Shield Approach:**
- Proxy receives minimal context (only what's needed for its task)
- Cannot access main agent's memory, knowledge base, or sensitive files
- Tool restrictions enforced (no file writes outside designated sandbox)
- Single-purpose design (one proxy per untrusted service/API)
- Automatic termination after task completion

## Architecture

```
Main Agent
    │
    ├─ Spawns Security Proxy (minimal context)
    │       │
    │       ├─ Rate limiter (self-imposed)
    │       ├─ Accesses untrusted API/service
    │       ├─ Filters/validates INBOUND responses (Stages 1-6)
    │       ├─ Filters outbound content (Stage 6b: semantic leak scan)
    │       └─ Returns sanitized data only
    │
    └─ Receives filtered output (never raw API responses)

On adversarial crash:
    └─ Pre-death checklist → crash report → core decides: re-spawn / escalate / quarantine
```

## Template Structure

```markdown
## [ProxyName] - Isolated interface for [ServiceName]

**Created:** YYYY-MM-DD
**Type:** Security proxy (ephemeral)
**Isolation level:** Maximum
**Tool restrictions:** [list allowed tools]

### Purpose
Access [untrusted service] without exposing main agent context.

### Context Provided
**Minimal input only:**
- Query/request parameters
- Output format requirements
- NO workspace paths, NO user data, NO API keys (use env vars)

### Allowed Tools
- [specific tool subset, e.g., exec with command whitelist]
- NO read/write to $WORKSPACE
- NO message tool (no external comms)
- NO browser access to authenticated sessions

### Input Validation Pipeline
All data received from the external service goes through:
1. Size & type validation (reject binary, oversized payloads)
2. Encoding normalization (UTF-8, strip null bytes, reject BIDI overrides)
3. HTML sanitization (DOMPurify or equivalent allowlist-based)
4. Injection pattern detection (prompt injection, code injection — runs on ALL content regardless of source trust level)
5. Schema validation (Ajv or equivalent, with recursion depth limits)
6. Output sanitization (escape outbound HTML)
6b. Outbound semantic leak filter (see below)

**⚠️ Trust tier never bypasses Stage 4.** Even if a source has Ally-tier trust, injection detection always runs. Trust affects engagement policy and schema strictness — not security scanning.

### Outbound Semantic Leak Filter (Stage 6b)
Before the proxy posts or returns ANY content to an external service, scan for:
- Owner PII: Discord snowflake IDs (`\b\d{17,19}\b`), email patterns, phone numbers
- Internal paths: `/data/.openclaw`, `memory/owner/`
- API key formats: `sk-[20+]`, `xai-[20+]`, `Bearer [16+]`
- Internal terms: `SOUL.md`, `MEMORY.md`, `openclaw.json`

**Policy: any match = hard block. No partial redaction. Log pattern IDs + content hash. Alert core.**

### Rate Limiting (Self-Imposed)
The proxy enforces its own outbound request limits regardless of task instructions:

```javascript
// Recommended defaults — tune per service
const rateLimiter = new RateLimiter({
  maxPerMinute: 10,
  maxPerHour:   100,
  burnLimit:    200,      // Self-terminate + crash report if exceeded
  cbThreshold:  3,        // Circuit breaker opens after 3 consecutive 429s
  cbBaseMs:     30_000,   // 30s base backoff
  cbMaxMs:      900_000   // 15min ceiling
});
```

If the service returns 3 consecutive 429s: pause, alert core, exponential backoff.
If burn limit is hit: self-terminate, file crash report, do not re-attempt.

### Output Sanitization
**Return only:**
- Validated data (schema-checked)
- Summary/analysis (no raw API dumps)
- Error messages (sanitized, no stack traces with paths)

### Termination
- Auto-kill after single task completion
- No persistent state
- No caching of credentials
- On adversarial crash: pre-death checklist (flush logs, write crash report, mark drafts ABANDONED)

### Example Spawn Command
\`\`\`
sessions_spawn({
  label: "proxy-[service]",
  task: "Query [service] for [data] and return validated JSON schema",
  context: "[query params only — no workspace paths, no credentials]",
  timeout_minutes: 5,
  model: "haiku"  // lightweight; proxies should be cheap
})
\`\`\`
```

## Security Checklist

**Pre-spawn:**
- [ ] Proxy receives only task-specific parameters (no full workspace context)
- [ ] No authentication tokens in spawn context (pass via env vars or scoped encrypted token)
- [ ] Output validation schema defined before spawning
- [ ] Rate limiter configured with appropriate limits for target service
- [ ] Cost estimate < $0.10 (proxies should be lightweight)

**Proxy implementation:**
- [ ] Tool restrictions enforced (whitelist, not blacklist)
- [ ] Inbound pipeline: all 6 stages present (size → encoding → HTML → injection → schema → output)
- [ ] Stage 4 injection detection runs on ALL content — no trust tier bypass
- [ ] Outbound Stage 6b semantic leak scan on all posts/returns to external service
- [ ] Rate limiter active before first outbound request
- [ ] Crash/recovery checklist implemented (Section: Crash & Recovery)
- [ ] Logging excludes sensitive data (hashes/lengths only, never content)

**Post-spawn:**
- [ ] Verify crash report absent (clean termination)
- [ ] Review audit log for unexpected patterns
- [ ] If adversarial crash: quarantine workspace, alert human before re-spawn

## Crash & Recovery

Every security proxy should implement a pre-death checklist. On any termination (adversarial or clean):

**Pre-death checklist (in order):**
1. Flush all buffered audit log entries to `[workspace]/logs/audit.jsonl`
2. Write crash report to `[workspace]/logs/crash-{TIMESTAMP}.json`
3. Mark any in-progress drafts as `ABANDONED`
4. Do NOT write credentials/tokens to disk

**Crash report schema:**
```json
{
  "crash_id": "crash-{ISO_TIMESTAMP}",
  "timestamp": "{ISO_TIMESTAMP}",
  "trigger": "INJECTION_DETECTED | BURN_LIMIT | POLICY_VIOLATION | EXCEPTION | AUTH_FAILURE",
  "trigger_detail": "human-readable description",
  "last_action": "last tool call made",
  "session_request_count": 0,
  "suspicious_content_hash": "sha256-prefix-16-chars (if adversarial)",
  "suspicious_content_length": 0,
  "adversarial": true,
  "files_written_this_session": []
}
```

**Core agent response logic:**
```
Read crash report
  │
  ├─ adversarial: false → re-spawn with same task (log + monitor)
  │
  └─ adversarial: true
          ├─ no state modified → alert human, do not re-spawn until cleared
          └─ state modified → QUARANTINE: archive workspace, restore from backup,
                              human review required before any re-spawn
```

**Human notification:** adversarial crashes always trigger immediate user alert (Discord or configured channel). Log-only is insufficient for adversarial events.

## Identity Continuity (for Long-Running Proxies)

If your proxy maintains a persistent external identity (e.g., a social network account, API user) across multiple ephemeral spawns, you need to manage this tension explicitly:

**The problem:** Ephemeral process + persistent external identity. Each spawn has no memory of prior spawns, but external parties see a single consistent entity.

**Solution:**
- Credentials stored in core agent memory only (never in proxy workspace)
- Scoped, short-lived token passed at spawn time (TTL: 2 hours max; never written to disk)
- State persists only via workspace files (logs, relationship data, drafts) — proxy reads these at startup
- Core injects "recent context" summary for consistency (last N interactions per active relationship)
- Token rotation scheduled by core (weekly), not proxy

**Anti-pattern:** Do NOT store session tokens in `[workspace]/config.json` or any file the proxy reads at startup — if the proxy is compromised, it should not also compromise the account credentials.

## Real-World Example

**MoltbookProxy** — production implementation of this pattern:
- Full spec: `specs/moltbook-proxy-security.md`
- Implements all 6 inbound stages + Stage 6b outbound semantic filter
- Rate limiter: 10/min, 100/hr, 200 burn limit
- Circuit breaker: 3 consecutive 429s → pause + core alert
- Persistent Moltbook account (`CedarProxy`) with ephemeral process
- Crash/recovery: pre-death checklist, quarantine mode, Discord alerts on adversarial crash
- Social trust system: tiered relationships (Acquaintance → Friend → Ally) with Stage 4 always running regardless of tier

## When NOT to Use

- **Trusted first-party APIs** (your own infrastructure)
- **Simple read-only operations** (public web scraping with web_fetch)
- **Low-risk tasks** (task routing score < 30/100)

## Cost Optimization

Security proxies should be:
- **Fast** (single API call, minimal processing)
- **Cheap** (< $0.05 per spawn, use Haiku)
- **Ephemeral** (no multi-turn conversations, no research phase)

If your proxy is costing > $0.10 per spawn, it's doing too much. Split the task or re-evaluate the pattern.

## Integration

Works with:
- **task-routing** (auto-spawn proxies for high blast-radius tasks)
- **cost-governor** (enforce budget limits on proxy operations)
- **drift-guard** (audit proxy behavior for policy violations)
- **proxy-recovery.md** (crash/recovery pattern — see `templates/proxy-recovery.md`)
