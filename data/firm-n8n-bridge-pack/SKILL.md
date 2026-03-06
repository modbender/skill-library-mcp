---
name: firm-n8n-bridge-pack
version: 1.0.0
description: >
  n8n workflow bridge pack.
  Export OpenClaw pipelines to n8n format and import n8n workflows. 2 bridge tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - n8n
  - workflow
  - bridge
  - automation
  - export
---

# firm-n8n-bridge-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Bridges OpenClaw workflows with n8n automation platform. Exports OpenClaw pipelines
to n8n JSON format (20 node type mappings) and imports n8n workflows back with validation.

## Tools (2)

| Tool | Description |
|------|-------------|
| `openclaw_n8n_workflow_export` | Export OpenClaw pipeline to n8n JSON |
| `openclaw_n8n_workflow_import` | Import n8n workflow into OpenClaw |

## Usage

```yaml
skills:
  - firm-n8n-bridge-pack

# Export/import workflows:
openclaw_n8n_workflow_export config_path=/path/to/config.json pipeline_name=my-pipeline
openclaw_n8n_workflow_import workflow_path=/path/to/workflow.json
```

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
- n8n >= 1.0 (recommended)
