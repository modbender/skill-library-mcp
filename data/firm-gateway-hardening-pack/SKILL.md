---
name: firm-gateway-hardening-pack
version: 1.0.0
description: >
  Gateway authentication hardening and credentials audit pack.
  Validates device auth, Baileys credentials, webhook HMAC signatures,
  log configuration, and workspace integrity. 5 specialized security tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - security
  - gateway
  - hardening
  - audit
  - credentials
---

# firm-gateway-hardening-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Hardens the OpenClaw Gateway by auditing authentication configuration,
credentials storage, webhook signatures, logging, and workspace file integrity.

## Tools (5)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_gateway_auth_check` | Validate Gateway device auth is enabled | CRITICAL |
| `openclaw_credentials_check` | Audit Baileys credentials storage security | HIGH |
| `openclaw_webhook_sig_check` | Verify HMAC signature on webhooks | HIGH |
| `openclaw_log_config_check` | Check log configuration (no sensitive data) | MEDIUM |
| `openclaw_workspace_integrity_check` | Verify workspace file integrity | MEDIUM |

## Usage

```yaml
skills:
  - firm-gateway-hardening-pack

# Run full gateway hardening audit:
openclaw_gateway_auth_check config_path=/path/to/config.json
openclaw_credentials_check config_path=/path/to/config.json
openclaw_webhook_sig_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
