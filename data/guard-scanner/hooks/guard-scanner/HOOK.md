---
name: guard-scanner
description: "Runtime Guard — intercepts dangerous tool calls using threat intelligence patterns before execution"
metadata: { "openclaw": { "emoji": "🛡️", "events": ["agent:before_tool_call"], "requires": { "bins": ["node"] } } }
---

# guard-scanner Runtime Guard — before_tool_call Hook

Real-time security monitoring for OpenClaw agents. Intercepts dangerous
tool calls before execution and checks against threat intelligence patterns.

## Triggers

| Event                      | Action | Purpose                                    |
|----------------------------|--------|-------------------------------------------|
| `agent:before_tool_call`   | scan   | Check tool args for malicious patterns    |

## What It Does

Scans every `exec`/`write`/`edit`/`browser`/`web_fetch`/`message` call against 26 runtime threat patterns (5 layers):

| ID | Severity | Layer | Description |
|----|----------|-------|-------------|
| `RT_REVSHELL` | CRITICAL | 1 | Reverse shell via /dev/tcp, netcat, socat |
| `RT_CRED_EXFIL` | CRITICAL | 1 | Credential exfiltration to webhook.site, requestbin, etc. |
| `RT_GUARDRAIL_OFF` | CRITICAL | 1 | Guardrail disabling (exec.approvals=off) |
| `RT_GATEKEEPER` | CRITICAL | 1 | macOS Gatekeeper bypass via xattr |
| `RT_AMOS` | CRITICAL | 1 | ClawHavoc AMOS stealer indicators |
| `RT_MAL_IP` | CRITICAL | 1 | Known malicious C2 IPs |
| `RT_DNS_EXFIL` | HIGH | 1 | DNS-based data exfiltration |
| `RT_B64_SHELL` | CRITICAL | 1 | Base64 decode piped to shell |
| `RT_CURL_BASH` | CRITICAL | 1 | Download piped to shell execution |
| `RT_SSH_READ` | HIGH | 1 | SSH private key access |
| `RT_WALLET` | HIGH | 1 | Crypto wallet credential access |
| `RT_CLOUD_META` | CRITICAL | 1 | Cloud metadata endpoint SSRF |
| `RT_MEM_WRITE` | HIGH | 2 | Direct memory file write bypass |
| `RT_MEM_INJECT` | CRITICAL | 2 | Memory poisoning via episode injection |
| `RT_SOUL_TAMPER` | CRITICAL | 2 | SOUL.md modification attempt |
| `RT_CONFIG_TAMPER` | HIGH | 2 | Workspace config tampering |
| `RT_PROMPT_INJECT` | CRITICAL | 3 | Prompt injection / jailbreak detection |
| `RT_TRUST_BYPASS` | CRITICAL | 3 | Trust safety bypass |
| `RT_SHUTDOWN_REFUSE` | HIGH | 3 | Shutdown refusal / self-preservation |
| `RT_NO_RESEARCH` | MEDIUM | 4 | Agent executing tools without prior research |
| `RT_BLIND_TRUST` | MEDIUM | 4 | Trusting external input without memory check |
| `RT_CHAIN_SKIP` | HIGH | 4 | Acting on single source without cross-verification |
| `RT_AUTHORITY_CLAIM` | HIGH | 5 | Authority role claim to override safety |
| `RT_CREATOR_BYPASS` | CRITICAL | 5 | Creator impersonation to disable safety |
| `RT_AUDIT_EXCUSE` | CRITICAL | 5 | Fake audit excuse for safety bypass |
| `RT_TRUST_PARTNER_EXPLOIT` | CRITICAL | 5 | Weaponizing partnership trust |



## Modes

| Mode | Behavior |
|------|----------|
| `monitor` | Log all detections, never block |
| `enforce` (default) | Block CRITICAL, log rest |
| `strict` | Block HIGH + CRITICAL, log MEDIUM+ |

## Audit Log

All detections logged to `~/.openclaw/guard-scanner/audit.jsonl`.

Format: JSON lines with fields:
```json
{"tool":"exec","check":"RT_CURL_BASH","severity":"CRITICAL","desc":"Download piped to shell","mode":"enforce","action":"blocked","session":"...","ts":"2026-02-17T..."}
```

## Configuration

Set mode in `openclaw.json`:
```json
{
  "hooks": {
    "internal": {
      "entries": {
        "guard-scanner": {
          "enabled": true,
          "mode": "enforce"
        }
      }
    }
  }
}
```

## Part of guard-scanner v1.0.0

- **Static scanner**: `npx guard-scanner [dir]` — 17 threat categories, 170+ patterns
- **Runtime Guard: This hook** — 12 real-time patterns, 3 modes
- **Plugin API** — Custom detection rules
- **CI/CD** — SARIF output for GitHub Code Scanning
