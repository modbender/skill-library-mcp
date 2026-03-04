---
name: firm-spec-compliance-pack
version: 1.0.0
description: >
  MCP 2025-11-25 specification compliance audit pack.
  Validates elicitation, tasks, resources/prompts, audio content, JSON Schema 2020-12,
  SSE transport, and icon metadata compliance. 7 specialized audit tools.
author: romainsantoli-web
license: MIT
metadata:
  openclaw:
    registry: ClawHub
    requires:
      - mcp-openclaw-extensions >= 3.0.0
tags:
  - mcp
  - compliance
  - spec
  - audit
  - protocol
---

# firm-spec-compliance-pack

> ⚠️ Contenu généré par IA — validation humaine requise avant utilisation.

## Purpose

Audit pack ensuring full compliance with MCP specification version **2025-11-25**.
Covers all new protocol features introduced since 2025-03-26.

## Tools (7)

| Tool | Description | Severity |
|------|-------------|----------|
| `openclaw_elicitation_audit` | Validate elicitation flow implementation | HIGH |
| `openclaw_tasks_audit` | Check tasks/durable requests support | HIGH |
| `openclaw_resources_prompts_audit` | Verify resources & prompts capabilities | MEDIUM |
| `openclaw_audio_content_audit` | Audio content type support validation | MEDIUM |
| `openclaw_json_schema_dialect_check` | JSON Schema 2020-12 dialect compliance | HIGH |
| `openclaw_sse_transport_audit` | SSE transport + resumption validation | HIGH |
| `openclaw_icon_metadata_audit` | Icon metadata format verification | LOW |

## Usage

```yaml
# In your agent configuration:
skills:
  - firm-spec-compliance-pack

# Run full compliance check:
openclaw_elicitation_audit config_path=/path/to/config.json
openclaw_tasks_audit config_path=/path/to/config.json
openclaw_resources_prompts_audit config_path=/path/to/config.json
openclaw_json_schema_dialect_check config_path=/path/to/config.json
openclaw_sse_transport_audit config_path=/path/to/config.json
openclaw_icon_metadata_audit config_path=/path/to/config.json
```

## Spec Coverage

- **Elicitation** (SEP-032): Server-initiated user input requests
- **Tasks** (SEP-044): Long-running durable operations with status tracking
- **Resources/Prompts**: Capability declaration and handler completeness
- **Audio Content**: Binary audio type support in messages
- **JSON Schema 2020-12**: Dialect URI and vocabulary compliance
- **SSE Transport**: Event streaming with Last-Event-ID resumption
- **Icons**: URI format, media type validation, and accessibility

## Requirements

- `mcp-openclaw-extensions >= 3.0.0`
- MCP Protocol Version: `2025-11-25`
