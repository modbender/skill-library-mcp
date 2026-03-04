---
name: firm-advanced-security-pack
version: 1.0.0
description: >
  Advanced security audit pack covering secrets lifecycle, path canonicalization,
  exec plan freeze, hook routing, config includes, prototype pollution,
  safeBins profiles, and group policy defaults. 8 deep security tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - security
  - advanced
  - audit
  - prototype-pollution
  - exec-freeze
---

# firm-advanced-security-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Deep security auditing for OpenClaw configurations — covers external secrets lifecycle,
channel path canonicalization, execution plan freeze validation, hook session routing,
`$include` directive guards, prototype pollution detection, safeBins profile enforcement,
and group policy default audit.

## Tools (8)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_secrets_lifecycle_check` | External Secrets lifecycle audit | CRITICAL |
| `openclaw_channel_auth_canon_check` | Channel path canonicalization | CRITICAL |
| `openclaw_exec_approval_freeze_check` | Exec plan freeze validation | CRITICAL |
| `openclaw_hook_session_routing_check` | Hook session routing audit | HIGH |
| `openclaw_config_include_check` | `$include` directive guards | HIGH |
| `openclaw_config_prototype_check` | Prototype pollution detection | HIGH |
| `openclaw_safe_bins_profile_check` | safeBins profile enforcement | HIGH |
| `openclaw_group_policy_default_check` | Group policy default audit | HIGH |

## Usage

```yaml
skills:
  - firm-advanced-security-pack

# Run full advanced security audit:
openclaw_secrets_lifecycle_check config_path=/path/to/config.json
openclaw_config_prototype_check config_path=/path/to/config.json
openclaw_safe_bins_profile_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
