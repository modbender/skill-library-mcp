---
name: firm-fleet-manager-pack
version: 1.0.0
description: >
  Multi-instance Gateway fleet management pack.
  Status monitoring, dynamic add/remove, broadcast commands, config sync,
  and fleet inventory. 6 fleet orchestration tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - fleet
  - gateway
  - orchestration
  - monitoring
  - scaling
---

# firm-fleet-manager-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Manages N concurrent Gateway instances: health checks, dynamic scaling,
broadcast commands, configuration synchronization, and fleet inventory.

## Tools (6)

| Tool | Description |
|------|-------------|
| `firm_gateway_fleet_status` | Health check all fleet instances |
| `firm_gateway_fleet_add` | Add a new Gateway instance to the fleet |
| `firm_gateway_fleet_remove` | Remove an instance from the fleet |
| `firm_gateway_fleet_broadcast` | Broadcast a command to all instances |
| `firm_gateway_fleet_sync` | Synchronize configuration across fleet |
| `firm_gateway_fleet_list` | List all fleet instances with metadata |

## Usage

```yaml
skills:
  - firm-fleet-manager-pack

# Monitor fleet health:
firm_gateway_fleet_status
firm_gateway_fleet_list
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
