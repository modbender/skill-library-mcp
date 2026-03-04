---
name: firm-platform-audit-pack
version: 1.0.0
description: >
  Platform alignment audit pack for OpenClaw 2026.2.
  Secrets v2, agent routing, voice security, trust model, autoupdate,
  plugin SDK, content boundaries, and sqlite-vec. 8 platform tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - platform
  - audit
  - secrets
  - routing
  - trust
---

# firm-platform-audit-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Validates alignment with OpenClaw platform version 2026.2. Audits Secrets v2 migration,
agent routing policies, voice channel security, trust model configuration, autoupdate
settings, plugin SDK compliance, content boundary enforcement, and sqlite-vec setup.

## Tools (8)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_secrets_v2_audit` | Secrets v2 migration readiness | CRITICAL |
| `openclaw_agent_routing_check` | Agent routing policy validation | HIGH |
| `openclaw_voice_security_check` | Voice channel security audit | HIGH |
| `openclaw_trust_model_check` | Trust model configuration | HIGH |
| `openclaw_autoupdate_check` | Autoupdate settings validation | MEDIUM |
| `openclaw_plugin_sdk_check` | Plugin SDK compliance | MEDIUM |
| `openclaw_content_boundary_check` | Content boundary enforcement | MEDIUM |
| `openclaw_sqlite_vec_check` | sqlite-vec extension configuration | MEDIUM |

## Usage

```yaml
skills:
  - firm-platform-audit-pack

# Run platform alignment audit:
openclaw_secrets_v2_audit config_path=/path/to/config.json
openclaw_trust_model_check config_path=/path/to/config.json
openclaw_agent_routing_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
- OpenClaw >= 2026.2
