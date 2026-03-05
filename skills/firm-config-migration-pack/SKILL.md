---
name: firm-config-migration-pack
version: 1.0.0
description: >
  Configuration migration and integrity audit pack.
  Shell env sanitization, plugin integrity, token separation,
  OTEL redaction, and RPC rate limiting. 5 migration tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - config
  - migration
  - integrity
  - otel
  - security
---

# firm-config-migration-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Validates configuration migration safety: shell environment sanitization
(LD_PRELOAD, DYLD_*), plugin integrity via SHA-256 manifest verification,
token separation enforcement, OpenTelemetry PII redaction, and RPC rate limiting.

## Tools (5)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_shell_env_check` | Shell environment sanitization (LD_*/DYLD_*) | HIGH |
| `openclaw_plugin_integrity_check` | Plugin SHA-256 manifest drift detection | HIGH |
| `openclaw_token_separation_check` | Token separation enforcement | HIGH |
| `openclaw_otel_redaction_check` | OTEL PII redaction validation | MEDIUM |
| `openclaw_rpc_rate_limit_check` | RPC rate limiting configuration | MEDIUM |

## Usage

```yaml
skills:
  - firm-config-migration-pack

# Audit configuration before migration:
openclaw_shell_env_check config_path=/path/to/config.json
openclaw_plugin_integrity_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
