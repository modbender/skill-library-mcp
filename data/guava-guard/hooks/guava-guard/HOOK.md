---
name: guava-guard
description: "GuavaGuard Runtime Guard — warns on dangerous tool call patterns in real-time"
metadata: { "openclaw": { "emoji": "🍈", "events": ["agent:before_tool_call"], "requires": { "bins": ["node"] } } }
---

# GuavaGuard Runtime Guard — before_tool_call Hook

Real-time security monitoring for OpenClaw agents. Warns when dangerous
tool call patterns are detected (reverse shells, credential exfiltration, etc).

> **Note**: Blocking is not yet possible — OpenClaw's hook API does not
> currently support a cancel mechanism. See [Issue #18677](https://github.com/openclaw/openclaw/issues/18677).

## Triggers

| Event                    | Action | Purpose                                |
|--------------------------|--------|----------------------------------------|
| `agent:before_tool_call` | warn   | Check tool args for malicious patterns |

## What it does

Scans every exec/write/edit/browser/web_fetch/message call against 12 runtime threat patterns:

- Reverse shells, credential exfiltration, Gatekeeper bypass
- ClawHavoc AMOS IoCs, known malicious IPs
- DNS exfiltration, base64-to-shell, curl|bash
- SSH key access, crypto wallet credential access
- Cloud metadata SSRF (169.254.169.254)
- Guardrail disabling attempts (CVE-2026-25253)

## Audit Log

All detections logged to `~/.openclaw/guava-guard/audit.jsonl`.

## For comprehensive static scanning

Use **guard-scanner** — 170+ patterns, 17 threat categories:

```bash
npx guard-scanner ./skills
```

GitHub: https://github.com/koatora20/guard-scanner
