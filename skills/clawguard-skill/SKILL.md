---
name: clawwall
version: 0.3.0
description: "Outbound DLP for OpenClaw — hard regex blocks secrets & PII from leaving the machine. Domain control, no LLM."
author: Stanxy
openclaw:
  requires:
    bins:
      - python3
      - pip
      - node
      - npm
    envs: []
  hooks:
    - event: gateway:startup
      handler: hooks/openclaw/dist/handler.js
      export: onStartup
---

# ClawWall — Outbound DLP for OpenClaw

**GitHub:** https://github.com/Stanxy/clawguard
**PyPI:** https://pypi.org/project/clawwall

ClawWall sits between your AI agent and the outside world. Every outbound tool call is intercepted and scanned against 60+ hard-coded patterns before anything leaves the machine. If content matches — it is blocked or redacted. No LLM, no approximation: regex and entropy only.

## Setup

One command:

```bash
bash setup.sh
```

This installs the Python service, builds the plugin and hook, registers the plugin in your OpenClaw config, sets up a system service, and verifies the health endpoint.

The `gateway:startup` hook auto-starts the service whenever OpenClaw boots — no manual `clawwall` command needed.

## Trust & Permissions

**What this installs:**

| Component | What It Does |
|-----------|-------------|
| **Python service** (port 8642) | Receives every outbound tool call for scanning |
| **OpenClaw plugin** (`before_tool_call`) | Intercepts outbound content and routes to the service |
| **Startup hook** (`gateway:startup`) | Auto-starts the service when OpenClaw boots |
| **SQLite database** | Stores scan metadata (finding type, severity, action, duration) |
| **systemd/launchd service** | Fallback auto-start via OS service manager |

**What the database stores:** finding type, severity, position offsets, action taken, and duration. It **never** stores raw content, secrets, or PII values.

**What it does NOT do:** no telemetry, no external connections, no data leaves the machine. The service is fully local.

## Verify Installation

```bash
# Health check
curl -s http://127.0.0.1:8642/api/v1/health

# Test scan
curl -s -X POST http://127.0.0.1:8642/api/v1/scan \
  -H "Content-Type: application/json" \
  -d '{"content": "key=AKIAIOSFODNN7EXAMPLE"}'

# Dashboard
open http://127.0.0.1:8642/dashboard
```

## What ClawWall Detects

- **Secrets (52 patterns):** AWS, GCP, Azure, GitHub, GitLab, Stripe, Square, PayPal, Slack, Discord, Telegram, Twilio, SSH/PGP private keys, database URIs, JWT/Bearer tokens, SaaS API keys, and more
- **PII (10 patterns):** SSNs, credit cards (Luhn-validated), emails, phone numbers, IP addresses
- **Entropy analysis:** high-entropy strings that don't match any known pattern
- **Custom patterns:** user-defined regex via policy YAML

## Configuration

Environment variables (all prefixed `CLAWGUARD_`):

| Variable | Default | Description |
|---|---|---|
| `CLAWGUARD_HOST` | `0.0.0.0` | Bind address |
| `CLAWGUARD_PORT` | `8642` | Port |
| `CLAWGUARD_DATABASE_URL` | `sqlite+aiosqlite:///~/.config/clawwall/clawwall.db` | Database path |
| `CLAWGUARD_POLICY_PATH` | `~/.config/clawwall/policy.yaml` | Policy file |
| `CLAWGUARD_LOG_LEVEL` | `INFO` | Log verbosity |

## Policy

Default policy redacts all findings. Edit via the dashboard or `~/.config/clawwall/policy.yaml`:

```yaml
default_action: REDACT      # BLOCK | REDACT | ALLOW
redaction:
  strategy: mask             # mask | hash | remove
  mask_char: "*"
  mask_preserve_edges: 4
destination_allowlist: []    # bypass scanning for trusted destinations
destination_blocklist: []    # always reject these destinations
custom_patterns: []          # add your own regex patterns
disabled_patterns: []        # disable specific built-in patterns by name
```

Policy evaluation order: severity overrides > destination allowlist > destination blocklist > destination rules > agent rules > default action.

## Agent Instructions

You are operating behind **ClawWall**. All outbound tool calls are scanned before leaving the machine using hard pattern matching — not an LLM.

| Result | Meaning |
|--------|---------|
| `ALLOW` | No sensitive data detected — call went through |
| `REDACT` | Sensitive portions were masked before sending |
| `BLOCK` | Call rejected — nothing was sent |

**Best practices:**
- Never include raw API keys, tokens, or PII in outbound calls
- Reference credentials by name (`$OPENAI_API_KEY`), not by value
- If blocked, check `findings` to see what matched, remove the sensitive data, and retry
- False positive? Tell the user to adjust the policy via the dashboard at http://localhost:8642/dashboard

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Service not starting | Check `~/.config/clawwall/clawwall.log` for errors |
| Port 8642 in use | Another process is using the port — check with `lsof -i :8642` |
| Plugin not intercepting | Verify plugin is registered in `~/.openclaw/openclaw.json` |
| False positives | Disable specific patterns via `disabled_patterns` in policy YAML |
| Hook not firing | Rebuild hook: `cd hooks/openclaw && npm run build` |
| `clawwall` not found | Ensure pip install directory is on PATH, or use `python3 -m clawguard` |
