---
name: firm-runtime-audit-pack
version: 1.0.0
description: >
  Runtime environment and configuration audit pack.
  Validates Node.js version, secrets workflow, HTTP headers, allowed commands,
  trusted proxy, disk budget, and DM allowlist. 7 runtime security tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - runtime
  - audit
  - security
  - nodejs
  - configuration
---

# firm-runtime-audit-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Audits the runtime environment of OpenClaw deployments: Node.js version compliance,
secrets handling, HTTP security headers, command allowlists, proxy configuration,
disk budget, and direct message policies.

## Tools (7)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_node_version_check` | Verify Node.js runtime version | CRITICAL |
| `openclaw_secrets_workflow_check` | Audit secrets handling in workflows | CRITICAL |
| `openclaw_http_headers_check` | Check HTTP security headers (HSTS, CSP) | HIGH |
| `openclaw_nodes_commands_check` | Validate nodes.allowCommands config | HIGH |
| `openclaw_trusted_proxy_check` | Verify trusted proxy configuration | HIGH |
| `openclaw_session_disk_budget_check` | Check session disk budget limits | MEDIUM |
| `openclaw_dm_allowlist_check` | Audit DM channel allowlist policy | MEDIUM |

## Usage

```yaml
skills:
  - firm-runtime-audit-pack

# Run full runtime audit:
openclaw_node_version_check config_path=/path/to/config.json
openclaw_secrets_workflow_check config_path=/path/to/config.json
openclaw_http_headers_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
- Node.js >= 20.x recommended
