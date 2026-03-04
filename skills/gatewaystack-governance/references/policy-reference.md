# Policy Configuration Reference

The governance policy is defined in `policy.json` at the skill root. This file controls the five core governance checks and three optional features.

## Schema

### `allowedTools` (required)

A map of tool names to their access policies. **Deny-by-default**: any tool not listed here is blocked.

```json
{
  "allowedTools": {
    "ToolName": {
      "roles": ["role1", "role2"],
      "maxArgsLength": 5000,
      "description": "Human-readable description"
    }
  }
}
```

- `roles` — array of role strings. User must have at least one matching role. If omitted or empty, any authenticated user can use the tool.
- `maxArgsLength` — maximum character length for tool arguments. Prevents payload stuffing.
- `description` — for documentation only; not enforced.

### `rateLimits` (required)

```json
{
  "rateLimits": {
    "perUser": { "maxCalls": 100, "windowSeconds": 3600 },
    "perSession": { "maxCalls": 30, "windowSeconds": 300 }
  }
}
```

- `perUser` — sliding window rate limit per resolved user identity
- `perSession` — sliding window rate limit per session identifier
- Both limits apply independently; the stricter one wins

### `identityMap` (required)

Maps OpenClaw agent IDs to governance identities. Since OpenClaw is a single-user personal AI, the identity map governs *agents* (e.g. "main", "ops", "dev"), not human users.

```json
{
  "identityMap": {
    "main": { "userId": "agent-main", "roles": ["admin"] },
    "ops": { "userId": "agent-ops", "roles": ["default"] },
    "dev": { "userId": "agent-dev", "roles": ["default", "admin"] },
    "unknown": { "userId": "unknown-agent", "roles": ["default"] }
  }
}
```

- Keys are agent IDs as reported by `ctx.agentId` in plugin mode, or passed via `--user` in CLI mode
- `userId` — the canonical identity for audit logging and rate limiting
- `roles` — governs which tools this identity can access
- The `"unknown"` entry is a catch-all for unrecognized agents

### `injectionDetection` (required)

```json
{
  "injectionDetection": {
    "enabled": true,
    "sensitivity": "medium",
    "customPatterns": ["my_custom_regex"],
    "obfuscationDetection": true,
    "multiLanguage": true,
    "canaryTokens": []
  }
}
```

- `enabled` — toggle injection detection on/off
- `sensitivity` — `"low"` | `"medium"` | `"high"`
  - `high`: all patterns checked (instruction injection, credential exfiltration, reverse shells, role impersonation, suspicious URLs, sensitive file access)
  - `medium`: high + medium patterns (default, recommended)
  - `low`: only high-severity patterns (instruction injection, credential exfiltration, reverse shells)
- `customPatterns` — array of regex strings for org-specific patterns. Each pattern has a 50ms timeout to guard against ReDoS.
- `obfuscationDetection` — (default `true`) decode base64, hex, URL-encoded, and unicode-escape segments, then re-scan for injection patterns
- `multiLanguage` — (default `true`) scan for injection phrases in Chinese, Japanese, Korean, Russian, Spanish, German, French, Portuguese, Arabic, and Hindi
- `canaryTokens` — array of strings planted in sensitive data. If any appear in tool arguments, it indicates data leakage.

### `auditLog` (required)

```json
{
  "auditLog": {
    "path": "audit.jsonl",
    "maxFileSizeMB": 100
  }
}
```

- `path` — file path for the append-only audit log (JSONL format)
- `maxFileSizeMB` — when the log exceeds this size, it rotates (renames with timestamp, starts fresh)

---

## Optional Features

The following three sections are **all optional and disabled by default**. The core five checks work without them. Enable features one at a time in `policy.json`.

### `outputDlp` (optional)

Scans tool output for PII and sensitive data. Requires [`@gatewaystack/transformabl-core`](https://github.com/davidcrowe/GatewayStack):

```bash
npm install @gatewaystack/transformabl-core
```

```json
{
  "outputDlp": {
    "enabled": false,
    "mode": "log",
    "redactionMode": "mask",
    "customPatterns": []
  }
}
```

- `enabled` — toggle output DLP on/off
- `mode` — `"log"` | `"block"`
  - `"log"`: scan output and write DLP matches to the audit log, but don't modify output. Uses the `after_tool_call` hook (observational only).
  - `"block"`: scan output and redact PII before the agent sees it. Uses the `tool_result_persist` hook to modify output in-flight.
- `redactionMode` — `"mask"` | `"remove"`
  - `"mask"`: replace PII with masked placeholder (e.g. `***-**-6789`)
  - `"remove"`: strip PII entirely
- `customPatterns` — additional pattern strings passed to `transformabl-core`'s `detectPii()`

If `@gatewaystack/transformabl-core` is not installed and `outputDlp.enabled` is `true`, the plugin throws a clear error with install instructions.

### `escalation` (optional)

Human-in-the-loop review for ambiguous detections. No external dependencies required.

```json
{
  "escalation": {
    "enabled": false,
    "reviewOnMediumInjection": true,
    "reviewOnFirstToolUse": false,
    "tokenTTLSeconds": 300
  }
}
```

- `enabled` — toggle escalation on/off
- `reviewOnMediumInjection` — when `true`, medium-severity injection detections trigger a review instead of a hard block. HIGH-severity injections always block regardless.
- `reviewOnFirstToolUse` — when `true`, the first time an agent uses any tool triggers a review. Subsequent uses of the same tool by the same agent are allowed without review.
- `tokenTTLSeconds` — how long an approval token remains valid (default: 300 seconds / 5 minutes)

**Approval workflow:**

1. Governance blocks the tool call with a structured message containing an approval token (`gw-rev-...`)
2. A human reviews the context and runs: `gatewaystack-governance approve gw-rev-<token>`
3. The agent retries the same tool call — the hook finds the valid approval and allows it
4. The token is consumed (single-use) and expired tokens are cleaned up automatically

**Severity classification:**

| Match prefix | Severity | Behavior with escalation |
|---|---|---|
| `HIGH:`, `EXTRACTION:`, `OBFUSCATED:` | HIGH | Always blocked |
| `MEDIUM:`, `MULTILANG:`, `CANARY:` | MEDIUM | Review (if `reviewOnMediumInjection`) |
| `LOW:` | LOW | Blocked |
| `CUSTOM:` | LOW | Blocked |

State files (gitignored):
- `.agent-tool-usage.json` — tracks which tools each agent has used
- `.pending-reviews.json` — stores pending and approved tokens

### `behavioralMonitoring` (optional)

Detects anomalous tool usage by comparing the current session against a historical baseline. Optionally uses [`@gatewaystack/limitabl-core`](https://github.com/davidcrowe/GatewayStack) for workflow-level limits:

```bash
npm install @gatewaystack/limitabl-core
```

```json
{
  "behavioralMonitoring": {
    "enabled": false,
    "spikeThreshold": 3.0,
    "monitoringWindowSeconds": 3600,
    "action": "log"
  }
}
```

- `enabled` — toggle behavioral monitoring on/off
- `spikeThreshold` — multiplier for frequency spike detection. If current call rate exceeds `spikeThreshold` times the baseline average, it's flagged. Default `3.0` means 3x the baseline.
- `monitoringWindowSeconds` — the sliding window for counting calls and building baselines (default: 3600 = 1 hour)
- `action` — `"log"` | `"review"` | `"block"`
  - `"log"`: record anomalies in the audit log but allow the tool call
  - `"review"`: trigger an escalation review (requires `escalation.enabled: true`)
  - `"block"`: deny the tool call

**Building a baseline:**

Before enabling monitoring, build a baseline from your existing audit log:

```bash
node scripts/governance-gateway.js --action build-baseline
```

This reads `audit.jsonl`, calculates average call rates and known tools, and saves the result to `.behavioral-baseline.json` (gitignored). The baseline is cached in memory with a 60-second TTL.

**Anomaly types:**

| Type | Severity | Description |
|---|---|---|
| `new-tool` | medium | Agent uses a tool not seen in the baseline |
| `frequency-spike` | high | Current call rate exceeds `spikeThreshold` x baseline average |
| `unusual-pattern` | low | No baseline exists for this agent |

---

## Audit Log Format

Each line in `audit.jsonl` is a JSON object:

```json
{
  "timestamp": "2026-02-15T03:36:05.750Z",
  "requestId": "gov-1771126565749-691394d0",
  "action": "tool-check",
  "tool": "read",
  "user": "main",
  "resolvedIdentity": "agent-main",
  "roles": ["admin"],
  "session": "agent:main:main",
  "allowed": true,
  "reason": "All governance checks passed",
  "checks": {
    "identity": { "passed": true, "detail": "Mapped main → agent-main with roles [admin]" },
    "scope": { "passed": true, "detail": "Tool \"read\" is allowlisted for roles [admin]" },
    "rateLimit": { "passed": true, "detail": "Rate limit OK: 1/100 calls in window" },
    "injection": { "passed": true, "detail": "No injection patterns detected" },
    "behavioral": { "passed": true, "detail": "No anomalies detected" }
  },
  "dlpMatches": ["EMAIL: \"user@ex...\" (confidence: 0.95)"],
  "anomalies": [{ "type": "new-tool", "severity": "medium", "detail": "..." }]
}
```

The `dlpMatches` and `anomalies` fields are only present when the corresponding features are enabled and detect something. The `checks` map includes `behavioral`, `escalation`, and `firstUse` entries when those features are active.
```

## Built-in Injection Patterns

Patterns are derived from published security research on OpenClaw:

### HIGH severity (always checked)
- Instruction injection: "ignore previous instructions", "disregard all rules"
- System prompt extraction: "reveal your system prompt"
- Credential exfiltration: curl/wget with API keys or tokens (Snyk ToxicSkills)
- Reverse shell: bash -c, netcat, /dev/tcp (Cisco Skill Scanner)
- Webhook exfiltration: requestbin, pipedream, burpcollaborator
- Encoded payloads: base64 decode, atob, Buffer.from

### MEDIUM severity
- Role impersonation: "I am admin", "act as root"
- Permission escalation: "grant me admin access"
- Sensitive file access: .env, .ssh, id_rsa, .aws/credentials
- Hidden instruction markers: [SYSTEM], [ADMIN], [OVERRIDE]
- Temp file staging

### LOW severity
- Raw IP addresses in URLs
- Tunnel services: ngrok, serveo, localhost.run
