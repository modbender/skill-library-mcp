---
name: firm-reliability-pack
version: 1.0.0
description: >
  Reliability probing and documentation sync pack.
  Gateway health probing, documentation sync validation, channel audit,
  and ADR generation. 4 reliability tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - reliability
  - gateway
  - adr
  - documentation
  - audit
---

# firm-reliability-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Ensures deployment reliability: Gateway health probing with latency tracking,
documentation-code sync verification, channel configuration audit, and
Architecture Decision Record (ADR) generation in MADR format.

## Tools (4)

| Tool | Description |
|------|-------------|
| `openclaw_gateway_probe` | Gateway health probe with latency metrics |
| `openclaw_doc_sync_check` | Documentation-code sync validation |
| `openclaw_channel_audit` | Channel configuration audit |
| `firm_adr_generate` | Generate ADR in MADR format |

## Usage

```yaml
skills:
  - firm-reliability-pack

# Probe gateway and check docs:
openclaw_gateway_probe config_path=/path/to/config.json
openclaw_doc_sync_check config_path=/path/to/config.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
